# eBPF runtime detection benchmark: 20261022T204058Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261022T204058Z |
| grace_seconds | 10 |
| host.architecture | x86_64 |
| host.cgroup_driver | systemd |
| host.cgroup_version | 2 |
| host.cpus | 8 |
| host.docker_api_version | 1.55 |
| host.docker_version | 29.7.1 |
| host.kernel | 6.6.87.2-microsoft-standard-WSL2 |
| host.memory_bytes | 16540459008 |
| host.operating_system | Ubuntu 24.04 LTS |
| host.runner_python | 3.12.14 |
| host.storage_driver | overlayfs |
| config.backend | docker |
| config.control_scenarios | True |
| config.grace_seconds | 10 |
| config.idle_seconds | 3 |
| config.kubernetes | {"context": "kind-ebpf-bench", "kubeconfig": null, "namespace": "ebpf-bench", "node": null} |
| config.overhead | {"duration_seconds": 30, "enabled": true, "repetitions": 3, "workloads": ["syscall", "exec", "fileio"]} |
| config.profiles | ["default", "tuned", "enforce"] |
| config.repetitions | 5 |
| config.results_dir | results |
| config.scenarios | all |
| config.tools | ["falco", "tetragon", "tracee", "kubearmor", "kunai", "pulsar"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| falco | 0.45.0 | ok | default, tuned | default: a9318548d127, enforce: None, tuned: 18d84b1b69aa |
| kubearmor | 1.7.5 | ok | default, enforce, tuned | default: 15ef430d85e9, enforce: b81f0ff463d7, tuned: 12cfa057de2f |
| kunai | 0.6.2 | ok | default, enforce, tuned | default: ea10f4f706e7, enforce: 2f3296c51ff8, tuned: 3c0a05fb5002 |
| pulsar | 0.10.1 | ok | default, tuned | default: 9cb2665a655e, enforce: None, tuned: dd1914d53753 |
| tetragon | 1.7.1 | ok | default, enforce, tuned | default: 4eb2531db490, enforce: 4b4c1eeaecc5, tuned: 39c0c7d92c85 |
| tracee | 0.24.1 | ok | default, tuned | default: c5763fb3419e, enforce: None, tuned: 3bffc520aa3d |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | tuned | 100.0% | 100.0% | 16.7% | 0.111s | 0 | 2.25 | 377.58 | +81.6% |
| tetragon | enforce | 100.0% | 100.0% | 16.7% | 0.120s | 0 | 2.09 | 375.10 | +82.0% |
| falco | tuned | 100.0% | 100.0% | 33.3% | 0.002s | 0 | 5.25 | 68.23 | +2.4% |
| kunai | tuned | 100.0% | 100.0% | 33.3% | 0.090s | 0 | 9.42 | 77.19 | +245.0% |
| kunai | enforce | 100.0% | 100.0% | 33.3% | 0.096s | 0 | 12.26 | 106.74 | +623.7% |
| tracee | tuned | 91.7% | 91.7% | 33.3% | 0.002s | 0 | 18.64 | 126.67 | +36.7% |
| kubearmor | default | 91.7% | 91.7% | 100.0% | 0.096s | 0 | 19.59 | 87.32 | +3.9% |
| kubearmor | tuned | 83.3% | 83.3% | 3.3% | 0.098s | 0 | 19.71 | 107.51 | +3.9% |
| falco | default | 45.8% | 45.8% | 16.7% | 0.002s | 0 | 3.93 | 67.04 | +6.2% |
| tetragon | default | 45.8% | 45.8% | 16.7% | 0.098s | 0 | 1.96 | 387.90 | -0.3% |
| tracee | default | 20.8% | 20.8% | 16.7% | 0.005s | 0 | 15.57 | 124.73 | +22.7% |
| pulsar | default | 16.7% | 16.7% | 16.7% | 0.004s | 0 | 61.48 | 301.43 | +683.9% |
| pulsar | tuned | 16.7% | 16.7% | 16.7% | 0.105s | 0 | 155.78 | 571.88 | +759.3% |
| kubearmor | enforce | 4.2% | 4.2% | 3.3% | 0.172s | 0 | 32.03 | 88.71 | +301.0% |
| kunai | default | 0.0% | 0.0% | 0.0% | — | 0 | 13.75 | 76.07 | +298.9% |

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
| t1046-network-scan | attack | 5 | 5/5 | 0 | 0 | ✅ valid |
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

All control scenarios are valid.

## Coverage matrix

✅ detected in a majority of repetitions, ⚠️ detected in some repetitions, ❌ missed, — not run. In enforce columns 🛡️ means prevented in a majority of repetitions (effect not achieved while the control run achieved it), ✅/⚠️ detected only; † marks a deployment whose enforcement could not be verified. (invalid) marks scenarios whose effect was not achieved in the control runs.

| Tactic | Scenario | Technique | falco/default | falco/tuned | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| execution | t1059-006-python-exec | T1059.006 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1053-003-cron-persistence | T1053.003 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1136-001-create-account | T1136.001 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1543-002-systemd-service | T1543.002 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1547-006-kernel-module | T1547.006 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 † | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1611-escape-to-host | T1611 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 † | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| defense-evasion | t1036-005-masquerading | T1036.005 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-002-clear-logs | T1070.002 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-003-clear-history | T1070.003 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1222-002-permission-modification | T1222.002 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1620-fileless-exec | T1620 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| credential-access | t1003-008-shadow-read | T1003.008 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-001-credentials-in-files | T1552.001 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-007-container-api | T1552.007 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| discovery | t1046-network-scan | T1046 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1082-system-discovery | T1082 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1613-container-discovery | T1613 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| command-and-control | t1105-ingress-tool-transfer | T1105 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| exfiltration | t1048-exfiltration-http | T1048 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1485-data-destruction | T1485 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1496-cryptominer | T1496 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 † | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |

### Coverage per tactic

| Tactic | falco/default | falco/tuned | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | 1/2 | 2/2 | 2/2 | 0/2 | 2/2 | 0/2 | 2/2 | 2/2 | 0/2 | 0/2 | 1/2 | 2/2 | 2/2 | 1/2 | 2/2 |
| persistence | 1/5 | 5/5 | 4/5 | 0/5 | 4/5 | 0/5 | 5/5 | 5/5 | 2/5 | 2/5 | 5/5 | 5/5 | 5/5 | 1/5 | 3/5 |
| privilege-escalation | 1/2 | 2/2 | 1/2 | 0/2 | 1/2 | 0/2 | 2/2 | 2/2 | 0/2 | 0/2 | 1/2 | 2/2 | 2/2 | 1/2 | 2/2 |
| defense-evasion | 3/5 | 5/5 | 5/5 | 1/5 | 3/5 | 0/5 | 5/5 | 5/5 | 2/5 | 2/5 | 1/5 | 5/5 | 5/5 | 1/5 | 5/5 |
| credential-access | 2/3 | 3/3 | 3/3 | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 | 2/3 | 3/3 | 3/3 | 1/3 | 3/3 |
| discovery | 0/3 | 3/3 | 3/3 | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 0/3 | 3/3 |
| command-and-control | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| exfiltration | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| impact | 2/2 | 2/2 | 2/2 | 0/2 | 2/2 | 0/2 | 2/2 | 2/2 | 0/2 | 0/2 | 0/2 | 2/2 | 2/2 | 0/2 | 2/2 |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | falco/default | falco/tuned | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benign-admin-commands | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 1/5 | ⚠️ 1/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 |
| benign-backup | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-compile | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 |
| benign-log-rotation | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 |
| benign-package-query | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-web-server | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | default | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-log-rotation | Log File Deleted or Truncated |
| kubearmor | default | benign-admin-commands | harden-shell-history-mod |
| kubearmor | default | benign-backup | harden-shell-history-mod |
| kubearmor | default | benign-compile | harden-shell-history-mod |
| kubearmor | default | benign-log-rotation | harden-shell-history-mod |
| kubearmor | default | benign-package-query | harden-pkg-mngr-exec, harden-shell-history-mod |
| kubearmor | default | benign-web-server | harden-shell-history-mod |
| kubearmor | enforce | benign-admin-commands | tuned-container-escape |
| kubearmor | tuned | benign-admin-commands | tuned-container-escape |
| kunai | enforce | benign-admin-commands | discovery.system.information |
| kunai | enforce | benign-web-server | download.to.tmpfs |
| kunai | tuned | benign-admin-commands | discovery.system.information |
| kunai | tuned | benign-web-server | download.to.tmpfs |
| pulsar | default | benign-compile | Create files below /root |
| pulsar | tuned | benign-compile | Create files below /root |
| tetragon | default | benign-log-rotation | file-monitoring-filtered |
| tetragon | enforce | benign-log-rotation | file-monitoring-filtered, history-and-log-tampering |
| tetragon | tuned | benign-log-rotation | file-monitoring-filtered, history-and-log-tampering |
| tracee | default | benign-compile | New executable dropped |
| tracee | tuned | benign-admin-commands | detect-container-discovery |
| tracee | tuned | benign-compile | New executable dropped |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | falco/default | falco/tuned | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1059-004-reverse-shell | 0.003s / 0.004s | 0.003s / 0.004s | 0.109s / 0.180s | — | 0.060s / 0.153s | — | 0.100s / 0.128s | 0.082s / 0.104s | — | — | 0.073s / 0.140s | 0.166s / 0.202s | 0.129s / 0.191s | 0.003s / 0.004s | 0.002s / 0.003s |
| t1059-006-python-exec | — | 0.014s / 0.017s | 0.152s / 0.178s | — | 0.095s / 0.185s | — | 0.119s / 0.364s | 0.119s / 0.163s | — | — | — | 0.151s / 0.201s | 0.109s / 0.188s | — | 0.015s / 0.015s |
| t1053-003-cron-persistence | — | 0.001s / 0.001s | 0.069s / 0.150s | — | 0.093s / 0.164s | — | 0.066s / 0.085s | 0.077s / 0.115s | 0.003s / 0.007s | 0.105s / 0.114s | 0.075s / 0.158s | 0.166s / 0.196s | 0.106s / 0.139s | 0.001s / 0.001s | 0.001s / 0.001s |
| t1098-004-ssh-authorized-keys | — | 0.003s / 0.005s | 0.055s / 0.090s | — | 0.147s / 0.173s | — | 0.106s / 0.129s | 0.073s / 0.118s | — | — | 0.127s / 0.143s | 0.149s / 0.167s | 0.132s / 0.188s | — | — |
| t1136-001-create-account | — | 0.001s / 0.001s | 0.171s / 0.179s | — | 0.024s / 0.190s | — | 0.121s / 0.135s | 0.114s / 0.134s | — | — | 0.184s / 0.197s | 0.119s / 0.166s | 0.039s / 0.153s | — | 0.001s / 0.002s |
| t1543-002-systemd-service | — | 0.001s / 0.002s | 0.048s / 0.140s | — | 0.080s / 0.193s | — | 0.083s / 0.094s | 0.092s / 0.139s | — | 0.105s / 0.128s | 0.133s / 0.151s | 0.052s / 0.077s | 0.125s / 0.172s | — | — |
| t1547-006-kernel-module | 0.003s / 0.007s | 0.001s / 0.002s | — | — | — | — | 0.104s / 0.143s | 0.072s / 0.127s | 0.007s / 0.020s | — | 0.179s / 0.192s | 0.083s / 0.126s | 0.162s / 0.194s | — | 0.001s / 0.002s |
| t1548-001-setuid-binary | 0.005s / 0.006s | 0.002s / 0.003s | 0.148s / 0.189s | — | 0.116s / 0.199s | — | 0.089s / 0.141s | 0.075s / 0.153s | — | — | 0.062s / 0.114s | 0.127s / 0.170s | 0.056s / 0.181s | — | 0.002s / 0.003s |
| t1611-escape-to-host | — | 0.001s / 0.003s | — | — | — | — | 0.092s / 0.129s | 0.105s / 0.158s | — | — | — | 0.152s / 0.194s | 0.089s / 0.111s | 0.005s / 0.006s | 0.001s / 0.001s |
| t1036-005-masquerading | 0.003s / 0.004s | 0.003s / 0.003s | 0.107s / 0.174s | — | 0.026s / 0.094s | — | 0.098s / 0.112s | 0.111s / 0.134s | — | — | — | 0.121s / 0.149s | 0.154s / 0.174s | — | 0.003s / 0.004s |
| t1070-002-clear-logs | -0.019s / -0.017s | -0.022s / -0.020s | 0.125s / 0.165s | — | 0.052s / 0.108s | — | 0.115s / 0.150s | 0.072s / 0.133s | -0.098s / -0.043s | 0.051s / 0.059s | 0.092s / 0.142s | 0.028s / 0.129s | 0.003s / 0.110s | — | 0.003s / 0.003s |
| t1070-003-clear-history | — | 0.003s / 0.005s | 0.170s / 0.193s | 0.172s / 0.199s | 0.078s / 0.111s | — | 0.096s / 0.112s | 0.068s / 0.121s | 0.411s / 0.465s | 0.447s / 0.696s | — | 0.148s / 0.188s | 0.172s / 0.196s | — | 0.002s / 0.003s |
| t1222-002-permission-modification | — | 0.001s / 0.002s | 0.119s / 0.124s | — | — | — | 0.122s / 0.138s | 0.101s / 0.115s | — | — | — | 0.147s / 0.200s | 0.115s / 0.145s | — | 0.001s / 0.001s |
| t1620-fileless-exec | 0.008s / 0.009s | 0.008s / 0.008s | 0.058s / 0.157s | — | — | — | 0.106s / 0.137s | 0.095s / 0.107s | — | — | — | 0.073s / 0.083s | 0.133s / 0.159s | 0.008s / 0.009s | 0.009s / 0.009s |
| t1003-008-shadow-read | 0.001s / 0.002s | 0.001s / 0.003s | 0.072s / 0.162s | — | 0.171s / 0.194s | — | 0.097s / 0.126s | 0.087s / 0.185s | — | — | 0.112s / 0.134s | 0.081s / 0.098s | 0.158s / 0.191s | — | 0.001s / 0.002s |
| t1552-001-credentials-in-files | 0.001s / 0.001s | 0.001s / 0.001s | 0.097s / 0.196s | — | 0.071s / 0.152s | — | 0.120s / 0.152s | 0.090s / 0.140s | — | — | 0.098s / 0.122s | 0.150s / 0.195s | 0.046s / 0.090s | — | 0.003s / 0.003s |
| t1552-007-container-api | — | 0.002s / 0.003s | 0.058s / 0.128s | — | 0.104s / 0.117s | — | 0.070s / 0.116s | 0.090s / 0.100s | — | — | — | 0.141s / 0.182s | 0.045s / 0.092s | 0.008s / 0.009s | 0.003s / 0.003s |
| t1046-network-scan | — | 0.002s / 0.002s | 0.055s / 0.145s | — | 0.074s / 0.124s | — | 0.109s / 0.124s | 0.109s / 0.130s | — | — | — | 0.096s / 0.148s | 0.080s / 0.182s | — | 0.002s / 0.003s |
| t1082-system-discovery | — | 0.001s / 0.002s | 0.028s / 0.039s | — | 0.124s / 0.149s | — | 0.115s / 0.128s | 0.083s / 0.137s | — | — | — | 0.077s / 0.192s | 0.105s / 0.171s | — | 0.001s / 0.001s |
| t1613-container-discovery | — | 0.003s / 0.003s | 0.131s / 0.163s | — | 0.144s / 0.186s | — | 0.129s / 0.151s | 0.097s / 0.106s | — | — | — | 0.060s / 0.166s | 0.116s / 0.157s | — | 0.003s / 0.003s |
| t1105-ingress-tool-transfer | — | 0.007s / 0.009s | 0.123s / 0.146s | — | 0.159s / 0.204s | — | 0.059s / 0.117s | 0.065s / 0.129s | — | — | — | 0.118s / 0.201s | 0.142s / 0.208s | — | 0.011s / 0.013s |
| t1048-exfiltration-http | 0.002s / 0.003s | 0.002s / 0.002s | 0.126s / 0.190s | — | 0.167s / 0.184s | — | 0.090s / 0.119s | 0.072s / 0.083s | — | — | 0.059s / 0.106s | 0.131s / 0.177s | 0.076s / 0.120s | — | 0.003s / 0.003s |
| t1485-data-destruction | 0.001s / 0.001s | 0.001s / 0.001s | 0.145s / 0.158s | — | 0.175s / 0.199s | — | 0.099s / 0.114s | 0.080s / 0.099s | — | — | — | 0.174s / 0.197s | 0.120s / 0.174s | — | 0.001s / 0.001s |
| t1496-cryptominer | 0.001s / 0.002s | 0.001s / 0.002s | 0.031s / 0.119s | — | 0.050s / 0.189s | — | 0.091s / 0.112s | 0.076s / 0.141s | — | — | — | 0.053s / 0.192s | 0.125s / 0.170s | — | 0.001s / 0.001s |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| falco | default | 100.0% | 5 |
| falco | tuned | 100.0% | 5 |
| kubearmor | default | 100.0% | 3 |
| kubearmor | enforce | 100.0% | 0 |
| kubearmor | tuned | 100.0% | 0 |
| kunai | default | 100.0% | 0 |
| kunai | enforce | 100.0% | 0 |
| kunai | tuned | 100.0% | 0 |
| pulsar | default | 100.0% | 5 |
| pulsar | tuned | 100.0% | 2 |
| tetragon | default | 100.0% | 0 |
| tetragon | enforce | 100.0% | 1 |
| tetragon | tuned | 100.0% | 2 |
| tracee | default | 100.0% | 0 |
| tracee | tuned | 100.0% | 0 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | detection only | — | — | — | — | — | — | — | — |
| kubearmor | invalid: 0.0% (0/24) | 5 | 0 | 0 (0.0%) | — | 0 | no | bpf-lsm, apparmor, selinux-host-only, presets | yes |
| kunai | 0.0% (0/24) | 120 | 0 | 0 (0.0%) | 0.096s | 343 | yes | kill | no |
| pulsar | detection only | — | — | — | — | — | — | — | — |
| tetragon | 91.7% (22/24) | 10 | 0 | 0 (0.0%) | 0.121s | 409 | — | sigkill | yes |
| tracee | detection only | — | — | — | — | — | — | — | — |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | falco/default | falco/tuned | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exec | execs_per_sec | 2,188 | 2,159 (+1.3%) | 2,173 (+0.7%) | 1,958 (+10.5%) | 524.18 (+76.0%) | 1,952 (+10.8%) | 815.36 (+62.7%) | 522.29 (+76.1%) | 1,004 (+54.1%) | 302.92 (+86.2%) | 237.26 (+89.2%) | 1,544 (+29.4%) | 1,384 (+36.7%) | 1,370 (+37.4%) | 1,985 (+9.3%) | 1,914 (+12.5%) |
| exec | p50_us | 427.38 | 440.72 (+3.1%) | 438.22 (+2.5%) | 472.69 (+10.6%) | 1,502 (+251.4%) | 470.14 (+10.0%) | 1,020 (+138.8%) | 1,581 (+270.0%) | 862.05 (+101.7%) | 2,509 (+487.1%) | 3,056 (+615.2%) | 575.38 (+34.6%) | 644.52 (+50.8%) | 647.78 (+51.6%) | 467.64 (+9.4%) | 483.42 (+13.1%) |
| exec | p99_us | 899.82 | 930.23 (+3.4%) | 854.96 (-5.0%) | 1,016 (+12.9%) | 10,760 (+1095.7%) | 1,044 (+16.0%) | 6,254 (+595.0%) | 7,356 (+717.5%) | 5,199 (+477.8%) | 12,793 (+1321.7%) | 18,457 (+1951.2%) | 1,259 (+39.9%) | 1,396 (+55.1%) | 1,400 (+55.5%) | 1,031 (+14.6%) | 1,057 (+17.5%) |
| fileio | ops_per_sec | 600.08 | 717.96 (-19.6%) | 730.61 (-21.8%) | 689.19 (-14.8%) | 335.92 (+44.0%) | 706.20 (-17.7%) | 416.36 (+30.6%) | 237.42 (+60.4%) | 452.73 (+24.6%) | 204.68 (+65.9%) | 160.76 (+73.2%) | 730.61 (-21.8%) | 714.60 (-19.1%) | 715.90 (-19.3%) | 706.57 (-17.7%) | 702.70 (-17.1%) |
| fileio | p50_us | 1,548 | 1,329 (-14.2%) | 1,312 (-15.2%) | 1,351 (-12.7%) | 2,657 (+71.7%) | 1,344 (-13.2%) | 2,041 (+31.9%) | 3,591 (+132.1%) | 1,922 (+24.2%) | 4,123 (+166.4%) | 5,024 (+224.7%) | 1,303 (-15.8%) | 1,325 (-14.4%) | 1,322 (-14.6%) | 1,345 (-13.1%) | 1,359 (-12.2%) |
| fileio | p99_us | 3,521 | 2,289 (-35.0%) | 2,083 (-40.8%) | 2,627 (-25.4%) | 10,142 (+188.1%) | 2,380 (-32.4%) | 11,052 (+213.9%) | 11,993 (+240.7%) | 8,582 (+143.8%) | 14,146 (+301.8%) | 20,444 (+480.7%) | 2,274 (-35.4%) | 2,231 (-36.6%) | 2,306 (-34.5%) | 2,376 (-32.5%) | 2,334 (-33.7%) |
| syscall | connect_ops_per_sec | 71,556 | 63,698 (+11.0%) | 68,481 (+4.3%) | 32,391 (+54.7%) | 7,601 (+89.4%) | 32,821 (+54.1%) | 15,984 (+77.7%) | 13,639 (+80.9%) | 25,595 (+64.2%) | 5,212 (+92.7%) | 2,714 (+96.2%) | 76,195 (-6.5%) | 57,033 (+20.3%) | 58,348 (+18.5%) | 52,948 (+26.0%) | 51,605 (+27.9%) |
| syscall | connect_p50_ns | 5,502 | 5,872 (+6.7%) | 5,880 (+6.9%) | 12,304 (+123.6%) | 31,389 (+470.5%) | 12,286 (+123.3%) | 20,264 (+268.3%) | 26,345 (+378.8%) | 17,548 (+218.9%) | 55,814 (+914.4%) | 58,362 (+960.7%) | 5,523 (+0.4%) | 7,335 (+33.3%) | 7,046 (+28.1%) | 9,079 (+65.0%) | 9,172 (+66.7%) |
| syscall | connect_p99_ns | 19,932 | 21,032 (+5.5%) | 20,367 (+2.2%) | 59,417 (+198.1%) | 436,768 (+2091.3%) | 58,131 (+191.6%) | 256,285 (+1185.8%) | 319,884 (+1504.9%) | 110,868 (+456.2%) | 792,581 (+3876.4%) | 3,469,566 (+17307.0%) | 17,118 (-14.1%) | 22,175 (+11.3%) | 21,577 (+8.3%) | 38,091 (+91.1%) | 39,852 (+99.9%) |
| syscall | getpid_ops_per_sec | 7,433,961 | 7,114,932 (+4.3%) | 7,511,818 (-1.0%) | 7,485,410 (-0.7%) | 7,360,745 (+1.0%) | 7,475,219 (-0.6%) | 3,498,306 (+52.9%) | 2,185,899 (+70.6%) | 3,888,162 (+47.7%) | 1,927,375 (+74.1%) | 2,125,517 (+71.4%) | 7,883,530 (-6.0%) | 2,494,727 (+66.4%) | 2,479,807 (+66.6%) | 7,835,099 (-5.4%) | 6,913,544 (+7.0%) |
| syscall | getpid_p50_ns | 87.00 | 94.00 (+8.0%) | 90.00 (+3.4%) | 91.00 (+4.6%) | 91.00 (+4.6%) | 91.00 (+4.6%) | 178.00 (+104.6%) | 266.00 (+205.7%) | 160.00 (+83.9%) | 260.00 (+198.9%) | 253.00 (+190.8%) | 83.00 (-4.6%) | 344.00 (+295.4%) | 347.00 (+298.9%) | 83.00 (-4.6%) | 100.00 (+14.9%) |
| syscall | getpid_p99_ns | 120.00 | 116.00 (-3.3%) | 111.00 (-7.5%) | 109.00 (-9.2%) | 115.00 (-4.2%) | 111.00 (-7.5%) | 345.00 (+187.5%) | 1,051 (+775.8%) | 274.00 (+128.3%) | 991.00 (+725.8%) | 1,001 (+734.2%) | 102.00 (-15.0%) | 436.00 (+263.3%) | 485.00 (+304.2%) | 102.00 (-15.0%) | 127.00 (+5.8%) |
| syscall | openat_ops_per_sec | 758,493 | 578,265 (+23.8%) | 567,859 (+25.1%) | 163,746 (+78.4%) | 131,951 (+82.6%) | 140,656 (+81.5%) | 301,503 (+60.2%) | 168,936 (+77.7%) | 303,030 (+60.0%) | 33,404 (+95.6%) | 29,751 (+96.1%) | 769,860 (-1.5%) | 496,165 (+34.6%) | 497,500 (+34.4%) | 212,319 (+72.0%) | 175,039 (+76.9%) |
| syscall | openat_p50_ns | 983.00 | 1,370 (+39.4%) | 1,362 (+38.6%) | 4,378 (+345.4%) | 4,599 (+367.9%) | 4,458 (+353.5%) | 2,402 (+144.4%) | 4,025 (+309.5%) | 2,356 (+139.7%) | 15,038 (+1429.8%) | 13,989 (+1323.1%) | 974.00 (-0.9%) | 1,650 (+67.9%) | 1,654 (+68.3%) | 5,105 (+419.3%) | 5,729 (+482.8%) |
| syscall | openat_p99_ns | 2,225 | 2,924 (+31.4%) | 3,630 (+63.1%) | 31,272 (+1305.5%) | 46,033 (+1968.9%) | 39,907 (+1693.6%) | 14,129 (+535.0%) | 18,603 (+736.1%) | 11,269 (+406.5%) | 252,508 (+11248.7%) | 279,098 (+12443.7%) | 2,249 (+1.1%) | 3,356 (+50.8%) | 3,400 (+52.8%) | 10,888 (+389.3%) | 14,788 (+564.6%) |
| syscall | read_ops_per_sec | 4,758,444 | 4,650,371 (+2.3%) | 4,878,067 (-2.5%) | 4,918,184 (-3.4%) | 2,536,517 (+46.7%) | 4,826,997 (-1.4%) | 1,186,580 (+75.1%) | 659,596 (+86.1%) | 1,395,018 (+70.7%) | 1,279,576 (+73.1%) | 953,489 (+80.0%) | 588,716 (+87.6%) | 277,774 (+94.2%) | 289,624 (+93.9%) | 4,093,640 (+14.0%) | 3,778,799 (+20.6%) |
| syscall | read_p50_ns | 156.00 | 165.00 (+5.8%) | 158.00 (+1.3%) | 158.00 (+1.3%) | 167.00 (+7.1%) | 160.00 (+2.6%) | 670.00 (+329.5%) | 1,097 (+603.2%) | 579.00 (+271.2%) | 466.00 (+198.7%) | 479.00 (+207.1%) | 1,567 (+904.5%) | 3,368 (+2059.0%) | 3,256 (+1987.2%) | 194.00 (+24.4%) | 215.00 (+37.8%) |
| syscall | read_p99_ns | 205.00 | 226.00 (+10.2%) | 200.00 (-2.4%) | 190.00 (-7.3%) | 685.00 (+234.1%) | 193.00 (-5.9%) | 1,262 (+515.6%) | 4,204 (+1950.7%) | 1,274 (+521.5%) | 1,458 (+611.2%) | 1,813 (+784.4%) | 2,762 (+1247.3%) | 5,008 (+2342.9%) | 5,211 (+2442.0%) | 248.00 (+21.0%) | 278.00 (+35.6%) |
| syscall | stat_ops_per_sec | 2,453,513 | 2,354,916 (+4.0%) | 2,464,626 (-0.5%) | 2,456,937 (-0.1%) | 747,427 (+69.5%) | 2,458,635 (-0.2%) | 1,186,851 (+51.6%) | 642,470 (+73.8%) | 1,349,477 (+45.0%) | 673,465 (+72.6%) | 406,610 (+83.4%) | 2,533,832 (-3.3%) | 1,368,867 (+44.2%) | 1,378,392 (+43.8%) | 2,548,465 (-3.9%) | 2,327,430 (+5.1%) |
| syscall | stat_p50_ns | 337.00 | 354.00 (+5.0%) | 346.00 (+2.7%) | 348.00 (+3.3%) | 383.00 (+13.6%) | 348.00 (+3.3%) | 641.00 (+90.2%) | 1,046 (+210.4%) | 553.00 (+64.1%) | 1,045 (+210.1%) | 1,109 (+229.1%) | 341.00 (+1.2%) | 661.00 (+96.1%) | 657.00 (+95.0%) | 336.00 (-0.3%) | 372.00 (+10.4%) |
| syscall | stat_p99_ns | 544.00 | 510.00 (-6.2%) | 450.00 (-17.3%) | 445.00 (-18.2%) | 3,994 (+634.2%) | 443.00 (-18.6%) | 3,906 (+618.0%) | 4,048 (+644.1%) | 2,149 (+295.0%) | 4,036 (+641.9%) | 4,155 (+663.8%) | 426.00 (-21.7%) | 900.00 (+65.4%) | 915.00 (+68.2%) | 432.00 (-20.6%) | 515.00 (-5.3%) |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | default | 3.93 | 87.73 | 67.04 | 73.21 | +5.3% | +4.0% | 14.74 | 36.26 | +1.2 pp |
| falco | tuned | 5.25 | 100.44 | 68.23 | 80.29 | +1.7% | -0.5% | 15.46 | 43.34 | +1.9 pp |
| kubearmor | default | 19.59 | 429.32 | 87.32 | 116.26 | +3.9% | -0.1% | 17.42 | 73.73 | +3.9 pp |
| kubearmor | enforce | 32.03 | 415.16 | 88.71 | 101.74 | +242.8% | +69.5% | 22.07 | 72.76 | +8.5 pp |
| kubearmor | tuned | 19.71 | 469.74 | 107.51 | 453.82 | +3.9% | -0.2% | 17.40 | 86.98 | +3.8 pp |
| kunai | default | 13.75 | 100.42 | 76.07 | 76.74 | +241.1% | +60.2% | 26.32 | 70.10 | +12.8 pp |
| kunai | enforce | 12.26 | 103.34 | 106.74 | 107.25 | +491.0% | +76.1% | 22.32 | 64.38 | +8.8 pp |
| kunai | tuned | 9.42 | 60.34 | 77.19 | 77.81 | +181.3% | +54.1% | 17.82 | 43.04 | +4.3 pp |
| pulsar | default | 61.48 | 357.71 | 301.43 | 326.58 | +626.6% | +74.1% | 45.84 | 76.31 | +32.3 pp |
| pulsar | tuned | 155.78 | 251.91 | 571.88 | 576.65 | +699.0% | +83.4% | 63.53 | 89.46 | +50.0 pp |
| tetragon | default | 1.96 | 91.27 | 387.90 | 464.69 | -0.3% | -3.3% | 15.09 | 36.15 | +1.5 pp |
| tetragon | enforce | 2.09 | 60.32 | 375.10 | 454.00 | +60.3% | +36.7% | 15.34 | 39.39 | +1.8 pp |
| tetragon | tuned | 2.25 | 58.64 | 377.58 | 429.05 | +61.9% | +37.4% | 15.06 | 37.40 | +1.5 pp |
| tracee | default | 15.57 | 265.11 | 124.73 | 137.58 | +12.0% | +9.3% | 18.65 | 59.25 | +5.1 pp |
| tracee | tuned | 18.64 | 260.12 | 126.67 | 140.75 | +16.2% | +12.5% | 19.30 | 58.94 | +5.7 pp |

Host CPU is sampled from /proc/stat every second during workloads (Docker backend only); baseline median 13.56%, max 32.22%. The delta is in percentage points of the whole host.

## Operational aspects

Scores follow the rubric in docs/methodology.md (1 worst, 5 best).

| Tool | Version | License | Deployment | Rule customization | Output quality | Deploy steps | Rule language | Custom rules | Hot reload | Output formats | Enrichment | ATT&CK mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | 0.45.0 | Apache-2.0 | 5 | 5 | 5 | 2 | YAML rules, macros and lists whose conditions use the Falco filter language over syscall and plugin fields, with exceptions, append and override | yes | yes | json, text | container, kubernetes | yes | Deployment 5: the image runs with defaults (docker/falco/Dockerfile ships /usr/bin/falco as CMD, its usage label is a single privileged docker run, falco.yaml defaults engine.kind to modern_ebpf which needs no kernel headers or driver loader, and the container plugin is enabled by the packaged config.d/falco.container_plugin.yaml); on Kubernetes the chart README documents a plain "helm install falco falcosecurity/falco". The only benchmark change is a config.d drop-in enabling json_output and disabling syslog. Modern eBPF still requires a BTF-enabled kernel. Rule customization 5: declarative YAML rules loaded from rules_files and rules.d, rule enable/disable by name or tag in falco.yaml, and watch_config_files: true reloads configuration and rules on change (plus SIGHUP and the 0.45 reload API). Output quality 5: json_output emits rule, priority, time, source, hostname, tags and output_fields (formats.cpp); upstream stable rules carry mitre_* and Txxxx tags, the container plugin adds container.* and k8s.pod.* fields, and parent/ancestor fields (proc.pname, proc.aname) are available, although ancestry depth depends on each rule's output template.  |
| kubearmor | 1.7.5 | Apache-2.0 | 3 | 4 | 4 | 2 | declarative KubeArmorPolicy YAML (process, file, network, capabilities, syscalls and presets rules with matchPaths, matchDirectories, matchPatterns, fromSource, Allow/Audit/Block actions) | yes | yes | json | container, kubernetes | no | deployment 3: outside Kubernetes the daemon must be started with k8s=false and policy flags (deployments/podman/docker-compose.yaml, KubeArmor/packaging/kubearmor.yaml), upstream pairs it with the kubearmor-init container that compiles the eBPF objects against the host kernel (Dockerfile.init, build/compile.sh), it needs the container runtime socket, bpffs, securityfs and debugfs, and policies can only be fed through the gRPC PolicyService (karmor vm policy add) or the JSON backup directory /opt/kubearmor/policies read at startup (core/unorchestratedUpdates.go restoreKubeArmorPolicies). Helm and the operator make the Kubernetes path simpler. rule_customization 4: policies are declarative and applied live (CRD watchers in Kubernetes, gRPC PolicyService outside), but expressiveness is limited to paths, directories, glob patterns, source binaries and protocols; arguments can only be matched for Allow lists (matchArgs) and there is no correlation; Audit rules need visibility enabled (getting-started/kubearmor_visibility.md). output_quality 4: JSON per event (types/types.go Log struct) with container id/name/image, pod, namespace, labels, host and container pids, parent process name, source command line, policy name, severity, tags, message, action and result; ATT&CK mapping only exists when the policy author puts MITRE tags in the policy (hardening templates do), there is no built-in technique field and no ancestry beyond the parent. |
| kunai | 0.6.2 | GPL-3.0 | 3 | 4 | 4 | 3 | Gene YAML rules (match-on event names, $variables matching event fields with ==, ~= regex, &= flags and numeric comparisons, boolean condition, severity, ATT&CK ids), plus JSON-lines IoCs and YARA for file scans | yes | no | json | process_ancestry, container, file_hashes, user, dns | yes | Deployment 3: upstream ships a distribution-agnostic static binary (assets kunai-amd64 / kunai-aarch64 with .asc signatures and sha512.txt on the v0.6.2 release) and no container image or Kubernetes manifest; the README recommends the binary, the docs install it as a systemd service with `kunai install`. Running it in a container needs host preparation: privileged mode, host PID namespace, BTF and the bpf/debug filesystems. Steps 3 = download, chmod +x, `kunai run -r <rules>`; upstream ships no detection rule, so with the bare `sudo kunai` quickstart every event is printed and nothing is an alert. Rule customization 4: rules are declarative YAML (Gene engine) with detection, filter and dependency types, regex and flag operators, severity and actions (kill, scan-files), loaded from the config `scanner.rules` or `-r`; there is no runtime reload in 0.6.2, a restart is required (hardened mode even requires a reboot). Output quality 4: one JSON object per line (`data`, `detection`, `filter`, `info`) with process ancestors, parent command line, executable hashes, task/parent uid/gid, mount namespace and container name/type; `detection` carries rule names, tags, severity and ATT&CK ids from rule metadata. Not 5 because container context is only the UTS hostname plus a heuristic type (no container id, image or Kubernetes metadata), and the container `type` is often null for processes started after kunai. |
| pulsar | 0.10.1 | Apache-2.0 AND GPL-2.0 | 4 | 4 | 4 | 2 | YAML rule files (name, type, category, severity, description, condition) with a typed condition DSL over event header and payload (==, !=, <, >, STARTS_WITH, ENDS_WITH, CONTAINS, IN, AND/OR/NOT, is_some()) | yes | yes | json, plaintext, syslog | container, image, user | no | Deployment 4: upstream publishes release binaries (pulsard-<arch>[-static], pulsar-<arch>[-static], pulsar-install.sh) and the release workflow pushes ghcr.io/exein-io/pulsar:<tag> built from .github/docker/Dockerfile with the default config and rules baked in; the quickstart is 2 commands (install script, `pulsard`), and the image only needs the usual eBPF privileges and mounts plus /var/lib/docker for container enrichment. No Helm chart or manifest upstream. Rule customization 4: 47 default YAML rule files in rules/ (Elastic detection-rules based) loaded recursively from /var/lib/pulsar/rules; the DSL is declarative and typed but has no regex, no process ancestry and only per-event fields. hot_reload is true because the rules-engine on_config_change hook rebuilds the engine from disk when its configuration is changed at runtime through `pulsar config` / the engine API (no file watcher); this was removed after 0.10.1. Output quality 4: threat-logger prints threat events as JSON (`output_format=json`) with header (image, pid, parent_pid, uid, gid, container id/name/image/image_digest/layers, threat source/description/extra) and the typed payload; the rule name is threat.description and extra holds category, severity, description and condition. No ATT&CK ids (only a category), no ancestry beyond parent_pid, timestamps are serialized as secs/nanos since epoch. |
| tetragon | 1.7.1 | Apache-2.0 | 5 | 4 | 4 | 2 | TracingPolicy YAML (Kubernetes CRD format) attaching kprobes, tracepoints, uprobes or LSM hooks with in-kernel selectors (matchArgs, matchBinaries, matchNamespaces, matchCapabilities) and actions | yes | yes | json | container, kubernetes | no | Deployment 5: docs/content/en/docs/installation/container.md runs the stable image with a single privileged docker run (only the BTF file is mounted) and the Helm chart installs with defaults; the benchmark adds bpffs, /procRoot and an export file location, mirroring the chart's tetragon_configmap.yaml (procfs /procRoot, export-filename). Rule customization 4: policies are declarative and can be added or removed at runtime (TracingPolicy CRDs, tetra tracingpolicy add), but they are low level: authors must know kernel function or syscall names and argument types, a hook takes at most 5 selectors and 5 argument filters, integer filters accept at most 4 values (pkg/selectors/kernel.go), a policy referencing a missing symbol fails unless ignore.callNotFound is set, and there is no correlation across events. Output quality 4: JSON events carry process and parent (binary, arguments, uid, exec_id, start time), optional full ancestry (enable-ancestors), pod/container/workload metadata on Kubernetes and the cgroup-derived container id ("docker") elsewhere, plus policy_name, message and user-defined tags; there is no built-in ATT&CK mapping or severity, and outside Kubernetes the container name and image are not resolved.  |
| tracee | 0.24.1 | Apache-2.0 | 4 | 3 | 4 | 1 | built-in Go signatures selected by YAML Policy CRDs (scope plus event rules with data, scope and return value filters); new signatures require Go code compiled as plugins | yes | no | json, table, gotemplate | container, kubernetes | yes | deployment 4: docs/docs/install/docker.md documents a single docker run (privileged, --pid=host, --cgroupns=host, os-release and /var/run mounts) and the 0.24.1 Helm chart and static manifest exist; it needs a BTF kernel and a few host mounts but no build or kernel headers. rule_customization 3: Policy CRDs (docs/docs/policies) only select events and filter them on scope and single data fields with prefix or suffix wildcards, without correlation, process ancestry or array argument matching; writing a new signature means Go code (signatures-dir loads compiled .so plugins, docs/docs/flags/signatures-dir.1.md) and policies are only read at startup. YAML detectors with CEL exist on main but are not in a release yet. output_quality 4: one JSON object per line (types/trace/trace.go) with process ids, parent pid, executable, container id/name/image and pod fields; signature findings carry metadata.Properties with Severity, Category, Technique and external_id (ATT&CK id) and the triggering event under the detectedFrom argument (pkg/events/findings/findings.go); full ancestry is only in the unreleased v1beta1 format. |

### Measured operational metrics

Measured per deployment: time from container start to readiness, alert and log volume over the deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and share of alerts carrying a container id or name. Rubric scores repeated for comparison.

| Tool | Profile | Deployment score | Output quality score | Time to ready | Alerts / min | Log lines / min | Log volume MiB | Attributed alerts | Alerts with container identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | default | 5 | 5 | 0.087s | 12.06 | 17.13 | 0.27 | 86.4% | 100.0% |
| falco | tuned | 5 | 5 | 0.069s | 92.08 | 105.51 | 1.46 | 61.2% | 99.9% |
| kubearmor | default | 3 | 4 | 3.015s | 31.16 | 124,789 | 1,344 | 100.0% | 100.0% |
| kubearmor | enforce | 3 | 4 | 2.917s | 0.12 | 3,269 | 1,205 | 100.0% | 100.0% |
| kubearmor | tuned | 3 | 4 | 3.035s | 33.08 | 158,681 | 1,705 | 100.0% | 100.0% |
| kunai | default | 3 | 4 | 1.711s | 0.00 | 83,123 | 1,195 | — | — |
| kunai | enforce | 3 | 4 | 2.817s | 33.73 | 80.58 | 0.65 | 90.2% | 99.8% |
| kunai | tuned | 3 | 4 | 1.385s | 32.48 | 35.52 | 0.57 | 93.4% | 96.4% |
| pulsar | default | 4 | 4 | 0.248s | 107.48 | 89,670 | 141.67 | 2.5% | 0.0% |
| pulsar | tuned | 4 | 4 | 0.257s | 157.21 | 207,015 | 307.97 | 2.1% | 0.0% |
| tetragon | default | 5 | 4 | 8.787s | 3,797 | 25,315 | 301.62 | 10.6% | 14.0% |
| tetragon | enforce | 5 | 4 | 22.068s | 3,543 | 23,136 | 271.26 | 9.8% | 10.5% |
| tetragon | tuned | 5 | 4 | 20.791s | 4,297 | 23,217 | 286.89 | 21.4% | 22.1% |
| tracee | default | 4 | 4 | 1.614s | 76.20 | 102.31 | 1.93 | 6.3% | 100.0% |
| tracee | tuned | 4 | 4 | 1.806s | 114.35 | 142.59 | 2.69 | 37.7% | 100.0% |

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
| falco | tuned | t1046-network-scan | Cryptominer Pool Port Connection, Network Scanning Tool Executed |
| falco | tuned | t1082-system-discovery | System Information Discovery |
| falco | tuned | t1613-container-discovery | Container Environment Discovery |
| falco | tuned | t1105-ingress-tool-transfer | Executable Bit Set on File in Temporary Directory, Execution From Temporary Directory, System Information Discovery |
| falco | tuned | t1048-exfiltration-http | Data Upload With Command-Line HTTP Client, Read sensitive file untrusted |
| falco | tuned | t1485-data-destruction | Remove Bulk Data from Disk |
| falco | tuned | t1496-cryptominer | Cryptominer Pool Port Connection, Drop and execute new binary in container |
| kubearmor | default | t1059-004-reverse-shell | harden-shell-history-mod |
| kubearmor | default | t1059-006-python-exec | harden-shell-history-mod |
| kubearmor | default | t1053-003-cron-persistence | harden-shell-history-mod |
| kubearmor | default | t1098-004-ssh-authorized-keys | harden-shell-history-mod |
| kubearmor | default | t1136-001-create-account | harden-shell-history-mod |
| kubearmor | default | t1543-002-systemd-service | harden-shell-history-mod |
| kubearmor | default | t1548-001-setuid-binary | harden-shell-history-mod, ksp-block-exec-inside-tmp |
| kubearmor | default | t1036-005-masquerading | harden-shell-history-mod, ksp-block-exec-inside-tmp |
| kubearmor | default | t1070-002-clear-logs | harden-shell-history-mod |
| kubearmor | default | t1070-003-clear-history | harden-shell-history-mod |
| kubearmor | default | t1222-002-permission-modification | harden-shell-history-mod |
| kubearmor | default | t1620-fileless-exec | harden-shell-history-mod |
| kubearmor | default | t1003-008-shadow-read | harden-shell-history-mod |
| kubearmor | default | t1552-001-credentials-in-files | harden-shell-history-mod |
| kubearmor | default | t1552-007-container-api | harden-shell-history-mod, ksp-block-service-account |
| kubearmor | default | t1046-network-scan | harden-shell-history-mod |
| kubearmor | default | t1082-system-discovery | harden-network-service-scanning, harden-shell-history-mod |
| kubearmor | default | t1613-container-discovery | harden-shell-history-mod |
| kubearmor | default | t1105-ingress-tool-transfer | harden-shell-history-mod |
| kubearmor | default | t1048-exfiltration-http | harden-shell-history-mod |
| kubearmor | default | t1485-data-destruction | harden-shell-history-mod |
| kubearmor | default | t1496-cryptominer | harden-shell-history-mod, ksp-block-exec-inside-tmp |
| kubearmor | enforce | t1070-003-clear-history | harden-shell-history-mod |
| kubearmor | tuned | t1059-004-reverse-shell | tuned-shell-network-socket, tuned-system-discovery |
| kubearmor | tuned | t1059-006-python-exec | tuned-interpreter-spawned-shell, tuned-system-discovery |
| kubearmor | tuned | t1053-003-cron-persistence | tuned-scheduled-task-mod |
| kubearmor | tuned | t1098-004-ssh-authorized-keys | tuned-ssh-authorized-keys-mod |
| kubearmor | tuned | t1136-001-create-account | tuned-account-manipulation, tuned-shadow-file-access |
| kubearmor | tuned | t1543-002-systemd-service | tuned-systemd-unit-mod |
| kubearmor | tuned | t1548-001-setuid-binary | ksp-block-exec-inside-tmp |
| kubearmor | tuned | t1036-005-masquerading | ksp-block-exec-inside-tmp |
| kubearmor | tuned | t1070-002-clear-logs | tuned-log-tampering |
| kubearmor | tuned | t1070-003-clear-history | harden-shell-history-mod, tuned-log-tampering, tuned-shell-network-socket |
| kubearmor | tuned | t1003-008-shadow-read | tuned-shadow-file-access |
| kubearmor | tuned | t1552-001-credentials-in-files | tuned-credentials-in-files |
| kubearmor | tuned | t1552-007-container-api | ksp-block-service-account |
| kubearmor | tuned | t1046-network-scan | harden-network-service-scanning |
| kubearmor | tuned | t1082-system-discovery | harden-network-service-scanning, tuned-system-discovery |
| kubearmor | tuned | t1613-container-discovery | tuned-container-discovery |
| kubearmor | tuned | t1105-ingress-tool-transfer | tuned-system-discovery |
| kubearmor | tuned | t1048-exfiltration-http | tuned-credentials-in-files, tuned-shadow-file-access |
| kubearmor | tuned | t1485-data-destruction | tuned-data-destruction |
| kubearmor | tuned | t1496-cryptominer | ksp-block-exec-inside-tmp |
| kunai | enforce | t1059-004-reverse-shell | discovery.system.information, exec.shell.dev_tcp_redirection, net.shell.outbound_connection |
| kunai | enforce | t1059-006-python-exec | discovery.system.information, exec.interpreter.inline_code_shell,exec.interpreter.spawns_shell |
| kunai | enforce | t1053-003-cron-persistence | persistence.cron.write |
| kunai | enforce | t1098-004-ssh-authorized-keys | persistence.ssh.authorized_keys.cmdline, persistence.ssh.authorized_keys.write |
| kunai | enforce | t1136-001-create-account | persistence.account.create |
| kunai | enforce | t1543-002-systemd-service | persistence.systemd.unit.write |
| kunai | enforce | t1547-006-kernel-module | persistence.kernel_module.load |
| kunai | enforce | t1548-001-setuid-binary | exec.from.tmpfs, privesc.setuid.chmod |
| kunai | enforce | t1611-escape-to-host | discovery.container.environment, privesc.escape.mount_block_device, privesc.escape.nsenter_host |
| kunai | enforce | t1036-005-masquerading | defense_evasion.exec.hidden_path,defense_evasion.masquerading.system_binary_name,exec.from.tmpfs |
| kunai | enforce | t1070-002-clear-logs | defense_evasion.logs.clear |
| kunai | enforce | t1070-003-clear-history | defense_evasion.history.delete, defense_evasion.history.tamper_cmdline |
| kunai | enforce | t1222-002-permission-modification | credential_access.shadow.cmdline, defense_evasion.sensitive_file.permissions |
| kunai | enforce | t1620-fileless-exec | defense_evasion.fileless.memfd_exec |
| kunai | enforce | t1003-008-shadow-read | credential_access.shadow.cmdline, credential_access.shadow.read |
| kunai | enforce | t1552-001-credentials-in-files | credential_access.credential_files.cmdline |
| kunai | enforce | t1552-007-container-api | credential_access.container_api.cmdline |
| kunai | enforce | t1046-network-scan | discovery.network.port_scan, impact.cryptominer.connection |
| kunai | enforce | t1082-system-discovery | discovery.system.information |
| kunai | enforce | t1613-container-discovery | discovery.container.environment |
| kunai | enforce | t1105-ingress-tool-transfer | chmod.exec.in.tmpfs, discovery.system.information, download.to.tmpfs, exec.from.tmpfs |
| kunai | enforce | t1048-exfiltration-http | credential_access.credential_files.cmdline,credential_access.shadow.cmdline, credential_access.shadow.read, download.to.tmpfs,exfiltration.http.upload |
| kunai | enforce | t1485-data-destruction | impact.data_destruction |
| kunai | enforce | t1496-cryptominer | exec.from.tmpfs,impact.cryptominer.process, impact.cryptominer.connection |
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
| kunai | tuned | t1046-network-scan | discovery.network.port_scan, impact.cryptominer.connection |
| kunai | tuned | t1082-system-discovery | discovery.system.information |
| kunai | tuned | t1613-container-discovery | discovery.container.environment |
| kunai | tuned | t1105-ingress-tool-transfer | chmod.exec.in.tmpfs, discovery.system.information, download.to.tmpfs, exec.from.tmpfs |
| kunai | tuned | t1048-exfiltration-http | credential_access.credential_files.cmdline,credential_access.shadow.cmdline, credential_access.shadow.read, download.to.tmpfs,exfiltration.http.upload |
| kunai | tuned | t1485-data-destruction | impact.data_destruction |
| kunai | tuned | t1496-cryptominer | exec.from.tmpfs,impact.cryptominer.process, impact.cryptominer.connection |
| pulsar | default | t1053-003-cron-persistence | Schedule a Cron job |
| pulsar | default | t1547-006-kernel-module | Linux Kernel Module Injection Detected (insmod) |
| pulsar | default | t1070-002-clear-logs | Truncate log files |
| pulsar | default | t1070-003-clear-history | Shell history deletion |
| pulsar | tuned | t1053-003-cron-persistence | Cron file created, Schedule a Cron job |
| pulsar | tuned | t1543-002-systemd-service | Systemd unit file modification |
| pulsar | tuned | t1070-002-clear-logs | Truncate log files |
| pulsar | tuned | t1070-003-clear-history | Shell history deletion |
| tetragon | default | t1059-004-reverse-shell | file-monitoring-filtered, privileges-raise |
| tetragon | default | t1053-003-cron-persistence | file-monitoring-filtered |
| tetragon | default | t1098-004-ssh-authorized-keys | file-monitoring-filtered |
| tetragon | default | t1136-001-create-account | file-monitoring-filtered |
| tetragon | default | t1543-002-systemd-service | file-monitoring-filtered |
| tetragon | default | t1547-006-kernel-module | monitor-kernel-modules |
| tetragon | default | t1548-001-setuid-binary | privileges-raise |
| tetragon | default | t1070-002-clear-logs | file-monitoring-filtered |
| tetragon | default | t1003-008-shadow-read | file-monitoring-filtered |
| tetragon | default | t1552-001-credentials-in-files | file-monitoring-filtered |
| tetragon | default | t1048-exfiltration-http | file-monitoring-filtered |
| tetragon | enforce | t1059-004-reverse-shell | mining-pool-connect, shell-outbound-connect |
| tetragon | enforce | t1059-006-python-exec | interpreter-spawns-shell, monitor-kernel-modules |
| tetragon | enforce | t1053-003-cron-persistence | file-monitoring-filtered, persistence-file-write |
| tetragon | enforce | t1098-004-ssh-authorized-keys | file-monitoring-filtered, persistence-file-write |
| tetragon | enforce | t1136-001-create-account | monitor-kernel-modules, suspicious-tool-exec |
| tetragon | enforce | t1543-002-systemd-service | file-monitoring-filtered, persistence-file-write |
| tetragon | enforce | t1547-006-kernel-module | kernel-module-syscalls, kernel-module-syscalls-exit, monitor-kernel-modules |
| tetragon | enforce | t1548-001-setuid-binary | permission-change |
| tetragon | enforce | t1611-escape-to-host | container-escape |
| tetragon | enforce | t1036-005-masquerading | exec-from-temp-dir, monitor-kernel-modules, system-binary-masquerading |
| tetragon | enforce | t1070-002-clear-logs | file-monitoring-filtered, history-and-log-tampering |
| tetragon | enforce | t1070-003-clear-history | history-and-log-tampering |
| tetragon | enforce | t1222-002-permission-modification | permission-change |
| tetragon | enforce | t1620-fileless-exec | fileless-exec |
| tetragon | enforce | t1003-008-shadow-read | credential-file-read, file-monitoring-filtered |
| tetragon | enforce | t1552-001-credentials-in-files | credential-file-read, file-monitoring-filtered |
| tetragon | enforce | t1552-007-container-api | credential-file-read |
| tetragon | enforce | t1046-network-scan | netcat-outbound-connect |
| tetragon | enforce | t1082-system-discovery | suspicious-tool-exec |
| tetragon | enforce | t1613-container-discovery | suspicious-tool-exec |
| tetragon | enforce | t1105-ingress-tool-transfer | permission-change |
| tetragon | enforce | t1048-exfiltration-http | credential-file-read, file-monitoring-filtered |
| tetragon | enforce | t1485-data-destruction | monitor-kernel-modules, suspicious-tool-exec |
| tetragon | enforce | t1496-cryptominer | exec-from-temp-dir, monitor-kernel-modules, suspicious-tool-exec |
| tetragon | tuned | t1059-004-reverse-shell | file-monitoring-filtered, mining-pool-connect, privileges-raise, shell-outbound-connect, suspicious-tool-exec |
| tetragon | tuned | t1059-006-python-exec | interpreter-spawns-shell, suspicious-tool-exec |
| tetragon | tuned | t1053-003-cron-persistence | file-monitoring-filtered, persistence-file-write |
| tetragon | tuned | t1098-004-ssh-authorized-keys | file-monitoring-filtered, persistence-file-write |
| tetragon | tuned | t1136-001-create-account | credential-file-read, file-monitoring-filtered, persistence-file-write, suspicious-tool-exec |
| tetragon | tuned | t1543-002-systemd-service | file-monitoring-filtered, persistence-file-write |
| tetragon | tuned | t1547-006-kernel-module | kernel-module-syscalls, kernel-module-syscalls-exit, monitor-kernel-modules |
| tetragon | tuned | t1548-001-setuid-binary | exec-from-temp-dir, permission-change, privileges-raise |
| tetragon | tuned | t1611-escape-to-host | container-escape |
| tetragon | tuned | t1036-005-masquerading | exec-from-temp-dir, system-binary-masquerading |
| tetragon | tuned | t1070-002-clear-logs | file-monitoring-filtered, history-and-log-tampering |
| tetragon | tuned | t1070-003-clear-history | history-and-log-tampering |
| tetragon | tuned | t1222-002-permission-modification | permission-change |
| tetragon | tuned | t1620-fileless-exec | fileless-exec |
| tetragon | tuned | t1003-008-shadow-read | credential-file-read, file-monitoring-filtered |
| tetragon | tuned | t1552-001-credentials-in-files | credential-file-read, file-monitoring-filtered |
| tetragon | tuned | t1552-007-container-api | credential-file-read |
| tetragon | tuned | t1046-network-scan | mining-pool-connect, netcat-outbound-connect |
| tetragon | tuned | t1082-system-discovery | suspicious-tool-exec |
| tetragon | tuned | t1613-container-discovery | suspicious-tool-exec |
| tetragon | tuned | t1105-ingress-tool-transfer | exec-from-temp-dir, permission-change, suspicious-tool-exec |
| tetragon | tuned | t1048-exfiltration-http | credential-file-read, file-monitoring-filtered, http-client-upload |
| tetragon | tuned | t1485-data-destruction | suspicious-tool-exec |
| tetragon | tuned | t1496-cryptominer | exec-from-temp-dir, mining-pool-connect, suspicious-tool-exec |
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
| tracee | tuned | t1036-005-masquerading | detect-masquerading |
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

None.

### Scenario executions with a non-zero exit code

| Tool | Profile | Scenario | Repetition | Exit code |
| --- | --- | --- | --- | --- |
| tetragon | enforce | t1003-008-shadow-read | 0 | 1 |
| tetragon | enforce | t1003-008-shadow-read | 1 | 1 |
| tetragon | enforce | t1003-008-shadow-read | 2 | 1 |
| tetragon | enforce | t1003-008-shadow-read | 3 | 1 |
| tetragon | enforce | t1003-008-shadow-read | 4 | 1 |
| tetragon | enforce | t1036-005-masquerading | 0 | 1 |
| tetragon | enforce | t1036-005-masquerading | 1 | 1 |
| tetragon | enforce | t1036-005-masquerading | 2 | 1 |
| tetragon | enforce | t1036-005-masquerading | 3 | 1 |
| tetragon | enforce | t1036-005-masquerading | 4 | 1 |
| tetragon | enforce | t1046-network-scan | 0 | 1 |
| tetragon | enforce | t1046-network-scan | 1 | 1 |
| tetragon | enforce | t1046-network-scan | 2 | 1 |
| tetragon | enforce | t1046-network-scan | 3 | 1 |
| tetragon | enforce | t1046-network-scan | 4 | 1 |
| tetragon | enforce | t1048-exfiltration-http | 0 | 1 |
| tetragon | enforce | t1048-exfiltration-http | 1 | 1 |
| tetragon | enforce | t1048-exfiltration-http | 2 | 1 |
| tetragon | enforce | t1048-exfiltration-http | 3 | 1 |
| tetragon | enforce | t1048-exfiltration-http | 4 | 1 |
| tetragon | enforce | t1053-003-cron-persistence | 0 | 137 |
| tetragon | enforce | t1053-003-cron-persistence | 1 | 137 |
| tetragon | enforce | t1053-003-cron-persistence | 2 | 137 |
| tetragon | enforce | t1053-003-cron-persistence | 3 | 137 |
| tetragon | enforce | t1053-003-cron-persistence | 4 | 137 |
| tetragon | enforce | t1059-004-reverse-shell | 0 | 137 |
| tetragon | enforce | t1059-004-reverse-shell | 1 | 137 |
| tetragon | enforce | t1059-004-reverse-shell | 2 | 137 |
| tetragon | enforce | t1059-004-reverse-shell | 3 | 137 |
| tetragon | enforce | t1059-004-reverse-shell | 4 | 137 |
| tetragon | enforce | t1059-006-python-exec | 0 | 247 |
| tetragon | enforce | t1059-006-python-exec | 1 | 247 |
| tetragon | enforce | t1059-006-python-exec | 2 | 247 |
| tetragon | enforce | t1059-006-python-exec | 3 | 247 |
| tetragon | enforce | t1059-006-python-exec | 4 | 247 |
| tetragon | enforce | t1070-002-clear-logs | 0 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 1 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 2 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 3 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 4 | 137 |
| tetragon | enforce | t1070-003-clear-history | 0 | 1 |
| tetragon | enforce | t1070-003-clear-history | 1 | 1 |
| tetragon | enforce | t1070-003-clear-history | 2 | 1 |
| tetragon | enforce | t1070-003-clear-history | 3 | 1 |
| tetragon | enforce | t1070-003-clear-history | 4 | 1 |
| tetragon | enforce | t1098-004-ssh-authorized-keys | 0 | 137 |
| tetragon | enforce | t1098-004-ssh-authorized-keys | 1 | 137 |
| tetragon | enforce | t1098-004-ssh-authorized-keys | 2 | 137 |
| tetragon | enforce | t1098-004-ssh-authorized-keys | 3 | 137 |
| tetragon | enforce | t1098-004-ssh-authorized-keys | 4 | 137 |
| tetragon | enforce | t1105-ingress-tool-transfer | 0 | 1 |
| tetragon | enforce | t1105-ingress-tool-transfer | 1 | 1 |
| tetragon | enforce | t1105-ingress-tool-transfer | 2 | 1 |
| tetragon | enforce | t1105-ingress-tool-transfer | 3 | 1 |
| tetragon | enforce | t1105-ingress-tool-transfer | 4 | 1 |
| tetragon | enforce | t1136-001-create-account | 0 | 1 |
| tetragon | enforce | t1136-001-create-account | 1 | 1 |
| tetragon | enforce | t1136-001-create-account | 2 | 1 |
| tetragon | enforce | t1136-001-create-account | 3 | 1 |
| tetragon | enforce | t1136-001-create-account | 4 | 1 |
| tetragon | enforce | t1222-002-permission-modification | 0 | 1 |
| tetragon | enforce | t1222-002-permission-modification | 1 | 1 |
| tetragon | enforce | t1222-002-permission-modification | 2 | 1 |
| tetragon | enforce | t1222-002-permission-modification | 3 | 1 |
| tetragon | enforce | t1222-002-permission-modification | 4 | 1 |
| tetragon | enforce | t1485-data-destruction | 0 | 1 |
| tetragon | enforce | t1485-data-destruction | 1 | 1 |
| tetragon | enforce | t1485-data-destruction | 2 | 1 |
| tetragon | enforce | t1485-data-destruction | 3 | 1 |
| tetragon | enforce | t1485-data-destruction | 4 | 1 |
| tetragon | enforce | t1496-cryptominer | 0 | 1 |
| tetragon | enforce | t1496-cryptominer | 1 | 1 |
| tetragon | enforce | t1496-cryptominer | 2 | 1 |
| tetragon | enforce | t1496-cryptominer | 3 | 1 |
| tetragon | enforce | t1496-cryptominer | 4 | 1 |
| tetragon | enforce | t1543-002-systemd-service | 0 | 1 |
| tetragon | enforce | t1543-002-systemd-service | 1 | 1 |
| tetragon | enforce | t1543-002-systemd-service | 2 | 1 |
| tetragon | enforce | t1543-002-systemd-service | 3 | 1 |
| tetragon | enforce | t1543-002-systemd-service | 4 | 1 |
| tetragon | enforce | t1547-006-kernel-module | 0 | 1 |
| tetragon | enforce | t1547-006-kernel-module | 1 | 1 |
| tetragon | enforce | t1547-006-kernel-module | 2 | 1 |
| tetragon | enforce | t1547-006-kernel-module | 3 | 1 |
| tetragon | enforce | t1547-006-kernel-module | 4 | 1 |
| tetragon | enforce | t1548-001-setuid-binary | 0 | 1 |
| tetragon | enforce | t1548-001-setuid-binary | 1 | 1 |
| tetragon | enforce | t1548-001-setuid-binary | 2 | 1 |
| tetragon | enforce | t1548-001-setuid-binary | 3 | 1 |
| tetragon | enforce | t1548-001-setuid-binary | 4 | 1 |
| tetragon | enforce | t1552-001-credentials-in-files | 0 | 1 |
| tetragon | enforce | t1552-001-credentials-in-files | 1 | 1 |
| tetragon | enforce | t1552-001-credentials-in-files | 2 | 1 |
| tetragon | enforce | t1552-001-credentials-in-files | 3 | 1 |
| tetragon | enforce | t1552-001-credentials-in-files | 4 | 1 |
| tetragon | enforce | t1552-007-container-api | 0 | 1 |
| tetragon | enforce | t1552-007-container-api | 1 | 1 |
| tetragon | enforce | t1552-007-container-api | 2 | 1 |
| tetragon | enforce | t1552-007-container-api | 3 | 1 |
| tetragon | enforce | t1552-007-container-api | 4 | 1 |
| tetragon | enforce | t1611-escape-to-host | 0 | 1 |
| tetragon | enforce | t1611-escape-to-host | 1 | 1 |
| tetragon | enforce | t1611-escape-to-host | 2 | 1 |
| tetragon | enforce | t1611-escape-to-host | 3 | 1 |
| tetragon | enforce | t1611-escape-to-host | 4 | 1 |
| tetragon | enforce | t1620-fileless-exec | 0 | 137 |
| tetragon | enforce | t1620-fileless-exec | 1 | 137 |
| tetragon | enforce | t1620-fileless-exec | 2 | 137 |
| tetragon | enforce | t1620-fileless-exec | 3 | 137 |
| tetragon | enforce | t1620-fileless-exec | 4 | 137 |

### Scenario cleanups with a non-zero exit code

| Tool | Profile | Scenario | Repetition | Exit code |
| --- | --- | --- | --- | --- |
| tetragon | enforce | t1070-002-clear-logs | 0 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 1 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 2 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 3 | 137 |
| tetragon | enforce | t1070-002-clear-logs | 4 | 137 |
