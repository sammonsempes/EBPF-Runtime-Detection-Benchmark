from __future__ import annotations

import json
import subprocess
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from bench.adapters.base import ContainerSpec, Mount
from bench.config import KubernetesConfig, load_config, parse_config
from bench.docker_backend import ContainerRef, LineBuffer, ToolStartError
from bench.k8s_backend import (
    ADAPTER,
    KubeApi,
    KubernetesBackend,
    MetricsSampler,
    PodStartError,
    adapter_pod_spec,
    custom_resources,
    exec_command,
    helm_escape,
    helm_install_command,
    helm_uninstall_command,
    kubearmor_resource,
    load_tool_deployment,
    parse_cpu,
    parse_memory,
    pod_metrics_sample,
    pod_state,
    pump_log_streams,
    strip_container_id,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = ("falco", "tetragon", "tracee", "kubearmor", "kunai", "pulsar")
VICTIM_ID = "a" * 64
PRIV_ID = "b" * 64
ATTACKER_ID = "c" * 64
WORKLOAD_ID = "d" * 64


class ApiError(Exception):
    def __init__(self, status: int) -> None:
        super().__init__(f"status {status}")
        self.status = status


def running_status(name: str, cid: str, restarts: int = 0, ready: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        container_id=f"containerd://{cid}",
        ready=ready,
        restart_count=restarts,
        state=SimpleNamespace(running=SimpleNamespace(), waiting=None, terminated=None),
    )


def waiting_status(name: str, reason: str) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        container_id=None,
        ready=False,
        restart_count=0,
        state=SimpleNamespace(running=None, waiting=SimpleNamespace(reason=reason, message="boom"), terminated=None),
    )


def make_pod(name: str, statuses: list, uid: str | None = None, node: str = "node-1", phase: str = "Running"):
    return SimpleNamespace(
        metadata=SimpleNamespace(name=name, uid=uid or f"uid-{name}", deletion_timestamp=None, labels={}),
        spec=SimpleNamespace(node_name=node),
        status=SimpleNamespace(phase=phase, container_statuses=statuses),
    )


class FakeLogResponse:
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks
        self.closed = False

    def stream(self, amt=None, decode_content=False):
        yield from self.chunks

    def close(self) -> None:
        self.closed = True

    def release_conn(self) -> None:
        pass


class FakeCore:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str | None, str], dict] = {}
        self.pods: dict[tuple[str, str], SimpleNamespace] = {}
        self.calls: list[tuple] = []
        self.logs: dict[tuple[str, str], list[bytes]] = {}
        self.pod_statuses: dict[str, list] = {}
        self.selector_pods: dict[tuple[str, str], list] = {}
        self.nodes = [
            SimpleNamespace(
                metadata=SimpleNamespace(name="node-1"),
                spec=SimpleNamespace(unschedulable=False),
                status=SimpleNamespace(
                    conditions=[SimpleNamespace(type="Ready", status="True")],
                    node_info=SimpleNamespace(
                        kernel_version="6.6.0",
                        os_image="Debian GNU/Linux 12",
                        architecture="amd64",
                        container_runtime_version="containerd://2.1.1",
                        kubelet_version="v1.33.1",
                    ),
                    capacity={"cpu": "8", "memory": "16Gi"},
                ),
            )
        ]

    def _store(self, kind: str, namespace: str | None, body: dict) -> None:
        name = body["metadata"]["name"]
        key = (kind, namespace, name)
        if key in self.objects:
            raise ApiError(409)
        self.objects[key] = body
        self.calls.append(("create", kind, namespace, name))
        if kind == "Pod":
            container = body["spec"]["containers"][0]["name"]
            statuses = self.pod_statuses.get(name) or [running_status(container, self._cid(name))]
            self.pods[(namespace, name)] = make_pod(name, statuses)

    @staticmethod
    def _cid(name: str) -> str:
        return {"bench-victim": VICTIM_ID, "bench-victim-priv": PRIV_ID, "bench-workload": WORKLOAD_ID}.get(name, "e" * 64)

    def _remove(self, kind: str, namespace: str | None, name: str) -> None:
        self.calls.append(("delete", kind, namespace, name))
        if self.objects.pop((kind, namespace, name), None) is None:
            raise ApiError(404)
        if kind == "Pod":
            self.pods.pop((namespace, name), None)

    def _read(self, kind: str, namespace: str | None, name: str) -> dict:
        if (kind, namespace, name) not in self.objects:
            raise ApiError(404)
        return self.objects[(kind, namespace, name)]

    def create_namespace(self, body):
        self._store("Namespace", None, body)

    def read_namespace(self, name):
        self._read("Namespace", None, name)
        return SimpleNamespace(status=SimpleNamespace(phase="Active"))

    def create_namespaced_config_map(self, namespace, body):
        self._store("ConfigMap", namespace, body)

    def replace_namespaced_config_map(self, name, namespace, body):
        self.calls.append(("replace", "ConfigMap", namespace, name))
        self.objects[("ConfigMap", namespace, name)] = body

    def delete_namespaced_config_map(self, name, namespace, **kwargs):
        self._remove("ConfigMap", namespace, name)

    def read_namespaced_config_map(self, name, namespace):
        return self._read("ConfigMap", namespace, name)

    def create_namespaced_service(self, namespace, body):
        self._store("Service", namespace, body)

    def read_namespaced_service(self, name, namespace):
        return self._read("Service", namespace, name)

    def delete_namespaced_service(self, name, namespace, **kwargs):
        self._remove("Service", namespace, name)

    def list_namespaced_service(self, namespace, label_selector=None):
        return SimpleNamespace(items=[])

    def create_namespaced_pod(self, namespace, body):
        self._store("Pod", namespace, body)

    def read_namespaced_pod(self, name, namespace):
        if (namespace, name) not in self.pods:
            raise ApiError(404)
        return self.pods[(namespace, name)]

    def delete_namespaced_pod(self, name, namespace, **kwargs):
        self._remove("Pod", namespace, name)

    def list_namespaced_pod(self, namespace, label_selector=None):
        return SimpleNamespace(items=list(self.selector_pods.get((namespace, label_selector), [])))

    def list_node(self):
        return SimpleNamespace(items=self.nodes)

    def read_node(self, name):
        return self.nodes[0]

    def connect_get_namespaced_pod_exec(self, *args, **kwargs):
        raise AssertionError("must be called through stream")

    def read_namespaced_pod_log(self, name, namespace, container=None, **kwargs):
        self.calls.append(("logs", namespace, name, container, kwargs.get("timestamps"), kwargs.get("follow")))
        return FakeLogResponse(self.logs.get((name, container), []))


class FakeApps:
    def __init__(self, core: FakeCore) -> None:
        self.core = core
        self.patches: list[tuple] = []

    def create_namespaced_deployment(self, namespace, body):
        self.core._store("Deployment", namespace, body)

    def read_namespaced_deployment(self, name, namespace):
        return self.core._read("Deployment", namespace, name)

    def delete_namespaced_deployment(self, name, namespace, **kwargs):
        self.core._remove("Deployment", namespace, name)

    def list_namespaced_deployment(self, namespace, label_selector=None):
        return SimpleNamespace(items=[])

    def create_namespaced_daemon_set(self, namespace, body):
        self.core._store("DaemonSet", namespace, body)

    def read_namespaced_daemon_set(self, name, namespace):
        return self.core._read("DaemonSet", namespace, name)

    def delete_namespaced_daemon_set(self, name, namespace, **kwargs):
        self.core._remove("DaemonSet", namespace, name)

    def list_namespaced_daemon_set(self, namespace):
        return SimpleNamespace(items=[SimpleNamespace(metadata=SimpleNamespace(name="tracee"))])

    def patch_namespaced_daemon_set(self, name, namespace, body):
        self.patches.append((name, namespace, body))


class FakeCustom:
    def __init__(self) -> None:
        self.created: list[tuple] = []
        self.deleted: list[tuple] = []
        self.missing_crd = 0
        self.metrics: dict | None = None

    def create_cluster_custom_object(self, group, version, plural, body):
        if self.missing_crd:
            self.missing_crd -= 1
            raise ApiError(404)
        self.created.append((group, version, None, plural, body))

    def create_namespaced_custom_object(self, group, version, namespace, plural, body):
        self.created.append((group, version, namespace, plural, body))

    def delete_cluster_custom_object(self, group, version, plural, name):
        self.deleted.append((group, version, None, plural, name))

    def delete_namespaced_custom_object(self, group, version, namespace, plural, name):
        self.deleted.append((group, version, namespace, plural, name))

    def get_namespaced_custom_object(self, group, version, namespace, plural, name):
        if self.metrics is None:
            raise ApiError(404)
        return self.metrics


class FakeExecClient:
    def __init__(self, stdout: list[str], stderr: list[str], returncode: int, hang: bool = False, tick=None) -> None:
        self.stdout = list(stdout)
        self.stderr = list(stderr)
        self._returncode = returncode
        self.hang = hang
        self.tick = tick
        self.updates = 0
        self.closed = False
        self._pending_out = ""
        self._pending_err = ""

    def is_open(self) -> bool:
        return self.hang or bool(self.stdout or self.stderr)

    def update(self, timeout=0):
        self.updates += 1
        if self.tick is not None:
            self.tick()
        if self.stdout:
            self._pending_out += self.stdout.pop(0)
        if self.stderr:
            self._pending_err += self.stderr.pop(0)

    def peek_stdout(self, timeout=0):
        return self._pending_out

    def peek_stderr(self, timeout=0):
        return self._pending_err

    def read_stdout(self, timeout=None):
        value, self._pending_out = self._pending_out, ""
        return value

    def read_stderr(self, timeout=None):
        value, self._pending_err = self._pending_err, ""
        return value

    @property
    def returncode(self):
        return self._returncode

    def close(self):
        self.closed = True


class FakeStream:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.client: FakeExecClient | None = None

    def __call__(self, method, name, namespace, **kwargs):
        self.calls.append({"method": method, "name": name, "namespace": namespace, **kwargs})
        return self.client


class FakeRunner:
    def __init__(self, returncode: int = 0, stderr: str = "") -> None:
        self.commands: list[list[str]] = []
        self.returncode = returncode
        self.stderr = stderr

    def __call__(self, command, **kwargs):
        self.commands.append(list(command))
        return subprocess.CompletedProcess(command, self.returncode, stdout="", stderr=self.stderr)


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += max(seconds, 0.5)


def make_backend(repo_root: Path = REPO_ROOT, runner: FakeRunner | None = None):
    core = FakeCore()
    stream = FakeStream()
    api = KubeApi(core=core, apps=FakeApps(core), custom=FakeCustom(), stream=stream)
    clock = FakeClock()
    backend = KubernetesBackend(
        repo_root,
        Path("/host/repo"),
        KubernetesConfig(context="kind-ebpf-bench"),
        api=api,
        runner=runner or FakeRunner(),
        clock=clock,
        monotonic=clock,
        sleep=clock.sleep,
        metrics_interval=0.01,
    )
    return backend, api, clock


def test_host_info_keeps_only_kind_node_names() -> None:
    backend, api, _ = make_backend()
    info = backend.host_info()
    assert info["kernel"] == "6.6.0" and info["cpus"] == 8
    assert "hostname" not in info and info["node"] is None
    assert "node-1" not in repr(info)
    api.core.nodes[0].spec.provider_id = "kind://docker/ebpf-bench/ebpf-bench-control-plane"
    assert backend.host_info()["node"] == "node-1"


def test_strip_container_id_and_quantities() -> None:
    assert strip_container_id("containerd://abc") == "abc"
    assert strip_container_id("cri-o://xyz") == "xyz"
    assert strip_container_id(None) == ""
    assert parse_cpu("250m") == pytest.approx(0.25)
    assert parse_cpu("1500000n") == pytest.approx(0.0015)
    assert parse_cpu("2") == 2.0
    assert parse_cpu("") is None
    assert parse_memory("1Ki") == 1024.0
    assert parse_memory("64Mi") == 64 * 1024.0**2
    assert parse_memory("1G") == 1e9
    assert parse_memory("123") == 123.0
    assert parse_memory("bogus") is None


def test_pod_metrics_sample_sums_containers() -> None:
    data = {
        "timestamp": "2026-01-01T00:00:00Z",
        "containers": [
            {"name": "tetragon", "usage": {"cpu": "500m", "memory": "100Mi"}},
            {"name": "export-stdout", "usage": {"cpu": "100m", "memory": "28Mi"}},
        ],
    }
    stamp, cpu, memory = pod_metrics_sample(data)
    assert stamp == "2026-01-01T00:00:00Z"
    assert cpu == pytest.approx(60.0)
    assert memory == 128 * 1024.0**2
    assert pod_metrics_sample({"containers": []}) is None
    assert pod_metrics_sample(None) is None


def test_exec_command_wraps_timeout_and_environment() -> None:
    command = exec_command(["sh", "/scenarios/x/run.sh"], {"BENCH_MARKER": "m1", "BENCH_ATTACKER": "attacker"}, 30)
    assert command == [
        "timeout",
        "--kill-after=5",
        "30",
        "env",
        "BENCH_ATTACKER=attacker",
        "BENCH_MARKER=m1",
        "sh",
        "/scenarios/x/run.sh",
    ]


def test_helm_escape() -> None:
    assert helm_escape("process,file,network") == "process\\,file\\,network"
    assert helm_escape(True) == "true"
    assert helm_escape(10) == "10"


def test_pod_state() -> None:
    assert pod_state(make_pod("p", [running_status("c", "x")]), ["c"]) == ("ready", "running")
    assert pod_state(make_pod("p", [running_status("c", "x", ready=False)]), ["c"])[0] == "pending"
    assert pod_state(make_pod("p", [running_status("c", "x", ready=False)]), ["c"], require_ready=False)[0] == "ready"
    assert pod_state(make_pod("p", [waiting_status("c", "ErrImageNeverPull")]), ["c"])[0] == "failed"
    assert pod_state(make_pod("p", [waiting_status("c", "ContainerCreating")]), ["c"])[0] == "pending"
    assert pod_state(make_pod("p", []), ["c"])[0] == "pending"
    assert pod_state(make_pod("p", [], phase="Failed"), ["c"])[0] == "failed"


def test_pump_log_streams_merges_and_closes() -> None:
    buffer = LineBuffer()
    first = lambda: iter([b"2026-01-02T03:04:05.5Z hel", b"lo\n"])
    second = lambda: iter([b"2026-01-02T03:04:06Z world\n2026-01-02T03:04:07Z tail"])
    pump_log_streams([first, second], buffer)
    assert buffer.wait_closed(5)
    lines = sorted(buffer.lines())
    expected = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC).timestamp() + 0.5
    assert lines[0] == (pytest.approx(expected), "hello")
    assert [line for _, line in lines] == ["hello", "world", "tail"]
    empty = LineBuffer()
    pump_log_streams([], empty)
    assert empty.closed


def test_metrics_sampler_deduplicates_and_handles_missing() -> None:
    samples = iter([("t1", 10.0, 100.0), ("t1", 10.0, 100.0), ("t2", 20.0, None), None])

    def fetch():
        return next(samples, None)

    sampler = MetricsSampler(fetch, interval=0.01)
    time.sleep(0.2)
    cpu, memory = sampler.stop()
    assert cpu == [10.0, 20.0]
    assert memory == [100.0]
    failing = MetricsSampler(lambda: (_ for _ in ()).throw(RuntimeError("no metrics")), interval=0.01)
    time.sleep(0.05)
    assert failing.stop() == ([], [])


@pytest.mark.parametrize("tool", TOOLS)
def test_repository_tool_deployments_are_valid(tool: str) -> None:
    deployment = load_tool_deployment(REPO_ROOT, tool)
    assert deployment.tool == tool
    assert deployment.namespace.startswith("ebpf-bench-")
    assert deployment.alerts_container
    assert deployment.ready_pattern == ADAPTER
    if deployment.kind == "helm":
        for profile in ("default", "tuned"):
            assert (deployment.directory / deployment.install["values"][profile]).is_file()
        assert deployment.install["version"]
    else:
        for name in deployment.install["manifests"]:
            assert (deployment.directory / name).is_file()


def test_missing_tool_deployment(tmp_path: Path) -> None:
    with pytest.raises(ToolStartError, match="no Kubernetes deployment"):
        load_tool_deployment(tmp_path, "falco")


def test_helm_install_command_for_tracee() -> None:
    deployment = load_tool_deployment(REPO_ROOT, "tracee")
    profile_dir = REPO_ROOT / "tools" / "tracee" / "tuned"
    command = helm_install_command(deployment, "tuned", profile_dir, KubernetesConfig(context="kind-x", kubeconfig="/k"))
    assert command[:5] == ["helm", "upgrade", "--install", "tracee", "tracee"]
    assert command[command.index("--repo") + 1] == "https://aquasecurity.github.io/helm-charts"
    assert command[command.index("--version") + 1] == "0.24.1"
    assert command[command.index("--namespace") + 1] == "ebpf-bench-tracee"
    assert command[command.index("--values") + 1].endswith("deploy/kubernetes/tools/tracee/values-tuned.yaml")
    assert command[command.index("--set-file") + 1] == f"configFile={profile_dir / 'config.yaml'}"
    assert command[-4:] == ["--kubeconfig", "/k", "--kube-context", "kind-x"]


def test_helm_install_command_sets_kubearmor_config_from_profile() -> None:
    deployment = load_tool_deployment(REPO_ROOT, "kubearmor")
    profile_dir = REPO_ROOT / "tools" / "kubearmor" / "tuned"
    command = helm_install_command(deployment, "tuned", profile_dir, KubernetesConfig())
    sets = [command[index + 1] for index, item in enumerate(command) if item == "--set-string"]
    assert "kubearmorConfigMap.visibility=process\\,file\\,network\\,capabilities" in sets
    assert "kubearmorConfigMap.defaultFilePosture=audit" in sets
    assert "kubearmorConfigMap.alertThrottling=true" in sets
    assert "--kube-context" not in command


def test_helm_install_command_rejects_unknown_profile() -> None:
    deployment = load_tool_deployment(REPO_ROOT, "falco")
    with pytest.raises(ToolStartError, match="no Helm values"):
        helm_install_command(deployment, "paranoid", REPO_ROOT, KubernetesConfig())


def test_helm_uninstall_command() -> None:
    deployment = load_tool_deployment(REPO_ROOT, "falco")
    command = helm_uninstall_command(deployment, KubernetesConfig(context="kind-x"))
    assert command[:5] == ["helm", "uninstall", "falco", "--namespace", "ebpf-bench-falco"]
    assert "--wait" in command and "--ignore-not-found" in command
    assert command[-2:] == ["--kube-context", "kind-x"]


def test_kubearmor_backup_policies_become_custom_resources() -> None:
    document = json.loads(
        (REPO_ROOT / "tools/kubearmor/tuned/policies/tuned-shadow-file-access.json").read_text(encoding="utf-8")
    )
    resource = kubearmor_resource(document, "ebpf-bench", "security.kubearmor.com", "v1")
    assert resource.plural == "kubearmorpolicies"
    assert resource.namespace == "ebpf-bench"
    assert resource.body["apiVersion"] == "security.kubearmor.com/v1"
    assert resource.body["metadata"] == {"name": "tuned-shadow-file-access", "namespace": "ebpf-bench"}
    assert resource.body["spec"]["selector"]["matchLabels"] == {"kubearmor.io/container.name": "bench-victim"}
    host = kubearmor_resource({"kind": "KubeArmorHostPolicy", "metadata": {"policyName": "h"}}, "ns", "g", "v1")
    assert host.namespace is None and host.plural == "kubearmorhostpolicies"
    with pytest.raises(ToolStartError):
        kubearmor_resource({"kind": "Other", "metadata": {"policyName": "x"}}, "ns", "g", "v1")


def test_custom_resources_from_manifests() -> None:
    entry = {"source": "policies", "format": "manifest", "group": "tracee.aquasec.com", "version": "v1beta1", "plural": "policies"}
    resources = custom_resources(entry, REPO_ROOT / "tools/tracee/default", "ebpf-bench")
    names = {resource.name for resource in resources}
    assert "tracee-startup" in names
    assert all(resource.namespace is None for resource in resources)
    assert custom_resources(dict(entry, source="missing"), REPO_ROOT / "tools/tracee/default", "ns") == []


def test_adapter_pod_spec_translates_container_spec(tmp_path: Path) -> None:
    profile = tmp_path / "tools" / "kunai" / "tuned"
    (profile / "sub").mkdir(parents=True)
    (profile / "config.yaml").write_text("a: 1\n")
    (profile / "rules.yaml").write_text("r: 1\n")
    (profile / "sub" / "extra.txt").write_text("x")
    host = Path("/host/repo")
    spec = ContainerSpec(
        image="ebpf-bench/kunai:0.6.2",
        command=["run", "-c", "/etc/kunai/config.yaml"],
        entrypoint=["/usr/bin/kunai"],
        cap_add=["CAP_BPF"],
        environment={"A": "1"},
        mounts=[
            Mount(source=str(host / "tools/kunai/tuned"), target="/etc/kunai"),
            Mount(source=str(host / "tools/kunai/tuned/config.yaml"), target="/etc/single.yaml"),
            Mount(source="/sys/kernel/debug", target="/sys/kernel/debug", read_only=False),
            Mount(source="/var/run/docker.sock", target="/var/run/docker.sock"),
            Mount(source=str(host / "results/run/raw/kunai-tuned"), target="/out", read_only=False),
        ],
        alerts_file="alerts.jsonl",
    )
    pod_spec = {"containers": [{"name": "kunai", "image": "placeholder"}]}
    configmaps = adapter_pod_spec(pod_spec, "kunai", spec, "kunai", tmp_path, host)
    container = pod_spec["containers"][0]
    assert container["image"] == "ebpf-bench/kunai:0.6.2"
    assert container["command"] == ["/usr/bin/kunai"]
    assert container["args"] == ["run", "-c", "/etc/kunai/config.yaml"]
    assert container["env"] == [{"name": "A", "value": "1"}]
    assert container["securityContext"] == {"privileged": True, "capabilities": {"add": ["BPF"]}}
    assert pod_spec["hostPID"] is True and pod_spec["hostNetwork"] is True
    assert dict(configmaps) == {
        "bench-kunai-0": {"config.yaml": "a: 1\n", "rules.yaml": "r: 1\n"},
        "bench-kunai-0-1": {"extra.txt": "x"},
        "bench-kunai-1": {"config.yaml": "a: 1\n"},
    }
    mounts = {item["mountPath"]: item for item in container["volumeMounts"]}
    assert mounts["/etc/kunai/sub"]["readOnly"] is True
    assert mounts["/etc/single.yaml"]["subPath"] == "config.yaml"
    assert "readOnly" not in mounts["/sys/kernel/debug"]
    assert "/var/run/docker.sock" not in mounts
    volumes = {item["name"]: item for item in pod_spec["volumes"]}
    assert volumes["bench-2"] == {"name": "bench-2", "hostPath": {"path": "/sys/kernel/debug"}}
    assert volumes["bench-4"] == {"name": "bench-4", "emptyDir": {}}
    sidecar = pod_spec["containers"][1]
    assert sidecar["name"] == "alerts"
    assert "/out/alerts.jsonl" in sidecar["command"][-1]


def test_prepare_creates_namespace_and_picks_node() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    assert ("Namespace", None, "ebpf-bench") in api.core.objects
    assert backend.node == "node-1"
    backend.prepare()


def test_start_targets_creates_pods_and_uses_container_ids() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    api.core.selector_pods[("ebpf-bench", "app.kubernetes.io/name=attacker")] = [
        make_pod("attacker-5d9", [running_status("attacker", ATTACKER_ID)])
    ]
    targets = backend.start_targets()
    assert targets.victim == ContainerRef(id=VICTIM_ID, name="bench-victim")
    assert targets.victim_privileged == ContainerRef(id=PRIV_ID, name="bench-victim-priv")
    assert targets.attacker == ContainerRef(id=ATTACKER_ID, name="attacker")
    victim = api.core.objects[("Pod", "ebpf-bench", "bench-victim")]
    assert victim["spec"]["nodeName"] == "node-1"
    assert victim["spec"]["automountServiceAccountToken"] is False
    assert victim["spec"]["containers"][0]["imagePullPolicy"] == "IfNotPresent"
    privileged = api.core.objects[("Pod", "ebpf-bench", "bench-victim-priv")]
    assert privileged["spec"]["containers"][0]["securityContext"] == {"privileged": True}
    assert ("Service", "ebpf-bench", "attacker") in api.core.objects
    assert ("Deployment", "ebpf-bench", "attacker") in api.core.objects
    backend.stop(targets.victim)
    assert ("Pod", "ebpf-bench", "bench-victim") not in api.core.objects
    api.core.selector_pods[("ebpf-bench", "app.kubernetes.io/name=attacker")] = []
    backend.stop(targets.attacker)
    assert ("Service", "ebpf-bench", "attacker") not in api.core.objects
    assert ("Deployment", "ebpf-bench", "attacker") not in api.core.objects


def test_target_start_fails_fast_on_image_error() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    api.core.pod_statuses["bench-workload"] = [waiting_status("bench-workload", "ErrImageNeverPull")]
    with pytest.raises(PodStartError, match="ErrImageNeverPull"):
        backend.start_workload_host()


def test_target_start_times_out() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    api.core.pod_statuses["bench-workload"] = [waiting_status("bench-workload", "ContainerCreating")]
    with pytest.raises(PodStartError, match="timed out"):
        backend.start_workload_host()


def tool_pod(name: str, containers: list[str], uid: str = "uid-tool", restarts: int = 0):
    return make_pod(name, [running_status(container, "f" * 64, restarts) for container in containers], uid=uid)


def test_start_tool_with_helm_configmaps_and_logs() -> None:
    runner = FakeRunner()
    backend, api, _ = make_backend(runner=runner)
    backend.prepare()
    selector = "app.kubernetes.io/name=falco,app.kubernetes.io/instance=falco"
    pod = tool_pod("falco-abc", ["falco"])
    api.core.selector_pods[("ebpf-bench-falco", selector)] = [pod]
    api.core.logs[("falco-abc", "falco")] = [
        b"2026-01-02T03:04:05.000000001Z Opening 'syscall' source with modern BPF probe.\n",
        b'2026-01-02T03:04:06.25Z {"rule": "Read sensitive file", "priority": "Warning"}\n',
    ]
    spec = ContainerSpec(image="docker.io/falcosecurity/falco:0.45.0", ready_pattern=r"Opening 'syscall' source")
    ref = backend.start_tool("falco", "tuned", spec)
    assert ref == ContainerRef(id="uid-tool", name="falco-abc")
    assert runner.commands[0][:4] == ["helm", "upgrade", "--install", "falco"]
    config = api.core.objects[("ConfigMap", "ebpf-bench-falco", "bench-falco-config")]
    assert "falco.bench.yaml" in config["data"]
    rules = api.core.objects[("ConfigMap", "ebpf-bench-falco", "bench-falco-rules")]
    assert "custom_rules.yaml" in rules["data"]
    logs = backend.follow_logs(ref)
    backend.wait_ready(ref, logs, spec.ready_pattern, 5)
    assert logs.wait_closed(5)
    stamp, line = logs.lines()[1]
    assert stamp == pytest.approx(datetime(2026, 1, 2, 3, 4, 6, tzinfo=UTC).timestamp() + 0.25)
    assert line.startswith('{"rule"')
    assert ("logs", "ebpf-bench-falco", "falco-abc", "falco", True, True) in api.core.calls
    api.core.selector_pods[("ebpf-bench-falco", selector)] = []
    backend.stop(ref)
    assert runner.commands[-1][:3] == ["helm", "uninstall", "falco"]
    assert ("ConfigMap", "ebpf-bench-falco", "bench-falco-config") not in api.core.objects


def test_start_tool_default_profile_tolerates_missing_optional_configmap() -> None:
    backend, api, _ = make_backend()
    selector = "app.kubernetes.io/name=falco,app.kubernetes.io/instance=falco"
    api.core.selector_pods[("ebpf-bench-falco", selector)] = [tool_pod("falco-abc", ["falco"])]
    backend.start_tool("falco", "default", ContainerSpec(image="x"))
    assert api.core.objects[("ConfigMap", "ebpf-bench-falco", "bench-falco-rules")]["data"] == {}


def test_start_tool_failure_tears_down_and_raises() -> None:
    runner = FakeRunner(returncode=1, stderr="Error: chart not found")
    backend, api, _ = make_backend(runner=runner)
    with pytest.raises(ToolStartError, match="chart not found"):
        backend.start_tool("falco", "default", ContainerSpec(image="x"))
    assert ("ConfigMap", "ebpf-bench-falco", "bench-falco-config") not in api.core.objects
    assert runner.commands[-1][:2] == ["helm", "uninstall"]
    assert backend._pending == []


def test_start_tool_tracee_applies_policies_and_restarts() -> None:
    backend, api, _ = make_backend()
    api.custom.missing_crd = 2
    selector = "app.kubernetes.io/name=tracee,app.kubernetes.io/instance=tracee"
    old = tool_pod("tracee-old", ["tracee"], uid="uid-old")
    new = tool_pod("tracee-new", ["tracee"], uid="uid-new")
    responses = iter([[old], [old, new]])
    api.core.list_namespaced_pod = lambda namespace, label_selector=None: SimpleNamespace(
        items=next(responses, [new]) if label_selector == selector else []
    )
    ref = backend.start_tool("tracee", "tuned", ContainerSpec(image="aquasec/tracee:0.24.1"))
    assert ref.name == "tracee-new"
    plurals = {(group, plural) for group, _, _, plural, _ in api.custom.created}
    assert plurals == {("tracee.aquasec.com", "policies")}
    assert len(api.custom.created) == len(list((REPO_ROOT / "tools/tracee/tuned/policies").glob("*.yaml")))
    assert api.apps.patches and api.apps.patches[0][0] == "tracee"
    api.core.list_namespaced_pod = lambda namespace, label_selector=None: SimpleNamespace(items=[])
    backend.stop(ref)
    assert len(api.custom.deleted) == len(api.custom.created)


def test_start_tool_from_adapter_manifest() -> None:
    profile = REPO_ROOT / "tools" / "kunai" / "default"
    backend, api, _ = make_backend()
    api.core.selector_pods[("ebpf-bench-kunai", "app.kubernetes.io/name=kunai")] = [tool_pod("kunai-x", ["kunai"])]
    spec = ContainerSpec(
        image="ebpf-bench/kunai:0.6.2",
        command=["run", "-c", "/etc/kunai/config.yaml"],
        mounts=[Mount(source=str(Path("/host/repo") / "tools/kunai/default"), target="/etc/kunai")],
    )
    ref = backend.start_tool("kunai", "default", spec)
    daemonset = api.core.objects[("DaemonSet", "ebpf-bench-kunai", "kunai")]
    container = daemonset["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "ebpf-bench/kunai:0.6.2"
    assert container["args"] == ["run", "-c", "/etc/kunai/config.yaml"]
    assert daemonset["metadata"]["namespace"] == "ebpf-bench-kunai"
    data = api.core.objects[("ConfigMap", "ebpf-bench-kunai", "bench-kunai-0")]["data"]
    assert data == {item.name: item.read_text() for item in profile.iterdir() if item.is_file()}
    api.core.selector_pods[("ebpf-bench-kunai", "app.kubernetes.io/name=kunai")] = []
    backend.stop(ref)
    assert ("DaemonSet", "ebpf-bench-kunai", "kunai") not in api.core.objects


def test_tail_file_follows_alerts_container() -> None:
    backend, api, _ = make_backend()
    selector = "app.kubernetes.io/name=tetragon,app.kubernetes.io/instance=tetragon"
    api.core.selector_pods[("ebpf-bench-tetragon", selector)] = [tool_pod("tetragon-x", ["tetragon", "export-stdout"])]
    api.core.logs[("tetragon-x", "export-stdout")] = [b'2026-01-02T03:04:05Z {"process_exec": {}}\n']
    ref = backend.start_tool("tetragon", "default", ContainerSpec(image="x"))
    buffer = backend.tail_file(Path("/ignored"))
    assert buffer.wait_closed(5)
    assert [line for _, line in buffer.lines()] == ['{"process_exec": {}}']
    logs = backend.follow_logs(ref)
    assert logs.wait_closed(5)
    containers = {call[3] for call in api.core.calls if call[0] == "logs"}
    assert containers == {"tetragon", "export-stdout"}


def test_tail_file_without_tool_is_closed() -> None:
    backend, _, _ = make_backend()
    assert backend.tail_file(Path("x")).closed


def test_wait_ready_detects_restart() -> None:
    backend, api, _ = make_backend()
    selector = "app.kubernetes.io/name=falco,app.kubernetes.io/instance=falco"
    api.core.selector_pods[("ebpf-bench-falco", selector)] = [tool_pod("falco-abc", ["falco"])]
    ref = backend.start_tool("falco", "default", ContainerSpec(image="x"))
    api.core.pods[("ebpf-bench-falco", "falco-abc")] = tool_pod("falco-abc", ["falco"], restarts=1)
    logs = LineBuffer()
    logs.append(1.0, "starting")
    with pytest.raises(ToolStartError, match="restarted"):
        backend.wait_ready(ref, logs, "never", 0.1)


def test_exec_collects_output_and_exit_code() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    ref = backend.start_workload_host()
    api.stream.client = FakeExecClient(["out1 ", "out2"], ["err"], 3)
    result = backend.exec(ref, ["sh", "-c", "exit 3"], {"BENCH_MARKER": "m"}, 30)
    assert result.exit_code == 3
    assert result.output == "out1 errout2"
    call = api.stream.calls[0]
    assert call["name"] == "bench-workload" and call["namespace"] == "ebpf-bench"
    assert call["container"] == "bench-workload"
    assert call["command"][:4] == ["timeout", "--kill-after=5", "30", "env"]
    assert "BENCH_MARKER=m" in call["command"]
    assert call["stdin"] is False and call["tty"] is False
    assert api.stream.client.closed


def test_exec_client_side_timeout() -> None:
    backend, api, clock = make_backend()
    backend.prepare()
    ref = backend.start_workload_host()
    api.stream.client = FakeExecClient([], [], 0, hang=True, tick=lambda: clock.sleep(1))
    result = backend.exec(ref, ["sleep", "100"], {}, 1)
    assert result.exit_code == 124
    assert "timed out after 1s" in result.output
    assert api.stream.client.closed


def test_exec_timeout_exit_code_from_coreutils() -> None:
    backend, api, clock = make_backend()
    backend.prepare()
    ref = backend.start_workload_host()
    api.stream.client = FakeExecClient(["partial"], [], 124, tick=lambda: clock.sleep(5))
    result = backend.exec(ref, ["sleep", "100"], {}, 2)
    assert result.exit_code == 124
    assert result.output.startswith("partial")


def test_exec_stream_error() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    ref = backend.start_workload_host()

    def broken(*args, **kwargs):
        raise RuntimeError("upgrade failed")

    api.stream = broken
    result = backend.exec(ref, ["true"], {}, 5)
    assert result.exit_code == -1
    assert "upgrade failed" in result.output


def test_start_stats_uses_metrics_server() -> None:
    backend, api, _ = make_backend()
    selector = "app.kubernetes.io/name=falco,app.kubernetes.io/instance=falco"
    api.core.selector_pods[("ebpf-bench-falco", selector)] = [tool_pod("falco-abc", ["falco"])]
    ref = backend.start_tool("falco", "default", ContainerSpec(image="x"))
    api.custom.metrics = {"timestamp": "t", "containers": [{"usage": {"cpu": "200m", "memory": "10Mi"}}]}
    sampler = backend.start_stats(ref)
    time.sleep(0.1)
    cpu, memory = sampler.stop()
    assert cpu == [pytest.approx(20.0)]
    assert memory == [10 * 1024.0**2]


def test_start_stats_without_metrics_server_is_empty() -> None:
    backend, api, _ = make_backend()
    backend.prepare()
    ref = backend.start_workload_host()
    sampler = backend.start_stats(ref)
    time.sleep(0.05)
    assert sampler.stop() == ([], [])


def test_cleanup_stops_everything() -> None:
    runner = FakeRunner()
    backend, api, _ = make_backend(runner=runner)
    backend.prepare()
    selector = "app.kubernetes.io/name=falco,app.kubernetes.io/instance=falco"
    api.core.selector_pods[("ebpf-bench-falco", selector)] = [tool_pod("falco-abc", ["falco"])]
    backend.start_tool("falco", "default", ContainerSpec(image="x"))
    backend.start_workload_host()
    api.core.selector_pods[("ebpf-bench-falco", selector)] = []
    backend.cleanup()
    assert backend._tools == {} and backend._pods == {}
    assert ("Pod", "ebpf-bench", "bench-workload") not in api.core.objects
    assert runner.commands[-1][:2] == ["helm", "uninstall"]


def test_host_info_reports_node() -> None:
    backend, _, _ = make_backend()
    info = backend.host_info()
    assert info["backend"] == "kubernetes"
    assert info["kernel"] == "6.6.0"
    assert info["cpus"] == 8
    assert info["memory_bytes"] == 16 * 1024.0**3
    assert info["container_runtime"] == "containerd://2.1.1"
    assert info["kube_context"] == "kind-ebpf-bench"


def test_config_kubernetes_section(tmp_path: Path) -> None:
    path = tmp_path / "bench.yaml"
    path.write_text(
        "backend: kubernetes\nkubernetes:\n  kubeconfig: /root/.kube/config\n  context: kind-ebpf-bench\n"
        "  namespace: bench-ns\n  node: worker\n"
    )
    config = load_config(path)
    assert config.backend == "kubernetes"
    assert config.kubernetes == KubernetesConfig("/root/.kube/config", "kind-ebpf-bench", "bench-ns", "worker")
    assert parse_config(config.as_dict()) == replace(config, source="")


def test_config_kubernetes_defaults() -> None:
    config = parse_config({})
    assert config.backend == "docker"
    assert config.kubernetes == KubernetesConfig()
    assert config.kubernetes.namespace == "ebpf-bench"
    assert parse_config({"kubernetes": {"namespace": None}}).kubernetes.namespace == "ebpf-bench"


@pytest.mark.parametrize(
    "data, message",
    [
        ({"backend": "podman"}, "backend must be one of"),
        ({"kubernetes": ["x"]}, "kubernetes must be a mapping"),
        ({"kubernetes": {"cluster": "x"}}, "unknown kubernetes keys"),
        ({"kubernetes": {"namespace": "Bad_Name"}}, "kubernetes.namespace"),
        ({"kubernetes": {"context": ""}}, "kubernetes.context"),
        ({"kubernetes": {"kubeconfig": 3}}, "kubernetes.kubeconfig"),
    ],
)
def test_config_kubernetes_invalid(data: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_config(data)


def test_repository_bench_yaml_declares_backend() -> None:
    config = load_config(REPO_ROOT / "bench.yaml")
    assert config.backend == "docker"
    assert config.kubernetes.namespace == "ebpf-bench"


def test_cli_selects_kubernetes_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    from bench import __main__ as cli

    config = replace(parse_config({}), backend="kubernetes", kubernetes=KubernetesConfig(context="kind-x"))
    backend = cli.build_backend(config, REPO_ROOT, Path("/host"))
    assert isinstance(backend, KubernetesBackend)
    assert backend.settings.context == "kind-x"
    assert backend.host_repo_root == Path("/host")
