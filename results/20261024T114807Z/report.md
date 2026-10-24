# eBPF runtime detection benchmark: 20261024T114807Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261024T114807Z |
| grace_seconds | 10.0 |
| host.architecture | amd64 |
| host.backend | kubernetes |
| host.container_runtime | containerd://2.1.1 |
| host.cpus | 8 |
| host.kernel | 6.6.87.2-microsoft-standard-WSL2 |
| host.kube_context | kind-ebpf-bench |
| host.kubelet_version | v1.33.1 |
| host.kubernetes_version | v1.33.1 |
| host.memory_bytes | 16540467200.0 |
| host.namespace | ebpf-bench |
| host.node | ebpf-bench-control-plane |
| host.operating_system | Debian GNU/Linux 12 (bookworm) |
| host.runner_python | 3.12.14 |
| config.backend | kubernetes |
| config.control_scenarios | True |
| config.grace_seconds | 10 |
| config.idle_seconds | 3 |
| config.kubernetes | {"context": "kind-ebpf-bench", "kubeconfig": null, "namespace": "ebpf-bench", "node": null} |
| config.max_log_bytes | 2147483648 |
| config.max_log_lines | 5000000 |
| config.overhead | {"duration_seconds": 30, "enabled": true, "repetitions": 3, "workloads": ["syscall", "exec", "fileio"]} |
| config.profiles | ["default", "tuned"] |
| config.repetitions | 5 |
| config.results_dir | results |
| config.scenarios | all |
| config.tools | ["falco", "tracee", "kunai", "pulsar"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| falco | 0.45.0 | ok | default, tuned | default: a9318548d127, tuned: 18d84b1b69aa |
| kunai | 0.6.2 | ok | default, tuned | default: ea10f4f706e7, tuned: 3c0a05fb5002 |
| pulsar | 0.10.1 | failed | default, tuned | default: 9cb2665a655e, tuned: dd1914d53753 |
| tracee | 0.24.1 | ok | default, tuned | default: c5763fb3419e, tuned: 3bffc520aa3d |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | tuned | 100.0% | 100.0% | 33.3% | 0.003s | 0 | — | — | +7.1% |
| kunai | tuned | 100.0% | 100.0% | 33.3% | 0.076s | 0 | — | — | +28.3% |
| tracee | tuned | 91.7% | 91.7% | 33.3% | 0.002s | 0 | — | — | +46.9% |
| falco | default | 45.8% | 45.8% | 16.7% | 0.003s | 0 | — | — | +9.6% |
| tracee | default | 20.8% | 20.8% | 16.7% | 0.006s | 0 | — | — | +35.5% |
| kunai | default | 0.0% | 0.0% | 0.0% | — | 0 | — | — | +76.8% |
| pulsar | default | — | — | — | — | 0 | — | — | +75.1% |
| pulsar | tuned | — | — | — | — | 0 | — | — | — |

## Control runs

Every scenario is run without any tool deployed; a scenario is valid when `check.sh` reports its effect as achieved in a majority of control repetitions. Invalid scenarios are excluded from prevention metrics and flagged (invalid) in detection tables.

| Scenario | Kind | Repetitions | Effect achieved | Effect unknown | Non-zero exits | Validity |
| --- | --- | --- | --- | --- | --- | --- |
| benign-admin-commands | benign | 5 | 5/5 | 0 | 0 | ✅ valid |
| benign-backup | benign | 5 | 5/5 | 0 | 0 | ✅ valid |
| benign-compile | benign | 5 | 5/5 | 0 | 0 | ✅ valid |
| benign-log-rotation | benign | 5 | 5/5 | 0 | 0 | ✅ valid |
| benign-package-query | benign | 5 | 5/5 | 0 | 0 | ✅ valid |
| benign-web-server | benign | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1003-008-shadow-read | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1036-005-masquerading | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1046-network-scan | attack | 5 | 0/5 | 0 | 5 | ❌ invalid |
| t1048-exfiltration-http | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1053-003-cron-persistence | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1059-004-reverse-shell | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1059-006-python-exec | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1070-002-clear-logs | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1070-003-clear-history | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1082-system-discovery | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1098-004-ssh-authorized-keys | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1105-ingress-tool-transfer | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1136-001-create-account | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1222-002-permission-modification | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1485-data-destruction | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1496-cryptominer | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1543-002-systemd-service | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1547-006-kernel-module | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1548-001-setuid-binary | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1552-001-credentials-in-files | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1552-007-container-api | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1611-escape-to-host | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1613-container-discovery | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
| t1620-fileless-exec | attack | 5 | 5/5 | 0 | 0 | ✅ valid |

Invalid scenarios: t1046-network-scan.

## Coverage matrix

✅ detected in a majority of repetitions, ⚠️ detected in some repetitions, ❌ missed, — not run. In enforce columns 🛡️ means prevented in a majority of repetitions (effect not achieved while the control run achieved it), ✅/⚠️ detected only; † marks a deployment whose enforcement could not be verified. (invalid) marks scenarios whose effect was not achieved in the control runs.

| Tactic | Scenario | Technique | falco/default | falco/tuned | kunai/default | kunai/tuned | pulsar/default | pulsar/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 |
| execution | t1059-006-python-exec | T1059.006 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| persistence | t1053-003-cron-persistence | T1053.003 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ❌ 0/5 |
| persistence | t1136-001-create-account | T1136.001 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| persistence | t1543-002-systemd-service | T1543.002 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ❌ 0/5 |
| persistence | t1547-006-kernel-module | T1547.006 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1611-escape-to-host | T1611 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 |
| defense-evasion | t1036-005-masquerading | T1036.005 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-002-clear-logs | T1070.002 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-003-clear-history | T1070.003 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1222-002-permission-modification | T1222.002 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1620-fileless-exec | T1620 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 |
| credential-access | t1003-008-shadow-read | T1003.008 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-001-credentials-in-files | T1552.001 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-007-container-api | T1552.007 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 |
| discovery | t1046-network-scan (invalid) | T1046 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| discovery | t1082-system-discovery | T1082 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| discovery | t1613-container-discovery | T1613 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| command-and-control | t1105-ingress-tool-transfer | T1105 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| exfiltration | t1048-exfiltration-http | T1048 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| impact | t1485-data-destruction | T1485 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |
| impact | t1496-cryptominer | T1496 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | — | — | ❌ 0/5 | ✅ 5/5 |

### Coverage per tactic

| Tactic | falco/default | falco/tuned | kunai/default | kunai/tuned | pulsar/default | pulsar/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | 1/2 | 2/2 | 0/2 | 2/2 | — | — | 1/2 | 2/2 |
| persistence | 1/5 | 5/5 | 0/5 | 5/5 | — | — | 1/5 | 3/5 |
| privilege-escalation | 1/2 | 2/2 | 0/2 | 2/2 | — | — | 1/2 | 2/2 |
| defense-evasion | 3/5 | 5/5 | 0/5 | 5/5 | — | — | 1/5 | 5/5 |
| credential-access | 2/3 | 3/3 | 0/3 | 3/3 | — | — | 1/3 | 3/3 |
| discovery | 0/3 | 3/3 | 0/3 | 3/3 | — | — | 0/3 | 3/3 |
| command-and-control | 0/1 | 1/1 | 0/1 | 1/1 | — | — | 0/1 | 1/1 |
| exfiltration | 1/1 | 1/1 | 0/1 | 1/1 | — | — | 0/1 | 1/1 |
| impact | 2/2 | 2/2 | 0/2 | 2/2 | — | — | 0/2 | 2/2 |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | falco/default | falco/tuned | kunai/default | kunai/tuned | pulsar/default | pulsar/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benign-admin-commands | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | — | — | ✅ 0/5 | ⚠️ 5/5 |
| benign-backup | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | ✅ 0/5 | ✅ 0/5 |
| benign-compile | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | — | — | ⚠️ 5/5 | ⚠️ 5/5 |
| benign-log-rotation | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | — | — | ✅ 0/5 | ✅ 0/5 |
| benign-package-query | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | ✅ 0/5 | ✅ 0/5 |
| benign-web-server | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | — | — | ✅ 0/5 | ✅ 0/5 |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | default | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-log-rotation | Log File Deleted or Truncated |
| kunai | tuned | benign-admin-commands | discovery.system.information |
| kunai | tuned | benign-web-server | download.to.tmpfs |
| tracee | default | benign-compile | New executable dropped |
| tracee | tuned | benign-admin-commands | detect-container-discovery |
| tracee | tuned | benign-compile | New executable dropped |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | falco/default | falco/tuned | kunai/default | kunai/tuned | pulsar/default | pulsar/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1059-004-reverse-shell | 0.003s / 0.004s | 0.003s / 0.003s | — | 0.042s / 0.111s | — | — | 0.004s / 0.005s | 0.002s / 0.002s |
| t1059-006-python-exec | — | 0.015s / 0.016s | — | 0.120s / 0.127s | — | — | — | 0.015s / 0.016s |
| t1053-003-cron-persistence | — | 0.001s / 0.002s | — | 0.083s / 0.124s | — | — | 0.001s / 0.002s | 0.001s / 0.003s |
| t1098-004-ssh-authorized-keys | — | 0.003s / 0.006s | — | 0.087s / 0.109s | — | — | — | — |
| t1136-001-create-account | — | 0.001s / 0.002s | — | 0.042s / 0.088s | — | — | — | 0.001s / 0.005s |
| t1543-002-systemd-service | — | 0.002s / 0.005s | — | 0.089s / 0.125s | — | — | — | — |
| t1547-006-kernel-module | 0.003s / 0.004s | 0.001s / 0.002s | — | 0.063s / 0.101s | — | — | — | 0.001s / 0.003s |
| t1548-001-setuid-binary | 0.004s / 0.008s | 0.003s / 0.004s | — | 0.079s / 0.107s | — | — | — | 0.003s / 0.003s |
| t1611-escape-to-host | — | 0.001s / 0.002s | — | 0.076s / 0.104s | — | — | 0.006s / 0.007s | 0.001s / 0.001s |
| t1036-005-masquerading | 0.003s / 0.006s | 0.003s / 0.005s | — | 0.062s / 0.123s | — | — | — | 0.003s / 0.003s |
| t1070-002-clear-logs | -0.021s / -0.018s | -0.025s / -0.024s | — | 0.056s / 0.097s | — | — | — | 0.003s / 0.004s |
| t1070-003-clear-history | — | 0.004s / 0.005s | — | 0.084s / 0.108s | — | — | — | 0.002s / 0.002s |
| t1222-002-permission-modification | — | 0.002s / 0.007s | — | 0.050s / 0.110s | — | — | — | 0.001s / 0.002s |
| t1620-fileless-exec | 0.009s / 0.009s | 0.009s / 0.009s | — | 0.069s / 0.105s | — | — | 0.008s / 0.010s | 0.008s / 0.009s |
| t1003-008-shadow-read | 0.002s / 0.002s | 0.003s / 0.006s | — | 0.066s / 0.123s | — | — | — | 0.001s / 0.001s |
| t1552-001-credentials-in-files | 0.002s / 0.007s | 0.001s / 0.002s | — | 0.075s / 0.109s | — | — | — | 0.003s / 0.004s |
| t1552-007-container-api | — | 0.003s / 0.007s | — | 0.051s / 0.109s | — | — | 0.009s / 0.010s | 0.003s / 0.003s |
| t1046-network-scan | — | 0.003s / 0.005s | — | 0.101s / 0.133s | — | — | — | 0.002s / 0.002s |
| t1082-system-discovery | — | 0.002s / 0.002s | — | 0.056s / 0.107s | — | — | — | 0.001s / 0.001s |
| t1613-container-discovery | — | 0.003s / 0.004s | — | 0.067s / 0.099s | — | — | — | 0.002s / 0.003s |
| t1105-ingress-tool-transfer | — | 0.009s / 0.011s | — | 0.101s / 0.105s | — | — | — | 0.012s / 0.013s |
| t1048-exfiltration-http | 0.002s / 0.003s | 0.002s / 0.003s | — | 0.088s / 0.098s | — | — | — | 0.002s / 0.004s |
| t1485-data-destruction | 0.001s / 0.002s | 0.002s / 0.007s | — | 0.076s / 0.106s | — | — | — | 0.001s / 0.002s |
| t1496-cryptominer | 0.001s / 0.002s | 0.002s / 0.006s | — | 0.076s / 0.105s | — | — | — | 0.001s / 0.001s |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| falco | default | 100.0% | 5 |
| falco | tuned | 100.0% | 5 |
| kunai | default | 100.0% | 0 |
| kunai | tuned | 100.0% | 0 |
| pulsar | default | — | 0 |
| pulsar | tuned | — | 0 |
| tracee | default | 100.0% | 0 |
| tracee | tuned | 100.0% | 0 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | detection only | — | — | — | — | — | — | — | — |
| kunai | no enforce run | — | — | — | — | — | — | kill | no |
| pulsar | detection only | — | — | — | — | — | — | — | — |
| tracee | detection only | — | — | — | — | — | — | — | — |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | falco/default | falco/tuned | kunai/default | kunai/tuned | pulsar/default | pulsar/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exec | execs_per_sec | 2,076 | 2,086 (-0.5%) | 2,104 (-1.4%) | 1,022 (+50.8%) | 1,757 (+15.4%) | 1,025 (+50.6%) | — | 1,786 (+14.0%) | 1,886 (+9.2%) |
| exec | p50_us | 440.98 | 451.82 (+2.5%) | 451.02 (+2.3%) | 878.65 (+99.2%) | 498.10 (+13.0%) | 871.02 (+97.5%) | — | 501.28 (+13.7%) | 491.55 (+11.5%) |
| exec | p99_us | 1,043 | 949.54 (-9.0%) | 908.81 (-12.9%) | 2,788 (+167.2%) | 1,369 (+31.3%) | 2,836 (+171.9%) | — | 1,163 (+11.5%) | 1,082 (+3.7%) |
| fileio | ops_per_sec | 710.00 | 717.63 (-1.1%) | 725.95 (-2.2%) | 361.13 (+49.1%) | 705.28 (+0.7%) | 332.60 (+53.2%) | — | 655.26 (+7.7%) | 685.94 (+3.4%) |
| fileio | p50_us | 1,337 | 1,319 (-1.3%) | 1,318 (-1.4%) | 2,525 (+89.0%) | 1,345 (+0.7%) | 2,652 (+98.4%) | — | 1,446 (+8.2%) | 1,389 (+3.9%) |
| fileio | p99_us | 2,310 | 2,296 (-0.6%) | 2,154 (-6.7%) | 7,801 (+237.7%) | 2,370 (+2.6%) | 8,879 (+284.4%) | — | 2,589 (+12.1%) | 2,387 (+3.3%) |
| syscall | connect_ops_per_sec | 85,512 | 76,558 (+10.5%) | 77,650 (+9.2%) | 36,349 (+57.5%) | 62,779 (+26.6%) | 19,477 (+77.2%) | — | 62,020 (+27.5%) | 61,452 (+28.1%) |
| syscall | connect_p50_ns | 4,252 | 4,693 (+10.4%) | 4,567 (+7.4%) | 9,592 (+125.6%) | 7,246 (+70.4%) | 18,558 (+336.4%) | — | 7,380 (+73.6%) | 7,405 (+74.2%) |
| syscall | connect_p99_ns | 17,821 | 18,752 (+5.2%) | 17,888 (+0.4%) | 90,074 (+405.4%) | 26,003 (+45.9%) | 153,654 (+762.2%) | — | 34,863 (+95.6%) | 32,206 (+80.7%) |
| syscall | getpid_ops_per_sec | 7,980,122 | 7,417,156 (+7.1%) | 7,473,614 (+6.3%) | 5,804,301 (+27.3%) | 7,541,874 (+5.5%) | 6,556,242 (+17.8%) | — | 7,834,072 (+1.8%) | 7,052,263 (+11.6%) |
| syscall | getpid_p50_ns | 80.00 | 90.00 (+12.5%) | 90.00 (+12.5%) | 99.00 (+23.8%) | 88.00 (+10.0%) | 96.00 (+20.0%) | — | 81.00 (+1.2%) | 97.00 (+21.2%) |
| syscall | getpid_p99_ns | 93.00 | 108.00 (+16.1%) | 107.00 (+15.1%) | 164.00 (+76.3%) | 103.00 (+10.8%) | 157.00 (+68.8%) | — | 93.00 (+0.0%) | 124.00 (+33.3%) |
| syscall | openat_ops_per_sec | 772,853 | 532,251 (+31.1%) | 540,421 (+30.1%) | 474,528 (+38.6%) | 618,934 (+19.9%) | 149,574 (+80.6%) | — | 290,850 (+62.4%) | 240,799 (+68.8%) |
| syscall | openat_p50_ns | 965.00 | 1,511 (+56.6%) | 1,467 (+52.0%) | 1,462 (+51.5%) | 1,275 (+32.1%) | 4,882 (+405.9%) | — | 2,367 (+145.3%) | 2,904 (+200.9%) |
| syscall | openat_p99_ns | 2,255 | 3,189 (+41.4%) | 3,162 (+40.2%) | 3,842 (+70.4%) | 2,807 (+24.5%) | 27,240 (+1108.0%) | — | 8,529 (+278.2%) | 10,711 (+375.0%) |
| syscall | read_ops_per_sec | 5,171,987 | 4,830,643 (+6.6%) | 4,957,876 (+4.1%) | 1,678,221 (+67.6%) | 2,365,365 (+54.3%) | 4,113,811 (+20.5%) | — | 4,022,338 (+22.2%) | 3,817,186 (+26.2%) |
| syscall | read_p50_ns | 146.00 | 159.00 (+8.9%) | 156.00 (+6.8%) | 437.00 (+199.3%) | 360.00 (+146.6%) | 173.50 (+18.8%) | — | 196.00 (+34.2%) | 212.00 (+45.2%) |
| syscall | read_p99_ns | 177.00 | 190.00 (+7.3%) | 189.00 (+6.8%) | 994.00 (+461.6%) | 450.00 (+154.2%) | 313.00 (+76.8%) | — | 242.00 (+36.7%) | 263.00 (+48.6%) |
| syscall | stat_ops_per_sec | 2,604,985 | 2,510,034 (+3.6%) | 2,501,304 (+4.0%) | 1,976,515 (+24.1%) | 2,512,002 (+3.6%) | 2,041,075 (+21.6%) | — | 2,543,293 (+2.4%) | 2,356,814 (+9.5%) |
| syscall | stat_p50_ns | 328.00 | 344.00 (+4.9%) | 345.00 (+5.2%) | 398.00 (+21.3%) | 340.00 (+3.7%) | 380.00 (+15.9%) | — | 332.00 (+1.2%) | 364.00 (+11.0%) |
| syscall | stat_p99_ns | 403.00 | 423.00 (+5.0%) | 420.00 (+4.2%) | 714.00 (+77.2%) | 423.00 (+5.0%) | 698.50 (+73.3%) | — | 424.00 (+5.2%) | 481.00 (+19.4%) |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | default | — | — | — | — | +6.3% | +6.6% | — | — | — |
| falco | tuned | — | — | — | — | +6.0% | +4.1% | — | — | — |
| kunai | default | — | — | — | — | +94.1% | +49.1% | — | — | — |
| kunai | tuned | — | — | — | — | +18.7% | +15.4% | — | — | — |
| pulsar | default | — | — | — | — | +98.0% | +50.6% | — | — | — |
| pulsar | tuned | — | — | — | — | — | — | — | — | — |
| tracee | default | — | — | — | — | +12.9% | +14.0% | — | — | — |
| tracee | tuned | — | — | — | — | +27.3% | +11.6% | — | — | — |

## Operational aspects

Scores follow the rubric in docs/methodology.md (1 worst, 5 best).

| Tool | Version | License | Deployment | Rule customization | Output quality | Deploy steps | Rule language | Custom rules | Hot reload | Output formats | Enrichment | ATT&CK mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | 0.45.0 | Apache-2.0 | 5 | 5 | 5 | 2 | YAML rules, macros and lists whose conditions use the Falco filter language over syscall and plugin fields, with exceptions, append and override | yes | yes | json, text | container, kubernetes | yes | Deployment 5: the image runs with defaults (docker/falco/Dockerfile ships /usr/bin/falco as CMD, its usage label is a single privileged docker run, falco.yaml defaults engine.kind to modern_ebpf which needs no kernel headers or driver loader, and the container plugin is enabled by the packaged config.d/falco.container_plugin.yaml); on Kubernetes the chart README documents a plain "helm install falco falcosecurity/falco". The only benchmark change is a config.d drop-in enabling json_output and disabling syslog. Modern eBPF still requires a BTF-enabled kernel. Rule customization 5: declarative YAML rules loaded from rules_files and rules.d, rule enable/disable by name or tag in falco.yaml, and watch_config_files: true reloads configuration and rules on change (plus SIGHUP and the 0.45 reload API). Output quality 5: json_output emits rule, priority, time, source, hostname, tags and output_fields (formats.cpp); upstream stable rules carry mitre_* and Txxxx tags, the container plugin adds container.* and k8s.pod.* fields, and parent/ancestor fields (proc.pname, proc.aname) are available, although ancestry depth depends on each rule's output template.  |
| kunai | 0.6.2 | GPL-3.0 | 3 | 4 | 4 | 3 | Gene YAML rules (match-on event names, $variables matching event fields with ==, ~= regex, &= flags and numeric comparisons, boolean condition, severity, ATT&CK ids), plus JSON-lines IoCs and YARA for file scans | yes | no | json | process_ancestry, container, file_hashes, user, dns | yes | Deployment 3: upstream ships a distribution-agnostic static binary (assets kunai-amd64 / kunai-aarch64 with .asc signatures and sha512.txt on the v0.6.2 release) and no container image or Kubernetes manifest; the README recommends the binary, the docs install it as a systemd service with `kunai install`. Running it in a container needs host preparation: privileged mode, host PID namespace, BTF and the bpf/debug filesystems. Steps 3 = download, chmod +x, `kunai run -r <rules>`; upstream ships no detection rule, so with the bare `sudo kunai` quickstart every event is printed and nothing is an alert. Rule customization 4: rules are declarative YAML (Gene engine) with detection, filter and dependency types, regex and flag operators, severity and actions (kill, scan-files), loaded from the config `scanner.rules` or `-r`; there is no runtime reload in 0.6.2, a restart is required (hardened mode even requires a reboot). Output quality 4: one JSON object per line (`data`, `detection`, `filter`, `info`) with process ancestors, parent command line, executable hashes, task/parent uid/gid, mount namespace and container name/type; `detection` carries rule names, tags, severity and ATT&CK ids from rule metadata. Not 5 because container context is only the UTS hostname plus a heuristic type (no container id, image or Kubernetes metadata), and the container `type` is often null for processes started after kunai. |
| pulsar | 0.10.1 | Apache-2.0 AND GPL-2.0 | 4 | 4 | 4 | 2 | YAML rule files (name, type, category, severity, description, condition) with a typed condition DSL over event header and payload (==, !=, <, >, STARTS_WITH, ENDS_WITH, CONTAINS, IN, AND/OR/NOT, is_some()) | yes | yes | json, plaintext, syslog | container, image, user | no | Deployment 4: upstream publishes release binaries (pulsard-<arch>[-static], pulsar-<arch>[-static], pulsar-install.sh) and the release workflow pushes ghcr.io/exein-io/pulsar:<tag> built from .github/docker/Dockerfile with the default config and rules baked in; the quickstart is 2 commands (install script, `pulsard`), and the image only needs the usual eBPF privileges and mounts plus /var/lib/docker for container enrichment. No Helm chart or manifest upstream. Rule customization 4: 47 default YAML rule files in rules/ (Elastic detection-rules based) loaded recursively from /var/lib/pulsar/rules; the DSL is declarative and typed but has no regex, no process ancestry and only per-event fields. hot_reload is true because the rules-engine on_config_change hook rebuilds the engine from disk when its configuration is changed at runtime through `pulsar config` / the engine API (no file watcher); this was removed after 0.10.1. Output quality 4: threat-logger prints threat events as JSON (`output_format=json`) with header (image, pid, parent_pid, uid, gid, container id/name/image/image_digest/layers, threat source/description/extra) and the typed payload; the rule name is threat.description and extra holds category, severity, description and condition. No ATT&CK ids (only a category), no ancestry beyond parent_pid, timestamps are serialized as secs/nanos since epoch. |
| tracee | 0.24.1 | Apache-2.0 | 4 | 3 | 4 | 1 | built-in Go signatures selected by YAML Policy CRDs (scope plus event rules with data, scope and return value filters); new signatures require Go code compiled as plugins | yes | no | json, table, gotemplate | container, kubernetes | yes | deployment 4: docs/docs/install/docker.md documents a single docker run (privileged, --pid=host, --cgroupns=host, os-release and /var/run mounts) and the 0.24.1 Helm chart and static manifest exist; it needs a BTF kernel and a few host mounts but no build or kernel headers. rule_customization 3: Policy CRDs (docs/docs/policies) only select events and filter them on scope and single data fields with prefix or suffix wildcards, without correlation, process ancestry or array argument matching; writing a new signature means Go code (signatures-dir loads compiled .so plugins, docs/docs/flags/signatures-dir.1.md) and policies are only read at startup. YAML detectors with CEL exist on main but are not in a release yet. output_quality 4: one JSON object per line (types/trace/trace.go) with process ids, parent pid, executable, container id/name/image and pod fields; signature findings carry metadata.Properties with Severity, Category, Technique and external_id (ATT&CK id) and the triggering event under the detectedFrom argument (pkg/events/findings/findings.go); full ancestry is only in the unreleased v1beta1 format. |

### Measured operational metrics

Measured per deployment: time from container start to readiness, alert and log volume over the deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and share of alerts carrying a container id or name. Rubric scores repeated for comparison.

| Tool | Profile | Deployment score | Output quality score | Time to ready | Alerts / min | Log lines / min | Log volume MiB | Attributed alerts | Alerts with container identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | default | 5 | 5 | 0.008s | 8.15 | 11.47 | 0.22 | 100.0% | 100.0% |
| falco | tuned | 5 | 5 | 0.007s | 47.38 | 57.21 | 1.11 | 90.2% | 97.1% |
| kunai | default | 3 | 4 | 0.005s | 0.00 | 117,069 | 2,048 | — | — |
| kunai | tuned | 3 | 4 | 0.007s | 27.92 | 19,019 | 37.76 | 90.4% | 100.0% |
| pulsar | default | 4 | 4 | 0.004s | — | — | — | — | — |
| pulsar | tuned | 4 | 4 | — | — | — | — | — | — |
| tracee | default | 4 | 4 | 1.333s | 3.77 | 12.11 | 0.15 | 100.0% | 100.0% |
| tracee | tuned | 4 | 4 | 0.917s | 33.70 | 41.92 | 0.83 | 100.0% | 100.0% |

## Matched rules

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | default | t1059-004-reverse-shell | Redirect STDOUT/STDIN to Network Connection in Container |
| falco | default | t1547-006-kernel-module | Linux Kernel Module Injection Detected |
| falco | default | t1548-001-setuid-binary | Drop and execute new binary in container |
| falco | default | t1036-005-masquerading | Drop and execute new binary in container |
| falco | default | t1070-002-clear-logs | Clear Log Activities |
| falco | default | t1620-fileless-exec | Fileless execution via memfd_create |
| falco | default | t1003-008-shadow-read | Read sensitive file untrusted |
| falco | default | t1552-001-credentials-in-files | Find AWS Credentials, Search Private Keys or Passwords |
| falco | default | t1048-exfiltration-http | Read sensitive file untrusted |
| falco | default | t1485-data-destruction | Remove Bulk Data from Disk |
| falco | default | t1496-cryptominer | Drop and execute new binary in container |
| falco | tuned | t1059-004-reverse-shell | Outbound Connection From Shell Process, Redirect STDOUT/STDIN to Network Connection in Container, System Information Discovery |
| falco | tuned | t1059-006-python-exec | Shell Spawned by Script Interpreter, System Information Discovery |
| falco | tuned | t1053-003-cron-persistence | Write Below Cron Directories |
| falco | tuned | t1098-004-ssh-authorized-keys | SSH Authorized Keys Modified |
| falco | tuned | t1136-001-create-account | User Account Management Command, Write to User Database File |
| falco | tuned | t1543-002-systemd-service | Write Below Systemd Unit Directories |
| falco | tuned | t1547-006-kernel-module | Kernel Module Load Attempt, Linux Kernel Module Injection Detected |
| falco | tuned | t1548-001-setuid-binary | Drop and execute new binary in container, Executable Bit Set on File in Temporary Directory |
| falco | tuned | t1611-escape-to-host | Block Device Mounted in Container, Container Environment Discovery, Container Process Entering Other Namespaces |
| falco | tuned | t1036-005-masquerading | Drop and execute new binary in container |
| falco | tuned | t1070-002-clear-logs | Clear Log Activities, Log File Deleted or Truncated |
| falco | tuned | t1070-003-clear-history | Shell History Tampering |
| falco | tuned | t1222-002-permission-modification | Permission Change on Sensitive File |
| falco | tuned | t1620-fileless-exec | Fileless execution via memfd_create |
| falco | tuned | t1003-008-shadow-read | Read sensitive file untrusted |
| falco | tuned | t1552-001-credentials-in-files | Find AWS Credentials, Read Credential Files With Interactive Tool, Search Private Keys or Passwords |
| falco | tuned | t1552-007-container-api | Container Runtime Socket Access From Container, Read Kubernetes Service Account Token |
| falco | tuned | t1046-network-scan | Network Scanning Tool Executed |
| falco | tuned | t1082-system-discovery | System Information Discovery |
| falco | tuned | t1613-container-discovery | Container Environment Discovery |
| falco | tuned | t1105-ingress-tool-transfer | Executable Bit Set on File in Temporary Directory, Execution From Temporary Directory, System Information Discovery |
| falco | tuned | t1048-exfiltration-http | Data Upload With Command-Line HTTP Client, Read sensitive file untrusted |
| falco | tuned | t1485-data-destruction | Remove Bulk Data from Disk |
| falco | tuned | t1496-cryptominer | Cryptominer Pool Port Connection, Drop and execute new binary in container |
| kunai | tuned | t1059-004-reverse-shell | discovery.system.information, exec.shell.dev_tcp_redirection, net.shell.outbound_connection |
| kunai | tuned | t1059-006-python-exec | discovery.system.information, exec.interpreter.inline_code_shell,exec.interpreter.spawns_shell |
| kunai | tuned | t1053-003-cron-persistence | persistence.cron.write |
| kunai | tuned | t1098-004-ssh-authorized-keys | persistence.ssh.authorized_keys.cmdline, persistence.ssh.authorized_keys.write |
| kunai | tuned | t1136-001-create-account | persistence.account.create |
| kunai | tuned | t1543-002-systemd-service | persistence.systemd.unit.write |
| kunai | tuned | t1547-006-kernel-module | persistence.kernel_module.load |
| kunai | tuned | t1548-001-setuid-binary | exec.from.tmpfs, privesc.setuid.chmod |
| kunai | tuned | t1611-escape-to-host | discovery.container.environment, privesc.escape.mount_block_device, privesc.escape.nsenter_host |
| kunai | tuned | t1036-005-masquerading | defense_evasion.exec.hidden_path,defense_evasion.masquerading.system_binary_name,exec.from.tmpfs |
| kunai | tuned | t1070-002-clear-logs | defense_evasion.logs.clear |
| kunai | tuned | t1070-003-clear-history | defense_evasion.history.delete, defense_evasion.history.tamper_cmdline |
| kunai | tuned | t1222-002-permission-modification | credential_access.shadow.cmdline, defense_evasion.sensitive_file.permissions |
| kunai | tuned | t1620-fileless-exec | defense_evasion.fileless.memfd_exec |
| kunai | tuned | t1003-008-shadow-read | credential_access.shadow.cmdline, credential_access.shadow.read |
| kunai | tuned | t1552-001-credentials-in-files | credential_access.credential_files.cmdline |
| kunai | tuned | t1552-007-container-api | credential_access.container_api.cmdline |
| kunai | tuned | t1046-network-scan | discovery.network.port_scan |
| kunai | tuned | t1082-system-discovery | discovery.system.information |
| kunai | tuned | t1613-container-discovery | discovery.container.environment |
| kunai | tuned | t1105-ingress-tool-transfer | chmod.exec.in.tmpfs, discovery.system.information, download.to.tmpfs, exec.from.tmpfs |
| kunai | tuned | t1048-exfiltration-http | credential_access.credential_files.cmdline,credential_access.shadow.cmdline, credential_access.shadow.read, download.to.tmpfs,exfiltration.http.upload |
| kunai | tuned | t1485-data-destruction | impact.data_destruction |
| kunai | tuned | t1496-cryptominer | exec.from.tmpfs,impact.cryptominer.process, impact.cryptominer.connection |
| tracee | default | t1059-004-reverse-shell | Process standard input/output over socket detected |
| tracee | default | t1053-003-cron-persistence | Scheduled tasks modification detected |
| tracee | default | t1611-escape-to-host | Container device mount detected |
| tracee | default | t1620-fileless-exec | Fileless execution detected |
| tracee | default | t1552-007-container-api | Docker socket abuse detected |
| tracee | tuned | t1059-004-reverse-shell | Process standard input/output over socket detected, detect-shell-network-connect, detect-system-discovery |
| tracee | tuned | t1059-006-python-exec | detect-interpreter-shell, detect-system-discovery |
| tracee | tuned | t1053-003-cron-persistence | Scheduled tasks modification detected |
| tracee | tuned | t1136-001-create-account | detect-account-creation, detect-shadow-read |
| tracee | tuned | t1547-006-kernel-module | detect-kernel-module |
| tracee | tuned | t1548-001-setuid-binary | detect-exec-from-temp-dir, detect-setuid-bit |
| tracee | tuned | t1611-escape-to-host | Container device mount detected, detect-container-escape |
| tracee | tuned | t1036-005-masquerading | detect-exec-from-temp-dir, detect-masquerading |
| tracee | tuned | t1070-002-clear-logs | detect-log-tampering |
| tracee | tuned | t1070-003-clear-history | detect-history-clearing, detect-log-tampering, detect-shell-network-connect |
| tracee | tuned | t1222-002-permission-modification | detect-sensitive-permission-change |
| tracee | tuned | t1620-fileless-exec | Fileless execution detected |
| tracee | tuned | t1003-008-shadow-read | detect-shadow-read |
| tracee | tuned | t1552-001-credentials-in-files | detect-credentials-in-files |
| tracee | tuned | t1552-007-container-api | Docker socket abuse detected, detect-container-api |
| tracee | tuned | t1046-network-scan | detect-network-scan |
| tracee | tuned | t1082-system-discovery | detect-system-discovery |
| tracee | tuned | t1613-container-discovery | detect-container-discovery |
| tracee | tuned | t1105-ingress-tool-transfer | detect-system-discovery |
| tracee | tuned | t1048-exfiltration-http | detect-credentials-in-files, detect-shadow-read |
| tracee | tuned | t1485-data-destruction | detect-data-destruction |
| tracee | tuned | t1496-cryptominer | detect-cryptominer, detect-exec-from-temp-dir |

## Failures

### Failed tools

| Tool | Status | Error |
| --- | --- | --- |
| pulsar | failed | crashed the kind node: Docker and the WSL2 VM exited (code 255) during the pulsar-default overhead workloads, at the same step in runs 20261023T132537Z and 20261024T114807Z; run stopped there |

### Scenario executions with a non-zero exit code

| Tool | Profile | Scenario | Repetition | Exit code |
| --- | --- | --- | --- | --- |
| falco | default | t1046-network-scan | 0 | 1 |
| falco | default | t1046-network-scan | 1 | 1 |
| falco | default | t1046-network-scan | 2 | 1 |
| falco | default | t1046-network-scan | 3 | 1 |
| falco | default | t1046-network-scan | 4 | 1 |
| falco | tuned | t1046-network-scan | 0 | 1 |
| falco | tuned | t1046-network-scan | 1 | 1 |
| falco | tuned | t1046-network-scan | 2 | 1 |
| falco | tuned | t1046-network-scan | 3 | 1 |
| falco | tuned | t1046-network-scan | 4 | 1 |
| kunai | default | t1046-network-scan | 0 | 1 |
| kunai | default | t1046-network-scan | 1 | 1 |
| kunai | default | t1046-network-scan | 2 | 1 |
| kunai | default | t1046-network-scan | 3 | 1 |
| kunai | default | t1046-network-scan | 4 | 1 |
| kunai | tuned | t1046-network-scan | 0 | 1 |
| kunai | tuned | t1046-network-scan | 1 | 1 |
| kunai | tuned | t1046-network-scan | 2 | 1 |
| kunai | tuned | t1046-network-scan | 3 | 1 |
| kunai | tuned | t1046-network-scan | 4 | 1 |
| tracee | default | t1046-network-scan | 0 | 1 |
| tracee | default | t1046-network-scan | 1 | 1 |
| tracee | default | t1046-network-scan | 2 | 1 |
| tracee | default | t1046-network-scan | 3 | 1 |
| tracee | default | t1046-network-scan | 4 | 1 |
| tracee | tuned | t1046-network-scan | 0 | 1 |
| tracee | tuned | t1046-network-scan | 1 | 1 |
| tracee | tuned | t1046-network-scan | 2 | 1 |
| tracee | tuned | t1046-network-scan | 3 | 1 |
| tracee | tuned | t1046-network-scan | 4 | 1 |

### Scenario cleanups with a non-zero exit code

None.
