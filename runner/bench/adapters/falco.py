from __future__ import annotations

from pathlib import Path
from typing import Any

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.model import Alert

IMAGE = "docker.io/falcosecurity/falco"
VERSION = "0.45.0"
CONFIG_MOUNT = "/etc/falco/bench"
DROP_IN_FILE = "falco.bench.yaml"
DROP_IN_MOUNT = "/etc/falco/config.d/zz-bench.yaml"
READY_PATTERN = r"Opening 'syscall' source with modern BPF probe"
MISSING_VALUES = {"", "<NA>", "N/A"}
HOST_CONTAINER = "host"


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text in MISSING_VALUES else text


def _container(value: Any) -> str | None:
    text = _text(value)
    return None if text == HOST_CONTAINER else text


class Adapter(ToolAdapter):
    name = "falco"
    version = VERSION
    profiles = ("default", "tuned", "community")

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        config_dir = self.config_dir(Path(host_repo_root), profile)
        return ContainerSpec(
            image=f"{IMAGE}:{VERSION}",
            command=["/usr/bin/falco"],
            mounts=[
                Mount(source=str(config_dir), target=CONFIG_MOUNT),
                Mount(source=str(config_dir / DROP_IN_FILE), target=DROP_IN_MOUNT),
                Mount(source="/var/run/docker.sock", target="/host/var/run/docker.sock", read_only=False),
                Mount(source="/proc", target="/host/proc"),
                Mount(source="/etc", target="/host/etc"),
            ],
            environment={"HOST_ROOT": "/host"},
            ready_pattern=READY_PATTERN,
        )

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        event = self.load_json(line)
        if event is None:
            return None
        rule = event.get("rule")
        if not isinstance(rule, str) or not rule or "priority" not in event:
            return None
        if event.get("source") == "internal" or rule.startswith("Falco internal"):
            return None
        fields = event.get("output_fields")
        if not isinstance(fields, dict):
            fields = {}
        priority = _text(event.get("priority"))
        return Alert(
            tool=self.name,
            rule=rule,
            emitted_at=emitted_at,
            severity=priority.lower() if priority else None,
            event_at=self.parse_time(event.get("time")),
            container_id=_container(fields.get("container.id")),
            container_name=_container(fields.get("container.name")),
            process=_text(fields.get("proc.name")) or _text(fields.get("proc.exepath")),
            command_line=_text(fields.get("proc.cmdline")),
            raw=event,
        )
