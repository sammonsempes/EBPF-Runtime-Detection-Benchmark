from __future__ import annotations

import json
import re
import sys
import types
from dataclasses import replace
from pathlib import Path

import pytest

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter
from bench.config import Config, OverheadConfig
from bench.docker_backend import (
    Backend,
    ContainerRef,
    ExecResult,
    LineBuffer,
    StatsSampler,
    Targets,
    ToolStartError,
)
from bench.model import Alert, Scenario, ScenarioKind
from bench.orchestrator import Orchestrator, parse_action_at

VICTIM = ContainerRef(id="victim-id", name="bench-victim")
PRIVILEGED = ContainerRef(id="victim-priv-id", name="bench-victim-priv")
ATTACKER = ContainerRef(id="attacker-id", name="attacker")
WORKLOAD_HOST = ContainerRef(id="workload-id", name="bench-workload")


class FakeAdapter(ToolAdapter):
    name = "falco"
    version = "1.2.3"

    def __init__(self, ready_pattern: str = "ready", alerts_file: str | None = None) -> None:
        self.ready_pattern = ready_pattern
        self.alerts_file = alerts_file
        self.spec_calls: list[tuple[Path, str, Path]] = []

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        self.spec_calls.append((host_repo_root, profile, host_output_dir))
        return ContainerSpec(
            image="fake/falco:1.2.3",
            mounts=[Mount(str(host_repo_root / "tools" / "falco" / profile), "/etc/falco")],
            ready_pattern=self.ready_pattern,
            startup_timeout=1,
            alerts_file=self.alerts_file,
        )

    def parse(self, line: str, emitted_at: float) -> Alert | None:
        data = self.load_json(line)
        if data is None or "rule" not in data:
            return None
        if data["rule"] == "explode":
            raise RuntimeError("bad line")
        return Alert(tool=self.name, rule=data["rule"], emitted_at=emitted_at, container_name=data.get("container"), raw=data)


class FakeBackend(Backend):
    def __init__(
        self,
        interrupt_on_exec: bool = False,
        check_codes: dict[tuple[str, str], int] | None = None,
        cleanup_code: int = 0,
        extra_logs: list[str] | None = None,
    ) -> None:
        self.interrupt_on_exec = interrupt_on_exec
        self.check_codes = check_codes or {}
        self.cleanup_code = cleanup_code
        self.extra_logs = extra_logs or []
        self.current_tool = "none"
        self.url_waits: list[tuple[str, str, float]] = []
        self.events: list[str] = []
        self.specs: list[ContainerSpec] = []
        self.execs: list[tuple[str, list[str], dict[str, str], float]] = []
        self.stopped: list[str] = []
        self.tool_logs: LineBuffer | None = None
        self.counter = 0
        self.now = 1000.0

    def prepare(self) -> None:
        self.events.append("prepare")

    def start_targets(self) -> Targets:
        self.events.append("targets")
        return Targets(victim=VICTIM, victim_privileged=PRIVILEGED, attacker=ATTACKER)

    def start_workload_host(self) -> ContainerRef:
        self.events.append("workload-host")
        return WORKLOAD_HOST

    def start_tool(self, tool: str, profile: str, spec: ContainerSpec) -> ContainerRef:
        self.counter += 1
        self.specs.append(spec)
        self.events.append(f"tool:{tool}-{profile}")
        self.current_tool = f"{tool}-{profile}"
        return ContainerRef(id=f"tool-{self.counter}", name=f"bench-tool-{tool}-{profile}")

    def follow_logs(self, ref: ContainerRef) -> LineBuffer:
        buffer = LineBuffer()
        buffer.append(1.0, "booting")
        buffer.append(2.0, "engine ready")
        buffer.append(3.0, json.dumps({"rule": "explode"}))
        for line in self.extra_logs:
            buffer.append(4.0, line)
        self.tool_logs = buffer
        return buffer

    def wait_url(self, ref: ContainerRef, logs: LineBuffer, url: str, timeout: float) -> None:
        self.url_waits.append((ref.id, url, timeout))

    def tail_file(self, path: Path) -> LineBuffer:
        buffer = LineBuffer()
        buffer.append(5.0, json.dumps({"rule": "from-file"}))
        buffer.close()
        return buffer

    def wait_ready(self, ref: ContainerRef, logs: LineBuffer, pattern: str | None, timeout: float) -> None:
        if pattern and not logs.wait_for(pattern, 0):
            raise ToolStartError(f"ready pattern {pattern!r} not seen")

    def exec(self, ref: ContainerRef, command: list[str], environment: dict[str, str], timeout: float) -> ExecResult:
        self.execs.append((ref.id, command, environment, timeout))
        self.now += 10
        if command[0] == "sh":
            if self.interrupt_on_exec:
                raise KeyboardInterrupt
            scenario_id, script = command[1].split("/")[-2:]
            if script == "check.sh":
                return ExecResult(self.check_codes.get((self.current_tool, scenario_id), 0), "", self.now, self.now + 0.1)
            if script == "cleanup.sh":
                return ExecResult(self.cleanup_code, "cleanup output", self.now, self.now + 0.1)
            if self.tool_logs is not None and self.current_tool != "none":
                alert = {"rule": "hit", "marker": environment["BENCH_MARKER"]}
                self.tool_logs.append(self.now + 0.2, json.dumps(alert))
            return ExecResult(0, f"setup\nBENCH_ACTION {self.now + 0.1:.6f}\ndone", self.now, self.now + 0.5)
        return ExecResult(0, json.dumps({"name": command[0], "metrics": {"ops": 100.0}}), self.now, self.now + 1)

    def start_stats(self, ref: ContainerRef) -> StatsSampler:
        return StatsSampler(lambda: [])

    def stop(self, ref: ContainerRef) -> None:
        self.stopped.append(ref.id)
        if ref.id.startswith("tool-") and self.tool_logs is not None:
            self.tool_logs.close()
            self.current_tool = "none"

    def cleanup(self) -> None:
        self.events.append("cleanup")

    def host_info(self) -> dict:
        return {"kernel": "6.6.0", "cpus": 4}


def scenario(repo: Path, scenario_id: str, kind: ScenarioKind, requires: tuple[str, ...] = ()) -> Scenario:
    attack = kind is ScenarioKind.ATTACK
    return Scenario(
        id=scenario_id,
        name=scenario_id,
        kind=kind,
        description="test",
        path=repo / "scenarios" / scenario_id,
        tactic="privilege-escalation" if attack else None,
        technique="T1611" if attack else None,
        timeout=7,
        requires=requires,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "tools" / "falco" / "default").mkdir(parents=True)
    (root / "tools" / "falco" / "default" / "falco.yaml").write_text("rules: []\n")
    (root / "tools" / "falco" / "operational.yaml").write_text("deployment: easy\n")
    return root


@pytest.fixture
def scenarios(repo: Path) -> list[Scenario]:
    items = [
        scenario(repo, "t1611-escape", ScenarioKind.ATTACK, ("privileged",)),
        scenario(repo, "benign-ls", ScenarioKind.BENIGN),
    ]
    for item in items:
        item.path.mkdir(parents=True)
        for name in ("run.sh", "check.sh", "cleanup.sh"):
            (item.path / name).write_text("#!/bin/sh\nexit 0\n")
    return items


def make_config(**changes) -> Config:
    values = dict(
        tools=("falco", "tetragon"),
        profiles=("default", "tuned"),
        repetitions=2,
        grace_seconds=4,
        idle_seconds=1,
        overhead=OverheadConfig(duration_seconds=1, repetitions=2, workloads=("syscall",)),
        source="tools: [falco, tetragon]\n",
        control_scenarios=False,
    )
    values.update(changes)
    return Config(**values)


def factory_for(adapter: ToolAdapter):
    def factory(name: str) -> ToolAdapter:
        if name == "falco":
            return adapter
        raise ImportError(f"no adapter for {name}")

    return factory


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def make_orchestrator(repo, scenarios, backend, adapter, sleeps=None, **changes) -> Orchestrator:
    return Orchestrator(
        make_config(**changes),
        scenarios,
        backend,
        repo,
        host_repo_root=Path("/host/repo"),
        adapter_factory=factory_for(adapter),
        sleep=(sleeps.append if sleeps is not None else lambda seconds: None),
        log=lambda message: None,
        finalize=False,
        run_id="20260101T000000Z",
    )


def test_full_run(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend()
    adapter = FakeAdapter()
    sleeps: list[float] = []
    results = make_orchestrator(repo, scenarios, backend, adapter, sleeps).run()

    assert results == repo / "results" / "20260101T000000Z"
    assert backend.events[0] == "prepare"
    assert backend.events[-1] == "cleanup"
    assert adapter.spec_calls[0] == (
        Path("/host/repo"),
        "default",
        Path("/host/repo/results/20260101T000000Z/raw/falco-default"),
    )

    runs = read_jsonl(results / "runs.jsonl")
    assert len(runs) == 2 * 2 * 2
    assert {run["profile"] for run in runs} == {"default", "tuned"}
    assert all(re.fullmatch(r"[0-9a-f]{12}", run["marker"]) for run in runs)
    assert len({run["marker"] for run in runs}) == len(runs)
    by_id = {run["scenario_id"]: run["victim_container_id"] for run in runs}
    assert by_id == {"t1611-escape": PRIVILEGED.id, "benign-ls": VICTIM.id}
    first = runs[0]
    assert first["repetition"] == 0 and first["exit_code"] == 0 and first["output"].endswith("done")
    assert first["ended_at"] > first["started_at"]
    assert first["action_at"] == pytest.approx(first["started_at"] + 0.1)
    assert first["effect_achieved"] is True and first["check_exit_code"] == 0 and first["cleanup_exit_code"] == 0
    assert [run["scenario_id"] for run in runs[:4]] == ["t1611-escape", "benign-ls"] * 2

    scenario_execs = [call for call in backend.execs if call[1][0] == "sh"]
    assert [call[1][1] for call in scenario_execs[:3]] == [
        "/scenarios/t1611-escape/run.sh",
        "/scenarios/t1611-escape/check.sh",
        "/scenarios/t1611-escape/cleanup.sh",
    ]
    assert {call[0] for call in scenario_execs[:3]} == {PRIVILEGED.id}
    assert scenario_execs[0][2]["BENCH_ATTACKER"] == "attacker"
    assert scenario_execs[1][2] == scenario_execs[0][2]
    assert scenario_execs[0][3] == 7

    alerts = read_jsonl(results / "alerts" / "falco-default.jsonl")
    assert len(alerts) == 4
    assert all(alert["tool"] == "falco" and alert["rule"] == "hit" for alert in alerts)
    markers = {run["marker"] for run in runs if run["profile"] == "default"}
    assert {alert["raw"]["marker"] for alert in alerts} == markers
    assert not (results / "alerts" / "tetragon-default.jsonl").exists()
    assert (results / "raw" / "falco-default" / "container.log").read_text().count("\n") == 3 + 4

    workloads = read_jsonl(results / "workloads.jsonl")
    assert len(workloads) == 2 + 2 * 2
    assert [workload["tool"] for workload in workloads[:2]] == [None, None]
    assert {workload["profile"] for workload in workloads[2:]} == {"default", "tuned"}
    assert workloads[0]["metrics"] == {"ops": 100.0}

    assert sleeps.count(1) == 2 * 3
    assert sleeps.count(4) == 2
    assert sleeps.count(5.0) == 2

    metadata = json.loads((results / "metadata.json").read_text())
    assert metadata["status"] == "completed"
    assert metadata["host"] == {"kernel": "6.6.0", "cpus": 4}
    assert metadata["bench_yaml"] == "tools: [falco, tetragon]\n"
    assert metadata["config"]["repetitions"] == 2
    assert metadata["tools"]["falco"]["version"] == "1.2.3"
    assert len(metadata["tools"]["falco"]["config_sha256"]["default"]) == 64
    assert metadata["tools"]["falco"]["config_sha256"]["tuned"] is None
    assert metadata["tools"]["tetragon"]["available"] is False
    assert metadata["tools"]["falco"]["status"] == "ok"
    assert metadata["tools"]["tetragon"]["status"] == "failed"
    assert "adapter unavailable" in metadata["tools"]["tetragon"]["error"]
    assert metadata["operational"] == {"falco": {"deployment": "easy"}}
    assert metadata["scenarios"][0]["kind"] == "attack"
    assert metadata["scenarios"][0]["requires"] == ["privileged"]
    assert isinstance(metadata["scenarios"][0]["path"], str)
    assert metadata["baseline"]["status"] == "completed"
    deployments = metadata["deployments"]
    assert deployments["falco-default"]["status"] == "completed"
    assert deployments["falco-default"]["alerts"] == 4
    assert deployments["falco-default"]["parse_errors"] == 1
    assert deployments["falco-default"]["runs"] == 4
    assert deployments["falco-default"]["enforcement_verified"] is None
    assert deployments["falco-default"]["enforce"] is False
    assert deployments["falco-default"]["time_to_ready"] is not None
    assert deployments["falco-default"]["log_lines"] == 7
    assert deployments["falco-default"]["log_bytes"] > 0
    assert metadata["control"] == {"status": "skipped"}
    assert deployments["tetragon-default"]["status"] == "failed"
    assert "adapter unavailable" in deployments["tetragon-default"]["error"]
    assert set(backend.stopped) >= {"tool-1", "tool-2", VICTIM.id, PRIVILEGED.id, ATTACKER.id, WORKLOAD_HOST.id}


def test_tool_start_failure_does_not_abort(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend()
    results = make_orchestrator(repo, scenarios, backend, FakeAdapter(ready_pattern="never-printed")).run()
    metadata = json.loads((results / "metadata.json").read_text())
    assert metadata["status"] == "completed"
    deployment = metadata["deployments"]["falco-default"]
    assert deployment["status"] == "failed"
    assert "ToolStartError" in deployment["error"]
    assert metadata["deployments"]["falco-tuned"]["status"] == "failed"
    assert read_jsonl(results / "runs.jsonl") == []
    assert "tool-1" in backend.stopped and "tool-2" in backend.stopped
    assert backend.events[-1] == "cleanup"


def test_alerts_file_is_used_when_declared(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend()
    results = make_orchestrator(
        repo, scenarios, backend, FakeAdapter(alerts_file="events.json"), tools=("falco",), profiles=("default",)
    ).run()
    alerts = read_jsonl(results / "alerts" / "falco-default.jsonl")
    assert [alert["rule"] for alert in alerts] == ["from-file"]


def test_skip_overhead_and_unsupported_profile(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend()
    adapter = FakeAdapter()
    adapter.profiles = ("default",)
    results = make_orchestrator(
        repo,
        scenarios,
        backend,
        adapter,
        tools=("falco",),
        overhead=OverheadConfig(enabled=False),
    ).run()
    metadata = json.loads((results / "metadata.json").read_text())
    assert metadata["baseline"]["status"] == "skipped"
    assert metadata["deployments"]["falco-tuned"]["status"] == "skipped"
    assert read_jsonl(results / "workloads.jsonl") == []
    assert "workload-host" not in backend.events


def test_interrupt_cleans_up(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend(interrupt_on_exec=True)
    orchestrator = make_orchestrator(repo, scenarios, backend, FakeAdapter(), tools=("falco",))
    with pytest.raises(KeyboardInterrupt):
        orchestrator.run()
    metadata = json.loads((orchestrator.results_dir / "metadata.json").read_text())
    assert metadata["status"] == "interrupted"
    assert metadata["deployments"]["falco-default"]["status"] == "interrupted"
    assert backend.events[-1] == "cleanup"
    assert {"tool-1", VICTIM.id, PRIVILEGED.id, ATTACKER.id} <= set(backend.stopped)
    assert (orchestrator.results_dir / "alerts" / "falco-default.jsonl").exists()


def test_results_are_consumed_by_real_scoring(repo: Path, scenarios: list[Scenario]) -> None:
    scoring = pytest.importorskip("bench.scoring")
    orchestrator = make_orchestrator(repo, scenarios, FakeBackend(), FakeAdapter(), tools=("falco",))
    results = orchestrator.run()
    score = scoring.score_results(results, 4)
    falco = score["tools"]["falco"]
    assert falco["status"] == "ok"
    default = falco["profiles"]["default"]
    assert default["scenarios"]["t1611-escape"]["detected"] == 2
    assert default["scenarios"]["benign-ls"]["false_positives"] == 2
    assert default["overhead"]["available"] is True


class EnforcingAdapter(FakeAdapter):
    profiles = ("default", "enforce")

    def __init__(self, **kwargs) -> None:
        self.settle_seconds = kwargs.pop("settle_seconds", 5.0)
        self.ready_url = kwargs.pop("ready_url", None)
        super().__init__(**kwargs)

    def container_spec(self, host_repo_root: Path, profile: str, host_output_dir: Path) -> ContainerSpec:
        spec = super().container_spec(host_repo_root, profile, host_output_dir)
        return replace(spec, settle_seconds=self.settle_seconds, ready_url=self.ready_url)

    def is_enforcement(self, alert: Alert) -> bool:
        return alert.rule == "hit"

    def enforcement_check(self, log_lines: list[str]) -> bool | None:
        return True if any("ENFORCER ON" in line for line in log_lines) else None

    def confirmed_enforcements(self, log_lines: list[tuple[float, str]]) -> list[float]:
        return [stamp for stamp, line in log_lines if line.startswith("KILLED")]


def test_parse_action_at() -> None:
    assert parse_action_at("setup\nBENCH_ACTION 1700000000.123456789\nBENCH_ACTION 5\n") == pytest.approx(
        1700000000.123456789
    )
    assert parse_action_at("BENCH_ACTION 42\n") == 42.0
    assert parse_action_at("BENCH_ACTION 1700000000.%N\n") is None
    assert parse_action_at("no marker here") is None
    assert parse_action_at("") is None


def test_control_phase_runs_scenarios_without_tool(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend()
    results = make_orchestrator(
        repo,
        scenarios,
        backend,
        FakeAdapter(),
        tools=("falco",),
        profiles=("default",),
        overhead=OverheadConfig(enabled=False),
        control_scenarios=True,
    ).run()
    runs = read_jsonl(results / "runs.jsonl")
    control = [run for run in runs if run["tool"] == "none"]
    assert len(control) == 4
    assert {run["profile"] for run in control} == {"control"}
    assert all(run["effect_achieved"] is True for run in control)
    assert runs[:4] == control
    assert backend.events[:3] == ["prepare", "targets", "tool:falco-default"]
    assert {VICTIM.id, PRIVILEGED.id, ATTACKER.id} <= set(backend.stopped[:3])
    metadata = json.loads((results / "metadata.json").read_text())
    assert metadata["control"]["status"] == "completed"
    assert metadata["control"]["runs"] == 4
    assert "none" not in metadata["deployments"] and "none" not in metadata["tools"]
    assert not (results / "alerts" / "none-control.jsonl").exists()


def test_control_phase_disabled_or_without_scenarios(repo: Path, scenarios: list[Scenario]) -> None:
    results = make_orchestrator(
        repo, [], FakeBackend(), FakeAdapter(), tools=("falco",), profiles=("default",), control_scenarios=True
    ).run()
    assert json.loads((results / "metadata.json").read_text())["control"] == {"status": "skipped"}


def test_enforce_deployment_records_enforcement(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend(
        check_codes={("falco-enforce", "t1611-escape"): 1},
        extra_logs=["ENFORCER ON", "KILLED pid=42"],
    )
    results = make_orchestrator(
        repo,
        scenarios,
        backend,
        EnforcingAdapter(),
        tools=("falco",),
        profiles=("default", "enforce"),
        overhead=OverheadConfig(enabled=False),
    ).run()
    metadata = json.loads((results / "metadata.json").read_text())
    enforce = metadata["deployments"]["falco-enforce"]
    default = metadata["deployments"]["falco-default"]
    assert enforce["enforce"] is True and default["enforce"] is False
    assert enforce["enforcement_verified"] is True
    assert default["enforcement_verified"] is None
    assert enforce["confirmed_enforcements"] == [4.0]
    assert enforce["enforcement_alerts"] == 4
    alerts = read_jsonl(results / "alerts" / "falco-enforce.jsonl")
    assert {alert["action"] for alert in alerts} == {"enforce"}
    runs = [run for run in read_jsonl(results / "runs.jsonl") if run["profile"] == "enforce"]
    effects = {(run["scenario_id"], run["effect_achieved"], run["check_exit_code"]) for run in runs}
    assert effects == {("t1611-escape", False, 1), ("benign-ls", True, 0)}
    assert backend.events.count("targets") == 2


def test_unexpected_check_code_and_cleanup_failure(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend(check_codes={("falco-default", "benign-ls"): 124}, cleanup_code=3)
    results = make_orchestrator(
        repo, scenarios, backend, FakeAdapter(), tools=("falco",), profiles=("default",), overhead=OverheadConfig(enabled=False)
    ).run()
    runs = read_jsonl(results / "runs.jsonl")
    benign = [run for run in runs if run["scenario_id"] == "benign-ls"]
    assert all(run["effect_achieved"] is None and run["check_exit_code"] == 124 for run in benign)
    assert all(run["cleanup_exit_code"] == 3 for run in runs)
    deployment = json.loads((results / "metadata.json").read_text())["deployments"]["falco-default"]
    assert deployment["status"] == "completed"
    assert deployment["cleanup_failures"] == 4
    assert any(error.startswith("cleanup t1611-escape #0 exit=3") for error in deployment["errors"])


def test_missing_check_script_leaves_effect_unknown(repo: Path) -> None:
    bare = [scenario(repo, "t1611-bare", ScenarioKind.ATTACK)]
    backend = FakeBackend()
    results = make_orchestrator(
        repo, bare, backend, FakeAdapter(), tools=("falco",), profiles=("default",), overhead=OverheadConfig(enabled=False)
    ).run()
    runs = read_jsonl(results / "runs.jsonl")
    assert all(run["effect_achieved"] is None and run["check_exit_code"] is None for run in runs)
    assert all(run["cleanup_exit_code"] is None for run in runs)
    assert [call[1][1] for call in backend.execs if call[1][0] == "sh"] == ["/scenarios/t1611-bare/run.sh"] * 2


def test_ready_url_and_settle(repo: Path, scenarios: list[Scenario]) -> None:
    backend = FakeBackend()
    sleeps: list[float] = []
    adapter = EnforcingAdapter(settle_seconds=0.0, ready_url="http://127.0.0.1:3366/healthz")
    make_orchestrator(
        repo, scenarios, backend, adapter, sleeps, tools=("falco",), profiles=("default",), overhead=OverheadConfig(enabled=False)
    ).run()
    assert [(ref, url) for ref, url, _ in backend.url_waits] == [("tool-1", "http://127.0.0.1:3366/healthz")]
    assert backend.url_waits[0][2] == pytest.approx(1.0)
    assert 0.0 not in sleeps and 5.0 not in sleeps


def test_enforce_results_are_scored(repo: Path, scenarios: list[Scenario]) -> None:
    scoring = pytest.importorskip("bench.scoring")
    backend = FakeBackend(
        check_codes={("falco-enforce", "t1611-escape"): 1, ("falco-enforce", "benign-ls"): 1},
        extra_logs=["ENFORCER ON"],
    )
    results = make_orchestrator(
        repo,
        scenarios,
        backend,
        EnforcingAdapter(),
        tools=("falco",),
        profiles=("default", "enforce"),
        overhead=OverheadConfig(enabled=False),
        control_scenarios=True,
    ).run()
    score = scoring.score_results(results, 4)
    assert score["control"]["available"] is True
    assert score["control"]["valid_scenarios"] == ["benign-ls", "t1611-escape"]
    assert "none" not in score["tools"]
    enforce = score["tools"]["falco"]["profiles"]["enforce"]
    response = enforce["response"]
    assert response["enforcement_verified"] is True and response["valid"] is True
    assert response["prevention_rate"] == 1.0
    assert response["prevented"] == ["t1611-escape"]
    assert response["prevented_without_alert"] == 0
    assert response["collateral_damage"] == 1
    assert response["collateral_damage_scenarios"] == ["benign-ls"]
    assert response["response_latency_median"] == pytest.approx(0.1)
    assert enforce["scenarios"]["t1611-escape"]["latencies"] == [pytest.approx(0.1)] * 2
    assert enforce["summary"]["action_timestamp_share"] == 1.0
    default = score["tools"]["falco"]["profiles"]["default"]
    assert "response" not in default and default["enforce"] is False


def test_finalize_calls_scoring_and_report(
    repo: Path, scenarios: list[Scenario], monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple] = []
    scoring = types.ModuleType("bench.scoring")
    scoring.score_results = lambda results_dir, grace_seconds: calls.append(("score", results_dir, grace_seconds)) or {}
    report = types.ModuleType("bench.report")
    report.write_report = lambda results_dir: calls.append(("report", results_dir)) or results_dir / "report.md"
    monkeypatch.setitem(sys.modules, "bench.scoring", scoring)
    monkeypatch.setitem(sys.modules, "bench.report", report)
    orchestrator = make_orchestrator(repo, scenarios, FakeBackend(), FakeAdapter(), tools=("falco",))
    orchestrator.finalize = True
    results = orchestrator.run()
    assert calls == [("score", results, 4), ("report", results)]
