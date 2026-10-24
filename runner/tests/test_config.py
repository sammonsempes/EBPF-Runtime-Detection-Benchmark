from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from bench.adapters import TOOLS
from bench.config import Config, OverheadConfig, load_config, parse_config

REPO_CONFIG = Path(__file__).resolve().parents[2] / "bench.yaml"

FULL = """
tools: [falco, tetragon]
profiles: [default, tuned]
scenarios: [a, b]
repetitions: 2
grace_seconds: 5
idle_seconds: 1.5
overhead:
  duration_seconds: 10
  repetitions: 2
  workloads: [syscall]
results_dir: out
"""


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "bench.yaml"
    path.write_text(text)
    return path


def test_load_full_config(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, FULL))
    assert config.tools == ("falco", "tetragon")
    assert config.profiles == ("default", "tuned")
    assert config.scenarios == ("a", "b")
    assert config.repetitions == 2
    assert config.grace_seconds == 5
    assert config.idle_seconds == 1.5
    assert config.overhead == OverheadConfig(duration_seconds=10, repetitions=2, workloads=("syscall",))
    assert config.results_dir == Path("out")
    assert config.source == FULL


def test_defaults_and_all(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, "tools: all\nscenarios: all\n"))
    assert config.tools == TOOLS
    assert config.scenarios is None
    assert config.repetitions == 5
    assert config.overhead.enabled
    assert config.overhead.workloads == ("syscall", "exec", "fileio")


def test_repository_config_is_valid() -> None:
    if not REPO_CONFIG.is_file():
        pytest.skip("bench.yaml not present")
    config = load_config(REPO_CONFIG)
    assert config.tools == TOOLS
    assert config.repetitions == 5


@pytest.mark.parametrize(
    "text, message",
    [
        ("tools: [nope]\n", "unknown tools"),
        ("tools: []\n", "must not be empty"),
        ("tools: [falco, falco]\n", "duplicates"),
        ("repetitions: 0\n", "repetitions"),
        ("repetitions: true\n", "repetitions"),
        ("grace_seconds: -1\n", "grace_seconds"),
        ("idle_seconds: fast\n", "idle_seconds"),
        ("overhead: {duration_seconds: 0}\n", "duration_seconds"),
        ("overhead: {colour: red}\n", "unknown overhead keys"),
        ("overhead: {workloads: ['../evil']}\n", "invalid name"),
        ("surprise: 1\n", "unknown configuration keys"),
        ("results_dir: ''\n", "results_dir"),
        ("- a\n- b\n", "mapping"),
        ("tools: [falco\n", "invalid YAML"),
    ],
)
def test_invalid_configs(tmp_path: Path, text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        load_config(write(tmp_path, text))


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        load_config(tmp_path / "missing.yaml")


def test_replace_revalidates() -> None:
    config = parse_config({})
    assert replace(config, repetitions=1).repetitions == 1
    with pytest.raises(ValueError):
        replace(config, tools=("unknown",))


def test_control_scenarios_and_profiles() -> None:
    assert parse_config({}).control_scenarios is True
    assert parse_config({"control_scenarios": False}).control_scenarios is False
    assert parse_config({"profiles": "all"}).profiles == ("default", "tuned", "enforce", "community")
    assert parse_config({}).profiles == ("default", "tuned")
    with pytest.raises(ValueError, match="control_scenarios"):
        parse_config({"control_scenarios": "yes"})


def test_repository_config_enables_enforce_and_control() -> None:
    if not REPO_CONFIG.is_file():
        pytest.skip("bench.yaml not present")
    config = load_config(REPO_CONFIG)
    assert config.profiles == ("default", "tuned", "enforce", "community")
    assert config.control_scenarios is True


def test_overhead_disabled() -> None:
    assert parse_config({"overhead": False}).overhead.enabled is False
    assert parse_config({"overhead": {"enabled": False}}).overhead.enabled is False


def test_log_caps() -> None:
    config = parse_config({})
    assert config.max_log_lines == 5_000_000
    assert config.max_log_bytes == 2 * 1024**3
    custom = parse_config({"max_log_lines": 10, "max_log_bytes": 1000})
    assert (custom.max_log_lines, custom.max_log_bytes) == (10, 1000)
    assert parse_config(custom.as_dict()) == custom
    for key in ("max_log_lines", "max_log_bytes"):
        with pytest.raises(ValueError, match=key):
            parse_config({key: 0})


def test_as_dict_round_trips() -> None:
    config = parse_config({"tools": ["kunai"], "scenarios": ["x"]})
    assert parse_config(config.as_dict()) == replace(config, source="")
    assert isinstance(Config().as_dict()["results_dir"], str)
