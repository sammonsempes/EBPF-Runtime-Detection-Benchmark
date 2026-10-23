from __future__ import annotations

import re
from pathlib import Path

import pytest

from bench.adapters import get_adapter
from bench.adapters.falco import Adapter

FIXTURE = Path(__file__).parent / "fixtures" / "falco" / "alerts.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[2]
needs_tools = pytest.mark.skipif(not (REPO_ROOT / "tools" / "falco").is_dir(), reason="tools directory not available")


@pytest.fixture(scope="module")
def lines() -> list[str]:
    return FIXTURE.read_text().splitlines()


@pytest.fixture(scope="module")
def adapter() -> Adapter:
    return Adapter()


def spec_for(adapter: Adapter, profile: str):
    return adapter.container_spec(Path("/host/repo"), profile, Path("/host/out"))


def test_identity(adapter: Adapter) -> None:
    assert adapter.name == "falco"
    assert adapter.profiles == ("default", "tuned", "community")
    assert re.fullmatch(r"\d+\.\d+\.\d+", adapter.version)
    assert isinstance(get_adapter("falco"), Adapter)


def test_log_lines_are_not_alerts(adapter: Adapter, lines: list[str]) -> None:
    for index in range(6):
        assert adapter.parse(lines[index], 1.0) is None


def test_internal_drop_message_is_not_an_alert(adapter: Adapter, lines: list[str]) -> None:
    assert adapter.parse(lines[10], 1.0) is None


def test_garbage_is_not_an_alert(adapter: Adapter) -> None:
    for line in ("", "{", "[]", "{\"output\": \"no rule\"}", "not json at all"):
        assert adapter.parse(line, 1.0) is None


def test_container_alert(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[6], 42.5)
    assert alert is not None
    assert alert.tool == "falco"
    assert alert.rule == "Fileless execution via memfd_create"
    assert alert.severity == "critical"
    assert alert.emitted_at == 42.5
    assert alert.event_at == pytest.approx(1792656971.123456)
    assert alert.container_id == "3ad7b26ded6d"
    assert alert.container_name == "bench-victim"
    assert alert.process == "3"
    assert alert.command_line == "3"
    assert alert.raw["output_fields"]["evt.arg.flags"] == "EXE_WRITABLE|EXE_FROM_MEMFD"
    assert "T1620" in alert.raw["tags"]


def test_stable_rule_alert(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[7], 1.0)
    assert alert is not None
    assert alert.rule == "Clear Log Activities"
    assert alert.severity == "warning"
    assert alert.process == "sh"
    assert alert.command_line == "sh -c : > /var/log/auth.log"
    assert alert.raw["output_fields"]["fd.name"] == "/var/log/auth.log"


def test_host_alert_has_no_container(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[8], 1.0)
    assert alert is not None
    assert alert.rule == "Read sensitive file untrusted"
    assert alert.container_id is None
    assert alert.container_name is None
    assert alert.process == "cat"


def test_tuned_rule_alert(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[9], 1.0)
    assert alert is not None
    assert alert.rule == "Outbound Connection From Shell Process"
    assert alert.severity == "critical"
    assert alert.process == "bash"
    assert alert.command_line == "bash -i"
    assert alert.container_name == "bench-victim"


def test_alert_count(adapter: Adapter, lines: list[str]) -> None:
    alerts = [alert for alert in (adapter.parse(line, 1.0) for line in lines) if alert is not None]
    assert len(alerts) == 4


@pytest.mark.parametrize("profile", ["default", "tuned", "community"])
def test_container_spec(adapter: Adapter, profile: str) -> None:
    spec = spec_for(adapter, profile)
    assert spec.image == f"docker.io/falcosecurity/falco:{adapter.version}"
    assert spec.privileged is True
    assert spec.pid_mode == "host"
    assert spec.alerts_file is None
    mounts = {mount.target: mount for mount in spec.mounts}
    config = mounts["/etc/falco/bench"]
    assert config.source == f"/host/repo/tools/falco/{profile}"
    assert config.read_only is True
    drop_in = mounts["/etc/falco/config.d/zz-bench.yaml"]
    assert drop_in.source == f"/host/repo/tools/falco/{profile}/falco.bench.yaml"
    assert mounts["/host/var/run/docker.sock"].source == "/var/run/docker.sock"
    assert mounts["/host/proc"].source == "/proc"
    assert mounts["/host/etc"].source == "/etc"


def test_ready_pattern(adapter: Adapter, lines: list[str]) -> None:
    pattern = re.compile(spec_for(adapter, "default").ready_pattern)
    matching = [line for line in lines if pattern.search(line)]
    assert matching == ["2026-10-22T08:15:02+0000: Opening 'syscall' source with modern BPF probe."]


@needs_tools
@pytest.mark.parametrize("profile", ["default", "tuned", "community"])
def test_profile_files_exist(profile: str) -> None:
    profile_dir = REPO_ROOT / "tools" / "falco" / profile
    drop_in = (profile_dir / "falco.bench.yaml").read_text()
    assert "json_output: true" in drop_in
    assert "kind: modern_ebpf" in drop_in


@needs_tools
def test_tuned_profile_loads_custom_rules() -> None:
    tuned = REPO_ROOT / "tools" / "falco" / "tuned"
    assert "/etc/falco/bench/rules.d" in (tuned / "falco.bench.yaml").read_text()
    rules = (tuned / "rules.d" / "custom_rules.yaml").read_text()
    assert rules.count("- rule: ") >= 20
    assert "BENCH_MARKER" not in rules
    assert "bench-" not in rules
    assert "attacker" not in rules


@needs_tools
def test_community_sources_are_pinned() -> None:
    community = REPO_ROOT / "tools" / "falco" / "community"
    entries = [line.split() for line in (community / "sources.txt").read_text().splitlines() if line.strip()]
    assert len(entries) == 2
    for checksum, url, dest in entries:
        assert re.fullmatch(r"[0-9a-f]{64}", checksum)
        assert re.fullmatch(r"https://raw\.githubusercontent\.com/falcosecurity/rules/[0-9a-f]{40}/rules/[\w.-]+\.yaml", url)
        assert url.rsplit("/", 1)[1] == Path(dest).name
        assert dest.startswith("rules.d/")
        assert (community / dest).is_file()


@needs_tools
def test_community_profile_loads_upstream_rules_only() -> None:
    community = REPO_ROOT / "tools" / "falco" / "community"
    assert "/etc/falco/bench/rules.d" in (community / "falco.bench.yaml").read_text()
    files = sorted(path.name for path in (community / "rules.d").iterdir())
    assert files == ["falco-incubating_rules.yaml", "falco-sandbox_rules.yaml"]
    expected = (
        ("falco-incubating_rules.yaml", "maturity_incubating", 31),
        ("falco-sandbox_rules.yaml", "maturity_sandbox", 39),
    )
    for name, maturity, count in expected:
        rules = (community / "rules.d" / name).read_text()
        assert rules.count("- rule: ") == count
        assert rules.count(f"tags: [{maturity},") == count
        assert "required_plugin_versions" in rules
