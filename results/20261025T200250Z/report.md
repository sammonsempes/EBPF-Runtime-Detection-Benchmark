# eBPF runtime detection benchmark: 20261025T200250Z

## Run metadata

| Key | Value |
| --- | --- |
| run_id | 20261025T200250Z |
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
| config.tools | ["pulsar"] |

### Tools

| Tool | Version | Status | Profiles | Config SHA-256 |
| --- | --- | --- | --- | --- |
| pulsar | 0.10.1 | partial | default, tuned | community: None, default: 9cb2665a655e, enforce: None, tuned: dd1914d53753 |

## Leaderboard

Recall counts attack scenarios detected in a majority of repetitions. Overhead percentages are positive when the tool makes the workload worse.

| Tool | Profile | Recall | Detection rate | FP rate | Median latency | Background noise | CPU % (median) | Memory MiB (median) | Syscall latency overhead |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pulsar | default | — | — | — | — | 0 | 173.51 | 15,260 | +42.3% |
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

| Tactic | Scenario | Technique | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- |
| execution | t1059-004-reverse-shell | T1059.004 | — | — |
| execution | t1059-006-python-exec | T1059.006 | — | — |
| persistence | t1053-003-cron-persistence | T1053.003 | — | — |
| persistence | t1098-004-ssh-authorized-keys | T1098.004 | — | — |
| persistence | t1136-001-create-account | T1136.001 | — | — |
| persistence | t1543-002-systemd-service | T1543.002 | — | — |
| persistence | t1547-006-kernel-module | T1547.006 | — | — |
| privilege-escalation | t1548-001-setuid-binary | T1548.001 | — | — |
| privilege-escalation | t1611-escape-to-host | T1611 | — | — |
| defense-evasion | t1036-005-masquerading | T1036.005 | — | — |
| defense-evasion | t1070-002-clear-logs | T1070.002 | — | — |
| defense-evasion | t1070-003-clear-history | T1070.003 | — | — |
| defense-evasion | t1222-002-permission-modification | T1222.002 | — | — |
| defense-evasion | t1620-fileless-exec | T1620 | — | — |
| credential-access | t1003-008-shadow-read | T1003.008 | — | — |
| credential-access | t1552-001-credentials-in-files | T1552.001 | — | — |
| credential-access | t1552-007-container-api | T1552.007 | — | — |
| discovery | t1046-network-scan (invalid) | T1046 | — | — |
| discovery | t1082-system-discovery | T1082 | — | — |
| discovery | t1613-container-discovery | T1613 | — | — |
| command-and-control | t1105-ingress-tool-transfer | T1105 | — | — |
| exfiltration | t1048-exfiltration-http | T1048 | — | — |
| impact | t1485-data-destruction | T1485 | — | — |
| impact | t1496-cryptominer | T1496 | — | — |

### Coverage per tactic

| Tactic | pulsar/default | pulsar/tuned |
| --- | --- | --- |

## False positives

Benign runs with at least one attributed alert, out of all benign runs.

| Scenario | pulsar/default | pulsar/tuned |
| --- | --- | --- |
| benign-admin-commands | — | — |
| benign-backup | — | — |
| benign-compile | — | — |
| benign-log-rotation | — | — |
| benign-package-query | — | — |
| benign-web-server | — | — |

## Detection latency

Median / p95 of the first attributed alert's emission time minus the action timestamp printed by the scenario (`BENCH_ACTION`), or minus the scenario start time when the script printed none.

| Scenario | pulsar/default | pulsar/tuned |
| --- | --- | --- |
| t1059-004-reverse-shell | — | — |
| t1059-006-python-exec | — | — |
| t1053-003-cron-persistence | — | — |
| t1098-004-ssh-authorized-keys | — | — |
| t1136-001-create-account | — | — |
| t1543-002-systemd-service | — | — |
| t1547-006-kernel-module | — | — |
| t1548-001-setuid-binary | — | — |
| t1611-escape-to-host | — | — |
| t1036-005-masquerading | — | — |
| t1070-002-clear-logs | — | — |
| t1070-003-clear-history | — | — |
| t1222-002-permission-modification | — | — |
| t1620-fileless-exec | — | — |
| t1003-008-shadow-read | — | — |
| t1552-001-credentials-in-files | — | — |
| t1552-007-container-api | — | — |
| t1046-network-scan | — | — |
| t1082-system-discovery | — | — |
| t1613-container-discovery | — | — |
| t1105-ingress-tool-transfer | — | — |
| t1048-exfiltration-http | — | — |
| t1485-data-destruction | — | — |
| t1496-cryptominer | — | — |

### Latency reference

| Tool | Profile | Runs with action timestamp | Alerts before the action |
| --- | --- | --- | --- |
| pulsar | default | — | 0 |
| pulsar | tuned | — | 0 |

## Response effectiveness

Enforce profiles only. Prevention rate: valid attack scenarios whose effect was not achieved in a majority of repetitions, over valid attack scenarios run. Detected not prevented and prevented without alert count repetitions; a prevention without any attributed alert is suspicious (the effect may have failed for another reason). Collateral damage: valid benign scenarios whose effect was not achieved under enforcement. Response latency: first enforcement alert minus the action timestamp. Results of a deployment whose enforcement could not be verified are marked invalid.

| Tool | Prevention rate | Detected not prevented | Prevented without alert | Collateral damage | Median response latency | Enforcement alerts | Enforcement verified | Mechanisms | Synchronous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pulsar | detection only | — | — | — | — | — | — | — | — |

## Overhead

Median over repetitions. The percentage is the overhead relative to the baseline median: positive always means worse. Δ marks metrics without a known direction (signed relative delta).

| Workload | Metric | Baseline | pulsar/default | pulsar/tuned |
| --- | --- | --- | --- | --- |
| exec | execs_per_sec | 1,561 | 604.03 (+61.3%) | — |
| exec | p50_us | 622.96 | 852.09 (+36.8%) | — |
| exec | p99_us | 1,064 | 80,634 (+7478.1%) | — |
| fileio | ops_per_sec | 1,427 | 1,213 (+15.0%) | — |
| fileio | p50_us | 687.54 | 747.45 (+8.7%) | — |
| fileio | p99_us | 880.63 | 1,962 (+122.8%) | — |
| syscall | connect_ops_per_sec | 91,348 | 45,330 (+50.4%) | — |
| syscall | connect_p50_ns | 5,099 | 11,037 (+116.5%) | — |
| syscall | connect_p99_ns | 5,909 | 18,012 (+204.8%) | — |
| syscall | getpid_ops_per_sec | 2,615,140 | 2,217,568 (+15.2%) | — |
| syscall | getpid_p50_ns | 348.00 | 396.00 (+13.8%) | — |
| syscall | getpid_p99_ns | 384.00 | 549.00 (+43.0%) | — |
| syscall | openat_ops_per_sec | 531,224 | 255,758 (+51.9%) | — |
| syscall | openat_p50_ns | 1,846 | 3,622 (+96.2%) | — |
| syscall | openat_p99_ns | 1,999 | 5,696 (+185.0%) | — |
| syscall | read_ops_per_sec | 330,792 | 278,599 (+15.8%) | — |
| syscall | read_p50_ns | 2,994 | 3,490 (+16.6%) | — |
| syscall | read_p99_ns | 3,233 | 4,578 (+41.6%) | — |
| syscall | stat_ops_per_sec | 1,350,695 | 1,146,751 (+15.1%) | — |
| syscall | stat_p50_ns | 706.00 | 818.00 (+15.9%) | — |
| syscall | stat_p99_ns | 771.00 | 1,055 (+36.8%) | — |

### Tool resource usage

| Tool | Profile | CPU % median | CPU % max | Memory MiB median | Memory MiB max | Latency overhead | Throughput overhead | Host CPU % median | Host CPU % max | Host CPU Δ vs baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pulsar | default | 173.51 | 200.54 | 15,260 | 22,892 | +42.3% | +15.8% | — | — | — |
| pulsar | tuned | — | — | — | — | — | — | — | — | — |

## Operational aspects

Scores follow the rubric in docs/methodology.md (1 worst, 5 best).

| Tool | Version | License | Deployment | Rule customization | Output quality | Deploy steps | Rule language | Custom rules | Hot reload | Output formats | Enrichment | ATT&CK mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pulsar | 0.10.1 | Apache-2.0 AND GPL-2.0 | 4 | 4 | 4 | 2 | YAML rule files (name, type, category, severity, description, condition) with a typed condition DSL over event header and payload (==, !=, <, >, STARTS_WITH, ENDS_WITH, CONTAINS, IN, AND/OR/NOT, is_some()) | yes | yes | json, plaintext, syslog | container, image, user | no | Deployment 4: upstream publishes release binaries (pulsard-<arch>[-static], pulsar-<arch>[-static], pulsar-install.sh) and the release workflow pushes ghcr.io/exein-io/pulsar:<tag> built from .github/docker/Dockerfile with the default config and rules baked in; the quickstart is 2 commands (install script, `pulsard`), and the image only needs the usual eBPF privileges and mounts plus /var/lib/docker for container enrichment. No Helm chart or manifest upstream. Rule customization 4: 47 default YAML rule files in rules/ (Elastic detection-rules based) loaded recursively from /var/lib/pulsar/rules; the DSL is declarative and typed but has no regex, no process ancestry and only per-event fields. hot_reload is true because the rules-engine on_config_change hook rebuilds the engine from disk when its configuration is changed at runtime through `pulsar config` / the engine API (no file watcher); this was removed after 0.10.1. Output quality 4: threat-logger prints threat events as JSON (`output_format=json`) with header (image, pid, parent_pid, uid, gid, container id/name/image/image_digest/layers, threat source/description/extra) and the typed payload; the rule name is threat.description and extra holds category, severity, description and condition. No ATT&CK ids (only a category), no ancestry beyond parent_pid, timestamps are serialized as secs/nanos since epoch. |

### Measured operational metrics

Measured per deployment: time from container start to readiness, alert and log volume over the deployment lifetime (container logs plus alerts file), share of alerts attributed to a scenario run and share of alerts carrying a container id or name. Rubric scores repeated for comparison.

| Tool | Profile | Deployment score | Output quality score | Time to ready | Alerts / min | Log lines / min | Log volume MiB | Attributed alerts | Alerts with container identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pulsar | default | 4 | 4 | 0.011s | 0.01 | 4,688 | 231.34 | 0.0% | 0.0% |
| pulsar | tuned | 4 | 4 | — | 0.00 | 0.00 | — | — | — |

## Matched rules

| Tool | Profile | Scenario | Rules |
| --- | --- | --- | --- |

## Failures

### Failed tools

| Tool | Status | Error |
| --- | --- | --- |
| pulsar | partial | default: MaxRetryError: HTTPSConnectionPool(host='127.0.0.1', port=37723): Max retries exceeded with url: /apis/apps/v1/namespaces/ebpf-bench/deployments/attacker?propagationPolicy=Foreground (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)'))) |

### Log overflow

Deployments whose log or alerts stream exceeded `max_log_lines` / `max_log_bytes`: lines after the cap were dropped, so alerts emitted after it are missing and detection results are a lower bound.

None.

### Scenario executions with a non-zero exit code

None.

### Scenario cleanups with a non-zero exit code

None.
