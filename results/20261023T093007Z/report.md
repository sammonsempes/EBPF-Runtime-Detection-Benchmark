# eBPF runtime detection benchmark: 20261023T093007Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261023T093007Z |
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
| config.tools | ["tetragon"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| tetragon | 1.7.1 | ok | community | community: 1451971dd8bf |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | community | 100.0% | 100.0% | 100.0% | 0.105s | 11 | 15.43 | 478.76 | +7.4% |

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

| Tactic | Scenario | Technique | tetragon/community |
| --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | ✅ 5/5 |
| execution | t1059-006-python-exec | T1059.006 | ✅ 5/5 |
| persistence | t1053-003-cron-persistence | T1053.003 | ✅ 5/5 |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | ✅ 5/5 |
| persistence | t1136-001-create-account | T1136.001 | ✅ 5/5 |
| persistence | t1543-002-systemd-service | T1543.002 | ✅ 5/5 |
| persistence | t1547-006-kernel-module | T1547.006 | ✅ 5/5 |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | ✅ 5/5 |
| privilege-escalation | t1611-escape-to-host | T1611 | ✅ 5/5 |
| defense-evasion | t1036-005-masquerading | T1036.005 | ✅ 5/5 |
| defense-evasion | t1070-002-clear-logs | T1070.002 | ✅ 5/5 |
| defense-evasion | t1070-003-clear-history | T1070.003 | ✅ 5/5 |
| defense-evasion | t1222-002-permission-modification | T1222.002 | ✅ 5/5 |
| defense-evasion | t1620-fileless-exec | T1620 | ✅ 5/5 |
| credential-access | t1003-008-shadow-read | T1003.008 | ✅ 5/5 |
| credential-access | t1552-001-credentials-in-files | T1552.001 | ✅ 5/5 |
| credential-access | t1552-007-container-api | T1552.007 | ✅ 5/5 |
| discovery | t1046-network-scan | T1046 | ✅ 5/5 |
| discovery | t1082-system-discovery | T1082 | ✅ 5/5 |
| discovery | t1613-container-discovery | T1613 | ✅ 5/5 |
| command-and-control | t1105-ingress-tool-transfer | T1105 | ✅ 5/5 |
| exfiltration | t1048-exfiltration-http | T1048 | ✅ 5/5 |
| impact | t1485-data-destruction | T1485 | ✅ 5/5 |
| impact | t1496-cryptominer | T1496 | ✅ 5/5 |

### Coverage per tactic

| Tactic | tetragon/community |
| --- | --- |
| execution | 2/2 |
| persistence | 5/5 |
| privilege-escalation | 2/2 |
| defense-evasion | 5/5 |
| credential-access | 3/3 |
| discovery | 3/3 |
| command-and-control | 1/1 |
| exfiltration | 1/1 |
| impact | 2/2 |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | tetragon/community |
| --- | --- |
| benign-admin-commands | ⚠️ 5/5 |
| benign-backup | ⚠️ 5/5 |
| benign-compile | ⚠️ 5/5 |
| benign-log-rotation | ⚠️ 5/5 |
| benign-package-query | ⚠️ 5/5 |
| benign-web-server | ⚠️ 5/5 |

### Rules raising false positives

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
| tetragon | community | benign-admin-commands | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-backup | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-compile | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-log-rotation | creds-capability-checks, file-monitoring-filtered, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-package-query | creds-capability-checks, process-creds-changed, process-exec-elf-begin |
| tetragon | community | benign-web-server | accept, connect, creds-capability-checks, process-creds-changed, process-exec-elf-begin |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | tetragon/community |
| --- | --- |
| t1059-004-reverse-shell | 0.142s / 0.195s |
| t1059-006-python-exec | 0.149s / 0.185s |
| t1053-003-cron-persistence | 0.131s / 0.168s |
| t1098-004-ssh-authorized-keys | 0.116s / 0.137s |
| t1136-001-create-account | 0.136s / 0.153s |
| t1543-002-systemd-service | 0.116s / 0.180s |
| t1547-006-kernel-module | 0.098s / 0.108s |
| t1548-001-setuid-binary | 0.060s / 0.124s |
| t1611-escape-to-host | 0.122s / 0.146s |
| t1036-005-masquerading | 0.046s / 0.167s |
| t1070-002-clear-logs | -0.009s / 0.079s |
| t1070-003-clear-history | 0.141s / 0.155s |
| t1222-002-permission-modification | 0.073s / 0.123s |
| t1620-fileless-exec | 0.115s / 0.181s |
| t1003-008-shadow-read | 0.043s / 0.124s |
| t1552-001-credentials-in-files | 0.063s / 0.156s |
| t1552-007-container-api | 0.082s / 0.154s |
| t1046-network-scan | 0.108s / 0.168s |
| t1082-system-discovery | 0.153s / 0.182s |
| t1613-container-discovery | 0.127s / 0.168s |
| t1105-ingress-tool-transfer | 0.131s / 0.150s |
| t1048-exfiltration-http | 0.085s / 0.172s |
| t1485-data-destruction | -0.006s / 0.097s |
| t1496-cryptominer | 0.124s / 0.160s |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| tetragon | community | 100.0% | 9 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | no enforce run | — | — | — | — | — | — | sigkill | yes |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | tetragon/community |
| --- | --- | --- | --- |
| exec | execs_per_sec | 2,031 | 1,242 (+38.9%) |
| exec | p50_us | 463.38 | 697.16 (+50.5%) |
| exec | p99_us | 1,105 | 1,947 (+76.1%) |
| fileio | ops_per_sec | 593.06 | 605.48 (-2.1%) |
| fileio | p50_us | 1,547 | 1,517 (-1.9%) |
| fileio | p99_us | 3,518 | 3,358 (-4.5%) |
| syscall | connect_ops_per_sec | 68,411 | 31,882 (+53.4%) |
| syscall | connect_p50_ns | 5,527 | 9,017 (+63.1%) |
| syscall | connect_p99_ns | 21,276 | 88,072 (+313.9%) |
| syscall | getpid_ops_per_sec | 7,003,014 | 7,092,658 (-1.3%) |
| syscall | getpid_p50_ns | 87.00 | 87.00 (+0.0%) |
| syscall | getpid_p99_ns | 178.00 | 177.00 (-0.6%) |
| syscall | openat_ops_per_sec | 671,101 | 719,410 (-7.2%) |
| syscall | openat_p50_ns | 1,018 | 1,006 (-1.2%) |
| syscall | openat_p99_ns | 2,508 | 2,238 (-10.8%) |
| syscall | read_ops_per_sec | 4,616,471 | 566,845 (+87.7%) |
| syscall | read_p50_ns | 156.00 | 1,543 (+889.1%) |
| syscall | read_p99_ns | 226.00 | 2,338 (+934.5%) |
| syscall | stat_ops_per_sec | 2,303,577 | 2,290,806 (+0.6%) |
| syscall | stat_p50_ns | 346.00 | 344.00 (-0.6%) |
| syscall | stat_p99_ns | 528.00 | 606.00 (+14.8%) |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | community | 15.43 | 318.31 | 478.76 | 2,861 | +7.4% | +0.6% | 16.94 | 62.64 | +4.0 pp |

Host CPU is sampled from /proc/stat every second during workloads (Docker backend only); baseline median 12.97%, max 30.32%. The delta is in percentage points of the whole host.

## Operational aspects

Scores follow the rubric in docs/methodology.md (1 worst, 5 best).

| Tool | Version | License | Deployment | Rule customization | Output quality | Deploy steps | Rule language | Custom rules | Hot reload | Output formats | Enrichment | ATT&CK mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | 1.7.1 | Apache-2.0 | 5 | 4 | 4 | 2 | TracingPolicy YAML (Kubernetes CRD format) attaching kprobes, tracepoints, uprobes or LSM hooks with in-kernel selectors (matchArgs, matchBinaries, matchNamespaces, matchCapabilities) and actions | yes | yes | json | container, kubernetes | no | Deployment 5: docs/content/en/docs/installation/container.md runs the stable image with a single privileged docker run (only the BTF file is mounted) and the Helm chart installs with defaults; the benchmark adds bpffs, /procRoot and an export file location, mirroring the chart's tetragon_configmap.yaml (procfs /procRoot, export-filename). Rule customization 4: policies are declarative and can be added or removed at runtime (TracingPolicy CRDs, tetra tracingpolicy add), but they are low level: authors must know kernel function or syscall names and argument types, a hook takes at most 5 selectors and 5 argument filters, integer filters accept at most 4 values (pkg/selectors/kernel.go), a policy referencing a missing symbol fails unless ignore.callNotFound is set, and there is no correlation across events. Output quality 4: JSON events carry process and parent (binary, arguments, uid, exec_id, start time), optional full ancestry (enable-ancestors), pod/container/workload metadata on Kubernetes and the cgroup-derived container id ("docker") elsewhere, plus policy_name, message and user-defined tags; there is no built-in ATT&CK mapping or severity, and outside Kubernetes the container name and image are not resolved.  |

### Measured operational metrics

Measured per deployment: time from container start to readiness, alert and log volume over the deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and share of alerts carrying a container id or name. Rubric scores repeated for comparison.

| Tool | Profile | Deployment score | Output quality score | Time to ready | Alerts / min | Log lines / min | Log volume MiB | Attributed alerts | Alerts with container identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tetragon | community | 5 | 4 | 20.840s | 33,545 | 40,407 | 1,724 | 2.5% | 71.8% |

## Matched rules

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |
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

## Failures

### Failed tools

None.

### Scenario executions with a non-zero exit code

None.

### Scenario cleanups with a non-zero exit code

None.
