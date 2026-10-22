from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from bench.scoring import read_json, score_results

DEFAULT_GRACE_SECONDS = 10.0
NONE = "—"
STATUS_ICONS = {"detected": "✅", "partial": "⚠️", "missed": "❌"}
PREVENTED_ICON = "🛡️"
UNVERIFIED_MARK = "†"
INVALID_MARK = "(invalid)"
MIB = 1024.0 * 1024.0
TACTIC_ORDER = (
    "reconnaissance",
    "resource-development",
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
)

Column = tuple[str, str]


def escape(value: Any) -> str:
    text = NONE if value is None or value == "" else str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def table(headers: list[str], rows: Iterable[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(escape(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(escape(cell) for cell in row) + " |" for row in rows)
    return lines


def fmt_ratio(value: float | None) -> str:
    return NONE if value is None else f"{value * 100:.1f}%"


def fmt_signed(value: float | None) -> str:
    return NONE if value is None else f"{value:+.1f}%"


def fmt_seconds(value: float | None) -> str:
    return NONE if value is None else f"{value:.3f}s"


def fmt_number(value: float | None) -> str:
    if value is None:
        return NONE
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:.2f}"


def fmt_points(value: float | None) -> str:
    return NONE if value is None else f"{value:+.1f} pp"


def fmt_bool(value: Any) -> str:
    if value is None:
        return NONE
    return "yes" if value else "no"


def fmt_list(values: Any) -> str:
    if not values:
        return NONE
    if isinstance(values, (list, tuple)):
        return ", ".join(str(value) for value in values)
    return str(values)


def fmt_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return NONE if value is None else str(value)


def tactic_rank(tactic: str | None) -> tuple[int, str]:
    slug = str(tactic or "").strip().lower().replace("_", "-").replace(" ", "-")
    if slug in TACTIC_ORDER:
        return (TACTIC_ORDER.index(slug), slug)
    return (len(TACTIC_ORDER), slug or "~")


def columns(score: dict[str, Any]) -> list[Column]:
    return [
        (tool, profile)
        for tool, entry in sorted((score.get("tools") or {}).items())
        for profile in sorted(entry.get("profiles") or {})
    ]


def column_label(column: Column) -> str:
    return f"{column[0]}/{column[1]}"


def profile_entry(score: dict[str, Any], column: Column) -> dict[str, Any]:
    return score["tools"][column[0]]["profiles"][column[1]]


def scenario_entry(score: dict[str, Any], column: Column, scenario_id: str) -> dict[str, Any] | None:
    return profile_entry(score, column).get("scenarios", {}).get(scenario_id)


def ordered_scenarios(score: dict[str, Any], kind: str) -> list[tuple[str, dict[str, Any]]]:
    items = [
        (scenario_id, info)
        for scenario_id, info in (score.get("scenarios") or {}).items()
        if info.get("kind") == kind
    ]
    return sorted(items, key=lambda item: (tactic_rank(item[1].get("tactic")), item[0]))


def coverage_cell(entry: dict[str, Any] | None) -> str:
    if not entry or not entry.get("repetitions"):
        return NONE
    icon = STATUS_ICONS.get(entry.get("status"), NONE)
    return f"{icon} {entry['detected']}/{entry['repetitions']}"


def false_positive_cell(entry: dict[str, Any] | None) -> str:
    if not entry or not entry.get("repetitions"):
        return NONE
    detected = entry.get("detected", 0)
    icon = "⚠️" if detected else "✅"
    return f"{icon} {detected}/{entry['repetitions']}"


def response_valid(score: dict[str, Any], column: Column) -> bool:
    return bool(profile_entry(score, column).get("response", {}).get("valid", True))


def enforce_cell(entry: dict[str, Any] | None, valid: bool) -> str:
    if not entry or not entry.get("repetitions"):
        return NONE
    response = entry.get("response") or {}
    if not valid:
        return f"{coverage_cell(entry)} {UNVERIFIED_MARK}"
    if response.get("status") == "prevented":
        return f"{PREVENTED_ICON} {response.get('prevented', 0)}/{entry['repetitions']}"
    if response.get("status") == "invalid":
        return f"{coverage_cell(entry)} {INVALID_MARK}"
    return coverage_cell(entry)


def matrix_cell(score: dict[str, Any], column: Column, scenario_id: str) -> str:
    entry = scenario_entry(score, column, scenario_id)
    if profile_entry(score, column).get("enforce"):
        return enforce_cell(entry, response_valid(score, column))
    return coverage_cell(entry)


def scenario_label(score: dict[str, Any], scenario_id: str) -> str:
    control = nested(score, "control", "scenarios", scenario_id) or {}
    return f"{scenario_id} {INVALID_MARK}" if control.get("valid") is False else scenario_id


def latency_cell(entry: dict[str, Any] | None) -> str:
    if not entry or entry.get("latency_median") is None:
        return NONE
    return f"{fmt_seconds(entry['latency_median'])} / {fmt_seconds(entry['latency_p95'])}"


def section_metadata(score: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    lines = ["## Run metadata", ""]
    host = metadata.get("host") if isinstance(metadata.get("host"), dict) else {}
    config = metadata.get("config") if isinstance(metadata.get("config"), dict) else {}
    rows = [["run_id", score.get("run_id")], ["grace_seconds", score.get("grace_seconds")]]
    rows.extend([f"host.{key}", fmt_value(value)] for key, value in sorted(host.items()))
    rows.extend([f"config.{key}", fmt_value(value)] for key, value in sorted(config.items()))
    lines.extend(table(["Key", "Value"], rows))
    lines.extend(["", "### Tools", ""])
    tools_meta = metadata.get("tools") if isinstance(metadata.get("tools"), dict) else {}
    rows = []
    for tool in sorted(set(tools_meta) | set(score.get("tools") or {})):
        info = tools_meta.get(tool) if isinstance(tools_meta.get(tool), dict) else {}
        scored = (score.get("tools") or {}).get(tool, {})
        hashes = info.get("config_sha256") if isinstance(info.get("config_sha256"), dict) else {}
        profiles = sorted(set(info.get("profiles") or []) | set(scored.get("profiles") or {}))
        rows.append(
            [
                tool,
                info.get("version") or scored.get("version"),
                info.get("status") or scored.get("status"),
                fmt_list(profiles),
                fmt_list([f"{profile}: {str(value)[:12]}" for profile, value in sorted(hashes.items())]),
            ]
        )
    lines.extend(table(["Tool", "Version", "Status", "Profiles", "Config SHA-256"], rows))
    return lines


def leaderboard_key(item: tuple[Column, dict[str, Any]]) -> tuple:
    column, entry = item
    summary = entry.get("summary", {})
    recall = summary.get("recall")
    fp_rate = summary.get("false_positive_rate")
    latency = summary.get("latency_median")
    return (
        recall is None,
        -(recall or 0.0),
        float("inf") if fp_rate is None else fp_rate,
        float("inf") if latency is None else latency,
        column,
    )


def section_leaderboard(score: dict[str, Any]) -> list[str]:
    lines = [
        "## Leaderboard",
        "",
        "Recall counts attack scenarios detected in a majority of repetitions. "
        "Overhead percentages are positive when the tool makes the workload worse.",
        "",
    ]
    items = sorted(((column, profile_entry(score, column)) for column in columns(score)), key=leaderboard_key)
    rows = []
    for column, entry in items:
        summary = entry.get("summary", {})
        overhead = entry.get("overhead", {})
        rows.append(
            [
                column[0],
                column[1],
                fmt_ratio(summary.get("recall")),
                fmt_ratio(summary.get("detection_rate")),
                fmt_ratio(summary.get("false_positive_rate")),
                fmt_seconds(summary.get("latency_median")),
                summary.get("background_noise", 0),
                fmt_number(overhead.get("cpu_percent", {}).get("median")),
                fmt_number(overhead.get("memory_mib", {}).get("median")),
                fmt_signed(overhead.get("syscall_latency_overhead_percent")),
            ]
        )
    headers = [
        "Tool",
        "Profile",
        "Recall",
        "Detection rate",
        "FP rate",
        "Median latency",
        "Background noise",
        "CPU % (median)",
        "Memory MiB (median)",
        "Syscall latency overhead",
    ]
    lines.extend(table(headers, rows))
    return lines


def section_coverage(score: dict[str, Any]) -> list[str]:
    cols = columns(score)
    lines = [
        "## Coverage matrix",
        "",
        "✅ detected in a majority of repetitions, ⚠️ detected in some repetitions, ❌ missed, — not run. "
        f"In enforce columns {PREVENTED_ICON} means prevented in a majority of repetitions (effect not achieved while "
        f"the control run achieved it), ✅/⚠️ detected only; {UNVERIFIED_MARK} marks a deployment whose enforcement "
        f"could not be verified. {INVALID_MARK} marks scenarios whose effect was not achieved in the control runs.",
        "",
    ]
    rows = [
        [info.get("tactic"), scenario_label(score, scenario_id), info.get("technique")]
        + [matrix_cell(score, column, scenario_id) for column in cols]
        for scenario_id, info in ordered_scenarios(score, "attack")
    ]
    lines.extend(table(["Tactic", "Scenario", "Technique"] + [column_label(column) for column in cols], rows))
    lines.extend(["", "### Coverage per tactic", ""])
    tactics = sorted(
        {
            tactic
            for column in cols
            for tactic in profile_entry(score, column).get("summary", {}).get("coverage", {})
        },
        key=tactic_rank,
    )
    rows = []
    for tactic in tactics:
        row: list[Any] = [tactic]
        for column in cols:
            bucket = profile_entry(score, column).get("summary", {}).get("coverage", {}).get(tactic)
            row.append(f"{bucket['detected']}/{bucket['scenarios']}" if bucket else NONE)
        rows.append(row)
    lines.extend(table(["Tactic"] + [column_label(column) for column in cols], rows))
    return lines


def section_false_positives(score: dict[str, Any]) -> list[str]:
    cols = columns(score)
    lines = [
        "## False positives",
        "",
        "Benign runs with at least one attributed alert, out of all benign runs.",
        "",
    ]
    benign = ordered_scenarios(score, "benign")
    rows = [
        [scenario_id] + [false_positive_cell(scenario_entry(score, column, scenario_id)) for column in cols]
        for scenario_id, _ in benign
    ]
    lines.extend(table(["Scenario"] + [column_label(column) for column in cols], rows))
    details = [
        [column[0], column[1], scenario_id, fmt_list(entry.get("rules"))]
        for column in cols
        for scenario_id, _ in benign
        for entry in [scenario_entry(score, column, scenario_id)]
        if entry and entry.get("detected")
    ]
    if details:
        lines.extend(["", "### Rules raising false positives", ""])
        lines.extend(table(["Tool", "Profile", "Scenario", "Rules"], details))
    return lines


def section_latency(score: dict[str, Any]) -> list[str]:
    cols = columns(score)
    lines = [
        "## Detection latency",
        "",
        "Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the "
        "scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.",
        "",
    ]
    rows = [
        [scenario_id] + [latency_cell(scenario_entry(score, column, scenario_id)) for column in cols]
        for scenario_id, _ in ordered_scenarios(score, "attack")
    ]
    lines.extend(table(["Scenario"] + [column_label(column) for column in cols], rows))
    lines.extend(["", "### Latency reference", ""])
    rows = [
        [
            column[0],
            column[1],
            fmt_ratio(profile_entry(score, column).get("summary", {}).get("action_timestamp_share")),
            profile_entry(score, column).get("summary", {}).get("early_alerts", 0),
        ]
        for column in cols
    ]
    lines.extend(table(["Tool", "Profile", "Runs with action timestamp", "Alerts before the action"], rows))
    return lines


def overhead_cell(item: dict[str, Any] | None) -> str:
    if not item or item.get("value") is None:
        return NONE
    value = fmt_number(item["value"])
    if item.get("overhead_percent") is not None:
        return f"{value} ({fmt_signed(item['overhead_percent'])})"
    if item.get("delta") is not None:
        return f"{value} (Δ {fmt_signed(item['delta'] * 100)})"
    return value


def section_overhead(score: dict[str, Any]) -> list[str]:
    cols = columns(score)
    lines = [
        "## Overhead",
        "",
        "Median over repetitions. The percentage is the overhead relative to the baseline median: "
        "positive always means worse. Δ marks metrics without a known direction (signed relative delta).",
        "",
    ]
    baseline = score.get("baseline") or {}
    keys = {(name, metric) for name, metrics in baseline.items() for metric in metrics}
    for column in cols:
        workloads = profile_entry(score, column).get("overhead", {}).get("workloads", {})
        keys.update((name, metric) for name, metrics in workloads.items() for metric in metrics)
    rows = []
    for name, metric in sorted(keys):
        row: list[Any] = [name, metric, fmt_number(baseline.get(name, {}).get(metric))]
        for column in cols:
            workloads = profile_entry(score, column).get("overhead", {}).get("workloads", {})
            row.append(overhead_cell(workloads.get(name, {}).get(metric)))
        rows.append(row)
    lines.extend(table(["Workload", "Metric", "Baseline"] + [column_label(column) for column in cols], rows))
    lines.extend(["", "### Tool resource usage", ""])
    rows = []
    for column in cols:
        overhead = profile_entry(score, column).get("overhead", {})
        cpu = overhead.get("cpu_percent", {})
        memory = overhead.get("memory_mib", {})
        host = overhead.get("host_cpu_percent") or {}
        rows.append(
            [
                column[0],
                column[1],
                fmt_number(cpu.get("median")),
                fmt_number(cpu.get("max")),
                fmt_number(memory.get("median")),
                fmt_number(memory.get("max")),
                fmt_signed(overhead.get("latency_overhead_percent")),
                fmt_signed(overhead.get("throughput_overhead_percent")),
                fmt_number(host.get("median")),
                fmt_number(host.get("max")),
                fmt_points(overhead.get("host_cpu_delta_pp")),
            ]
        )
    headers = [
        "Tool",
        "Profile",
        "CPU % median",
        "CPU % max",
        "Memory MiB median",
        "Memory MiB max",
        "Latency overhead",
        "Throughput overhead",
        "Host CPU % median",
        "Host CPU % max",
        "Host CPU Δ vs baseline",
    ]
    lines.extend(table(headers, rows))
    baseline_host = next(
        (
            profile_entry(score, column).get("overhead", {}).get("host_cpu_baseline")
            for column in cols
            if profile_entry(score, column).get("overhead", {}).get("host_cpu_baseline", {}).get("samples")
        ),
        None,
    )
    if baseline_host:
        lines.extend(
            [
                "",
                f"Host CPU is sampled from /proc/stat every second during workloads (Docker backend only); baseline "
                f"median {fmt_number(baseline_host.get('median'))}%, max {fmt_number(baseline_host.get('max'))}%. "
                "The delta is in percentage points of the whole host.",
            ]
        )
    return lines


def nested(data: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def section_operational(score: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    lines = [
        "## Operational aspects",
        "",
        "Scores follow the rubric in docs/methodology.md (1 worst, 5 best).",
        "",
    ]
    operational = metadata.get("operational") if isinstance(metadata.get("operational"), dict) else {}
    rows = []
    for tool, info in sorted(operational.items()):
        rows.append(
            [
                tool,
                nested(info, "version"),
                nested(info, "license"),
                nested(info, "scores", "deployment"),
                nested(info, "scores", "rule_customization"),
                nested(info, "scores", "output_quality"),
                nested(info, "deployment", "steps"),
                nested(info, "rules", "language"),
                fmt_bool(nested(info, "rules", "custom_rules")),
                fmt_bool(nested(info, "rules", "hot_reload")),
                fmt_list(nested(info, "output", "formats")),
                fmt_list(nested(info, "output", "enrichment")),
                fmt_bool(nested(info, "output", "attack_mapping")),
                nested(info, "notes"),
            ]
        )
    headers = [
        "Tool",
        "Version",
        "License",
        "Deployment",
        "Rule customization",
        "Output quality",
        "Deploy steps",
        "Rule language",
        "Custom rules",
        "Hot reload",
        "Output formats",
        "Enrichment",
        "ATT&CK mapping",
        "Notes",
    ]
    lines.extend(table(headers, rows))
    lines.extend(
        [
            "",
            "### Measured operational metrics",
            "",
            "Measured per deployment: time from container start to readiness, alert and log volume over the "
            "deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and "
            "share of alerts carrying a container id or name. Rubric scores repeated for comparison.",
            "",
        ]
    )
    rows = []
    for column in columns(score):
        measured = profile_entry(score, column).get("operational") or {}
        info = operational.get(column[0]) if isinstance(operational.get(column[0]), dict) else {}
        log_bytes = measured.get("log_bytes")
        rows.append(
            [
                column[0],
                column[1],
                nested(info, "scores", "deployment"),
                nested(info, "scores", "output_quality"),
                fmt_seconds(measured.get("time_to_ready")),
                fmt_number(measured.get("alerts_per_minute")),
                fmt_number(measured.get("log_lines_per_minute")),
                fmt_number(log_bytes / MIB) if log_bytes else NONE,
                fmt_ratio(measured.get("attributed_share")),
                fmt_ratio(measured.get("container_identity_share")),
            ]
        )
    headers = [
        "Tool",
        "Profile",
        "Deployment score",
        "Output quality score",
        "Time to ready",
        "Alerts / min",
        "Log lines / min",
        "Log volume MiB",
        "Attributed alerts",
        "Alerts with container identity",
    ]
    lines.extend(table(headers, rows))
    return lines


def section_control(score: dict[str, Any]) -> list[str]:
    control = score.get("control") or {}
    lines = [
        "## Control runs",
        "",
        "Every scenario is run without any tool deployed; a scenario is valid when `check.sh` reports its effect as "
        "achieved in a majority of control repetitions. Invalid scenarios are excluded from prevention metrics and "
        f"flagged {INVALID_MARK} in detection tables.",
        "",
    ]
    if not control.get("available"):
        return lines + [f"No control runs (status: {control.get('status') or 'skipped'})."]
    rows = [
        [
            scenario_id,
            entry.get("kind"),
            entry.get("repetitions"),
            f"{entry.get('effect_achieved', 0)}/{entry.get('repetitions', 0)}",
            entry.get("effect_unknown"),
            entry.get("failed_executions"),
            {True: "✅ valid", False: "❌ invalid"}.get(entry.get("valid"), "unknown"),
        ]
        for scenario_id, entry in sorted((control.get("scenarios") or {}).items())
        if entry.get("repetitions")
    ]
    lines.extend(
        table(["Scenario", "Kind", "Repetitions", "Effect achieved", "Effect unknown", "Non-zero exits", "Validity"], rows)
    )
    invalid = control.get("invalid_scenarios") or []
    lines.extend(["", f"Invalid scenarios: {fmt_list(invalid)}." if invalid else "All control scenarios are valid."])
    return lines


def response_row(tool: str, column: Column | None, score: dict[str, Any], info: dict[str, Any]) -> list[Any]:
    response = info.get("response") if isinstance(info.get("response"), dict) else {}
    mechanisms = fmt_list(response.get("mechanisms"))
    synchronous = fmt_bool(response.get("synchronous"))
    if column is None:
        return [tool, "detection only", NONE, NONE, NONE, NONE, NONE, NONE, mechanisms, synchronous]
    summary = profile_entry(score, column).get("response") or {}
    rate = fmt_ratio(summary.get("prevention_rate"))
    if summary.get("prevention_rate") is not None:
        rate = f"{rate} ({summary.get('prevented_scenarios', 0)}/{summary.get('valid_attack_scenarios', 0)})"
    if not summary.get("valid", True):
        rate = f"invalid: {rate}"
    collateral = summary.get("collateral_damage")
    collateral_cell = NONE
    if collateral is not None:
        collateral_cell = f"{collateral} ({fmt_ratio(summary.get('collateral_damage_rate'))})"
    return [
        tool,
        rate,
        summary.get("detected_not_prevented"),
        summary.get("prevented_without_alert"),
        collateral_cell,
        fmt_seconds(summary.get("response_latency_median")),
        summary.get("enforcement_alerts"),
        fmt_bool(summary.get("enforcement_verified")),
        mechanisms,
        synchronous,
    ]


def section_response(score: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    lines = [
        "## Response effectiveness",
        "",
        "Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of "
        "repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count "
        "repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another "
        "reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response "
        "latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could "
        "not be verified are marked invalid.",
        "",
    ]
    operational = metadata.get("operational") if isinstance(metadata.get("operational"), dict) else {}
    enforce_columns = {column[0]: column for column in columns(score) if profile_entry(score, column).get("enforce")}
    tools = sorted(set(operational) | set(score.get("tools") or {}))
    rows = []
    for tool in tools:
        info = operational.get(tool) if isinstance(operational.get(tool), dict) else {}
        column = enforce_columns.get(tool)
        if column is None and not nested(info, "response", "blocking") and not nested(info, "response", "mechanisms"):
            rows.append(response_row(tool, None, score, info))
        elif column is not None:
            rows.append(response_row(tool, column, score, info))
        else:
            row = response_row(tool, None, score, info)
            row[1] = "no enforce run"
            rows.append(row)
    headers = [
        "Tool",
        "Prevention rate",
        "Detected not prevented",
        "Prevented without alert",
        "Collateral damage",
        "Median response latency",
        "Enforcement alerts",
        "Enforcement verified",
        "Mechanisms",
        "Synchronous",
    ]
    lines.extend(table(headers, rows) if rows else ["None."])
    suspicious = [
        [column[0], fmt_list(profile_entry(score, column).get("response", {}).get("prevented_without_alert_scenarios"))]
        for column in enforce_columns.values()
        if profile_entry(score, column).get("response", {}).get("prevented_without_alert_scenarios")
    ]
    if suspicious:
        lines.extend(["", "### Prevented without alert", ""])
        lines.extend(table(["Tool", "Scenarios"], suspicious))
    return lines


def section_rules(score: dict[str, Any]) -> list[str]:
    rows = [
        [column[0], column[1], scenario_id, fmt_list(entry.get("rules"))]
        for column in columns(score)
        for scenario_id, _ in ordered_scenarios(score, "attack")
        for entry in [scenario_entry(score, column, scenario_id)]
        if entry and entry.get("rules")
    ]
    return ["## Matched rules", ""] + table(["Tool", "Profile", "Scenario", "Rules"], rows)


def section_failures(score: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    lines = ["## Failures", "", "### Failed tools", ""]
    tools_meta = metadata.get("tools") if isinstance(metadata.get("tools"), dict) else {}
    rows = []
    for tool in sorted(set(tools_meta) | set(score.get("tools") or {})):
        info = tools_meta.get(tool) if isinstance(tools_meta.get(tool), dict) else {}
        scored = (score.get("tools") or {}).get(tool, {})
        status = info.get("status") or scored.get("status")
        if status != "ok":
            rows.append([tool, status, info.get("error") or scored.get("error")])
    lines.extend(table(["Tool", "Status", "Error"], rows) if rows else ["None."])
    lines.extend(["", "### Scenario executions with a non-zero exit code", ""])
    rows = [
        [column[0], column[1], scenario_id, run.get("repetition"), run.get("exit_code")]
        for column in columns(score)
        for scenario_id, entry in sorted(profile_entry(score, column).get("scenarios", {}).items())
        for run in entry.get("runs", [])
        if run.get("exit_code") != 0
    ]
    lines.extend(table(["Tool", "Profile", "Scenario", "Repetition", "Exit code"], rows) if rows else ["None."])
    lines.extend(["", "### Scenario cleanups with a non-zero exit code", ""])
    rows = [
        [column[0], column[1], scenario_id, run.get("repetition"), run.get("cleanup_exit_code")]
        for column in columns(score)
        for scenario_id, entry in sorted(profile_entry(score, column).get("scenarios", {}).items())
        for run in entry.get("runs", [])
        if run.get("cleanup_exit_code") not in (None, 0)
    ]
    lines.extend(table(["Tool", "Profile", "Scenario", "Repetition", "Exit code"], rows) if rows else ["None."])
    return lines


def render_report(score: dict[str, Any], metadata: dict[str, Any]) -> str:
    sections = [
        [f"# eBPF runtime detection benchmark: {score.get('run_id') or NONE}"],
        section_metadata(score, metadata),
        section_leaderboard(score),
        section_control(score),
        section_coverage(score),
        section_false_positives(score),
        section_latency(score),
        section_response(score, metadata),
        section_overhead(score),
        section_operational(score, metadata),
        section_rules(score),
        section_failures(score, metadata),
    ]
    return "\n\n".join("\n".join(section) for section in sections) + "\n"


def write_report(results_dir: Path) -> Path:
    results_dir = Path(results_dir)
    metadata = read_json(results_dir / "metadata.json")
    score = read_json(results_dir / "score.json")
    if not score:
        grace = nested(metadata, "config", "grace_seconds")
        score = score_results(results_dir, float(grace if grace is not None else DEFAULT_GRACE_SECONDS))
    path = results_dir / "report.md"
    path.write_text(render_report(score, metadata), encoding="utf-8")
    return path
