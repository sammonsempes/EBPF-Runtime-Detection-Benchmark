# eBPF Runtime Detection Benchmark

An open, reproducible framework for evaluating eBPF-based runtime threat detection tools on Linux and Kubernetes.

The benchmark runs a standardized set of attack scenarios, mapped to [MITRE ATT&CK](https://attack.mitre.org/) techniques, against each tool and measures how well and at what cost it detects them, and, for tools that can block, how well it prevents them.

The goal is to provide transparent, vendor-neutral results that help security teams choose the right tool for their environment. All scenarios, configurations, and raw results are included so anyone can reproduce or extend the benchmark.

## What is measured

| Dimension | Metrics |
|---|---|
| **Detection coverage** | Behaviors detected, missed, or falsely flagged |
| **Performance overhead** | CPU, memory, and syscall latency impact on the host |
| **Alert latency** | Time between the malicious event and the generated alert |
| **Response effectiveness** | Attacks actually prevented by blocking profiles, and benign activity broken by them |
| **Operational aspects** | Ease of deployment, rule customization, and output quality |

## Tools under evaluation

| Tool | Version | Profiles | Can block |
|---|---|---|---|
| [Falco](https://github.com/falcosecurity/falco) | 0.45.0 | default, tuned | no |
| [Tetragon](https://github.com/cilium/tetragon) | 1.7.1 | default, tuned, enforce | yes (Sigkill) |
| [Tracee](https://github.com/aquasecurity/tracee) | 0.24.1 | default, tuned | no |
| [KubeArmor](https://github.com/kubearmor/KubeArmor) | 1.7.5 | default, tuned, enforce | yes (BPF-LSM) |
| [Kunai](https://github.com/kunai-project/kunai) | 0.6.2 | default, tuned, enforce | kill after the event (asynchronous) |
| [Pulsar](https://github.com/exein-io/pulsar) | 0.10.1 | default, tuned | no |

- **default**: what an operator gets out of the box (upstream configuration and rules). Kunai ships no detection rules, so its default profile detects nothing by design.
- **tuned**: default plus rules written for the behaviors of the scenario catalog. They target behaviors, never benchmark-specific tokens, but they were written knowing the scenarios: see [Limitations](#limitations).
- **enforce**: tuned rules with the tool's blocking action on malicious behaviors only.

Each tool's deployment, profiles and alert definition are documented in `tools/<tool>/README.md`.

## Results

Run `20261022T204058Z`, 2026-10-22, single host. Full report: [`results/20261022T204058Z/report.md`](results/20261022T204058Z/report.md).

| Host | Value |
|---|---|
| Kernel | 6.6.87.2-microsoft-standard-WSL2 |
| OS | Ubuntu 24.04 LTS, Docker 29.7.1, cgroup v2 |
| CPU / memory | 8 vCPUs, 15.4 GiB |
| Catalog | 24 attack scenarios, 6 benign scenarios, 5 repetitions each |
| Control | every scenario achieved its effect 5/5 times without any tool: all 30 scenarios are valid |

### Detection coverage

Recall: attack scenarios detected in a majority of the 5 repetitions, out of 24. FP rate: benign scenarios with at least one alert, out of 6. Latency: median time from the scenario's `BENCH_ACTION` timestamp to the first attributed alert.

| Tool | Profile | Recall | FP rate | Median latency |
|---|---|---|---|---|
| Tetragon | tuned | 100.0% | 16.7% | 0.111 s |
| Tetragon | enforce | 100.0% | 16.7% | 0.120 s |
| Falco | tuned | 100.0% | 33.3% | 0.002 s |
| Kunai | tuned | 100.0% | 33.3% | 0.090 s |
| Kunai | enforce | 100.0% | 33.3% | 0.096 s |
| Tracee | tuned | 91.7% | 33.3% | 0.002 s |
| KubeArmor | default | 91.7% | 100.0% | 0.096 s |
| KubeArmor | tuned | 83.3% | 3.3% | 0.098 s |
| Falco | default | 45.8% | 16.7% | 0.002 s |
| Tetragon | default | 45.8% | 16.7% | 0.098 s |
| Tracee | default | 20.8% | 16.7% | 0.005 s |
| Pulsar | default | 16.7% | 16.7% | 0.004 s |
| Pulsar | tuned | 16.7% | 16.7% | 0.105 s |
| KubeArmor | enforce † | 4.2% | 3.3% | 0.172 s |
| Kunai | default | 0.0% | 0.0% | — |

† KubeArmor enforce is not valid on this host, see [Response effectiveness](#response-effectiveness).

Reading notes:

- **KubeArmor default** reaches 91.7% recall only because the upstream `harden-shell-history-mod` policy fires on every shell started in the container; the same rule flags all 6 benign scenarios (100% FP rate). Its recall is not meaningful on its own.
- **Pulsar** alerts carried no container identity on this host (0% of alerts, see operational metrics), so they could only be attributed through the scenario marker. Its recall is a lower bound.
- **Falco, Tracee and Pulsar default** emit alerts in 1–5 ms; Tetragon, KubeArmor and Kunai take 60–180 ms. Tetragon and KubeArmor alerts are read from a file polled every 200 ms here, so their latency is an upper bound.
- Out of the box, Falco and Tetragon cover 11 of 24 techniques, Tracee 5, Pulsar 4, Kunai none.

Per-scenario coverage, the rules that matched, and the rules behind each false positive are in the [full report](results/20261022T204058Z/report.md#coverage-matrix).

### Response effectiveness

Prevention: attack scenarios whose effect, checked by the scenario's `check.sh`, was not achieved in a majority of repetitions, while it was achieved in every control run. Collateral damage: benign scenarios broken by enforcement.

| Tool | Mechanism | Prevention | Detected, not prevented (runs) | Collateral damage | Median response latency | Enforcement verified |
|---|---|---|---|---|---|---|
| Tetragon | Sigkill at the hook | **91.7% (22/24)** | 10 | 0 | 0.121 s | not checkable |
| Kunai | kill after the event | 0.0% (0/24) | 120 | 0 | 0.096 s | yes |
| KubeArmor | BPF-LSM | invalid on this host | 5 | 0 | — | no |
| Falco, Tracee, Pulsar | detection only | — | — | — | — | — |

- **Tetragon** blocked everything except system and container discovery (T1082, T1613), which its enforce profile deliberately only observes.
- **Kunai** raised 343 alerts carrying its kill action and its logs confirm the kills, but the kill happens after the syscall has completed: the effect landed in all 120 attack runs. Asynchronous response is not prevention.
- **KubeArmor** needs BPF-LSM to block containers started outside Kubernetes, and the WSL2 kernel does not offer it: the enforcer was not verified, nothing was blocked and almost nothing was reported (0.12 alerts/min versus 33 in tuned). Run it on a kernel booted with `lsm=...,bpf` for a valid result.

### Performance overhead

Overhead is relative to the baseline without any tool; positive always means worse. Tool CPU is in percent of one core.

| Tool | Profile | Tool CPU (median) | Tool memory (median) | Host CPU Δ | `exec` throughput | `openat` p50 latency | Syscall latency (median of metrics) |
|---|---|---|---|---|---|---|---|
| Falco | default | 3.9% | 67 MiB | +1.2 pp | +1.3% | +39.4% | +6.2% |
| Falco | tuned | 5.3% | 68 MiB | +1.9 pp | +0.7% | +38.6% | +2.4% |
| Tetragon | default | 2.0% | 388 MiB | +1.5 pp | +29.4% | -0.9% | -0.3% |
| Tetragon | tuned | 2.3% | 378 MiB | +1.5 pp | +37.4% | +68.3% | +81.6% |
| Tetragon | enforce | 2.1% | 375 MiB | +1.8 pp | +36.7% | +67.9% | +82.0% |
| Tracee | default | 15.6% | 125 MiB | +5.1 pp | +9.3% | +419.3% | +22.7% |
| Tracee | tuned | 18.6% | 127 MiB | +5.7 pp | +12.5% | +482.8% | +36.7% |
| KubeArmor | default | 19.6% | 87 MiB | +3.9 pp | +10.5% | +345.4% | +3.9% |
| KubeArmor | tuned | 19.7% | 108 MiB | +3.8 pp | +10.8% | +353.5% | +3.9% |
| KubeArmor | enforce † | 32.0% | 89 MiB | +8.5 pp | +76.0% | +367.9% | +301.0% |
| Kunai | default | 13.8% | 76 MiB | +12.8 pp | +62.7% | +144.4% | +298.9% |
| Kunai | tuned | 9.4% | 77 MiB | +4.3 pp | +54.1% | +139.7% | +245.0% |
| Kunai | enforce | 12.3% | 107 MiB | +8.8 pp | +76.1% | +309.5% | +623.7% |
| Pulsar | default | 61.5% | 301 MiB | +32.3 pp | +86.2% | +1429.8% | +683.9% |
| Pulsar | tuned | 155.8% | 572 MiB | +50.0 pp | +89.2% | +1323.1% | +759.3% |

- **Falco** has the lowest overall cost. **Tetragon** uses little CPU but the most memory of the low-overhead tools; its tuned and enforce profiles add about 80% median syscall latency, and all its profiles raise `read` latency sharply (p50 +900% to +2,000%) through their file access hooks.
- **KubeArmor (default and tuned), Kunai default and Pulsar** write their telemetry to stdout in this setup (83,000 to 207,000 log lines per minute, up to 1.7 GiB per deployment), collected by Docker's logging driver. Part of their overhead is the cost of that pipeline rather than of the probes alone.
- The baseline `fileio` run, which ran first, was slower than most later runs, so `fileio` overheads come out negative for several tools and are omitted here. Per-metric numbers, including `fileio`, are in the [full report](results/20261022T204058Z/report.md#overhead).

### Operational aspects

Rubric scores (1–5) are defined in [docs/methodology.md](docs/methodology.md) and justified with upstream facts in each `tools/<tool>/operational.yaml`. The measured columns come from this run.

| Tool | Deployment | Rule customization | Output quality | Time to ready | Alerts / min (tuned) | Alerts with container identity (tuned) |
|---|---|---|---|---|---|---|
| Falco | 5 | 5 | 5 | 0.07 s | 92 | 99.9% |
| Tetragon | 5 | 4 | 4 | 20.8 s | 4,297 | 22.1% |
| Tracee | 4 | 3 | 4 | 1.8 s | 114 | 100.0% |
| KubeArmor | 3 | 4 | 4 | 3.0 s | 33 | 100.0% |
| Kunai | 3 | 4 | 4 | 1.4 s | 32 | 96.4% |
| Pulsar | 4 | 4 | 4 | 0.26 s | 157 | 0.0% |

- **Tetragon**'s default and library policies observe the whole host, which explains about 4,000 alerts per minute, mostly from processes other than the victims.
- Time to ready is measured until each tool's readiness log line. Falco prints its line before its probes attach, so the runner always waits 5 more seconds before starting.

### Integration issues found on this host

Fixes that were needed to run each pinned release, kept in the repository:

- **Pulsar 0.10.1**: the official image `ghcr.io/exein-io/pulsar:v0.10.1` does not start (`GLIBC_2.38 not found`); `tools/pulsar/Dockerfile` reuses its binary and default rules on `ubuntu:24.04`.
- **Tetragon 1.7.1**: Override is unavailable without `CONFIG_BPF_KPROBE_OVERRIDE` (WSL2), so the enforce profile uses Sigkill only; a policy cannot mix kprobes and tracepoints.
- **Tracee 0.24.1**: policy data filters only support equality, and the health endpoint did not answer with the documented configuration; readiness uses the `tracee_info` event.
- **Kunai 0.6.2**: fails without `/sys/class/dmi/id/product_uuid` (`failed to read host_uuid`); the configurations set a fixed `host_uuid`.

## Limitations

- **Single host, WSL2 kernel.** Results come from one machine with a Microsoft WSL2 kernel, which lacks BPF-LSM and the kprobe override helper. Absolute numbers and the enforcement results of KubeArmor and Tetragon may differ on a regular Linux host.
- **Tuning bias.** The tuned and enforce profiles were written by the benchmark authors knowing the scenario catalog. They show what each rule language can express, not what a team would reach on unknown attacks. The default profiles are the unbiased comparison.
- **Scenario realism.** Scenarios are short, simulated behaviors run in containers; they do not reproduce multi-stage intrusions or evasion.
- **Attribution.** Alerts are credited to a scenario through container identity or the scenario marker. Tools that report no container identity, like Pulsar here, are under-credited.
- **Raw alert files are not published.** `alerts/*.jsonl` contain host-wide events of the machine that ran the benchmark, not only the victim containers, and the Tetragon files weigh 73–95 MB each. `runs.jsonl`, `workloads.jsonl`, `metadata.json`, `score.json` (with the rules matched per run) and `report.md` are published; re-running the benchmark regenerates the alert files.
- **Kubernetes mode** (`deploy/kubernetes/`) is implemented and unit-tested but these results come from Docker mode only.

See [docs/methodology.md](docs/methodology.md#threats-to-validity) for the full list.

## Quick start

Requirements: a Linux host with a BTF-enabled kernel (5.8+), Docker Engine with Compose v2. Run on a dedicated machine or VM: the scenarios modify the victim containers and some tools run privileged.

```bash
docker compose build          # runner, victim, attacker, Kunai and Pulsar images
docker compose up tests       # unit tests
docker compose up -d bench    # full benchmark described in bench.yaml (several hours)
docker compose logs -f bench
```

Results are written to `results/<run_id>/`: `metadata.json`, `runs.jsonl`, `alerts/`, `workloads.jsonl`, `score.json` and `report.md`. Scoring and the report can be recomputed offline from these files.

Behind a TLS-intercepting proxy, point `BENCH_CA_DIR` at a directory holding the proxy CA certificates before building.

## Repository layout

```
bench.yaml            run configuration (tools, profiles, scenarios, repetitions)
compose.yaml          runner, tests, victim, attacker and tool image builds
runner/               Python orchestrator, tool adapters, scoring and report
scenarios/<id>/       scenario.yaml, run.sh, check.sh, cleanup.sh
victim/, attacker/    target and attacker images
workloads/            C workloads for overhead (syscall, exec, fileio)
tools/<tool>/         per-profile configuration and rules, operational assessment
deploy/kubernetes/    Kubernetes mode (kind, Helm values, manifests)
docs/                 architecture, methodology, scenario catalog
results/              published runs
```

- [docs/architecture.md](docs/architecture.md): contracts between the runner, scenarios and tool adapters.
- [docs/methodology.md](docs/methodology.md): phases, attribution rules, metric definitions, scoring rubric.
- [docs/scenarios.md](docs/scenarios.md): every scenario, its ATT&CK technique and the telemetry it produces.

## Contributing

Contributions are welcome:

- new attack scenarios mapped to ATT&CK techniques,
- support for additional eBPF detection tools,
- improved rules or configurations for an existing tool,
- runs on other kernels and hosts,
- corrections to results or methodology.

Open an issue or a pull request describing the change and, for scenarios, the expected detection behavior. [docs/methodology.md](docs/methodology.md) explains how to add a scenario or a tool.

## Disclaimer

Attack scenarios are intended for isolated lab environments only. Do not run them on production systems or on hosts you are not authorized to test.
