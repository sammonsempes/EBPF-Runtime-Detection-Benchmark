# Tetragon

- Version: **1.7.1**. Image `quay.io/cilium/tetragon:v1.7.1`, the agent tag pinned by the upstream Helm chart (`install/kubernetes/tetragon/values.yaml`, `tetragon.image.tag`); the docs site still advertises v1.7.0 (`docs/config/_default/hugo.toml`), 1.7.1 is the newest patch release referenced upstream.
- License: Apache-2.0.

## Deployment in this benchmark

One privileged container with host PID, cgroup and network namespaces (`ContainerSpec` defaults) running the image entrypoint `/usr/bin/tetragon` with `--config-dir=/etc/tetragon/bench/tetragon.conf.d --export-filename=/bench-output/tetragon-<profile>-events.json`.

| Host path | Container path | Why |
| --- | --- | --- |
| `tools/tetragon/<profile>/` | `/etc/tetragon/bench` (ro) | `tetragon.conf.d` options and `tetragon.tp.d` policies |
| run output dir | `/bench-output` (rw) | JSON export file read by the runner (`alerts_file`) |
| `/sys/kernel/btf/vmlinux` | `/var/lib/tetragon/btf` (ro) | BTF, as in the upstream Docker install docs |
| `/sys/fs/bpf` | `/sys/fs/bpf` (rw) | bpffs for pinned maps, as mounted by the chart |
| `/proc` | `/procRoot` (ro) | host procfs, `procfs: /procRoot` as in the chart config map |

`tetragon.conf.d` mirrors the Helm chart defaults (`templates/tetragon_configmap.yaml` and `values.yaml`): chart export allowlist, process cache size, process credentials/namespaces off, policy filter on, metrics on `:2112`, health on `:6789`, gRPC on the unix socket, text logs at info level. Deviations needed in Docker: `enable-k8s-api: false`; the chart denylist entry `{"namespace":["", "cilium", "kube-system"]}` is dropped because outside Kubernetes every event has an empty namespace and would be discarded (only `{"health_check":true}` is kept); the export file is 644 and rotates at 2048 MB instead of 10 MB so the runner can tail a single file; the export file lives outside `/var/log` so the file monitoring policy does not observe Tetragon's own writes. Docker container enrichment is limited to the cgroup-derived `process.docker` id: Tetragon only resolves names and images through the Kubernetes API or CRI, so no docker.sock or containerd socket is mounted.

## Profiles and what "default" means

A plain Tetragon install (Helm chart or container) ships **no TracingPolicy**: it only produces `process_exec` / `process_exit` events. Because this benchmark counts only policy events as alerts (below), `default` is defined as the upstream policies a default install recommends, unchanged except where needed to load on current kernels:

- `examples/quickstart/file_monitoring.yaml` (the Getting Started "File Access Monitoring" policy, `file-monitoring-filtered`). Upstream documents (`docs/content/en/docs/use-cases/filename-access.md`, Kernel compatibility) that `security_path_truncate` does not exist on kernels >= 6.2 and that the whole policy then fails to load; following that guidance, both `security_path_truncate` and `security_file_truncate` are listed with `ignore.callNotFound: true`.
- From the Observability Policy Library (`docs/content/en/docs/policy-library/observability/_index.md`), the policies that need no cluster-specific input: `examples/policylibrary/modules.yaml`, `bpf.yaml` and `privileges/privileges-raise.yaml`. Excluded: `egress.yaml` (needs pod and service CIDRs), `sshd.yaml` (traces every `tcp_close` system-wide), `library.yaml` (loader events, not alerts).

`tuned` is `default` plus behaviour policies for the scenario catalog: `shell-outbound-connect`, `netcat-outbound-connect`, `mining-pool-connect`, `http-client-upload`, `interpreter-spawns-shell`, `exec-from-temp-dir`, `system-binary-masquerading`, `suspicious-tool-exec` (account management, scanners, miners, shred, container and system discovery tools in containers), `persistence-file-write` (cron, systemd/init, authorized_keys, account databases), `credential-file-read`, `permission-change` (setuid/setgid, account database chmod, +x on temporary files), `container-escape` (disk mounts through `mount`, `fsopen`, `fsconfig`, `setns`, `chroot` from containers), `history-and-log-tampering`, `kernel-module-syscalls` (`raw_syscalls/sys_exit` filtered on `init_module`/`finit_module`, so attempts denied by Docker's seccomp profile are still seen) and `fileless-exec` (`execveat` with `AT_EMPTY_PATH`). They contain no benchmark tokens and were checked against the benign scenarios.

`community` is `default` plus the upstream policy library, see [Community profile](#community-profile).

`enforce` is `tuned` with enforcement actions, and the same policy names:

| Policy | Action | Scope |
| --- | --- | --- |
| `shell-outbound-connect`, `netcat-outbound-connect`, `mining-pool-connect` | `Sigkill` on `tcp_connect` | container mount namespaces |
| `http-client-upload` | `Sigkill` on `security_socket_sendmsg` | containers |
| `interpreter-spawns-shell`, `exec-from-temp-dir`, `system-binary-masquerading`, `fileless-exec` | `Sigkill` | containers |
| `suspicious-tool-exec` | `Sigkill` for account management, scanners, miners, shred; discovery tools are only observed | containers |
| `persistence-file-write`, `credential-file-read` | `Sigkill` on `security_file_permission` | containers |
| `permission-change`, `history-and-log-tampering`, `kernel-module-syscalls` | `Sigkill` on the syscalls / `security_file_truncate` | containers |
| `container-escape` | `Sigkill` for disk mounts, `chroot` and `setns` by `nsenter`; other `setns` calls are observed | containers |

Every enforcing selector carries `matchNamespaces: Mnt NotIn host_ns` (`Pid` for `setns`), so host processes are never killed; host matches are kept as plain observation selectors where the selector budget allows. The default policies stay observation only.

The profile uses `Sigkill` only, never `Override`, so it loads on kernels without `bpf_override_return` (`CONFIG_BPF_KPROBE_OVERRIDE` unset, as on the WSL2 6.6 kernel, where Tetragon rejects Override with `override action not supported on syscalls, bpf_override_return helper not available`). Sigkill is raised synchronously in the kernel at the hook, but without Override the in-flight syscall may still complete before the process dies: a write, send, chmod, unlink or mount can take effect (`docs/content/en/docs/concepts/enforcement/_index.md`). Measured blocking is therefore "process killed at the hook", not "operation denied". A variant adding `- action: Override` with `argError: -1` before `Sigkill` on the syscall and `security_*` selectors (not on `tcp_connect`) gives true denial on kernels built with `CONFIG_BPF_KPROBE_OVERRIDE`; it is not shipped so that one profile runs on every target host. Killing a scenario step can also kill the scenario shell itself (for example a shell redirection into `/etc/cron.d`), so its exit trap may not run; scenario `cleanup.sh` scripts handle that.

## Community profile

`community` is `default` plus the upstream-maintained observation policies that a default install does not load, verbatim, with no policy written by us. Source: the cilium/tetragon repository at tag `v1.7.1`, commit `99ca93d98710b98a42551bf3c12613e32888885d` (Apache-2.0, `tools/tetragon/community/LICENSE`). The set is the Observability Policy Library (`examples/policylibrary/`) plus the `examples/tracingpolicy/` policies that the upstream use-case documentation (`docs/content/en/docs/use-cases/`) publishes for security monitoring. The rest of `examples/tracingpolicy/` is API demos (uprobes on specific binaries or PIDs, datagram/tty/write tracing, `Override`/`Sigkill` samples, CVE-specific policies) and is not part of any documented security set.

Files are fetched by `tools/fetch_community.py` from `tools/tetragon/community/sources.txt` (raw URLs pinned to the commit, sha256 checked). `tetragon.conf.d` is a copy of `default`'s; `tetragon.tp.d` holds the four default policies (byte-identical) and the included files below, downloaded straight into it.

| Included file (upstream path) | Policy name | Hooks |
| --- | --- | --- |
| `examples/policylibrary/sshd.yaml` | `accept` | `sk_alloc`, `sk_free`, `tcp_set_state`, `tcp_create_openreq_child` (sshd/tcpserver), `tcp_close` (all processes) |
| `examples/policylibrary/privileges/privileges-setuid-root.yaml` | `privileges-setuid-root` | `__sys_set*id` to root, with return value |
| `examples/tracingpolicy/tcp-connect.yaml` | `connect` | `tcp_connect`, `tcp_close`, `tcp_sendmsg` (all processes) |
| `examples/tracingpolicy/process-credentials/process-creds-installed.yaml` | `process-creds-changed` | `commit_creds`, non-host pid namespaces, rate limited |
| `examples/tracingpolicy/process-credentials/creds-capability-usage.yaml` | `creds-capability-checks` | `cap_capable`, non-host pid namespaces, rate limited |
| `examples/tracingpolicy/process-exec/process-exec-elf-begin.yaml` | `process-exec-elf-begin` | `security_bprm_creds_from_file` (every exec) |

Excluded upstream files (kept verbatim under `tools/tetragon/community/excluded/` for traceability, never mounted as policies):

| File | Reason |
| --- | --- |
| `examples/policylibrary/egress.yaml` | needs `${PODCIDR}` / `${SERVICECIDR}` substitution; verbatim it is not a valid `NotDAddr` list and the load would fail |
| `examples/policylibrary/library.yaml` | loader sensor: produces `process_loader` events only, which the export allowlist drops and which are not alerts |
| `examples/tracingpolicy/host-changes/monitor-kernel-modules.yaml` | same `metadata.name` (`monitor-kernel-modules`) as the default `modules.yaml`; Tetragon rejects a second policy with an existing name and exits. Its two extra hooks (`do_init_module`, `free_module`) are therefore not loaded |
| `examples/tracingpolicy/host-changes/monitor-signed-kernel-modules.yaml` | hooks `find_module_sections`, which upstream notes may be inlined; a missing symbol makes the policy fail and Tetragon exit |
| `examples/tracingpolicy/process-credentials/process.credentials.changes.at.syscalls.yaml` | its policy name contains dots; on the benchmark host Tetragon failed to create the per-policy bpffs directory (`mkdir /run/cilium/bpffs/tetragon/process.credentials.changes.at.syscalls: operation not permitted`) and exited. Renaming it would modify the upstream policy |
| `examples/tracingpolicy/filename_monitoring.yaml`, `filename_monitoring_filtered.yaml` | hook `security_path_truncate` without `ignore.callNotFound`, absent on kernels >= 6.2 (load failure); superseded by the default `file_monitoring.yaml` |

No included file uses `Override`, `Sigkill`, `Signal` or `NotifyEnforcer`, and each uses a single hook section (kprobes only), so they load on kernels without `bpf_override_return`. Every kprobe symbol of the profile was checked against the WSL2 6.6 kernel's `/proc/kallsyms`. Every regular file of `tracing-policy-dir` (and of its first-level subdirectories) is parsed as a policy and any failure stops Tetragon (`cmd/tetragon/main.go`, `loadTpFromDir`), so `tetragon.tp.d` must contain nothing else.

Expected cost: `tcp-connect.yaml` and the `tcp_close` hook of `sshd.yaml` report every TCP connect/close/sendmsg of the host, `process-exec-elf-begin` reports every exec, and `cap_capable`/`commit_creds` sit on hot paths (rate limited per process). The resulting events from benign activity are counted as alerts like any other policy event.

## What counts as an alert

An alert is any event produced by a TracingPolicy of the active profile: `process_kprobe`, `process_tracepoint`, `process_lsm`, `process_uprobe` or `process_usdt`. `process_exec`, `process_exit` and other events are execution telemetry exported by every install; counting them would turn every command, benign or not, into a detection, so they are never alerts (none of the profiles treats them as such).

| Alert | Tetragon JSON |
| --- | --- |
| `rule` | `policy_name`, else `function_name`, else `subsys/event` for tracepoints |
| `severity` | none (Tetragon has no severity) |
| `event_at` | top-level `time` |
| `container_id` | `process.pod.container.id` without its `containerd://` style scheme, else `process.docker` (cgroup-derived, 31 characters) |
| `container_name` | `process.pod.container.name` (Kubernetes only) |
| `process` | `process.binary` |
| `command_line` | `process.binary` + `process.arguments` |
| `raw` | the whole exported event |

Enforcement is identified from upstream fields only: `raw.process_kprobe.action` (or the `action` of the other policy event types) is `KPROBE_ACTION_SIGKILL` (or `KPROBE_ACTION_OVERRIDE` for an Override variant) instead of `KPROBE_ACTION_POST`; the killed process later produces a `process_exit` with `signal: "SIGKILL"` (telemetry, not parsed as an alert).

Alerts are read from the export file (`alerts_file`), so `emitted_at` is the runner read time. In Kubernetes mode the chart's `export-stdout` sidecar is disabled and the export file lives in `/var/lib/ebpf-bench/tetragon`, read with `tail -F` through the exec API: printing events on stdout or writing them under `/var/log` makes `file-monitoring-filtered` report its own output in a loop (see `deploy/kubernetes/README.md`, "Known differences from Docker mode"). `ready_pattern` is `Listening for events\.\.\.`, logged by `pkg/observer/observer_linux.go` after the base sensor and all policies of `tracing-policy-dir` are loaded (`cmd/tetragon/main.go`).

## Kubernetes mode

On kind under WSL2, Tetragon 1.7.1 (chart 1.7.0) runs but its events cannot be attributed: it rejects the mounted procfs (`inode mismatch: procfs does not appear to be host procfs`) because the WSL2 Linux distribution itself runs in a non-initial PID namespace of the WSL utility VM, so most policy events have `"flags":"unknown"` and no pod or container id (0% recall in both profiles). The `/var/log` feedback loop of the chart's stdout export was fixed in the deployment. Details and evidence: `deploy/kubernetes/README.md`, "Validated on kind / WSL2". A Kubernetes result for Tetragon needs a native Linux node.

## Fixtures

`runner/tests/fixtures/tetragon/alerts.jsonl` (pretty-printed upstream samples compacted to one line, fields unchanged):

1. `process_kprobe` with `policy_name` from `docs/content/en/docs/use-cases/filename-access.md`;
2. `process_kprobe` `security_kernel_module_request` in a pod, from `docs/content/en/docs/use-cases/host-system-changes/linux-kernel-modules.md`;
3. host `process_kprobe` `security_kernel_read_file` (insmod), same document;
4. `process_exec`, line 2 of `testdata/events.json` (verbatim);
5. `process_exec` of `modprobe`, from `linux-kernel-modules.md`;
6. an export filter line from `docs/content/en/docs/concepts/events.md` (JSON that is not an event).

Tests derive the tracepoint, enforcement (`KPROBE_ACTION_SIGKILL` / `KPROBE_ACTION_OVERRIDE`) and pod-less variants from these lines by substituting single fields.

## Known limitations

- The kernel must provide BTF; kprobe policies referencing symbols that the running kernel lacks fail to load unless `ignore.callNotFound` is set (used for `sys_fchmodat2`, `sys_fsopen`, `sys_fsconfig`, `sys_unlink`, `sys_chmod`, truncate hooks). A failed policy makes Tetragon exit at startup.
- Policies were not loaded against the real image in this environment; start the image once with each profile mounted (`docker run --rm --privileged --pid=host --cgroupns=host -v $PWD/tools/tetragon/tuned:/etc/tetragon/bench -v /sys/kernel/btf/vmlinux:/var/lib/tetragon/btf quay.io/cilium/tetragon:v1.7.1 --config-dir=/etc/tetragon/bench/tetragon.conf.d`) and check for `Added TracingPolicy with success` lines.
- Outside Kubernetes, alerts carry only the container id prefix (`process.docker`), no container name or image.
- `kernel-module-syscalls` attaches to `raw_syscalls/sys_exit`, i.e. runs a filter on every syscall exit; `security_file_permission` and `tcp_sendmsg` hooks are on hot paths. This overhead is part of the tuned and enforce measurements.
- No policy covers the Docker socket probe of `t1552-007` (the service account token read is covered); `sockaddr_un` filtering is not used to stay compatible with the pinned release.
- Binary paths are matched as executed (`/bin/sh` and `/usr/bin/sh` are both listed); interpreters started through unusual paths are not matched.
