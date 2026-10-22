from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from bench.model import Alert, ScenarioRun, WorkloadResult
from bench.scoring import (
    MIB,
    attribute,
    classify,
    compute_overhead,
    id_matches,
    identifies,
    in_window,
    median,
    metric_direction,
    overhead_percent,
    percentile,
    relative_delta,
    score_results,
    score_scenario,
    split_alert_file,
)

VICTIM_ID = "3f2a9c1b7d4e" + "0" * 52
PRIV_ID = "9b8c7d6e5f4a" + "1" * 52
BASE = 1000.0
GRACE = 2.0


def make_run(scenario_id: str, repetition: int, start: float, victim: str = VICTIM_ID, **extra) -> ScenarioRun:
    values = dict(
        scenario_id=scenario_id,
        tool="falco",
        profile="default",
        repetition=repetition,
        marker=f"BENCH-{scenario_id}-{repetition}",
        victim_container_id=victim,
        started_at=start,
        ended_at=start + 5.0,
        exit_code=0,
    )
    values.update(extra)
    return ScenarioRun(**values)


def make_alert(emitted_at: float, rule: str = "rule", **extra) -> Alert:
    return Alert(tool="falco", rule=rule, emitted_at=emitted_at, **extra)


def scenario(id: str, kind: str, tactic: str | None = None, technique: str | None = None, requires=()) -> dict:
    return {
        "id": id,
        "name": id.replace("-", " "),
        "kind": kind,
        "description": "",
        "path": f"/scenarios/{id}",
        "tactic": tactic,
        "technique": technique,
        "timeout": 30.0,
        "requires": list(requires),
    }


def write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(asdict(record)) + "\n" for record in records), encoding="utf-8")


def build_results(root: Path) -> Path:
    results = root / "run-1"
    results.mkdir()
    scenarios = [
        scenario("reverse-shell", "attack", "execution", "T1059.004"),
        scenario("cron-persist", "attack", "persistence", "T1053.003"),
        scenario("ns-escape", "attack", "privilege-escalation", "T1611", ["privileged"]),
        scenario("pkg-install", "benign"),
    ]
    metadata = {
        "run_id": "run-1",
        "host": {"kernel": "6.6.0", "docker": "27.0", "cpus": 4, "memory": 8589934592},
        "config": {"grace_seconds": GRACE, "repetitions": 2},
        "tools": {
            "falco": {
                "version": "0.39.0",
                "status": "ok",
                "error": None,
                "profiles": ["default", "tuned"],
                "config_sha256": {"default": "a" * 64, "tuned": "b" * 64},
            },
            "tetragon": {
                "version": "1.2.0",
                "status": "failed",
                "error": "image pull failed",
                "profiles": ["default"],
                "config_sha256": {},
            },
        },
        "scenarios": scenarios,
        "operational": {
            "falco": {
                "tool": "falco",
                "version": "0.39.0",
                "license": "Apache-2.0",
                "deployment": {"linux": "container", "kubernetes": "helm", "steps": 1},
                "rules": {"language": "YAML", "custom_rules": True, "hot_reload": True},
                "output": {"formats": ["json"], "enrichment": ["container"], "attack_mapping": True},
                "scores": {"deployment": 5, "rule_customization": 5, "output_quality": 4},
                "notes": "Needs | pipes escaped",
            }
        },
    }
    (results / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    schedule = [
        ("reverse-shell", 1),
        ("reverse-shell", 2),
        ("cron-persist", 1),
        ("cron-persist", 2),
        ("ns-escape", 1),
        ("ns-escape", 2),
        ("pkg-install", 1),
        ("pkg-install", 2),
    ]
    runs = []
    for index, (scenario_id, repetition) in enumerate(schedule):
        victim = PRIV_ID if scenario_id == "ns-escape" else VICTIM_ID
        runs.append(make_run(scenario_id, repetition, BASE + index * 20.0, victim))
    runs[3] = make_run("cron-persist", 2, runs[3].started_at, exit_code=1)
    write_jsonl(results / "runs.jsonl", list(reversed(runs)))
    starts = {(run.scenario_id, run.repetition): run for run in runs}
    alerts = [
        make_alert(starts["reverse-shell", 1].started_at + 1.5, "Reverse shell", container_id=VICTIM_ID[:12]),
        make_alert(starts["reverse-shell", 1].started_at + 3.0, "Shell spawned", container_id=VICTIM_ID[:12]),
        make_alert(starts["reverse-shell", 2].started_at + 0.5, "Reverse shell", container_name="/bench-victim"),
        make_alert(
            starts["cron-persist", 1].ended_at + GRACE,
            "Cron write",
            raw={"output": f"open /etc/cron.d/{starts['cron-persist', 1].marker}"},
        ),
        make_alert(starts["ns-escape", 1].started_at + 1.0, "Wrong victim", container_name="bench-victim"),
        make_alert(starts["pkg-install", 1].started_at + 2.0, "Package manager", container_id=VICTIM_ID),
        make_alert(BASE - 100.0, "Noise", container_id=VICTIM_ID),
        make_alert(BASE - 50.0, "Host", container_id="host"),
    ]
    write_jsonl(results / "alerts" / "falco-default.jsonl", alerts)
    write_jsonl(results / "alerts" / "falco-tuned.jsonl", [])
    workloads = [
        WorkloadResult("syscall", None, None, 1, {"getpid_p50_ns": 100.0, "openat_ops_per_sec": 1000.0, "score": 10.0}),
        WorkloadResult("syscall", None, None, 2, {"getpid_p50_ns": 110.0, "openat_ops_per_sec": 1000.0, "score": 10.0}),
        WorkloadResult("syscall", None, None, 3, {"getpid_p50_ns": 120.0, "openat_ops_per_sec": 1000.0, "score": 10.0}),
        WorkloadResult(
            "syscall",
            "falco",
            "default",
            1,
            {"getpid_p50_ns": 121.0, "openat_ops_per_sec": 800.0, "score": 12.0},
            [1.0, 2.0],
            [100 * MIB],
        ),
        WorkloadResult(
            "syscall",
            "falco",
            "default",
            2,
            {"getpid_p50_ns": 132.0, "openat_ops_per_sec": 800.0, "score": 12.0},
            [3.0],
            [200 * MIB, 300 * MIB],
        ),
        WorkloadResult(
            "syscall",
            "falco",
            "default",
            3,
            {"getpid_p50_ns": 143.0, "openat_ops_per_sec": 800.0, "score": 12.0},
        ),
        WorkloadResult("syscall", "falco", "tuned", 1, {"getpid_p50_ns": 99.0, "openat_ops_per_sec": 1100.0}),
    ]
    write_jsonl(results / "workloads.jsonl", workloads)
    return results


def test_window_includes_start_and_grace_end_boundaries():
    run = make_run("s", 1, 100.0)
    assert in_window(make_alert(100.0), run, GRACE)
    assert in_window(make_alert(105.0 + GRACE), run, GRACE)
    assert not in_window(make_alert(99.999), run, GRACE)
    assert not in_window(make_alert(105.0 + GRACE + 0.001), run, GRACE)


def test_attribute_respects_grace_window():
    run = make_run("s", 1, 100.0)
    assert attribute(make_alert(107.0, container_id=VICTIM_ID), [run], GRACE) == run
    assert attribute(make_alert(107.01, container_id=VICTIM_ID), [run], GRACE) is None
    assert attribute(make_alert(107.01, container_id=VICTIM_ID), [run], 3.0) == run


def test_container_id_prefix_match_in_both_directions():
    assert id_matches(VICTIM_ID[:12], VICTIM_ID)
    assert id_matches(VICTIM_ID, VICTIM_ID[:12])
    assert id_matches("docker://" + VICTIM_ID.upper(), VICTIM_ID)
    assert not id_matches(VICTIM_ID[:11], VICTIM_ID)
    assert not id_matches(PRIV_ID, VICTIM_ID)
    assert not id_matches(None, VICTIM_ID)


def test_container_name_must_match_expected_victim():
    run = make_run("s", 1, 100.0, PRIV_ID)
    assert identifies(make_alert(101.0, container_name="/bench-victim-priv"), run, "bench-victim-priv")
    assert not identifies(make_alert(101.0, container_name="bench-victim"), run, "bench-victim-priv")
    assert identifies(make_alert(101.0, container_name="bench-victim"), run, None)
    assert not identifies(make_alert(101.0, container_name="other"), run, None)


def test_marker_anywhere_in_raw():
    run = make_run("s", 1, 100.0)
    nested = make_alert(101.0, raw={"process": {"args": ["touch", f"/tmp/{run.marker}.txt"]}})
    assert identifies(nested, run)
    assert not identifies(make_alert(101.0, raw={"process": "touch"}), run)


def test_alert_in_overlapping_windows_goes_to_earliest_run():
    first = make_run("a", 1, 100.0)
    second = make_run("b", 1, 103.0)
    alert = make_alert(104.0, container_id=VICTIM_ID)
    assert attribute(alert, [second, first], GRACE) == first


def test_overlapping_windows_skip_run_whose_identity_fails():
    first = make_run("a", 1, 100.0, PRIV_ID)
    second = make_run("b", 1, 103.0)
    alert = make_alert(104.0, container_id=VICTIM_ID)
    assert attribute(alert, [first, second], GRACE) == second


def test_victim_names_mapping_is_used_per_scenario():
    unprivileged = make_run("a", 1, 100.0)
    privileged = make_run("b", 1, 101.0, PRIV_ID)
    alert = make_alert(102.0, container_name="bench-victim-priv")
    names = {"a": "bench-victim", "b": "bench-victim-priv"}
    assert attribute(alert, [unprivileged, privileged], GRACE, names) == privileged


def test_median_and_p95():
    assert median([]) is None
    assert percentile([], 95) is None
    assert median([3.0, 1.0, 2.0]) == 2.0
    assert median([1.0, 2.0, 3.0, 4.0]) == 2.5
    assert percentile([5.0], 95) == 5.0
    assert percentile([float(value) for value in range(1, 21)], 95) == pytest.approx(19.05)
    assert percentile([1.0, 2.0], 95) == pytest.approx(1.95)


def test_classify_majority():
    assert classify(0, 0) == "not_run"
    assert classify(2, 3) == "detected"
    assert classify(1, 2) == "partial"
    assert classify(0, 3) == "missed"


def test_overhead_sign_conventions():
    assert metric_direction("getpid_p50_ns") == "higher_is_worse"
    assert metric_direction("connect_p99_us") == "higher_is_worse"
    assert metric_direction("openat_ops_per_sec") == "lower_is_worse"
    assert metric_direction("score") is None
    assert overhead_percent(relative_delta(100.0, 120.0), "higher_is_worse") == pytest.approx(20.0)
    assert overhead_percent(relative_delta(100.0, 80.0), "higher_is_worse") == pytest.approx(-20.0)
    assert overhead_percent(relative_delta(1000.0, 800.0), "lower_is_worse") == pytest.approx(20.0)
    assert overhead_percent(relative_delta(1000.0, 1100.0), "lower_is_worse") == pytest.approx(-10.0)
    assert overhead_percent(relative_delta(10.0, 12.0), None) is None
    assert relative_delta(0.0, 5.0) is None


def test_compute_overhead_without_workloads():
    overhead = compute_overhead({"syscall": {"getpid_p50_ns": 100.0}}, [])
    assert overhead["available"] is False
    assert overhead["workloads"]["syscall"]["getpid_p50_ns"]["value"] is None
    assert overhead["cpu_percent"] == {"median": None, "max": None, "samples": 0}


def test_split_alert_file_handles_dashes():
    known = {"falco": {"default"}, "kube-armor": {"tuned-strict"}}
    assert split_alert_file("kube-armor-tuned-strict", known) == ("kube-armor", "tuned-strict")
    assert split_alert_file("falco-default", known) == ("falco", "default")
    assert split_alert_file("other-tool-default", known) == ("other-tool", "default")
    assert split_alert_file("nodash", known) is None


def test_score_results_end_to_end(tmp_path):
    results = build_results(tmp_path)
    score = score_results(results, GRACE)
    assert json.loads((results / "score.json").read_text(encoding="utf-8")) == score
    falco = score["tools"]["falco"]["profiles"]["default"]
    scenarios = falco["scenarios"]

    reverse = scenarios["reverse-shell"]
    assert (reverse["detected"], reverse["repetitions"], reverse["status"]) == (2, 2, "detected")
    assert reverse["latencies"] == [1.5, 0.5]
    assert reverse["latency_median"] == 1.0
    assert reverse["latency_p95"] == pytest.approx(1.45)
    assert reverse["rules"] == ["Reverse shell", "Shell spawned"]
    assert reverse["alerts"] == 3

    cron = scenarios["cron-persist"]
    assert (cron["detected"], cron["status"], cron["detection_rate"]) == (1, "partial", 0.5)
    assert cron["latencies"] == [5.0 + GRACE]
    assert cron["failed_executions"] == 1

    escape = scenarios["ns-escape"]
    assert (escape["detected"], escape["status"]) == (0, "missed")

    benign = scenarios["pkg-install"]
    assert benign["false_positives"] == 1
    assert benign["rules"] == ["Package manager"]

    summary = falco["summary"]
    assert summary["true_positives"] == 3
    assert summary["false_negatives"] == 3
    assert summary["false_positives"] == 1
    assert summary["benign_runs"] == 2
    assert summary["false_positive_rate"] == 0.5
    assert summary["recall"] == pytest.approx(1 / 3, abs=1e-6)
    assert summary["detection_rate"] == 0.5
    assert summary["background_noise"] == 1
    assert summary["unattributed_in_window"] == 1
    assert summary["non_victim_alerts"] == 1
    assert summary["alerts_total"] == 8
    assert summary["alerts_attributed"] == 5
    assert summary["latency_median"] == 1.5
    assert summary["coverage"]["execution"] == {
        "scenarios": 1,
        "detected": 1,
        "partial": 0,
        "missed": 0,
        "coverage": 1.0,
    }
    assert summary["coverage"]["persistence"]["partial"] == 1
    assert summary["coverage"]["privilege-escalation"]["coverage"] == 0.0


def test_score_results_overhead(tmp_path):
    score = score_results(build_results(tmp_path), GRACE)
    assert score["baseline"]["syscall"]["getpid_p50_ns"] == 110.0
    overhead = score["tools"]["falco"]["profiles"]["default"]["overhead"]
    getpid = overhead["workloads"]["syscall"]["getpid_p50_ns"]
    assert getpid["value"] == 132.0
    assert getpid["delta"] == pytest.approx(0.2)
    assert getpid["overhead_percent"] == pytest.approx(20.0)
    openat = overhead["workloads"]["syscall"]["openat_ops_per_sec"]
    assert openat["delta"] == pytest.approx(-0.2)
    assert openat["overhead_percent"] == pytest.approx(20.0)
    plain = overhead["workloads"]["syscall"]["score"]
    assert plain["delta"] == pytest.approx(0.2)
    assert plain["overhead_percent"] is None
    assert overhead["syscall_latency_overhead_percent"] == pytest.approx(20.0)
    assert overhead["cpu_percent"] == {"median": 2.0, "max": 3.0, "samples": 3}
    assert overhead["memory_mib"] == {"median": 200.0, "max": 300.0, "samples": 3}
    tuned = score["tools"]["falco"]["profiles"]["tuned"]["overhead"]["workloads"]["syscall"]
    assert tuned["openat_ops_per_sec"]["overhead_percent"] == pytest.approx(-10.0)
    assert tuned["getpid_p50_ns"]["overhead_percent"] == pytest.approx(-10.0)
    assert tuned["score"]["value"] is None


def test_score_results_failed_tool_and_unrun_profile(tmp_path):
    score = score_results(build_results(tmp_path), GRACE)
    tetragon = score["tools"]["tetragon"]
    assert tetragon["status"] == "failed"
    assert tetragon["error"] == "image pull failed"
    profile = tetragon["profiles"]["default"]
    assert profile["summary"]["recall"] is None
    assert profile["summary"]["false_positive_rate"] is None
    assert profile["overhead"]["available"] is False
    assert {entry["status"] for entry in profile["scenarios"].values()} == {"not_run"}
    tuned = score["tools"]["falco"]["profiles"]["tuned"]
    assert tuned["summary"]["attack_scenarios"] == 0
    assert tuned["overhead"]["available"] is True


def test_score_results_tolerates_missing_files(tmp_path):
    results = tmp_path / "empty"
    results.mkdir()
    score = score_results(results, GRACE)
    assert score == {
        "baseline": {},
        "control": {
            "available": False,
            "invalid_scenarios": [],
            "scenarios": {},
            "status": "skipped",
            "unknown_scenarios": [],
            "valid_scenarios": [],
        },
        "grace_seconds": GRACE,
        "run_id": "empty",
        "scenarios": {},
        "tools": {},
    }


def test_alert_after_run_end_by_event_time_is_not_attributed():
    run = make_run("s", 1, 100.0)
    inside = make_alert(106.0, container_id=VICTIM_ID, event_at=105.5)
    late_event = make_alert(106.0, container_id=VICTIM_ID, event_at=106.2)
    unknown_time = make_alert(106.0, container_id=VICTIM_ID)
    assert attribute(inside, [run], GRACE) == run
    assert attribute(late_event, [run], GRACE) is None
    assert attribute(unknown_time, [run], GRACE) == run


def enforce_results(root: Path, verified=True, control_effects=None) -> Path:
    results = root / "enforce-run"
    results.mkdir()
    scenarios = [
        scenario("shell", "attack", "execution", "T1059.004"),
        scenario("cron", "attack", "persistence", "T1053.003"),
        scenario("broken", "attack", "impact", "T1485"),
        scenario("ghost", "attack", "discovery", "T1082"),
        scenario("build", "benign"),
        scenario("serve", "benign"),
    ]
    control_effects = control_effects or {
        "shell": True,
        "cron": True,
        "broken": False,
        "ghost": True,
        "build": True,
        "serve": True,
    }
    enforce_effects = {"shell": False, "cron": True, "broken": False, "ghost": False, "build": False, "serve": True}
    runs = []
    alerts = []
    start = BASE
    for scenario_id, effect in control_effects.items():
        for repetition in (0, 1):
            runs.append(
                make_run(scenario_id, repetition, start, tool="none", profile="control", effect_achieved=effect)
            )
            start += 20.0
    for scenario_id, effect in enforce_effects.items():
        for repetition in (0, 1):
            run = make_run(
                scenario_id,
                repetition,
                start,
                profile="enforce",
                action_at=start + 1.0,
                effect_achieved=effect,
                check_exit_code=0 if effect else 1,
            )
            runs.append(run)
            if scenario_id == "shell":
                alerts.append(make_alert(start + 1.5, "Shell", container_id=VICTIM_ID, action="kill"))
            if scenario_id == "cron":
                alerts.append(make_alert(start + 2.0, "Cron", container_id=VICTIM_ID))
            if scenario_id == "build":
                alerts.append(make_alert(start + 0.5, "Build", container_id=VICTIM_ID, action="kill"))
            start += 20.0
    metadata = {
        "run_id": "enforce-run",
        "tools": {"kunai": {"version": "0.6.2", "status": "ok", "profiles": ["enforce"]}},
        "scenarios": scenarios,
        "control": {"status": "completed"},
        "deployments": {
            "kunai-enforce": {
                "status": "completed",
                "container_started_at": BASE + 200.0,
                "ended_at": BASE + 200.0 + 600.0,
                "time_to_ready": 2.5,
                "log_lines": 100,
                "log_bytes": 4096,
                "alerts_file_lines": 20,
                "alerts_file_bytes": 1024,
                "enforcement_verified": verified,
                "enforcement_alerts": 4,
                "confirmed_enforcements": [BASE + 241.6, BASE + 261.6],
            }
        },
    }
    (results / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    write_jsonl(results / "runs.jsonl", [replace(run, tool="kunai") if run.tool == "falco" else run for run in runs])
    write_jsonl(results / "alerts" / "kunai-enforce.jsonl", [replace(alert, tool="kunai") for alert in alerts])
    return results


def test_control_validity(tmp_path):
    score = score_results(enforce_results(tmp_path), GRACE)
    control = score["control"]
    assert control["available"] is True and control["status"] == "completed"
    assert control["invalid_scenarios"] == ["broken"]
    assert control["valid_scenarios"] == ["build", "cron", "ghost", "serve", "shell"]
    assert control["scenarios"]["broken"]["effect_not_achieved"] == 2
    assert "none" not in score["tools"]
    assert set(score["tools"]) == {"kunai"}


def test_enforce_response_metrics(tmp_path):
    score = score_results(enforce_results(tmp_path), GRACE)
    profile = score["tools"]["kunai"]["profiles"]["enforce"]
    assert profile["enforce"] is True
    scenarios = profile["scenarios"]
    shell = scenarios["shell"]
    assert shell["latencies"] == [0.5, 0.5]
    assert {item["latency_reference"] for item in shell["runs"]} == {"action"}
    assert shell["response"]["status"] == "prevented"
    assert shell["response"]["prevented"] == 2
    assert shell["response"]["response_latency_median"] == 0.5
    assert shell["response"]["confirmed_enforcements"] == 2
    assert scenarios["cron"]["response"]["status"] == "detected"
    assert scenarios["cron"]["response"]["detected_not_prevented"] == 2
    assert scenarios["broken"]["response"]["status"] == "invalid"
    assert scenarios["broken"]["response"]["prevention_rate"] is None
    assert scenarios["broken"]["valid"] is False
    assert scenarios["ghost"]["response"]["prevented_without_alert"] == 2
    assert scenarios["build"]["response"]["collateral_damage"] is True
    assert scenarios["build"]["latencies"] == [-0.5, -0.5]
    assert scenarios["serve"]["response"]["collateral_damage"] is False
    response = profile["response"]
    assert response["enforcement_verified"] is True and response["valid"] is True
    assert response["valid_attack_scenarios"] == 3
    assert response["prevented"] == ["ghost", "shell"]
    assert response["prevention_rate"] == pytest.approx(2 / 3, abs=1e-6)
    assert response["detected_not_prevented"] == 2
    assert response["detected_not_prevented_scenarios"] == ["cron"]
    assert response["prevented_without_alert"] == 2
    assert response["prevented_without_alert_scenarios"] == ["ghost"]
    assert response["collateral_damage"] == 1
    assert response["collateral_damage_rate"] == 0.5
    assert response["invalid_scenarios"] == ["broken"]
    assert response["response_latency_median"] == 0.5
    assert response["confirmed_enforcements"] == 2
    summary = profile["summary"]
    assert summary["invalid_attack_scenarios"] == ["broken"]
    assert summary["action_timestamp_share"] == 1.0
    assert summary["early_alerts"] == 0


def test_enforce_unverified_marks_profile_invalid(tmp_path):
    score = score_results(enforce_results(tmp_path, verified=False), GRACE)
    response = score["tools"]["kunai"]["profiles"]["enforce"]["response"]
    assert response["enforcement_verified"] is False
    assert response["valid"] is False
    assert response["invalid_reason"]


def test_measured_operational(tmp_path):
    score = score_results(enforce_results(tmp_path), GRACE)
    operational = score["tools"]["kunai"]["profiles"]["enforce"]["operational"]
    assert operational["time_to_ready"] == 2.5
    assert operational["duration_seconds"] == 600.0
    assert operational["alerts"] == 6
    assert operational["alerts_per_minute"] == 0.6
    assert operational["log_lines"] == 120
    assert operational["log_lines_per_minute"] == 12.0
    assert operational["log_bytes"] == 5120
    assert operational["attributed_share"] == 1.0
    assert operational["container_identity_share"] == 1.0


def test_latency_falls_back_to_start_without_action():
    info = {"name": "s", "kind": "attack", "tactic": "execution", "technique": "T1059", "requires": []}
    with_action = make_run("s", 0, 100.0, action_at=101.0)
    without = make_run("s", 1, 200.0)
    attributed = {
        (with_action.scenario_id, 0, with_action.marker, 100.0): [make_alert(101.25)],
        (without.scenario_id, 1, without.marker, 200.0): [make_alert(201.25)],
    }
    entry = score_scenario(info, [with_action, without], attributed)
    assert [item["latency_reference"] for item in entry["runs"]] == ["action", "start"]
    assert entry["latencies"] == [0.25, 1.25]
    assert entry["action_timestamps"] == 1
    assert "response" not in entry


def test_host_cpu_overhead():
    baseline = [WorkloadResult("syscall", None, None, 0, {"ops": 1.0}, host_cpu_percent=[10.0, 12.0, 14.0])]
    measured = [WorkloadResult("syscall", "falco", "default", 0, {"ops": 1.0}, host_cpu_percent=[20.0, 30.0])]
    overhead = compute_overhead({}, measured, [value for item in baseline for value in item.host_cpu_percent])
    assert overhead["host_cpu_percent"] == {"median": 25.0, "max": 30.0, "samples": 2}
    assert overhead["host_cpu_baseline"]["median"] == 12.0
    assert overhead["host_cpu_delta_pp"] == 13.0
    assert compute_overhead({}, [])["host_cpu_delta_pp"] is None
