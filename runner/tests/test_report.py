from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from bench.model import Alert, ScenarioRun, WorkloadResult
from bench.report import render_report, write_report
from bench.scoring import score_results

VICTIM_ID = "c0ffee123456" + "0" * 52
GRACE = 2.0


def test_report_never_renders_host_hostname() -> None:
    text = render_report({"run_id": "r1"}, {"host": {"hostname": "secret-laptop", "kernel": "6.6.87"}})
    assert "host.kernel" in text and "6.6.87" in text
    assert "hostname" not in text and "secret-laptop" not in text


def write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(asdict(record)) + "\n" for record in records), encoding="utf-8")


def scenario(id: str, kind: str, tactic: str | None, technique: str | None) -> dict:
    return {
        "id": id,
        "name": id,
        "kind": kind,
        "description": "",
        "path": f"/scenarios/{id}",
        "tactic": tactic,
        "technique": technique,
        "timeout": 30.0,
        "requires": [],
    }


def run(tool: str, profile: str, scenario_id: str, repetition: int, start: float, exit_code: int = 0) -> ScenarioRun:
    return ScenarioRun(
        scenario_id=scenario_id,
        tool=tool,
        profile=profile,
        repetition=repetition,
        marker=f"M-{tool}-{profile}-{scenario_id}-{repetition}",
        victim_container_id=VICTIM_ID,
        started_at=start,
        ended_at=start + 4.0,
        exit_code=exit_code,
    )


def build_results(root: Path, reverse: bool = False) -> Path:
    results = root / ("reversed" if reverse else "ordered")
    results.mkdir()
    metadata = {
        "run_id": "2026-10-22T10-00-00",
        "host": {"kernel": "6.6.87", "docker": "27.3.1", "cpus": 8, "memory": 16000000000},
        "config": {"grace_seconds": GRACE, "repetitions": 2},
        "tools": {
            "falco": {
                "version": "0.39.0",
                "status": "ok",
                "error": None,
                "profiles": ["default"],
                "config_sha256": {"default": "0123456789abcdef" * 4},
            },
            "tracee": {
                "version": "0.22.0",
                "status": "ok",
                "error": None,
                "profiles": ["default"],
                "config_sha256": {"default": "fedcba9876543210" * 4},
            },
            "tetragon": {
                "version": "1.2.0",
                "status": "failed",
                "error": "BTF not available",
                "profiles": ["default"],
                "config_sha256": {},
            },
        },
        "scenarios": [
            scenario("t1059-reverse-shell", "attack", "execution", "T1059.004"),
            scenario("t1053-cron", "attack", "persistence", "T1053.003"),
            scenario("t1611-escape", "attack", "privilege-escalation", "T1611"),
            scenario("benign-apt", "benign", None, None),
        ],
        "operational": {
            "tracee": {
                "tool": "tracee",
                "version": "0.22.0",
                "license": "Apache-2.0",
                "deployment": {"linux": "docker run", "kubernetes": "helm", "steps": 2},
                "rules": {"language": "Rego/Go", "custom_rules": True, "hot_reload": False},
                "output": {"formats": ["json", "table"], "enrichment": ["container"], "attack_mapping": True},
                "scores": {"deployment": 4, "rule_customization": 4, "output_quality": 5},
                "notes": "Signatures | events",
            },
            "falco": {
                "tool": "falco",
                "version": "0.39.0",
                "license": "Apache-2.0",
                "deployment": {"linux": "docker run", "kubernetes": "helm", "steps": 1},
                "rules": {"language": "YAML", "custom_rules": True, "hot_reload": True},
                "output": {"formats": ["json"], "enrichment": ["container", "k8s"], "attack_mapping": True},
                "scores": {"deployment": 5, "rule_customization": 5, "output_quality": 4},
                "notes": "Default ruleset",
            },
        },
    }
    (results / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    order = ["t1059-reverse-shell", "t1053-cron", "t1611-escape", "benign-apt"]
    runs = []
    start = 1000.0
    for tool in ("falco", "tracee"):
        for scenario_id in order:
            for repetition in (1, 2):
                failed = (tool, scenario_id, repetition) == ("tracee", "t1611-escape", 2)
                runs.append(run(tool, "default", scenario_id, repetition, start, 1 if failed else 0))
                start += 30.0
    by_key = {(item.tool, item.scenario_id, item.repetition): item for item in runs}

    def hit(tool: str, scenario_id: str, repetition: int, delay: float, rule: str) -> Alert:
        target = by_key[tool, scenario_id, repetition]
        return Alert(tool=tool, rule=rule, emitted_at=target.started_at + delay, container_id=VICTIM_ID[:12])

    falco_alerts = [
        hit("falco", "t1059-reverse-shell", 1, 0.4, "Reverse shell"),
        hit("falco", "t1059-reverse-shell", 2, 0.6, "Reverse shell"),
        hit("falco", "t1053-cron", 1, 1.0, "Cron modified"),
        hit("falco", "benign-apt", 2, 1.0, "Package management launched"),
    ]
    tracee_alerts = [
        hit("tracee", "t1059-reverse-shell", 1, 0.2, "TRC-1"),
        hit("tracee", "t1059-reverse-shell", 2, 0.2, "TRC-1"),
        hit("tracee", "t1053-cron", 1, 0.3, "TRC-2"),
        hit("tracee", "t1053-cron", 2, 0.3, "TRC-2"),
        hit("tracee", "t1611-escape", 1, 0.3, "TRC-3"),
    ]
    workloads = [
        WorkloadResult("syscall", None, None, 1, {"getpid_p50_ns": 100.0, "openat_ops_per_sec": 2000.0}),
        WorkloadResult("syscall", "falco", "default", 1, {"getpid_p50_ns": 125.0, "openat_ops_per_sec": 1800.0}, [5.0], [64 * 1048576]),
        WorkloadResult("syscall", "tracee", "default", 1, {"getpid_p50_ns": 150.0, "openat_ops_per_sec": 1500.0}, [9.0], [256 * 1048576]),
    ]
    if reverse:
        runs = list(reversed(runs))
        falco_alerts = list(reversed(falco_alerts))
        tracee_alerts = list(reversed(tracee_alerts))
        workloads = list(reversed(workloads))
    write_jsonl(results / "runs.jsonl", runs)
    write_jsonl(results / "alerts" / "falco-default.jsonl", falco_alerts)
    write_jsonl(results / "alerts" / "tracee-default.jsonl", tracee_alerts)
    write_jsonl(results / "workloads.jsonl", workloads)
    return results


def make_report(root: Path, reverse: bool = False) -> str:
    results = build_results(root, reverse)
    score_results(results, GRACE)
    path = write_report(results)
    assert path == results / "report.md"
    return path.read_text(encoding="utf-8")


def test_report_sections_and_rows(tmp_path):
    text = make_report(tmp_path)
    for heading in (
        "## Run metadata",
        "## Leaderboard",
        "## Coverage matrix",
        "## False positives",
        "## Detection latency",
        "## Overhead",
        "## Operational aspects",
        "## Failures",
    ):
        assert heading in text
    assert "| host.kernel | 6.6.87 |" in text
    assert "| falco | 0.39.0 | ok | default | default: 0123456789ab |" in text
    assert "| execution | t1059-reverse-shell | T1059.004 | ✅ 2/2 | — | ✅ 2/2 |" in text
    assert "| persistence | t1053-cron | T1053.003 | ⚠️ 1/2 | — | ✅ 2/2 |" in text
    assert "| privilege-escalation | t1611-escape | T1611 | ❌ 0/2 | — | ⚠️ 1/2 |" in text
    assert "| benign-apt | ⚠️ 1/2 | — | ✅ 0/2 |" in text
    assert "| falco | default | benign-apt | Package management launched |" in text
    assert "| t1059-reverse-shell | 0.500s / 0.590s | — | 0.200s / 0.200s |" in text
    assert "| syscall | getpid_p50_ns | 100.00 | 125.00 (+25.0%) | — | 150.00 (+50.0%) |" in text
    assert "| syscall | openat_ops_per_sec | 2,000 | 1,800 (+10.0%) | — | 1,500 (+25.0%) |" in text
    assert "| tetragon | failed | BTF not available |" in text
    assert "| tracee | default | t1611-escape | 2 | 1 |" in text
    assert "| falco | 0.39.0 | Apache-2.0 | 5 | 5 | 4 | 1 | YAML | yes | yes | json | container, k8s | yes | Default ruleset |" in text
    assert "Signatures \\| events" in text


def test_leaderboard_is_ranked_by_recall(tmp_path):
    text = make_report(tmp_path)
    board = text.split("## Leaderboard", 1)[1].split("## Coverage matrix", 1)[0]
    rows = [line for line in board.splitlines() if line.startswith("| ") and "---" not in line][1:]
    assert [row.split(" | ")[0] for row in rows] == ["| tracee", "| falco", "| tetragon"]
    assert rows[0].startswith("| tracee | default | 66.7% | 83.3% | 0.0% | 0.300s | 0 | 9.00 | 256.00 | +50.0% |")
    assert rows[1].startswith("| falco | default | 33.3% | 50.0% | 50.0% | 0.600s | 0 | 5.00 | 64.00 | +25.0% |")


def test_operational_rows_sorted(tmp_path):
    text = make_report(tmp_path)
    section = text.split("## Operational aspects", 1)[1]
    assert section.index("| falco |") < section.index("| tracee |")


def test_report_is_deterministic(tmp_path):
    first = make_report(tmp_path)
    second = make_report(tmp_path, reverse=True)
    assert first == second.replace("reversed", "ordered")
    results = tmp_path / "ordered"
    assert write_report(results).read_text(encoding="utf-8") == first


def test_report_scores_when_score_missing(tmp_path):
    results = build_results(tmp_path)
    write_report(results)
    assert (results / "score.json").is_file()
    assert "✅ 2/2" in (results / "report.md").read_text(encoding="utf-8")


def build_enforce_results(root: Path, verified: bool | None = True) -> Path:
    results = root / "enforce"
    results.mkdir()
    metadata = {
        "run_id": "enforce-run",
        "config": {"grace_seconds": GRACE},
        "tools": {
            "kubearmor": {"version": "1.7.5", "status": "ok", "profiles": ["default", "enforce"]},
            "falco": {"version": "0.45.0", "status": "ok", "profiles": ["default"]},
        },
        "scenarios": [
            scenario("t1059-shell", "attack", "execution", "T1059.004"),
            scenario("t1053-cron", "attack", "persistence", "T1053.003"),
            scenario("t1485-broken", "attack", "impact", "T1485"),
            scenario("benign-build", "benign", None, None),
        ],
        "operational": {
            "kubearmor": {
                "scores": {"deployment": 3, "output_quality": 4},
                "response": {"blocking": True, "mechanisms": ["bpf-lsm"], "synchronous": True},
            },
            "falco": {"scores": {"deployment": 5, "output_quality": 5}, "response": {"blocking": False, "mechanisms": []}},
        },
        "control": {"status": "completed"},
        "deployments": {
            "kubearmor-enforce": {
                "status": "completed",
                "container_started_at": 900.0,
                "ended_at": 1500.0,
                "time_to_ready": 3.25,
                "log_lines": 600,
                "log_bytes": 2 * 1048576,
                "enforcement_verified": verified,
                "enforcement_alerts": 2,
            }
        },
    }
    (results / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    runs = []
    alerts = []
    start = 1000.0
    control = {"t1059-shell": True, "t1053-cron": True, "t1485-broken": False, "benign-build": True}
    enforce = {"t1059-shell": False, "t1053-cron": True, "t1485-broken": False, "benign-build": False}
    for profile, effects in (("control", control), ("enforce", enforce), ("default", control)):
        for scenario_id, effect in effects.items():
            for repetition in (1, 2):
                tool = "none" if profile == "control" else "kubearmor"
                item = replace(
                    run(tool, profile, scenario_id, repetition, start),
                    action_at=start + 1.0,
                    effect_achieved=effect,
                    cleanup_exit_code=2 if (profile, scenario_id, repetition) == ("enforce", "t1053-cron", 2) else 0,
                )
                runs.append(item)
                if profile == "enforce" and scenario_id == "t1059-shell":
                    alerts.append(
                        Alert(tool="kubearmor", rule="block", emitted_at=start + 1.2, container_id=VICTIM_ID[:12], action="Block")
                    )
                if profile == "enforce" and scenario_id == "t1053-cron":
                    alerts.append(Alert(tool="kubearmor", rule="cron", emitted_at=start + 1.5, container_id=VICTIM_ID[:12]))
                start += 30.0
    write_jsonl(results / "runs.jsonl", runs)
    write_jsonl(results / "alerts" / "kubearmor-enforce.jsonl", alerts)
    write_jsonl(
        results / "workloads.jsonl",
        [
            WorkloadResult("syscall", None, None, 1, {"getpid_p50_ns": 100.0}, host_cpu_percent=[10.0, 20.0]),
            WorkloadResult("syscall", "kubearmor", "enforce", 1, {"getpid_p50_ns": 110.0}, [3.0], [1048576], [30.0]),
        ],
    )
    score_results(results, GRACE)
    return results


def test_response_section(tmp_path):
    text = write_report(build_enforce_results(tmp_path)).read_text(encoding="utf-8")
    assert "## Response effectiveness" in text
    assert "## Control runs" in text
    section = text.split("## Response effectiveness", 1)[1].split("## Overhead", 1)[0]
    assert "| falco | detection only |" in section
    assert "| kubearmor | 50.0% (1/2) | 2 | 0 | 1 (100.0%) | 0.200s | 2 | yes | bpf-lsm | yes |" in section


def test_enforce_coverage_and_control_tables(tmp_path):
    text = write_report(build_enforce_results(tmp_path)).read_text(encoding="utf-8")
    coverage = text.split("## Coverage matrix", 1)[1].split("## False positives", 1)[0]
    assert "| execution | t1059-shell | T1059.004 | — | ❌ 0/2 | 🛡️ 2/2 |" in coverage
    assert "| persistence | t1053-cron | T1053.003 | — | ❌ 0/2 | ✅ 2/2 |" in coverage
    assert "| impact | t1485-broken (invalid) | T1485 | — | ❌ 0/2 | ❌ 0/2 (invalid) |" in coverage
    control = text.split("## Control runs", 1)[1].split("## Coverage matrix", 1)[0]
    assert "| t1485-broken | attack | 2 | 0/2 | 0 | 0 | ❌ invalid |" in control
    assert "| t1059-shell | attack | 2 | 2/2 | 0 | 0 | ✅ valid |" in control
    assert "Invalid scenarios: t1485-broken." in control
    assert "| kubearmor | enforce | t1053-cron | 2 | 2 |" in text.split("### Scenario cleanups", 1)[1]


def test_unverified_enforcement_is_marked_invalid(tmp_path):
    text = write_report(build_enforce_results(tmp_path, verified=False)).read_text(encoding="utf-8")
    section = text.split("## Response effectiveness", 1)[1].split("## Overhead", 1)[0]
    assert "| kubearmor | invalid: 50.0% (1/2) |" in section
    assert "| execution | t1059-shell | T1059.004 | — | ❌ 0/2 | ✅ 2/2 † |" in text


def test_measured_operational_and_host_cpu(tmp_path):
    text = write_report(build_enforce_results(tmp_path)).read_text(encoding="utf-8")
    measured = text.split("### Measured operational metrics", 1)[1]
    assert "| kubearmor | enforce | 3 | 4 | 3.250s | 0.40 | 60.00 | 2.00 | 100.0% | 100.0% |" in measured
    resources = text.split("### Tool resource usage", 1)[1]
    assert "| 30.00 | 30.00 | +15.0 pp |" in resources
    assert "baseline median 15.00%" in resources
    latency = text.split("### Latency reference", 1)[1]
    assert "| kubearmor | enforce | 100.0% | 0 |" in latency


def test_render_report_handles_empty_inputs():
    text = render_report({}, {})
    assert text.startswith("# eBPF runtime detection benchmark: —")
    assert "None." in text
