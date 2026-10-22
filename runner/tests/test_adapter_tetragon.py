from __future__ import annotations

import re
from pathlib import Path

import pytest

from bench.adapters import get_adapter
from bench.adapters.tetragon import Adapter

FIXTURE = Path(__file__).parent / "fixtures" / "tetragon" / "alerts.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[2]
needs_tools = pytest.mark.skipif(not (REPO_ROOT / "tools" / "tetragon").is_dir(), reason="tools directory not available")
DEFAULT_POLICIES = {"file_monitoring.yaml", "modules.yaml", "bpf.yaml", "privileges-raise.yaml"}


@pytest.fixture(scope="module")
def lines() -> list[str]:
    return FIXTURE.read_text().splitlines()


@pytest.fixture(scope="module")
def adapter() -> Adapter:
    return Adapter()


def spec_for(adapter: Adapter, profile: str):
    return adapter.container_spec(Path("/host/repo"), profile, Path("/host/out/run-1"))


def test_identity(adapter: Adapter) -> None:
    assert adapter.name == "tetragon"
    assert re.fullmatch(r"\d+\.\d+\.\d+", adapter.version)
    assert isinstance(get_adapter("tetragon"), Adapter)


def test_policy_kprobe_in_pod(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[0], 12.0)
    assert alert is not None
    assert alert.tool == "tetragon"
    assert alert.rule == "file-monitoring"
    assert alert.severity is None
    assert alert.emitted_at == 12.0
    assert alert.event_at == pytest.approx(1713061094.376304)
    assert alert.container_id == "6b742e38ee3a212239e6d48b2954435a407af44b9a354bdf540db22f460ab40e"
    assert alert.container_name == "file-access"
    assert alert.process == "/bin/vi"
    assert alert.command_line == "/bin/vi /etc/passwd"
    assert alert.raw["process_kprobe"]["args"][0]["file_arg"]["path"] == "/etc/passwd"


def test_kprobe_without_policy_name_falls_back_to_function(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[1], 1.0)
    assert alert is not None
    assert alert.rule == "security_kernel_module_request"
    assert alert.container_id == "1e910d5cc8d8d68c894934170b162ef93aea5652867ed6bd7c620c7e3f9a10f1"
    assert alert.process == "/bin/mount"
    assert alert.command_line == "/bin/mount -o loop -t xfs loop.xfs /mnt/xfs.volume/"


def test_host_kprobe_has_no_container(adapter: Adapter, lines: list[str]) -> None:
    alert = adapter.parse(lines[2], 1.0)
    assert alert is not None
    assert alert.rule == "security_kernel_read_file"
    assert alert.container_id is None
    assert alert.container_name is None
    assert alert.process == "/usr/sbin/insmod"


def test_docker_field_is_used_without_pod(adapter: Adapter, lines: list[str]) -> None:
    line = lines[0].replace('"pod":{"namespace":"default","name":"file-access","container":', '"pod_removed":{"namespace":"default","name":"file-access","container":', 1)
    alert = adapter.parse(line, 1.0)
    assert alert is not None
    assert alert.container_id == "6b742e38ee3a212239e6d48b2954435"
    assert alert.container_name is None


def test_tracepoint_event_is_an_alert(adapter: Adapter, lines: list[str]) -> None:
    line = lines[2].replace('"process_kprobe"', '"process_tracepoint"', 1)
    line = line.replace('"function_name":"security_kernel_read_file"', '"subsys":"raw_syscalls","event":"sys_exit"', 1)
    alert = adapter.parse(line, 1.0)
    assert alert is not None
    assert alert.rule == "raw_syscalls/sys_exit"


def test_profiles(adapter: Adapter) -> None:
    assert adapter.profiles == ("default", "tuned", "enforce")


@pytest.mark.parametrize("action", ["KPROBE_ACTION_SIGKILL", "KPROBE_ACTION_OVERRIDE"])
def test_enforcement_event_is_an_alert_with_upstream_action(adapter: Adapter, lines: list[str], action: str) -> None:
    line = lines[0].replace('"action":"KPROBE_ACTION_POST","policy_name"', f'"action":"{action}","policy_name"', 1)
    alert = adapter.parse(line, 1.0)
    assert alert is not None
    assert alert.rule == "file-monitoring"
    assert alert.raw["process_kprobe"]["action"] == action


@pytest.mark.parametrize("action", ["KPROBE_ACTION_SIGKILL", "KPROBE_ACTION_OVERRIDE"])
def test_enforcement_hooks(adapter: Adapter, lines: list[str], action: str) -> None:
    line = lines[0].replace('"action":"KPROBE_ACTION_POST","policy_name"', f'"action":"{action}","policy_name"', 1)
    alert = adapter.parse(line, 1.0)
    assert alert.action == action and adapter.is_enforcement(alert)
    plain = adapter.parse(lines[0], 1.0)
    assert plain.action is None and not adapter.is_enforcement(plain)
    lsm = adapter.parse(line.replace('"process_kprobe"', '"process_lsm"', 1), 1.0)
    assert lsm is not None and lsm.action == action
    assert adapter.enforcement_check(['level=INFO msg="Listening for events..."']) is None


def test_exec_events_are_not_alerts(adapter: Adapter, lines: list[str]) -> None:
    assert adapter.parse(lines[3], 1.0) is None
    assert adapter.parse(lines[4], 1.0) is None


def test_non_event_lines_are_not_alerts(adapter: Adapter, lines: list[str]) -> None:
    assert adapter.parse(lines[5], 1.0) is None
    for line in ("", "time=x level=INFO msg=\"Listening for events...\"", "{", "{\"process_exit\": {}}"):
        assert adapter.parse(line, 1.0) is None


@pytest.mark.parametrize("profile", ["default", "tuned", "enforce"])
def test_container_spec(adapter: Adapter, profile: str) -> None:
    spec = spec_for(adapter, profile)
    assert spec.image == f"quay.io/cilium/tetragon:v{adapter.version}"
    assert spec.privileged is True
    assert spec.pid_mode == "host"
    assert spec.cgroupns_mode == "host"
    assert spec.alerts_file == f"tetragon-{profile}-events.json"
    assert "--config-dir=/etc/tetragon/bench/tetragon.conf.d" in spec.command
    assert f"--export-filename=/bench-output/{spec.alerts_file}" in spec.command
    mounts = {mount.target: mount for mount in spec.mounts}
    config = mounts["/etc/tetragon/bench"]
    assert config.source == f"/host/repo/tools/tetragon/{profile}"
    assert config.read_only is True
    output = mounts["/bench-output"]
    assert output.source == "/host/out/run-1"
    assert output.read_only is False
    assert mounts["/var/lib/tetragon/btf"].source == "/sys/kernel/btf/vmlinux"
    assert mounts["/sys/fs/bpf"].read_only is False
    assert mounts["/procRoot"].source == "/proc"


def test_ready_pattern(adapter: Adapter) -> None:
    pattern = re.compile(spec_for(adapter, "default").ready_pattern)
    assert pattern.search('time=2024-01-01T00:00:00Z level=INFO msg="Listening for events..."')
    assert not pattern.search('time=2024-01-01T00:00:00Z level=INFO msg="Listening for events completed."')


@needs_tools
@pytest.mark.parametrize("profile", ["default", "tuned", "enforce"])
def test_profile_configuration(profile: str) -> None:
    profile_dir = REPO_ROOT / "tools" / "tetragon" / profile
    conf = profile_dir / "tetragon.conf.d"
    assert (conf / "tracing-policy-dir").read_text().strip() == "/etc/tetragon/bench/tetragon.tp.d"
    assert (conf / "procfs").read_text().strip() == "/procRoot"
    assert not (conf / "export-filename").exists()
    policies = {path.name for path in (profile_dir / "tetragon.tp.d").glob("*.yaml")}
    assert DEFAULT_POLICIES <= policies


def policy_names(profile: str) -> set[str]:
    names = set()
    for path in (REPO_ROOT / "tools" / "tetragon" / profile / "tetragon.tp.d").glob("*.yaml"):
        match = re.search(r'^  name: "([^"]+)"', path.read_text(), re.MULTILINE)
        assert match is not None
        names.add(match.group(1))
    return names


@needs_tools
def test_enforce_profile_mirrors_tuned_policies() -> None:
    assert policy_names("enforce") == policy_names("tuned")


@needs_tools
def test_enforce_actions_are_scoped_to_containers() -> None:
    directory = REPO_ROOT / "tools" / "tetragon" / "enforce" / "tetragon.tp.d"
    enforcing = 0
    for path in directory.glob("*.yaml"):
        text = path.read_text()
        assert "BENCH_MARKER" not in text
        assert "bench-" not in text
        if "action: Sigkill" in text:
            enforcing += 1
            assert text.count('- "host_ns"') >= text.count("action: Sigkill")
    assert enforcing >= 10
    for name in DEFAULT_POLICIES:
        enforce_lines = [line.rstrip() for line in (directory / name).read_text().splitlines()]
        default_path = REPO_ROOT / "tools" / "tetragon" / "default" / "tetragon.tp.d" / name
        assert enforce_lines == [line.rstrip() for line in default_path.read_text().splitlines()]


@needs_tools
@pytest.mark.parametrize("profile", ["default", "tuned"])
def test_observation_profiles_do_not_enforce(profile: str) -> None:
    for path in (REPO_ROOT / "tools" / "tetragon" / profile / "tetragon.tp.d").glob("*.yaml"):
        text = path.read_text()
        assert "Sigkill" not in text
        assert "Override" not in text


@needs_tools
def test_tuned_policies_are_behavioural() -> None:
    policies = sorted((REPO_ROOT / "tools" / "tetragon" / "tuned" / "tetragon.tp.d").glob("*.yaml"))
    assert len(policies) > len(DEFAULT_POLICIES)
    names = set()
    for path in policies:
        text = path.read_text()
        assert text.count("kind: TracingPolicy") == 1
        assert "BENCH_MARKER" not in text
        assert "bench-" not in text
        match = re.search(r'^  name: "([^"]+)"', text, re.MULTILINE)
        assert match is not None
        names.add(match.group(1))
    assert len(names) == len(policies)
