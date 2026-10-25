# eBPF runtime detection benchmark: 20261025T090806Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261025T090806Z |
| grace_seconds | 10.0 |
| host.architecture | x86_64 |
| host.cgroup_driver | systemd |
| host.cgroup_version | 2 |
| host.cpus | 8 |
| host.docker_api_version | 1.45 |
| host.docker_version | 26.1.5+dfsg1 |
| host.kernel | 6.12.105+deb13-amd64 |
| host.memory_bytes | 33201963008 |
| host.operating_system | Debian GNU/Linux 13 (trixie) |
| host.runner_python | 3.12.15 |
| host.storage_driver | overlay2 |
| config.backend | docker |
| config.control_scenarios | True |
| config.grace_seconds | 10 |
| config.idle_seconds | 3 |
| config.kubernetes | {"context": "kind-ebpf-bench", "kubeconfig": null, "namespace": "ebpf-bench", "node": null} |
| config.max_log_bytes | 2147483648 |
| config.max_log_lines | 5000000 |
| config.overhead | {"duration_seconds": 30, "enabled": true, "repetitions": 3, "workloads": ["syscall", "exec", "fileio"]} |
| config.profiles | ["default", "tuned", "enforce", "community"] |
| config.repetitions | 5 |
| config.results_dir | results |
| config.scenarios | all |
| config.tools | ["falco", "tetragon", "tracee", "kubearmor", "kunai", "pulsar"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| falco | 0.45.0 | ok | community, default, tuned | community: bad5350a7c3a, default: a9318548d127, enforce: None, tuned: 18d84b1b69aa |
| kubearmor | 1.7.5 | ok | community, default, enforce, tuned | community: cf1c6c0ff99c, default: 15ef430d85e9, enforce: b81f0ff463d7, tuned: 12cfa057de2f |
| kunai | 0.6.2 | running | community, default, enforce, tuned | community: a8d2102db595, default: ea10f4f706e7, enforce: 2f3296c51ff8, tuned: 3c0a05fb5002 |
| pulsar | 0.10.1 | pending | default, tuned | community: None, default: 9cb2665a655e, enforce: None, tuned: dd1914d53753 |
| tetragon | 1.7.1 | ok | community, default, enforce, tuned | community: 1451971dd8bf, default: 4eb2531db490, enforce: 4b4c1eeaecc5, tuned: 39c0c7d92c85 |
| tracee | 0.24.1 | ok | default, tuned | community: None, default: c5763fb3419e, enforce: None, tuned: 3bffc520aa3d |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | tuned | 100.0% | 100.0% | 16.7% | 0.103s | 0 | 0.06 | 370.52 | +83.6% |
| tetragon | enforce | 100.0% | 100.0% | 16.7% | 0.108s | 0 | 0.07 | 394.36 | +71.7% |
| falco | tuned | 100.0% | 100.0% | 33.3% | 0.001s | 0 | 59.53 | 127.34 | +8.9% |
| kunai | tuned | 100.0% | 100.0% | 33.3% | 0.083s | 0 | 6.27 | 92.21 | +19.1% |
| tetragon | community | 100.0% | 100.0% | 100.0% | 0.095s | 0 | 7.27 | 557.74 | +1.0% |
| tracee | tuned | 91.7% | 91.7% | 33.3% | 0.001s | 0 | 163.54 | 158.81 | +48.9% |
| falco | community | 79.2% | 79.2% | 66.7% | 0.001s | 2 | 91.87 | 130.76 | +11.6% |
| falco | default | 45.8% | 45.8% | 16.7% | 0.001s | 0 | 29.77 | 124.45 | +8.2% |
| tetragon | default | 45.8% | 45.8% | 16.7% | 0.107s | 0 | 0.05 | 435.65 | -1.8% |
| tracee | default | 20.8% | 20.8% | 16.7% | 0.005s | 0 | 145.49 | 153.40 | +29.3% |
| kubearmor | community | 0.0% | 0.0% | 0.0% | — | 0 | 24.42 | 321.35 | +63.6% |
| kubearmor | default | 0.0% | 0.0% | 0.0% | — | 0 | 24.07 | 318.10 | +63.3% |
| kubearmor | enforce | 0.0% | 0.0% | 0.0% | — | 0 | 24.18 | 322.85 | +68.4% |
| kubearmor | tuned | 0.0% | 0.0% | 0.0% | — | 0 | 21.09 | 366.15 | +60.3% |
| kunai | default | 0.0% | 0.0% | 0.0% | — | 0 | 6.58 | 105.64 | +17.9% |
| kunai | enforce | 0.0% | 0.0% | 0.0% | — | 0 | 6.44 | 92.19 | +20.6% |
| kunai | community | — | — | — | — | 0 | — | — | — |
| pulsar | default | — | — | — | — | 0 | — | — | — |
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

| Tactic | Scenario | Technique | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| execution | t1059-006-python-exec | T1059.006 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1053-003-cron-persistence | T1053.003 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1136-001-create-account | T1136.001 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1543-002-systemd-service | T1543.002 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1547-006-kernel-module | T1547.006 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1611-escape-to-host | T1611 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| defense-evasion | t1036-005-masquerading | T1036.005 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-002-clear-logs | T1070.002 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-003-clear-history | T1070.003 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1222-002-permission-modification | T1222.002 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1620-fileless-exec | T1620 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| credential-access | t1003-008-shadow-read | T1003.008 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-001-credentials-in-files | T1552.001 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-007-container-api | T1552.007 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| discovery | t1046-network-scan | T1046 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1082-system-discovery | T1082 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1613-container-discovery | T1613 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| command-and-control | t1105-ingress-tool-transfer | T1105 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| exfiltration | t1048-exfiltration-http | T1048 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | — | — | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1485-data-destruction | T1485 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1496-cryptominer | T1496 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | — | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | — | — | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |

### Coverage per tactic

| Tactic | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | 1/2 | 1/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | — | 0/2 | 0/2 | 2/2 | — | — | 2/2 | 1/2 | 2/2 | 2/2 | 1/2 | 2/2 |
| persistence | 5/5 | 1/5 | 5/5 | 0/5 | 0/5 | 0/5 | 0/5 | — | 0/5 | 0/5 | 5/5 | — | — | 5/5 | 5/5 | 5/5 | 5/5 | 1/5 | 3/5 |
| privilege-escalation | 2/2 | 1/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | — | 0/2 | 0/2 | 2/2 | — | — | 2/2 | 1/2 | 2/2 | 2/2 | 1/2 | 2/2 |
| defense-evasion | 4/5 | 3/5 | 5/5 | 0/5 | 0/5 | 0/5 | 0/5 | — | 0/5 | 0/5 | 5/5 | — | — | 5/5 | 1/5 | 5/5 | 5/5 | 1/5 | 5/5 |
| credential-access | 2/3 | 2/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | — | 0/3 | 0/3 | 3/3 | — | — | 3/3 | 2/3 | 3/3 | 3/3 | 1/3 | 3/3 |
| discovery | 1/3 | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | — | 0/3 | 0/3 | 3/3 | — | — | 3/3 | 0/3 | 3/3 | 3/3 | 0/3 | 3/3 |
| command-and-control | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | — | 0/1 | 0/1 | 1/1 | — | — | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| exfiltration | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | — | 0/1 | 0/1 | 1/1 | — | — | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| impact | 2/2 | 2/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | — | 0/2 | 0/2 | 2/2 | — | — | 2/2 | 0/2 | 2/2 | 2/2 | 0/2 | 2/2 |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benign-admin-commands | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | — | — | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 |
| benign-backup | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-compile | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 |
| benign-log-rotation | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 |
| benign-package-query | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-web-server | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | — | — | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | community | benign-admin-commands | Read environment variable from /proc files |
| falco | community | benign-compile | Drop and execute new binary in container |
| falco | community | benign-package-query | Launch Package Management Process in Container |
| falco | community | benign-web-server | Launch Ingress Remote File Copy Tools in Container |
| falco | default | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-log-rotation | Log File Deleted or Truncated |
| kunai | tuned | benign-admin-commands | discovery.system.information |
| kunai | tuned | benign-web-server | download.to.tmpfs |
| tetragon | community | benign-admin-commands | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-backup | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-compile | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-log-rotation | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-package-query | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-web-server | accept, connect, creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | default | benign-log-rotation | file-monitoring-filtered |
| tetragon | enforce | benign-log-rotation | file-monitoring-filtered, history-and-log-tampering |
| tetragon | tuned | benign-log-rotation | file-monitoring-filtered, history-and-log-tampering |
| tracee | default | benign-compile | New executable dropped |
| tracee | tuned | benign-admin-commands | detect-container-discovery |
| tracee | tuned | benign-compile | New executable dropped |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1059-004-reverse-shell | 0.002s / 0.003s | 0.002s / 0.003s | 0.002s / 0.003s | — | — | — | — | — | — | — | 0.097s / 0.121s | — | — | 0.046s / 0.140s | 0.089s / 0.157s | 0.088s / 0.180s | 0.036s / 0.136s | 0.002s / 0.004s | 0.001s / 0.002s |
| t1059-006-python-exec | — | — | 0.019s / 0.019s | — | — | — | — | — | — | — | 0.088s / 0.122s | — | — | 0.095s / 0.158s | — | 0.136s / 0.167s | 0.076s / 0.155s | — | 0.018s / 0.019s |
| t1053-003-cron-persistence | 0.001s / 0.001s | — | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.078s / 0.108s | — | — | 0.031s / 0.165s | 0.163s / 0.168s | 0.094s / 0.175s | 0.097s / 0.184s | 0.000s / 0.005s | 0.000s / 0.000s |
| t1098-004-ssh-authorized-keys | -0.002s / -0.001s | — | 0.002s / 0.004s | — | — | — | — | — | — | — | 0.076s / 0.111s | — | — | 0.141s / 0.189s | 0.124s / 0.135s | 0.048s / 0.116s | 0.094s / 0.141s | — | — |
| t1136-001-create-account | 0.020s / 0.023s | — | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.083s / 0.121s | — | — | 0.138s / 0.181s | 0.021s / 0.121s | 0.116s / 0.188s | 0.181s / 0.197s | — | 0.000s / 0.000s |
| t1543-002-systemd-service | 0.001s / 0.002s | — | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.044s / 0.088s | — | — | 0.056s / 0.132s | 0.092s / 0.179s | 0.133s / 0.149s | 0.112s / 0.185s | — | — |
| t1547-006-kernel-module | 0.001s / 0.003s | 0.002s / 0.002s | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.090s / 0.123s | — | — | 0.134s / 0.156s | 0.093s / 0.146s | 0.081s / 0.178s | 0.134s / 0.184s | — | 0.001s / 0.002s |
| t1548-001-setuid-binary | 0.002s / 0.002s | 0.003s / 0.004s | 0.001s / 0.002s | — | — | — | — | — | — | — | 0.047s / 0.094s | — | — | 0.020s / 0.102s | 0.134s / 0.166s | 0.065s / 0.121s | 0.064s / 0.191s | — | 0.001s / 0.002s |
| t1611-escape-to-host | 0.001s / 0.002s | — | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.074s / 0.089s | — | — | 0.059s / 0.107s | — | 0.181s / 0.198s | 0.155s / 0.183s | 0.004s / 0.006s | 0.000s / 0.000s |
| t1036-005-masquerading | 0.002s / 0.003s | 0.002s / 0.002s | 0.002s / 0.002s | — | — | — | — | — | — | — | 0.083s / 0.109s | — | — | 0.162s / 0.186s | — | 0.140s / 0.149s | 0.091s / 0.151s | — | 0.002s / 0.002s |
| t1070-002-clear-logs | -0.011s / -0.010s | -0.013s / -0.011s | -0.014s / -0.013s | — | — | — | — | — | — | — | 0.069s / 0.100s | — | — | 0.055s / 0.160s | 0.154s / 0.168s | 0.018s / 0.102s | 0.039s / 0.160s | — | 0.002s / 0.002s |
| t1070-003-clear-history | 0.001s / 0.002s | — | 0.002s / 0.003s | — | — | — | — | — | — | — | 0.113s / 0.118s | — | — | 0.069s / 0.174s | — | 0.149s / 0.195s | 0.029s / 0.144s | — | 0.001s / 0.001s |
| t1222-002-permission-modification | — | — | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.119s / 0.133s | — | — | 0.063s / 0.171s | — | 0.033s / 0.148s | 0.107s / 0.163s | — | 0.001s / 0.002s |
| t1620-fileless-exec | 0.011s / 0.011s | 0.010s / 0.010s | 0.009s / 0.009s | — | — | — | — | — | — | — | 0.067s / 0.083s | — | — | 0.099s / 0.137s | — | 0.143s / 0.165s | 0.157s / 0.196s | 0.009s / 0.010s | 0.009s / 0.010s |
| t1003-008-shadow-read | 0.002s / 0.005s | 0.001s / 0.001s | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.087s / 0.107s | — | — | 0.094s / 0.142s | 0.178s / 0.184s | 0.106s / 0.181s | 0.075s / 0.149s | — | 0.001s / 0.001s |
| t1552-001-credentials-in-files | 0.001s / 0.002s | 0.001s / 0.001s | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.055s / 0.098s | — | — | 0.153s / 0.190s | 0.107s / 0.177s | 0.139s / 0.188s | 0.095s / 0.183s | — | 0.002s / 0.002s |
| t1552-007-container-api | — | — | 0.001s / 0.002s | — | — | — | — | — | — | — | 0.066s / 0.133s | — | — | 0.075s / 0.124s | — | 0.155s / 0.188s | 0.075s / 0.156s | 0.007s / 0.009s | 0.002s / 0.002s |
| t1046-network-scan | 0.021s / 0.021s | — | 0.001s / 0.002s | — | — | — | — | — | — | — | 0.070s / 0.118s | — | — | 0.105s / 0.187s | — | 0.100s / 0.187s | 0.106s / 0.167s | — | 0.001s / 0.001s |
| t1082-system-discovery | — | — | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.084s / 0.127s | — | — | 0.110s / 0.175s | — | 0.034s / 0.127s | 0.070s / 0.116s | — | 0.001s / 0.001s |
| t1613-container-discovery | — | — | 0.002s / 0.002s | — | — | — | — | — | — | — | 0.079s / 0.113s | — | — | 0.118s / 0.120s | — | 0.131s / 0.148s | 0.116s / 0.138s | — | 0.002s / 0.004s |
| t1105-ingress-tool-transfer | 0.001s / 0.002s | — | 0.008s / 0.008s | — | — | — | — | — | — | — | 0.116s / 0.127s | — | — | 0.111s / 0.167s | — | 0.099s / 0.164s | 0.044s / 0.100s | — | 0.009s / 0.012s |
| t1048-exfiltration-http | 0.001s / 0.003s | 0.001s / 0.002s | 0.002s / 0.002s | — | — | — | — | — | — | — | 0.089s / 0.096s | — | — | 0.115s / 0.184s | 0.103s / 0.121s | 0.156s / 0.177s | 0.175s / 0.194s | — | 0.001s / 0.001s |
| t1485-data-destruction | 0.001s / 0.002s | 0.001s / 0.002s | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.108s / 0.116s | — | — | 0.048s / 0.158s | — | 0.144s / 0.193s | 0.130s / 0.145s | — | 0.001s / 0.001s |
| t1496-cryptominer | 0.001s / 0.002s | 0.001s / 0.001s | 0.001s / 0.001s | — | — | — | — | — | — | — | 0.129s / 0.177s | — | — | 0.083s / 0.134s | — | 0.175s / 0.188s | 0.125s / 0.173s | — | 0.001s / 0.001s |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| falco | community | 100.0% | 10 |
| falco | default | 100.0% | 5 |
| falco | tuned | 100.0% | 5 |
| kubearmor | community | 100.0% | 0 |
| kubearmor | default | 100.0% | 0 |
| kubearmor | enforce | 100.0% | 0 |
| kubearmor | tuned | 100.0% | 0 |
| kunai | community | — | 0 |
| kunai | default | 100.0% | 0 |
| kunai | enforce | 100.0% | 0 |
| kunai | tuned | 100.0% | 0 |
| pulsar | default | — | 0 |
| pulsar | tuned | — | 0 |
| tetragon | community | 100.0% | 2 |
| tetragon | default | 100.0% | 0 |
| tetragon | enforce | 100.0% | 0 |
| tetragon | tuned | 100.0% | 2 |
| tracee | default | 100.0% | 0 |
| tracee | tuned | 100.0% | 0 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | detection only | — | — | — | — | — | — | — | — |
| kubearmor | 91.7% (22/24) | 0 | 110 | 0 (0.0%) | — | 0 | yes | bpf-lsm, apparmor, selinux-host-only, presets | yes |
| kunai | 12.5% (3/24) | 0 | 15 | 0 (0.0%) | — | 0 | — | kill | no |
| pulsar | detection only | — | — | — | — | — | — | — | — |
| tetragon | 91.7% (22/24) | 10 | 0 | 0 (0.0%) | 0.114s | 260 | — | sigkill | yes |
| tracee | detection only | — | — | — | — | — | — | — | — |

### Prevented without alert

| Tool | Scenarios |
| --- | --- |
| kubearmor | t1003-008-shadow-read, t1036-005-masquerading, t1046-network-scan, t1053-003-cron-persistence, t1059-004-reverse-shell, t1059-006-python-exec, t1070-003-clear-history, t1082-system-discovery, t1098-004-ssh-authorized-keys, t1105-ingress-tool-transfer, t1136-001-create-account, t1222-002-permission-modification, t1485-data-destruction, t1496-cryptominer, t1543-002-systemd-service, t1547-006-kernel-module, t1548-001-setuid-binary, t1552-001-credentials-in-files, t1552-007-container-api, t1611-escape-to-host, t1613-container-discovery, t1620-fileless-exec |
| kunai | t1036-005-masquerading, t1485-data-destruction, t1496-cryptominer |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exec | execs_per_sec | 2,336 | 2,437 (-4.3%) | 2,254 (+3.5%) | 2,328 (+0.3%) | 2,181 (+6.6%) | 2,175 (+6.9%) | 2,166 (+7.3%) | 2,154 (+7.8%) | — | 2,273 (+2.7%) | 2,072 (+11.3%) | 2,099 (+10.1%) | — | — | 1,604 (+31.3%) | 1,600 (+31.5%) | 1,316 (+43.7%) | 1,326 (+43.2%) | 2,388 (-2.2%) | 2,260 (+3.3%) |
| exec | p50_us | 406.93 | 365.80 (-10.1%) | 428.85 (+5.4%) | 402.84 (-1.0%) | 458.69 (+12.7%) | 459.25 (+12.9%) | 455.99 (+12.1%) | 459.45 (+12.9%) | — | 403.03 (-1.0%) | 497.81 (+22.3%) | 490.95 (+20.6%) | — | — | 601.85 (+47.9%) | 644.42 (+58.4%) | 776.53 (+90.8%) | 771.31 (+89.5%) | 397.52 (-2.3%) | 421.23 (+3.5%) |
| exec | p99_us | 829.40 | 867.97 (+4.7%) | 832.08 (+0.3%) | 903.26 (+8.9%) | 797.86 (-3.8%) | 805.82 (-2.8%) | 815.63 (-1.7%) | 833.09 (+0.4%) | — | 910.62 (+9.8%) | 1,010 (+21.8%) | 987.00 (+19.0%) | — | — | 948.51 (+14.4%) | 971.90 (+17.2%) | 1,086 (+31.0%) | 1,101 (+32.7%) | 693.18 (-16.4%) | 745.74 (-10.1%) |
| fileio | ops_per_sec | 1,432 | 1,451 (-1.3%) | 1,430 (+0.1%) | 1,432 (-0.0%) | 1,432 (-0.0%) | 1,433 (-0.1%) | 1,431 (+0.1%) | 1,433 (-0.1%) | — | 1,414 (+1.3%) | 1,437 (-0.3%) | 1,431 (+0.0%) | — | — | 1,441 (-0.6%) | 1,436 (-0.3%) | 1,436 (-0.3%) | 1,424 (+0.6%) | 1,406 (+1.8%) | 1,397 (+2.4%) |
| fileio | p50_us | 688.73 | 678.81 (-1.4%) | 690.49 (+0.3%) | 689.66 (+0.1%) | 684.81 (-0.6%) | 684.81 (-0.6%) | 685.79 (-0.4%) | 685.22 (-0.5%) | — | 693.09 (+0.6%) | 687.90 (-0.1%) | 689.44 (+0.1%) | — | — | 685.95 (-0.4%) | 687.49 (-0.2%) | 686.92 (-0.3%) | 693.79 (+0.7%) | 682.62 (-0.9%) | 683.03 (-0.8%) |
| fileio | p99_us | 851.21 | 794.93 (-6.6%) | 841.23 (-1.2%) | 812.87 (-4.5%) | 852.85 (+0.2%) | 839.89 (-1.3%) | 846.73 (-0.5%) | 846.86 (-0.5%) | — | 930.29 (+9.3%) | 805.71 (-5.3%) | 801.86 (-5.8%) | — | — | 799.00 (-6.1%) | 790.19 (-7.2%) | 814.09 (-4.4%) | 807.67 (-5.1%) | 1,173 (+37.8%) | 1,411 (+65.7%) |
| syscall | connect_ops_per_sec | 111,301 | 94,858 (+14.8%) | 96,418 (+13.4%) | 97,999 (+12.0%) | 54,358 (+51.2%) | 53,518 (+51.9%) | 55,139 (+50.5%) | 54,030 (+51.5%) | — | 79,900 (+28.2%) | 78,329 (+29.6%) | 80,399 (+27.8%) | — | — | 55,225 (+50.4%) | 113,439 (-1.9%) | 77,803 (+30.1%) | 79,039 (+29.0%) | 95,302 (+14.4%) | 86,949 (+21.9%) |
| syscall | connect_p50_ns | 4,578 | 5,178 (+13.1%) | 5,066 (+10.7%) | 5,071 (+10.8%) | 8,898 (+94.4%) | 9,048 (+97.6%) | 8,753 (+91.2%) | 9,021 (+97.1%) | — | 7,195 (+57.2%) | 7,340 (+60.3%) | 7,146 (+56.1%) | — | — | 7,841 (+71.3%) | 4,501 (-1.7%) | 6,801 (+48.6%) | 6,517 (+42.4%) | 6,287 (+37.3%) | 6,699 (+46.3%) |
| syscall | connect_p99_ns | 5,584 | 6,245 (+11.8%) | 6,474 (+15.9%) | 6,144 (+10.0%) | 11,161 (+99.9%) | 13,574 (+143.1%) | 13,384 (+139.7%) | 12,889 (+130.8%) | — | 10,337 (+85.1%) | 9,262 (+65.9%) | 9,999 (+79.1%) | — | — | 9,118 (+63.3%) | 5,524 (-1.1%) | 7,930 (+42.0%) | 7,623 (+36.5%) | 7,786 (+39.4%) | 8,455 (+51.4%) |
| syscall | getpid_ops_per_sec | 8,020,788 | 7,254,207 (+9.6%) | 7,520,310 (+6.2%) | 7,435,455 (+7.3%) | 7,322,830 (+8.7%) | 7,115,993 (+11.3%) | 7,250,156 (+9.6%) | 7,253,146 (+9.6%) | — | 7,063,675 (+11.9%) | 7,249,236 (+9.6%) | 7,262,066 (+9.5%) | — | — | 7,892,413 (+1.6%) | 8,232,910 (-2.6%) | 2,356,407 (+70.6%) | 2,447,041 (+69.5%) | 7,720,949 (+3.7%) | 6,310,459 (+21.3%) |
| syscall | getpid_p50_ns | 94.00 | 104.00 (+10.6%) | 102.00 (+8.5%) | 101.00 (+7.4%) | 105.00 (+11.7%) | 110.00 (+17.0%) | 107.00 (+13.8%) | 106.00 (+12.8%) | — | 110.00 (+17.0%) | 106.00 (+12.8%) | 106.00 (+12.8%) | — | — | 95.00 (+1.1%) | 91.00 (-3.2%) | 387.00 (+311.7%) | 372.00 (+295.7%) | 97.00 (+3.2%) | 124.00 (+31.9%) |
| syscall | getpid_p99_ns | 101.00 | 114.00 (+12.9%) | 109.00 (+7.9%) | 113.00 (+11.9%) | 114.00 (+12.9%) | 118.00 (+16.8%) | 116.00 (+14.9%) | 121.00 (+19.8%) | — | 120.00 (+18.8%) | 116.00 (+14.9%) | 117.00 (+15.8%) | — | — | 102.00 (+1.0%) | 99.00 (-2.0%) | 437.00 (+332.7%) | 414.00 (+309.9%) | 108.00 (+6.9%) | 146.00 (+44.6%) |
| syscall | openat_ops_per_sec | 804,354 | 597,327 (+25.7%) | 594,075 (+26.1%) | 609,568 (+24.2%) | 264,644 (+67.1%) | 252,358 (+68.6%) | 250,754 (+68.8%) | 266,028 (+66.9%) | — | 714,114 (+11.2%) | 667,457 (+17.0%) | 680,332 (+15.4%) | — | — | 819,698 (-1.9%) | 824,579 (-2.5%) | 520,383 (+35.3%) | 521,811 (+35.1%) | 377,922 (+53.0%) | 286,299 (+64.4%) |
| syscall | openat_p50_ns | 1,205 | 1,620 (+34.4%) | 1,644 (+36.4%) | 1,596 (+32.4%) | 3,714 (+208.2%) | 3,883 (+222.2%) | 3,769 (+212.8%) | 3,739 (+210.3%) | — | 1,365 (+13.3%) | 1,458 (+21.0%) | 1,440 (+19.5%) | — | — | 1,186 (-1.6%) | 1,177 (-2.3%) | 1,891 (+56.9%) | 1,875 (+55.6%) | 2,478 (+105.6%) | 3,307 (+174.4%) |
| syscall | openat_p99_ns | 1,316 | 1,911 (+45.2%) | 1,863 (+41.6%) | 1,827 (+38.8%) | 4,878 (+270.7%) | 5,069 (+285.2%) | 5,878 (+346.7%) | 4,341 (+229.9%) | — | 1,472 (+11.9%) | 1,582 (+20.2%) | 1,562 (+18.7%) | — | — | 1,279 (-2.8%) | 1,273 (-3.3%) | 2,028 (+54.1%) | 2,029 (+54.2%) | 3,641 (+176.7%) | 4,536 (+244.7%) |
| syscall | read_ops_per_sec | 5,753,055 | 5,213,043 (+9.4%) | 5,449,101 (+5.3%) | 5,430,684 (+5.6%) | 3,752,574 (+34.8%) | 3,759,303 (+34.7%) | 3,761,402 (+34.6%) | 3,754,425 (+34.7%) | — | 2,636,076 (+54.2%) | 2,677,139 (+53.5%) | 2,745,207 (+52.3%) | — | — | 528,082 (+90.8%) | 563,167 (+90.2%) | 262,712 (+95.4%) | 257,054 (+95.5%) | 4,687,157 (+18.5%) | 3,824,420 (+33.5%) |
| syscall | read_p50_ns | 142.00 | 158.00 (+11.3%) | 152.00 (+7.0%) | 150.00 (+5.6%) | 223.00 (+57.0%) | 223.00 (+57.0%) | 222.00 (+56.3%) | 220.00 (+54.9%) | — | 345.00 (+143.0%) | 339.00 (+138.7%) | 331.00 (+133.1%) | — | — | 1,852 (+1204.2%) | 1,737 (+1123.2%) | 3,705 (+2509.2%) | 3,849 (+2610.6%) | 180.00 (+26.8%) | 224.00 (+57.7%) |
| syscall | read_p99_ns | 154.00 | 170.00 (+10.4%) | 164.00 (+6.5%) | 166.00 (+7.8%) | 262.00 (+70.1%) | 261.00 (+69.5%) | 278.00 (+80.5%) | 255.00 (+65.6%) | — | 378.00 (+145.5%) | 371.00 (+140.9%) | 362.00 (+135.1%) | — | — | 2,019 (+1211.0%) | 1,878 (+1119.5%) | 4,269 (+2672.1%) | 4,154 (+2597.4%) | 203.00 (+31.8%) | 261.00 (+69.5%) |
| syscall | stat_ops_per_sec | 2,337,473 | 2,130,745 (+8.8%) | 2,238,919 (+4.2%) | 2,268,862 (+2.9%) | 2,245,726 (+3.9%) | 2,222,804 (+4.9%) | 2,257,208 (+3.4%) | 2,250,255 (+3.7%) | — | 2,310,353 (+1.2%) | 2,259,712 (+3.3%) | 2,265,233 (+3.1%) | — | — | 2,461,796 (-5.3%) | 2,360,187 (-1.0%) | 1,416,283 (+39.4%) | 1,314,457 (+43.8%) | 2,317,890 (+0.8%) | 1,972,875 (+15.6%) |
| syscall | stat_p50_ns | 393.00 | 432.00 (+9.9%) | 411.00 (+4.6%) | 406.00 (+3.3%) | 410.00 (+4.3%) | 416.00 (+5.9%) | 409.00 (+4.1%) | 409.00 (+4.1%) | — | 398.00 (+1.3%) | 407.00 (+3.6%) | 409.00 (+4.1%) | — | — | 372.00 (-5.3%) | 389.00 (-1.0%) | 668.00 (+70.0%) | 724.00 (+84.2%) | 394.00 (+0.3%) | 468.00 (+19.1%) |
| syscall | stat_p99_ns | 433.00 | 477.00 (+10.2%) | 453.00 (+4.6%) | 442.00 (+2.1%) | 449.00 (+3.7%) | 452.00 (+4.4%) | 445.00 (+2.8%) | 448.00 (+3.5%) | — | 432.00 (-0.2%) | 443.00 (+2.3%) | 445.00 (+2.8%) | — | — | 416.00 (-3.9%) | 425.00 (-1.8%) | 751.00 (+73.4%) | 792.00 (+82.9%) | 450.00 (+3.9%) | 529.00 (+22.2%) |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | community | 91.87 | 100.28 | 130.76 | 131.87 | +10.5% | +9.4% | 49.72 | 56.18 | +10.0 pp |
| falco | default | 29.77 | 101.07 | 124.45 | 126.12 | +6.8% | +5.3% | 42.61 | 57.80 | +2.9 pp |
| falco | tuned | 59.53 | 100.42 | 127.34 | 128.26 | +7.6% | +5.6% | 44.60 | 50.75 | +4.9 pp |
| kubearmor | community | 24.42 | 411.23 | 321.35 | 379.51 | +12.8% | +8.7% | 38.28 | 93.43 | -1.4 pp |
| kubearmor | default | 24.07 | 414.75 | 318.10 | 377.59 | +16.9% | +11.3% | 38.40 | 93.66 | -1.3 pp |
| kubearmor | enforce | 24.18 | 407.04 | 322.85 | 415.84 | +14.3% | +9.6% | 38.53 | 93.34 | -1.2 pp |
| kubearmor | tuned | 21.09 | 427.62 | 366.15 | 518.84 | +16.4% | +9.6% | 42.45 | 96.62 | +2.8 pp |
| kunai | community | — | — | — | — | — | — | — | — | — |
| kunai | default | 6.58 | 68.32 | 105.64 | 106.00 | +12.6% | +11.2% | 38.27 | 73.60 | -1.4 pp |
| kunai | enforce | 6.44 | 73.43 | 92.19 | 92.74 | +20.6% | +11.3% | 38.43 | 46.05 | -1.3 pp |
| kunai | tuned | 6.27 | 80.71 | 92.21 | 92.46 | +18.8% | +10.1% | 38.42 | 50.12 | -1.3 pp |
| pulsar | default | — | — | — | — | — | — | — | — | — |
| pulsar | tuned | — | — | — | — | — | — | — | — | — |
| tetragon | community | 7.27 | 302.87 | 557.74 | 7,083 | +1.0% | +1.6% | 38.64 | 79.44 | -1.0 pp |
| tetragon | default | 0.05 | 50.54 | 435.65 | 646.11 | -1.4% | -1.0% | 38.15 | 44.74 | -1.5 pp |
| tetragon | enforce | 0.07 | 51.24 | 394.36 | 546.64 | +63.5% | +39.4% | 38.47 | 44.20 | -1.2 pp |
| tetragon | tuned | 0.06 | 51.27 | 370.52 | 534.14 | +69.3% | +43.2% | 38.26 | 45.99 | -1.4 pp |
| tracee | default | 145.49 | 241.37 | 153.40 | 173.13 | +16.8% | +3.7% | 55.30 | 68.41 | +15.6 pp |
| tracee | tuned | 163.54 | 259.56 | 158.81 | 173.70 | +45.4% | +21.3% | 57.68 | 70.49 | +18.0 pp |

Host CPU is sampled from /proc/stat every second during workloads (Docker backend only); baseline median 39.68%, max 50.32%. The delta is in percentage points of the whole host.

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
| falco | community | 5 | 5 | 0.161s | 33.92 | 40.78 | 0.61 | 94.5% | 95.4% |
| falco | default | 5 | 5 | 0.051s | 10.44 | 15.52 | 0.21 | 100.0% | 100.0% |
| falco | tuned | 5 | 5 | 0.072s | 128.27 | 141.56 | 1.96 | 44.0% | 99.9% |
| kubearmor | community | 3 | 4 | 2.555s | 0.00 | 198,048 | 2,058 | — | — |
| kubearmor | default | 3 | 4 | 2.683s | 0.00 | 200,266 | 2,059 | — | — |
| kubearmor | enforce | 3 | 4 | 2.589s | 0.00 | 204,975 | 2,058 | — | — |
| kubearmor | tuned | 3 | 4 | 2.639s | 0.00 | 188,517 | 2,048 | — | — |
| kunai | community | 3 | 4 | — | — | — | — | — | — |
| kunai | default | 3 | 4 | 0.862s | 0.00 | 136,200 | 2,048 | — | — |
| kunai | enforce | 3 | 4 | 0.940s | — | — | — | — | — |
| kunai | tuned | 3 | 4 | 0.828s | 75.49 | 89.27 | 1.61 | 43.2% | 99.9% |
| pulsar | default | 4 | 4 | — | — | — | — | — | — |
| pulsar | tuned | 4 | 4 | — | — | — | — | — | — |
| tetragon | community | 5 | 4 | 12.399s | 93,541 | 114,999 | 1,942 | 2.3% | 99.3% |
| tetragon | default | 5 | 4 | 6.824s | 578.09 | 22,416 | 247.75 | 67.0% | 75.6% |
| tetragon | enforce | 5 | 4 | 22.085s | 628.92 | 18,718 | 208.69 | 53.8% | 78.2% |
| tetragon | tuned | 5 | 4 | 22.691s | 1,163 | 18,693 | 220.22 | 75.2% | 87.9% |
| tracee | default | 4 | 4 | 2.127s | 117.15 | 137.87 | 3.16 | 4.1% | 64.4% |
| tracee | tuned | 4 | 4 | 2.323s | 155.20 | 175.54 | 3.87 | 27.6% | 73.2% |

## Matched rules

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | community | t1059-004-reverse-shell | Redirect STDOUT/STDIN to Network Connection in Container, System procs network activity |
| falco | community | t1053-003-cron-persistence | Schedule Cron Jobs |
| falco | community | t1098-004-ssh-authorized-keys | Adding ssh keys to authorized_keys, Read ssh information |
| falco | community | t1136-001-create-account | Modify Shell Configuration File |
| falco | community | t1543-002-systemd-service | Write below etc |
| falco | community | t1547-006-kernel-module | Linux Kernel Module Injection Detected |
| falco | community | t1548-001-setuid-binary | Drop and execute new binary in container, Set Setuid or Setgid bit |
| falco | community | t1611-escape-to-host | Change thread namespace, Mount Launched in Privileged Container |
| falco | community | t1036-005-masquerading | Drop and execute new binary in container |
| falco | community | t1070-002-clear-logs | Clear Log Activities |
| falco | community | t1070-003-clear-history | Delete or rename shell history, Modify Shell Configuration File, Write below root |
| falco | community | t1620-fileless-exec | Fileless execution via memfd_create |
| falco | community | t1003-008-shadow-read | Read sensitive file untrusted |
| falco | community | t1552-001-credentials-in-files | Find AWS Credentials, Read ssh information, Search Private Keys or Passwords |
| falco | community | t1046-network-scan | Launch Suspicious Network Tool in Container |
| falco | community | t1105-ingress-tool-transfer | Launch Ingress Remote File Copy Tools in Container |
| falco | community | t1048-exfiltration-http | Launch Ingress Remote File Copy Tools in Container, Read sensitive file untrusted, Read ssh information |
| falco | community | t1485-data-destruction | Remove Bulk Data from Disk |
| falco | community | t1496-cryptominer | Drop and execute new binary in container |
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
| tetragon | community | t1059-004-reverse-shell | accept, connect, creds-capability-checks, file-monitoring-filtered, privileges-raise, privileges-setuid-root, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1059-006-python-exec | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1053-003-cron-persistence | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1098-004-ssh-authorized-keys | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1136-001-create-account | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1543-002-systemd-service | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1547-006-kernel-module | creds-capability-checks, monitor-kernel-modules, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1548-001-setuid-binary | creds-capability-checks, privileges-raise, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1611-escape-to-host | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1036-005-masquerading | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1070-002-clear-logs | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1070-003-clear-history | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1222-002-permission-modification | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1620-fileless-exec | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1003-008-shadow-read | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1552-001-credentials-in-files | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1552-007-container-api | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1046-network-scan | accept, connect, creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1082-system-discovery | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1613-container-discovery | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1105-ingress-tool-transfer | accept, connect, creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1048-exfiltration-http | accept, connect, creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1485-data-destruction | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | t1496-cryptominer | accept, connect, creds-capability-checks, process-creds-changed, process-exec-elf-begin |
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
| tetragon | enforce | t1222-002-permission-modification | credential-file-read, file-monitoring-filtered, permission-change |
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
| kunai | running | — |
| pulsar | pending | — |

### Log overflow

Deployments whose log or alerts stream exceeded `max_log_lines` / `max_log_bytes`: lines after the cap were dropped, so alerts emitted after it are missing and detection results are a lower bound.

| Tool | Profile | Dropped log lines | Dropped alerts file lines | Dropped MiB |
| --- | --- | --- | --- | --- |
| kubearmor | community | 0 | 3456964 | 2,793 |
| kubearmor | default | 0 | 3376526 | 2,722 |
| kubearmor | enforce | 0 | 3614273 | 2,922 |
| kubearmor | tuned | 0 | 5093708 | 4,115 |
| kunai | default | 195774 | 0 | 207.71 |

### Scenario executions with a non-zero exit code

| Tool | Profile | Scenario | Repetition | Exit code |
| --- | --- | --- | --- | --- |
| kubearmor | enforce | t1003-008-shadow-read | 0 | 1 |
| kubearmor | enforce | t1003-008-shadow-read | 1 | 1 |
| kubearmor | enforce | t1003-008-shadow-read | 2 | 1 |
| kubearmor | enforce | t1003-008-shadow-read | 3 | 1 |
| kubearmor | enforce | t1003-008-shadow-read | 4 | 1 |
| kubearmor | enforce | t1036-005-masquerading | 0 | 1 |
| kubearmor | enforce | t1036-005-masquerading | 1 | 1 |
| kubearmor | enforce | t1036-005-masquerading | 2 | 1 |
| kubearmor | enforce | t1036-005-masquerading | 3 | 1 |
| kubearmor | enforce | t1036-005-masquerading | 4 | 1 |
| kubearmor | enforce | t1046-network-scan | 0 | 1 |
| kubearmor | enforce | t1046-network-scan | 1 | 1 |
| kubearmor | enforce | t1046-network-scan | 2 | 1 |
| kubearmor | enforce | t1046-network-scan | 3 | 1 |
| kubearmor | enforce | t1046-network-scan | 4 | 1 |
| kubearmor | enforce | t1053-003-cron-persistence | 0 | 1 |
| kubearmor | enforce | t1053-003-cron-persistence | 1 | 1 |
| kubearmor | enforce | t1053-003-cron-persistence | 2 | 1 |
| kubearmor | enforce | t1053-003-cron-persistence | 3 | 1 |
| kubearmor | enforce | t1053-003-cron-persistence | 4 | 1 |
| kubearmor | enforce | t1059-004-reverse-shell | 0 | 1 |
| kubearmor | enforce | t1059-004-reverse-shell | 1 | 1 |
| kubearmor | enforce | t1059-004-reverse-shell | 2 | 1 |
| kubearmor | enforce | t1059-004-reverse-shell | 3 | 1 |
| kubearmor | enforce | t1059-004-reverse-shell | 4 | 1 |
| kubearmor | enforce | t1059-006-python-exec | 0 | 1 |
| kubearmor | enforce | t1059-006-python-exec | 1 | 1 |
| kubearmor | enforce | t1059-006-python-exec | 2 | 1 |
| kubearmor | enforce | t1059-006-python-exec | 3 | 1 |
| kubearmor | enforce | t1059-006-python-exec | 4 | 1 |
| kubearmor | enforce | t1070-002-clear-logs | 0 | 1 |
| kubearmor | enforce | t1070-002-clear-logs | 1 | 1 |
| kubearmor | enforce | t1070-002-clear-logs | 2 | 1 |
| kubearmor | enforce | t1070-002-clear-logs | 3 | 1 |
| kubearmor | enforce | t1070-002-clear-logs | 4 | 1 |
| kubearmor | enforce | t1070-003-clear-history | 0 | 1 |
| kubearmor | enforce | t1070-003-clear-history | 1 | 1 |
| kubearmor | enforce | t1070-003-clear-history | 2 | 1 |
| kubearmor | enforce | t1070-003-clear-history | 3 | 1 |
| kubearmor | enforce | t1070-003-clear-history | 4 | 1 |
| kubearmor | enforce | t1082-system-discovery | 0 | 1 |
| kubearmor | enforce | t1082-system-discovery | 1 | 1 |
| kubearmor | enforce | t1082-system-discovery | 2 | 1 |
| kubearmor | enforce | t1082-system-discovery | 3 | 1 |
| kubearmor | enforce | t1082-system-discovery | 4 | 1 |
| kubearmor | enforce | t1098-004-ssh-authorized-keys | 0 | 1 |
| kubearmor | enforce | t1098-004-ssh-authorized-keys | 1 | 1 |
| kubearmor | enforce | t1098-004-ssh-authorized-keys | 2 | 1 |
| kubearmor | enforce | t1098-004-ssh-authorized-keys | 3 | 1 |
| kubearmor | enforce | t1098-004-ssh-authorized-keys | 4 | 1 |
| kubearmor | enforce | t1105-ingress-tool-transfer | 0 | 1 |
| kubearmor | enforce | t1105-ingress-tool-transfer | 1 | 1 |
| kubearmor | enforce | t1105-ingress-tool-transfer | 2 | 1 |
| kubearmor | enforce | t1105-ingress-tool-transfer | 3 | 1 |
| kubearmor | enforce | t1105-ingress-tool-transfer | 4 | 1 |
| kubearmor | enforce | t1136-001-create-account | 0 | 1 |
| kubearmor | enforce | t1136-001-create-account | 1 | 1 |
| kubearmor | enforce | t1136-001-create-account | 2 | 1 |
| kubearmor | enforce | t1136-001-create-account | 3 | 1 |
| kubearmor | enforce | t1136-001-create-account | 4 | 1 |
| kubearmor | enforce | t1222-002-permission-modification | 0 | 1 |
| kubearmor | enforce | t1222-002-permission-modification | 1 | 1 |
| kubearmor | enforce | t1222-002-permission-modification | 2 | 1 |
| kubearmor | enforce | t1222-002-permission-modification | 3 | 1 |
| kubearmor | enforce | t1222-002-permission-modification | 4 | 1 |
| kubearmor | enforce | t1485-data-destruction | 0 | 1 |
| kubearmor | enforce | t1485-data-destruction | 1 | 1 |
| kubearmor | enforce | t1485-data-destruction | 2 | 1 |
| kubearmor | enforce | t1485-data-destruction | 3 | 1 |
| kubearmor | enforce | t1485-data-destruction | 4 | 1 |
| kubearmor | enforce | t1496-cryptominer | 0 | 1 |
| kubearmor | enforce | t1496-cryptominer | 1 | 1 |
| kubearmor | enforce | t1496-cryptominer | 2 | 1 |
| kubearmor | enforce | t1496-cryptominer | 3 | 1 |
| kubearmor | enforce | t1496-cryptominer | 4 | 1 |
| kubearmor | enforce | t1543-002-systemd-service | 0 | 1 |
| kubearmor | enforce | t1543-002-systemd-service | 1 | 1 |
| kubearmor | enforce | t1543-002-systemd-service | 2 | 1 |
| kubearmor | enforce | t1543-002-systemd-service | 3 | 1 |
| kubearmor | enforce | t1543-002-systemd-service | 4 | 1 |
| kubearmor | enforce | t1547-006-kernel-module | 0 | 1 |
| kubearmor | enforce | t1547-006-kernel-module | 1 | 1 |
| kubearmor | enforce | t1547-006-kernel-module | 2 | 1 |
| kubearmor | enforce | t1547-006-kernel-module | 3 | 1 |
| kubearmor | enforce | t1547-006-kernel-module | 4 | 1 |
| kubearmor | enforce | t1552-007-container-api | 0 | 1 |
| kubearmor | enforce | t1552-007-container-api | 1 | 1 |
| kubearmor | enforce | t1552-007-container-api | 2 | 1 |
| kubearmor | enforce | t1552-007-container-api | 3 | 1 |
| kubearmor | enforce | t1552-007-container-api | 4 | 1 |
| kubearmor | enforce | t1611-escape-to-host | 0 | 1 |
| kubearmor | enforce | t1611-escape-to-host | 1 | 1 |
| kubearmor | enforce | t1611-escape-to-host | 2 | 1 |
| kubearmor | enforce | t1611-escape-to-host | 3 | 1 |
| kubearmor | enforce | t1611-escape-to-host | 4 | 1 |
| kubearmor | enforce | t1613-container-discovery | 0 | 1 |
| kubearmor | enforce | t1613-container-discovery | 1 | 1 |
| kubearmor | enforce | t1613-container-discovery | 2 | 1 |
| kubearmor | enforce | t1613-container-discovery | 3 | 1 |
| kubearmor | enforce | t1613-container-discovery | 4 | 1 |
| kubearmor | enforce | t1620-fileless-exec | 0 | 1 |
| kubearmor | enforce | t1620-fileless-exec | 1 | 1 |
| kubearmor | enforce | t1620-fileless-exec | 2 | 1 |
| kubearmor | enforce | t1620-fileless-exec | 3 | 1 |
| kubearmor | enforce | t1620-fileless-exec | 4 | 1 |
| kunai | enforce | t1036-005-masquerading | 0 | 1 |
| kunai | enforce | t1036-005-masquerading | 1 | 1 |
| kunai | enforce | t1036-005-masquerading | 2 | 1 |
| kunai | enforce | t1036-005-masquerading | 3 | 1 |
| kunai | enforce | t1036-005-masquerading | 4 | 1 |
| kunai | enforce | t1485-data-destruction | 0 | 1 |
| kunai | enforce | t1485-data-destruction | 1 | 1 |
| kunai | enforce | t1485-data-destruction | 2 | 1 |
| kunai | enforce | t1485-data-destruction | 3 | 1 |
| kunai | enforce | t1485-data-destruction | 4 | 1 |
| kunai | enforce | t1496-cryptominer | 0 | 1 |
| kunai | enforce | t1496-cryptominer | 1 | 1 |
| kunai | enforce | t1496-cryptominer | 2 | 1 |
| kunai | enforce | t1496-cryptominer | 3 | 1 |
| kunai | enforce | t1496-cryptominer | 4 | 1 |
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
