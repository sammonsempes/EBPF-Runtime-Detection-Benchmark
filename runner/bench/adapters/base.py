from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from bench.model import Alert


@dataclass(frozen=True)
class Mount:
    source: str
    target: str
    read_only: bool = True


@dataclass(frozen=True)
class ContainerSpec:
    image: str
    command: list[str] = field(default_factory=list)
    entrypoint: list[str] | None = None
    build_context: str | None = None
    privileged: bool = True
    pid_mode: str | None = "host"
    network_mode: str | None = "host"
    cgroupns_mode: str | None = "host"
    cap_add: list[str] = field(default_factory=list)
    security_opt: list[str] = field(default_factory=list)
    mounts: list[Mount] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    ready_pattern: str | None = None
    startup_timeout: float = 120.0
    alerts_file: str | None = None
    settle_seconds: float = 5.0
    ready_url: str | None = None


class ToolAdapter(ABC):
    name: str
    version: str
    profiles: tuple[str, ...] = ("default", "tuned")

    def config_dir(self, repo_root: Path, profile: str) -> Path:
        return repo_root / "tools" / self.name / profile

    def is_enforcement(self, alert: Alert) -> bool:
        return False

    def enforcement_check(self, log_lines: list[str]) -> bool | None:
        return None

    def confirmed_enforcements(self, log_lines: list[tuple[float, str]]) -> list[float]:
        return []

    @abstractmethod
    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec: ...

    @abstractmethod
    def parse(self, line: str, emitted_at: float) -> Alert | None: ...

    @staticmethod
    def load_json(line: str) -> dict[str, Any] | None:
        line = line.strip()
        if not line.startswith("{"):
            return None
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def parse_time(value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            number = float(value)
            for threshold, divisor in ((1e17, 1e9), (1e14, 1e6), (1e11, 1e3)):
                if number > threshold:
                    return number / divisor
            return number
        if isinstance(value, str):
            text = value.strip().replace("Z", "+00:00")
            if "." in text:
                head, _, tail = text.partition(".")
                digits = "".join(ch for ch in tail if ch.isdigit())
                zone = tail[len(digits):]
                text = f"{head}.{digits[:6]}{zone}"
            try:
                return datetime.fromisoformat(text).timestamp()
            except ValueError:
                return None
        return None
