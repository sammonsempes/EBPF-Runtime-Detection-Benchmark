# Methodology

This document defines how the benchmark is executed and how every published number is computed. The implementation lives in `runner/bench/scoring.py` (attribution and metrics) and `runner/bench/report.py` (report rendering). When this document and the code disagree, the code is a bug.

## Environment requirements

- Linux host (bare metal or VM) with a kernel supporting eBPF; 5.8+ with BTF (`/sys/kernel/btf/vmlinux`) is recommended. Some tools need kernel headers or debugfs/tracefs mounted.
- Docker Engine with Compose v2. The runner talks to the host daemon through `/var/run/docker.sock` and starts tool containers privileged, with host PID, network and cgroup namespaces.
- No other security agent and no heavy workload running on the host during a run. CPU frequency scaling and other noisy neighbours should be minimised for overhead measurements.
- The host description (kernel, Docker version, CPU count, memory) is recorded in `metadata.json` and printed in the report. Results are only comparable between runs on the same host and kernel.

## Phases

A run (`docker compose up bench`) executes the following phases, configured by `bench.yaml`:

1. **Baseline.** The workload host container is started with no tool deployed. Every workload runs `repetitions` times; the results are stored in `workloads.jsonl` with `tool` set to null, including host-wide CPU samples.
2. **Control.** With `control_scenarios: true`, the victim containers (`bench-victim`, unprivileged, and `bench-victim-priv`, privileged) and the attacker are started with no tool deployed and every scenario runs `repetitions` times, exactly as in phase 5. The runs are stored with `tool: none`, `profile: control`; they are never scored as a tool and only establish scenario validity.
3. **Deploy.** For each tool and profile (`default`, `tuned`, `enforce` when the adapter supports it), the tool container is started from its adapter's `ContainerSpec`. The tool is ready when its `ready_pattern` appears in its logs and, if `ready_url` is set, that URL returns HTTP 200, or failed if `startup_timeout` elapses. The runner then waits `settle_seconds` (5 s by default) for probes to attach. A tool that cannot be deployed is recorded with `status: failed` and its error, and is skipped; the remaining tools still run.
4. **Workloads.** With the tool running, every workload runs `repetitions` times. The tool container's CPU percentage and memory usage, and the host-wide CPU utilisation, are sampled during the workloads.
5. **Scenarios.** Fresh victim and attacker containers are created. Every scenario runs `repetitions` times, sequentially, each execution receiving a unique `BENCH_MARKER`, as `sh run.sh`, then `sh check.sh`, then `sh cleanup.sh` in the same container with the same environment. The runner records `started_at` right before the `run.sh` exec and `ended_at` when it returns, the exit code and output, the first `BENCH_ACTION` timestamp printed by the script (`action_at`), the `check.sh` verdict (`effect_achieved`: exit 0 true, exit 1 false, anything else or no `check.sh` null) and the `cleanup.sh` exit code (`runs.jsonl`).
6. **Grace.** After the last scenario, the runner keeps collecting alerts for at least `grace_seconds` so that late alerts of the last execution are not lost.
7. **Teardown.** The victims, the attacker and the tool container are stopped and removed; the tool's alerts are normalised by the adapter's `parse` and written to `alerts/<tool>-<profile>.jsonl`, every container log line is kept in `raw/<tool>-<profile>/container.log`, and for `enforce` deployments the adapter's `enforcement_check` decides `enforcement_verified`.

Scoring (`score.json`) and the report (`report.md`) are computed offline from these files and can be recomputed at any time.

## Attribution rules

An alert is attributed to a scenario run of the same tool and profile when both conditions hold:

1. **Time window:** `run.started_at <= alert.emitted_at <= run.ended_at + grace_seconds` (both bounds inclusive). The window starts at `started_at`, not at the action timestamp, so alerts on setup steps still count.
2. **Event time:** when the alert carries an `event_at` (tool-reported kernel event time), it is not later than `run.ended_at + 1 s`. Events produced by `check.sh`, `cleanup.sh` or the next execution therefore cannot be credited to the run; alerts without `event_at` are only bound by the window above.
3. **Identity:** at least one of
   - the alert's `container_id` and the run's `victim_container_id` are prefixes of one another, after lowercasing and stripping a `docker://`, `containerd://` or `cri-o://` scheme, with at least 12 characters on both sides (short Docker ids match full ids);
   - the alert's `container_name`, without a leading `/`, equals the victim name expected for the scenario: `bench-victim-priv` when the scenario requires `privileged`, `bench-victim` otherwise;
   - the run's `BENCH_MARKER` appears anywhere in the JSON serialisation of the alert's `raw` payload.

Each alert is attributed to at most one run: among the runs whose window contains the alert and whose identity check passes, the one that started first wins (ties broken by scenario id, then repetition). Windows only overlap when `grace_seconds` exceeds the pause between two executions.

Unattributed alerts are classified as:

- **background noise:** the alert identifies a victim container (name `bench-victim`/`bench-victim-priv`, or container id matching any run's victim) and falls outside every scenario window;
- **unattributed in window:** the alert identifies a victim and falls inside some window but fails that run's identity check (for example an alert from the unprivileged victim during a privileged scenario);
- **non-victim:** the alert does not identify a victim (host processes, the tool itself, other containers). These are reported for information only.

## Metric definitions

Per tool, profile and scenario:

- **repetitions:** number of executions of the scenario.
- **detected:** number of repetitions with at least one attributed alert.
- **detection rate:** detected / repetitions.
- **status:** `detected` when detected in a strict majority of repetitions (`2 * detected > repetitions`), `partial` when detected at least once but not in a majority, `missed` when never detected, `not_run` when there are no repetitions (tool failed, scenario skipped).
- **latencies:** for each detected repetition, `min(alert.emitted_at) - reference` over its attributed alerts, where `reference` is the `BENCH_ACTION` timestamp (`action_at`) when the script printed one and `started_at` otherwise; median and p95 (linear interpolation between closest ranks) are reported. An alert on a setup step before the action yields a negative latency (counted as `early_alerts`). The share of runs whose latency uses the action timestamp is reported per tool/profile (`action_timestamp_share`).
- **valid:** the scenario's validity from the control runs (see below); invalid scenarios stay in detection metrics but are flagged.
- **rules:** sorted set of rule names of attributed alerts.
- **false positives** (benign scenarios): number of repetitions with at least one attributed alert.

Repetitions whose script exited non-zero are counted like any other repetition and listed separately in the report; a non-zero exit usually means the behaviour was not fully performed, so the corresponding cells deserve scrutiny.

Per tool and profile, over scenarios that were run:

- **true positives / false negatives:** attack repetitions with / without an attributed alert.
- **recall:** attack scenarios with status `detected` / attack scenarios run. A scenario counts only when detected in a majority of its repetitions.
- **detection rate:** true positives / attack repetitions (per-repetition recall).
- **false positive rate:** benign repetitions with an attributed alert / benign repetitions.
- **background noise:** count of background-noise alerts as defined above. It indicates how chatty a tool is on an idle container; it is not part of the false positive rate.
- **latency median / p95:** over all detected attack repetitions.
- **coverage per tactic:** for each ATT&CK tactic, number of attack scenarios run and how many are detected, partial and missed; coverage is detected / run.

### Latency and its limits

Latency is measured from the action timestamp printed by the script right before the first malicious step (`BENCH_ACTION`, taken with `date +%s.%N` inside the victim; same kernel clock as the runner) or, when missing, from the moment the runner starts the scenario (`started_at`, before `docker exec`), to the moment the alert is observed (`emitted_at`):

- for alerts read from container logs, `emitted_at` is the Docker log timestamp, set by the Docker daemon when the line is written to the tool's stdout/stderr;
- for alerts read from a file (`alerts_file`), `emitted_at` is the time the runner read the line, which adds the tailing poll interval and makes latency an upper bound. In Kubernetes mode, Tetragon's export file is read with `tail -F` over the exec API, so the read time also includes that stream's delay.

Consequences: with the action timestamp, latency excludes `docker exec` start-up and setup time but still includes the process start of the first malicious command; with the start fallback it includes both, so the two references must not be mixed when comparing scenarios (the report shows the share per tool/profile). It is not the tool's internal detection latency and includes the tool's own output buffering. The tool's `event_at` (kernel event time, when available) is preserved in alerts but not used for scoring, because it is not comparable across tools. Differences below a few hundred milliseconds should not be over-interpreted.

## Scenario validity (control runs)

For every scenario, the control runs (no tool) give the number of repetitions whose `check.sh` reported the effect as achieved. A scenario is **valid** when its effect is achieved in a strict majority of its control repetitions, **invalid** when it is not, and **unknown** when there are no control runs or every check was inconclusive. Invalid scenarios do not work on this host (missing kernel feature, network, image content) and cannot measure prevention: they are excluded from all prevention metrics, flagged `(invalid)` in the coverage matrix, and listed in the control table of the report. Unknown validity (control disabled) is treated as valid and flagged by `control_available: false`.

## Response effectiveness (enforce profile)

Per enforce deployment, scenario and repetition, with `effect` the `check.sh` verdict:

- **prevented:** attack scenario that is not invalid and whose effect was not achieved (`effect_achieved: false`). An unknown verdict is never a prevention.
- **detected not prevented:** at least one attributed alert and effect achieved.
- **prevented without alert:** prevented with no attributed alert. This is suspicious: the effect may have failed for another reason (timing, side effect of a previous run), and is reported separately.
- **response latency:** emission time of the first attributed enforcement alert (non-null `action`) minus the latency reference.
- **confirmed enforcements:** adapter-provided confirmation log lines (Kunai `sending SIGKILL to PID=`) inside the run window.

Per scenario, the response status is `prevented` when prevented in a strict majority of repetitions, `invalid` when the scenario is invalid, and the detection status otherwise (`detected`, `partial`, `missed`). Per deployment:

- **prevention rate:** prevented attack scenarios / valid attack scenarios run (majority rule, like recall).
- **collateral damage:** valid benign scenarios whose effect was not achieved in a majority of enforce repetitions, as a count and as a rate over valid benign scenarios run.
- **enforcement verified:** `enforcement_verified` from the adapter's `enforcement_check` on the deployment logs: true when the logs prove an enforcing mechanism was active (KubeArmor `Initialized BPF-LSM Enforcer`, at least one Kunai kill confirmation), false when they prove it was not (KubeArmor `Disabled KubeArmor Enforcer` or the AppArmor enforcer, which cannot apply to runner-started victims), null when unknown (Tetragon: it refuses to start when Override is unsupported, but no log line proves the enforcement path). When it is false, the deployment's prevention results are marked invalid in `score.json` (`response.valid: false`) and in the report.

The report's response table also shows, from `operational.yaml` `response:`, the mechanisms and whether the response is synchronous; tools without an enforce run and without blocking capability are listed as "detection only".

## Overhead computation

For every workload metric, the median over repetitions is computed for the baseline and for each tool/profile. The signed relative delta is `(tool_median - baseline_median) / |baseline_median|` (undefined when the baseline is zero or missing). The normalised **overhead %** makes positive always mean worse:

- metrics ending with `_ns` or `_us` (latencies): higher is worse, overhead % = `+delta * 100`;
- metrics ending with `_per_sec` (throughput): lower is worse, overhead % = `-delta * 100`;
- other metrics have no known direction: only the signed delta is reported.

Summary values per tool/profile are medians of overhead % over all directional metrics (overall), latency metrics, throughput metrics, and latency metrics of the `syscall` workload (the "syscall latency overhead" in the leaderboard).

Tool resource usage is the median and maximum of the tool container's CPU percentage and memory (MiB, 1 MiB = 1048576 bytes) over all samples taken during that tool/profile's workloads.

**Host CPU** captures what the container statistics miss (eBPF programs run in the context of the traced processes, kernel threads, the Docker daemon): during every workload the runner reads the first line of `/proc/stat` (host-wide, not namespaced) about once per second and records the busy share `1 - (idle + iowait) / total` of the interval, in percent of all CPUs. Median and maximum are reported per tool/profile with the baseline median, and the delta `median(tool) - median(baseline)` in percentage points. This is only sampled by the Docker backend; in Kubernetes mode the list is empty (the runner does not run on the node).

## Measured operational metrics

Next to the declarative rubric, each deployment records:

- **time to ready:** seconds from the tool container start (after image pull or build) to the readiness condition;
- **alert volume:** normalised alerts per minute over the deployment lifetime (container start to teardown, including workloads and idle time);
- **log volume:** lines per minute and total bytes of everything the tool wrote (container logs plus alerts file);
- **attributed share:** attributed alerts / all alerts;
- **container identity share:** alerts carrying a container id or name / all alerts.

## Operational rubric

Each tool's `tools/<tool>/operational.yaml` records deployment, rule and output characteristics and three scores from 1 to 5:

**deployment**

- 5 = single container/Helm install with defaults works
- 4 = minor configuration
- 3 = needs host preparation (headers, mounts, kernel features)
- 2 = build from source
- 1 = not containerizable

**rule_customization**

- 5 = expressive declarative rule language with hot reload
- 4 = declarative without hot reload
- 3 = limited policy options
- 2 = code changes required
- 1 = none

**output_quality**

- 5 = structured JSON with process ancestry, container/k8s context and ATT&CK mapping
- 4 = JSON with container context
- 3 = JSON with minimal context
- 2 = unstructured text
- 1 = no alert output

## Default, tuned and enforce profiles

- **default:** the tool's upstream configuration and rule set as shipped, with only the changes required to run in the benchmark (output format, log destination, enabling the event sources needed to emit alerts at all).
- **tuned:** realistic rules a security team would write to detect the behaviours covered by the scenarios (for example "shell with network socket as stdin", "write below /etc/cron.d"). Tuned rules must target behaviours, never benchmark-specific tokens: no `BENCH_MARKER`, no scenario ids, no attacker hostname, no victim container names, no file names that only the scenario scripts use. Tuned rules should also be checked against the benign scenarios, since a rule that fires on everything is not a detection.

- **enforce:** the tuned rules with the tool's blocking or kill action on rules that only match malicious behaviours (rules that could match benign scenarios stay detection-only), for tools that can respond. Tools without that capability have no enforce profile and are reported as detection only.

All profiles' configuration directories are hashed (`config_sha256` in `metadata.json`) and printed in the report so that a result can be traced to the exact rules that produced it.

## Threats to validity

- **Single host.** Each run uses one host; overhead depends on CPU model, kernel and background load. Overhead numbers are relative to that host's baseline and should not be compared across hosts.
- **WSL and VM kernels.** WSL2 and some cloud VM kernels lack BTF, kprobes or LSM hooks, or expose them differently; a tool failing or missing events there may work on a stock distribution kernel. The kernel version is recorded for this reason.
- **Scenario realism.** Scenarios reproduce one technique each, in a short and noise-free script. Real intrusions are slower, chained and mixed with legitimate activity; detection here is a necessary, not sufficient, signal.
- **Rule tuning bias.** Tuned profiles are written with knowledge of the scenarios. The behaviour-only rule above limits but does not remove this bias; default-profile results are the less biased comparison.
- **Timing noise.** Latency includes container exec and log pipeline delays; overhead measurements are sensitive to CPU scheduling and frequency scaling. Repetitions and medians reduce, but do not eliminate, this noise.
- **Attribution.** Alerts that carry neither container context nor the marker cannot be attributed, which penalises tools with poor container enrichment; this is intentional, as such alerts are hard to triage in practice. `check.sh` and `cleanup.sh` run right after `run.sh`, inside the grace window: a tool alerting on their file accesses or deletions without an `event_at` could still be credited to the run.
- **Asynchronous kill versus synchronous deny.** KubeArmor (BPF-LSM) and Tetragon Override deny the operation in the kernel before it happens; Kunai kill and Tetragon Sigkill send SIGKILL after the event, so the operation that triggered the rule has usually completed (a file written to `/etc/cron.d` stays). A "prevented" verdict for an asynchronous mechanism means the scenario was stopped before its checked effect, which depends on how far the effect is from the triggering event; prevention rates of synchronous and asynchronous tools are not equivalent.
- **WSL2 and BPF-LSM.** WSL2 kernels have no BPF-LSM (and no securityfs), so KubeArmor falls back to no enforcer: its enforce results on WSL2 cannot be valid and are marked by `enforcement_verified: false`. Run enforcement comparisons on a kernel booted with `lsm=...,bpf`.
- **Log cap.** The runner keeps every tool log and alerts line in memory until teardown. To keep a runaway tool (or a feedback loop such as an agent observing the writes of its own output) from exhausting the runner's memory, each stream (container logs, alerts file) keeps at most `max_log_lines` lines (default 5,000,000) and `max_log_bytes` bytes (default 2 GiB) from `bench.yaml`. Once a stream hits the cap, every later line of that stream is dropped, not only the oversized one. The run continues. The deployment gets `log_overflow: true` with `dropped_log_lines`, `dropped_log_bytes`, `dropped_alerts_file_lines` and `dropped_alerts_file_bytes` in `metadata.json`, an entry in its `errors`, and a row under "Log overflow" in the report. Alerts emitted after the cap are missing: detections, false positives and alert volume of that deployment are lower bounds, and scenarios run after the overflow look like misses.
- **Control validity.** The control phase runs before the tools; a scenario whose effect depends on the host state (network, kernel modules) may behave differently later. Invalid scenarios are excluded from prevention, not from detection.

## Adding a scenario

1. Create `scenarios/<id>/scenario.yaml` following the contract in `docs/architecture.md` (`kind`, `tactic` slug and `technique` id for attacks, `requires`).
2. Write `scenarios/<id>/run.sh` (POSIX shell, calls its own `cleanup.sh` first, prints `BENCH_ACTION <epoch>` right before the first malicious step, leaves its effects in place, finishes within `timeout`, embeds `$BENCH_MARKER` in created file names or arguments where it does not change the behaviour), `check.sh` (exit 0 when the effect is achieved, 1 otherwise, silent, inspects state only) and `cleanup.sh` (idempotent, always exit 0), following the contract in `docs/architecture.md`.
3. Run the benchmark with only that scenario and check the control runs in `runs.jsonl` for `effect_achieved: true` and a non-null `action_at`.
4. Do not update tuned rules to match tokens of the new scenario; only add behaviour-based rules if a realistic rule is missing.

## Adding a tool

1. Add `runner/bench/adapters/<tool>.py` with a class `Adapter` implementing `ToolAdapter`: `container_spec` (image, mounts built from `host_repo_root`/`host_output_dir`, `ready_pattern`, optional `alerts_file`) and `parse` returning a normalised `Alert` (with `container_id`/`container_name` whenever the tool provides them, and the full original event in `raw`).
2. Add `tools/<tool>/default/` (upstream configuration) and `tools/<tool>/tuned/` (behaviour-based rules), a `README.md` describing deployment and alert collection, and `operational.yaml` scored with the rubric above.
3. Add real alert samples under `runner/tests/fixtures/<tool>/` and parser tests.
4. Enable the tool in `bench.yaml` and run the benchmark; the scoring and report pick it up automatically.
