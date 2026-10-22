from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from bench.adapters.kubearmor import Adapter

FIXTURE = Path(__file__).parent / "fixtures" / "kubearmor" / "alerts.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[2]
needs_tools = pytest.mark.skipif(not (REPO_ROOT / "tools" / "kubearmor").is_dir(), reason="tools directory not available")


@pytest.fixture(scope="module")
def lines() -> list[str]:
    return FIXTURE.read_text().splitlines()


@pytest.fixture(scope="module")
def adapter() -> Adapter:
    return Adapter()


def test_identity(adapter: Adapter) -> None:
    assert adapter.name == "kubearmor"
    assert adapter.image.endswith(":v" + adapter.version)


def test_process_alert(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[0], 10.0)
    assert alert is not None
    assert alert.tool == "kubearmor"
    assert alert.rule == "harden-wordpress-pkg-mngr-exec"
    assert alert.severity == "5"
    assert alert.emitted_at == 10.0
    assert alert.container_id.startswith("72de193f")
    assert alert.container_name == "wordpress"
    assert alert.process == "/usr/bin/apt"
    assert alert.command_line == "/usr/bin/apt"
    assert alert.raw["Action"] == "Block"


def test_file_alert_uses_source_as_command_line(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[1], 1.0)
    assert alert is not None
    assert alert.rule == "harden-wordpress-file-integrity-monitoring"
    assert alert.process == "/bin/rm"
    assert alert.command_line == "/bin/rm /sbin/raw"


def test_audit_network_alert(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[2], 1.0)
    assert alert is not None
    assert alert.rule == "ksp-vault-network"
    assert alert.raw["Action"] == "Audit"
    assert alert.command_line == "/bin/vault status -tls-skip-verify"


def test_host_alert_and_event_time(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[3], 1.0)
    assert alert is not None
    assert alert.rule == "sleep-deny"
    assert alert.container_id is None
    assert alert.command_line == "/usr/bin/sleep 10"
    assert alert.event_at == pytest.approx(1692813948.301798)


def test_recent_alert_fields(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[4], 1.0)
    assert alert is not None
    assert alert.command_line == "/usr/bin/python3.6 -m pydoc"
    assert alert.event_at == pytest.approx(1765863439.127331)


def test_log_path_camel_case_alert(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[7], 1.0)
    assert alert is not None
    assert alert.rule == "ksp-ubuntu-1-allow-proc-args"
    assert alert.container_name == "ubuntu-1-container"
    assert alert.container_id.startswith("4771ac3e")
    assert alert.process == "/usr/bin/python3.6"
    assert alert.command_line == "/usr/bin/python3.6 -m pydoc"
    assert alert.severity == "5"
    assert alert.event_at == pytest.approx(1765863439.127331)


def test_telemetry_and_noise_are_not_alerts(adapter: Adapter, lines: list[str]) -> None:
    for index in (5, 6, 8, 9, 10):
        assert adapter.parse(lines[index], 1.0) is None


def test_container_spec(adapter: Adapter) -> None:
    for profile in adapter.profiles:
        spec = adapter.container_spec(Path("/host/repo"), profile, Path("/host/out"))
        assert spec.image == "kubearmor/kubearmor:v1.7.5"
        assert spec.privileged and spec.pid_mode == "host" and spec.network_mode == "host"
        mounts = {mount.target: mount for mount in spec.mounts}
        assert mounts["/opt/kubearmor/profile"].source == f"/host/repo/tools/kubearmor/{profile}"
        assert mounts["/opt/kubearmor/policies"].source == f"/host/repo/tools/kubearmor/{profile}/policies"
        assert mounts["/var/log/kubearmor"].source == "/host/out"
        assert not mounts["/var/log/kubearmor"].read_only
        assert mounts["/var/run/docker.sock"].source == "/var/run/docker.sock"
        assert spec.environment["KUBEARMOR_CFG"] == "/opt/kubearmor/profile/kubearmor.yaml"
        assert spec.alerts_file == "kubearmor-alerts.jsonl"
        assert f"-logPath=/var/log/kubearmor/{spec.alerts_file}" in spec.command
        assert re.search(spec.ready_pattern, "2026-10-22 21:05:00.000000\tINFO\tInitialized KubeArmor")
        assert not re.search(spec.ready_pattern, "INFO\tInitialized KubeArmor Logger")
        assert not re.search(spec.ready_pattern, "INFO\tInitialized KubeArmor Enforcer")


def test_profiles(adapter: Adapter) -> None:
    assert adapter.profiles == ("default", "tuned", "enforce")


def test_block_identification(adapter: Adapter, lines: list[str]) -> None:
    blocked = adapter.parse(lines[0], 1.0)
    audited = adapter.parse(lines[2], 1.0)
    camel = adapter.parse(lines[7], 1.0)
    assert blocked.raw["Action"] == "Block" and blocked.raw["Result"] == "Permission denied"
    assert Adapter.is_blocked(blocked.raw)
    assert not Adapter.is_blocked(audited.raw)
    assert camel.raw["action"] == "Block" and Adapter.is_blocked(camel.raw)
    assert not Adapter.is_blocked({"type": "MatchedPolicy", "action": "Block", "result": "Passed"})


def test_enforcement_hooks(adapter: Adapter, lines: list[str]) -> None:
    blocked = adapter.parse(lines[0], 1.0)
    audited = adapter.parse(lines[2], 1.0)
    passed = adapter.parse(
        json.dumps({"type": "MatchedPolicy", "policyName": "p", "action": "Block", "result": "Passed"}), 1.0
    )
    assert blocked.action == "Block" and adapter.is_enforcement(blocked)
    assert audited.action is None and not adapter.is_enforcement(audited)
    assert passed.action is None and not adapter.is_enforcement(passed)


@pytest.mark.parametrize(
    "logs, expected",
    [
        (["2026-10-22 21:05:00.000000\tINFO\tInitialized BPF-LSM Enforcer"], True),
        (["INFO\tInitialized AppArmor Enforcer"], False),
        (["INFO\tDisabled KubeArmor Enforcer since No LSM is enabled"], False),
        (["INFO\tInitialized KubeArmor"], None),
        ([], None),
        (["INFO\tInitialized AppArmor Enforcer", "INFO\tInitialized BPF-LSM Enforcer"], True),
    ],
)
def test_enforcement_check(adapter: Adapter, logs: list[str], expected: bool | None) -> None:
    assert adapter.enforcement_check(logs) is expected


@needs_tools
def test_enforce_profile_mirrors_tuned() -> None:
    root = REPO_ROOT / "tools" / "kubearmor"
    tuned = {path.name for path in (root / "tuned" / "policies").glob("*.json")}
    enforce = {path.name for path in (root / "enforce" / "policies").glob("*.json")}
    assert tuned == enforce
    config = (root / "enforce" / "kubearmor.yaml").read_text()
    assert 'lsm: "bpf"' in config
    assert "enableKubeArmorHostPolicy: false" in config


@needs_tools
@pytest.mark.parametrize("profile", ["default", "tuned", "enforce"])
def test_policies_are_restorable(profile: str) -> None:
    expected_action = "Block" if profile == "enforce" else "Audit"
    profile_dir = REPO_ROOT / "tools" / "kubearmor" / profile
    assert (profile_dir / "kubearmor.yaml").is_file()
    policies = sorted((profile_dir / "policies").glob("*.json"))
    assert policies
    names = set()
    for path in policies:
        policy = json.loads(path.read_text())
        assert policy["kind"] == "KubeArmorPolicy"
        assert "namespaceName" in policy["metadata"]
        assert policy["metadata"]["policyName"] == path.stem
        names.add(path.stem)
        spec = policy["spec"]
        assert spec["action"] == expected_action
        assert spec["selector"]["matchLabels"] == {"kubearmor.io/container.name": "bench-victim"}
        for section in ("process", "file", "network"):
            for rules in spec.get(section, {}).values():
                for rule in rules:
                    assert rule.get("action", expected_action) == expected_action
        for preset in spec.get("presets", []):
            assert preset["action"] == expected_action
    assert len(names) == len(policies)
