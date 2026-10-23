from __future__ import annotations

from pathlib import Path
from typing import Any

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.model import Alert

ALERT_TYPES = frozenset({"MatchedPolicy", "MatchedHostPolicy", "MatchedNetworkPolicy"})
ALERTS_FILE = "kubearmor-alerts.jsonl"
LOG_DIR = "/var/log/kubearmor"
PROFILE_DIR = "/opt/kubearmor/profile"
POLICY_DIR = "/opt/kubearmor/policies"
ENFORCER_STATES = (
    ("Initialized BPF-LSM Enforcer", True),
    ("Initialized AppArmor Enforcer", False),
    ("Initialized SELinux Enforcer", False),
    ("Disabled KubeArmor Enforcer", False),
)
BLOCK_ACTION = "Block"


def _field(event: dict[str, Any], name: str) -> Any:
    for key in (name, name[:1].upper() + name[1:]):
        value = event.get(key)
        if value not in (None, ""):
            return value
    return None


class Adapter(ToolAdapter):
    name = "kubearmor"
    version = "1.7.5"
    image = "kubearmor/kubearmor:v1.7.5"
    profiles = ("default", "tuned", "enforce", "community")

    @staticmethod
    def is_blocked(raw: dict[str, Any]) -> bool:
        action = str(_field(raw, "action") or "")
        result = str(_field(raw, "result") or "")
        return BLOCK_ACTION in action and result not in ("", "Passed")

    def is_enforcement(self, alert: Alert) -> bool:
        return self.is_blocked(alert.raw)

    def enforcement_check(self, log_lines: list[str]) -> bool | None:
        state = None
        for line in log_lines:
            for message, verified in ENFORCER_STATES:
                if message in line:
                    state = verified
        return state

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        profile_dir = self.config_dir(host_repo_root, profile)
        return ContainerSpec(
            image=self.image,
            command=[f"-logPath={LOG_DIR}/{ALERTS_FILE}"],
            privileged=True,
            pid_mode="host",
            network_mode="host",
            cgroupns_mode="host",
            mounts=[
                Mount(str(profile_dir), PROFILE_DIR, True),
                Mount(str(profile_dir / "policies"), POLICY_DIR, True),
                Mount(str(host_output_dir), LOG_DIR, False),
                Mount("/var/run/docker.sock", "/var/run/docker.sock", True),
                Mount("/sys/fs/bpf", "/sys/fs/bpf", False),
                Mount("/sys/kernel/security", "/sys/kernel/security", False),
                Mount("/sys/kernel/debug", "/sys/kernel/debug", False),
            ],
            environment={"KUBEARMOR_CFG": f"{PROFILE_DIR}/kubearmor.yaml"},
            ready_pattern=r"Initialized KubeArmor(?![ \w])",
            startup_timeout=180.0,
            alerts_file=ALERTS_FILE,
        )

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        event = self.load_json(line)
        if event is None or _field(event, "type") not in ALERT_TYPES:
            return None
        operation = _field(event, "operation")
        command_line = _field(event, "resource") if operation == "Process" else _field(event, "source")
        severity = _field(event, "severity")
        return Alert(
            tool=self.name,
            rule=str(_field(event, "policyName") or "unknown"),
            emitted_at=emitted_at,
            severity=str(severity) if severity is not None else None,
            event_at=self.parse_time(_field(event, "updatedTime")) or self.parse_time(_field(event, "timestamp")),
            container_id=_field(event, "containerID"),
            container_name=_field(event, "containerName"),
            process=_field(event, "processName"),
            command_line=command_line,
            raw=event,
            action=BLOCK_ACTION if self.is_blocked(event) else None,
        )
