from __future__ import annotations

import json
import statistics
from typing import Any

from bench.docker_backend import Backend, ContainerRef
from bench.model import WorkloadResult

WORKLOAD_BIN_DIR = "/opt/bench/bin"
WORKLOAD_TIMEOUT_MARGIN = 120.0


class WorkloadError(RuntimeError):
    pass


def workload_command(name: str, duration: float) -> list[str]:
    return [f"{WORKLOAD_BIN_DIR}/{name}", "--duration", f"{duration:g}"]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_workload_output(output: str) -> dict[str, float]:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            document = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(document, dict) and isinstance(document.get("metrics"), dict):
            return {str(key): float(value) for key, value in document["metrics"].items() if _is_number(value)}
    raise WorkloadError(f"no workload JSON line found in output: {output[-500:]!r}")


def run_workload(
    backend: Backend,
    host: ContainerRef,
    name: str,
    duration: float,
    repetition: int,
    tool: str | None = None,
    profile: str | None = None,
    tool_container: ContainerRef | None = None,
) -> WorkloadResult:
    start_host_stats = getattr(backend, "start_host_stats", None)
    host_sampler = start_host_stats() if start_host_stats is not None else None
    sampler = backend.start_stats(tool_container) if tool_container is not None else None
    try:
        result = backend.exec(host, workload_command(name, duration), {}, duration + WORKLOAD_TIMEOUT_MARGIN)
    finally:
        cpu, memory = sampler.stop() if sampler is not None else ([], [])
        host_cpu = host_sampler.stop() if host_sampler is not None else []
    if result.exit_code != 0:
        raise WorkloadError(f"workload {name} exited with code {result.exit_code}: {result.output[-500:]!r}")
    return WorkloadResult(
        name=name,
        tool=tool,
        profile=profile,
        repetition=repetition,
        metrics=parse_workload_output(result.output),
        tool_cpu_percent=cpu,
        tool_memory_bytes=memory,
        host_cpu_percent=host_cpu,
    )


def median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def relative_delta(baseline: float | None, measured: float | None) -> float | None:
    if baseline is None or measured is None or baseline == 0:
        return None
    return (measured - baseline) / baseline


def summarize(values: list[float]) -> dict[str, float | int | None]:
    return {"median": median(values), "max": max(values) if values else None, "samples": len(values)}


def compute_overhead(baseline: list[WorkloadResult], measured: list[WorkloadResult]) -> dict:
    overhead: dict[str, Any] = {}
    for name in sorted({result.name for result in measured}):
        reference = [result for result in baseline if result.name == name]
        runs = [result for result in measured if result.name == name]
        metric_names = sorted({metric for result in runs + reference for metric in result.metrics})
        metrics = {}
        for metric in metric_names:
            base = median([result.metrics[metric] for result in reference if metric in result.metrics])
            value = median([result.metrics[metric] for result in runs if metric in result.metrics])
            metrics[metric] = {"baseline": base, "measured": value, "delta": relative_delta(base, value)}
        overhead[name] = {
            "metrics": metrics,
            "repetitions": {"baseline": len(reference), "measured": len(runs)},
            "tool_cpu_percent": summarize([sample for result in runs for sample in result.tool_cpu_percent]),
            "tool_memory_bytes": summarize([sample for result in runs for sample in result.tool_memory_bytes]),
            "host_cpu_percent": summarize([sample for result in runs for sample in result.host_cpu_percent]),
        }
    return overhead
