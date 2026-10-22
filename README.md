# eBPF Runtime Detection Benchmark

An open, reproducible framework for evaluating eBPF-based runtime threat detection tools on Linux and Kubernetes.

The benchmark runs a standardized set of attack scenarios, mapped to [MITRE ATT&CK](https://attack.mitre.org/) techniques, against each tool and measures how well and at what cost it detects them.

The goal is to provide transparent, vendor-neutral results that help security teams choose the right tool for their environment. All scenarios, configurations, and raw results are included so anyone can reproduce or extend the benchmark.

## What is measured

| Dimension | Metrics |
|---|---|
| **Detection coverage** | Behaviors detected, missed, or falsely flagged |
| **Performance overhead** | CPU, memory, and syscall latency impact on the host |
| **Alert latency** | Time between the malicious event and the generated alert |
| **Operational aspects** | Ease of deployment, rule customization, and output quality |

## Tools under evaluation

| Tool | Maintainer | Scope |
|---|---|---|
| [Falco](https://github.com/falcosecurity/falco) | CNCF | Linux, Kubernetes |
| [Tetragon](https://github.com/cilium/tetragon) | Cilium / CNCF | Linux, Kubernetes |
| [Tracee](https://github.com/aquasecurity/tracee) | Aqua Security | Linux, Kubernetes |
| [KubeArmor](https://github.com/kubearmor/KubeArmor) | CNCF | Linux, Kubernetes |
| [Kunai](https://github.com/kunai-project/kunai) | Kunai project | Linux |
| [Pulsar](https://github.com/exein-io/pulsar) | Exein | Linux, IoT |

Each tool is evaluated with its default rule set first, then with tuned rules, so results show both out-of-the-box and best-effort coverage.

## Methodology

1. **Baseline** — run the workload on a clean host without any detection tool to capture reference CPU, memory, and syscall latency.
2. **Deploy** — install one tool at a time with a versioned, committed configuration.
3. **Attack** — execute the scenario suite; every scenario records a precise start timestamp.
4. **Collect** — gather alerts from the tool output and resource metrics from the host.
5. **Score** — match alerts to scenarios to compute true positives, false negatives, false positives, and alert latency.
6. **Repeat** — run each scenario several times to report medians and variance rather than single values.

### Scenario mapping

Each scenario targets one MITRE ATT&CK technique, for example:

| Tactic | Example technique |
|---|---|
| Execution | T1059 — Command and Scripting Interpreter |
| Persistence | T1053 — Scheduled Task/Job |
| Privilege Escalation | T1611 — Escape to Host |
| Defense Evasion | T1070 — Indicator Removal |
| Credential Access | T1552 — Unsecured Credentials |
| Discovery | T1613 — Container and Resource Discovery |
| Command and Control | T1105 — Ingress Tool Transfer |

Benign workloads are also run to measure false positives under realistic noise.

## Reproducibility

- Tool versions, kernel version, and host specs are pinned and recorded with every run.
- Configurations and rules used for each tool are committed alongside results.
- Raw alerts and metrics are stored as-is, so scoring can be re-run or audited independently.

## Contributing

Contributions are welcome:

- new attack scenarios mapped to ATT&CK techniques,
- support for additional eBPF detection tools,
- improved rules or configurations for an existing tool,
- corrections to results or methodology.

Open an issue or a pull request describing the change and, for scenarios, the expected detection behavior.

## Disclaimer

Attack scenarios are intended for isolated lab environments only. Do not run them on production systems or on hosts you are not authorized to test.
