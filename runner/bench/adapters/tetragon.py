from __future__ import annotations

from pathlib import Path
from typing import Any

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.model import Alert

IMAGE = "quay.io/cilium/tetragon"
VERSION = "1.7.1"
CONFIG_MOUNT = "/etc/tetragon/bench"
CONF_DIR = "tetragon.conf.d"
OUTPUT_MOUNT = "/bench-output"
READY_PATTERN = r"Listening for events\.\.\."
POLICY_EVENTS = ("process_kprobe", "process_tracepoint", "process_lsm", "process_uprobe", "process_usdt")
CONTAINER_ID_SCHEMES = ("docker://", "containerd://", "cri-o://")
ENFORCEMENT_ACTIONS = frozenset({"KPROBE_ACTION_SIGKILL", "KPROBE_ACTION_OVERRIDE"})


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _strip_scheme(value: str | None) -> str | None:
    if value is None:
        return None
    for scheme in CONTAINER_ID_SCHEMES:
        if value.startswith(scheme):
            return value[len(scheme):] or None
    return value


class Adapter(ToolAdapter):
    name = "tetragon"
    version = VERSION
    profiles = ("default", "tuned", "enforce")

    @staticmethod
    def export_file(profile: str) -> str:
        return f"tetragon-{profile}-events.json"

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        config_dir = self.config_dir(Path(host_repo_root), profile)
        export_file = self.export_file(profile)
        return ContainerSpec(
            image=f"{IMAGE}:v{VERSION}",
            command=[
                f"--config-dir={CONFIG_MOUNT}/{CONF_DIR}",
                f"--export-filename={OUTPUT_MOUNT}/{export_file}",
            ],
            mounts=[
                Mount(source=str(config_dir), target=CONFIG_MOUNT),
                Mount(source=str(Path(host_output_dir)), target=OUTPUT_MOUNT, read_only=False),
                Mount(source="/sys/kernel/btf/vmlinux", target="/var/lib/tetragon/btf"),
                Mount(source="/sys/fs/bpf", target="/sys/fs/bpf", read_only=False),
                Mount(source="/proc", target="/procRoot"),
            ],
            ready_pattern=READY_PATTERN,
            startup_timeout=180.0,
            alerts_file=export_file,
        )

    @staticmethod
    def enforcement_action(event: dict[str, Any]) -> str | None:
        for key in POLICY_EVENTS:
            body = event.get(key)
            if isinstance(body, dict) and body.get("action") in ENFORCEMENT_ACTIONS:
                return str(body["action"])
        return None

    def is_enforcement(self, alert: Alert) -> bool:
        return self.enforcement_action(alert.raw) is not None

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        event = self.load_json(line)
        if event is None:
            return None
        kind = next((key for key in POLICY_EVENTS if isinstance(event.get(key), dict)), None)
        if kind is None:
            return None
        body = event[kind]
        rule = _text(body.get("policy_name")) or _text(body.get("function_name"))
        if rule is None and kind == "process_tracepoint":
            subsys, name = _text(body.get("subsys")), _text(body.get("event"))
            rule = f"{subsys}/{name}" if subsys and name else None
        if rule is None:
            return None
        process = body.get("process") if isinstance(body.get("process"), dict) else {}
        pod = process.get("pod") if isinstance(process.get("pod"), dict) else {}
        container = pod.get("container") if isinstance(pod.get("container"), dict) else {}
        binary = _text(process.get("binary"))
        arguments = _text(process.get("arguments"))
        command_line = " ".join(part for part in (binary, arguments) if part) or None
        return Alert(
            tool=self.name,
            rule=rule,
            emitted_at=emitted_at,
            severity=None,
            event_at=self.parse_time(event.get("time")),
            container_id=_strip_scheme(_text(container.get("id"))) or _text(process.get("docker")),
            container_name=_text(container.get("name")),
            process=binary,
            command_line=command_line,
            raw=event,
            action=self.enforcement_action(event),
        )
