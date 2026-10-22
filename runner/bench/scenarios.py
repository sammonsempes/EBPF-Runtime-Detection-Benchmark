from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from bench.model import Scenario, ScenarioKind

TECHNIQUE_PATTERN = re.compile(r"^T\d{4}(\.\d{3})?$")
TACTIC_PATTERN = re.compile(r"^[a-z]+(-[a-z]+)*$")
ALLOWED_REQUIREMENTS = frozenset({"privileged", "attacker"})
MANIFEST = "scenario.yaml"
SCRIPT = "run.sh"
SCRIPTS = (SCRIPT, "check.sh", "cleanup.sh")


def _invalid(manifest: Path, message: str) -> ValueError:
    return ValueError(f"{manifest}: {message}")


def _text(manifest: Path, data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise _invalid(manifest, f"field '{key}' must be a non-empty string, got {value!r}")
    return value


def _kind(manifest: Path, data: dict[str, Any]) -> ScenarioKind:
    value = data.get("kind")
    try:
        return ScenarioKind(value)
    except ValueError:
        allowed = [kind.value for kind in ScenarioKind]
        raise _invalid(manifest, f"field 'kind' must be one of {allowed}, got {value!r}") from None


def _classification(manifest: Path, data: dict[str, Any], kind: ScenarioKind) -> tuple[str | None, str | None]:
    tactic = data.get("tactic")
    technique = data.get("technique")
    if kind is ScenarioKind.BENIGN:
        if tactic is not None or technique is not None:
            raise _invalid(manifest, "benign scenarios must have null 'tactic' and 'technique'")
        return None, None
    if not isinstance(technique, str) or not TECHNIQUE_PATTERN.match(technique):
        raise _invalid(manifest, f"field 'technique' must match T1234 or T1234.567, got {technique!r}")
    if not isinstance(tactic, str) or not TACTIC_PATTERN.match(tactic):
        raise _invalid(manifest, f"field 'tactic' must be an ATT&CK tactic slug, got {tactic!r}")
    return tactic, technique


def _timeout(manifest: Path, data: dict[str, Any]) -> float:
    value = data.get("timeout", 60)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise _invalid(manifest, f"field 'timeout' must be a positive number, got {value!r}")
    return float(value)


def _requires(manifest: Path, data: dict[str, Any]) -> tuple[str, ...]:
    value = data.get("requires")
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise _invalid(manifest, f"field 'requires' must be a list of strings, got {value!r}")
    unknown = sorted(set(value) - ALLOWED_REQUIREMENTS)
    if unknown:
        raise _invalid(manifest, f"field 'requires' has unknown values {unknown}, allowed: {sorted(ALLOWED_REQUIREMENTS)}")
    if len(set(value)) != len(value):
        raise _invalid(manifest, f"field 'requires' contains duplicates: {value}")
    return tuple(value)


def load_scenario(directory: Path) -> Scenario:
    manifest = directory / MANIFEST
    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise _invalid(manifest, f"invalid YAML: {error}") from error
    if not isinstance(data, dict):
        raise _invalid(manifest, "expected a mapping")
    scenario_id = _text(manifest, data, "id")
    if scenario_id != directory.name:
        raise _invalid(manifest, f"id {scenario_id!r} must equal the directory name {directory.name!r}")
    kind = _kind(manifest, data)
    tactic, technique = _classification(manifest, data, kind)
    for script in SCRIPTS:
        if not (directory / script).is_file():
            raise _invalid(manifest, f"missing {script} in {directory}")
    return Scenario(
        id=scenario_id,
        name=_text(manifest, data, "name"),
        kind=kind,
        description=_text(manifest, data, "description"),
        path=directory,
        tactic=tactic,
        technique=technique,
        timeout=_timeout(manifest, data),
        requires=_requires(manifest, data),
    )


def load_scenarios(root: Path) -> list[Scenario]:
    root = Path(root)
    if (root / "scenarios").is_dir():
        root = root / "scenarios"
    if not root.is_dir():
        raise ValueError(f"scenario directory not found: {root}")
    directories = sorted(path for path in root.iterdir() if path.is_dir() and (path / MANIFEST).is_file())
    return [load_scenario(directory) for directory in directories]


def select_scenarios(scenarios: list[Scenario], ids: tuple[str, ...] | list[str] | None) -> list[Scenario]:
    if ids is None:
        return list(scenarios)
    by_id = {scenario.id: scenario for scenario in scenarios}
    unknown = [scenario_id for scenario_id in ids if scenario_id not in by_id]
    if unknown:
        raise ValueError(f"unknown scenarios: {unknown}")
    return [by_id[scenario_id] for scenario_id in ids]
