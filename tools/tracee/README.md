# Tracee

- Version: **0.24.1** (latest release tag in the upstream repository; `deploy/helm/tracee/Chart.yaml` and
  `deploy/kubernetes/tracee/tracee.yaml` both pin `aquasec/tracee:0.24.1`).
- Image: `aquasec/tracee:0.24.1`, no local build.
- Adapter: `runner/bench/adapters/tracee.py`.

## Deployment in the benchmark

One privileged container, host PID, cgroup and network namespaces, started as
`/tracee/tracee --config /tracee/profile/config.yaml --policy /tracee/profile/policies`, exactly like the
upstream DaemonSet (`deploy/kubernetes/tracee/tracee.yaml`).

| Host path | Container path | Why |
|---|---|---|
| `tools/tracee/<profile>/` | `/tracee/profile` (ro) | configuration and policies |
| `/etc/os-release` | `/etc/os-release-host` (ro) | kernel/OS detection, `LIBBPFGO_OSRELEASE_FILE` |
| `/var/run/docker.sock` | `/var/run/docker.sock` (ro) | container enrichment (name, image) |
| run output dir | `/tmp/tracee` | Tracee working directory (artifacts) |

Requirements: kernel with BTF (CO-RE). The HTTP server listens on `:3366` of the host (healthz, metrics).

`config.yaml` is the configuration shipped in the 0.24.1 manifest `tracee-config` ConfigMap
(`output.json.files: [stdout]`, decoded data, executable hash `dev-inode`). Events are printed as JSON on stdout
and read from the container logs.

Readiness: Tracee 0.24.1 does not log a readiness line at info level (its own scripts poll `/healthz`,
`scripts/tracee_start.sh`). Both profiles therefore load `policies/tracee-startup.yaml`, which selects the
`tracee_info` event emitted once at initialisation (`docs/docs/events/builtin/man/misc/tracee_info.md`); the
`ready_pattern` waits for that event. It is never counted as an alert.

## Profiles

- `default`: the upstream `default-policy` from the 0.24.1 manifest / Helm chart (`templates/default-policy.yaml`):
  all built-in signatures enabled by the chart (TRC-101..TRC-1031 such as `stdio_over_socket`, `fileless_execution`,
  `kernel_module_loading`, `scheduled_task_mod`, `disk_mount`, `dropped_executable`, `illegitimate_shell`,
  `hidden_file_created`, `sudoers_modification`) plus `container_create` / `container_remove` lifecycle events.
- `tuned`: the default plus 21 policies named `detect-*`. Tracee 0.24.1 has no declarative signature language
  (new signatures are Go plugins compiled against the exact Tracee build; YAML/CEL detectors only exist on the
  unreleased main branch), so tuning uses the official policy mechanism: each `detect-*` policy selects kernel
  events in containers (`scope: container`) with data/scope filters describing one behavior:

| Policy | Events | Techniques |
|---|---|---|
| detect-shell-network-connect | security_socket_connect by bash/sh/dash | T1059.004 |
| detect-interpreter-shell | execve of a shell by python/perl/ruby/node/php | T1059.006 |
| detect-exec-from-temp-dir | sched_process_exec from /tmp, /var/tmp, /dev/shm | T1105, T1036.005 |
| detect-masquerading | daemon names (sshd, cron...) executed from unexpected paths | T1036.005 |
| detect-ssh-authorized-keys | write open of authorized_keys | T1098.004 |
| detect-systemd-persistence | write open in systemd unit dirs | T1543.002 |
| detect-account-creation | useradd/usermod/chpasswd exec, write to /etc/passwd, /etc/group | T1136.001 |
| detect-kernel-module | init_module, finit_module, insmod/modprobe exec | T1547.006 |
| detect-setuid-bit | chmod_common with mode >= 1024 | T1548.001 |
| detect-sensitive-permission-change | chmod_common on /etc/shadow, passwd, sudoers | T1222.002 |
| detect-container-escape | nsenter/unshare/chroot/mknod exec, security_sb_mount | T1611 |
| detect-history-clearing | write open or unlink of `*_history` | T1070.003 |
| detect-log-tampering | truncating open (`O_TRUNC`, not append) in /var/log by shells and generic tools (not gzip/logrotate), truncate exec | T1070.002 |
| detect-shadow-read | open of /etc/shadow, /etc/gshadow | T1003.008 |
| detect-credentials-in-files | open of cloud, ssh, kube, docker, git credential files and .env | T1552.001 |
| detect-container-api | k8s_service_account_token signature, token and runtime socket opens | T1552.007 |
| detect-container-discovery | capsh/docker/kubectl exec, /.dockerenv, /proc/1/cgroup | T1613 |
| detect-system-discovery | uname, lscpu, hostnamectl, dmidecode... exec | T1082 |
| detect-network-scan | nc/ncat/nmap/masscan exec | T1046 |
| detect-cryptominer | xmrig and other miner names exec/connect | T1496 |
| detect-data-destruction | shred/wipe/srm exec | T1485 |

Benign scenarios were considered: none of these rules match gcc, python http.server + curl, gzip/logrotate,
tar, ps/ls/df/id or dpkg/apt-cache. The rules target behaviors and standard paths, never benchmark markers.

No `enforce` profile: Tracee 0.24.1 has no blocking capability (policies have no Block/Deny action, signatures
only emit findings); response is limited to artifact capture and webhooks for an external responder
(`operational.yaml` `response.blocking: false`).

## What counts as an alert

`parse` returns an `Alert` only for:

1. signature findings in the 0.24.1 JSON format (`types/trace/trace.go`): events with a non-null `metadata`
   (`pkg/events/findings/findings.go` fills `Properties.signatureID`, `signatureName`, `Severity`, `Category`,
   `Technique`, `external_id`); rule = `signatureName`, severity 0..4 mapped to info/low/medium/high/critical;
2. events matched by a `detect-*` policy (`matchedPolicies`); rule = policy name;
3. the same two cases in the newer `v1beta1` JSON format produced by the main branch (`api/v1beta1/event_json.go`):
   `threat` present (rule = `threat.name`), `detected_from` present (derived detector event) or a `detect-*`
   policy in `policies.matched`. This keeps the adapter working if the image is upgraded.

Everything else (raw syscall/LSM events, `container_create`, `tracee_info`, log lines) returns `None`.
Mapping: `timestamp` (ns) -> `event_at`, `container.id`/`containerId` -> `container_id`, `container.name` ->
`container_name`, `processName` -> `process`, `argv` (event or `detectedFrom` args) or `executable.path` ->
`command_line`; the full JSON is kept in `raw`.

## Fixtures (`runner/tests/fixtures/tracee/alerts.jsonl`)

| Line | Source |
|---|---|
| 1 | verbatim, `docs/docs/policies/rules.md` (security_file_open, raw event, not an alert) |
| 2 | verbatim, `types/trace/trace_test.go` TestEventUnmarshalJSON (ptrace raw event, compacted to one line) |
| 3 | derived: legacy signature finding built with the field set of line 1 (`types/trace/trace.go` tags) and the finding conversion of `pkg/events/findings/findings.go` (`detectedFrom` arg, `metadata.Properties`), TRC-105 metadata from `docs/docs/events/builtin/man/security/fileless_execution.md` |
| 4 | derived: line 1 with `matchedPolicies: ["detect-shadow-read"]` and container fields (policy-match alert) |
| 5 | `docs/docs/outputs/event-structure.md` detector example, elided `{...}` parts filled with the shapes written by `api/v1beta1/event_json.go` |
| 6 | verbatim, `examples/detectors/yaml/CHAIN_TEST.md` (chained detector event) |
| 7 | `docs/docs/outputs/event-structure.md` raw `sched_process_exec` example (not an alert) |
| 8, 9 | non-JSON-event noise |

No verbatim 0.24.1 signature finding exists in the upstream tree (the main branch has migrated to v1beta1), hence the
derived lines 3 and 4; their field names come from the Go struct tags of the released format.

## Known limitations

- Exfiltration over HTTP (tar + curl POST) is not covered: policies cannot correlate tar output with a curl
  upload and curl is used by benign scenarios.
- Policy filters only support prefix/suffix wildcards and single fields; `detect-log-tampering` relies on the
  writing process name and on the flags string starting with `O_WRONLY|O_TRUNC` / `O_WRONLY|O_CREAT|O_TRUNC`
  (shell `>` redirection); appends (`>>`, used by the benign log rotation scenario) do not match.
- Some 0.24.1 signatures (`kernel_module_loading`, `disk_mount`) need the corresponding action to succeed;
  the unprivileged insmod attempt is caught only by `detect-kernel-module` in the tuned profile.
- Policies are read at startup only (no hot reload).
- The `tracee_info` readiness marker is emitted during initialisation, possibly slightly before every probe is
  attached; the adapter therefore also sets `ready_url: http://127.0.0.1:3366/healthz` and the runner waits for
  both (Docker mode, the `bench` service uses the host network), then `settle_seconds`.
