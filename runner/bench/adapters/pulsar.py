from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.model import Alert

PLAINTEXT_THREAT = re.compile(
    r"^\[(?P<time>\S+)\s+(?:\x1b\[[0-9;]*m)?THREAT(?:\x1b\[0m)?\s+(?P<process>.*?)\s+\((?P<pid>-?\d+)\)\]\s+"
    r"\[(?P<source>[^\s\]]+) - (?P<description>.*?)\]\s(?P<payload>.*)$"
)
LEGACY_RULE_NAME = re.compile(r'rule_name\s*=\s*"(?P<name>[^"]*)"')


def _section(value: Any, key: str) -> dict[str, Any]:
    if isinstance(value, dict):
        child = value.get(key)
        if isinstance(child, dict):
            return child
    return {}


def _system_time(value: Any) -> float | None:
    if isinstance(value, dict) and "secs_since_epoch" in value:
        return float(value["secs_since_epoch"]) + float(value.get("nanos_since_epoch", 0)) / 1e9
    return None


class Adapter(ToolAdapter):
    name = "pulsar"
    version = "0.10.1"
    image = "ghcr.io/exein-io/pulsar"
    config_mount = "/etc/bench/pulsar"
    rules_root = "/var/lib/pulsar/rules"

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        profile_dir = Path(host_repo_root) / "tools" / self.name / profile
        return ContainerSpec(
            image=f"{self.image}:v{self.version}",
            command=["--config-file", f"{self.config_mount}/pulsar.ini"],
            mounts=[
                Mount(source=str(profile_dir), target=self.config_mount),
                Mount(source=str(profile_dir / "rules"), target=f"{self.rules_root}/bench-{profile}"),
                Mount(source="/sys/kernel/debug", target="/sys/kernel/debug", read_only=False),
                Mount(source="/sys/kernel/btf", target="/sys/kernel/btf"),
                Mount(source="/sys/fs/bpf", target="/sys/fs/bpf", read_only=False),
                Mount(source="/var/lib/docker", target="/var/lib/docker"),
            ],
            ready_pattern=r"Starting module rules-engine",
        )

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        event = self.load_json(line)
        if event is not None:
            return self._parse_json(event, emitted_at)
        return self._parse_plaintext(line, emitted_at)

    def _parse_json(self, event: dict[str, Any], emitted_at: float) -> Alert | None:
        header = _section(event, "header")
        threat = header.get("threat")
        if not isinstance(threat, dict):
            return None
        extra = threat.get("extra") if isinstance(threat.get("extra"), dict) else {}
        container = _section(header, "container")
        payload = _section(event, "payload")
        content = payload.get("content") if isinstance(payload.get("content"), dict) else {}
        argv = content.get("argv") if payload.get("type") == "Exec" else None
        severity = extra.get("severity")
        return Alert(
            tool=self.name,
            rule=str(threat.get("description") or threat.get("source") or "unknown"),
            emitted_at=emitted_at,
            severity=None if severity is None else str(severity),
            event_at=_system_time(header.get("timestamp")),
            container_id=container.get("id") or None,
            container_name=container.get("name") or None,
            process=header.get("image") or None,
            command_line=" ".join(str(arg) for arg in argv) if isinstance(argv, list) else None,
            raw=event,
        )

    def _parse_plaintext(self, line: str, emitted_at: float) -> Alert | None:
        match = PLAINTEXT_THREAT.match(line.strip())
        if match is None:
            return None
        description = match["description"]
        legacy = LEGACY_RULE_NAME.search(description)
        rule = legacy["name"] if legacy else description
        process = match["process"].split()[-1] if match["process"].split() else None
        return Alert(
            tool=self.name,
            rule=rule,
            emitted_at=emitted_at,
            event_at=self.parse_time(match["time"]),
            process=process,
            raw={"format": "plaintext", "line": line.strip(), **match.groupdict()},
        )
