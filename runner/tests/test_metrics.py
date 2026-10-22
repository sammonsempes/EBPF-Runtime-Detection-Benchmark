from __future__ import annotations

import json

import pytest

from bench.docker_backend import ContainerRef, ExecResult, StatsSampler
from bench.metrics import (
    WorkloadError,
    compute_overhead,
    parse_workload_output,
    relative_delta,
    run_workload,
    workload_command,
)
from bench.model import WorkloadResult

HOST = ContainerRef(id="host-id", name="bench-workload")
TOOL = ContainerRef(id="tool-id", name="bench-tool")


def stats(cpu: int, previous_cpu: int, system: int, previous_system: int, usage: int, inactive: int) -> dict:
    return {
        "cpu_stats": {"cpu_usage": {"total_usage": cpu}, "system_cpu_usage": system, "online_cpus": 2},
        "precpu_stats": {"cpu_usage": {"total_usage": previous_cpu}, "system_cpu_usage": previous_system},
        "memory_stats": {"usage": usage, "stats": {"inactive_file": inactive}},
    }


class FakeBackend:
    def __init__(self, output: str, exit_code: int = 0) -> None:
        self.output = output
        self.exit_code = exit_code
        self.commands: list[tuple[str, list[str], float]] = []

    def start_stats(self, ref: ContainerRef) -> StatsSampler:
        return StatsSampler(lambda: [stats(200, 100, 2000, 1000, 1000, 200)])

    def exec(self, ref: ContainerRef, command: list[str], environment: dict, timeout: float) -> ExecResult:
        self.commands.append((ref.id, command, timeout))
        return ExecResult(self.exit_code, self.output, 1.0, 2.0)


def result(name: str, metrics: dict, cpu: list[float] = (), memory: list[float] = (), tool: str | None = None):
    return WorkloadResult(name, tool, None, 0, metrics, list(cpu), list(memory))


def test_workload_command() -> None:
    assert workload_command("syscall", 30) == ["/opt/bench/bin/syscall", "--duration", "30"]
    assert workload_command("exec", 2.5) == ["/opt/bench/bin/exec", "--duration", "2.5"]


def test_parse_workload_output_takes_json_line() -> None:
    line = json.dumps({"name": "syscall", "metrics": {"getpid_p50_ns": 120, "flag": True, "label": "x"}})
    assert parse_workload_output(f"warming up\n{line}\n") == {"getpid_p50_ns": 120.0}


@pytest.mark.parametrize("output", ["", "nothing here", '{"name": "x"}', "{broken"])
def test_parse_workload_output_rejects(output: str) -> None:
    with pytest.raises(WorkloadError):
        parse_workload_output(output)


def test_run_workload_with_tool_samples_stats() -> None:
    backend = FakeBackend(json.dumps({"name": "syscall", "metrics": {"ops": 10.0}}))
    outcome = run_workload(backend, HOST, "syscall", 5, 1, tool="falco", profile="default", tool_container=TOOL)
    assert outcome.metrics == {"ops": 10.0}
    assert (outcome.tool, outcome.profile, outcome.repetition) == ("falco", "default", 1)
    assert outcome.tool_cpu_percent == [20.0]
    assert outcome.tool_memory_bytes == [800.0]
    assert backend.commands[0][0] == "host-id"
    assert backend.commands[0][2] > 5


def test_run_workload_baseline_has_no_stats() -> None:
    backend = FakeBackend(json.dumps({"name": "exec", "metrics": {"ops": 3}}))
    outcome = run_workload(backend, HOST, "exec", 5, 0)
    assert outcome.tool is None
    assert outcome.tool_cpu_percent == []


class FakeHostSampler:
    def __init__(self) -> None:
        self.stopped = False

    def stop(self) -> list[float]:
        self.stopped = True
        return [12.5, 40.0]


class HostStatsBackend(FakeBackend):
    def __init__(self, output: str) -> None:
        super().__init__(output)
        self.sampler = FakeHostSampler()

    def start_host_stats(self) -> FakeHostSampler:
        return self.sampler


def test_run_workload_samples_host_cpu_for_baseline_and_tool() -> None:
    output = json.dumps({"name": "exec", "metrics": {"ops": 3}})
    backend = HostStatsBackend(output)
    outcome = run_workload(backend, HOST, "exec", 5, 0)
    assert outcome.host_cpu_percent == [12.5, 40.0]
    assert backend.sampler.stopped
    backend = HostStatsBackend(output)
    outcome = run_workload(backend, HOST, "exec", 5, 0, tool="falco", profile="default", tool_container=TOOL)
    assert outcome.host_cpu_percent == [12.5, 40.0]
    assert outcome.tool_cpu_percent == [20.0]


def test_run_workload_without_host_sampler() -> None:
    outcome = run_workload(FakeBackend(json.dumps({"name": "exec", "metrics": {"ops": 3}})), HOST, "exec", 5, 0)
    assert outcome.host_cpu_percent == []


def test_run_workload_failure() -> None:
    with pytest.raises(WorkloadError, match="exited with code 1"):
        run_workload(FakeBackend("boom", exit_code=1), HOST, "exec", 5, 0)


def test_relative_delta() -> None:
    assert relative_delta(100.0, 110.0) == pytest.approx(0.1)
    assert relative_delta(0.0, 1.0) is None
    assert relative_delta(None, 1.0) is None


def test_compute_overhead_medians() -> None:
    baseline = [result("syscall", {"lat": value, "ops": 1000.0}) for value in (100.0, 110.0, 90.0)]
    measured = [
        result("syscall", {"lat": 120.0, "ops": 900.0}, cpu=[5.0, 7.0], memory=[100.0], tool="falco"),
        result("syscall", {"lat": 130.0, "ops": 800.0}, cpu=[9.0], memory=[300.0, 200.0], tool="falco"),
        result("syscall", {"lat": 110.0, "ops": 850.0}, cpu=[], memory=[], tool="falco"),
    ]
    overhead = compute_overhead(baseline, measured)
    syscall = overhead["syscall"]
    assert syscall["metrics"]["lat"] == {"baseline": 100.0, "measured": 120.0, "delta": pytest.approx(0.2)}
    assert syscall["metrics"]["ops"]["delta"] == pytest.approx(-0.15)
    assert syscall["tool_cpu_percent"] == {"median": 7.0, "max": 9.0, "samples": 3}
    assert syscall["tool_memory_bytes"] == {"median": 200.0, "max": 300.0, "samples": 3}
    assert syscall["repetitions"] == {"baseline": 3, "measured": 3}


def test_compute_overhead_missing_baseline() -> None:
    overhead = compute_overhead([], [result("fileio", {"mbps": 10.0})])
    assert overhead["fileio"]["metrics"]["mbps"] == {"baseline": None, "measured": 10.0, "delta": None}
    assert overhead["fileio"]["tool_cpu_percent"]["median"] is None
