from __future__ import annotations

import copy
import json
import platform
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from bench.adapters.base import ContainerSpec
from bench.config import KubernetesConfig
from bench.docker_backend import (
    ATTACKER_NAME,
    LOG_DRAIN_TIMEOUT,
    PRIVILEGED_VICTIM_NAME,
    TARGET_STOP_TIMEOUT,
    TIMEOUT_EXIT_CODE,
    VICTIM_NAME,
    WORKLOAD_HOST_NAME,
    Backend,
    ContainerRef,
    ExecResult,
    LineBuffer,
    StatsSampler,
    Targets,
    ToolStartError,
    split_timestamped,
)

DEPLOY_DIR = Path("deploy") / "kubernetes"
TARGETS_DIR = DEPLOY_DIR / "targets"
TOOLS_DIR = DEPLOY_DIR / "tools"
TOOL_FILE = "tool.yaml"
ROLE_LABEL = "ebpf-bench.role"
ADAPTER = "adapter"
ID_SCHEMES = ("containerd://", "docker://", "cri-o://")
KIND_PROVIDER_PREFIX = "kind://"
INSTALL_TYPES = ("helm", "manifests")
POLL_SECONDS = 1.0
TARGET_START_TIMEOUT = 180.0
DELETE_TIMEOUT = 120.0
HELM_TIMEOUT = 900.0
EXEC_KILL_AFTER = 5
EXEC_GRACE_SECONDS = 15.0
EXEC_TIMEOUT_CODES = (TIMEOUT_EXIT_CODE, 137)
EXEC_OPEN_ATTEMPTS = 30
METRICS_POLL_SECONDS = 5.0
METRICS_GROUP = "metrics.k8s.io"
METRICS_VERSION = "v1beta1"
RESTART_ANNOTATION = "ebpf-bench/restarted-at"
ALERTS_SIDECAR = "alerts"
ALERTS_SIDECAR_IMAGE = "busybox:1.36.1"
CONFIG_SUFFIXES = (".yaml", ".yml", ".json")
DIAGNOSTIC_LOG_LINES = 200
SUMMARY_LOG_LINES = 20
SUMMARY_EVENTS = 10
DIAGNOSTICS_TAG = "[diagnostics]"
FAILED_WAITING_REASONS = frozenset(
    {
        "ErrImagePull",
        "ImagePullBackOff",
        "ErrImageNeverPull",
        "InvalidImageName",
        "CrashLoopBackOff",
        "CreateContainerConfigError",
        "CreateContainerError",
        "RunContainerError",
    }
)
SKIPPED_HOST_PATHS = frozenset({"/var/run/docker.sock", "/run/docker.sock", "/var/lib/docker"})
KUBEARMOR_KINDS = {"KubeArmorPolicy": ("kubearmorpolicies", True), "KubeArmorHostPolicy": ("kubearmorhostpolicies", False)}
TARGET_FILES = {
    "namespace": "namespace.yaml",
    ATTACKER_NAME: "attacker.yaml",
    VICTIM_NAME: "victim.yaml",
    PRIVILEGED_VICTIM_NAME: "victim-priv.yaml",
    WORKLOAD_HOST_NAME: "workload.yaml",
}
KINDS = {
    "Namespace": ("core", "namespace", False),
    "ServiceAccount": ("core", "namespaced_service_account", True),
    "ConfigMap": ("core", "namespaced_config_map", True),
    "Service": ("core", "namespaced_service", True),
    "Pod": ("core", "namespaced_pod", True),
    "Deployment": ("apps", "namespaced_deployment", True),
    "DaemonSet": ("apps", "namespaced_daemon_set", True),
}
CPU_SUFFIXES = {"n": 1e-9, "u": 1e-6, "m": 1e-3}
MEMORY_SUFFIXES = {
    "Ki": 1024.0,
    "Mi": 1024.0**2,
    "Gi": 1024.0**3,
    "Ti": 1024.0**4,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
}


class PodStartError(ToolStartError):
    pass


@dataclass
class KubeApi:
    core: Any
    apps: Any
    custom: Any
    stream: Callable[..., Any]
    exec_core: Any = None
    version: Any = None

    def __post_init__(self) -> None:
        if self.exec_core is None:
            self.exec_core = self.core


@dataclass(frozen=True)
class ToolDeployment:
    tool: str
    directory: Path
    namespace: str
    release: str
    install: dict[str, Any]
    selector: str
    log_containers: tuple[str, ...]
    alerts_container: str
    ready_pattern: str | None = ADAPTER
    configmaps: tuple[dict[str, Any], ...] = ()
    custom_resources: tuple[dict[str, Any], ...] = ()
    restart_after_resources: bool = False
    startup_timeout: float | None = None
    alerts_file: str | None = None

    @property
    def kind(self) -> str:
        return str(self.install["type"])


@dataclass(frozen=True)
class CustomResource:
    group: str
    version: str
    plural: str
    namespace: str | None
    body: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.body["metadata"]["name"])


@dataclass
class PodHandle:
    namespace: str
    pod: str
    containers: tuple[str, ...]
    objects: list[tuple[str, str]] = field(default_factory=list)
    selector: str | None = None


@dataclass
class ToolHandle:
    deployment: ToolDeployment
    profile: str
    spec: ContainerSpec
    pod: str | None = None
    restarts: dict[str, int] = field(default_factory=dict)
    helm: bool = False
    configmaps: list[str] = field(default_factory=list)
    objects: list[tuple[str, str]] = field(default_factory=list)
    resources: list[CustomResource] = field(default_factory=list)

    @property
    def namespace(self) -> str:
        return self.deployment.namespace


def load_api(kubeconfig: str | None, context: str | None) -> KubeApi:
    from kubernetes import client, config
    from kubernetes.config.config_exception import ConfigException
    from kubernetes.stream import stream

    try:
        config.load_kube_config(config_file=kubeconfig, context=context)
    except ConfigException:
        if kubeconfig or context:
            raise
        config.load_incluster_config()
    return KubeApi(
        core=client.CoreV1Api(),
        apps=client.AppsV1Api(),
        custom=client.CustomObjectsApi(),
        stream=stream,
        exec_core=client.CoreV1Api(client.ApiClient()),
        version=client.VersionApi(),
    )


def is_status(error: BaseException, *codes: int) -> bool:
    return getattr(error, "status", None) in codes


def strip_container_id(value: Any) -> str:
    text = str(value or "").strip()
    for scheme in ID_SCHEMES:
        if text.startswith(scheme):
            return text[len(scheme):]
    return text


def parse_cpu(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    scale = CPU_SUFFIXES.get(text[-1])
    try:
        return float(text[:-1]) * scale if scale else float(text)
    except ValueError:
        return None


def parse_memory(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    for suffix in sorted(MEMORY_SUFFIXES, key=len, reverse=True):
        if text.endswith(suffix):
            try:
                return float(text[: -len(suffix)]) * MEMORY_SUFFIXES[suffix]
            except ValueError:
                return None
    try:
        return float(text)
    except ValueError:
        return None


def pod_metrics_sample(data: Any) -> tuple[str, float | None, float | None] | None:
    if not isinstance(data, dict):
        return None
    containers = data.get("containers") or []
    if not containers:
        return None
    cpu = [parse_cpu((item.get("usage") or {}).get("cpu")) for item in containers]
    memory = [parse_memory((item.get("usage") or {}).get("memory")) for item in containers]
    cpu_values = [value for value in cpu if value is not None]
    memory_values = [value for value in memory if value is not None]
    return (
        str(data.get("timestamp") or ""),
        sum(cpu_values) * 100.0 if cpu_values else None,
        sum(memory_values) if memory_values else None,
    )


def is_kind_node(node: Any) -> bool:
    provider = str(getattr(getattr(node, "spec", None), "provider_id", None) or "")
    return provider.startswith(KIND_PROVIDER_PREFIX)


def exec_command(command: list[str], environment: dict[str, str], timeout: float) -> list[str]:
    variables = [f"{key}={value}" for key, value in sorted((environment or {}).items())]
    return ["timeout", f"--kill-after={EXEC_KILL_AFTER}", f"{timeout:g}", "env", *variables, *command]


def selector_string(labels: dict[str, Any]) -> str:
    return ",".join(f"{key}={value}" for key, value in sorted(labels.items()))


def helm_escape(value: Any) -> str:
    text = ("true" if value else "false") if isinstance(value, bool) else str(value)
    return text.replace("\\", "\\\\").replace(",", "\\,")


def load_documents(path: Path) -> list[dict[str, Any]]:
    return [document for document in yaml.safe_load_all(path.read_text(encoding="utf-8")) if isinstance(document, dict)]


def configmap_data(path: Path) -> dict[str, str]:
    if path.is_file():
        return {path.name: path.read_text(encoding="utf-8")}
    if path.is_dir():
        return {item.name: item.read_text(encoding="utf-8") for item in sorted(path.iterdir()) if item.is_file()}
    return {}


def configmap_source(profile_dir: Path, entry: dict[str, Any]) -> dict[str, str]:
    path = profile_dir / str(entry["source"])
    if not path.exists() and not entry.get("optional"):
        raise ToolStartError(f"configmap {entry['name']}: {path} not found")
    return configmap_data(path)


def local_path(value: str, repo_root: Path, host_repo_root: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        return repo_root / path
    try:
        return repo_root / path.relative_to(host_repo_root)
    except ValueError:
        return path


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def load_tool_deployment(repo_root: Path, tool: str) -> ToolDeployment:
    directory = Path(repo_root) / TOOLS_DIR / tool
    path = directory / TOOL_FILE
    if not path.is_file():
        raise ToolStartError(f"no Kubernetes deployment for {tool}: {path} not found")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    install = data.get("install") or {}
    agent = data.get("agent") or {}
    missing = [key for key in ("namespace", "release") if not data.get(key)]
    missing += [f"agent.{key}" for key in ("selector", "log_containers") if not agent.get(key)]
    if missing:
        raise ToolStartError(f"{path}: missing {missing}")
    if install.get("type") not in INSTALL_TYPES:
        raise ToolStartError(f"{path}: install.type must be one of {list(INSTALL_TYPES)}")
    required = ("repo", "chart", "version", "values") if install["type"] == "helm" else ("manifests", "container")
    absent = [f"install.{key}" for key in required if not install.get(key)]
    if absent:
        raise ToolStartError(f"{path}: missing {absent}")
    log_containers = tuple(str(name) for name in agent["log_containers"])
    startup_timeout = agent.get("startup_timeout")
    if startup_timeout is not None:
        if isinstance(startup_timeout, bool) or not isinstance(startup_timeout, (int, float)) or startup_timeout <= 0:
            raise ToolStartError(f"{path}: agent.startup_timeout must be a positive number of seconds")
        startup_timeout = float(startup_timeout)
    alerts_file = agent.get("alerts_file")
    if alerts_file is not None and (not isinstance(alerts_file, str) or not alerts_file.startswith("/")):
        raise ToolStartError(f"{path}: agent.alerts_file must be an absolute path inside agent.alerts_container")
    return ToolDeployment(
        tool=tool,
        directory=directory,
        namespace=str(data["namespace"]),
        release=str(data["release"]),
        install=dict(install),
        selector=str(agent["selector"]),
        log_containers=log_containers,
        alerts_container=str(agent.get("alerts_container") or log_containers[0]),
        ready_pattern=agent.get("ready_pattern", ADAPTER),
        configmaps=tuple(data.get("configmaps") or ()),
        custom_resources=tuple(data.get("custom_resources") or ()),
        restart_after_resources=bool(data.get("restart_after_resources", False)),
        startup_timeout=startup_timeout,
        alerts_file=alerts_file,
    )


def tail_command(path: str) -> list[str]:
    return ["tail", "-n", "+1", "-F", path]


def kube_flags(settings: KubernetesConfig) -> list[str]:
    flags = []
    if settings.kubeconfig:
        flags += ["--kubeconfig", settings.kubeconfig]
    if settings.context:
        flags += ["--kube-context", settings.context]
    return flags


def helm_install_command(
    deployment: ToolDeployment, profile: str, profile_dir: Path, settings: KubernetesConfig
) -> list[str]:
    install = deployment.install
    values = install["values"].get(profile)
    if not values:
        raise ToolStartError(f"{deployment.tool}: no Helm values for profile {profile!r}")
    command = [
        "helm",
        "upgrade",
        "--install",
        deployment.release,
        str(install["chart"]),
        "--repo",
        str(install["repo"]),
        "--version",
        str(install["version"]),
        "--namespace",
        deployment.namespace,
        "--values",
        str(deployment.directory / values),
    ]
    for key, relative in sorted((install.get("set_file") or {}).items()):
        command += ["--set-file", f"{key}={profile_dir / relative}"]
    for entry in install.get("set_from_profile") or []:
        source = profile_dir / entry["file"]
        data = yaml.safe_load(source.read_text(encoding="utf-8")) if source.is_file() else None
        data = data if isinstance(data, dict) else {}
        for key in entry.get("keys") or []:
            if data.get(key) is not None:
                command += ["--set-string", f"{entry['prefix']}.{key}={helm_escape(data[key])}"]
    return command + kube_flags(settings)


def helm_uninstall_command(deployment: ToolDeployment, settings: KubernetesConfig) -> list[str]:
    return [
        "helm",
        "uninstall",
        deployment.release,
        "--namespace",
        deployment.namespace,
        "--wait",
        "--timeout",
        f"{int(DELETE_TIMEOUT)}s",
        "--ignore-not-found",
    ] + kube_flags(settings)


def kubearmor_resource(document: dict[str, Any], namespace: str, group: str, version: str) -> CustomResource:
    kind = str(document.get("kind") or "KubeArmorPolicy")
    if kind not in KUBEARMOR_KINDS:
        raise ToolStartError(f"unsupported KubeArmor policy kind {kind!r}")
    plural, namespaced = KUBEARMOR_KINDS[kind]
    metadata = document.get("metadata") or {}
    name = metadata.get("policyName") or metadata.get("name")
    if not name:
        raise ToolStartError("KubeArmor policy without policyName")
    body_metadata: dict[str, Any] = {"name": str(name)}
    if namespaced:
        body_metadata["namespace"] = namespace
    body = {"apiVersion": f"{group}/{version}", "kind": kind, "metadata": body_metadata, "spec": document.get("spec") or {}}
    return CustomResource(group, version, plural, namespace if namespaced else None, body)


def custom_resources(entry: dict[str, Any], profile_dir: Path, namespace: str) -> list[CustomResource]:
    source = profile_dir / str(entry["source"])
    if source.is_dir():
        files = sorted(item for item in source.iterdir() if item.is_file() and item.suffix in CONFIG_SUFFIXES)
    elif source.is_file():
        files = [source]
    else:
        files = []
    group = str(entry["group"])
    version = str(entry["version"])
    resources = []
    for path in files:
        for document in load_documents(path):
            if entry.get("format") == "kubearmor-backup":
                resources.append(kubearmor_resource(document, namespace, group, version))
                continue
            body = copy.deepcopy(document)
            namespaced = bool(entry.get("namespaced"))
            if namespaced:
                body.setdefault("metadata", {})["namespace"] = namespace
            resources.append(CustomResource(group, version, str(entry["plural"]), namespace if namespaced else None, body))
    return resources


def adapter_pod_spec(
    pod_spec: dict[str, Any],
    container_name: str,
    spec: ContainerSpec,
    tool: str,
    repo_root: Path,
    host_repo_root: Path,
) -> list[tuple[str, dict[str, str]]]:
    containers = pod_spec.setdefault("containers", [])
    container = next((item for item in containers if item.get("name") == container_name), None)
    if container is None:
        container = {"name": container_name}
        containers.append(container)
    container["image"] = spec.image
    container.setdefault("imagePullPolicy", "IfNotPresent")
    if spec.entrypoint is not None:
        container["command"] = list(spec.entrypoint)
    if spec.command:
        container["args"] = list(spec.command)
    if spec.environment:
        container["env"] = [{"name": key, "value": value} for key, value in sorted(spec.environment.items())]
    security = container.setdefault("securityContext", {})
    if spec.privileged:
        security["privileged"] = True
    if spec.cap_add:
        security.setdefault("capabilities", {})["add"] = [cap.upper().removeprefix("CAP_") for cap in spec.cap_add]
    if spec.pid_mode == "host":
        pod_spec["hostPID"] = True
    if spec.network_mode == "host":
        pod_spec["hostNetwork"] = True
        pod_spec["dnsPolicy"] = "ClusterFirstWithHostNet"
    volumes = pod_spec.setdefault("volumes", [])
    mounts = container.setdefault("volumeMounts", [])
    configmaps: list[tuple[str, dict[str, str]]] = []
    tools_root = Path(repo_root) / "tools"
    for index, mount in enumerate(spec.mounts):
        if mount.source in SKIPPED_HOST_PATHS:
            continue
        local = local_path(mount.source, Path(repo_root), Path(host_repo_root))
        volume = f"bench-{index}"
        if is_within(local, tools_root):
            name = f"bench-{tool}-{index}"
            if local.is_file():
                configmaps.append((name, configmap_data(local)))
                volumes.append({"name": volume, "configMap": {"name": name}})
                mounts.append({"name": volume, "mountPath": mount.target, "subPath": local.name, "readOnly": True})
                continue
            directories = [local] + (sorted(item for item in local.rglob("*") if item.is_dir()) if local.is_dir() else [])
            for offset, directory in enumerate(directories):
                suffix = f"-{offset}" if offset else ""
                configmaps.append((name + suffix, configmap_data(directory)))
                volumes.append({"name": volume + suffix, "configMap": {"name": name + suffix}})
                target = mount.target
                if offset:
                    target = f"{mount.target.rstrip('/')}/{directory.relative_to(local).as_posix()}"
                mounts.append({"name": volume + suffix, "mountPath": target, "readOnly": True})
        elif is_within(local, Path(repo_root)):
            volumes.append({"name": volume, "emptyDir": {}})
            mounts.append({"name": volume, "mountPath": mount.target})
            if spec.alerts_file:
                alerts = f"{mount.target.rstrip('/')}/{spec.alerts_file}"
                containers.append(
                    {
                        "name": ALERTS_SIDECAR,
                        "image": ALERTS_SIDECAR_IMAGE,
                        "imagePullPolicy": "IfNotPresent",
                        "command": ["sh", "-c", f"touch {alerts} && exec tail -n +1 -F {alerts}"],
                        "volumeMounts": [{"name": volume, "mountPath": mount.target}],
                    }
                )
        else:
            entry: dict[str, Any] = {"name": volume, "mountPath": mount.target}
            if mount.read_only:
                entry["readOnly"] = True
            volumes.append({"name": volume, "hostPath": {"path": mount.source}})
            mounts.append(entry)
    return configmaps


def pod_state(pod: Any, containers: Iterable[str], require_ready: bool = True) -> tuple[str, str]:
    status = getattr(pod, "status", None)
    if status is None:
        return "pending", "no status yet"
    if status.phase in ("Failed", "Succeeded"):
        return "failed", f"pod phase {status.phase}"
    statuses = {item.name: item for item in status.container_statuses or []}
    for name in containers:
        item = statuses.get(name)
        if item is None:
            return "pending", f"container {name} not created"
        state = item.state
        waiting = getattr(state, "waiting", None)
        terminated = getattr(state, "terminated", None)
        if waiting is not None:
            detail = f"container {name} {waiting.reason}: {waiting.message or ''}".strip()
            return ("failed" if waiting.reason in FAILED_WAITING_REASONS else "pending"), detail
        if terminated is not None:
            return "failed", f"container {name} terminated with exit code {terminated.exit_code} ({terminated.reason})"
        if getattr(state, "running", None) is None:
            return "pending", f"container {name} not running"
        if require_ready and not item.ready:
            return "pending", f"container {name} not ready"
    return "ready", "running"


def restart_counts(pod: Any) -> dict[str, int]:
    statuses = getattr(getattr(pod, "status", None), "container_statuses", None) or []
    return {item.name: int(item.restart_count or 0) for item in statuses}


def container_id(pod: Any, container: str) -> str:
    for item in pod.status.container_statuses or []:
        if item.name == container:
            return strip_container_id(item.container_id)
    raise PodStartError(f"pod {pod.metadata.name} has no container {container}")


def one_line(value: Any) -> str:
    return " | ".join(line.strip() for line in str(value or "").splitlines() if line.strip())


def error_text(error: BaseException) -> str:
    body = getattr(error, "body", None)
    message = None
    if body:
        try:
            message = json.loads(body).get("message")
        except (ValueError, TypeError, AttributeError):
            message = body
    status = getattr(error, "status", None)
    text = one_line(message or f"{type(error).__name__}: {error}")
    return f"HTTP {status}: {text}" if status is not None else text


def format_state(state: Any) -> str:
    if state is None:
        return "unknown"
    terminated = getattr(state, "terminated", None)
    if terminated is not None:
        return (
            f"terminated exit_code={getattr(terminated, 'exit_code', None)} "
            f"reason={getattr(terminated, 'reason', None)} message={one_line(getattr(terminated, 'message', None))}"
        )
    waiting = getattr(state, "waiting", None)
    if waiting is not None:
        return f"waiting reason={getattr(waiting, 'reason', None)} message={one_line(getattr(waiting, 'message', None))}"
    running = getattr(state, "running", None)
    if running is not None:
        return f"running started_at={getattr(running, 'started_at', None)}"
    return "none"


def pod_containers(pod: Any) -> list[tuple[Any, bool]]:
    status = getattr(pod, "status", None)
    init = [(item, True) for item in getattr(status, "init_container_statuses", None) or []]
    main = [(item, False) for item in getattr(status, "container_statuses", None) or []]
    return init + main


def has_previous(item: Any) -> bool:
    last = getattr(item, "last_state", None)
    return int(getattr(item, "restart_count", 0) or 0) > 0 or getattr(last, "terminated", None) is not None


def is_failing(item: Any, init: bool) -> bool:
    state = getattr(item, "state", None)
    terminated = getattr(state, "terminated", None)
    if init:
        return terminated is None or getattr(terminated, "exit_code", None) != 0
    return terminated is not None or getattr(state, "waiting", None) is not None or has_previous(item)


def pod_summary(pod: Any) -> list[str]:
    status = getattr(pod, "status", None)
    head = f"pod phase={getattr(status, 'phase', None)} node={getattr(getattr(pod, 'spec', None), 'node_name', None)}"
    for attribute in ("reason", "message"):
        value = getattr(status, attribute, None)
        if value:
            head += f" {attribute}={one_line(value)}"
    texts = [head]
    for condition in getattr(status, "conditions", None) or []:
        if getattr(condition, "status", None) != "True":
            texts.append(
                f"condition {condition.type}={condition.status} reason={getattr(condition, 'reason', None)} "
                f"message={one_line(getattr(condition, 'message', None))}"
            )
    for item, init in pod_containers(pod):
        text = (
            f"{'init container' if init else 'container'} {item.name}: {format_state(getattr(item, 'state', None))} "
            f"restarts={int(getattr(item, 'restart_count', 0) or 0)} ready={getattr(item, 'ready', None)}"
        )
        last = getattr(item, "last_state", None)
        if getattr(last, "terminated", None) is not None:
            text += f"; last state: {format_state(last)}"
        texts.append(text)
    return texts


def event_line(event: Any) -> str:
    involved = getattr(event, "involved_object", None)
    target = f"{getattr(involved, 'kind', None)}/{getattr(involved, 'name', None)}"
    return (
        f"[event {target}] {getattr(event, 'type', None)} {getattr(event, 'reason', None)} "
        f"x{getattr(event, 'count', None) or 1}: {one_line(getattr(event, 'message', None))}"
    )


def event_time(event: Any, default: float) -> float:
    for attribute in ("last_timestamp", "event_time", "first_timestamp"):
        value = getattr(event, attribute, None)
        if isinstance(value, datetime):
            return value.timestamp()
    return default


def with_diagnostics(error: BaseException, summary: str, diagnostics: list[tuple[float, str]]) -> ToolStartError:
    if isinstance(error, ToolStartError):
        cls: type[ToolStartError] = type(error)
        message = str(error)
    else:
        cls = ToolStartError
        message = f"{type(error).__name__}: {error}"
    return cls(f"{message}\n{summary}" if summary else message, list(getattr(error, "diagnostics", [])) + diagnostics)


def pump_log_streams(sources: list[Callable[[], Iterable[bytes]]], buffer: LineBuffer, name: str = "logs") -> None:
    if not sources:
        buffer.close()
        return
    remaining = [len(sources)]
    lock = threading.Lock()

    def pump(source: Callable[[], Iterable[bytes]]) -> None:
        pending = b""
        try:
            for chunk in source():
                pending += chunk
                *complete, pending = pending.split(b"\n")
                for raw in complete:
                    if raw.strip():
                        buffer.append(*split_timestamped(raw.decode("utf-8", errors="replace")))
        except Exception:
            pass
        finally:
            if pending.strip():
                buffer.append(*split_timestamped(pending.decode("utf-8", errors="replace")))
            with lock:
                remaining[0] -= 1
                done = remaining[0] == 0
            if done:
                buffer.close()

    for index, source in enumerate(sources):
        threading.Thread(target=pump, args=(source,), name=f"{name}-{index}", daemon=True).start()


def pump_read_lines(
    source: Callable[[], Iterable[str | bytes]], buffer: LineBuffer, clock: Callable[[], float], name: str = "tail"
) -> None:
    def pump() -> None:
        pending = ""
        try:
            for chunk in source():
                now = clock()
                pending += chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else str(chunk)
                *complete, pending = pending.split("\n")
                for line in complete:
                    if line.strip():
                        buffer.append(now, line.rstrip("\r"))
        except Exception:
            pass
        finally:
            if pending.strip():
                buffer.append(clock(), pending.rstrip("\r"))
            buffer.close()

    threading.Thread(target=pump, name=name, daemon=True).start()


class MetricsSampler(StatsSampler):
    def __init__(
        self,
        fetch: Callable[[], tuple[str, float | None, float | None] | None],
        interval: float = METRICS_POLL_SECONDS,
    ) -> None:
        self._fetch = fetch
        self._interval = interval
        super().__init__(lambda: ())

    def _run(self, source: Callable[[], Iterable[dict[str, Any]]]) -> None:
        seen: set[str] = set()
        while not self._stop.is_set():
            try:
                sample = self._fetch()
            except Exception:
                sample = None
            if sample is not None and sample[0] not in seen:
                seen.add(sample[0])
                with self._lock:
                    if sample[1] is not None:
                        self.cpu_percent.append(sample[1])
                    if sample[2] is not None:
                        self.memory_bytes.append(sample[2])
            self._stop.wait(self._interval)


class KubernetesBackend(Backend):
    def __init__(
        self,
        repo_root: Path,
        host_repo_root: Path | None = None,
        settings: KubernetesConfig | None = None,
        api: KubeApi | None = None,
        runner: Callable[..., Any] = subprocess.run,
        clock: Callable[[], float] = time.time,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        metrics_interval: float = METRICS_POLL_SECONDS,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.host_repo_root = Path(host_repo_root) if host_repo_root else self.repo_root
        self.settings = settings or KubernetesConfig()
        self.namespace = self.settings.namespace
        self.node = self.settings.node
        self.runner = runner
        self.clock = clock
        self.monotonic = monotonic
        self.sleep = sleep
        self.metrics_interval = metrics_interval
        self._api = api
        self._pods: dict[str, PodHandle] = {}
        self._tools: dict[str, ToolHandle] = {}
        self._pending: list[ToolHandle] = []
        self._buffers: dict[str, list[LineBuffer]] = {}
        self._responses: dict[str, list[Any]] = {}
        self._current_tool: str | None = None

    @property
    def api(self) -> KubeApi:
        if self._api is None:
            self._api = load_api(self.settings.kubeconfig, self.settings.context)
        return self._api

    def _call(self, kind: str, verb: str, namespace: str | None, *args: Any, **kwargs: Any) -> Any:
        api_name, suffix, namespaced = KINDS[kind]
        method = getattr(getattr(self.api, api_name), f"{verb}_{suffix}")
        if verb.startswith("create") or verb.startswith("list"):
            return method(namespace, *args, **kwargs) if namespaced else method(*args, **kwargs)
        name, *rest = args
        return method(name, namespace, *rest, **kwargs) if namespaced else method(name, *rest, **kwargs)

    def _delete(self, kind: str, name: str, namespace: str | None, grace: int | None = None) -> None:
        options: dict[str, Any] = {"propagation_policy": "Foreground"}
        if grace is not None:
            options["grace_period_seconds"] = grace
        try:
            self._call(kind, "delete", namespace, name, **options)
        except Exception as error:
            if not is_status(error, 404):
                raise

    def _exists(self, kind: str, name: str, namespace: str | None) -> bool:
        try:
            self._call(kind, "read", namespace, name)
            return True
        except Exception as error:
            if is_status(error, 404):
                return False
            raise

    def _wait_deleted(self, kind: str, name: str, namespace: str | None, timeout: float = DELETE_TIMEOUT) -> None:
        deadline = self.monotonic() + timeout
        while self._exists(kind, name, namespace):
            if self.monotonic() >= deadline:
                raise RuntimeError(f"{kind} {namespace}/{name} still present after {timeout:.0f}s")
            self.sleep(POLL_SECONDS)

    def _wait_pods_gone(self, namespace: str, selector: str, timeout: float = DELETE_TIMEOUT) -> None:
        deadline = self.monotonic() + timeout
        while self.api.core.list_namespaced_pod(namespace, label_selector=selector).items:
            if self.monotonic() >= deadline:
                raise RuntimeError(f"pods {selector} in {namespace} still present after {timeout:.0f}s")
            self.sleep(POLL_SECONDS)

    def _create(self, document: dict[str, Any], namespace: str | None) -> str:
        kind = document["kind"]
        name = document["metadata"]["name"]
        try:
            self._call(kind, "create", namespace, document)
        except Exception as error:
            if not is_status(error, 409):
                raise
            self._delete(kind, name, namespace)
            self._wait_deleted(kind, name, namespace)
            self._call(kind, "create", namespace, document)
        return name

    def _ensure_namespace(self, name: str, labels: dict[str, str] | None = None) -> None:
        body = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": name, "labels": dict(labels or {})}}
        deadline = self.monotonic() + DELETE_TIMEOUT
        while True:
            try:
                self.api.core.create_namespace(body)
                return
            except Exception as error:
                if not is_status(error, 409):
                    raise
            current = self.api.core.read_namespace(name)
            if getattr(getattr(current, "status", None), "phase", None) != "Terminating":
                return
            if self.monotonic() >= deadline:
                raise RuntimeError(f"namespace {name} stuck in Terminating")
            self.sleep(POLL_SECONDS)

    def _target_documents(self, key: str) -> list[dict[str, Any]]:
        documents = load_documents(self.repo_root / TARGETS_DIR / TARGET_FILES[key])
        prepared = []
        for document in documents:
            document = copy.deepcopy(document)
            metadata = document.setdefault("metadata", {})
            if document.get("kind") == "Namespace":
                metadata["name"] = self.namespace
            else:
                metadata["namespace"] = self.namespace
            if document.get("kind") == "Pod" and self.node:
                document.setdefault("spec", {})["nodeName"] = self.node
            if document.get("kind") == "Deployment" and self.node:
                document["spec"]["template"].setdefault("spec", {})["nodeName"] = self.node
            prepared.append(document)
        return prepared

    def _pick_node(self) -> str:
        for node in self.api.core.list_node().items:
            if getattr(node.spec, "unschedulable", False):
                continue
            conditions = {item.type: item.status for item in node.status.conditions or []}
            if conditions.get("Ready") == "True":
                return node.metadata.name
        raise RuntimeError("no Ready schedulable node found in the cluster")

    def _remove_labelled(self, namespace: str) -> None:
        for kind, lister in (
            ("Deployment", self.api.apps.list_namespaced_deployment),
            ("Service", self.api.core.list_namespaced_service),
            ("Pod", self.api.core.list_namespaced_pod),
        ):
            for item in lister(namespace, label_selector=ROLE_LABEL).items:
                self._delete(kind, item.metadata.name, namespace, grace=TARGET_STOP_TIMEOUT)
        self._wait_pods_gone(namespace, ROLE_LABEL)

    def prepare(self) -> None:
        namespace = self._target_documents("namespace")[0]
        self._ensure_namespace(self.namespace, (namespace.get("metadata") or {}).get("labels"))
        self._remove_labelled(self.namespace)
        self.node = self.node or self._pick_node()

    def _on_node(self, pod: Any) -> bool:
        node = getattr(getattr(pod, "spec", None), "node_name", None)
        return not (self.node and node and node != self.node)

    def _read_log(
        self, namespace: str, pod: str, container: str, previous: bool
    ) -> tuple[list[tuple[float, str]], str | None]:
        try:
            response = self.api.core.read_namespaced_pod_log(
                pod,
                namespace,
                container=container,
                previous=previous,
                timestamps=True,
                tail_lines=DIAGNOSTIC_LOG_LINES,
            )
        except Exception as error:
            return [], error_text(error)
        text = response.decode("utf-8", errors="replace") if isinstance(response, bytes) else str(response or "")
        return [split_timestamped(line) for line in text.splitlines() if line.strip()], None

    def _events(self, namespace: str) -> tuple[list[Any], str | None]:
        try:
            return list(self.api.core.list_namespaced_event(namespace).items or []), None
        except Exception as error:
            return [], error_text(error)

    def _diagnose(
        self,
        namespace: str,
        selector: str,
        containers: Iterable[str],
        followed: Iterable[str] = (),
        exclude: frozenset[str] = frozenset(),
    ) -> tuple[list[tuple[float, str]], str]:
        containers = tuple(containers)
        followed = tuple(followed)
        now = self.clock()
        lines: list[tuple[float, str]] = []
        try:
            listed = self.api.core.list_namespaced_pod(namespace, label_selector=selector).items or []
            pods = [pod for pod in listed if pod.metadata.uid not in exclude and self._on_node(pod)]
            failure = None
        except Exception as error:
            pods, failure = [], error_text(error)
        scope = f"{namespace} {selector} on node {self.node or 'any'}"
        lines.append((now, f"{DIAGNOSTICS_TAG} ===== {len(pods)} agent pod(s) {scope} ====="))
        if failure:
            lines.append((now, f"{DIAGNOSTICS_TAG} cannot list pods: {failure}"))
        collected: dict[tuple[str, str, bool], list[tuple[float, str]]] = {}
        target: tuple[str, Any, bool] | None = None
        fallback: tuple[str, Any, bool] | None = None
        for pod in pods:
            name = pod.metadata.name
            lines.extend((now, f"[{name}] {text}") for text in pod_summary(pod))
            for item, init in pod_containers(pod):
                if target is None and is_failing(item, init):
                    target = (name, item, init)
                if fallback is None and not init and item.name in containers:
                    fallback = (name, item, init)
                for previous in (False, True) if has_previous(item) else (False,):
                    tag = f"{name}/{item.name}{' previous' if previous else ''}"
                    logs, unavailable = self._read_log(namespace, name, item.name, previous)
                    if unavailable:
                        lines.append((now, f"[{tag}] logs unavailable: {unavailable}"))
                        continue
                    lines.append((now, f"[{tag}] ----- last {len(logs)} log lines (tail {DIAGNOSTIC_LOG_LINES}) -----"))
                    lines.extend((stamp, f"[{tag}] {text}") for stamp, text in logs)
                    collected[(name, item.name, previous)] = logs
        events, unavailable = self._events(namespace)
        lines.append((now, f"{DIAGNOSTICS_TAG} ----- {len(events)} event(s) in {namespace} -----"))
        if unavailable:
            lines.append((now, f"{DIAGNOSTICS_TAG} events unavailable: {unavailable}"))
        lines.extend((event_time(event, now), event_line(event)) for event in events)
        parts = [] if pods or failure else [f"no agent pod {scope}"]
        chosen = target or fallback
        if chosen is not None:
            name, item, init = chosen
            kind = "init container" if init else "container"
            parts.append(f"{kind} {name}/{item.name}: {format_state(getattr(item, 'state', None))}")
            previous = not collected.get((name, item.name, False)) and bool(collected.get((name, item.name, True)))
            logs = collected.get((name, item.name, previous)) or []
            if logs and (init or previous or item.name not in followed):
                label = f"{name}/{item.name}{' previous' if previous else ''}"
                parts.append(f"last logs ({label}):\n" + "\n".join(text for _, text in logs[-SUMMARY_LOG_LINES:]))
        warnings = [event for event in events if getattr(event, "type", None) == "Warning"]
        if warnings:
            parts.append("events:\n" + "\n".join(event_line(event) for event in warnings[-SUMMARY_EVENTS:]))
        parts.append("full diagnostics in container.log")
        return lines, "\n".join(parts)

    def _await_pod(
        self,
        namespace: str,
        containers: Iterable[str],
        timeout: float,
        name: str | None = None,
        selector: str | None = None,
        exclude: frozenset[str] = frozenset(),
        require_ready: bool = True,
    ) -> Any:
        containers = tuple(containers)
        deadline = self.monotonic() + timeout
        last = "no pod yet"
        while True:
            if name is not None:
                try:
                    pods = [self.api.core.read_namespaced_pod(name, namespace)]
                except Exception as error:
                    if not is_status(error, 404):
                        raise
                    pods = []
            else:
                pods = self.api.core.list_namespaced_pod(namespace, label_selector=selector).items
            candidates = [
                pod
                for pod in pods
                if pod.metadata.deletion_timestamp is None and pod.metadata.uid not in exclude and self._on_node(pod)
            ]
            for pod in candidates:
                state, detail = pod_state(pod, containers, require_ready)
                if state == "ready":
                    return pod
                if state == "failed":
                    raise PodStartError(f"pod {namespace}/{pod.metadata.name}: {detail}")
                last = f"{pod.metadata.name}: {detail}"
            if self.monotonic() >= deadline:
                raise PodStartError(f"timed out after {timeout:.0f}s waiting for a pod in {namespace}: {last}")
            self.sleep(POLL_SECONDS)

    def _create_pod(self, key: str) -> dict[str, Any]:
        document = self._target_documents(key)[0]
        self._delete("Pod", document["metadata"]["name"], self.namespace, grace=0)
        self._wait_deleted("Pod", document["metadata"]["name"], self.namespace)
        self._create(document, self.namespace)
        return document

    def _register_pod(self, document: dict[str, Any]) -> ContainerRef:
        name = document["metadata"]["name"]
        container = document["spec"]["containers"][0]["name"]
        pod = self._await_pod(self.namespace, (container,), TARGET_START_TIMEOUT, name=name)
        ref = ContainerRef(id=container_id(pod, container), name=name)
        self._pods[ref.id] = PodHandle(self.namespace, name, (container,), objects=[("Pod", name)])
        return ref

    def _start_attacker(self) -> tuple[list[dict[str, Any]], Callable[[], ContainerRef]]:
        documents = self._target_documents(ATTACKER_NAME)
        for document in documents:
            self._delete(document["kind"], document["metadata"]["name"], self.namespace)
        for document in documents:
            self._wait_deleted(document["kind"], document["metadata"]["name"], self.namespace)
            self._create(document, self.namespace)
        deployment = next(item for item in documents if item["kind"] == "Deployment")
        selector = selector_string(deployment["spec"]["selector"]["matchLabels"])
        container = deployment["spec"]["template"]["spec"]["containers"][0]["name"]

        def register() -> ContainerRef:
            pod = self._await_pod(self.namespace, (container,), TARGET_START_TIMEOUT, selector=selector)
            ref = ContainerRef(id=container_id(pod, container), name=ATTACKER_NAME)
            self._pods[ref.id] = PodHandle(
                self.namespace,
                pod.metadata.name,
                (container,),
                objects=[(item["kind"], item["metadata"]["name"]) for item in documents],
                selector=selector,
            )
            return ref

        return documents, register

    def start_targets(self) -> Targets:
        _, register_attacker = self._start_attacker()
        victim = self._create_pod(VICTIM_NAME)
        privileged = self._create_pod(PRIVILEGED_VICTIM_NAME)
        attacker_ref = register_attacker()
        return Targets(
            victim=self._register_pod(victim),
            victim_privileged=self._register_pod(privileged),
            attacker=attacker_ref,
        )

    def start_workload_host(self) -> ContainerRef:
        return self._register_pod(self._create_pod(WORKLOAD_HOST_NAME))

    def _helm(self, command: list[str]) -> None:
        try:
            result = self.runner(command, capture_output=True, text=True, timeout=HELM_TIMEOUT, check=False)
        except FileNotFoundError as error:
            raise ToolStartError("helm binary not found in PATH") from error
        except subprocess.TimeoutExpired as error:
            raise ToolStartError(f"{' '.join(command[:2])} timed out after {HELM_TIMEOUT:.0f}s") from error
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()[-2000:]
            raise ToolStartError(f"{' '.join(command[:3])} failed with code {result.returncode}: {detail}")

    def _apply_configmap(self, handle: ToolHandle, name: str, data: dict[str, str]) -> None:
        body = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": name, "labels": {ROLE_LABEL: "tool-config"}},
            "data": data,
        }
        try:
            self.api.core.create_namespaced_config_map(handle.namespace, body)
        except Exception as error:
            if not is_status(error, 409):
                raise
            self.api.core.replace_namespaced_config_map(name, handle.namespace, body)
        handle.configmaps.append(name)

    def _create_custom(self, resource: CustomResource) -> None:
        custom = self.api.custom
        if resource.namespace:
            custom.create_namespaced_custom_object(
                resource.group, resource.version, resource.namespace, resource.plural, resource.body
            )
        else:
            custom.create_cluster_custom_object(resource.group, resource.version, resource.plural, resource.body)

    def _delete_custom(self, resource: CustomResource) -> None:
        custom = self.api.custom
        try:
            if resource.namespace:
                custom.delete_namespaced_custom_object(
                    resource.group, resource.version, resource.namespace, resource.plural, resource.name
                )
            else:
                custom.delete_cluster_custom_object(resource.group, resource.version, resource.plural, resource.name)
        except Exception as error:
            if not is_status(error, 404):
                raise

    def _apply_custom_resources(self, handle: ToolHandle, profile_dir: Path, timeout: float) -> None:
        deadline = self.monotonic() + timeout
        for entry in handle.deployment.custom_resources:
            for resource in custom_resources(entry, profile_dir, self.namespace):
                while True:
                    try:
                        self._create_custom(resource)
                        break
                    except Exception as error:
                        if is_status(error, 409):
                            self._delete_custom(resource)
                        elif not is_status(error, 404) or self.monotonic() >= deadline:
                            raise ToolStartError(
                                f"cannot create {resource.plural}/{resource.name}: {error}"
                            ) from error
                        self.sleep(POLL_SECONDS)
                handle.resources.append(resource)

    def _install_manifests(self, handle: ToolHandle) -> None:
        deployment = handle.deployment
        install = deployment.install
        documents = [copy.deepcopy(item) for name in install["manifests"] for item in load_documents(deployment.directory / name)]
        for document in documents:
            if install.get("from_adapter") and document.get("kind") in ("DaemonSet", "Deployment"):
                pod_spec = document["spec"]["template"].setdefault("spec", {})
                for name, data in adapter_pod_spec(
                    pod_spec, str(install["container"]), handle.spec, deployment.tool, self.repo_root, self.host_repo_root
                ):
                    self._apply_configmap(handle, name, data)
        for document in documents:
            if KINDS[document["kind"]][2]:
                document.setdefault("metadata", {})["namespace"] = deployment.namespace
            handle.objects.append((document["kind"], self._create(document, deployment.namespace)))

    def _restart_daemonsets(self, handle: ToolHandle) -> frozenset[str]:
        namespace = handle.namespace
        existing = self.api.core.list_namespaced_pod(namespace, label_selector=handle.deployment.selector).items
        stamp = datetime.fromtimestamp(self.clock(), UTC).isoformat()
        body = {"spec": {"template": {"metadata": {"annotations": {RESTART_ANNOTATION: stamp}}}}}
        for daemonset in self.api.apps.list_namespaced_daemon_set(namespace).items:
            self.api.apps.patch_namespaced_daemon_set(daemonset.metadata.name, namespace, body)
        return frozenset(pod.metadata.uid for pod in existing)

    def start_tool(self, tool: str, profile: str, spec: ContainerSpec) -> ContainerRef:
        deployment = load_tool_deployment(self.repo_root, tool)
        handle = ToolHandle(deployment=deployment, profile=profile, spec=spec)
        profile_dir = self.repo_root / "tools" / tool / profile
        timeout = deployment.startup_timeout or spec.startup_timeout
        exclude: frozenset[str] = frozenset()
        self._pending.append(handle)
        try:
            self._ensure_namespace(deployment.namespace, {ROLE_LABEL: "tool"})
            for entry in deployment.configmaps:
                self._apply_configmap(handle, str(entry["name"]), configmap_source(profile_dir, entry))
            if deployment.kind == "helm":
                handle.helm = True
                self._helm(helm_install_command(deployment, profile, profile_dir, self.settings))
            else:
                self._install_manifests(handle)
            self._apply_custom_resources(handle, profile_dir, timeout)
            if deployment.restart_after_resources and handle.resources:
                exclude = self._restart_daemonsets(handle)
            pod = self._await_pod(
                deployment.namespace,
                deployment.log_containers,
                timeout,
                selector=deployment.selector,
                exclude=exclude,
                require_ready=False,
            )
        except Exception as error:
            diagnostics, summary = self._diagnose(
                deployment.namespace, deployment.selector, deployment.log_containers, exclude=exclude
            )
            self._pending.remove(handle)
            try:
                self._teardown_tool(handle)
            except Exception:
                pass
            raise with_diagnostics(error, summary, diagnostics) from error
        self._pending.remove(handle)
        handle.pod = pod.metadata.name
        handle.restarts = restart_counts(pod)
        ref = ContainerRef(id=str(pod.metadata.uid), name=str(pod.metadata.name))
        self._tools[ref.id] = handle
        self._current_tool = ref.id
        return ref

    def _log_source(self, key: str, namespace: str, pod: str, container: str) -> Callable[[], Iterable[bytes]]:
        def open_stream() -> Iterable[bytes]:
            response = self.api.core.read_namespaced_pod_log(
                pod, namespace, container=container, follow=True, timestamps=True, _preload_content=False
            )
            self._responses.setdefault(key, []).append(response)
            if hasattr(response, "stream"):
                return response.stream(amt=None, decode_content=False)
            return iter(response)

        return open_stream

    def _follow(self, key: str, namespace: str, pod: str, containers: Iterable[str]) -> LineBuffer:
        buffer = LineBuffer()
        sources = [self._log_source(key, namespace, pod, container) for container in containers]
        self._buffers.setdefault(key, []).append(buffer)
        pump_log_streams(sources, buffer, f"logs-{pod}")
        return buffer

    def _location(self, ref: ContainerRef) -> tuple[str, str, tuple[str, ...]]:
        if ref.id in self._tools:
            handle = self._tools[ref.id]
            return handle.namespace, str(handle.pod), handle.deployment.log_containers
        if ref.id in self._pods:
            target = self._pods[ref.id]
            return target.namespace, target.pod, target.containers
        raise KeyError(f"unknown container reference {ref.name}")

    def follow_logs(self, ref: ContainerRef) -> LineBuffer:
        namespace, pod, containers = self._location(ref)
        return self._follow(ref.id, namespace, pod, containers)

    def _open_exec(self, namespace: str, pod: str, container: str, command: list[str]) -> Any:
        return self.api.stream(
            self.api.exec_core.connect_get_namespaced_pod_exec,
            pod,
            namespace,
            container=container,
            command=command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _preload_content=False,
        )

    def _exec_source(
        self, key: str, namespace: str, pod: str, container: str, command: list[str], buffer: LineBuffer
    ) -> Callable[[], Iterable[str]]:
        def open_stream() -> Iterable[str]:
            client = None
            for _ in range(EXEC_OPEN_ATTEMPTS):
                if buffer.stop_requested.is_set():
                    return
                try:
                    client = self._open_exec(namespace, pod, container, command)
                    break
                except Exception:
                    self.sleep(POLL_SECONDS)
            if client is None:
                return
            self._responses.setdefault(key, []).append(client)
            try:
                while client.is_open():
                    client.update(timeout=POLL_SECONDS)
                    if client.peek_stdout():
                        yield client.read_stdout()
                    if client.peek_stderr():
                        client.read_stderr()
                if client.peek_stdout():
                    yield client.read_stdout()
            finally:
                try:
                    client.close()
                except Exception:
                    pass

        return open_stream

    def tail_file(self, path: Path) -> LineBuffer:
        handle = self._tools.get(self._current_tool or "")
        if handle is None:
            buffer = LineBuffer()
            buffer.close()
            return buffer
        key = str(self._current_tool)
        deployment = handle.deployment
        if deployment.alerts_file is None:
            return self._follow(key, handle.namespace, str(handle.pod), (deployment.alerts_container,))
        buffer = LineBuffer()
        self._buffers.setdefault(key, []).append(buffer)
        source = self._exec_source(
            key, handle.namespace, str(handle.pod), deployment.alerts_container, tail_command(deployment.alerts_file), buffer
        )
        pump_read_lines(source, buffer, self.clock, f"tail-{handle.pod}")
        return buffer

    def _log_tail(self, logs: LineBuffer, count: int = 20) -> str:
        return "\n".join(line for _, line in logs.lines()[-count:])

    def _ensure_running(self, ref: ContainerRef, logs: LineBuffer) -> None:
        handle = self._tools.get(ref.id)
        if handle is None:
            return
        try:
            pod = self.api.core.read_namespaced_pod(handle.pod, handle.namespace)
        except Exception as error:
            if is_status(error, 404):
                raise ToolStartError(f"pod {handle.namespace}/{handle.pod} disappeared") from error
            raise
        state, detail = pod_state(pod, handle.deployment.log_containers, require_ready=False)
        restarted = [
            name for name, count in restart_counts(pod).items() if count > handle.restarts.get(name, 0)
        ]
        if state == "failed" or restarted:
            reason = detail if state == "failed" else f"containers restarted: {restarted}"
            raise ToolStartError(f"pod {handle.pod}: {reason}; last logs:\n{self._log_tail(logs)}")

    def wait_ready(self, ref: ContainerRef, logs: LineBuffer, pattern: str | None, timeout: float) -> None:
        handle = self._tools.get(ref.id)
        if handle is not None and handle.deployment.ready_pattern != ADAPTER:
            pattern = handle.deployment.ready_pattern
        if handle is not None and handle.deployment.startup_timeout:
            timeout = handle.deployment.startup_timeout
        try:
            self._wait_ready(ref, logs, pattern, timeout)
        except Exception as error:
            if handle is None:
                raise
            deployment = handle.deployment
            diagnostics, summary = self._diagnose(
                handle.namespace, deployment.selector, deployment.log_containers, followed=deployment.log_containers
            )
            raise with_diagnostics(error, summary, diagnostics) from error

    def _wait_ready(self, ref: ContainerRef, logs: LineBuffer, pattern: str | None, timeout: float) -> None:
        if pattern is None:
            self.sleep(min(3.0, timeout))
            self._ensure_running(ref, logs)
            return
        deadline = self.monotonic() + timeout
        while True:
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                break
            if logs.wait_for(pattern, min(2.0, remaining)):
                return
            self._ensure_running(ref, logs)
            if logs.closed:
                self.sleep(min(1.0, max(remaining, 0)))
        raise ToolStartError(
            f"ready pattern {pattern!r} not seen within {timeout:.0f}s; last logs:\n{self._log_tail(logs)}"
        )

    def exec(self, ref: ContainerRef, command: list[str], environment: dict[str, str], timeout: float) -> ExecResult:
        namespace, pod, containers = self._location(ref)
        if ref.id in self._tools:
            containers = (self._tools[ref.id].deployment.alerts_container,)
        argv = exec_command(command, environment, timeout)
        started_at = self.clock()
        try:
            client = self._open_exec(namespace, pod, containers[0], argv)
        except Exception as error:
            return ExecResult(-1, f"[bench] exec error: {error}", started_at, self.clock())
        chunks: list[str] = []
        timed_out = False
        exit_code: Any = None
        failure: Exception | None = None
        deadline = self.monotonic() + timeout + EXEC_GRACE_SECONDS
        try:
            while client.is_open():
                remaining = deadline - self.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                client.update(timeout=min(1.0, remaining))
                self._drain_exec(client, chunks)
            ended_at = self.clock()
            self._drain_exec(client, chunks)
            if not timed_out:
                exit_code = client.returncode
        except Exception as error:
            ended_at = self.clock()
            failure = error
        finally:
            try:
                client.close()
            except Exception:
                pass
        output = "".join(chunks)
        if failure is not None:
            output += f"\n[bench] exec error: {failure}"
        elapsed = ended_at - started_at
        if timed_out or (exit_code in EXEC_TIMEOUT_CODES and elapsed >= timeout):
            return ExecResult(TIMEOUT_EXIT_CODE, output + f"\n[bench] timed out after {timeout:g}s", started_at, ended_at)
        return ExecResult(exit_code if isinstance(exit_code, int) else -1, output, started_at, ended_at)

    @staticmethod
    def _drain_exec(client: Any, chunks: list[str]) -> None:
        if client.peek_stdout():
            chunks.append(client.read_stdout())
        if client.peek_stderr():
            chunks.append(client.read_stderr())

    def _pod_metrics(self, namespace: str, pod: str) -> tuple[str, float | None, float | None] | None:
        try:
            data = self.api.custom.get_namespaced_custom_object(METRICS_GROUP, METRICS_VERSION, namespace, "pods", pod)
        except Exception:
            return None
        return pod_metrics_sample(data)

    def start_stats(self, ref: ContainerRef) -> StatsSampler:
        namespace, pod, _ = self._location(ref)
        return MetricsSampler(lambda: self._pod_metrics(namespace, pod), self.metrics_interval)

    def _teardown_tool(self, handle: ToolHandle) -> None:
        errors: list[str] = []
        for resource in reversed(handle.resources):
            try:
                self._delete_custom(resource)
            except Exception as error:
                errors.append(f"delete {resource.plural}/{resource.name}: {error}")
        if handle.helm:
            try:
                self._helm(helm_uninstall_command(handle.deployment, self.settings))
            except Exception as error:
                errors.append(str(error))
        for kind, name in reversed(handle.objects):
            try:
                self._delete(kind, name, handle.namespace)
            except Exception as error:
                errors.append(f"delete {kind}/{name}: {error}")
        try:
            self._wait_pods_gone(handle.namespace, handle.deployment.selector)
        except Exception as error:
            errors.append(str(error))
        for name in handle.configmaps:
            try:
                self._delete("ConfigMap", name, handle.namespace)
            except Exception as error:
                errors.append(f"delete configmap {name}: {error}")
        if errors:
            raise RuntimeError("; ".join(errors))

    def _drain(self, key: str) -> None:
        buffers = self._buffers.pop(key, [])
        for buffer in buffers:
            buffer.wait_closed(LOG_DRAIN_TIMEOUT)
        for response in self._responses.pop(key, []):
            for method in ("close", "release_conn"):
                try:
                    getattr(response, method)()
                except Exception:
                    pass
        for buffer in buffers:
            buffer.wait_closed(1.0)

    def stop(self, ref: ContainerRef) -> None:
        failure: Exception | None = None
        if ref.id in self._tools:
            handle = self._tools.pop(ref.id)
            if self._current_tool == ref.id:
                self._current_tool = None
            try:
                self._teardown_tool(handle)
            except Exception as error:
                failure = error
        elif ref.id in self._pods:
            target = self._pods.pop(ref.id)
            for kind, name in target.objects:
                self._delete(kind, name, target.namespace, grace=TARGET_STOP_TIMEOUT)
            for kind, name in target.objects:
                if kind == "Pod":
                    self._wait_deleted(kind, name, target.namespace)
            if target.selector:
                self._wait_pods_gone(target.namespace, target.selector)
        self._drain(ref.id)
        if failure is not None:
            raise failure

    def cleanup(self) -> None:
        for key in list(self._tools) + list(self._pods):
            try:
                self.stop(ContainerRef(id=key, name=key))
            except Exception:
                pass
        for handle in list(self._pending):
            try:
                self._teardown_tool(handle)
            except Exception:
                pass
        self._pending.clear()
        try:
            self._remove_labelled(self.namespace)
        except Exception:
            pass

    def host_info(self) -> dict[str, Any]:
        self.node = self.node or self._pick_node()
        node = self.api.core.read_node(self.node)
        info = node.status.node_info
        capacity = node.status.capacity or {}
        cpus = parse_cpu(capacity.get("cpu"))
        server = None
        if self.api.version is not None:
            try:
                server = self.api.version.get_code().git_version
            except Exception:
                server = None
        return {
            "backend": "kubernetes",
            "kernel": info.kernel_version,
            "operating_system": info.os_image,
            "architecture": info.architecture,
            "cpus": int(cpus) if cpus is not None else None,
            "memory_bytes": parse_memory(capacity.get("memory")),
            "node": node.metadata.name if is_kind_node(node) else None,
            "container_runtime": info.container_runtime_version,
            "kubelet_version": info.kubelet_version,
            "kubernetes_version": server,
            "kube_context": self.settings.context,
            "namespace": self.namespace,
            "runner_python": platform.python_version(),
        }
