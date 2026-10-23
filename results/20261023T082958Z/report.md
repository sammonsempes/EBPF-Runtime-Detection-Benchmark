# eBPF runtime detection benchmark: 20261023T082958Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261023T082958Z |
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
| config.profiles | ["community"] |
| config.repetitions | 5 |
| config.results_dir | results |
| config.scenarios | all |
| config.tools | ["falco", "tetragon", "kubearmor", "kunai"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| falco | 0.45.0 | ok | community | community: bad5350a7c3a |
| kubearmor | 1.7.5 | ok | community | community: cf1c6c0ff99c |
| kunai | 0.6.2 | ok | community | community: a8d2102db595 |
| tetragon | 1.7.1 | failed | community | community: f2fe37d1e025 |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kubearmor | community | 91.7% | 91.7% | 100.0% | 0.082s | 0 | 41.40 | 64.11 | +72.7% |
| falco | community | 79.2% | 79.2% | 66.7% | 0.005s | 2 | 22.27 | 81.68 | +5.5% |
| kunai | community | 20.8% | 20.8% | 0.0% | 0.103s | 0 | 9.96 | 76.50 | +13.2% |
| tetragon | community | — | — | — | — | 0 | — | — | — |

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

| Tactic | Scenario | Technique | falco/community | kubearmor/community | kunai/community | tetragon/community |
| --- | --- | --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| execution | t1059-006-python-exec | T1059.006 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | — |
| persistence | t1053-003-cron-persistence | T1053.003 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| persistence | t1136-001-create-account | T1136.001 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| persistence | t1543-002-systemd-service | T1543.002 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| persistence | t1547-006-kernel-module | T1547.006 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | — |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | — |
| privilege-escalation | t1611-escape-to-host | T1611 | ✅ 5/5 | ❌ 0/5 | ❌ 0/5 | — |
| defense-evasion | t1036-005-masquerading | T1036.005 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | — |
| defense-evasion | t1070-002-clear-logs | T1070.002 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| defense-evasion | t1070-003-clear-history | T1070.003 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| defense-evasion | t1222-002-permission-modification | T1222.002 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | — |
| defense-evasion | t1620-fileless-exec | T1620 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | — |
| credential-access | t1003-008-shadow-read | T1003.008 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| credential-access | t1552-001-credentials-in-files | T1552.001 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| credential-access | t1552-007-container-api | T1552.007 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | — |
| discovery | t1046-network-scan | T1046 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| discovery | t1082-system-discovery | T1082 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | — |
| discovery | t1613-container-discovery | T1613 | ❌ 0/5 | ✅ 5/5 | ❌ 0/5 | — |
| command-and-control | t1105-ingress-tool-transfer | T1105 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | — |
| exfiltration | t1048-exfiltration-http | T1048 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| impact | t1485-data-destruction | T1485 | ✅ 5/5 | ✅ 5/5 | ❌ 0/5 | — |
| impact | t1496-cryptominer | T1496 | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | — |

### Coverage per tactic

| Tactic | falco/community | kubearmor/community | kunai/community | tetragon/community |
| --- | --- | --- | --- | --- |
| execution | 1/2 | 2/2 | 0/2 | — |
| persistence | 5/5 | 4/5 | 0/5 | — |
| privilege-escalation | 2/2 | 1/2 | 1/2 | — |
| defense-evasion | 4/5 | 5/5 | 2/5 | — |
| credential-access | 2/3 | 3/3 | 0/3 | — |
| discovery | 1/3 | 3/3 | 0/3 | — |
| command-and-control | 1/1 | 1/1 | 1/1 | — |
| exfiltration | 1/1 | 1/1 | 0/1 | — |
| impact | 2/2 | 2/2 | 1/2 | — |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | falco/community | kubearmor/community | kunai/community | tetragon/community |
| --- | --- | --- | --- | --- |
| benign-admin-commands | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | — |
| benign-backup | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | — |
| benign-compile | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | — |
| benign-log-rotation | ✅ 0/5 | ⚠️ 5/5 | ✅ 0/5 | — |
| benign-package-query | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | — |
| benign-web-server | ⚠️ 5/5 | ⚠️ 5/5 | ✅ 0/5 | — |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| falco | community | benign-admin-commands | Read environment variable from /proc files |
| falco | community | benign-compile | Drop and execute new binary in container |
| falco | community | benign-package-query | Launch Package Management Process in Container |
| falco | community | benign-web-server | Launch Ingress Remote File Copy Tools in Container |
| kubearmor | community | benign-admin-commands | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-discovery-process-discovery, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-backup | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-compile | harden-shell-history-mod |
| kubearmor | community | benign-log-rotation | harden-shell-history-mod, ksp-check-log-clearing, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | benign-package-query | harden-pkg-mngr-exec, harden-shell-history-mod |
| kubearmor | community | benign-web-server | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | falco/community | kubearmor/community | kunai/community | tetragon/community |
| --- | --- | --- | --- | --- |
| t1059-004-reverse-shell | 0.013s / 0.069s | 0.035s / 0.163s | — | — |
| t1059-006-python-exec | — | 0.073s / 0.144s | — | — |
| t1053-003-cron-persistence | 0.005s / 0.011s | 0.067s / 0.168s | — | — |
| t1098-004-ssh-authorized-keys | -0.017s / -0.006s | 0.106s / 0.173s | — | — |
| t1136-001-create-account | 0.115s / 0.156s | 0.062s / 0.091s | — | — |
| t1543-002-systemd-service | 0.003s / 0.005s | 0.025s / 0.140s | — | — |
| t1547-006-kernel-module | 0.013s / 0.599s | — | — | — |
| t1548-001-setuid-binary | 0.009s / 0.012s | 0.104s / 0.147s | 0.105s / 0.152s | — |
| t1611-escape-to-host | 0.003s / 0.008s | — | — | — |
| t1036-005-masquerading | 0.021s / 0.063s | 0.112s / 0.172s | 0.070s / 0.139s | — |
| t1070-002-clear-logs | -0.090s / -0.056s | -0.001s / 0.145s | — | — |
| t1070-003-clear-history | 0.006s / 0.040s | 0.105s / 0.163s | — | — |
| t1222-002-permission-modification | — | 0.058s / 0.121s | — | — |
| t1620-fileless-exec | 0.034s / 0.081s | 0.070s / 0.163s | 0.073s / 0.135s | — |
| t1003-008-shadow-read | 0.003s / 0.015s | 0.078s / 0.116s | — | — |
| t1552-001-credentials-in-files | 0.004s / 0.005s | 0.150s / 0.173s | — | — |
| t1552-007-container-api | — | 0.144s / 0.157s | — | — |
| t1046-network-scan | 0.005s / 0.010s | 0.081s / 0.122s | — | — |
| t1082-system-discovery | — | 0.121s / 0.159s | — | — |
| t1613-container-discovery | — | 0.084s / 0.178s | — | — |
| t1105-ingress-tool-transfer | 0.003s / 0.023s | 0.079s / 0.161s | 0.104s / 0.132s | — |
| t1048-exfiltration-http | 0.012s / 0.019s | 0.061s / 0.122s | — | — |
| t1485-data-destruction | 0.003s / 0.016s | -0.004s / 0.116s | — | — |
| t1496-cryptominer | 0.004s / 0.007s | 0.027s / 0.109s | 0.103s / 0.130s | — |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| falco | community | 100.0% | 10 |
| kubearmor | community | 100.0% | 13 |
| kunai | community | 100.0% | 0 |
| tetragon | community | — | 0 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | detection only | — | — | — | — | — | — | — | — |
| kubearmor | no enforce run | — | — | — | — | — | — | bpf-lsm, apparmor, selinux-host-only, presets | yes |
| kunai | no enforce run | — | — | — | — | — | — | kill | no |
| tetragon | no enforce run | — | — | — | — | — | — | sigkill | yes |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | falco/community | kubearmor/community | kunai/community | tetragon/community |
| --- | --- | --- | --- | --- | --- | --- |
| exec | execs_per_sec | 589.21 | 616.76 (-4.7%) | 619.55 (-5.1%) | 842.32 (-43.0%) | — |
| exec | p50_us | 1,312 | 1,366 (+4.1%) | 1,330 (+1.4%) | 1,012 (-22.9%) | — |
| exec | p99_us | 8,512 | 7,211 (-15.3%) | 7,095 (-16.7%) | 5,473 (-35.7%) | — |
| fileio | ops_per_sec | 183.53 | 207.05 (-12.8%) | 309.67 (-68.7%) | 381.39 (-107.8%) | — |
| fileio | p50_us | 4,339 | 3,951 (-8.9%) | 2,822 (-34.9%) | 2,276 (-47.5%) | — |
| fileio | p99_us | 20,682 | 15,187 (-26.6%) | 10,712 (-48.2%) | 9,698 (-53.1%) | — |
| syscall | connect_ops_per_sec | 21,254 | 18,379 (+13.5%) | 3,145 (+85.2%) | 22,560 (-6.1%) | — |
| syscall | connect_p50_ns | 15,935 | 16,715 (+4.9%) | 44,880 (+181.6%) | 19,720 (+23.8%) | — |
| syscall | connect_p99_ns | 154,551 | 200,270 (+29.6%) | 1,589,127 (+928.2%) | 124,865 (-19.2%) | — |
| syscall | getpid_ops_per_sec | 2,352,531 | 2,315,102 (+1.6%) | 2,148,045 (+8.7%) | 3,136,289 (-33.3%) | — |
| syscall | getpid_p50_ns | 257.00 | 264.00 (+2.7%) | 267.00 (+3.9%) | 191.00 (-25.7%) | — |
| syscall | getpid_p99_ns | 427.00 | 453.00 (+6.1%) | 1,011 (+136.8%) | 1,001 (+134.4%) | — |
| syscall | openat_ops_per_sec | 232,684 | 147,846 (+36.5%) | 27,062 (+88.4%) | 254,665 (-9.4%) | — |
| syscall | openat_p50_ns | 2,949 | 3,899 (+32.2%) | 13,659 (+363.2%) | 2,783 (-5.6%) | — |
| syscall | openat_p99_ns | 10,871 | 25,255 (+132.3%) | 271,381 (+2396.4%) | 14,126 (+29.9%) | — |
| syscall | read_ops_per_sec | 1,410,616 | 1,448,248 (-2.7%) | 1,482,833 (-5.1%) | 944,139 (+33.1%) | — |
| syscall | read_p50_ns | 429.00 | 466.00 (+8.6%) | 466.00 (+8.6%) | 807.00 (+88.1%) | — |
| syscall | read_p99_ns | 1,745 | 1,797 (+3.0%) | 977.00 (-44.0%) | 4,072 (+133.4%) | — |
| syscall | stat_ops_per_sec | 707,617 | 705,450 (+0.3%) | 677,240 (+4.3%) | 972,247 (-37.4%) | — |
| syscall | stat_p50_ns | 1,014 | 1,043 (+2.9%) | 1,044 (+3.0%) | 799.00 (-21.2%) | — |
| syscall | stat_p99_ns | 3,855 | 3,963 (+2.8%) | 4,135 (+7.3%) | 3,958 (+2.7%) | — |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | community | 22.27 | 127.03 | 81.68 | 88.23 | +3.5% | +0.3% | 24.81 | 52.07 | +3.8 pp |
| kubearmor | community | 41.40 | 687.23 | 64.11 | 112.43 | +5.6% | +4.3% | 26.96 | 79.91 | +5.9 pp |
| kunai | community | 9.96 | 58.59 | 76.50 | 78.11 | -12.4% | -33.3% | 18.58 | 43.16 | -2.5 pp |
| tetragon | community | — | — | — | — | — | — | — | — | — |

Host CPU is sampled from /proc/stat every second during workloads (Docker backend only); baseline median 21.06%, max 44.43%. The delta is in percentage points of the whole host.

## Operational aspects

Scores follow the rubric in docs/methodology.md (1 worst, 5 best).

| Tool | Version | License | Deployment | Rule customization | Output quality | Deploy steps | Rule language | Custom rules | Hot reload | Output formats | Enrichment | ATT&CK mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | 0.45.0 | Apache-2.0 | 5 | 5 | 5 | 2 | YAML rules, macros and lists whose conditions use the Falco filter language over syscall and plugin fields, with exceptions, append and override | yes | yes | json, text | container, kubernetes | yes | Deployment 5: the image runs with defaults (docker/falco/Dockerfile ships /usr/bin/falco as CMD, its usage label is a single privileged docker run, falco.yaml defaults engine.kind to modern_ebpf which needs no kernel headers or driver loader, and the container plugin is enabled by the packaged config.d/falco.container_plugin.yaml); on Kubernetes the chart README documents a plain "helm install falco falcosecurity/falco". The only benchmark change is a config.d drop-in enabling json_output and disabling syslog. Modern eBPF still requires a BTF-enabled kernel. Rule customization 5: declarative YAML rules loaded from rules_files and rules.d, rule enable/disable by name or tag in falco.yaml, and watch_config_files: true reloads configuration and rules on change (plus SIGHUP and the 0.45 reload API). Output quality 5: json_output emits rule, priority, time, source, hostname, tags and output_fields (formats.cpp); upstream stable rules carry mitre_* and Txxxx tags, the container plugin adds container.* and k8s.pod.* fields, and parent/ancestor fields (proc.pname, proc.aname) are available, although ancestry depth depends on each rule's output template.  |
| kubearmor | 1.7.5 | Apache-2.0 | 3 | 4 | 4 | 2 | declarative KubeArmorPolicy YAML (process, file, network, capabilities, syscalls and presets rules with matchPaths, matchDirectories, matchPatterns, fromSource, Allow/Audit/Block actions) | yes | yes | json | container, kubernetes | no | deployment 3: outside Kubernetes the daemon must be started with k8s=false and policy flags (deployments/podman/docker-compose.yaml, KubeArmor/packaging/kubearmor.yaml), upstream pairs it with the kubearmor-init container that compiles the eBPF objects against the host kernel (Dockerfile.init, build/compile.sh), it needs the container runtime socket, bpffs, securityfs and debugfs, and policies can only be fed through the gRPC PolicyService (karmor vm policy add) or the JSON backup directory /opt/kubearmor/policies read at startup (core/unorchestratedUpdates.go restoreKubeArmorPolicies). Helm and the operator make the Kubernetes path simpler. rule_customization 4: policies are declarative and applied live (CRD watchers in Kubernetes, gRPC PolicyService outside), but expressiveness is limited to paths, directories, glob patterns, source binaries and protocols; arguments can only be matched for Allow lists (matchArgs) and there is no correlation; Audit rules need visibility enabled (getting-started/kubearmor_visibility.md). output_quality 4: JSON per event (types/types.go Log struct) with container id/name/image, pod, namespace, labels, host and container pids, parent process name, source command line, policy name, severity, tags, message, action and result; ATT&CK mapping only exists when the policy author puts MITRE tags in the policy (hardening templates do), there is no built-in technique field and no ancestry beyond the parent. |
| kunai | 0.6.2 | GPL-3.0 | 3 | 4 | 4 | 3 | Gene YAML rules (match-on event names, $variables matching event fields with ==, ~= regex, &= flags and numeric comparisons, boolean condition, severity, ATT&CK ids), plus JSON-lines IoCs and YARA for file scans | yes | no | json | process_ancestry, container, file_hashes, user, dns | yes | Deployment 3: upstream ships a distribution-agnostic static binary (assets kunai-amd64 / kunai-aarch64 with .asc signatures and sha512.txt on the v0.6.2 release) and no container image or Kubernetes manifest; the README recommends the binary, the docs install it as a systemd service with `kunai install`. Running it in a container needs host preparation: privileged mode, host PID namespace, BTF and the bpf/debug filesystems. Steps 3 = download, chmod +x, `kunai run -r <rules>`; upstream ships no detection rule, so with the bare `sudo kunai` quickstart every event is printed and nothing is an alert. Rule customization 4: rules are declarative YAML (Gene engine) with detection, filter and dependency types, regex and flag operators, severity and actions (kill, scan-files), loaded from the config `scanner.rules` or `-r`; there is no runtime reload in 0.6.2, a restart is required (hardened mode even requires a reboot). Output quality 4: one JSON object per line (`data`, `detection`, `filter`, `info`) with process ancestors, parent command line, executable hashes, task/parent uid/gid, mount namespace and container name/type; `detection` carries rule names, tags, severity and ATT&CK ids from rule metadata. Not 5 because container context is only the UTS hostname plus a heuristic type (no container id, image or Kubernetes metadata), and the container `type` is often null for processes started after kunai. |
| tetragon | 1.7.1 | Apache-2.0 | 5 | 4 | 4 | 2 | TracingPolicy YAML (Kubernetes CRD format) attaching kprobes, tracepoints, uprobes or LSM hooks with in-kernel selectors (matchArgs, matchBinaries, matchNamespaces, matchCapabilities) and actions | yes | yes | json | container, kubernetes | no | Deployment 5: docs/content/en/docs/installation/container.md runs the stable image with a single privileged docker run (only the BTF file is mounted) and the Helm chart installs with defaults; the benchmark adds bpffs, /procRoot and an export file location, mirroring the chart's tetragon_configmap.yaml (procfs /procRoot, export-filename). Rule customization 4: policies are declarative and can be added or removed at runtime (TracingPolicy CRDs, tetra tracingpolicy add), but they are low level: authors must know kernel function or syscall names and argument types, a hook takes at most 5 selectors and 5 argument filters, integer filters accept at most 4 values (pkg/selectors/kernel.go), a policy referencing a missing symbol fails unless ignore.callNotFound is set, and there is no correlation across events. Output quality 4: JSON events carry process and parent (binary, arguments, uid, exec_id, start time), optional full ancestry (enable-ancestors), pod/container/workload metadata on Kubernetes and the cgroup-derived container id ("docker") elsewhere, plus policy_name, message and user-defined tags; there is no built-in ATT&CK mapping or severity, and outside Kubernetes the container name and image are not resolved.  |

### Measured operational metrics

Measured per deployment: time from container start to readiness, alert and log volume over the deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and share of alerts carrying a container id or name. Rubric scores repeated for comparison.

| Tool | Profile | Deployment score | Output quality score | Time to ready | Alerts / min | Log lines / min | Log volume MiB | Attributed alerts | Alerts with container identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falco | community | 5 | 5 | 0.897s | 32.66 | 39.04 | 0.68 | 89.3% | 94.4% |
| kubearmor | community | 3 | 4 | 5.926s | 602.90 | 32,797 | 384.54 | 100.0% | 100.0% |
| kunai | community | 3 | 4 | 2.322s | 568.40 | 569.84 | 9.00 | 2.9% | 100.0% |
| tetragon | community | 5 | 4 | — | 0.00 | 396.72 | 0.14 | — | — |

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
| kubearmor | community | t1059-004-reverse-shell | harden-shell-history-mod, ksp-block-untrusted-shell-execution, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1059-006-python-exec | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1053-003-cron-persistence | harden-shell-history-mod |
| kubearmor | community | t1098-004-ssh-authorized-keys | harden-shell-history-mod |
| kubearmor | community | t1136-001-create-account | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-t1053-tactic-persistence-create-account-local-account, ksp-mitre-t1548-001-setuid-setgid |
| kubearmor | community | t1543-002-systemd-service | harden-shell-history-mod, ksp-create-or-modify-system-process-systemd-service, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1548-001-setuid-binary | harden-shell-history-mod, ksp-block-exec-inside-tmp, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1036-005-masquerading | harden-shell-history-mod, ksp-block-exec-inside-tmp |
| kubearmor | community | t1070-002-clear-logs | harden-shell-history-mod, ksp-check-log-clearing, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1070-003-clear-history | harden-shell-history-mod, ksp-block-untrusted-shell-execution, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-defence-evasion-hidden-files-directories |
| kubearmor | community | t1222-002-permission-modification | harden-shell-history-mod |
| kubearmor | community | t1620-fileless-exec | harden-shell-history-mod, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1003-008-shadow-read | harden-shell-history-mod, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1552-001-credentials-in-files | harden-shell-history-mod, ksp-mitre-tactic-defence-evasion-hidden-files-directories |
| kubearmor | community | t1552-007-container-api | harden-shell-history-mod, ksp-block-service-account, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | community | t1046-network-scan | harden-shell-history-mod, ksp-defense-evasion-modify-system-image |
| kubearmor | community | t1082-system-discovery | harden-network-service-scanning, harden-shell-history-mod |
| kubearmor | community | t1613-container-discovery | harden-shell-history-mod, ksp-block-untrusted-shell-execution, ksp-mitre-t1053-persistence-external-remote-services |
| kubearmor | community | t1105-ingress-tool-transfer | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-discovery-account-discovery-local-account, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | community | t1048-exfiltration-http | harden-shell-history-mod, ksp-defense-evasion-modify-system-image, ksp-mitre-t1053-persistence-external-remote-services, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kubearmor | community | t1485-data-destruction | harden-shell-history-mod |
| kubearmor | community | t1496-cryptominer | harden-shell-history-mod, ksp-block-exec-inside-tmp, ksp-defense-evasion-modify-system-image, ksp-mitre-tactic-credential-access-unsecured-credentials-private-keys |
| kunai | community | t1548-001-setuid-binary | run.tmpfs |
| kunai | community | t1036-005-masquerading | run.tmpfs |
| kunai | community | t1620-fileless-exec | run.memfd |
| kunai | community | t1105-ingress-tool-transfer | run.tmpfs |
| kunai | community | t1496-cryptominer | run.tmpfs |

## Failures

### Failed tools

| Tool | Status | Error |
| --- | --- | --- |
| tetragon | failed | community: ToolStartError: container bench-tool-tetragon-community exited with code 255; last logs: level=warn msg="Unload failed during destroy" sensor=generic_kprobe error="unload of sensor generic_kprobe failed: sensor not loaded" level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor generic_kprobe" level=info msg="Sensor unloaded" sensor=generic_kprobe maps-error=[] level=info msg="Unloading sensor __base__" level=info msg="Sensor unloaded" sensor=__base__ maps-error=[] level=info msg="BPF events statistics: 0 received, 0% events loss" level=info msg="Observer events statistics" received=0 lost=0 errors=0 filterPass=0 filterDrop=0 level=error msg="Failed to execute tetragon" error="sensor generic_kprobe from collection process.credentials.changes.at.syscalls failed to load: tetragon, aborting could not load sensor BPF maps: failed to load map 'kprobe_calls' for sensor 'generic_kprobe': failed to create subbir for 'kprobe_calls': mkdir /run/cilium/bpffs/tetragon/process.credentials.changes.at.syscalls: operation not permitted" |

### Scenario executions with a non-zero exit code

None.

### Scenario cleanups with a non-zero exit code

None.
