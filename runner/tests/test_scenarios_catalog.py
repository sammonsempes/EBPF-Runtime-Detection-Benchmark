from pathlib import Path

import pytest

from bench.model import ScenarioKind
from bench.scenarios import load_scenarios

SCENARIOS_ROOT = Path(__file__).resolve().parents[2] / "scenarios"

EXPECTED_ATTACKS = {
    "t1059-004-reverse-shell": ("execution", "T1059.004"),
    "t1059-006-python-exec": ("execution", "T1059.006"),
    "t1105-ingress-tool-transfer": ("command-and-control", "T1105"),
    "t1053-003-cron-persistence": ("persistence", "T1053.003"),
    "t1098-004-ssh-authorized-keys": ("persistence", "T1098.004"),
    "t1543-002-systemd-service": ("persistence", "T1543.002"),
    "t1136-001-create-account": ("persistence", "T1136.001"),
    "t1547-006-kernel-module": ("persistence", "T1547.006"),
    "t1548-001-setuid-binary": ("privilege-escalation", "T1548.001"),
    "t1611-escape-to-host": ("privilege-escalation", "T1611"),
    "t1070-003-clear-history": ("defense-evasion", "T1070.003"),
    "t1070-002-clear-logs": ("defense-evasion", "T1070.002"),
    "t1036-005-masquerading": ("defense-evasion", "T1036.005"),
    "t1620-fileless-exec": ("defense-evasion", "T1620"),
    "t1222-002-permission-modification": ("defense-evasion", "T1222.002"),
    "t1003-008-shadow-read": ("credential-access", "T1003.008"),
    "t1552-001-credentials-in-files": ("credential-access", "T1552.001"),
    "t1552-007-container-api": ("credential-access", "T1552.007"),
    "t1613-container-discovery": ("discovery", "T1613"),
    "t1082-system-discovery": ("discovery", "T1082"),
    "t1046-network-scan": ("discovery", "T1046"),
    "t1048-exfiltration-http": ("exfiltration", "T1048"),
    "t1496-cryptominer": ("impact", "T1496"),
    "t1485-data-destruction": ("impact", "T1485"),
}

EXPECTED_BENIGN = {
    "benign-compile",
    "benign-web-server",
    "benign-log-rotation",
    "benign-backup",
    "benign-admin-commands",
    "benign-package-query",
}

REQUIRES_ATTACKER = {
    "t1059-004-reverse-shell",
    "t1105-ingress-tool-transfer",
    "t1046-network-scan",
    "t1048-exfiltration-http",
    "t1496-cryptominer",
}

REQUIRES_PRIVILEGED = {
    "t1547-006-kernel-module",
    "t1611-escape-to-host",
}


@pytest.fixture(scope="module")
def catalog():
    return load_scenarios(SCENARIOS_ROOT)


@pytest.fixture(scope="module")
def catalog_by_id(catalog):
    return {scenario.id: scenario for scenario in catalog}


def test_all_expected_scenarios_are_present(catalog_by_id):
    expected = set(EXPECTED_ATTACKS) | EXPECTED_BENIGN
    assert expected <= set(catalog_by_id)


def test_scenario_ids_are_unique(catalog):
    ids = [scenario.id for scenario in catalog]
    assert len(ids) == len(set(ids))


def test_scenario_id_matches_directory_name(catalog):
    for scenario in catalog:
        assert scenario.path.name == scenario.id or scenario.path.parent.name == scenario.id


@pytest.mark.parametrize("scenario_id", sorted(EXPECTED_ATTACKS))
def test_attack_scenarios_have_tactic_and_technique(catalog_by_id, scenario_id):
    scenario = catalog_by_id[scenario_id]
    expected_tactic, expected_technique = EXPECTED_ATTACKS[scenario_id]
    assert scenario.kind == ScenarioKind.ATTACK
    assert scenario.tactic == expected_tactic
    assert scenario.technique == expected_technique


@pytest.mark.parametrize("scenario_id", sorted(EXPECTED_BENIGN))
def test_benign_scenarios_have_no_tactic_or_technique(catalog_by_id, scenario_id):
    scenario = catalog_by_id[scenario_id]
    assert scenario.kind == ScenarioKind.BENIGN
    assert scenario.tactic is None
    assert scenario.technique is None


def test_every_attack_has_tactic_and_technique(catalog):
    for scenario in catalog:
        if scenario.kind == ScenarioKind.ATTACK:
            assert scenario.tactic and scenario.technique, scenario.id
        else:
            assert scenario.tactic is None and scenario.technique is None, scenario.id


def test_requirements_match_catalog(catalog_by_id):
    for scenario_id, scenario in catalog_by_id.items():
        assert ("attacker" in scenario.requires) == (scenario_id in REQUIRES_ATTACKER), scenario_id
        assert ("privileged" in scenario.requires) == (scenario_id in REQUIRES_PRIVILEGED), scenario_id


def test_timeouts_are_positive(catalog):
    for scenario in catalog:
        assert scenario.timeout > 0, scenario.id


@pytest.mark.parametrize("scenario_id", sorted(set(EXPECTED_ATTACKS) | EXPECTED_BENIGN))
def test_run_script_exists_with_shebang(scenario_id):
    run_script = SCENARIOS_ROOT / scenario_id / "run.sh"
    assert run_script.is_file()
    assert run_script.read_text().startswith("#!")


@pytest.mark.parametrize("scenario_id", sorted(set(EXPECTED_ATTACKS) | EXPECTED_BENIGN))
def test_check_and_cleanup_scripts_exist(scenario_id):
    for name in ("check.sh", "cleanup.sh"):
        script = SCENARIOS_ROOT / scenario_id / name
        assert script.is_file(), f"{scenario_id}/{name}"
        assert script.read_text().startswith("#!"), f"{scenario_id}/{name}"


@pytest.mark.parametrize("scenario_id", sorted(set(EXPECTED_ATTACKS) | EXPECTED_BENIGN))
def test_run_script_prints_action_timestamp(scenario_id):
    assert "BENCH_ACTION" in (SCENARIOS_ROOT / scenario_id / "run.sh").read_text()
