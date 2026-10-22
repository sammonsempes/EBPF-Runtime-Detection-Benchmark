from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ScenarioKind(str, Enum):
    ATTACK = "attack"
    BENIGN = "benign"


@dataclass(frozen=True)
class Scenario:
    id: str
    name: str
    kind: ScenarioKind
    description: str
    path: Path
    tactic: str | None = None
    technique: str | None = None
    timeout: float = 60.0
    requires: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScenarioRun:
    scenario_id: str
    tool: str
    profile: str
    repetition: int
    marker: str
    victim_container_id: str
    started_at: float
    ended_at: float
    exit_code: int
    output: str = ""
    action_at: float | None = None
    effect_achieved: bool | None = None
    check_exit_code: int | None = None
    cleanup_exit_code: int | None = None


@dataclass(frozen=True)
class Alert:
    tool: str
    rule: str
    emitted_at: float
    severity: str | None = None
    event_at: float | None = None
    container_id: str | None = None
    container_name: str | None = None
    process: str | None = None
    command_line: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    action: str | None = None


@dataclass(frozen=True)
class WorkloadResult:
    name: str
    tool: str | None
    profile: str | None
    repetition: int
    metrics: dict[str, float]
    tool_cpu_percent: list[float] = field(default_factory=list)
    tool_memory_bytes: list[float] = field(default_factory=list)
    host_cpu_percent: list[float] = field(default_factory=list)
