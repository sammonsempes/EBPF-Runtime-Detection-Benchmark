# Architecture

Everything runs through Docker Compose. The host only needs Docker and a Linux kernel with eBPF support (5.8+ recommended, BTF enabled).

```
docker compose build          # builds runner, victim and attacker images
docker compose up bench       # runs the benchmark described in bench.yaml
docker compose up tests       # runs the unit test suite
```

## Repository layout

```
compose.yaml                  services: bench, bench-k8s, tests, victim (build only), attacker (build only)
bench.yaml                    run configuration
runner/                       Python 3.12 package "bench" (orchestrator, adapters, scoring, report)
  Dockerfile
  pyproject.toml
  bench/
    model.py                  shared dataclasses (contract: only additive fields with defaults)
    adapters/base.py          ToolAdapter / ContainerSpec / Mount (contract)
    adapters/<tool>.py        one adapter per tool, class named Adapter
    config.py                 bench.yaml loader
    scenarios.py              scenario discovery and validation
    docker_backend.py         container lifecycle, exec, log streaming, stats
    orchestrator.py           phases: baseline, control, per tool/profile deploy, attack, collect
    metrics.py                workload execution and overhead computation
    scoring.py                alert attribution, coverage, latency, false positives
    report.py                 Markdown and JSON reports
    __main__.py               CLI
  tests/                      pytest suite, fixtures/<tool>/*.jsonl real alert samples
scenarios/<id>/               scenario.yaml + run.sh + check.sh + cleanup.sh
victim/                       victim image (scenario target and workload host)
attacker/                     attacker image (HTTP payload server, listener)
workloads/                    overhead workloads compiled or copied into the victim image
tools/<tool>/
  default/                    upstream default configuration and rules
  tuned/                      tuned configuration and rules
  enforce/                    tuned rules with blocking/kill actions (tools that can respond only)
  Dockerfile                  only when no upstream image exists
  operational.yaml            operational assessment
  README.md                   how the tool is deployed and how alerts are collected
deploy/kubernetes/            Kubernetes mode (backend: kubernetes, runner/bench/k8s_backend.py, see its README)
results/<run_id>/             raw and scored results
```

## Scenario contract

`scenarios/<id>/scenario.yaml`:

```yaml
id: t1059-004-reverse-shell
name: Reverse shell with bash
kind: attack                  # attack | benign
tactic: execution             # ATT&CK tactic slug, null for benign
technique: T1059.004          # ATT&CK technique id, null for benign
description: Opens a bash reverse shell to the attacker container.
timeout: 30
requires: []                  # subset of: privileged, attacker
```

`scenarios/<id>/run.sh` is executed with `sh /scenarios/<id>/run.sh` inside the victim container, as root, with:

- `BENCH_MARKER`: unique token for this execution; scripts embed it in created file names or arguments when possible to ease attribution.
- `BENCH_ATTACKER`: hostname of the attacker container (`attacker`).

Immediately before the first action a detection tool is expected to see, the script prints exactly one line on stdout: `BENCH_ACTION <unix epoch seconds with fractional part>`. It comes after all setup and, for multi-step behaviors, before the first step of the malicious chain; benign scenarios print it before their main activity. If several are printed, the first one wins. Alert latency is measured from this timestamp, falling back to `run.started_at` when the line is missing.

Each scenario also provides `check.sh` and `cleanup.sh`, executed by the runner with `sh` in the same container and with the same environment, in the order `run.sh`, `check.sh`, `cleanup.sh`. `run.sh` performs the behavior and leaves its effects in place (no cleanup trap); it first calls its own `cleanup.sh` so that a previous partial run does not affect it, backs up under `/tmp/bench-$BENCH_MARKER/` every existing file it is about to modify, and writes there any evidence of transient effects. It must finish within `timeout`, and its exit code is informative only, since an `enforce` profile may kill it half-way. `check.sh` exits 0 when the scenario's effect was achieved and 1 otherwise; it only inspects state, never performs the behavior, is fast and prints nothing. For benign scenarios it checks that the benign task completed, which measures the collateral damage of enforcement. `cleanup.sh` removes everything the scenario created and restores what it modified; it is idempotent, always exits 0, and works whether `run.sh` completed, was killed, or never ran.

The loader (`runner/bench/scenarios.py`) rejects a scenario directory without the three scripts. The runner gives `check.sh` 30 s and `cleanup.sh` 60 s. A `check.sh` exit code other than 0 or 1 (timeout, exec failure) records `effect_achieved: null`; a non-zero `cleanup.sh` exit is recorded (`cleanup_exit_code`, deployment `cleanup_failures` and `errors`) but does not stop the run. In Docker mode `scenarios/` is bind-mounted read-only at `/scenarios`; in Kubernetes mode the scripts are baked into the victim image (`COPY scenarios/ /scenarios/` in `victim/Dockerfile`), so the image must be rebuilt after a scenario change.

Scenarios requiring `privileged` run in a privileged victim container; others run in an unprivileged one. The victim and attacker containers are created at the start of every phase (control and each tool/profile deployment) and removed at its end, so effects left by a killed or blocked scenario under one profile never leak into the next.

## Workload contract

Workloads live in the victim image under `/opt/bench/bin/`. Each one is invoked as `<binary> --duration <seconds>` and prints exactly one JSON line on stdout:

```json
{"name": "syscall", "metrics": {"getpid_p50_ns": 120.0, "getpid_p99_ns": 410.0, "openat_ops_per_sec": 251000.0}}
```

Overhead is the relative difference of every metric between the baseline run (no tool) and the run with the tool deployed.

## Tool adapter contract

See `runner/bench/adapters/base.py`. Each tool runs as one container started from `ContainerSpec`. All bind mount sources are host paths, built from `host_repo_root` and `host_output_dir`, because the runner talks to the host Docker daemon through its socket.

Alerts are read from the tool container logs (stdout and stderr) unless `alerts_file` is set, in which case the runner tails `<host_output_dir>/<alerts_file>`. Every line is passed to `Adapter.parse(line, emitted_at)` where `emitted_at` is the Docker log timestamp (or read time for files). `parse` returns `None` for anything that is not a security alert.

The tool is considered ready when `ready_pattern` (regex) appears in its logs and, when `ready_url` is set, that URL answers HTTP 200 (both conditions, within `startup_timeout`). The runner then sleeps `settle_seconds` (default 5 s) before workloads and scenarios, because some tools (Kunai, Pulsar, Falco) report readiness before every probe is attached. `ready_url` is probed from the runner process without proxy: tools use the host network and the `bench` Compose service runs with `network_mode: host`, so `127.0.0.1` is the host loopback. In Kubernetes mode `ready_url` is ignored (the pod readiness and log pattern are used). Images without `build_context` are pulled when missing locally.

Optional adapter hooks (defaults in `base.py`):

- `is_enforcement(alert) -> bool` (default `False`): the alert reports an enforcement actually applied (KubeArmor `Block` with a non-`Passed` result, Kunai `detection.actions` containing `kill`, Tetragon `KPROBE_ACTION_SIGKILL`/`KPROBE_ACTION_OVERRIDE`). Adapters may already fill `Alert.action` with the action label; otherwise the runner sets `action: "enforce"` for alerts where the hook returns true. Scoring treats any alert with a non-null `action` as an enforcement alert.
- `enforcement_check(log_lines) -> bool | None` (default `None`, unknown): called on all collected lines (container logs and alerts file) of an `enforce` deployment to verify it really enforced (KubeArmor: `Initialized BPF-LSM Enforcer` -> true, `Initialized AppArmor Enforcer`/`Disabled KubeArmor Enforcer` -> false; Kunai: at least one `sending SIGKILL to PID=` line -> true). Stored as `enforcement_verified` in the deployment metadata.
- `confirmed_enforcements(lines) -> list[float]` (default `[]`): timestamps of log lines confirming an enforcement outcome (Kunai kill log lines); scoring counts them per scenario window.

## Profiles and phases

Profiles are `default`, `tuned` and `enforce`; a tool lists the ones it supports in `Adapter.profiles` and unsupported ones are skipped. `enforce` is the tuned rule set with blocking or kill actions, for tools that can respond (KubeArmor, Kunai, Tetragon). With `control_scenarios: true` (default) the runner first runs every scenario `repetitions` times with no tool deployed; these runs are stored in `runs.jsonl` with `tool: none` and `profile: control` and establish which scenarios actually achieve their effect on this host.

## Attribution and scoring

An alert is attributed to a scenario run when:

1. `run.started_at <= alert.emitted_at <= run.ended_at + grace_seconds`, and
2. the alert's `event_at`, when known, is not later than `run.ended_at + 1 s` (events produced by `check.sh`, `cleanup.sh` or the next run are not credited to the run), and
3. the alert identifies the victim container (`container_id` prefix match with the victim id, or `container_name` equal to the victim name), or `BENCH_MARKER` appears anywhere in the serialized raw alert.

Per scenario and repetition:

- attack scenario with at least one attributed alert: detected (true positive), otherwise missed (false negative);
- benign scenario with at least one attributed alert: false positive;
- alert latency: `min(alert.emitted_at) - reference` over attributed alerts, where `reference` is `run.action_at` (the `BENCH_ACTION` timestamp) when present, else `run.started_at` (`latency_reference` is `action` or `start`);
- `effect_achieved` from `check.sh`, used with the control runs for prevention and collateral damage (see `docs/methodology.md`).

Alerts from the victim container outside any scenario window are counted as background noise.

## Results layout

```
results/<run_id>/
  metadata.json               host, kernel, docker, tool versions, config hashes, bench.yaml, control, deployments
  runs.jsonl                  ScenarioRun records (control runs with tool "none", profile "control")
  alerts/<tool>-<profile>.jsonl  normalized Alert records including raw and action
  raw/<tool>-<profile>/container.log  every container log line (stdout and stderr) with its timestamp
  workloads.jsonl             WorkloadResult records
  score.json                  scored results
  report.md                   human readable report
```

Fields added to the contract (all additive with defaults): `ScenarioRun.action_at`, `effect_achieved`, `check_exit_code`, `cleanup_exit_code`; `Alert.action`; `WorkloadResult.host_cpu_percent` (host-wide CPU busy % sampled from `/proc/stat` every second during the workload, Docker backend only, empty in Kubernetes mode); `ContainerSpec.settle_seconds`, `ready_url`. Each `metadata.json` deployment also records `container_started_at`, `time_to_ready`, `log_lines`, `log_bytes`, `alerts_file_lines`, `alerts_file_bytes`, `cleanup_failures`, `enforce`, `enforcement_verified` (true, false or null), `enforcement_alerts` and `confirmed_enforcements` (timestamps); `metadata.control` has the same shape for the control phase.
