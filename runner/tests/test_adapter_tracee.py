from __future__ import annotations

import re
from pathlib import Path

import pytest

from bench.adapters.tracee import Adapter

FIXTURE = Path(__file__).parent / "fixtures" / "tracee" / "alerts.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[2]
needs_tools = pytest.mark.skipif(not (REPO_ROOT / "tools" / "tracee").is_dir(), reason="tools directory not available")


@pytest.fixture(scope="module")
def lines() -> list[str]:
    return FIXTURE.read_text().splitlines()


@pytest.fixture(scope="module")
def adapter() -> Adapter:
    return Adapter()


def test_identity(adapter: Adapter) -> None:
    assert adapter.profiles == ("default", "tuned")
    assert adapter.name == "tracee"
    assert adapter.image.endswith(":" + adapter.version)


def test_raw_events_are_not_alerts(adapter: Adapter, lines: list[str]) -> None:
    for index in (0, 1, 6, 7, 8):
        assert adapter.parse(lines[index], 1.0) is None


def test_legacy_signature_finding(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[2], 42.0)
    assert alert is not None
    assert alert.tool == "tracee"
    assert alert.rule == "Fileless execution detected"
    assert alert.severity == "high"
    assert alert.emitted_at == 42.0
    assert alert.event_at == pytest.approx(1680182976.364916505)
    assert alert.container_id.startswith("c0ffee")
    assert alert.container_name == "bench-victim"
    assert alert.process == "sshd"
    assert alert.command_line == "sshd -D"
    assert alert.raw["metadata"]["Properties"]["signatureID"] == "TRC-105"


def test_legacy_detection_policy_match(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[3], 1.0)
    assert alert is not None
    assert alert.rule == "detect-shadow-read"
    assert alert.severity is None
    assert alert.process == "cat"
    assert alert.command_line == "/usr/bin/cat"
    assert alert.container_name == "bench-victim"


def test_v1beta1_threat(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[4], 1.0)
    assert alert is not None
    assert alert.rule == "File Modification Test"
    assert alert.severity == "medium"
    assert alert.event_at is not None
    assert alert.container_name == "bench-victim"
    assert alert.process == "bash"
    assert alert.command_line == "/usr/bin/bash"


def test_v1beta1_derived_detector(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[5], 1.0)
    assert alert is not None
    assert alert.rule == "netcat_privileged_alert"


def test_container_spec(adapter: Adapter) -> None:
    for profile in adapter.profiles:
        spec = adapter.container_spec(Path("/host/repo"), profile, Path("/host/out"))
        assert spec.image == "aquasec/tracee:0.24.1"
        assert spec.privileged and spec.pid_mode == "host" and spec.cgroupns_mode == "host"
        sources = {mount.target: mount for mount in spec.mounts}
        assert sources["/tracee/profile"].source == f"/host/repo/tools/tracee/{profile}"
        assert sources["/tracee/profile"].read_only
        assert sources["/var/run/docker.sock"].source == "/var/run/docker.sock"
        assert sources["/etc/os-release-host"].source == "/etc/os-release"
        assert "/tracee/profile/config.yaml" in spec.command
        assert "/tracee/profile/policies" in spec.command
        assert spec.alerts_file is None
        assert re.search(spec.ready_pattern, '{"eventName":"tracee_info","args":[]}')
        assert re.search(spec.ready_pattern, '{"name": "tracee_info"}')
        assert not re.search(spec.ready_pattern, '{"eventName":"container_create"}')
        assert spec.ready_url is None
        assert spec.network_mode == "host"


@needs_tools
@pytest.mark.parametrize("profile", ["default", "tuned"])
def test_healthz_is_enabled(profile: str) -> None:
    config = (REPO_ROOT / "tools" / "tracee" / profile / "config.yaml").read_text()
    assert "healthz: true" in config
    assert "listen-addr: :3366" in config


@needs_tools
@pytest.mark.parametrize("profile", ["default", "tuned"])
def test_profile_files_exist(profile: str) -> None:
    profile_dir = REPO_ROOT / "tools" / "tracee" / profile
    assert (profile_dir / "config.yaml").is_file()
    policies = sorted((profile_dir / "policies").glob("*.yaml"))
    assert any(path.name == "default-policy.yaml" for path in policies)
    assert any("tracee_info" in path.read_text() for path in policies)
    assert len(policies) <= 64


@needs_tools
def test_tuned_detection_policies_use_prefix() -> None:
    policies = sorted((REPO_ROOT / "tools" / "tracee" / "tuned" / "policies").glob("detect-*.yaml"))
    assert len(policies) >= 15
    for path in policies:
        names = re.findall(r"^  name: (\S+)$", path.read_text(), re.MULTILINE)
        assert names and all(name.startswith("detect-") for name in names)
