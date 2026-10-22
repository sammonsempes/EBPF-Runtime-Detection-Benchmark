from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.model import Alert

CONTAINER_ID = re.compile(r"[0-9a-f]{12,64}")
UNKNOWN = {"", "?"}
KILL_ACTION = "kill"
KILL_CONFIRMATION = "sending SIGKILL to PID="


def _section(value: Any, key: str) -> dict[str, Any]:
    if isinstance(value, dict):
        child = value.get(key)
        if isinstance(child, dict):
            return child
    return {}


class Adapter(ToolAdapter):
    name = "kunai"
    version = "0.6.2"
    profiles = ("default", "tuned", "enforce")
    config_mount = "/etc/kunai"

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        tool_dir = Path(host_repo_root) / "tools" / self.name
        return ContainerSpec(
            image=f"ebpf-bench/{self.name}:{self.version}",
            command=["run", "-c", f"{self.config_mount}/config.yaml"],
            mounts=[
                Mount(source=str(tool_dir / profile), target=self.config_mount),
                Mount(source="/sys/kernel/debug", target="/sys/kernel/debug", read_only=False),
                Mount(source="/sys/kernel/btf", target="/sys/kernel/btf"),
                Mount(source="/sys/fs/bpf", target="/sys/fs/bpf", read_only=False),
            ],
            ready_pattern=r'"source":"kunai","id":1101,"name":"start"',
        )

    def is_enforcement(self, alert: Alert) -> bool:
        actions = _section(alert.raw, "detection").get("actions")
        return isinstance(actions, list) and KILL_ACTION in actions

    def enforcement_check(self, log_lines: list[str]) -> bool | None:
        return True if any(KILL_CONFIRMATION in line for line in log_lines) else None

    def confirmed_enforcements(self, log_lines: list[tuple[float, str]]) -> list[float]:
        return [emitted_at for emitted_at, line in log_lines if KILL_CONFIRMATION in line]

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        event = self.load_json(line)
        if event is None:
            return None
        detection = event.get("detection")
        if not isinstance(detection, dict):
            return None
        info = _section(event, "info")
        if _section(info, "event").get("source") != "kunai":
            return None
        data = _section(event, "data")
        names = sorted(detection.get("rules") or []) or sorted(f"ioc:{ioc}" for ioc in detection.get("iocs") or [])
        severity = detection.get("severity")
        container = _section(_section(info, "host"), "container")
        container_name = container.get("name")
        if not isinstance(container_name, str) or container_name in UNKNOWN:
            container_name = None
        container_id = container_name if container_name and CONTAINER_ID.fullmatch(container_name) else None
        exe = data.get("exe")
        process = exe.get("path") if isinstance(exe, dict) else None
        if not process:
            process = _section(info, "task").get("name")
        command_line = data.get("command_line")
        actions = detection.get("actions")
        return Alert(
            tool=self.name,
            rule=",".join(names) if names else "unknown",
            emitted_at=emitted_at,
            severity=None if severity is None else str(severity),
            event_at=self.parse_time(info.get("utc_time")),
            container_id=container_id,
            container_name=container_name,
            process=process,
            command_line=command_line if isinstance(command_line, str) else None,
            raw=event,
            action=KILL_ACTION if isinstance(actions, list) and KILL_ACTION in actions else None,
        )
