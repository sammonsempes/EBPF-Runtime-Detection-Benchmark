# KubeArmor

- Version: **1.7.5**, image `kubearmor/kubearmor:v1.7.5`, no local build.
  `STABLE-RELEASE` on main already says `v1.7.6`, but the repository only has `v1.7.6-rc1..rc6` tags; `v1.7.5`
  is the newest final tag (and the target of the upstream `latest` tag).
- Adapter: `runner/bench/adapters/kubearmor.py`.

## Deployment in the benchmark (non-Kubernetes, Docker)

One privileged container (host PID and network namespaces) running `/KubeArmor/kubearmor` in unorchestrated
mode, as in `deployments/podman/docker-compose.yaml` and the systemd package (`KubeArmor/packaging/kubearmor.yaml`):

- configuration: `KUBEARMOR_CFG=/opt/kubearmor/profile/kubearmor.yaml` (viper config, `KubeArmor/config/config.go`):
  `k8s: false`, container policies enabled, container visibility `process,file,network,capabilities`
  (needed: Audit rules only fire on traced events), default postures `audit`. Host policies are disabled
  (`enableKubeArmorHostPolicy: false`, upstream systemd packaging enables them): with the AppArmor enforcer the daemon
  would load a host AppArmor profile into the host kernel from inside the container, which a benchmark must not do;
- containers are discovered through the Docker socket (`core/dockerHandler.go`, auto-detected at
  `/var/run/docker.sock`), already running containers included;
- policies: the daemon restores every file of `/opt/kubearmor/policies/` at startup
  (`core/unorchestratedUpdates.go`, `restoreKubeArmorPolicies`). That directory is KubeArmor's own policy backup
  store, so files use its JSON layout `{"kind": "KubeArmorPolicy", "metadata": {"namespaceName", "policyName"}, "spec": {...}}`,
  `spec` being the regular KubeArmorPolicy spec. The profile `policies/` dir is mounted read-only there.
  At runtime the same policies could be pushed with the gRPC PolicyService (`karmor vm policy add`);
- alerts: `-logPath=/var/log/kubearmor/kubearmor-alerts.jsonl` makes the feeder write every log and alert as one
  JSON object per line (`feeder/feeder.go` `PushLog`, before gRPC alert throttling). The run output directory is
  mounted there and the runner tails it (`alerts_file`). No wrapper image or gRPC client is needed.

| Host path | Container path |
|---|---|
| `tools/kubearmor/<profile>/` | `/opt/kubearmor/profile` (ro) |
| `tools/kubearmor/<profile>/policies/` | `/opt/kubearmor/policies` (ro) |
| run output dir | `/var/log/kubearmor` (rw) |
| `/var/run/docker.sock` | same (ro) |
| `/sys/fs/bpf`, `/sys/kernel/security`, `/sys/kernel/debug` | same |

The upstream compose also runs `kubearmor-init` to compile the eBPF system monitor against the host kernel; here
the CO-RE `system_monitor.bpf.o` shipped in the image is used, which requires a BTF kernel. Ready when the daemon
logs `Initialized KubeArmor` (`core/kubeArmor.go`), immediately before policies are restored.

The LSM enforcer keeps the upstream order `bpf,apparmor,selinux`. With BPF-LSM the `filelessExec` preset is active;
on hosts without BPF-LSM or AppArmor no enforcer is loaded and Audit alerts come from the eBPF monitor
(`Enforcer: eBPF Monitor`), which is the documented detection path.

### Targeting the victims

Policies select `kubearmor.io/container.name: bench-victim`. In Docker mode KubeArmor adds the identity
`kubearmor.io/container.name=<container name>` to every container and compares this label as an unanchored POSIX
regex (`common/common.go` `MatchIdentities`/`MatchesRegex`), so the selector matches both `bench-victim` and
`bench-victim-priv`. No runner change (labels) is required.

## Profiles

KubeArmor ships no detection rules: with no policy it only emits telemetry. Upstream "recommended policies" are the
hardening templates distributed through `karmor recommend` (policy-templates repo), documented in this repository
under `getting-started/use-cases/res/*.yaml` and `getting-started/hardening_guide.md`.

- `default`: those upstream hardening use-case policies that apply to any Linux container, with the selector
  changed to the victims and `Block` turned into `Audit` (the benchmark must let attacks run):
  `fim.yaml` -> harden-file-integrity-monitoring, `pkg-tools.yaml` -> harden-pkg-mngr-exec,
  `trusted-cert-bundle.yaml` -> harden-trusted-cert-mod, `file-copy.yaml` -> harden-remote-file-copy,
  `tmp-noexec.yaml` -> ksp-block-exec-inside-tmp, `admin-tools.yaml` -> harden-k8s-client-tool-exec,
  `disc-tools.yaml` -> harden-network-service-scanning, `log-del.yaml` -> harden-shell-history-mod,
  `svc-act-token.yaml` -> ksp-block-service-account. Workload prefixes (mysql, wordpress, dvwa, nginx) were dropped
  from names. Left out: allow-list policies that need a default-deny posture (`net-acc`, `icmp-con`), workload
  specific ones (`db-access` for MySQL, `conf-data` ownerOnly on `*.conf`), and `res-cap` (capability rules are
  enforced by the LSM only, not audited by the monitor). Rules are kept verbatim, including the noisy ones
  (dpkg/make in the package manager list, every rm/mv execution in the history policy).
- `tuned`: the default set with three adjustments to remove benign noise (dpkg and make removed from the package
  manager list, the rm/mv process rule of the history policy replaced by readOnly rules on history files plus
  unlink syscall rules, extra temp dirs and container runtime sockets added), plus `tuned-*` policies:

| Policy | Rule | Techniques |
|---|---|---|
| tuned-shell-network-socket | tcp/udp socket from bash/dash/sh | T1059.004 |
| tuned-interpreter-spawned-shell | shell exec from python/perl/ruby/php/node | T1059.006 |
| tuned-scheduled-task-mod | writes in cron dirs and /etc/crontab | T1053.003 |
| tuned-ssh-authorized-keys-mod | writes to authorized_keys | T1098.004 |
| tuned-systemd-unit-mod | writes in systemd unit dirs, /etc/init.d | T1543.002 |
| tuned-account-manipulation | useradd/usermod/chpasswd exec, writes to passwd/group/sudoers | T1136.001 |
| tuned-kernel-module-load | kmod/insmod/modprobe exec | T1547.006 |
| tuned-permission-modification | chattr/setfacl/setcap exec | T1222.002 |
| tuned-container-escape | nsenter/unshare/chroot/mount/mknod exec, mount syscall | T1611 |
| tuned-shadow-file-access | any access to shadow files | T1003.008 |
| tuned-credentials-in-files | cloud, ssh, kube, docker credential files, .env | T1552.001 |
| tuned-container-discovery | capsh/getpcaps exec, /.dockerenv, /proc/1/cgroup | T1613 |
| tuned-system-discovery | uname/lscpu/hostnamectl/dmidecode exec | T1082 |
| tuned-cryptominer-exec | miner executable names (execname) | T1496 |
| tuned-data-destruction | shred/wipe/srm/wipefs exec | T1485 |
| tuned-log-tampering | writes in /var/log by truncate/shred/tee/sed, truncate exec | T1070.002 |
| tuned-fileless-exec | `filelessExec` preset and `/memfd:*` exec pattern | T1620 |

All rules use the `Audit` action. Paths are those of the Ubuntu 24.04 victim (merged /usr, so `/usr/bin/...`).
Checked against the benign scripts in `scenarios/benign-*`: the log rotation scenario runs `chmod` and appends to
`/var/log` from `sh`, so `chmod`/`chown` executions and shell writes to `/var/log` are deliberately not rules
(consequence: `chmod 777 /etc/shadow` is not visible to KubeArmor, see limitations).

- `enforce`: the exact tuned policy set with `action: Block` (preset `filelessExec` also `Block`) and `lsm: "bpf"`.
  Every tuned rule was compared with the benign scripts (gcc build in /root/workspace, http.server serving /tmp,
  logrotate + gzip, tar to /backup, id/ps/ls/df/free/cat/uptime, dpkg/apt-cache): none of them matches a rule, so no
  rule had to stay in Audit. Residual risk: `harden-file-integrity-monitoring` makes /usr/lib read-only, a Python
  process writing a missing `__pycache__` file there would be denied (Python ignores that failure).

## Enforcement (enforce profile)

Which enforcer works for Docker containers outside Kubernetes (`enforcer/runtimeEnforcer.go`, `selectLsm`):

- **BPF-LSM (used here)**: requires `CONFIG_BPF_LSM=y` and `bpf` in `/sys/kernel/security/lsm` (kernel boot parameter
  `lsm=...,bpf`, `getting-started/FAQ.md`), plus `/sys/kernel/security` and `/sys/fs/bpf` in the KubeArmor container
  (mounted). Containers are registered by pid/mnt namespace when Docker reports them (`RegisterContainer`), so it
  works on running unorchestrated containers with no runner change. Presets such as `filelessExec` only work with it.
- **AppArmor**: needs AppArmor on the host, `apparmor_parser`, `/etc/apparmor.d`, and the container must be started
  under the generated profile `kubearmor_<container name>` (`docker run --security-opt apparmor=kubearmor_bench-victim`)
  after KubeArmor created it. The benchmark victims are not started that way, so AppArmor would not block anything.
- **SELinux**: used for host policies only outside Kubernetes.

The enforce profile pins `lsm: "bpf"`, but if the host lacks BPF-LSM KubeArmor falls back to the next available LSM
or to no enforcer; Block rules are then only reported (`Result: Passed`). Check the daemon log for
`Initialized BPF-LSM Enforcer` (versus `Disabled KubeArmor Enforcer` / `Initialized AppArmor Enforcer`) before
trusting enforce results. WSL2 has no securityfs: no blocking there.

How a block is reported: `action` (`Action` in gRPC JSON) contains `Block` and `result` is the errno text of the denied
operation, `Permission denied` (EACCES) for most process/file/network denials, sometimes `Operation not permitted`;
`enforcer` is `BPFLSM`. A Block rule that was only observed (no enforcer) has `result: Passed`. Use
`Adapter.is_blocked(alert.raw)` (action contains Block and result is not empty or `Passed`). `parse()` keeps the
complete JSON, including `action`, `result` and `enforcer`, in `raw`.

## What counts as an alert

Only policy matches: lines whose `type` is `MatchedPolicy`, `MatchedHostPolicy` or `MatchedNetworkPolicy`
(`ContainerLog`/`HostLog` telemetry, throttling `SystemEvent`s and daemon logs return `None`). Mapping:
`policyName` -> rule, `severity` -> severity, `updatedTime` (fallback `timestamp`) -> `event_at`,
`containerID`/`containerName`, `processName` -> process, command line = `resource` for Process operations
(full exec command line) and `source` otherwise (command line of the acting process). The full JSON is kept in `raw`.

The `-logPath` file uses the Go `json` tags of `types.Log` (camelCase: `policyName`, `containerName`,
`updatedTime`, `hostPid`...), while gRPC clients (`karmor logs --json`) and all documentation samples use the
protobuf PascalCase names (`PolicyName`, `ContainerName`...). The parser accepts both spellings.

## Fixtures (`runner/tests/fixtures/kubearmor/alerts.jsonl`)

| Line | Source |
|---|---|
| 1-3 | verbatim, `getting-started/kubearmor-events.md` container Process, File and Network (Audit, eBPF Monitor) alerts |
| 4 | verbatim, `getting-started/kubearmor-events.md` host Process alert |
| 5 | verbatim, `getting-started/process_arguments.md` (v1.6.5 alert with EventData, Cwd, ExecEvent) |
| 6, 7 | verbatim, `getting-started/kubearmor-events.md` Process and File telemetry (`ContainerLog`, not alerts) |
| 8 | derived: line 5 re-keyed with the `types.Log` json tags (`KubeArmor/types/types.go`), i.e. the `-logPath` format |
| 9 | derived: the HostLog of `KubeArmor/feeder/feeder_test.go` TestMarshalVisibilityLog serialized with the same tags |
| 10, 11 | daemon console log line (format of `KubeArmor/log/logger.go`) and noise |

The JSON documents were compacted to one line each; no verbatim camelCase sample exists upstream.

## Known limitations

- Exfiltration (tar + curl POST) and network scanning by port cannot be expressed: rules match binaries, paths and
  protocols, not destinations, ports or argument values (argument matching only works for Allow lists).
- `chmod u+s` / `chmod 777` are only visible as `chmod` executions: the system monitor traces neither chmod nor
  finit_module/memfd_create syscalls (`monitor/systemMonitor.go`); since benign scripts run chmod, no chmod rule is
  kept, so T1222.002 is missed and T1548.001 is only caught because the setuid copy is executed from /tmp.
- In the enforce profile, blocked operations also break the scenario's own cleanup when it touches protected files
  (e.g. restoring `/root/.bash_history`); scenarios' cleanup.sh must cope with that.
- The `filelessExec` preset only works with the BPF-LSM enforcer.
- Audit rules require visibility, so every file/process/network event of every container is serialized to the
  alerts file; this is part of the measured overhead.
- Policies in `/opt/kubearmor/policies` are read at startup; the daemon also tries to rewrite them there (backup), which
  fails silently on the read-only mount.
- Readiness is signalled a few milliseconds before policies are restored.
