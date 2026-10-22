# Kubernetes mode

> **Status: not validated on a real cluster.** The backend, the manifests and the Helm values were written against
> the upstream charts and the Kubernetes API. They are covered only by unit tests that mock the Kubernetes client
> and `helm` (`runner/tests/test_k8s_backend.py`). Nobody has run a full benchmark on kind or any other cluster from
> this repository yet. Treat the first runs as a shake-down and report what breaks.

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
| `agent.alerts_container` | container read when the adapter declares an `alerts_file` |
| `agent.ready_pattern` | `adapter` reuses the adapter's `ready_pattern`; otherwise a regex override, or `null` |
| `configmaps` | ConfigMaps generated from `tools/<tool>/<profile>/<source>` (a file or the top-level files of a directory) |
| `custom_resources` | policy files in `tools/<tool>/<profile>/<source>` applied as custom resources |
| `restart_after_resources` | restart the agent DaemonSet after the custom resources are applied |

The rule and policy files are never copied. Each run builds ConfigMaps, `--set-file` arguments or custom resources
from `tools/<tool>/<profile>/`.

| Tool | Deployment | Version | Rules and policies |
|---|---|---|---|
| Falco | chart `falcosecurity/falco` 9.1.0, image tag 0.45.0 (the adapter version), `modern_ebpf` driver | 0.45.0 | ConfigMap `bench-falco-config` (`falco.bench.yaml`) mounted at `/etc/falco/config.d/zz-bench.yaml`; tuned adds ConfigMap `bench-falco-rules` (`rules.d/`) at `/etc/falco/bench/rules.d` |
| Tetragon | chart `cilium/tetragon` 1.7.0, `export.mode: stdout` | chart default | `tetragon.tp.d/*.yaml` applied as `TracingPolicy` resources (`cilium.io/v1alpha1`) |
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

You can pre-pull the tool images (`falcosecurity/falco:0.45.0`, `quay.io/cilium/tetragon:*`,
`aquasec/tracee:0.24.1`, `kubearmor/*:v1.7.5`, `ghcr.io/exein-io/pulsar:*`) and `kind load` them too. Otherwise the
kind node pulls them itself, which needs registry access from the node: behind the corporate TLS proxy, add the
proxy CA to the node, see the kind documentation on private registries.

Optional, for CPU and memory sampling of the tool pods:

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
  Tetragon kind guide.
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

## Open points before the first real run

- Check the chart values against the exact chart versions, especially the Falco 9.1.0 chart driving Falco 0.45.0,
  and whether a 0.45-specific chart exists.
- Confirm that Tracee 0.24.1 loads `Policy` resources at startup without the operator.
- Confirm the Tetragon and Pulsar ready patterns in Kubernetes logs.
- Confirm that the KubeArmor `kubearmor.io/container.name` selector matches pods in Kubernetes mode.
- Pin the Tetragon image tag to the adapter version once the Tetragon adapter exists.
