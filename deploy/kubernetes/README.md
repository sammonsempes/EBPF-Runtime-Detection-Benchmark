# Kubernetes mode

> **Status: run on kind on a native Linux node (runs `20261025T160602Z`, `20261025T200250Z`) and on kind under WSL2
> (run `20261024T114807Z`).** Falco, Tetragon, Tracee and Kunai detect and attribute the scenarios with the same recall
> as in Docker mode. KubeArmor produces no alert on kind, native kernel included. Pulsar exhausts the host's memory
> during its overhead workloads. See [Validated on kind / native Linux](#validated-on-kind--native-linux). Unit tests
> mock the Kubernetes client and `helm` (`runner/tests/test_k8s_backend.py`).

The scenarios, the scoring and the report are the same as in Docker mode. What changes:

- each tool is installed the way operators install it: the upstream Helm chart, or a DaemonSet for tools that have
  no upstream Kubernetes deployment;
- the victims, the attacker and the workload host run as pods.

The backend is `runner/bench/k8s_backend.py` (`KubernetesBackend`). It uses the official `kubernetes` Python client,
plus `helm` run as a subprocess.

## Layout

```
deploy/kubernetes/
  kind.yaml                     single-node kind cluster with the host mounts eBPF tools need
  targets/                      namespace ebpf-bench, attacker Deployment + Service, victim and workload pods
  tools/<tool>/tool.yaml        how the backend installs the tool and finds its agent pod
  tools/<tool>/values-*.yaml    Helm values per profile (falco, tetragon, tracee, kubearmor)
  tools/<tool>/daemonset.yaml   base DaemonSet (kunai, pulsar), completed from the adapter ContainerSpec
```

### `tool.yaml`

| Key | Meaning |
|---|---|
| `namespace`, `release` | tool namespace and Helm release name |
| `install.type` | `helm` or `manifests` |
| `install.repo/chart/version` | Helm repository URL, chart name and pinned chart version (installed with `helm upgrade --install --repo`, so no `helm repo add` is needed) |
| `install.values.<profile>` | values file used for this profile |
| `install.set_file` | `--set-file <key>=tools/<tool>/<profile>/<file>` |
| `install.set_from_profile` | copies keys from a profile file into chart values (`--set-string`) |
| `install.manifests`, `install.container`, `install.from_adapter` | for `manifests`: the base files and the container that gets image, command, args, env, privileges and mounts from the adapter's `ContainerSpec` |
| `agent.selector` | label selector of the agent DaemonSet pods |
| `agent.log_containers` | containers whose logs are followed (readiness and alerts) |
| `agent.alerts_container` | container read when the adapter declares an `alerts_file`: its logs, or the file below |
| `agent.alerts_file` | absolute path of the alerts file inside `alerts_container`. When it is set, the backend reads the file with `tail -n +1 -F` over the exec API instead of following container logs, and `emitted_at` is the read time (as for `alerts_file` in Docker mode) |
| `agent.ready_pattern` | `adapter` reuses the adapter's `ready_pattern`; otherwise a regex override, or `null` |
| `agent.startup_timeout` | seconds allowed for the agent pod to start and then for the ready pattern; default: the adapter's `startup_timeout`. KubeArmor sets 600 because its `kubearmor-init` container can be slow |
| `configmaps` | ConfigMaps generated from `tools/<tool>/<profile>/<source>` (a file or the top-level files of a directory) |
| `custom_resources` | policy files in `tools/<tool>/<profile>/<source>` applied as custom resources |
| `restart_after_resources` | restart the agent DaemonSet after the custom resources are applied |

The rule and policy files are never copied. Each run builds ConfigMaps, `--set-file` arguments or custom resources
from `tools/<tool>/<profile>/`.

| Tool | Deployment | Version | Rules and policies |
|---|---|---|---|
| Falco | chart `falcosecurity/falco` 9.1.0, image tag 0.45.0 (the adapter version), `modern_ebpf` driver | 0.45.0 | an `emptyDir` hides the image's `/etc/falco/config.d`; ConfigMap `bench-falco-config` (`falco.bench.yaml`) mounted at `/etc/falco/config.d/zz-bench.yaml`; tuned adds ConfigMap `bench-falco-rules` (`rules.d/`) at `/etc/falco/bench/rules.d` |
| Tetragon | chart `cilium/tetragon` 1.7.0, `export.mode: ""` (no `export-stdout` sidecar), export file `/var/lib/ebpf-bench/tetragon/tetragon.log` read through exec | chart default | `tetragon.tp.d/*.yaml` applied as `TracingPolicy` resources (`cilium.io/v1alpha1`) |
| Tracee | chart `aqua/tracee` 0.24.1, operator and chart default policy disabled | 0.24.1 | `--set-file configFile=config.yaml`; `policies/*.yaml` applied as `Policy` resources (`tracee.aquasec.com/v1beta1`), then the DaemonSet is restarted so Tracee loads them at startup |
| KubeArmor | chart `kubearmor/kubearmor` v1.7.5, relay disabled, `-logPath=/dev/stdout` | v1.7.5 | the keys of `kubearmor.yaml` (visibility, postures, throttling) copied into `kubearmorConfigMap`; `policies/*.json` (KubeArmor backup format) converted to `KubeArmorPolicy` resources in the `ebpf-bench` namespace |
| Kunai | DaemonSet `tools/kunai/daemonset.yaml`, image `ebpf-bench/kunai:0.6.2` built from `tools/kunai/Dockerfile` | 0.6.2 | the profile directory becomes ConfigMap `bench-kunai-0` mounted where the adapter mounts it (`/etc/kunai`) |
| Pulsar | DaemonSet `tools/pulsar/daemonset.yaml`, image from the adapter | adapter | profile directory and `rules/` become ConfigMaps at the adapter's mount targets |

For `manifests` tools, the DaemonSet is built from the adapter's `ContainerSpec`:

- files and directories under `tools/` become ConfigMaps;
- host paths become `hostPath` volumes, except the Docker socket and `/var/lib/docker`, which do not exist on a containerd node;
- a mount of the run output directory becomes an `emptyDir`. If the adapter declares an `alerts_file`, an `alerts`
  sidecar (`busybox:1.36.1`) tails it to stdout.

Neither Kunai nor Pulsar ships an upstream Kubernetes deployment (checked in their repositories).

## End-to-end run on kind

Requirements on the host: Docker, [kind](https://kind.sigs.k8s.io/) 0.29 or later, and a kernel with BTF. `helm`
3.16.4 and `kubectl` 1.33.1 are already installed in the runner image.

```sh
kind create cluster --config deploy/kubernetes/kind.yaml

docker compose build victim attacker bench-k8s
docker build -t ebpf-bench/kunai:0.6.2 tools/kunai
kind load docker-image --name ebpf-bench ebpf-bench/victim:latest ebpf-bench/attacker:latest ebpf-bench/kunai:0.6.2
```

If `kind load docker-image` (or `kind load image-archive`) fails with `ERROR: failed to detect containerd
snapshotter`, as it did on the kind / WSL2 host, import the images with `ctr` in the node instead:

```sh
docker save ebpf-bench/victim:latest ebpf-bench/attacker:latest ebpf-bench/kunai:0.6.2 -o images.tar
docker exec -i ebpf-bench-control-plane ctr -n k8s.io images import --all-platforms - < images.tar
```

You can pre-pull the tool images (`falcosecurity/falco:0.45.0`, `quay.io/cilium/tetragon:*`,
`aquasec/tracee:0.24.1`, `kubearmor/*:v1.7.5`, `ghcr.io/exein-io/pulsar:*`) and load them the same way. Otherwise
the kind node pulls them itself, which needs registry access from the node. Behind a TLS-intercepting proxy, the
node needs the proxy CA (here copied from the host's `/usr/local/share/ca-certificates`):

```sh
docker cp /usr/local/share/ca-certificates/. ebpf-bench-control-plane:/usr/local/share/ca-certificates/
docker exec ebpf-bench-control-plane sh -c "update-ca-certificates && systemctl restart containerd"
```

Optional, for CPU and memory sampling of the tool pods (not installed in the kind / WSL2 runs, so those runs have
no tool CPU or memory figures):

```sh
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.7.2/components.yaml
kubectl -n kube-system patch deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"},{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--metric-resolution=15s"}]'
```

Run the benchmark:

```sh
docker compose up -d bench-k8s
docker compose logs -f bench-k8s
```

`bench-k8s` runs `bench run --config bench.yaml --backend kubernetes` with:

- `network_mode: host`, so the kind API server on `127.0.0.1` is reachable;
- `~/.kube` mounted read-only at `/root/.kube`. Override it with `KUBECONFIG_DIR` and `KUBECONFIG_FILE`.

The context and the namespace come from the `kubernetes:` section of `bench.yaml`:

```yaml
backend: docker            # or kubernetes; --backend overrides it
kubernetes:
  kubeconfig: null         # path inside the runner container, null = $KUBECONFIG or ~/.kube/config
  context: kind-ebpf-bench
  namespace: ebpf-bench    # namespace of the victim, attacker and workload pods
  node: null               # node that runs the victims and whose agent pod is followed, null = first Ready node
```

Results land in `results/<run_id>/` exactly as in Docker mode. `metadata.json` has `config.backend: kubernetes`,
and the `host` section describes the node: kernel, OS image, containerd, kubelet and server versions.

## How it works

For every tool and profile:

1. Create the tool namespace and the ConfigMaps.
2. `helm upgrade --install` (or create the DaemonSet), then apply the custom resources. The backend retries while
   the CRD is not yet registered.
3. Wait for an agent pod on the bench node whose `log_containers` are running. Image pull errors, `CrashLoopBackOff`
   and similar states fail fast.
4. Follow the logs of those containers with `follow=True, timestamps=True`. Each line's `emitted_at` is the
   kubelet/containerd timestamp, the same as the Docker log timestamp in Docker mode. Lines from several containers
   are merged into one buffer and passed unchanged to the adapter's `parse()`.
5. Wait for the ready pattern while checking that the pod has not failed or restarted.
6. Create the attacker Deployment and Service and the victim pods, pinned with `nodeName` to the bench node. The
   victims get no service account token, so the honey token baked into the victim image stays visible.
7. Run each scenario with the Kubernetes exec API as `timeout --kill-after=5 <timeout> env BENCH_MARKER=... sh
   /scenarios/<id>/run.sh`. Exec cannot pass environment variables, hence `env`. Exit code 124 means timeout, as in
   Docker mode. The runner also gives up 15 s after the deadline.
8. Sample tool pod CPU and memory from `metrics.k8s.io` every 5 s, summed over the pod's containers. CPU is in
   percent of one core, memory is the working set. Without metrics-server, the samples are empty lists and the
   report shows no resource figures.
9. `helm uninstall --wait` (or delete the objects), delete the custom resources and ConfigMaps, wait for the agent
   pods to disappear, and drain the log streams.

### Diagnostics on start failure

A failed start is uninstalled right away, so the pods and their logs are gone afterwards. Before that, when the
install, the pod start or the ready wait fails (including timeouts), the backend collects for every agent pod of the
tool on the bench node:

- the pod phase, its non-`True` conditions, and the state of every container and init container (reason, message,
  exit code, restart count, last terminated state);
- the last 200 log lines of every container and init container, plus the `previous=True` logs when the container has
  restarted or has a terminated last state. A log that cannot be read is recorded as `logs unavailable: <reason>`;
- all Events of the tool namespace (type, reason, count, message, involved object), which covers image pull errors,
  `FailedMount`, `BackOff` and DaemonSet `FailedCreate`.

These lines are appended to `results/<run>/raw/<tool>-<profile>/container.log`, in the usual `<emitted_at> <line>`
format. Log lines keep their kubelet timestamp, events use their `lastTimestamp`, and the other lines use the time
of collection. Each line is prefixed with its source:

```
1767323099.000000 [falco-x/falco] Error: could not load BPF probe
1767323099.000000 [falco-x/falco previous] ...
1767323100.000000 [falco-x] init container falco-driver-loader: terminated exit_code=0 reason=Completed ...
1767323100.000000 [event Pod/falco-x] Warning BackOff x3: Back-off restarting failed container falco
```

The error message, stored in `metadata.json` and printed in the run log, ends with a short summary: the state of the
failing container (the first init container that did not complete, otherwise the first container that terminated,
waits or restarted), its last 20 log lines (unless they already appear under `last logs:`), and the last 10
`Warning` events.

### Attribution

The scoring code is unchanged:

- `ScenarioRun.victim_container_id` is the victim's containerd ID, read from the pod status with `containerd://`
  stripped. The existing ID prefix match therefore works against the IDs reported by the tools: Falco (12
  characters), Tetragon `process.docker` (31 characters), Tracee and KubeArmor (64 characters).
- Each victim pod and its container have the same name (`bench-victim`, `bench-victim-priv`), so the name match
  works whether a tool reports the Kubernetes container name or the pod name:
  - Falco, Tetragon, Tracee and KubeArmor report the container name;
  - Kunai reports the UTS hostname, which is the pod hostname set to the same value.
- KubeArmor may report the 64-hex ID as `ContainerName` before its pod watcher has caught up. The ID match still
  applies in that case.
- Pulsar only resolves Docker and Podman containers, so under containerd its alerts carry no container. They are
  attributed only through `BENCH_MARKER`, the same as host-level alerts.
- The victim pods carry the label `kubearmor.io/container.name: bench-victim`. Both victims therefore match the
  KubeArmor policy selector, which is what the unanchored regex does in Docker mode.

## Known differences from Docker mode

- **Host scope on kind.** kind nodes are containers. `hostPID` and `hostNetwork` pods see the node container's
  namespaces, not the real host's. The eBPF programs still see every process on the kernel, including unrelated
  Docker containers on the host. Tetragon reads the real host `/proc` through the `/procHost` extra mount, as in the
  Tetragon kind guide. Under WSL2 that host `/proc` is not the kernel's initial PID namespace, see
  [Validated on kind / WSL2](#validated-on-kind--wsl2).
- **Scenarios.** They come from the victim image (`COPY scenarios/ /scenarios/`), not from a bind mount. Rebuild and
  `kind load` the victim image after changing a scenario.
- **Network.** The victims reach `attacker` through a ClusterIP Service: kube-proxy DNAT, ports 8080, 4444 and 3333.
  In Docker mode they connect directly on a bridge network. Tools that record destination IPs see the Service IP.
- **Tool configuration.** It comes from the charts plus the profile files:
  - Falco: rules come from the image, because `falcoctl` artifact install and follow are disabled for
    reproducibility and offline runs.
  - Tetragon: the chart's own `tetragon.conf.d` is used, not `tools/tetragon/<profile>/tetragon.conf.d`, and its
    export deny list is aligned with the Docker profile.
  - Tracee: reads its policies from the Kubernetes API.
  - KubeArmor: runs in Kubernetes mode, with the posture and visibility from the profile copied into its ConfigMap.
  - KubeArmor: alerts go to the daemon's stdout instead of the relay.
- **Timing.** `emitted_at` comes from the node clock and the scenario window from the runner clock. On kind they
  share the same clock. On a remote cluster, the nodes and the runner must be NTP-synchronised.
- **Resource sampling.** metrics-server aggregates over its resolution window (15 s at best), so a 30 s workload gets
  only a few samples, against one per second for `docker stats`.
- **cgroup namespace.** Kubernetes has no `cgroupns: host`.
- **Tetragon export: no stdout, no `/var/log`.** The upstream default policy `file-monitoring-filtered` (kept
  verbatim) reports every write under `/var/log`, and the export deny list keeps host events. With the chart's
  `export.mode: stdout`, this made a feedback loop on kind: the `export-stdout` sidecar printed each event,
  containerd wrote that line to `/var/log/pods/<ns>_<pod>_<uid>/export-stdout/0.log`, Tetragon reported that write
  (`security_file_permission`, process with flags `unknown`), the sidecar printed the new event, and so on. One
  `default` run produced a 6.4 GB `container.log` in 25 minutes, and it kept growing after the scenarios ended.
  The chart default `exportDirectory: /var/log/tetragon` loops in the same way through Tetragon's own writes. The
  fix is in the deployment, not in the policies:
  - `export.mode: ""` removes the `export-stdout` sidecar, so exported events never reach a container's stdout or
    `/var/log/pods`;
  - `exportDirectory: /var/lib/ebpf-bench/tetragon` (a `hostPath`, disk-backed on kind) keeps the export file out
    of `/var/log`, as the Docker profile does;
  - `tetragon.exportFileMaxSizeMB: 2048` and `exportFileMaxBackups: 1`, so `tail -F` follows one file per run
    (Docker mode also rotates at 2048 MB);
  - `tetragon.commandOverride` runs `/bin/sh -c 'rm -f /var/lib/ebpf-bench/tetragon/tetragon*.log && exec
    /usr/bin/tetragon "$@"'` with the chart args unchanged. The `hostPath` outlives the pod and Tetragon appends to
    an existing export file, so without this a run would read the events of the previous profile;
  - `agent.alerts_file` makes the backend run `tail -n +1 -F /var/lib/ebpf-bench/tetragon/tetragon.log` in the
    `tetragon` container through the exec API (the image is Alpine-based, so BusyBox `tail` is available) and use
    the read time as `emitted_at`. The exec stream goes through the API server and kubelet, not through
    `/var/log/pods`. The backend still follows the `tetragon` container logs, which are low-volume agent logs, for
    the ready pattern.

  Tetragon still reports containerd's writes of every pod's log under `/var/log/pods` (the agent's own logs, the
  victims' output). That is the upstream policy doing what it says, and it is counted as non-victim noise. As a
  safeguard for every tool, the runner caps what it buffers (`max_log_lines`, `max_log_bytes`, see "Log cap" in
  `docs/methodology.md`).

## Validated on kind / WSL2

Host: WSL2, kernel `6.6.87.2-microsoft-standard-WSL2`, kind node `kindest/node:v1.33.1`, containerd 2.1.1, single
node created from `kind.yaml`. No metrics-server was installed, so these runs measure workload latency overhead but
not tool CPU or memory.

| Tool | Version (chart) | Result on kind / WSL2 |
|---|---|---|
| Falco | 0.45.0 (chart 9.1.0) | works after one fix to the values (below); full run: same recall and FP rate as Docker mode in both profiles |
| Tracee | 0.24.1 (chart 0.24.1) | works; full run: same recall and FP rate as Docker mode in both profiles |
| Kunai | 0.6.2 (DaemonSet) | works; full run: same recall and FP rate as Docker mode in both profiles |
| Pulsar | 0.10.1 (DaemonSet) | crashed the host during its overhead workloads, twice at the same step: not scored |
| Tetragon | 1.7.1 (chart 1.7.0) | blocked on this host: events cannot be tied to pods (0% recall in both profiles) |
| KubeArmor | v1.7.5 (chart v1.7.5) | starts and loads the policies, but 0 alerts: containers are registered with `pidns=0/mntns=0` |

### Falco: duplicate container plugin

The image ships `/etc/falco/config.d/falco.container_plugin.yaml` and the chart also loads the container plugin, so
Falco aborted at startup:

```
Runtime error: cannot register plugin /usr/share/falco/plugins/libcontainer.so in inspector: found another plugin with name container
```

Fix, in `values-default.yaml` and `values-tuned.yaml`: an `emptyDir` is mounted over `/etc/falco/config.d`, and the
benchmark drop-in is still mounted at `/etc/falco/config.d/zz-bench.yaml`. The chart's container plugin
configuration, with its containerd sockets, is then the only one loaded.

### Tracee and Kunai

Both work without change. Tracee logs `Cgroup mountpoint is not in the host cgroup namespace` and `error enriching
container in control plane ... already deleted` warnings. They had no effect on attribution.

### Full run

Run [`20261024T114807Z`](../../results/20261024T114807Z/report.md): Falco, Tracee and Kunai in the default and
tuned profiles, 5 repetitions, control phase and overhead workloads. Their recall and false positive rate match
Docker mode in every profile. Two differences:

- `t1046-network-scan` is invalid here (0/5 in the control runs). The attacker is reached through a ClusterIP
  Service that only exposes 8080, 4444 and 3333; connections to the other scanned ports get no answer, so the scan
  hits its 45 s timeout before it reports the open port. In Docker mode the attacker refuses them immediately.
- Kunai default prints every host event and exceeded the runner's log cap: 20.8 million lines were dropped. That
  profile has no rules, so its result (0 alerts) is unchanged.

### Pulsar

In smoke runs about 99% of Pulsar's log lines are `Process not found in tracker N: process not found` (from
`network-monitor` and `file-system-monitor`). Threat events are still produced, but they carry no container: Pulsar
resolves Docker and Podman containers only, not containerd. Attribution would rely on `BENCH_MARKER`, as for
host-level alerts in Docker mode.

In the full runs `20261023T132537Z` and `20261024T114807Z`, Pulsar default stopped the host at the same step: during
its overhead workloads, `syscall` repetition 2 timed out after 150 s, then Docker and the WSL2 VM exited (the runner
container exited with code 255) during `exec` repetition
2. The workload numbers recorded before the crash are in the report, but the deployment is marked failed and has no
detection result. The cause was not investigated further; in Docker mode on the same host Pulsar used up to 156% CPU
and 572 MiB, the highest of all tools.

### Tetragon

Two findings.

1. **Feedback loop through `/var/log` (fixed, applies to any cluster).** Described under "Tetragon export: no
   stdout, no `/var/log`" above: the `export-stdout` sidecar and `/var/log/pods` fed `file-monitoring-filtered` its
   own output (6.4 GB of logs in 25 minutes, control-plane components restarted). With `export.mode: ""`,
   `exportDirectory: /var/lib/ebpf-bench/tetragon`, the exec `tail -F` of the export file and the runner log cap
   (`max_log_lines` / `max_log_bytes`), the smoke run gave about 2,400 to 4,000 alerts per profile instead of
   167,000.
2. **Host procfs (not fixable on WSL2).** Tetragon logs:

   ```
   inode mismatch: procfs does not appear to be host procfs path=/procRoot/1/ns/pid inode=4026532221 expected inode=4026531836
   ```

   Tetragon needs the procfs of the kernel's initial PID namespace. On a native Linux host, the kind node's
   `/procHost` mount (the host `/proc`) is that namespace, as in the upstream kind guide. Under WSL2 the Linux
   distribution itself runs in a non-initial PID namespace of the WSL utility VM, so neither `/procHost` (inode
   4026532221) nor the node's own `/proc` (4026532310, also tested) qualifies. As a result, 2,495 of the 2,537 policy
   events reference processes Tetragon never saw exec (`"flags":"unknown"`, no pod, no container id). Nothing can be
   attributed: 0% recall in both profiles, including the `/etc/shadow` read, which is visible in the events.
   `hostProcPath` stays `/procHost`, the upstream recommendation, which is correct on native Linux.

### KubeArmor

KubeArmor needs `agent.startup_timeout: 600` because its `kubearmor-init` container is slow. It then loads the
policies (`Detected a Security Policy (added/ebpf-bench/...)`) and detects the victim pods, but registers every
container with `pidns=0/mntns=0`. No kernel event matches the victims' policies, so there are 0 alerts. The likely
cause suggested here, namespace resolution in nested PID namespaces under WSL2, is ruled out: the same
registration happens on a native kernel (see [Validated on kind / native Linux](#validated-on-kind--native-linux)).
KubeArmor also logs `BPF LSM not supported` and `Disabled KubeArmor Enforcer`: no enforcement on WSL2, as in Docker
mode.

### Conclusion

On kind / WSL2, Falco, Tracee and Kunai can be compared in Kubernetes mode. A valid Kubernetes comparison of
Tetragon, KubeArmor and Pulsar needs a native Linux node (bare metal or VM), not kind on WSL2.

## Validated on kind / native Linux

Host: Debian 13, kernel 6.12.105 with BTF and BPF-LSM, 8 CPUs, 30.9 GiB, Docker 26.1.5, kind 0.29.0 with
`kindest/node:v1.33.1` (containerd 2.1.1), metrics-server 0.7.2. The tool images were pulled into the node with
`crictl pull` before the run: the network needed almost 7 minutes for `kubearmor-init` alone, which would otherwise
count as time to ready. `bench.yaml` raised the log cap to 15 million lines.

| Tool | Result |
|---|---|
| Falco | default and tuned: same recall and false positive rate as Docker mode |
| Tetragon | default and tuned: same recall and false positive rate as Docker mode; the WSL2 procfs blocker does not exist here |
| Tracee | default and tuned: same recall and false positive rate as Docker mode |
| Kunai | all four profiles run (DaemonSet); same recall as Docker mode; enforce prevented 0 of 23 valid attacks, its kills only hit the victim pods |
| KubeArmor | 0 alerts in default and tuned: containers still registered with `pidns=0/mntns=0`, so the cause is kind's nested runtime, not WSL2; the controller never starts (`runAsNonRoot` with an image that runs as root) |
| Pulsar | `pulsard` reached 28.6 GiB RSS three minutes after start, during the second `fileio` workload; the host ran out of memory and the API server stopped answering; not scored |

- **Profiles**: `tool.yaml` of the Helm-based tools only maps `default` and `tuned`. Enforce and community were not
  added for this run. Tetragon enforce in particular is unsafe on kind as written: its Sigkill selectors exclude the
  host mount namespace, but the node's `kubelet` and `containerd` run in the kind container's namespace, and the
  `/var/log` rule of `history-and-log-tampering` would match their pod log cleanup.
- **Pulsar** ran in a separate runner because the first one held 18 GiB of log lines after Kunai default.
- **Overhead** in kind is noisier than in Docker mode (Tetragon default shows a negative latency overhead); KubeArmor
  uses 4.8 to 5.7 GiB there against about 0.3 GiB in Docker mode.

## Open points

- KubeArmor on kind: find why containers register with `pidns=0/mntns=0` (containerd 2.x task PID resolution from the
  agent's `/host/procfs` is the first suspect) or validate on a multi-node cluster on bare nodes.
- Add `enforce` and `community` Helm values, with blocking policies scoped to Kubernetes namespaces
  (`TracingPolicyNamespaced` for Tetragon) so they cannot hit node daemons.
- Pulsar: bound its memory or report the growth upstream before running it again in Kubernetes mode.
- Pin the Tetragon image tag to the adapter version once the Tetragon adapter exists.
