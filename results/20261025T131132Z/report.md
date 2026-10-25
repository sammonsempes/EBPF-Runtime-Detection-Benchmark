# eBPF runtime detection benchmark: 20261025T131132Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261025T131132Z |
| grace_seconds | 10 |
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
| config.max_log_bytes | 16106127360 |
| config.max_log_lines | 15000000 |
| config.overhead | {"duration_seconds": 30, "enabled": true, "repetitions": 3, "workloads": ["syscall", "exec", "fileio"]} |
| config.profiles | ["default", "tuned", "enforce", "community"] |
| config.repetitions | 5 |
| config.results_dir | results |
| config.scenarios | all |
| config.tools | ["kubearmor", "kunai", "pulsar"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| kubearmor | 1.7.5 | ok | community, default, enforce, tuned | community: cf1c6c0ff99c, default: 15ef430d85e9, enforce: b81f0ff463d7, tuned: 12cfa057de2f |
| kunai | 0.6.2 | ok | community, default, enforce, tuned | community: a8d2102db595, default: ea10f4f706e7, enforce: df81b47e0a5b, tuned: 3c0a05fb5002 |
| pulsar | 0.10.1 | ok | default, tuned | community: None, default: 9cb2665a655e, enforce: None, tuned: dd1914d53753 |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kunai | tuned | 100.0% | 100.0% | 33.3% | 0.078s | 0 | 6.31 | 92.19 | +14.1% |
| kunai | enforce | 100.0% | 100.0% | 33.3% | 0.085s | 0 | 6.16 | 93.97 | +16.9% |
| kubearmor | default | 91.7% | 91.7% | 100.0% | 0.087s | 0 | 21.07 | 371.64 | +63.9% |
| kubearmor | community | 91.7% | 91.7% | 100.0% | 0.097s | 0 | 23.89 | 296.27 | +67.9% |
| kubearmor | tuned | 87.5% | 87.5% | 3.3% | 0.107s | 0 | 24.27 | 310.34 | +58.2% |
| pulsar | tuned | 62.5% | 62.5% | 33.3% | 0.001s | 0 | 291.07 | 4,571 | +36.2% |
| kubearmor | enforce | 58.3% | 58.3% | 16.7% | 0.114s | 0 | 24.67 | 320.15 | +53.9% |
| kunai | community | 20.8% | 20.8% | 6.7% | 0.089s | 0 | 5.00 | 91.16 | +9.5% |
| pulsar | default | 16.7% | 16.7% | 16.7% | 0.000s | 0 | 266.73 | 5,370 | +27.2% |
| kunai | default | 0.0% | 0.0% | 0.0% | — | 0 | 6.57 | 93.03 | +13.5% |

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

| Tactic | Scenario | Technique | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| execution | t1059-006-python-exec | T1059.006 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1053-003-cron-persistence | T1053.003 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| persistence | t1136-001-create-account | T1136.001 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1543-002-systemd-service | T1543.002 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| persistence | t1547-006-kernel-module | T1547.006 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| privilege-escalation | t1611-escape-to-host | T1611 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| defense-evasion | t1036-005-masquerading | T1036.005 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| defense-evasion | t1070-002-clear-logs | T1070.002 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| defense-evasion | t1070-003-clear-history | T1070.003 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 |
| defense-evasion | t1222-002-permission-modification | T1222.002 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ❌ 0/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| defense-evasion | t1620-fileless-exec | T1620 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| credential-access | t1003-008-shadow-read | T1003.008 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| credential-access | t1552-001-credentials-in-files | T1552.001 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| credential-access | t1552-007-container-api | T1552.007 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| discovery | t1046-network-scan | T1046 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| discovery | t1082-system-discovery | T1082 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| discovery | t1613-container-discovery | T1613 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 |
| command-and-control | t1105-ingress-tool-transfer | T1105 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| exfiltration | t1048-exfiltration-http | T1048 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1485-data-destruction | T1485 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |
| impact | t1496-cryptominer | T1496 | ✅ 5/5 | ✅ 5/5 | 🛡️ 5/5 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | 🛡️ 5/5 | ✅ 5/5 | ❌ 0/5 | ✅ 5/5 |

### Coverage per tactic

| Tactic | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | 0/2 | 2/2 | 2/2 | 0/2 | 1/2 |
| persistence | 4/5 | 4/5 | 1/5 | 4/5 | 0/5 | 0/5 | 5/5 | 5/5 | 2/5 | 4/5 |
| privilege-escalation | 1/2 | 1/2 | 1/2 | 1/2 | 1/2 | 0/2 | 2/2 | 2/2 | 0/2 | 1/2 |
| defense-evasion | 5/5 | 5/5 | 4/5 | 4/5 | 2/5 | 0/5 | 5/5 | 5/5 | 2/5 | 4/5 |
| credential-access | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 0/3 | 3/3 | 3/3 | 0/3 | 1/3 |
| discovery | 3/3 | 3/3 | 2/3 | 3/3 | 0/3 | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| command-and-control | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| exfiltration | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| impact | 2/2 | 2/2 | 0/2 | 2/2 | 1/2 | 0/2 | 2/2 | 2/2 | 0/2 | 2/2 |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benign-admin-commands | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 5/5 | ⚠️ 1/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 |
| benign-backup | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-compile | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 2/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 |
| benign-log-rotation | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 |
| benign-package-query | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 |
| benign-web-server | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ✅ 0/5 | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | ✅ 0/5 |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| kubearmor | community | benign-admin-commands | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-discovery-process-discovery, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-backup | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-compile | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-log-rotation | harden-shell-history-mod, ksp-check-log-clearing, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-package-query | harden-pkg-mngr-exec, harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-web-server | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | default | benign-admin-commands | harden-shell-history-mod |
| kubearmor | default | benign-backup | harden-shell-history-mod |
| kubearmor | default | benign-compile | harden-shell-history-mod |
| kubearmor | default | benign-log-rotation | harden-shell-history-mod |
| kubearmor | default | benign-package-query | harden-pkg-mngr-exec, harden-shell-history-mod |
| kubearmor | default | benign-web-server | harden-shell-history-mod |
| kubearmor | enforce | benign-admin-commands | tuned-container-discovery, tuned-container-escape |
| kubearmor | tuned | benign-admin-commands | tuned-container-escape |
| kunai | community | benign-compile | exe.error |
| kunai | enforce | benign-admin-commands | discovery.system.information |
| kunai | enforce | benign-web-server | download.to.tmpfs |
| kunai | tuned | benign-admin-commands | discovery.system.information |
| kunai | tuned | benign-web-server | download.to.tmpfs |
| pulsar | default | benign-compile | Create files below /root |
| pulsar | tuned | benign-compile | Create files below /root |
| pulsar | tuned | benign-log-rotation | Executable bit set on file |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t1059-004-reverse-shell | 0.069s / 0.135s | 0.169s / 0.181s | 0.054s / 0.075s | 0.108s / 0.181s | — | — | 0.089s / 0.113s | 0.060s / 0.118s | — | — |
| t1059-006-python-exec | 0.140s / 0.184s | 0.173s / 0.192s | 0.109s / 0.116s | 0.056s / 0.162s | — | — | 0.088s / 0.132s | 0.085s / 0.102s | — | 0.000s / 0.001s |
| t1053-003-cron-persistence | 0.100s / 0.189s | 0.112s / 0.150s | 0.171s / 0.190s | 0.125s / 0.187s | — | — | 0.099s / 0.129s | 0.044s / 0.055s | 0.000s / 0.000s | 0.000s / 0.000s |
| t1098-004-ssh-authorized-keys | 0.086s / 0.103s | 0.058s / 0.124s | — | 0.099s / 0.149s | — | — | 0.097s / 0.114s | 0.065s / 0.110s | — | — |
| t1136-001-create-account | 0.111s / 0.154s | 0.107s / 0.109s | — | 0.102s / 0.151s | — | — | 0.087s / 0.123s | 0.100s / 0.120s | — | 0.000s / 0.001s |
| t1543-002-systemd-service | 0.127s / 0.171s | 0.106s / 0.166s | — | 0.138s / 0.192s | — | — | 0.104s / 0.117s | 0.044s / 0.098s | — | 0.000s / 0.000s |
| t1547-006-kernel-module | — | — | — | — | — | — | 0.049s / 0.128s | 0.087s / 0.107s | 0.001s / 0.001s | 0.000s / 0.001s |
| t1548-001-setuid-binary | 0.091s / 0.141s | 0.061s / 0.095s | 0.100s / 0.194s | 0.107s / 0.141s | 0.106s / 0.127s | — | 0.107s / 0.126s | 0.077s / 0.124s | — | 0.001s / 0.001s |
| t1611-escape-to-host | — | — | — | — | — | — | 0.084s / 0.129s | 0.089s / 0.107s | — | — |
| t1036-005-masquerading | 0.064s / 0.168s | 0.035s / 0.144s | 0.078s / 0.087s | 0.037s / 0.192s | 0.049s / 0.114s | — | 0.040s / 0.130s | 0.103s / 0.117s | — | 0.002s / 0.002s |
| t1070-002-clear-logs | 0.077s / 0.138s | 0.028s / 0.178s | 0.121s / 0.132s | 0.080s / 0.158s | — | — | 0.063s / 0.110s | 0.047s / 0.064s | -0.013s / -0.013s | -0.014s / -0.013s |
| t1070-003-clear-history | 0.091s / 0.178s | 0.008s / 0.052s | 0.145s / 0.172s | 0.095s / 0.164s | — | — | 0.087s / 0.125s | 0.067s / 0.133s | 0.087s / 0.100s | 0.088s / 0.098s |
| t1222-002-permission-modification | 0.044s / 0.096s | 0.055s / 0.142s | — | — | — | — | 0.065s / 0.084s | 0.108s / 0.116s | — | — |
| t1620-fileless-exec | 0.138s / 0.159s | 0.142s / 0.175s | 0.139s / 0.192s | 0.113s / 0.164s | 0.076s / 0.105s | — | 0.076s / 0.122s | 0.109s / 0.138s | — | 0.009s / 0.009s |
| t1003-008-shadow-read | 0.158s / 0.179s | 0.147s / 0.176s | 0.045s / 0.172s | 0.154s / 0.185s | — | — | 0.103s / 0.107s | 0.081s / 0.115s | — | — |
| t1552-001-credentials-in-files | 0.127s / 0.167s | 0.128s / 0.141s | 0.074s / 0.128s | 0.146s / 0.176s | — | — | 0.080s / 0.102s | 0.088s / 0.102s | — | — |
| t1552-007-container-api | 0.159s / 0.162s | 0.183s / 0.192s | 0.105s / 0.184s | 0.149s / 0.171s | — | — | 0.067s / 0.088s | 0.073s / 0.100s | — | 0.003s / 0.003s |
| t1046-network-scan | 0.079s / 0.141s | 0.063s / 0.119s | 0.139s / 0.147s | 0.059s / 0.105s | — | — | 0.068s / 0.119s | 0.071s / 0.093s | — | — |
| t1082-system-discovery | 0.057s / 0.169s | 0.055s / 0.101s | — | 0.094s / 0.128s | — | — | 0.105s / 0.139s | 0.051s / 0.074s | — | — |
| t1613-container-discovery | 0.097s / 0.174s | 0.099s / 0.111s | 0.140s / 0.190s | 0.096s / 0.156s | — | — | 0.060s / 0.111s | 0.039s / 0.101s | — | — |
| t1105-ingress-tool-transfer | 0.096s / 0.139s | 0.073s / 0.101s | — | 0.108s / 0.144s | 0.072s / 0.118s | — | 0.064s / 0.118s | 0.111s / 0.115s | — | 0.007s / 0.009s |
| t1048-exfiltration-http | 0.077s / 0.174s | 0.093s / 0.166s | 0.158s / 0.168s | 0.097s / 0.174s | — | — | 0.095s / 0.115s | 0.071s / 0.337s | — | 0.003s / 0.003s |
| t1485-data-destruction | 0.102s / 0.135s | 0.075s / 0.121s | — | 0.108s / 0.180s | — | — | 0.057s / 0.097s | 0.108s / 0.131s | — | 0.000s / 0.001s |
| t1496-cryptominer | 0.087s / 0.161s | 0.071s / 0.136s | — | 0.130s / 0.189s | 0.128s / 0.175s | — | 0.140s / 0.159s | 0.085s / 0.141s | — | 0.000s / 0.001s |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| kubearmor | community | 100.0% | 3 |
| kubearmor | default | 100.0% | 3 |
| kubearmor | enforce | 100.0% | 0 |
| kubearmor | tuned | 100.0% | 0 |
| kunai | community | 100.0% | 0 |
| kunai | default | 100.0% | 0 |
| kunai | enforce | 100.0% | 0 |
| kunai | tuned | 100.0% | 0 |
| pulsar | default | 100.0% | 5 |
| pulsar | tuned | 100.0% | 5 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kubearmor | 91.7% (22/24) | 10 | 50 | 0 (0.0%) | 0.105s | 180 | yes | bpf-lsm, apparmor, selinux-host-only, presets | yes |
| kunai | 12.5% (3/24) | 105 | 0 | 0 (0.0%) | 0.086s | 310 | yes | kill | no |
| pulsar | detection only | — | — | — | — | — | — | — | — |

### Prevented without alert

| Tool | Scenarios |
| --- | --- |
| kubearmor | t1082-system-discovery, t1098-004-ssh-authorized-keys, t1105-ingress-tool-transfer, t1136-001-create-account, t1222-002-permission-modification, t1485-data-destruction, t1496-cryptominer, t1543-002-systemd-service, t1547-006-kernel-module, t1611-escape-to-host |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | kubearmor/community | kubearmor/default | kubearmor/enforce | kubearmor/tuned | kunai/community | kunai/default | kunai/enforce | kunai/tuned | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exec | execs_per_sec | 2,202 | 2,169 (+1.5%) | 2,180 (+1.0%) | 2,168 (+1.6%) | 2,187 (+0.7%) | 2,063 (+6.3%) | 2,226 (-1.1%) | 2,075 (+5.8%) | 2,098 (+4.8%) | 2,056 (+6.6%) | 1,920 (+12.8%) |
| exec | p50_us | 465.88 | 458.00 (-1.7%) | 453.41 (-2.7%) | 457.71 (-1.8%) | 454.36 (-2.5%) | 494.72 (+6.2%) | 414.90 (-10.9%) | 495.77 (+6.4%) | 488.29 (+4.8%) | 467.12 (+0.3%) | 507.73 (+9.0%) |
| exec | p99_us | 861.34 | 802.13 (-6.9%) | 803.45 (-6.7%) | 811.93 (-5.7%) | 799.40 (-7.2%) | 1,008 (+17.0%) | 935.02 (+8.6%) | 1,022 (+18.6%) | 995.42 (+15.6%) | 871.40 (+1.2%) | 958.44 (+11.3%) |
| fileio | ops_per_sec | 1,436 | 1,432 (+0.3%) | 1,432 (+0.3%) | 1,432 (+0.3%) | 1,432 (+0.3%) | 1,440 (-0.2%) | 1,414 (+1.6%) | 1,431 (+0.4%) | 1,436 (+0.0%) | 1,448 (-0.8%) | 1,449 (-0.8%) |
| fileio | p50_us | 686.13 | 685.05 (-0.2%) | 685.65 (-0.1%) | 685.18 (-0.1%) | 685.30 (-0.1%) | 684.20 (-0.3%) | 692.61 (+0.9%) | 690.45 (+0.6%) | 688.84 (+0.4%) | 681.22 (-0.7%) | 681.67 (-0.6%) |
| fileio | p99_us | 789.53 | 840.20 (+6.4%) | 835.98 (+5.9%) | 850.19 (+7.7%) | 838.06 (+6.1%) | 797.43 (+1.0%) | 949.48 (+20.3%) | 810.98 (+2.7%) | 807.69 (+2.3%) | 785.26 (-0.5%) | 780.58 (-1.1%) |
| syscall | connect_ops_per_sec | 99,141 | 52,980 (+46.6%) | 53,291 (+46.2%) | 59,799 (+39.7%) | 52,968 (+46.6%) | 78,213 (+21.1%) | 91,240 (+8.0%) | 78,052 (+21.3%) | 76,628 (+22.7%) | 48,141 (+51.4%) | 48,117 (+51.5%) |
| syscall | connect_p50_ns | 5,255 | 9,378 (+78.5%) | 9,391 (+78.7%) | 8,245 (+56.9%) | 9,134 (+73.8%) | 7,323 (+39.4%) | 6,229 (+18.5%) | 7,376 (+40.4%) | 7,458 (+41.9%) | 11,632 (+121.4%) | 11,604 (+120.8%) |
| syscall | connect_p99_ns | 6,414 | 11,370 (+77.3%) | 10,989 (+71.3%) | 10,005 (+56.0%) | 13,727 (+114.0%) | 9,485 (+47.9%) | 8,454 (+31.8%) | 10,649 (+66.0%) | 10,925 (+70.3%) | 15,732 (+145.3%) | 15,988 (+149.3%) |
| syscall | getpid_ops_per_sec | 7,682,547 | 6,825,485 (+11.2%) | 7,089,583 (+7.7%) | 7,081,191 (+7.8%) | 7,129,078 (+7.2%) | 7,250,464 (+5.6%) | 7,026,235 (+8.5%) | 7,046,583 (+8.3%) | 7,075,304 (+7.9%) | 7,705,137 (-0.3%) | 7,154,207 (+6.9%) |
| syscall | getpid_p50_ns | 98.00 | 113.00 (+15.3%) | 110.00 (+12.2%) | 110.00 (+12.2%) | 109.00 (+11.2%) | 106.00 (+8.2%) | 111.00 (+13.3%) | 110.00 (+12.2%) | 110.00 (+12.2%) | 98.00 (+0.0%) | 106.00 (+8.2%) |
| syscall | getpid_p99_ns | 107.00 | 124.00 (+15.9%) | 118.00 (+10.3%) | 118.00 (+10.3%) | 118.00 (+10.3%) | 115.00 (+7.5%) | 120.00 (+12.1%) | 120.00 (+12.1%) | 121.00 (+13.1%) | 108.00 (+0.9%) | 116.00 (+8.4%) |
| syscall | openat_ops_per_sec | 776,346 | 261,133 (+66.4%) | 249,748 (+67.8%) | 254,650 (+67.2%) | 263,134 (+66.1%) | 710,007 (+8.5%) | 685,866 (+11.7%) | 672,416 (+13.4%) | 682,798 (+12.0%) | 349,119 (+55.0%) | 350,524 (+54.8%) |
| syscall | openat_p50_ns | 1,252 | 3,795 (+203.1%) | 3,815 (+204.7%) | 3,796 (+203.2%) | 3,724 (+197.4%) | 1,381 (+10.3%) | 1,424 (+13.7%) | 1,454 (+16.1%) | 1,434 (+14.5%) | 2,749 (+119.6%) | 2,741 (+118.9%) |
| syscall | openat_p99_ns | 1,362 | 4,744 (+248.3%) | 5,005 (+267.5%) | 5,067 (+272.0%) | 4,860 (+256.8%) | 1,480 (+8.7%) | 1,537 (+12.8%) | 1,602 (+17.6%) | 1,548 (+13.7%) | 4,262 (+212.9%) | 4,146 (+204.4%) |
| syscall | read_ops_per_sec | 5,633,715 | 3,556,466 (+36.9%) | 3,703,393 (+34.3%) | 3,779,895 (+32.9%) | 3,770,735 (+33.1%) | 2,734,883 (+51.5%) | 2,747,525 (+51.2%) | 2,614,339 (+53.6%) | 2,730,170 (+51.5%) | 4,851,555 (+13.9%) | 4,734,293 (+16.0%) |
| syscall | read_p50_ns | 145.00 | 237.00 (+63.4%) | 227.00 (+56.6%) | 220.00 (+51.7%) | 219.00 (+51.0%) | 332.00 (+129.0%) | 328.00 (+126.2%) | 348.00 (+140.0%) | 332.00 (+129.0%) | 169.00 (+16.6%) | 171.00 (+17.9%) |
| syscall | read_p99_ns | 156.00 | 269.00 (+72.4%) | 277.00 (+77.6%) | 265.00 (+69.9%) | 258.00 (+65.4%) | 366.00 (+134.6%) | 369.00 (+136.5%) | 381.00 (+144.2%) | 368.00 (+135.9%) | 187.00 (+19.9%) | 198.00 (+26.9%) |
| syscall | stat_ops_per_sec | 2,249,288 | 2,101,275 (+6.6%) | 2,218,508 (+1.4%) | 2,257,696 (-0.4%) | 2,219,375 (+1.3%) | 2,261,313 (-0.5%) | 2,225,958 (+1.0%) | 2,244,971 (+0.2%) | 2,285,117 (-1.6%) | 1,912,474 (+15.0%) | 1,736,172 (+22.8%) |
| syscall | stat_p50_ns | 409.00 | 438.00 (+7.1%) | 417.00 (+2.0%) | 411.00 (+0.5%) | 414.00 (+1.2%) | 407.00 (-0.5%) | 415.00 (+1.5%) | 412.00 (+0.7%) | 404.00 (-1.2%) | 478.00 (+16.9%) | 539.00 (+31.8%) |
| syscall | stat_p99_ns | 444.00 | 505.00 (+13.7%) | 453.00 (+2.0%) | 449.00 (+1.1%) | 450.00 (+1.4%) | 441.00 (-0.7%) | 453.00 (+2.0%) | 444.00 (+0.0%) | 438.00 (-1.4%) | 597.00 (+34.5%) | 624.00 (+40.5%) |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kubearmor | community | 23.89 | 421.08 | 296.27 | 371.49 | +15.6% | +11.2% | 38.63 | 93.84 | +0.3 pp |
| kubearmor | default | 21.07 | 415.88 | 371.64 | 482.71 | +11.3% | +7.7% | 38.44 | 94.54 | +0.1 pp |
| kubearmor | enforce | 24.67 | 414.67 | 320.15 | 374.20 | +11.3% | +7.8% | 38.89 | 93.91 | +0.5 pp |
| kubearmor | tuned | 24.27 | 406.10 | 310.34 | 348.09 | +10.8% | +7.2% | 38.54 | 93.76 | +0.2 pp |
| kunai | community | 5.00 | 69.20 | 91.16 | 91.65 | +8.4% | +6.3% | 38.34 | 52.65 | -0.0 pp |
| kunai | default | 6.57 | 91.05 | 93.03 | 93.50 | +13.1% | +8.0% | 38.48 | 77.23 | +0.1 pp |
| kunai | enforce | 6.16 | 63.29 | 93.97 | 94.47 | +14.2% | +8.3% | 38.20 | 47.06 | -0.2 pp |
| kunai | tuned | 6.31 | 82.82 | 92.19 | 101.02 | +13.4% | +7.9% | 38.32 | 50.06 | -0.1 pp |
| pulsar | default | 266.73 | 382.18 | 5,370 | 5,650 | +16.7% | +13.9% | 73.67 | 91.90 | +35.3 pp |
| pulsar | tuned | 291.07 | 372.73 | 4,571 | 4,889 | +22.4% | +16.0% | 83.20 | 91.14 | +44.8 pp |

Host CPU is sampled from /proc/stat every second during workloads (Docker backend only); baseline median 38.38%, max 43.29%. The delta is in percentage points of the whole host.

## Operational aspects

Scores follow the rubric in docs/methodology.md (1 worst, 5 best).

| Tool | Version | License | Deployment | Rule customization | Output quality | Deploy steps | Rule language | Custom rules | Hot reload | Output formats | Enrichment | ATT&CK mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kubearmor | 1.7.5 | Apache-2.0 | 3 | 4 | 4 | 2 | declarative KubeArmorPolicy YAML (process, file, network, capabilities, syscalls and presets rules with matchPaths, matchDirectories, matchPatterns, fromSource, Allow/Audit/Block actions) | yes | yes | json | container, kubernetes | no | deployment 3: outside Kubernetes the daemon must be started with k8s=false and policy flags (deployments/podman/docker-compose.yaml, KubeArmor/packaging/kubearmor.yaml), upstream pairs it with the kubearmor-init container that compiles the eBPF objects against the host kernel (Dockerfile.init, build/compile.sh), it needs the container runtime socket, bpffs, securityfs and debugfs, and policies can only be fed through the gRPC PolicyService (karmor vm policy add) or the JSON backup directory /opt/kubearmor/policies read at startup (core/unorchestratedUpdates.go restoreKubeArmorPolicies). Helm and the operator make the Kubernetes path simpler. rule_customization 4: policies are declarative and applied live (CRD watchers in Kubernetes, gRPC PolicyService outside), but expressiveness is limited to paths, directories, glob patterns, source binaries and protocols; arguments can only be matched for Allow lists (matchArgs) and there is no correlation; Audit rules need visibility enabled (getting-started/kubearmor_visibility.md). output_quality 4: JSON per event (types/types.go Log struct) with container id/name/image, pod, namespace, labels, host and container pids, parent process name, source command line, policy name, severity, tags, message, action and result; ATT&CK mapping only exists when the policy author puts MITRE tags in the policy (hardening templates do), there is no built-in technique field and no ancestry beyond the parent. |
| kunai | 0.6.2 | GPL-3.0 | 3 | 4 | 4 | 3 | Gene YAML rules (match-on event names, $variables matching event fields with ==, ~= regex, &= flags and numeric comparisons, boolean condition, severity, ATT&CK ids), plus JSON-lines IoCs and YARA for file scans | yes | no | json | process_ancestry, container, file_hashes, user, dns | yes | Deployment 3: upstream ships a distribution-agnostic static binary (assets kunai-amd64 / kunai-aarch64 with .asc signatures and sha512.txt on the v0.6.2 release) and no container image or Kubernetes manifest; the README recommends the binary, the docs install it as a systemd service with `kunai install`. Running it in a container needs host preparation: privileged mode, host PID namespace, BTF and the bpf/debug filesystems. Steps 3 = download, chmod +x, `kunai run -r <rules>`; upstream ships no detection rule, so with the bare `sudo kunai` quickstart every event is printed and nothing is an alert. Rule customization 4: rules are declarative YAML (Gene engine) with detection, filter and dependency types, regex and flag operators, severity and actions (kill, scan-files), loaded from the config `scanner.rules` or `-r`; there is no runtime reload in 0.6.2, a restart is required (hardened mode even requires a reboot). Output quality 4: one JSON object per line (`data`, `detection`, `filter`, `info`) with process ancestors, parent command line, executable hashes, task/parent uid/gid, mount namespace and container name/type; `detection` carries rule names, tags, severity and ATT&CK ids from rule metadata. Not 5 because container context is only the UTS hostname plus a heuristic type (no container id, image or Kubernetes metadata), and the container `type` is often null for processes started after kunai. |
| pulsar | 0.10.1 | Apache-2.0 AND GPL-2.0 | 4 | 4 | 4 | 2 | YAML rule files (name, type, category, severity, description, condition) with a typed condition DSL over event header and payload (==, !=, <, >, STARTS_WITH, ENDS_WITH, CONTAINS, IN, AND/OR/NOT, is_some()) | yes | yes | json, plaintext, syslog | container, image, user | no | Deployment 4: upstream publishes release binaries (pulsard-<arch>[-static], pulsar-<arch>[-static], pulsar-install.sh) and the release workflow pushes ghcr.io/exein-io/pulsar:<tag> built from .github/docker/Dockerfile with the default config and rules baked in; the quickstart is 2 commands (install script, `pulsard`), and the image only needs the usual eBPF privileges and mounts plus /var/lib/docker for container enrichment. No Helm chart or manifest upstream. Rule customization 4: 47 default YAML rule files in rules/ (Elastic detection-rules based) loaded recursively from /var/lib/pulsar/rules; the DSL is declarative and typed but has no regex, no process ancestry and only per-event fields. hot_reload is true because the rules-engine on_config_change hook rebuilds the engine from disk when its configuration is changed at runtime through `pulsar config` / the engine API (no file watcher); this was removed after 0.10.1. Output quality 4: threat-logger prints threat events as JSON (`output_format=json`) with header (image, pid, parent_pid, uid, gid, container id/name/image/image_digest/layers, threat source/description/extra) and the typed payload; the rule name is threat.description and extra holds category, severity, description and condition. No ATT&CK ids (only a category), no ancestry beyond parent_pid, timestamps are serialized as secs/nanos since epoch. |

### Measured operational metrics

Measured per deployment: time from container start to readiness, alert and log volume over the deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and share of alerts carrying a container id or name. Rubric scores repeated for comparison.

| Tool | Profile | Deployment score | Output quality score | Time to ready | Alerts / min | Log lines / min | Log volume MiB | Attributed alerts | Alerts with container identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kubearmor | community | 3 | 4 | 2.619s | 713.91 | 471,218 | 5,084 | 100.0% | 100.0% |
| kubearmor | default | 3 | 4 | 2.589s | 31.18 | 581,036 | 6,362 | 100.0% | 100.0% |
| kubearmor | enforce | 3 | 4 | 2.639s | 16.08 | 456,216 | 4,716 | 100.0% | 100.0% |
| kubearmor | tuned | 3 | 4 | 2.680s | 34.80 | 431,738 | 4,628 | 100.0% | 100.0% |
| kunai | community | 3 | 4 | 0.919s | 59.80 | 82.69 | 1.39 | 30.0% | 100.0% |
| kunai | default | 3 | 4 | 0.882s | 0.00 | 150,205 | 2,252 | — | — |
| kunai | enforce | 3 | 4 | 0.847s | 38.30 | 97.08 | 0.85 | 87.8% | 100.0% |
| kunai | tuned | 3 | 4 | 0.862s | 79.07 | 97.98 | 1.76 | 41.3% | 99.9% |
| pulsar | default | 4 | 4 | 0.040s | 106.75 | 130,189 | 191.86 | 2.8% | 0.0% |
| pulsar | tuned | 4 | 4 | 0.027s | 186.12 | 145,432 | 204.87 | 6.4% | 0.0% |

## Matched rules

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| kubearmor | community | t1059-004-reverse-shell | harden-shell-history-mod, ksp-block-untrusted-shell-execution, ksp-defense-evasion-modify-system-image, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1059-006-python-exec | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1053-003-cron-persistence | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1098-004-ssh-authorized-keys | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1136-001-create-account | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-t1053-tactic-persistence-create-account-local-account, ksp-mitre-t1548-001-setuid-setgid |
| kubearmor | community | t1543-002-systemd-service | harden-shell-history-mod, ksp-create-or-modify-system-process-systemd-service, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1548-001-setuid-binary | harden-shell-history-mod, ksp-block-exec-inside-tmp, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1036-005-masquerading | harden-shell-history-mod, ksp-block-exec-inside-tmp, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1070-002-clear-logs | harden-shell-history-mod, ksp-check-log-clearing, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1070-003-clear-history | harden-shell-history-mod, ksp-block-untrusted-shell-execution, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-defence-evasion-hidden-files-directories |
| kubearmor | community | t1222-002-permission-modification | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1620-fileless-exec | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1003-008-shadow-read | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1552-001-credentials-in-files | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-defence-evasion-hidden-files-directories |
| kubearmor | community | t1552-007-container-api | harden-shell-history-mod, ksp-block-service-account, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | community | t1046-network-scan | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1082-system-discovery | harden-network-service-scanning, harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1613-container-discovery | harden-shell-history-mod, ksp-block-untrusted-shell-execution, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1105-ingress-tool-transfer | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | community | t1048-exfiltration-http | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | community | t1485-data-destruction | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1496-cryptominer | harden-shell-history-mod, ksp-block-exec-inside-tmp, ksp-defense-evasion-modify-system-image, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
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
| kubearmor | enforce | t1059-004-reverse-shell | tuned-shell-network-socket |
| kubearmor | enforce | t1059-006-python-exec | tuned-interpreter-spawned-shell |
| kubearmor | enforce | t1053-003-cron-persistence | tuned-scheduled-task-mod |
| kubearmor | enforce | t1548-001-setuid-binary | ksp-block-exec-inside-tmp |
| kubearmor | enforce | t1036-005-masquerading | ksp-block-exec-inside-tmp |
| kubearmor | enforce | t1070-002-clear-logs | tuned-log-tampering |
| kubearmor | enforce | t1070-003-clear-history | harden-shell-history-mod |
| kubearmor | enforce | t1620-fileless-exec | tuned-fileless-exec |
| kubearmor | enforce | t1003-008-shadow-read | tuned-shadow-file-access |
| kubearmor | enforce | t1552-001-credentials-in-files | tuned-credentials-in-files |
| kubearmor | enforce | t1552-007-container-api | ksp-block-service-account |
| kubearmor | enforce | t1046-network-scan | harden-network-service-scanning |
| kubearmor | enforce | t1613-container-discovery | tuned-container-discovery |
| kubearmor | enforce | t1048-exfiltration-http | tuned-credentials-in-files, tuned-shadow-file-access |
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
| kubearmor | tuned | t1620-fileless-exec | tuned-fileless-exec |
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
| kunai | community | t1548-001-setuid-binary | exe.error,run.tmpfs, run.tmpfs |
| kunai | community | t1036-005-masquerading | run.tmpfs |
| kunai | community | t1620-fileless-exec | exe.error,run.memfd, run.memfd |
| kunai | community | t1105-ingress-tool-transfer | exe.error,run.tmpfs, run.tmpfs |
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
| pulsar | tuned | t1059-006-python-exec | Interpreter inline code execution |
| pulsar | tuned | t1053-003-cron-persistence | Cron file created, Schedule a Cron job |
| pulsar | tuned | t1136-001-create-account | Local account creation |
| pulsar | tuned | t1543-002-systemd-service | Systemd unit file modification |
| pulsar | tuned | t1547-006-kernel-module | Linux Kernel Module Injection Detected (insmod) |
| pulsar | tuned | t1548-001-setuid-binary | Execution from temporary directory, Setuid or setgid bit set |
| pulsar | tuned | t1036-005-masquerading | Execution from temporary directory, Process masquerading as system daemon |
| pulsar | tuned | t1070-002-clear-logs | Log file truncation command, Truncate log files |
| pulsar | tuned | t1070-003-clear-history | Shell history deletion |
| pulsar | tuned | t1620-fileless-exec | Fileless execution from memory file descriptor |
| pulsar | tuned | t1552-007-container-api | Container runtime socket access |
| pulsar | tuned | t1105-ingress-tool-transfer | Executable bit set on file, Execution from temporary directory, System information discovery |
| pulsar | tuned | t1048-exfiltration-http | HTTP data upload |
| pulsar | tuned | t1485-data-destruction | Secure file deletion |
| pulsar | tuned | t1496-cryptominer | Cryptominer execution, Execution from temporary directory, Mining pool connection |

## Failures

### Failed tools

None.

### Log overflow

Deployments whose log or alerts stream exceeded `max_log_lines` / `max_log_bytes`: lines after the cap were dropped, so alerts emitted after it are missing and detection results are a lower bound.

None.

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

### Scenario cleanups with a non-zero exit code

None.
