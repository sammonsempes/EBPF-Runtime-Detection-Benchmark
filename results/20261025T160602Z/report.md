# eBPF runtime detection benchmark: 20261025T160602Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261025T160602Z |
| grace_seconds | 10.0 |
| host.architecture | amd64 |
| host.backend | kubernetes |
| host.container_runtime | containerd://2.1.1 |
| host.cpus | 8 |
| host.kernel | 6.12.105+deb13-amd64 |
| host.kube_context | kind-ebpf-bench |
| host.kubelet_version | v1.33.1 |
| host.kubernetes_version | v1.33.1 |
| host.memory_bytes | 33201963008.0 |
| host.namespace | ebpf-bench |
| host.node | ebpf-bench-control-plane |
| host.operating_system | Debian GNU/Linux 12 (bookworm) |
| host.runner_python | 3.12.15 |
| config.backend | kubernetes |
| config.control_scenarios | True |
| config.grace_seconds | 10 |
| config.idle_seconds | 3 |
| config.kubernetes | {"context": "kind-ebpf-bench", "kubeconfig": null, "namespace": "ebpf-bench", "node": null} |
| config.max_log_bytes | 16106127360 |
| config.max_log_lines | 15000000 |
| config.overhead | {"duration_seconds": 30, "enabled": true, "repetitions": 3, "workloads": ["syscall", "exec", "fileio"]} |
| config.profiles | ["default", "tuned", "enforce", "community"] |
| config.repetitions | 5 |
| config.results_dir | results |
| config.scenarios | all |
| config.tools | ["falco", "tetragon", "tracee", "kubearmor", "kunai", "pulsar"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| falco | 0.45.0 | partial | community, default, tuned | community: bad5350a7c3a, default: a9318548d127, enforce: None, tuned: 18d84b1b69aa |
| kubearmor | 1.7.5 | partial | community, default, enforce, tuned | community: cf1c6c0ff99c, default: 15ef430d85e9, enforce: b81f0ff463d7, tuned: 12cfa057de2f |
| kunai | 0.6.2 | ok | community, default, enforce, tuned | community: a8d2102db595, default: ea10f4f706e7, enforce: df81b47e0a5b, tuned: 3c0a05fb5002 |
| pulsar | 0.10.1 | partial | default, tuned | community: None, default: 9cb2665a655e, enforce: None, tuned: dd1914d53753 |
| tetragon | 1.7.1 | partial | community, default, enforce, tuned | community: 1451971dd8bf, default: 4eb2531db490, enforce: 4b4c1eeaecc5, tuned: 39c0c7d92c85 |
| tracee | 0.24.1 | ok | default, tuned | community: None, default: c5763fb3419e, enforce: None, tuned: 3bffc520aa3d |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | tuned | 100.0% | 100.0% | 16.7% | 0.555s | 0 | 19.68 | 529.54 | -0.1% |
| falco | tuned | 100.0% | 100.0% | 33.3% | 0.002s | 6 | 32.66 | 143.58 | +8.2% |
| kunai | tuned | 100.0% | 100.0% | 33.3% | 0.087s | 0 | 13.07 | 93.90 | +12.1% |
| kunai | enforce | 100.0% | 100.0% | 33.3% | 0.089s | 0 | 21.61 | 92.66 | +10.5% |
| tracee | tuned | 91.7% | 91.7% | 33.3% | 0.002s | 0 | 123.98 | 168.65 | +19.7% |
| falco | default | 45.8% | 45.8% | 16.7% | 0.002s | 6 | 23.26 | 146.27 | +9.3% |
| tetragon | default | 45.8% | 45.8% | 16.7% | 0.510s | 0 | 7.16 | 617.58 | -41.9% |
| kunai | community | 20.8% | 20.8% | 0.0% | 0.079s | 0 | 21.22 | 89.62 | +9.2% |
| tracee | default | 20.8% | 20.8% | 16.7% | 0.006s | 0 | 109.25 | 157.64 | +10.3% |
| kubearmor | default | 0.0% | 0.0% | 0.0% | — | 0 | 52.83 | 4,880 | +21.4% |
| kubearmor | tuned | 0.0% | 0.0% | 0.0% | — | 0 | 55.41 | 5,834 | +18.6% |
| kunai | default | 0.0% | 0.0% | 0.0% | — | 0 | 61.94 | 139.62 | +39.0% |
| falco | community | — | — | — | — | 0 | — | — | — |
| kubearmor | community | — | — | — | — | 0 | — | — | — |
| kubearmor | enforce | — | — | — | — | 0 | — | — | — |
| pulsar | default | — | — | — | — | 0 | — | — | — |
| pulsar | tuned | — | — | — | — | 0 | — | — | — |
| tetragon | community | — | — | — | — | 0 | — | — | — |
| tetragon | enforce | — | — | — | — | 0 | — | — | — |

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

| Tactic | Scenario | Technique | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| execution | t1059-006-python-exec | T1059.006 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1053-003-cron-persistence | T1053.003 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1136-001-create-account | T1136.001 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1543-002-systemd-service | T1543.002 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1547-006-kernel-module | T1547.006 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1611-escape-to-host | T1611 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| defense-evasion | t1036-005-masquerading | T1036.005 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-002-clear-logs | T1070.002 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-003-clear-history | T1070.003 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1222-002-permission-modification | T1222.002 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1620-fileless-exec | T1620 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| credential-access | t1003-008-shadow-read | T1003.008 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-001-credentials-in-files | T1552.001 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1552-007-container-api | T1552.007 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| discovery | t1046-network-scan (invalid) | T1046 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 (invalid) | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1082-system-discovery | T1082 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1613-container-discovery | T1613 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| command-and-control | t1105-ingress-tool-transfer | T1105 | — | ❌ 0/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| exfiltration | t1048-exfiltration-http | T1048 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ✅ 5/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1485-data-destruction | T1485 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1496-cryptominer | T1496 | — | ✅ 5/5 | ✅ 5/5 | — | ❌ 0/5 | — | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | — | — | — | ❌ 0/5 | — | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |

### Coverage per tactic

| Tactic | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | — | 1/2 | 2/2 | — | 0/2 | — | 0/2 | 0/2 | 0/2 | 2/2 | 2/2 | — | — | — | 1/2 | — | 2/2 | 1/2 | 2/2 |
| persistence | — | 1/5 | 5/5 | — | 0/5 | — | 0/5 | 0/5 | 0/5 | 5/5 | 5/5 | — | — | — | 5/5 | — | 5/5 | 1/5 | 3/5 |
| privilege-escalation | — | 1/2 | 2/2 | — | 0/2 | — | 0/2 | 1/2 | 0/2 | 2/2 | 2/2 | — | — | — | 1/2 | — | 2/2 | 1/2 | 2/2 |
| defense-evasion | — | 3/5 | 5/5 | — | 0/5 | — | 0/5 | 2/5 | 0/5 | 5/5 | 5/5 | — | — | — | 1/5 | — | 5/5 | 1/5 | 5/5 |
| credential-access | — | 2/3 | 3/3 | — | 0/3 | — | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | — | — | — | 2/3 | — | 3/3 | 1/3 | 3/3 |
| discovery | — | 0/3 | 3/3 | — | 0/3 | — | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | — | — | — | 0/3 | — | 3/3 | 0/3 | 3/3 |
| command-and-control | — | 0/1 | 1/1 | — | 0/1 | — | 0/1 | 1/1 | 0/1 | 1/1 | 1/1 | — | — | — | 0/1 | — | 1/1 | 0/1 | 1/1 |
| exfiltration | — | 1/1 | 1/1 | — | 0/1 | — | 0/1 | 0/1 | 0/1 | 1/1 | 1/1 | — | — | — | 1/1 | — | 1/1 | 0/1 | 1/1 |
| impact | — | 2/2 | 2/2 | — | 0/2 | — | 0/2 | 1/2 | 0/2 | 2/2 | 2/2 | — | — | — | 0/2 | — | 2/2 | 0/2 | 2/2 |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benign-admin-commands | — | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | — | — | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 |
| benign-backup | — | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-compile | — | ⚠️ 5/5 | ⚠️ 5/5 | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | — | ✅ 0/5 | — | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 |
| benign-log-rotation | — | ✅ 0/5 | ⚠️ 5/5 | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | — | ⚠️ 5/5 | — | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 |
| benign-package-query | — | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | — | — | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-web-server | — | ✅ 0/5 | ✅ 0/5 | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | — | — | — | ✅ 0/5 | — | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | default | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-compile | Drop and execute new binary in container |
| falco | tuned | benign-log-rotation | Log File Deleted or Truncated |
| kunai | enforce | benign-admin-commands | discovery.system.information |
| kunai | enforce | benign-web-server | download.to.tmpfs |
| kunai | tuned | benign-admin-commands | discovery.system.information |
| kunai | tuned | benign-web-server | download.to.tmpfs |
| tetragon | default | benign-log-rotation | file-monitoring-filtered |
| tetragon | tuned | benign-log-rotation | file-monitoring-filtered, history-and-log-tampering |
| tracee | default | benign-compile | New executable dropped |
| tracee | tuned | benign-admin-commands | detect-container-discovery |
| tracee | tuned | benign-compile | New executable dropped |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1059-004-reverse-shell | — | 0.004s / 0.004s | 0.003s / 0.003s | — | — | — | — | — | — | 0.100s / 0.120s | 0.068s / 0.104s | — | — | — | 0.838s / 0.986s | — | 0.530s / 0.905s | 0.003s / 0.003s | 0.002s / 0.005s |
| t1059-006-python-exec | — | — | 0.022s / 0.022s | — | — | — | — | — | — | 0.077s / 0.139s | 0.102s / 0.125s | — | — | — | — | — | 0.444s / 0.928s | — | 0.021s / 0.021s |
| t1053-003-cron-persistence | — | — | 0.001s / 0.001s | — | — | — | — | — | — | 0.063s / 0.119s | 0.099s / 0.117s | — | — | — | 0.228s / 0.853s | — | 0.566s / 0.834s | 0.000s / 0.001s | 0.001s / 0.001s |
| t1098-004-ssh-authorized-keys | — | — | 0.002s / 0.005s | — | — | — | — | — | — | 0.091s / 0.108s | 0.081s / 0.102s | — | — | — | 0.523s / 0.811s | — | 0.333s / 0.840s | — | — |
| t1136-001-create-account | — | — | 0.001s / 0.002s | — | — | — | — | — | — | 0.046s / 0.097s | 0.061s / 0.130s | — | — | — | 0.474s / 0.839s | — | 0.629s / 0.812s | — | 0.001s / 0.002s |
| t1543-002-systemd-service | — | — | 0.001s / 0.001s | — | — | — | — | — | — | 0.055s / 0.126s | 0.087s / 0.129s | — | — | — | 0.478s / 0.861s | — | 0.460s / 0.827s | — | — |
| t1547-006-kernel-module | — | 0.002s / 0.003s | 0.001s / 0.001s | — | — | — | — | — | — | 0.045s / 0.105s | 0.097s / 0.119s | — | — | — | 0.311s / 0.733s | — | 0.492s / 0.931s | — | 0.001s / 0.001s |
| t1548-001-setuid-binary | — | 0.006s / 0.006s | 0.003s / 0.003s | — | — | — | — | 0.103s / 0.135s | — | 0.097s / 0.118s | 0.064s / 0.113s | — | — | — | 0.832s / 0.960s | — | 0.542s / 0.906s | — | 0.003s / 0.003s |
| t1611-escape-to-host | — | — | 0.001s / 0.002s | — | — | — | — | — | — | 0.064s / 0.116s | 0.051s / 0.098s | — | — | — | — | — | 0.478s / 0.890s | 0.006s / 0.006s | 0.001s / 0.001s |
| t1036-005-masquerading | — | 0.003s / 0.004s | 0.003s / 0.003s | — | — | — | — | 0.080s / 0.117s | — | 0.098s / 0.133s | 0.101s / 0.128s | — | — | — | — | — | 0.676s / 1.762s | — | 0.003s / 0.003s |
| t1070-002-clear-logs | — | -0.018s / -0.018s | -0.020s / -0.018s | — | — | — | — | — | — | 0.121s / 0.128s | 0.090s / 0.125s | — | — | — | 0.438s / 0.842s | — | 0.180s / 0.826s | — | 0.002s / 0.004s |
| t1070-003-clear-history | — | — | 0.004s / 0.004s | — | — | — | — | — | — | 0.093s / 0.123s | 0.095s / 0.115s | — | — | — | — | — | 0.745s / 0.971s | — | 0.001s / 0.003s |
| t1222-002-permission-modification | — | — | 0.002s / 0.002s | — | — | — | — | — | — | 0.084s / 0.105s | 0.090s / 0.110s | — | — | — | — | — | 0.347s / 0.572s | — | 0.001s / 0.001s |
| t1620-fileless-exec | — | 0.008s / 0.012s | 0.011s / 0.012s | — | — | — | — | 0.076s / 0.093s | — | 0.110s / 0.117s | 0.115s / 0.127s | — | — | — | — | — | 0.495s / 0.783s | 0.010s / 0.011s | 0.011s / 0.012s |
| t1003-008-shadow-read | — | 0.002s / 0.002s | 0.001s / 0.002s | — | — | — | — | — | — | 0.116s / 0.129s | 0.076s / 0.130s | — | — | — | 0.753s / 0.926s | — | 0.913s / 0.947s | — | 0.001s / 0.001s |
| t1552-001-credentials-in-files | — | 0.001s / 0.001s | 0.001s / 0.001s | — | — | — | — | — | — | 0.083s / 0.108s | 0.100s / 0.133s | — | — | — | 0.633s / 0.666s | — | 0.464s / 0.919s | — | 0.003s / 0.004s |
| t1552-007-container-api | — | — | 0.003s / 0.003s | — | — | — | — | — | — | 0.070s / 0.090s | 0.057s / 0.126s | — | — | — | — | — | 0.364s / 0.861s | 0.010s / 0.010s | 0.003s / 0.003s |
| t1046-network-scan | — | — | 0.002s / 0.002s | — | — | — | — | — | — | 0.106s / 0.128s | 0.074s / 0.108s | — | — | — | — | — | 0.782s / 1.337s | — | 0.002s / 0.002s |
| t1082-system-discovery | — | — | 0.001s / 0.001s | — | — | — | — | — | — | 0.081s / 0.118s | 0.077s / 0.115s | — | — | — | — | — | 0.606s / 0.737s | — | 0.001s / 0.001s |
| t1613-container-discovery | — | — | 0.002s / 0.003s | — | — | — | — | — | — | 0.092s / 0.112s | 0.073s / 0.115s | — | — | — | — | — | 0.244s / 0.735s | — | 0.002s / 0.002s |
| t1105-ingress-tool-transfer | — | — | 0.010s / 0.010s | — | — | — | — | 0.071s / 0.110s | — | 0.116s / 0.127s | 0.065s / 0.087s | — | — | — | — | — | 0.612s / 0.872s | — | 0.015s / 0.016s |
| t1048-exfiltration-http | — | 0.002s / 0.003s | 0.002s / 0.003s | — | — | — | — | — | — | 0.110s / 0.126s | 0.078s / 0.095s | — | — | — | 0.323s / 0.659s | — | 0.556s / 0.883s | — | 0.002s / 0.002s |
| t1485-data-destruction | — | 0.001s / 0.002s | 0.001s / 0.002s | — | — | — | — | — | — | 0.101s / 0.115s | 0.096s / 0.117s | — | — | — | — | — | 0.800s / 1.081s | — | 0.001s / 0.001s |
| t1496-cryptominer | — | 0.001s / 0.001s | 0.001s / 0.002s | — | — | — | — | 0.063s / 0.102s | — | 0.067s / 0.118s | 0.093s / 0.120s | — | — | — | — | — | 0.680s / 2.725s | — | 0.001s / 0.003s |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| falco | community | — | 0 |
| falco | default | 100.0% | 5 |
| falco | tuned | 100.0% | 5 |
| kubearmor | community | — | 0 |
| kubearmor | default | 100.0% | 0 |
| kubearmor | enforce | — | 0 |
| kubearmor | tuned | 100.0% | 0 |
| kunai | community | 100.0% | 0 |
| kunai | default | 100.0% | 0 |
| kunai | enforce | 100.0% | 0 |
| kunai | tuned | 100.0% | 0 |
| pulsar | default | — | 0 |
| pulsar | tuned | — | 0 |
| tetragon | community | — | 0 |
| tetragon | default | 100.0% | 0 |
| tetragon | enforce | — | 0 |
| tetragon | tuned | 100.0% | 0 |
| tracee | default | 100.0% | 0 |
| tracee | tuned | 100.0% | 0 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | detection only | — | — | — | — | — | — | — | — |
| kubearmor | — | 0 | 0 | 0 (—) | — | 0 | — | bpf-lsm, apparmor, selinux-host-only, presets | yes |
| kunai | 0.0% (0/23) | 115 | 0 | 0 (0.0%) | 0.083s | 305 | yes | kill | no |
| pulsar | detection only | — | — | — | — | — | — | — | — |
| tetragon | — | 0 | 0 | 0 (—) | — | 0 | — | sigkill | yes |
| tracee | detection only | — | — | — | — | — | — | — | — |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | falco/community | falco/default | falco/tuned | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned | tetragon/community | tetragon/default | tetragon/enforce | tetragon/tuned | tracee/default | tracee/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exec | execs_per_sec | 1,657 | — | 1,581 (+4.6%) | 1,592 (+3.9%) | — | 1,352 (+18.4%) | — | 1,349 (+18.6%) | 1,405 (+15.2%) | 1,445 (+12.8%) | 1,393 (+15.9%) | 1,399 (+15.5%) | — | — | — | 1,613 (+2.6%) | — | 1,331 (+19.6%) | 1,459 (+11.9%) | 1,394 (+15.8%) |
| exec | p50_us | 617.07 | — | 626.38 (+1.5%) | 608.73 (-1.4%) | — | 722.00 (+17.0%) | — | 717.56 (+16.3%) | 676.24 (+9.6%) | 655.10 (+6.2%) | 685.80 (+11.1%) | 681.29 (+10.4%) | — | — | — | 593.72 (-3.8%) | — | 720.73 (+16.8%) | 665.39 (+7.8%) | 697.55 (+13.0%) |
| exec | p99_us | 979.20 | — | 1,060 (+8.3%) | 1,059 (+8.2%) | — | 1,151 (+17.6%) | — | 1,136 (+16.0%) | 1,308 (+33.6%) | 2,728 (+178.6%) | 1,311 (+33.9%) | 1,295 (+32.2%) | — | — | — | 1,082 (+10.5%) | — | 1,330 (+35.8%) | 1,094 (+11.8%) | 1,144 (+16.8%) |
| fileio | ops_per_sec | 1,428 | — | 1,425 (+0.2%) | 1,425 (+0.2%) | — | 1,422 (+0.4%) | — | 1,416 (+0.8%) | 1,423 (+0.3%) | 1,187 (+16.9%) | 1,424 (+0.2%) | 1,422 (+0.4%) | — | — | — | 1,431 (-0.3%) | — | 1,428 (-0.0%) | 1,401 (+1.8%) | 1,391 (+2.6%) |
| fileio | p50_us | 689.57 | — | 687.78 (-0.3%) | 689.24 (-0.0%) | — | 688.04 (-0.2%) | — | 688.87 (-0.1%) | 690.30 (+0.1%) | 730.78 (+6.0%) | 689.76 (+0.0%) | 690.03 (+0.1%) | — | — | — | 687.26 (-0.3%) | — | 688.19 (-0.2%) | 690.49 (+0.1%) | 691.42 (+0.3%) |
| fileio | p99_us | 871.89 | — | 883.10 (+1.3%) | 882.87 (+1.3%) | — | 915.69 (+5.0%) | — | 925.90 (+6.2%) | 899.80 (+3.2%) | 2,558 (+193.4%) | 903.79 (+3.7%) | 911.61 (+4.6%) | — | — | — | 857.51 (-1.6%) | — | 872.33 (+0.1%) | 951.92 (+9.2%) | 1,031 (+18.2%) |
| syscall | connect_ops_per_sec | 95,002 | — | 82,399 (+13.3%) | 81,653 (+14.1%) | — | 44,893 (+52.7%) | — | 45,685 (+51.9%) | 74,055 (+22.0%) | 62,521 (+34.2%) | 69,664 (+26.7%) | 80,132 (+15.7%) | — | — | — | 137,710 (-45.0%) | — | 91,385 (+3.8%) | 77,185 (+18.8%) | 69,463 (+26.9%) |
| syscall | connect_p50_ns | 4,638 | — | 5,208 (+12.3%) | 5,286 (+14.0%) | — | 10,313 (+122.4%) | — | 10,150 (+118.8%) | 6,901 (+48.8%) | 8,362 (+80.3%) | 7,547 (+62.7%) | 6,368 (+37.3%) | — | — | — | 3,196 (-31.1%) | — | 5,143 (+10.9%) | 7,074 (+52.5%) | 7,775 (+67.6%) |
| syscall | connect_p99_ns | 5,438 | — | 6,177 (+13.6%) | 6,262 (+15.2%) | — | 13,671 (+151.4%) | — | 13,407 (+146.5%) | 9,676 (+77.9%) | 11,444 (+110.4%) | 11,416 (+109.9%) | 8,382 (+54.1%) | — | — | — | 3,926 (-27.8%) | — | 5,989 (+10.1%) | 9,249 (+70.1%) | 10,034 (+84.5%) |
| syscall | getpid_ops_per_sec | 2,534,416 | — | 2,364,865 (+6.7%) | 2,363,148 (+6.8%) | — | 2,416,111 (+4.7%) | — | 2,427,546 (+4.2%) | 2,435,165 (+3.9%) | 1,888,747 (+25.5%) | 2,464,794 (+2.7%) | 2,338,150 (+7.7%) | — | — | — | 8,688,166 (-242.8%) | — | 2,572,145 (-1.5%) | 2,320,772 (+8.4%) | 2,151,111 (+15.1%) |
| syscall | getpid_p50_ns | 359.00 | — | 387.00 (+7.8%) | 388.00 (+8.1%) | — | 377.00 (+5.0%) | — | 375.00 (+4.5%) | 372.00 (+3.6%) | 472.00 (+31.5%) | 371.00 (+3.3%) | 388.00 (+8.1%) | — | — | — | 84.00 (-76.6%) | — | 353.00 (-1.7%) | 391.00 (+8.9%) | 424.00 (+18.1%) |
| syscall | getpid_p99_ns | 399.00 | — | 442.00 (+10.8%) | 432.00 (+8.3%) | — | 418.00 (+4.8%) | — | 420.00 (+5.3%) | 416.00 (+4.3%) | 586.00 (+46.9%) | 412.00 (+3.3%) | 435.00 (+9.0%) | — | — | — | 90.00 (-77.4%) | — | 399.00 (+0.0%) | 436.00 (+9.3%) | 478.00 (+19.8%) |
| syscall | openat_ops_per_sec | 522,553 | — | 383,495 (+26.6%) | 383,808 (+26.6%) | — | 192,683 (+63.1%) | — | 194,920 (+62.7%) | 478,865 (+8.4%) | 397,740 (+23.9%) | 472,306 (+9.6%) | 453,331 (+13.2%) | — | — | — | 842,129 (-61.2%) | — | 533,708 (-2.1%) | 286,203 (+45.2%) | 223,041 (+57.3%) |
| syscall | openat_p50_ns | 1,874 | — | 2,565 (+36.9%) | 2,559 (+36.6%) | — | 5,067 (+170.4%) | — | 5,059 (+170.0%) | 2,047 (+9.2%) | 2,458 (+31.2%) | 2,091 (+11.6%) | 2,154 (+14.9%) | — | — | — | 1,157 (-38.3%) | — | 1,833 (-2.2%) | 3,301 (+76.1%) | 4,298 (+129.3%) |
| syscall | openat_p99_ns | 2,022 | — | 2,855 (+41.2%) | 2,853 (+41.1%) | — | 6,226 (+207.9%) | — | 6,236 (+208.4%) | 2,206 (+9.1%) | 2,801 (+38.5%) | 2,238 (+10.7%) | 2,343 (+15.9%) | — | — | — | 1,250 (-38.2%) | — | 1,996 (-1.3%) | 4,450 (+120.1%) | 5,484 (+171.2%) |
| syscall | read_ops_per_sec | 332,075 | — | 325,717 (+1.9%) | 321,823 (+3.1%) | — | 276,200 (+16.8%) | — | 286,300 (+13.8%) | 303,417 (+8.6%) | 255,780 (+23.0%) | 301,285 (+9.3%) | 297,082 (+10.5%) | — | — | — | 567,469 (-70.9%) | — | 255,785 (+23.0%) | 307,575 (+7.4%) | 286,999 (+13.6%) |
| syscall | read_p50_ns | 2,967 | — | 3,038 (+2.4%) | 3,076 (+3.7%) | — | 3,570 (+20.3%) | — | 3,451 (+16.3%) | 3,249 (+9.5%) | 3,842 (+29.5%) | 3,271 (+10.2%) | 3,324 (+12.0%) | — | — | — | 1,723 (-41.9%) | — | 3,862 (+30.2%) | 3,188 (+7.4%) | 3,432 (+15.7%) |
| syscall | read_p99_ns | 3,218 | — | 3,289 (+2.2%) | 3,385 (+5.2%) | — | 3,940 (+22.4%) | — | 3,890 (+20.9%) | 3,532 (+9.8%) | 4,488 (+39.5%) | 3,571 (+11.0%) | 3,610 (+12.2%) | — | — | — | 1,869 (-41.9%) | — | 4,173 (+29.7%) | 3,583 (+11.3%) | 3,848 (+19.6%) |
| syscall | stat_ops_per_sec | 1,320,029 | — | 1,260,526 (+4.5%) | 1,256,127 (+4.8%) | — | 1,221,463 (+7.5%) | — | 1,253,441 (+5.0%) | 1,308,479 (+0.9%) | 1,053,670 (+20.2%) | 1,299,674 (+1.5%) | 1,353,005 (-2.5%) | — | — | — | 2,456,521 (-86.1%) | — | 1,323,244 (-0.2%) | 1,304,303 (+1.2%) | 1,163,769 (+11.8%) |
| syscall | stat_p50_ns | 719.00 | — | 756.00 (+5.1%) | 758.00 (+5.4%) | — | 777.00 (+8.1%) | — | 757.00 (+5.3%) | 727.00 (+1.1%) | 885.00 (+23.1%) | 732.00 (+1.8%) | 694.00 (-3.5%) | — | — | — | 375.00 (-47.8%) | — | 717.00 (-0.3%) | 724.00 (+0.7%) | 817.00 (+13.6%) |
| syscall | stat_p99_ns | 796.00 | — | 827.00 (+3.9%) | 833.00 (+4.6%) | — | 872.00 (+9.5%) | — | 844.00 (+6.0%) | 794.00 (-0.3%) | 1,119 (+40.6%) | 806.00 (+1.3%) | 795.00 (-0.1%) | — | — | — | 410.00 (-48.5%) | — | 794.00 (-0.3%) | 820.00 (+3.0%) | 915.00 (+14.9%) |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | community | — | — | — | — | — | — | — | — | — |
| falco | default | 23.26 | 44.83 | 146.27 | 146.55 | +6.5% | +4.6% | — | — | — |
| falco | tuned | 32.66 | 63.17 | 143.58 | 144.09 | +6.8% | +4.8% | — | — | — |
| kubearmor | community | — | — | — | — | — | — | — | — | — |
| kubearmor | default | 52.83 | 173.92 | 4,880 | 5,479 | +17.3% | +16.8% | — | — | — |
| kubearmor | enforce | — | — | — | — | — | — | — | — | — |
| kubearmor | tuned | 55.41 | 160.20 | 5,834 | 6,478 | +16.1% | +13.8% | — | — | — |
| kunai | community | 21.22 | 41.82 | 89.62 | 90.23 | +9.2% | +8.4% | — | — | — |
| kunai | default | 61.94 | 90.94 | 139.62 | 150.16 | +39.0% | +23.0% | — | — | — |
| kunai | enforce | 21.61 | 49.93 | 92.66 | 92.88 | +10.5% | +9.3% | — | — | — |
| kunai | tuned | 13.07 | 43.46 | 93.90 | 94.12 | +11.2% | +10.5% | — | — | — |
| pulsar | default | — | — | — | — | — | — | — | — | — |
| pulsar | tuned | — | — | — | — | — | — | — | — | — |
| tetragon | community | — | — | — | — | — | — | — | — | — |
| tetragon | default | 7.16 | 52.44 | 617.58 | 916.09 | -38.2% | -61.2% | — | — | — |
| tetragon | enforce | — | — | — | — | — | — | — | — | — |
| tetragon | tuned | 19.68 | 66.10 | 529.54 | 728.74 | +0.0% | -0.0% | — | — | — |
| tracee | default | 109.25 | 186.46 | 157.64 | 165.11 | +9.2% | +8.4% | — | — | — |
| tracee | tuned | 123.98 | 172.71 | 168.65 | 181.63 | +18.2% | +15.1% | — | — | — |

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
| falco | community | 5 | 5 | — | 0.00 | 0.00 | — | — | — |
| falco | default | 5 | 5 | 0.011s | 8.72 | 11.99 | 0.25 | 92.1% | 100.0% |
| falco | tuned | 5 | 5 | 0.006s | 47.55 | 57.27 | 1.14 | 88.9% | 97.2% |
| kubearmor | community | 3 | 4 | — | 0.00 | 0.00 | — | — | — |
| kubearmor | default | 3 | 4 | 2.970s | 0.00 | 47.85 | 0.10 | — | — |
| kubearmor | enforce | 3 | 4 | — | 0.00 | 0.00 | — | — | — |
| kubearmor | tuned | 3 | 4 | 2.931s | 0.00 | 49.36 | 0.10 | — | — |
| kunai | community | 3 | 4 | 0.005s | 102.98 | 15,089 | 31.97 | 13.3% | 100.0% |
| kunai | default | 3 | 4 | 0.005s | 0.00 | 691,581 | 15,360 | — | — |
| kunai | enforce | 3 | 4 | 0.506s | 31.19 | 14,730 | 30.06 | 78.8% | 100.0% |
| kunai | tuned | 3 | 4 | 0.016s | 30.99 | 14,666 | 29.74 | 79.2% | 100.0% |
| pulsar | default | 4 | 4 | 0.004s | 0.00 | 1,521,072 | 37.13 | — | — |
| pulsar | tuned | 4 | 4 | — | — | — | — | — | — |
| tetragon | community | 5 | 4 | — | 0.00 | 0.00 | — | — | — |
| tetragon | default | 5 | 4 | 5.479s | 716.65 | 18,198 | 689.11 | 42.8% | 47.5% |
| tetragon | enforce | 5 | 4 | — | 0.00 | 0.00 | — | — | — |
| tetragon | tuned | 5 | 4 | 0.051s | 890.28 | 15,312 | 585.48 | 42.2% | 55.3% |
| tracee | default | 4 | 4 | 2.961s | 3.66 | 14.42 | 0.15 | 100.0% | 100.0% |
| tracee | tuned | 4 | 4 | 3.182s | 32.82 | 43.19 | 0.83 | 100.0% | 100.0% |

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
| kunai | community | t1548-001-setuid-binary | run.tmpfs |
| kunai | community | t1036-005-masquerading | run.tmpfs |
| kunai | community | t1620-fileless-exec | run.memfd |
| kunai | community | t1105-ingress-tool-transfer | run.tmpfs |
| kunai | community | t1496-cryptominer | run.tmpfs |
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
| kunai | enforce | t1046-network-scan | discovery.network.port_scan |
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
| kunai | tuned | t1046-network-scan | discovery.network.port_scan |
| kunai | tuned | t1082-system-discovery | discovery.system.information |
| kunai | tuned | t1613-container-discovery | discovery.container.environment |
| kunai | tuned | t1105-ingress-tool-transfer | chmod.exec.in.tmpfs, discovery.system.information, download.to.tmpfs, exec.from.tmpfs |
| kunai | tuned | t1048-exfiltration-http | credential_access.credential_files.cmdline,credential_access.shadow.cmdline, credential_access.shadow.read, download.to.tmpfs,exfiltration.http.upload |
| kunai | tuned | t1485-data-destruction | impact.data_destruction |
| kunai | tuned | t1496-cryptominer | exec.from.tmpfs,impact.cryptominer.process, impact.cryptominer.connection |
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
| tetragon | tuned | t1046-network-scan | netcat-outbound-connect |
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
| falco | partial | community: ToolStartError: falco: no Helm values for profile 'community' no agent pod ebpf-bench-falco app.kubernetes.io/name=falco,app.kubernetes.io/instance=falco on node ebpf-bench-control-plane full diagnostics in container.log |
| kubearmor | partial | enforce: ToolStartError: kubearmor: no Helm values for profile 'enforce' no agent pod ebpf-bench-kubearmor kubearmor-app=kubearmor on node ebpf-bench-control-plane events: [event Pod/kubearmor-controller-7bb6b748cb-bltk2] Warning Failed x71: Error: container has runAsNonRoot and image will run as root (pod: "kubearmor-controller-7bb6b748cb-bltk2_ebpf-bench-kubearmor(e3da7630-b1fd-407d-954d-07dc61fa4abb)", container: manager) [event Pod/kubearmor-controller-7bb6b748cb-l6g2j] Warning Failed x73: Error: container has runAsNonRoot and image will run as root (pod: "kubearmor-controller-7bb6b748cb-l6g2j_ebpf-bench-kubearmor(c7f49e86-0bc0-402a-9ee8-dd0611bddd3e)", container: manager) full diagnostics in container.log; community: ToolStartError: kubearmor: no Helm values for profile 'community' no agent pod ebpf-bench-kubearmor kubearmor-app=kubearmor on node ebpf-bench-control-plane events: [event Pod/kubearmor-controller-7bb6b748cb-bltk2] Warning Failed x71: Error: container has runAsNonRoot and image will run as root (pod: "kubearmor-controller-7bb6b748cb-bltk2_ebpf-bench-kubearmor(e3da7630-b1fd-407d-954d-07dc61fa4abb)", container: manager) [event Pod/kubearmor-controller-7bb6b748cb-l6g2j] Warning Failed x73: Error: container has runAsNonRoot and image will run as root (pod: "kubearmor-controller-7bb6b748cb-l6g2j_ebpf-bench-kubearmor(c7f49e86-0bc0-402a-9ee8-dd0611bddd3e)", container: manager) full diagnostics in container.log |
| pulsar | partial | — |
| tetragon | partial | enforce: ToolStartError: tetragon: no Helm values for profile 'enforce' no agent pod ebpf-bench-tetragon app.kubernetes.io/name=tetragon,app.kubernetes.io/instance=tetragon on node ebpf-bench-control-plane full diagnostics in container.log; community: ToolStartError: tetragon: no Helm values for profile 'community' no agent pod ebpf-bench-tetragon app.kubernetes.io/name=tetragon,app.kubernetes.io/instance=tetragon on node ebpf-bench-control-plane full diagnostics in container.log |

### Log overflow

Deployments whose log or alerts stream exceeded `max_log_lines` / `max_log_bytes`: lines after the cap were dropped, so alerts emitted after it are missing and detection results are a lower bound.

| Tool | Profile | Dropped log lines | Dropped alerts file lines | Dropped MiB |
| --- | --- | --- | --- | --- |
| kunai | default | 3864241 | 0 | 4,973 |

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
| kubearmor | default | t1046-network-scan | 0 | 1 |
| kubearmor | default | t1046-network-scan | 1 | 1 |
| kubearmor | default | t1046-network-scan | 2 | 1 |
| kubearmor | default | t1046-network-scan | 3 | 1 |
| kubearmor | default | t1046-network-scan | 4 | 1 |
| kubearmor | tuned | t1046-network-scan | 0 | 1 |
| kubearmor | tuned | t1046-network-scan | 1 | 1 |
| kubearmor | tuned | t1046-network-scan | 2 | 1 |
| kubearmor | tuned | t1046-network-scan | 3 | 1 |
| kubearmor | tuned | t1046-network-scan | 4 | 1 |
| kunai | community | t1046-network-scan | 0 | 1 |
| kunai | community | t1046-network-scan | 1 | 1 |
| kunai | community | t1046-network-scan | 2 | 1 |
| kunai | community | t1046-network-scan | 3 | 1 |
| kunai | community | t1046-network-scan | 4 | 1 |
| kunai | default | t1046-network-scan | 0 | 1 |
| kunai | default | t1046-network-scan | 1 | 1 |
| kunai | default | t1046-network-scan | 2 | 1 |
| kunai | default | t1046-network-scan | 3 | 1 |
| kunai | default | t1046-network-scan | 4 | 1 |
| kunai | enforce | t1046-network-scan | 0 | 1 |
| kunai | enforce | t1046-network-scan | 1 | 1 |
| kunai | enforce | t1046-network-scan | 2 | 1 |
| kunai | enforce | t1046-network-scan | 3 | 1 |
| kunai | enforce | t1046-network-scan | 4 | 1 |
| kunai | tuned | t1046-network-scan | 0 | 1 |
| kunai | tuned | t1046-network-scan | 1 | 1 |
| kunai | tuned | t1046-network-scan | 2 | 1 |
| kunai | tuned | t1046-network-scan | 3 | 1 |
| kunai | tuned | t1046-network-scan | 4 | 1 |
| tetragon | default | t1046-network-scan | 0 | 1 |
| tetragon | default | t1046-network-scan | 1 | 1 |
| tetragon | default | t1046-network-scan | 2 | 1 |
| tetragon | default | t1046-network-scan | 3 | 1 |
| tetragon | default | t1046-network-scan | 4 | 1 |
| tetragon | tuned | t1046-network-scan | 0 | 1 |
| tetragon | tuned | t1046-network-scan | 1 | 1 |
| tetragon | tuned | t1046-network-scan | 2 | 1 |
| tetragon | tuned | t1046-network-scan | 3 | 1 |
| tetragon | tuned | t1046-network-scan | 4 | 1 |
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
