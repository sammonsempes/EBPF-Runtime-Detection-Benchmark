from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from bench.adapters import TOOLS

DEFAULT_PROFILES = ("default", "tuned")
ALL_PROFILES = ("default", "tuned", "enforce")
ENFORCE_PROFILES = ("enforce",)
CONTROL_TOOL = "none"
CONTROL_PROFILE = "control"
DEFAULT_WORKLOADS = ("syscall", "exec", "fileio")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
CONFIG_KEYS = frozenset(
    {
        "tools",
        "profiles",
        "scenarios",
        "repetitions",
        "grace_seconds",
        "idle_seconds",
        "control_scenarios",
        "overhead",
        "results_dir",
        "backend",
        "kubernetes",
    }
)
OVERHEAD_KEYS = frozenset({"enabled", "duration_seconds", "repetitions", "workloads"})
BACKENDS = ("docker", "kubernetes")
KUBERNETES_KEYS = frozenset({"kubeconfig", "context", "namespace", "node"})
DEFAULT_KUBERNETES_NAMESPACE = "ebpf-bench"
KUBERNETES_NAME_PATTERN = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")


def _require_int(name: str, value: Any, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}, got {value!r}")


def _require_number(name: str, value: Any, minimum: float, strict: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {value!r}")
    if value < minimum or (strict and value == minimum):
        relation = ">" if strict else ">="
        raise ValueError(f"{name} must be {relation} {minimum}, got {value!r}")


def _require_names(name: str, values: Any, allow_empty: bool = False) -> None:
    if not isinstance(values, tuple):
        raise ValueError(f"{name} must be a list of names, got {values!r}")
    if not values and not allow_empty:
        raise ValueError(f"{name} must not be empty")
    for value in values:
        if not isinstance(value, str) or not NAME_PATTERN.match(value):
            raise ValueError(f"{name} contains an invalid name: {value!r}")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} contains duplicates: {list(values)}")


@dataclass(frozen=True)
class OverheadConfig:
    enabled: bool = True
    duration_seconds: float = 30.0
    repetitions: int = 3
    workloads: tuple[str, ...] = DEFAULT_WORKLOADS

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError(f"overhead.enabled must be a boolean, got {self.enabled!r}")
        _require_number("overhead.duration_seconds", self.duration_seconds, 0, strict=True)
        _require_int("overhead.repetitions", self.repetitions, 1)
        _require_names("overhead.workloads", self.workloads, allow_empty=True)


@dataclass(frozen=True)
class KubernetesConfig:
    kubeconfig: str | None = None
    context: str | None = None
    namespace: str = DEFAULT_KUBERNETES_NAMESPACE
    node: str | None = None

    def __post_init__(self) -> None:
        for name in ("kubeconfig", "context", "node"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError(f"kubernetes.{name} must be a non-empty string or null, got {value!r}")
        if not isinstance(self.namespace, str) or not KUBERNETES_NAME_PATTERN.match(self.namespace):
            raise ValueError(f"kubernetes.namespace must be a valid namespace name, got {self.namespace!r}")

    def as_dict(self) -> dict[str, Any]:
        return {"kubeconfig": self.kubeconfig, "context": self.context, "namespace": self.namespace, "node": self.node}


@dataclass(frozen=True)
class Config:
    tools: tuple[str, ...] = TOOLS
    profiles: tuple[str, ...] = DEFAULT_PROFILES
    scenarios: tuple[str, ...] | None = None
    repetitions: int = 5
    grace_seconds: float = 10.0
    idle_seconds: float = 3.0
    overhead: OverheadConfig = field(default_factory=OverheadConfig)
    results_dir: Path = Path("results")
    backend: str = "docker"
    kubernetes: KubernetesConfig = field(default_factory=KubernetesConfig)
    source: str = ""
    control_scenarios: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.control_scenarios, bool):
            raise ValueError(f"control_scenarios must be a boolean, got {self.control_scenarios!r}")
        if self.backend not in BACKENDS:
            raise ValueError(f"backend must be one of {list(BACKENDS)}, got {self.backend!r}")
        if not isinstance(self.kubernetes, KubernetesConfig):
            raise ValueError("kubernetes must be a KubernetesConfig")
        _require_names("tools", self.tools)
        unknown = [tool for tool in self.tools if tool not in TOOLS]
        if unknown:
            raise ValueError(f"unknown tools {unknown}, expected a subset of {list(TOOLS)}")
        _require_names("profiles", self.profiles)
        if self.scenarios is not None:
            _require_names("scenarios", self.scenarios)
        _require_int("repetitions", self.repetitions, 1)
        _require_number("grace_seconds", self.grace_seconds, 0)
        _require_number("idle_seconds", self.idle_seconds, 0)
        if not isinstance(self.overhead, OverheadConfig):
            raise ValueError("overhead must be an OverheadConfig")
        if not isinstance(self.results_dir, Path):
            raise ValueError(f"results_dir must be a path, got {self.results_dir!r}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "tools": list(self.tools),
            "profiles": list(self.profiles),
            "scenarios": "all" if self.scenarios is None else list(self.scenarios),
            "repetitions": self.repetitions,
            "grace_seconds": self.grace_seconds,
            "idle_seconds": self.idle_seconds,
            "control_scenarios": self.control_scenarios,
            "overhead": {
                "enabled": self.overhead.enabled,
                "duration_seconds": self.overhead.duration_seconds,
                "repetitions": self.overhead.repetitions,
                "workloads": list(self.overhead.workloads),
            },
            "results_dir": str(self.results_dir),
            "backend": self.backend,
            "kubernetes": self.kubernetes.as_dict(),
        }


def _names(name: str, value: Any, all_value: tuple[str, ...] | None) -> tuple[str, ...] | None:
    if value == "all":
        return all_value
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(value)
    raise ValueError(f"{name} must be 'all' or a list, got {value!r}")


def _overhead(value: Any) -> OverheadConfig:
    if value is None:
        return OverheadConfig()
    if value is False:
        return OverheadConfig(enabled=False)
    if not isinstance(value, dict):
        raise ValueError(f"overhead must be a mapping, got {value!r}")
    unknown = sorted(set(value) - OVERHEAD_KEYS)
    if unknown:
        raise ValueError(f"unknown overhead keys: {unknown}")
    workloads = value.get("workloads", list(DEFAULT_WORKLOADS))
    if workloads is None:
        workloads = []
    if not isinstance(workloads, list):
        raise ValueError(f"overhead.workloads must be a list, got {workloads!r}")
    return OverheadConfig(
        enabled=value.get("enabled", True),
        duration_seconds=value.get("duration_seconds", 30.0),
        repetitions=value.get("repetitions", 3),
        workloads=tuple(workloads),
    )


def _kubernetes(value: Any) -> KubernetesConfig:
    if value is None:
        return KubernetesConfig()
    if not isinstance(value, dict):
        raise ValueError(f"kubernetes must be a mapping, got {value!r}")
    unknown = sorted(set(value) - KUBERNETES_KEYS)
    if unknown:
        raise ValueError(f"unknown kubernetes keys: {unknown}")
    namespace = value.get("namespace")
    return KubernetesConfig(
        kubeconfig=value.get("kubeconfig"),
        context=value.get("context"),
        namespace=DEFAULT_KUBERNETES_NAMESPACE if namespace is None else namespace,
        node=value.get("node"),
    )


def parse_config(data: Any, source: str = "") -> Config:
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("configuration must be a mapping")
    unknown = sorted(set(data) - CONFIG_KEYS)
    if unknown:
        raise ValueError(f"unknown configuration keys: {unknown}")
    tools = _names("tools", data.get("tools", "all"), TOOLS)
    profiles = _names("profiles", data.get("profiles", list(DEFAULT_PROFILES)), ALL_PROFILES)
    scenarios = _names("scenarios", data.get("scenarios", "all"), None)
    results_dir = data.get("results_dir", "results")
    if not isinstance(results_dir, str) or not results_dir:
        raise ValueError(f"results_dir must be a non-empty string, got {results_dir!r}")
    return Config(
        tools=tools,
        profiles=profiles,
        scenarios=scenarios,
        repetitions=data.get("repetitions", 5),
        grace_seconds=data.get("grace_seconds", 10.0),
        idle_seconds=data.get("idle_seconds", 3.0),
        control_scenarios=data.get("control_scenarios", True),
        overhead=_overhead(data.get("overhead")),
        results_dir=Path(results_dir),
        backend=data.get("backend", "docker"),
        kubernetes=_kubernetes(data.get("kubernetes")),
        source=source,
    )


def load_config(path: Path) -> Config:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"configuration file not found: {path}")
    source = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(source)
    except yaml.YAMLError as error:
        raise ValueError(f"{path}: invalid YAML: {error}") from error
    try:
        return parse_config(data, source)
    except ValueError as error:
        raise ValueError(f"{path}: {error}") from error
