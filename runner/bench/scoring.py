from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Iterable

from bench.config import CONTROL_PROFILE, CONTROL_TOOL, ENFORCE_PROFILES
from bench.model import Alert, ScenarioRun, WorkloadResult

EVENT_SLACK_SECONDS = 1.0
PREVENTED = "prevented"
INVALID = "invalid"
ACTION_REFERENCE = "action"
START_REFERENCE = "start"
UNPRIVILEGED_VICTIM = "bench-victim"
PRIVILEGED_VICTIM = "bench-victim-priv"
VICTIM_NAMES = (UNPRIVILEGED_VICTIM, PRIVILEGED_VICTIM)
MIN_ID_PREFIX = 12
ID_SCHEMES = ("docker://", "containerd://", "cri-o://")
HIGHER_IS_WORSE_SUFFIXES = ("_ns", "_us")
LOWER_IS_WORSE_SUFFIXES = ("_per_sec",)
HIGHER_IS_WORSE = "higher_is_worse"
LOWER_IS_WORSE = "lower_is_worse"
MIB = 1024.0 * 1024.0
PRECISION = 6
DETECTED = "detected"
PARTIAL = "partial"
MISSED = "missed"
NOT_RUN = "not_run"

RunKey = tuple[str, int, str, float]


@dataclass
class AttributionResult:
    by_run: dict[RunKey, list[Alert]] = field(default_factory=dict)
    total: int = 0
    attributed: int = 0
    background_noise: int = 0
    unattributed_in_window: int = 0
    non_victim: int = 0


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def build(cls: type, data: dict[str, Any]) -> Any:
    names = {item.name for item in fields(cls)}
    try:
        return cls(**{key: value for key, value in data.items() if key in names})
    except TypeError:
        return None


def build_all(cls: type, records: Iterable[dict[str, Any]]) -> list[Any]:
    return [item for item in (build(cls, record) for record in records) if item is not None]


def rounded(value: float | None) -> float | None:
    return None if value is None else round(float(value), PRECISION)


def median(values: Iterable[float]) -> float | None:
    items = list(values)
    return rounded(statistics.median(items)) if items else None


def percentile(values: Iterable[float], q: float) -> float | None:
    ordered = sorted(values)
    if not ordered:
        return None
    rank = (len(ordered) - 1) * q / 100.0
    low = math.floor(rank)
    high = math.ceil(rank)
    return rounded(ordered[low] + (ordered[high] - ordered[low]) * (rank - low))


def ratio(numerator: float, denominator: float) -> float | None:
    return rounded(numerator / denominator) if denominator else None


def normalize_id(value: Any) -> str:
    text = str(value or "").strip().lower()
    for scheme in ID_SCHEMES:
        if text.startswith(scheme):
            text = text[len(scheme):]
    return text


def normalize_name(value: Any) -> str:
    return str(value or "").strip().lstrip("/")


def id_matches(alert_id: Any, victim_id: Any) -> bool:
    left = normalize_id(alert_id)
    right = normalize_id(victim_id)
    if len(left) < MIN_ID_PREFIX or len(right) < MIN_ID_PREFIX:
        return False
    return left.startswith(right) or right.startswith(left)


def name_matches(alert_name: Any, victim_name: str | None) -> bool:
    name = normalize_name(alert_name)
    if not name:
        return False
    if victim_name:
        return name == victim_name
    return name in VICTIM_NAMES


def marker_in_alert(alert: Alert, marker: str) -> bool:
    if not marker:
        return False
    serialized = json.dumps(alert.raw, sort_keys=True, default=str, ensure_ascii=False)
    return marker in serialized


def in_window(alert: Alert, run: ScenarioRun, grace_seconds: float) -> bool:
    return run.started_at <= alert.emitted_at <= run.ended_at + grace_seconds


def after_run(alert: Alert, run: ScenarioRun) -> bool:
    return is_number(alert.event_at) and alert.event_at > run.ended_at + EVENT_SLACK_SECONDS


def identifies(alert: Alert, run: ScenarioRun, victim_name: str | None = None) -> bool:
    return (
        id_matches(alert.container_id, run.victim_container_id)
        or name_matches(alert.container_name, victim_name)
        or marker_in_alert(alert, run.marker)
    )


def run_order(run: ScenarioRun) -> tuple[float, str, int, str]:
    return (run.started_at, run.scenario_id, run.repetition, run.marker)


def run_key(run: ScenarioRun) -> RunKey:
    return (run.scenario_id, run.repetition, run.marker, run.started_at)


def attribute(
    alert: Alert,
    runs: Iterable[ScenarioRun],
    grace_seconds: float,
    victim_names: dict[str, str] | None = None,
) -> ScenarioRun | None:
    names = victim_names or {}
    for run in sorted(runs, key=run_order):
        if (
            in_window(alert, run, grace_seconds)
            and not after_run(alert, run)
            and identifies(alert, run, names.get(run.scenario_id))
        ):
            return run
    return None


def is_victim_alert(alert: Alert, runs: Iterable[ScenarioRun]) -> bool:
    if name_matches(alert.container_name, None):
        return True
    return any(id_matches(alert.container_id, run.victim_container_id) for run in runs)


def attribute_all(
    alerts: Iterable[Alert],
    runs: list[ScenarioRun],
    grace_seconds: float,
    victim_names: dict[str, str] | None = None,
) -> AttributionResult:
    ordered = sorted(runs, key=run_order)
    result = AttributionResult()
    for alert in sorted(alerts, key=lambda item: (item.emitted_at, str(item.rule))):
        result.total += 1
        run = attribute(alert, ordered, grace_seconds, victim_names)
        if run is not None:
            result.attributed += 1
            result.by_run.setdefault(run_key(run), []).append(alert)
        elif not is_victim_alert(alert, ordered):
            result.non_victim += 1
        elif any(in_window(alert, candidate, grace_seconds) for candidate in ordered):
            result.unattributed_in_window += 1
        else:
            result.background_noise += 1
    return result


def classify(detected: int, total: int) -> str:
    if total == 0:
        return NOT_RUN
    if detected * 2 > total:
        return DETECTED
    if detected > 0:
        return PARTIAL
    return MISSED


def normalize_kind(value: Any) -> str:
    text = str(getattr(value, "value", value) or "").lower()
    return "benign" if "benign" in text else "attack"


def victim_name_for(requires: Iterable[str]) -> str:
    return PRIVILEGED_VICTIM if "privileged" in set(requires or ()) else UNPRIVILEGED_VICTIM


def scenario_catalog(metadata: dict[str, Any], runs: Iterable[ScenarioRun]) -> dict[str, dict[str, Any]]:
    catalog: dict[str, dict[str, Any]] = {}
    for item in metadata.get("scenarios") or []:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        requires = item.get("requires") or []
        catalog[str(item["id"])] = {
            "name": item.get("name") or item["id"],
            "kind": normalize_kind(item.get("kind")),
            "tactic": item.get("tactic"),
            "technique": item.get("technique"),
            "requires": sorted(str(value) for value in requires),
        }
    for run in runs:
        catalog.setdefault(
            run.scenario_id,
            {"name": run.scenario_id, "kind": "attack", "tactic": None, "technique": None, "requires": []},
        )
    return dict(sorted(catalog.items()))


def latency_reference(run: ScenarioRun) -> tuple[float, str]:
    if is_number(run.action_at):
        return float(run.action_at), ACTION_REFERENCE
    return run.started_at, START_REFERENCE


def effect_value(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def majority(count: int, total: int) -> bool:
    return total > 0 and count * 2 > total


def response_entry(
    info: dict[str, Any],
    repetitions: list[dict[str, Any]],
    valid: bool | None,
    status: str,
) -> dict[str, Any]:
    total = len(repetitions)
    blocked = sum(1 for item in repetitions if item["effect_achieved"] is False)
    known = sum(1 for item in repetitions if item["effect_achieved"] is not None)
    latencies = [item["response_latency"] for item in repetitions if item["response_latency"] is not None]
    entry: dict[str, Any] = {
        "valid": valid,
        "effect_achieved": sum(1 for item in repetitions if item["effect_achieved"] is True),
        "effect_not_achieved": blocked,
        "effect_unknown": total - known,
        "enforcement_alerts": sum(item["enforcement_alerts"] for item in repetitions),
        "confirmed_enforcements": sum(item["confirmed_enforcements"] for item in repetitions),
        "response_latencies": latencies,
        "response_latency_median": median(latencies),
    }
    if info["kind"] == "benign":
        entry["collateral_damage"] = valid is not False and majority(blocked, total)
        return entry
    prevented = sum(1 for item in repetitions if item["prevented"])
    entry.update(
        prevented=prevented,
        prevention_rate=ratio(prevented, known) if valid is not False else None,
        detected_not_prevented=sum(1 for item in repetitions if item["detected"] and item["effect_achieved"] is True),
        prevented_without_alert=sum(1 for item in repetitions if item["prevented"] and not item["detected"]),
    )
    if valid is False:
        entry["status"] = INVALID
    elif majority(prevented, total):
        entry["status"] = PREVENTED
    else:
        entry["status"] = status
    return entry


def score_scenario(
    info: dict[str, Any],
    runs: list[ScenarioRun],
    attributed: dict[RunKey, list[Alert]],
    valid: bool | None = None,
    enforce: bool = False,
    confirmations: Iterable[float] = (),
    grace_seconds: float = 0.0,
) -> dict[str, Any]:
    repetitions = []
    latencies = []
    rules: set[str] = set()
    alert_count = 0
    detected = 0
    confirmed_at = sorted(confirmations)
    for run in sorted(runs, key=lambda item: (item.repetition, item.started_at, item.marker)):
        hits = attributed.get(run_key(run), [])
        reference, reference_kind = latency_reference(run)
        latency = rounded(min(alert.emitted_at for alert in hits) - reference) if hits else None
        run_rules = sorted({str(alert.rule) for alert in hits})
        if hits:
            detected += 1
            latencies.append(latency)
        rules.update(run_rules)
        alert_count += len(hits)
        effect = effect_value(run.effect_achieved)
        item = {
            "repetition": run.repetition,
            "marker": run.marker,
            "exit_code": run.exit_code,
            "detected": bool(hits),
            "alerts": len(hits),
            "latency": latency,
            "latency_reference": reference_kind,
            "rules": run_rules,
            "effect_achieved": effect,
            "check_exit_code": run.check_exit_code,
            "cleanup_exit_code": run.cleanup_exit_code,
        }
        if enforce:
            enforcement = [alert for alert in hits if alert.action]
            item["enforcement_alerts"] = len(enforcement)
            item["response_latency"] = (
                rounded(min(alert.emitted_at for alert in enforcement) - reference) if enforcement else None
            )
            item["confirmed_enforcements"] = sum(
                1 for value in confirmed_at if run.started_at <= value <= run.ended_at + grace_seconds
            )
            item["prevented"] = info["kind"] == "attack" and valid is not False and effect is False
        repetitions.append(item)
    total = len(repetitions)
    entry = {
        "name": info["name"],
        "kind": info["kind"],
        "tactic": info["tactic"],
        "technique": info["technique"],
        "repetitions": total,
        "detected": detected,
        "detection_rate": ratio(detected, total),
        "status": classify(detected, total),
        "latencies": latencies,
        "latency_median": median(latencies),
        "latency_p95": percentile(latencies, 95),
        "rules": sorted(rules),
        "alerts": alert_count,
        "failed_executions": sum(1 for item in repetitions if item["exit_code"] != 0),
        "valid": valid,
        "action_timestamps": sum(1 for item in repetitions if item["latency_reference"] == ACTION_REFERENCE),
        "early_alerts": sum(1 for value in latencies if value < 0),
        "effect_achieved": sum(1 for item in repetitions if item["effect_achieved"] is True),
        "runs": repetitions,
    }
    if info["kind"] == "benign":
        entry["false_positives"] = detected
    if enforce:
        entry["response"] = response_entry(info, repetitions, valid, entry["status"])
    return entry


def tactic_coverage(scenarios: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    coverage: dict[str, dict[str, Any]] = {}
    for entry in scenarios.values():
        if entry["kind"] != "attack" or entry["status"] == NOT_RUN:
            continue
        tactic = entry["tactic"] or "unknown"
        bucket = coverage.setdefault(tactic, {"scenarios": 0, DETECTED: 0, PARTIAL: 0, MISSED: 0})
        bucket["scenarios"] += 1
        bucket[entry["status"]] += 1
    for bucket in coverage.values():
        bucket["coverage"] = ratio(bucket[DETECTED], bucket["scenarios"])
    return dict(sorted(coverage.items()))


def summarize(scenarios: dict[str, dict[str, Any]], attribution: AttributionResult) -> dict[str, Any]:
    attack = [entry for entry in scenarios.values() if entry["kind"] == "attack" and entry["repetitions"]]
    benign = [entry for entry in scenarios.values() if entry["kind"] == "benign" and entry["repetitions"]]
    true_positives = sum(entry["detected"] for entry in attack)
    attack_runs = sum(entry["repetitions"] for entry in attack)
    false_positives = sum(entry["detected"] for entry in benign)
    benign_runs = sum(entry["repetitions"] for entry in benign)
    detected_scenarios = sum(1 for entry in attack if entry["status"] == DETECTED)
    latencies = [value for entry in attack for value in entry["latencies"]]
    all_runs = [item for entry in scenarios.values() for item in entry["runs"]]
    return {
        "invalid_attack_scenarios": sorted(
            scenario_id
            for scenario_id, entry in scenarios.items()
            if entry["kind"] == "attack" and entry["repetitions"] and entry["valid"] is False
        ),
        "action_timestamp_share": ratio(
            sum(1 for item in all_runs if item["latency_reference"] == ACTION_REFERENCE), len(all_runs)
        ),
        "early_alerts": sum(entry["early_alerts"] for entry in attack),
        "attack_scenarios": len(attack),
        "attack_runs": attack_runs,
        "detected_scenarios": detected_scenarios,
        "partial_scenarios": sum(1 for entry in attack if entry["status"] == PARTIAL),
        "missed_scenarios": sum(1 for entry in attack if entry["status"] == MISSED),
        "true_positives": true_positives,
        "false_negatives": attack_runs - true_positives,
        "recall": ratio(detected_scenarios, len(attack)),
        "detection_rate": ratio(true_positives, attack_runs),
        "benign_scenarios": len(benign),
        "benign_runs": benign_runs,
        "false_positives": false_positives,
        "false_positive_scenarios": sum(1 for entry in benign if entry["detected"]),
        "false_positive_rate": ratio(false_positives, benign_runs),
        "latency_median": median(latencies),
        "latency_p95": percentile(latencies, 95),
        "alerts_total": attribution.total,
        "alerts_attributed": attribution.attributed,
        "background_noise": attribution.background_noise,
        "unattributed_in_window": attribution.unattributed_in_window,
        "non_victim_alerts": attribution.non_victim,
        "failed_executions": sum(entry["failed_executions"] for entry in scenarios.values()),
        "coverage": tactic_coverage(scenarios),
    }


def summarize_response(
    scenarios: dict[str, dict[str, Any]],
    deployment: dict[str, Any],
    control_available: bool,
) -> dict[str, Any]:
    run_entries = {key: entry for key, entry in scenarios.items() if entry["repetitions"] and "response" in entry}
    attack = {key: entry for key, entry in run_entries.items() if entry["kind"] == "attack"}
    benign = {key: entry for key, entry in run_entries.items() if entry["kind"] == "benign"}
    valid_attack = {key: entry for key, entry in attack.items() if entry["valid"] is not False}
    valid_benign = {key: entry for key, entry in benign.items() if entry["valid"] is not False}
    prevented = sorted(key for key, entry in valid_attack.items() if entry["response"]["status"] == PREVENTED)
    collateral = sorted(key for key, entry in valid_benign.items() if entry["response"]["collateral_damage"])
    latencies = [value for entry in attack.values() for value in entry["response"]["response_latencies"]]
    verified = deployment.get("enforcement_verified")
    verified = verified if isinstance(verified, bool) else None
    confirmed = deployment.get("confirmed_enforcements")
    summary = {
        "enforcement_verified": verified,
        "valid": verified is not False,
        "invalid_reason": "enforcement not verified for this deployment" if verified is False else None,
        "control_available": control_available,
        "valid_attack_scenarios": len(valid_attack),
        "invalid_scenarios": sorted(key for key, entry in run_entries.items() if entry["valid"] is False),
        "prevented_scenarios": len(prevented),
        "prevented": prevented,
        "prevention_rate": ratio(len(prevented), len(valid_attack)),
        "prevented_runs": sum(entry["response"]["prevented"] for entry in valid_attack.values()),
        "detected_not_prevented": sum(entry["response"]["detected_not_prevented"] for entry in valid_attack.values()),
        "detected_not_prevented_scenarios": sorted(
            key for key, entry in valid_attack.items() if entry["response"]["status"] in (DETECTED, PARTIAL)
        ),
        "prevented_without_alert": sum(
            entry["response"]["prevented_without_alert"] for entry in valid_attack.values()
        ),
        "prevented_without_alert_scenarios": sorted(
            key for key, entry in valid_attack.items() if entry["response"]["prevented_without_alert"]
        ),
        "valid_benign_scenarios": len(valid_benign),
        "collateral_damage": len(collateral),
        "collateral_damage_scenarios": collateral,
        "collateral_damage_rate": ratio(len(collateral), len(valid_benign)),
        "response_latency_median": median(latencies),
        "response_latency_p95": percentile(latencies, 95),
        "enforcement_alerts": int(deployment.get("enforcement_alerts") or 0),
        "confirmed_enforcements": len(confirmed) if isinstance(confirmed, list) else 0,
    }
    return summary


def score_control(catalog: dict[str, dict[str, Any]], runs: list[ScenarioRun], metadata: dict[str, Any]) -> dict:
    by_scenario: dict[str, list[ScenarioRun]] = {}
    for run in runs:
        by_scenario.setdefault(run.scenario_id, []).append(run)
    scenarios = {}
    for scenario_id, info in catalog.items():
        items = by_scenario.get(scenario_id, [])
        achieved = sum(1 for run in items if effect_value(run.effect_achieved) is True)
        not_achieved = sum(1 for run in items if effect_value(run.effect_achieved) is False)
        unknown = len(items) - achieved - not_achieved
        valid = None if not items or unknown == len(items) else majority(achieved, len(items))
        scenarios[scenario_id] = {
            "kind": info["kind"],
            "repetitions": len(items),
            "effect_achieved": achieved,
            "effect_not_achieved": not_achieved,
            "effect_unknown": unknown,
            "valid": valid,
            "failed_executions": sum(1 for run in items if run.exit_code != 0),
            "action_timestamps": sum(1 for run in items if is_number(run.action_at)),
        }
    control_meta = metadata.get("control") if isinstance(metadata.get("control"), dict) else {}
    return {
        "available": bool(runs),
        "status": control_meta.get("status") or ("completed" if runs else "skipped"),
        "scenarios": scenarios,
        "valid_scenarios": sorted(key for key, entry in scenarios.items() if entry["valid"] is True),
        "invalid_scenarios": sorted(key for key, entry in scenarios.items() if entry["valid"] is False),
        "unknown_scenarios": sorted(
            key for key, entry in scenarios.items() if entry["valid"] is None and entry["repetitions"]
        ),
    }


def has_identity(alert: Alert) -> bool:
    return bool(normalize_id(alert.container_id) or normalize_name(alert.container_name))


def per_minute(count: float, minutes: float | None) -> float | None:
    return rounded(count / minutes) if minutes else None


def measured_operational(deployment: dict[str, Any], alerts: list[Alert], attribution: AttributionResult) -> dict:
    start = deployment.get("container_started_at") or deployment.get("started_at")
    end = deployment.get("ended_at")
    duration = end - start if is_number(start) and is_number(end) and end > start else None
    minutes = duration / 60.0 if duration else None
    lines = int(deployment.get("log_lines") or 0) + int(deployment.get("alerts_file_lines") or 0)
    size = int(deployment.get("log_bytes") or 0) + int(deployment.get("alerts_file_bytes") or 0)
    time_to_ready = deployment.get("time_to_ready")
    return {
        "status": deployment.get("status"),
        "time_to_ready": rounded(time_to_ready) if is_number(time_to_ready) else None,
        "duration_seconds": rounded(duration),
        "alerts": len(alerts),
        "alerts_per_minute": per_minute(len(alerts), minutes),
        "log_lines": lines,
        "log_bytes": size,
        "log_lines_per_minute": per_minute(lines, minutes),
        "log_bytes_per_minute": per_minute(size, minutes),
        "attributed_share": ratio(attribution.attributed, attribution.total),
        "container_identity_share": ratio(sum(1 for alert in alerts if has_identity(alert)), len(alerts)),
    }


def metric_direction(metric: str) -> str | None:
    if metric.endswith(HIGHER_IS_WORSE_SUFFIXES):
        return HIGHER_IS_WORSE
    if metric.endswith(LOWER_IS_WORSE_SUFFIXES):
        return LOWER_IS_WORSE
    return None


def relative_delta(baseline: float | None, value: float | None) -> float | None:
    if baseline is None or value is None or baseline == 0:
        return None
    return rounded((value - baseline) / abs(baseline))


def overhead_percent(delta: float | None, direction: str | None) -> float | None:
    if delta is None or direction is None:
        return None
    sign = 1.0 if direction == HIGHER_IS_WORSE else -1.0
    return rounded(sign * delta * 100.0)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def median_metrics(results: Iterable[WorkloadResult]) -> dict[str, dict[str, float]]:
    samples: dict[str, dict[str, list[float]]] = {}
    for result in results:
        metrics = result.metrics if isinstance(result.metrics, dict) else {}
        for metric, value in metrics.items():
            if is_number(value):
                samples.setdefault(result.name, {}).setdefault(str(metric), []).append(float(value))
    return {
        name: {metric: median(values) for metric, values in sorted(metrics.items())}
        for name, metrics in sorted(samples.items())
    }


def resource_stats(values: Iterable[Any], scale: float = 1.0) -> dict[str, Any]:
    items = [float(value) / scale for value in values if is_number(value)]
    return {
        "median": median(items),
        "max": rounded(max(items)) if items else None,
        "samples": len(items),
    }


def host_cpu_samples(results: Iterable[WorkloadResult]) -> list[float]:
    return [value for result in results for value in result.host_cpu_percent or [] if is_number(value)]


def compute_overhead(
    baseline: dict[str, dict[str, float]],
    results: list[WorkloadResult],
    baseline_host_cpu: Iterable[float] = (),
) -> dict[str, Any]:
    host_cpu = resource_stats(host_cpu_samples(results))
    host_baseline = resource_stats(baseline_host_cpu)
    host_delta = (
        rounded(host_cpu["median"] - host_baseline["median"])
        if host_cpu["median"] is not None and host_baseline["median"] is not None
        else None
    )
    measured = median_metrics(results)
    workloads: dict[str, dict[str, Any]] = {}
    for name in sorted(set(measured) | set(baseline)):
        metrics = {}
        for metric in sorted(set(measured.get(name, {})) | set(baseline.get(name, {}))):
            base = baseline.get(name, {}).get(metric)
            value = measured.get(name, {}).get(metric)
            direction = metric_direction(metric)
            delta = relative_delta(base, value)
            metrics[metric] = {
                "baseline": base,
                "value": value,
                "direction": direction,
                "delta": delta,
                "overhead_percent": overhead_percent(delta, direction),
            }
        workloads[name] = metrics
    directional = [
        (name, metric, item)
        for name, metrics in workloads.items()
        for metric, item in metrics.items()
        if item["overhead_percent"] is not None
    ]
    return {
        "available": bool(measured),
        "repetitions": len(results),
        "workloads": workloads,
        "overall_overhead_percent": median(item["overhead_percent"] for _, _, item in directional),
        "latency_overhead_percent": median(
            item["overhead_percent"] for _, _, item in directional if item["direction"] == HIGHER_IS_WORSE
        ),
        "throughput_overhead_percent": median(
            item["overhead_percent"] for _, _, item in directional if item["direction"] == LOWER_IS_WORSE
        ),
        "syscall_latency_overhead_percent": median(
            item["overhead_percent"]
            for name, _, item in directional
            if name == "syscall" and item["direction"] == HIGHER_IS_WORSE
        ),
        "cpu_percent": resource_stats(value for result in results for value in result.tool_cpu_percent or []),
        "memory_mib": resource_stats(
            (value for result in results for value in result.tool_memory_bytes or []), MIB
        ),
        "host_cpu_percent": host_cpu,
        "host_cpu_baseline": host_baseline,
        "host_cpu_delta_pp": host_delta,
    }


def split_alert_file(stem: str, profiles_by_tool: dict[str, set[str]]) -> tuple[str, str] | None:
    candidates = sorted(
        ((tool, profile) for tool, profiles in profiles_by_tool.items() for profile in profiles),
        key=lambda item: (-len(item[0]) - len(item[1]), item),
    )
    for tool, profile in candidates:
        if stem == f"{tool}-{profile}":
            return tool, profile
    if "-" not in stem:
        return None
    tool, _, profile = stem.rpartition("-")
    return tool, profile


def load_alerts(results_dir: Path, profiles_by_tool: dict[str, set[str]]) -> dict[tuple[str, str], list[Alert]]:
    directory = results_dir / "alerts"
    alerts: dict[tuple[str, str], list[Alert]] = {}
    if not directory.is_dir():
        return alerts
    for path in sorted(directory.glob("*.jsonl")):
        key = split_alert_file(path.stem, profiles_by_tool)
        if key is None:
            continue
        loaded = [
            alert
            for alert in build_all(Alert, read_jsonl(path))
            if is_number(alert.emitted_at) and isinstance(alert.raw, dict)
        ]
        alerts.setdefault(key, []).extend(loaded)
    return alerts


def is_control(run: ScenarioRun) -> bool:
    return run.tool == CONTROL_TOOL and run.profile == CONTROL_PROFILE


def known_profiles(metadata: dict[str, Any], runs: Iterable[ScenarioRun]) -> dict[str, set[str]]:
    profiles: dict[str, set[str]] = {}
    for tool, info in (metadata.get("tools") or {}).items():
        declared = info.get("profiles") if isinstance(info, dict) else None
        profiles.setdefault(str(tool), set()).update(str(value) for value in declared or [])
    for run in runs:
        profiles.setdefault(run.tool, set()).add(run.profile)
    return profiles


def tool_info(metadata: dict[str, Any], tool: str, has_runs: bool) -> dict[str, Any]:
    info = (metadata.get("tools") or {}).get(tool)
    info = info if isinstance(info, dict) else {}
    return {
        "status": info.get("status") or ("ok" if has_runs else "unknown"),
        "error": info.get("error"),
        "version": info.get("version"),
    }


def score_profile(
    catalog: dict[str, dict[str, Any]],
    runs: list[ScenarioRun],
    alerts: list[Alert],
    workloads: list[WorkloadResult],
    baseline: dict[str, dict[str, float]],
    grace_seconds: float,
    control: dict[str, Any] | None = None,
    deployment: dict[str, Any] | None = None,
    enforce: bool = False,
    baseline_host_cpu: Iterable[float] = (),
) -> dict[str, Any]:
    control = control or {}
    deployment = deployment or {}
    validity = {key: entry.get("valid") for key, entry in (control.get("scenarios") or {}).items()}
    confirmations = [value for value in deployment.get("confirmed_enforcements") or [] if is_number(value)]
    victim_names = {scenario_id: victim_name_for(info["requires"]) for scenario_id, info in catalog.items()}
    attribution = attribute_all(alerts, runs, grace_seconds, victim_names)
    by_scenario: dict[str, list[ScenarioRun]] = {}
    for run in runs:
        by_scenario.setdefault(run.scenario_id, []).append(run)
    scenarios = {
        scenario_id: score_scenario(
            info,
            by_scenario.get(scenario_id, []),
            attribution.by_run,
            validity.get(scenario_id),
            enforce,
            confirmations,
            grace_seconds,
        )
        for scenario_id, info in catalog.items()
    }
    entry = {
        "enforce": enforce,
        "summary": summarize(scenarios, attribution),
        "scenarios": scenarios,
        "overhead": compute_overhead(baseline, workloads, baseline_host_cpu),
        "operational": measured_operational(deployment, alerts, attribution),
    }
    if enforce:
        entry["response"] = summarize_response(scenarios, deployment, bool(control.get("available")))
    return entry


def score_results(results_dir: Path, grace_seconds: float) -> dict:
    results_dir = Path(results_dir)
    metadata = read_json(results_dir / "metadata.json")
    all_runs: list[ScenarioRun] = [
        run
        for run in build_all(ScenarioRun, read_jsonl(results_dir / "runs.jsonl"))
        if is_number(run.started_at) and is_number(run.ended_at)
    ]
    control_runs = [run for run in all_runs if is_control(run)]
    runs = [run for run in all_runs if not is_control(run)]
    workloads: list[WorkloadResult] = build_all(WorkloadResult, read_jsonl(results_dir / "workloads.jsonl"))
    profiles = known_profiles(metadata, runs)
    alerts = load_alerts(results_dir, profiles)
    for tool, profile in alerts:
        profiles.setdefault(tool, set()).add(profile)
    for result in workloads:
        if result.tool:
            profiles.setdefault(result.tool, set()).add(result.profile or "default")
    catalog = scenario_catalog(metadata, all_runs)
    baseline = median_metrics(result for result in workloads if not result.tool)
    baseline_host_cpu = host_cpu_samples(result for result in workloads if not result.tool)
    control = score_control(catalog, control_runs, metadata)
    deployments = metadata.get("deployments") if isinstance(metadata.get("deployments"), dict) else {}
    tools: dict[str, Any] = {}
    for tool in sorted(profiles):
        tool_runs = [run for run in runs if run.tool == tool]
        entry = tool_info(metadata, tool, bool(tool_runs))
        entry["profiles"] = {}
        for profile in sorted(profiles[tool]):
            deployment = deployments.get(f"{tool}-{profile}")
            deployment = deployment if isinstance(deployment, dict) else {}
            entry["profiles"][profile] = score_profile(
                catalog,
                [run for run in tool_runs if run.profile == profile],
                alerts.get((tool, profile), []),
                [result for result in workloads if result.tool == tool and (result.profile or "default") == profile],
                baseline,
                grace_seconds,
                control,
                deployment,
                profile in ENFORCE_PROFILES,
                baseline_host_cpu,
            )
        tools[tool] = entry
    score = {
        "run_id": metadata.get("run_id") or results_dir.name,
        "grace_seconds": grace_seconds,
        "scenarios": catalog,
        "baseline": baseline,
        "control": control,
        "tools": tools,
    }
    text = json.dumps(score, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    (results_dir / "score.json").write_text(text, encoding="utf-8")
    return json.loads(text)
