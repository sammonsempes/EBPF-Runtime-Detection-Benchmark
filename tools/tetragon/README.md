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

`enforce` is `tuned` with enforcement actions, and the same policy names:

| Policy | Action | Scope |
| --- | --- | --- |
| `shell-outbound-connect`, `netcat-outbound-connect`, `mining-pool-connect` | `Sigkill` (`tcp_connect` cannot be overridden) | container mount namespaces |
| `http-client-upload` | `Override` -EPERM + `Sigkill` on `security_socket_sendmsg` | containers |
| `interpreter-spawns-shell`, `exec-from-temp-dir`, `system-binary-masquerading`, `fileless-exec` | `Override` -EPERM + `Sigkill` | containers |
| `suspicious-tool-exec` | `Override` + `Sigkill` for account management, scanners, miners, shred; discovery tools are only observed | containers |
| `persistence-file-write`, `credential-file-read` | `Override` + `Sigkill` on `security_file_permission` | containers |
| `permission-change`, `history-and-log-tampering`, `kernel-module-syscalls` | `Override` + `Sigkill` on the syscalls / `security_file_truncate` | containers |
| `container-escape` | `Override` + `Sigkill` for disk mounts, `chroot` and `setns` by `nsenter`; other `setns` calls are observed | containers |

Every enforcing selector carries `matchNamespaces: Mnt NotIn host_ns` (`Pid` for `setns`), so host processes are never killed; host matches are kept as plain observation selectors where the selector budget allows. The default policies stay observation only. Override needs `bpf_override_return` (`CONFIG_BPF_KPROBE_OVERRIDE`); on kernels without it the enforce policies fail to load and the profile is reported as failed. Sigkill on a write or send does not guarantee the in-flight operation is prevented (`docs/content/en/docs/concepts/enforcement/_index.md`), which is why it is paired with Override where the hook allows it. Killing a scenario step can also kill the scenario shell itself (for example a shell redirection into `/etc/cron.d`), so its exit trap may not run; scenario `cleanup.sh` scripts handle that.

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

Enforcement is identified from upstream fields only: `raw.process_kprobe.action` (or the `action` of the other policy event types) is `KPROBE_ACTION_SIGKILL` or `KPROBE_ACTION_OVERRIDE` instead of `KPROBE_ACTION_POST`; the killed process later produces a `process_exit` with `signal: "SIGKILL"` (telemetry, not parsed as an alert).

Alerts are read from the export file (`alerts_file`), so `emitted_at` is the runner read time. `ready_pattern` is `Listening for events\.\.\.`, logged by `pkg/observer/observer_linux.go` after the base sensor and all policies of `tracing-policy-dir` are loaded (`cmd/tetragon/main.go`).

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
