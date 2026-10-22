from __future__ import annotations

from pathlib import Path
from typing import Any

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.model import Alert

PROFILE_DIR = "/tracee/profile"
DETECTION_POLICY_PREFIX = "detect-"
SEVERITY_NAMES = {0: "info", 1: "low", 2: "medium", 3: "high", 4: "critical"}


def _severity(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        number = int(value)
        return SEVERITY_NAMES.get(number, str(number))
    return str(value).lower()


def _detection_policy(policies: Any) -> str | None:
    if not isinstance(policies, list):
        return None
    for policy in policies:
        if isinstance(policy, str) and policy.startswith(DETECTION_POLICY_PREFIX):
            return policy
    return None


def _legacy_argv(args: Any) -> str | None:
    if not isinstance(args, list):
        return None
    for arg in args:
        if not isinstance(arg, dict):
            continue
        if arg.get("name") == "argv" and isinstance(arg.get("value"), list):
            return " ".join(str(part) for part in arg["value"])
        if arg.get("name") == "detectedFrom" and isinstance(arg.get("value"), dict):
            nested = _legacy_argv(arg["value"].get("args"))
            if nested:
                return nested
    return None


def _v1_argv(data: Any) -> str | None:
    if not isinstance(data, list):
        return None
    for item in data:
        if isinstance(item, dict) and item.get("name") == "argv":
            values = (item.get("str_array") or {}).get("value")
            if isinstance(values, list):
                return " ".join(str(part) for part in values)
    return None


class Adapter(ToolAdapter):
    name = "tracee"
    version = "0.24.1"
    image = "aquasec/tracee:0.24.1"

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        profile_dir = self.config_dir(host_repo_root, profile)
        return ContainerSpec(
            image=self.image,
            entrypoint=["/tracee/tracee"],
            command=[
                "--config",
                f"{PROFILE_DIR}/config.yaml",
                "--policy",
                f"{PROFILE_DIR}/policies",
            ],
            privileged=True,
            pid_mode="host",
            network_mode="host",
            cgroupns_mode="host",
            mounts=[
                Mount(str(profile_dir), PROFILE_DIR, True),
                Mount("/etc/os-release", "/etc/os-release-host", True),
                Mount("/var/run/docker.sock", "/var/run/docker.sock", True),
                Mount(str(host_output_dir), "/tmp/tracee", False),
            ],
            environment={"LIBBPFGO_OSRELEASE_FILE": "/etc/os-release-host"},
            ready_pattern=r'"(eventName|name)":\s*"tracee_info"',
            startup_timeout=300.0,
        )

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        event = self.load_json(line)
        if event is None:
            return None
        if "eventName" in event:
            return self._parse_legacy(event, emitted_at)
        if "name" in event and ("workload" in event or "threat" in event or "detected_from" in event):
            return self._parse_v1beta1(event, emitted_at)
        return None

    def _parse_legacy(self, event: dict[str, Any], emitted_at: float) -> Alert | None:
        metadata = event.get("metadata")
        properties = metadata.get("Properties") if isinstance(metadata, dict) else None
        if isinstance(properties, dict):
            rule = properties.get("signatureName") or event.get("eventName")
            severity = _severity(properties.get("Severity"))
        else:
            rule = _detection_policy(event.get("matchedPolicies"))
            if rule is None:
                return None
            severity = None
        container = event.get("container") if isinstance(event.get("container"), dict) else {}
        executable = event.get("executable") if isinstance(event.get("executable"), dict) else {}
        return Alert(
            tool=self.name,
            rule=str(rule),
            emitted_at=emitted_at,
            severity=severity,
            event_at=self.parse_time(event.get("timestamp")),
            container_id=container.get("id") or event.get("containerId") or None,
            container_name=container.get("name") or None,
            process=event.get("processName") or None,
            command_line=_legacy_argv(event.get("args")) or executable.get("path") or None,
            raw=event,
        )

    def _parse_v1beta1(self, event: dict[str, Any], emitted_at: float) -> Alert | None:
        threat = event.get("threat") if isinstance(event.get("threat"), dict) else None
        policies = (event.get("policies") or {}).get("matched") if isinstance(event.get("policies"), dict) else None
        if threat:
            rule = threat.get("name") or event.get("name")
            severity = _severity(threat.get("severity"))
        elif isinstance(event.get("detected_from"), dict):
            rule = event.get("name")
            severity = None
        else:
            rule = _detection_policy(policies)
            if rule is None:
                return None
            severity = None
        workload = event.get("workload") if isinstance(event.get("workload"), dict) else {}
        container = workload.get("container") if isinstance(workload.get("container"), dict) else {}
        process = workload.get("process") if isinstance(workload.get("process"), dict) else {}
        thread = process.get("thread") if isinstance(process.get("thread"), dict) else {}
        executable = process.get("executable") if isinstance(process.get("executable"), dict) else {}
        detected_from = event.get("detected_from") if isinstance(event.get("detected_from"), dict) else {}
        return Alert(
            tool=self.name,
            rule=str(rule),
            emitted_at=emitted_at,
            severity=severity,
            event_at=self.parse_time(event.get("timestamp")),
            container_id=container.get("id") or None,
            container_name=container.get("name") or None,
            process=thread.get("name") or None,
            command_line=_v1_argv(event.get("data")) or _v1_argv(detected_from.get("data")) or executable.get("path") or None,
            raw=event,
        )
