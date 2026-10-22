from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from bench.model import ScenarioKind
from bench.scenarios import load_scenarios, select_scenarios

ATTACK = {
    "id": "t1059-004-reverse-shell",
    "name": "Reverse shell with bash",
    "kind": "attack",
    "tactic": "execution",
    "technique": "T1059.004",
    "description": "Opens a bash reverse shell to the attacker container.",
    "timeout": 30,
    "requires": ["attacker"],
}

BENIGN = {
    "id": "benign-package-list",
    "name": "List packages",
    "kind": "benign",
    "tactic": None,
    "technique": None,
    "description": "Lists installed packages.",
}


def make(root: Path, data: dict, directory: str | None = None, script: bool = True, skip: tuple[str, ...] = ()) -> Path:
    path = root / (directory or str(data["id"]))
    path.mkdir(parents=True)
    (path / "scenario.yaml").write_text(yaml.safe_dump(data))
    if script:
        for name in ("run.sh", "check.sh", "cleanup.sh"):
            if name not in skip:
                (path / name).write_text("#!/bin/sh\nexit 0\n")
    return path


def test_loads_valid_scenarios_sorted(tmp_path: Path) -> None:
    make(tmp_path, ATTACK)
    make(tmp_path, BENIGN)
    scenarios = load_scenarios(tmp_path)
    assert [scenario.id for scenario in scenarios] == ["benign-package-list", "t1059-004-reverse-shell"]
    benign, attack = scenarios
    assert attack.kind is ScenarioKind.ATTACK
    assert attack.technique == "T1059.004"
    assert attack.tactic == "execution"
    assert attack.timeout == 30.0
    assert attack.requires == ("attacker",)
    assert attack.path == tmp_path / ATTACK["id"]
    assert benign.kind is ScenarioKind.BENIGN
    assert benign.technique is None
    assert benign.timeout == 60.0
    assert benign.requires == ()


def test_accepts_repository_root(tmp_path: Path) -> None:
    make(tmp_path / "scenarios", ATTACK)
    assert [scenario.id for scenario in load_scenarios(tmp_path)] == [ATTACK["id"]]


def test_ignores_directories_without_manifest(tmp_path: Path) -> None:
    make(tmp_path, ATTACK)
    (tmp_path / "lib").mkdir()
    (tmp_path / "README.md").write_text("docs")
    assert len(load_scenarios(tmp_path)) == 1


def test_technique_without_subtechnique(tmp_path: Path) -> None:
    make(tmp_path, {**ATTACK, "technique": "T1105"})
    assert load_scenarios(tmp_path)[0].technique == "T1105"


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"kind": "evil"}, "kind"),
        ({"technique": "T59"}, "technique"),
        ({"technique": "t1059.004"}, "technique"),
        ({"technique": "T1059.04"}, "technique"),
        ({"technique": None}, "technique"),
        ({"tactic": None}, "tactic"),
        ({"tactic": "Execution"}, "tactic"),
        ({"requires": ["root"]}, "requires"),
        ({"requires": "privileged"}, "requires"),
        ({"requires": ["attacker", "attacker"]}, "duplicates"),
        ({"timeout": 0}, "timeout"),
        ({"timeout": "slow"}, "timeout"),
        ({"name": ""}, "name"),
        ({"description": None}, "description"),
        ({"id": "other-id"}, "directory name"),
    ],
)
def test_invalid_attack(tmp_path: Path, changes: dict, message: str) -> None:
    make(tmp_path, {**ATTACK, **changes}, directory=ATTACK["id"])
    with pytest.raises(ValueError, match=message):
        load_scenarios(tmp_path)


@pytest.mark.parametrize("changes", [{"technique": "T1059"}, {"tactic": "execution"}])
def test_benign_must_not_have_classification(tmp_path: Path, changes: dict) -> None:
    make(tmp_path, {**BENIGN, **changes})
    with pytest.raises(ValueError, match="benign"):
        load_scenarios(tmp_path)


def test_missing_run_script(tmp_path: Path) -> None:
    make(tmp_path, ATTACK, script=False)
    with pytest.raises(ValueError, match="run.sh"):
        load_scenarios(tmp_path)


@pytest.mark.parametrize("script", ["check.sh", "cleanup.sh"])
def test_missing_check_or_cleanup_script(tmp_path: Path, script: str) -> None:
    make(tmp_path, ATTACK, skip=(script,))
    with pytest.raises(ValueError, match=re.escape(f"missing {script}")):
        load_scenarios(tmp_path)


def test_error_mentions_manifest_path(tmp_path: Path) -> None:
    path = make(tmp_path, {**ATTACK, "kind": "nope"})
    with pytest.raises(ValueError, match=re.escape(str(path / "scenario.yaml"))):
        load_scenarios(tmp_path)


def test_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "broken"
    path.mkdir()
    (path / "scenario.yaml").write_text("id: [broken\n")
    (path / "run.sh").write_text("exit 0\n")
    with pytest.raises(ValueError, match="invalid YAML"):
        load_scenarios(tmp_path)


def test_missing_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        load_scenarios(tmp_path / "nowhere")


def test_select_scenarios(tmp_path: Path) -> None:
    make(tmp_path, ATTACK)
    make(tmp_path, BENIGN)
    scenarios = load_scenarios(tmp_path)
    assert select_scenarios(scenarios, None) == scenarios
    assert [scenario.id for scenario in select_scenarios(scenarios, [ATTACK["id"]])] == [ATTACK["id"]]
    with pytest.raises(ValueError, match="unknown scenarios"):
        select_scenarios(scenarios, ["missing"])
