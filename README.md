# eBPF Runtime Detection Benchmark

An open, reproducible framework for evaluating eBPF-based runtime threat detection tools on Linux and Kubernetes.

The benchmark runs a standardized set of attack scenarios, mapped to [MITRE ATT&CK](https://attack.mitre.org/) techniques, against each tool and measures how well and at what cost it detects them, and, for tools that can block, how well it prevents them.

The goal is to provide transparent, vendor-neutral results that help security teams choose the right tool for their environment. All scenarios, configurations, and raw results are included so anyone can reproduce or extend the benchmark.

## Ranking

Based only on the measurements of the native Linux runs of 2026-10-25 (Debian 13, kernel 6.12, BPF-LSM enabled), Docker mode. Each tool gets a rank from 1 (best) to 6 per criterion, ties share the average rank, and the overall rank is the unweighted mean. Reweight the criteria to match your own priorities: every value comes from the tables in [Results](#results).

| Criterion | Measure used | Falco | Kunai | Tetragon | KubeArmor | Tracee | Pulsar |
|---|---|---|---|---|---|---|---|
| Detection, tuned | recall, then FP rate (tuned profile) | 2.5 | 2.5 | **1** | 5 | 4 | 6 |
| Detection, out of the box | recall minus FP rate (default profile) | **1.5** | 4.5 | **1.5** | 6 | 3 | 4.5 |
| Prevention | attacks prevented by the enforce profile | 5 | 3 | **1.5** | **1.5** | 5 | 5 |
| Syscall latency overhead | median over syscall metrics (tuned) | **1** | 2 | 6 | 5 | 4 | 3 |
| Tool CPU and memory | rank of CPU plus rank of memory (tuned; Tetragon CPU taken during the `exec` workload, 38%, since its median hides the cost) | 2.5 | **1** | 4.5 | 2.5 | 4.5 | 6 |
| Alert latency | median, tuned | **2** | 4 | 5 | 6 | **2** | **2** |
| Container identity | share of alerts with a container id or name (tuned) | 2.5 | 2.5 | 4 | **1** | 5 | 6 |
| **Overall** | mean rank | **2.4** | **2.8** | **3.4** | **3.9** | **3.9** | **4.6** |

**1. Falco** (mean rank 2.4)
- Best: lowest syscall latency overhead (+8.9% median, `exec` throughput unchanged), alerts in about 1 ms, best out-of-the-box coverage (45.8% recall, tied with Tetragon), container identity on 99.9% of alerts, ready in under 0.2 s, identical results in Kubernetes.
- Worst: cannot block anything; the tuned profile flags 2 of 6 benign scenarios (33.3% of benign runs); the community rule set raises recall to 79.2% but flags 4 of 6 benign scenarios (66.7%); 0.6 core of CPU during the workloads with the tuned rules.

**2. Kunai** (mean rank 2.8)
- Best: smallest footprint (0.06 core, 92 MiB), 100% recall with the tuned rules, low overhead outside `read` (+14.1% median syscall latency), container identity on 99.9% of alerts, same recall in Kubernetes.
- Worst: ships no detection rules, so the default profile detects nothing; its kill action runs after the event and prevented only 3 of 24 attacks (0 of 23 in Kubernetes); unscoped kill rules killed `dockerd` during this benchmark (see [Response effectiveness](#response-effectiveness)); `read` latency +129%.

**3. Tetragon** (mean rank 3.4)
- Best: the only tool with 100% tuned recall at the lowest false positive rate of that group (16.7%), synchronous blocking that prevented 22 of 24 attacks with no collateral damage (Docker mode), same recall in Kubernetes on a native node.
- Worst: the highest syscall latency overhead with tuned or enforce policies (+72% to +84% median, `read` p50 +2,500%, `exec` throughput −43%), host-wide events (1,163 alerts per minute in tuned, 75% attributed to the victims), 7 to 23 s to become ready, alerts read from a file about 0.1 s after the event.

**4. KubeArmor** (mean rank 3.9)
- Best: BPF-LSM blocking prevented 22 of 24 attacks with no collateral damage, the lowest false positive rate of all tuned profiles (1 benign run of 30), container identity on 100% of alerts.
- Worst: the default policies flag every benign scenario (100%), tuned recall of 87.5%, below Falco, Kunai, Tetragon and Tracee, `openat` latency +197% and `connect` +74%, 430,000 to 580,000 telemetry lines per minute (4.5 to 6.2 GiB per deployment), no alert at all on kind even with a native kernel.

**5. Tracee** (mean rank 3.9)
- Best: alerts in about 1 ms, 91.7% tuned recall, the same recall in Kubernetes.
- Worst: the highest CPU after Pulsar (1.5 to 1.6 cores), `openat` latency +106% to +174%, only 20.8% recall out of the box, container identity on 64% to 73% of alerts.

**6. Pulsar** (mean rank 4.6)
- Best: alerts in about 1 ms, ready in 0.03 s.
- Worst: the heaviest tool by far (2.7 to 2.9 cores, 4.5 to 5.2 GiB), 62.5% tuned recall and 16.7% out of the box, no container identity on any alert (attribution relies on the scenario marker), `openat` +119% and `connect` +121%, and in Kubernetes it exhausted the host's memory (28.6 GiB) within three minutes.

### When to use which

These recommendations follow from the measured numbers only.

| Need | Tool | Why, from the results |
|---|---|---|
| Detection on production hosts where performance matters | **Falco** | lowest overhead, millisecond alerts, best default rules, same behavior in Docker and Kubernetes |
| Blocking attacks inside containers, with detection that also runs in Kubernetes | **Tetragon** (enforce) | 22/24 prevented synchronously, 0 benign scenario broken (measured in Docker mode; enforce was not run on kind), same detection in kind on a native node; budget the syscall latency cost |
| Blocking on Docker hosts with BPF-LSM, with the fewest false positives | **KubeArmor** (enforce) | 22/24 prevented, lowest tuned false positive rate; plan for its log volume and do not rely on its default policies |
| Small or resource-constrained hosts, with a team that writes its own rules | **Kunai** | smallest CPU and memory, 100% tuned recall; treat its kill as response, not prevention, and scope kill rules to containers |
| Fast alerting when CPU is available | **Tracee** | millisecond alerts and 91.7% tuned recall, at about 1.5 cores |
| — | **Pulsar** | no measured criterion where it leads, except alert latency shared with Falco and Tracee; it could not complete a Kubernetes run |

The tuned and enforce profiles were written knowing the scenario catalog ([Limitations](#limitations)): the default profiles and the overhead numbers are the least biased part of this ranking.

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
| [Falco](https://github.com/falcosecurity/falco) | 0.45.0 | default, tuned, community | no |
| [Tetragon](https://github.com/cilium/tetragon) | 1.7.1 | default, tuned, enforce, community | yes (Sigkill) |
| [Tracee](https://github.com/aquasecurity/tracee) | 0.24.1 | default, tuned | no |
| [KubeArmor](https://github.com/kubearmor/KubeArmor) | 1.7.5 | default, tuned, enforce, community | yes (BPF-LSM) |
| [Kunai](https://github.com/kunai-project/kunai) | 0.6.2 | default, tuned, enforce, community | kill after the event (asynchronous) |
| [Pulsar](https://github.com/exein-io/pulsar) | 0.10.1 | default, tuned | no |

- **default**: what an operator gets out of the box (upstream configuration and rules). Kunai ships no detection rules, so its default profile detects nothing by design.
- **tuned**: default plus rules written for the behaviors of the scenario catalog. They target behaviors, never benchmark-specific tokens, but they were written knowing the scenarios: see [Limitations](#limitations).
- **enforce**: tuned rules with the tool's blocking action on malicious behaviors only.
- **community**: default plus the optional rule set published by the project itself, verbatim, where one exists.

Each tool's deployment, profiles and alert definition are documented in `tools/<tool>/README.md`.

## Results

Native Linux host, 2026-10-25. Three Docker-mode runs and two Kubernetes-mode runs on the same machine, each with its own baseline and control phase:

| Run | Mode | Tools and profiles | Report |
|---|---|---|---|
| `20261025T090806Z` | Docker | Falco, Tetragon, Tracee (all profiles); Kunai default and tuned | [report](results/20261025T090806Z/report.md) |
| `20261025T131132Z` | Docker | KubeArmor, Kunai, Pulsar (all profiles), rerun with a higher log cap, see below | [report](results/20261025T131132Z/report.md) |
| `20261025T160602Z` | Kubernetes (kind) | default and tuned of every Helm-installed tool, all Kunai profiles | [report](results/20261025T160602Z/report.md) |
| `20261025T200250Z` | Kubernetes (kind) | Pulsar, in a fresh runner (exhausted host memory, not scored) | [report](results/20261025T200250Z/report.md) |

| Host | Value |
|---|---|
| Kernel | 6.12.105+deb13-amd64, BTF, LSMs `lockdown,capability,landlock,yama,apparmor,tomoyo,bpf,ipe,ima,evm` |
| OS | Debian GNU/Linux 13 (trixie), Docker 26.1.5, cgroup v2 |
| CPU / memory | 8 CPUs, 30.9 GiB |
| Catalog | 24 attack scenarios, 6 benign scenarios, 5 repetitions each |
| Control | every scenario achieved its effect 5/5 times without any tool in both Docker runs: all 30 scenarios are valid |

The main run `20261025T090806Z` also contains KubeArmor, Kunai enforce and Kunai community rows. They are superseded by the rerun:

- **KubeArmor (4 profiles)** exceeded the runner's log cap (5 million lines or 2 GiB per stream) during the overhead workloads, before any scenario ran: its telemetry reached 200,000 lines per minute on this host, and every alert was dropped (0 alerts). The rerun sets `max_log_lines: 15000000` and `max_log_bytes: 16106127360`; no KubeArmor stream overflowed. Prevention, measured by `check.sh` and not by alerts, was already 22/24 in the main run.
- **Kunai enforce killed `dockerd`.** The tuned rule `defense_evasion.history.delete` with `actions: [ kill ]` matched `dockerd` deleting a `.bash_history` file under `/var/lib/docker/overlay2` while removing a container; the daemon restarted and the runner lost its connection, so the run ended before Kunai community and Pulsar. The enforce rules now only kill processes whose ancestors include `containerd-shim` and never `runc`, `containerd`, `dockerd` or `kubelet` (`tools/kunai/enforce/rules.yaml`); the 33 scenario rules still match. The rerun used these rules.

### Detection coverage

Recall: attack scenarios detected in a majority of the 5 repetitions, out of 24. FP rate: benign runs with at least one attributed alert, out of 30. Latency: median time from the scenario's `BENCH_ACTION` timestamp to the first attributed alert.

| Tool | Profile | Recall | FP rate | Median latency |
|---|---|---|---|---|
| Tetragon | tuned | 100.0% | 16.7% | 0.103 s |
| Tetragon | enforce | 100.0% | 16.7% | 0.108 s |
| Falco | tuned | 100.0% | 33.3% | 0.001 s |
| Kunai | tuned | 100.0% | 33.3% | 0.078 s |
| Kunai | enforce | 100.0% | 33.3% | 0.085 s |
| Tracee | tuned | 91.7% | 33.3% | 0.001 s |
| KubeArmor | default | 91.7% | 100.0% | 0.087 s |
| KubeArmor | tuned | 87.5% | 3.3% | 0.107 s |
| Pulsar | tuned | 62.5% | 33.3% | 0.001 s |
| KubeArmor | enforce † | 58.3% | 16.7% | 0.114 s |
| Falco | default | 45.8% | 16.7% | 0.001 s |
| Tetragon | default | 45.8% | 16.7% | 0.107 s |
| Tracee | default | 20.8% | 16.7% | 0.005 s |
| Pulsar | default | 16.7% | 16.7% | 0.000 s |
| Kunai | default | 0.0% | 0.0% | — |

† KubeArmor enforce blocks most attacks before the audited operation happens, so fewer of them produce an alert: its recall is not comparable with detection-only profiles.

- **KubeArmor default** reaches 91.7% only because the upstream `harden-shell-history-mod` policy fires on every shell started in the container; the same rule flags all 6 benign scenarios.
- **False positive rules**: Falco `Drop and execute new binary in container` (compile) and, in tuned, `Log File Deleted or Truncated` (log rotation); Tetragon `file-monitoring-filtered` (log rotation); Tracee `New executable dropped` (compile) and, in tuned, `detect-container-discovery`; Kunai `discovery.system.information` and `download.to.tmpfs`; Pulsar `Create files below /root`; KubeArmor tuned `tuned-container-escape` once. Details per scenario are in each report.
- **Pulsar** alerts carry no container identity (0%), so they are only attributed through the scenario marker in the command line. Its tuned recall rose from 16.7% on WSL2 to 62.5% here.
- Out of the box, Falco and Tetragon cover 11 of 24 techniques, Tracee 5, Pulsar 4, Kunai none.

### Community rule sets

| Tool | Community source | Recall | FP rate | Median latency |
|---|---|---|---|---|
| Falco | `falcosecurity/rules` 5.2.0: incubating and sandbox | 79.2% (default 45.8%) | 66.7% (default 16.7%) | 0.001 s |
| KubeArmor | `kubearmor/policy-templates`: 47 MITRE container templates, in Audit | 91.7% (default 91.7%) | 100.0% (default 100.0%) | 0.097 s |
| Kunai | `kunai-project/community-rules`, branch `kunai-v0.5` | 20.8% (default 0.0%) | 6.7% | 0.089 s |
| Tetragon | `cilium/tetragon` v1.7.1 examples: 6 observability policies | 100.0% (default 45.8%) | 100.0% (default 16.7%) | 0.095 s |

Tetragon's 100% is generic telemetry (`process-exec-elf-begin` reports every exec, 1.3 million alerts in one deployment), not detection. Sources, pinned commits and exclusions are in `tools/<tool>/community/sources.txt` and each tool README.

### Response effectiveness

Prevention: attack scenarios whose effect, checked by the scenario's `check.sh`, was not achieved in a majority of repetitions, while it was achieved in every control run. Collateral damage: benign scenarios broken by enforcement.

| Tool | Mechanism | Prevention | Not prevented | Collateral damage | Median response latency | Enforcement verified |
|---|---|---|---|---|---|---|
| Tetragon | Sigkill at the hook | **91.7% (22/24)** | T1082, T1613 (observe-only by design) | 0 | 0.114 s | not checkable |
| KubeArmor | BPF-LSM | **91.7% (22/24)** | T1048 (HTTP exfiltration), T1070.002 (log truncation) | 0 | 0.105 s | yes |
| Kunai | kill after the event | 12.5% (3/24) | 21 scenarios | 0 | 0.086 s | yes |
| Falco, Tracee, Pulsar | detection only | — | — | — | — | — |

- **KubeArmor** blocks synchronously through BPF-LSM on this kernel; on WSL2 it could not block at all. 50 of the 120 attack runs were blocked without any attributed alert.
- **Kunai** sends SIGKILL from user space once the event is read: it prevented masquerading, data destruction and the miner, and none of the 21 other scenarios, whose effect landed before the kill.
- **Tetragon** uses Sigkill only: this kernel has no `CONFIG_BPF_KPROBE_OVERRIDE`, so the Override action is unavailable.

### Performance overhead

Overhead is relative to the baseline of the same run without any tool; positive always means worse. Tool CPU is in percent of one core, median over all workload samples.

| Tool | Profile | Tool CPU | Tool memory | `exec` throughput | `openat` p50 | `read` p50 | `connect` p50 | Syscall latency (median of metrics) |
|---|---|---|---|---|---|---|---|---|
| Falco | default | 30% | 124 MiB | +3.5% | +36.4% | +7.0% | +10.7% | +8.2% |
| Falco | tuned | 60% | 127 MiB | +0.3% | +32.4% | +5.6% | +10.8% | +8.9% |
| Tetragon | default | 0.1% ‡ | 436 MiB | +31.5% | -2.3% | +1,123% | -1.7% | -1.8% |
| Tetragon | tuned | 0.1% ‡ | 371 MiB | +43.2% | +55.6% | +2,611% | +42.4% | +83.6% |
| Tetragon | enforce | 0.1% ‡ | 394 MiB | +43.7% | +56.9% | +2,509% | +48.6% | +71.7% |
| Tracee | default | 145% | 153 MiB | -2.2% | +105.6% | +26.8% | +37.3% | +29.3% |
| Tracee | tuned | 164% | 159 MiB | +3.3% | +174.4% | +57.7% | +46.3% | +48.9% |
| KubeArmor | default | 21% | 372 MiB | +1.0% | +204.7% | +56.6% | +78.7% | +63.9% |
| KubeArmor | tuned | 24% | 310 MiB | +0.7% | +197.4% | +51.0% | +73.8% | +58.2% |
| KubeArmor | enforce | 25% | 320 MiB | +1.6% | +203.2% | +51.7% | +56.9% | +53.9% |
| Kunai | default | 7% | 93 MiB | -1.1% | +13.7% | +126.2% | +18.5% | +13.5% |
| Kunai | tuned | 6% | 92 MiB | +4.8% | +14.5% | +129.0% | +41.9% | +14.1% |
| Kunai | enforce | 6% | 94 MiB | +5.8% | +16.1% | +140.0% | +40.4% | +16.9% |
| Pulsar | default | 267% | 5,370 MiB | +6.6% | +119.6% | +16.6% | +121.4% | +27.2% |
| Pulsar | tuned | 291% | 4,571 MiB | +12.8% | +118.9% | +17.9% | +120.8% | +36.2% |

‡ Tetragon's agent uses about 38% of a core during the `exec` workload and almost nothing during the `syscall` and `fileio` workloads: its probes run in kernel context and their cost is charged to the monitored process, which is where the syscall latency overhead appears.

- **Falco** is the cheapest overall. **Kunai** has the smallest agent but its file hooks double `read` latency. **Tetragon** is nearly free with its default policy except on `read`, and costly once the tuned file and process policies are loaded.
- **KubeArmor** writes 430,000 to 580,000 telemetry lines per minute to stdout (4.5 to 6.2 GiB per deployment), collected by Docker's logging driver; part of its overhead is that pipeline. **Kunai default** prints every event too (150,000 lines per minute).
- **Pulsar** uses 8 to 18 times more memory than on the WSL2 host (0.3 to 0.6 GiB there).
- Per-metric numbers, including `fileio` and p99, are in each report.

### Operational aspects

Rubric scores (1–5) are defined in [docs/methodology.md](docs/methodology.md) and justified with upstream facts in each `tools/<tool>/operational.yaml`. The measured columns are for the tuned profile.

| Tool | Deployment | Rule customization | Output quality | Time to ready | Alerts / min | Alerts with container identity |
|---|---|---|---|---|---|---|
| Falco | 5 | 5 | 5 | 0.07 s | 128 | 99.9% |
| Tetragon | 5 | 4 | 4 | 22.7 s | 1,163 | 87.9% |
| Tracee | 4 | 3 | 4 | 2.3 s | 155 | 73.2% |
| KubeArmor | 3 | 4 | 4 | 2.7 s | 35 | 100.0% |
| Kunai | 3 | 4 | 4 | 0.86 s | 79 | 99.9% |
| Pulsar | 4 | 4 | 4 | 0.03 s | 186 | 0.0% |

### Integration issues

Fixes that were needed to run each pinned release, kept in the repository:

- **Pulsar 0.10.1**: the official image `ghcr.io/exein-io/pulsar:v0.10.1` does not start (`GLIBC_2.38 not found`); `tools/pulsar/Dockerfile` reuses its binary and default rules on `ubuntu:24.04`.
- **Tetragon 1.7.1**: Override needs `CONFIG_BPF_KPROBE_OVERRIDE`, which neither the WSL2 nor this Debian kernel enables, so the enforce profile uses Sigkill only; a policy cannot mix kprobes and tracepoints.
- **Tracee 0.24.1**: policy data filters only support equality, and the health endpoint did not answer with the documented configuration; readiness uses the `tracee_info` event.
- **Kunai 0.6.2**: fails without `/sys/class/dmi/id/product_uuid` (`failed to read host_uuid`); the configurations set a fixed `host_uuid`. `kunai replay` executes the `kill` action of matching rules against the PIDs of the replayed events: strip the actions before replaying enforce rules.
- **KubeArmor chart v1.7.5**: the controller pod never starts (`container has runAsNonRoot and image will run as root`); the agent DaemonSet runs.

### Kubernetes mode on kind

Runs `20261025T160602Z` and `20261025T200250Z`, same host, single-node kind cluster (Kubernetes 1.33.1, containerd 2.1.1), tools installed with their upstream Helm charts or a DaemonSet, metrics-server installed, tool images pulled into the node before the run so time to ready excludes the network. Details: [deploy/kubernetes/README.md](deploy/kubernetes/README.md#validated-on-kind--native-linux).

| Tool | Profile | Recall | FP rate | Median latency | Recall / FP rate in Docker mode |
|---|---|---|---|---|---|
| Tetragon | tuned | 100.0% | 16.7% | 0.555 s | 100.0% / 16.7% |
| Falco | tuned | 100.0% | 33.3% | 0.002 s | 100.0% / 33.3% |
| Kunai | tuned | 100.0% | 33.3% | 0.087 s | 100.0% / 33.3% |
| Kunai | enforce | 100.0% | 33.3% | 0.089 s | 100.0% / 33.3% |
| Tracee | tuned | 91.7% | 33.3% | 0.002 s | 91.7% / 33.3% |
| Falco | default | 45.8% | 16.7% | 0.002 s | 45.8% / 16.7% |
| Tetragon | default | 45.8% | 16.7% | 0.510 s | 45.8% / 16.7% |
| Kunai | community | 20.8% | 0.0% | 0.079 s | 20.8% / 6.7% |
| Tracee | default | 20.8% | 16.7% | 0.006 s | 20.8% / 16.7% |
| KubeArmor | default, tuned | 0.0% | 0.0% | — | 91.7% / 100.0%, 87.5% / 3.3% |
| Kunai | default | 0.0% | 0.0% | — | 0.0% / 0.0% |

- **Detection matches Docker mode** for Falco, Tetragon, Tracee and Kunai: same recall in every profile they share, and the same false positive rate except Kunai community (0.0% against 6.7%). Tetragon now runs in Kubernetes: the WSL2 blocker (no host procfs in the initial PID namespace) does not exist on a native kernel.
- **KubeArmor produces no alert in kind on a native kernel either**: it registers every container with `pidns=0/mntns=0`, so the WSL2 explanation was wrong; the cause is the nested container runtime of kind. Its controller also never starts with chart v1.7.5 (`container has runAsNonRoot and image will run as root`).
- **Kunai enforce prevented nothing in Kubernetes** (0/23): every kill landed after the effect. Its kills only hit the victim pods (62 in `bench-victim`, 4 in `bench-victim-priv` in the first 37 scenarios checked), never a node process.
- **Profiles not run in Kubernetes**: the Helm-based tools only have values for `default` and `tuned`. Tetragon enforce was deliberately not added: in kind the node's `kubelet` and `containerd` are not in the host mount namespace, so the `host_ns` exclusion of its Sigkill policies would not protect them (its `/var/log` rule would hit pod log cleanup).
- **t1046-network-scan is invalid in Kubernetes mode** (0/5 in the control runs): the attacker Service only exposes 3 ports and the scan times out. Recall still counts it out of 24.
- **Overhead in kind is noisier than in Docker mode** (Tetragon default shows −38% latency, which is not plausible): use the Docker-mode overhead table. KubeArmor uses 4.8 to 5.7 GiB in kind, against about 0.3 GiB in Docker mode.
- **Pulsar exhausted the host's memory in Kubernetes mode on a native kernel too.** It ran in a separate runner (the first one held 18 GiB of log lines after Kunai default, which exceeded even the 15 million line cap without effect on a profile that has no rules). Three minutes after it started, during the second `fileio` overhead workload, `pulsard` reached 28.6 GiB RSS (15 GiB median per metrics-server), the host ran out of memory for about 8 hours and the Kubernetes API stopped answering. This is the step where it crashed the WSL2 VM, so the cause is Pulsar in this deployment, not WSL2. Pulsar default is not scored in Kubernetes and Pulsar tuned was not started.

### Previous run on WSL2

The first published run (`20261022T204058Z`, plus `20261023T082958Z`, `20261023T093007Z` and the kind run `20261024T114807Z`) used a WSL2 kernel without BPF-LSM or kprobe override. Its reports stay in `results/`. On that host KubeArmor could not block, Tetragon could not run in Kubernetes, and Pulsar crashed the VM in Kubernetes mode; Falco, Tetragon, Tracee and Kunai had the same recall and false positive rates as here, while KubeArmor tuned (83.3%) and Pulsar tuned (16.7%) detected less.

## Limitations

- **Single host.** Results come from one machine (8 CPUs, Debian 13, kernel 6.12). Absolute overhead numbers depend on the CPU and on the event rate: on this host Falco and Tracee use several times more CPU than on the WSL2 host of the first run, and Pulsar 8 to 18 times more memory.
- **Several runs.** KubeArmor, Kunai enforce and community, and Pulsar come from the rerun `20261025T131132Z`, the other Docker numbers from `20261025T090806Z`. Both runs have their own baseline and control on the same idle host, and the overhead percentages are always computed against the baseline of the same run.
- **Tuning bias.** The tuned and enforce profiles were written by the benchmark authors knowing the scenario catalog. They show what each rule language can express, not what a team would reach on unknown attacks. The default profiles are the unbiased comparison.
- **Scenario realism.** Scenarios are short, simulated behaviors run in containers; they do not reproduce multi-stage intrusions or evasion.
- **Attribution.** Alerts are credited to a scenario through container identity or the scenario marker. Tools that report no container identity, like Pulsar, are under-credited.
- **Raw alert files are not published.** `alerts/*.jsonl` contain host-wide events of the machine that ran the benchmark, and some weigh several GiB. `runs.jsonl`, `workloads.jsonl`, `metadata.json`, `score.json` (with the rules matched per run) and `report.md` are published; re-running the benchmark regenerates the alert files.
- **Kubernetes mode** ran on kind, a single node inside a container. KubeArmor produces no alert there, the enforce and community profiles of the Helm-based tools are not available, Pulsar exhausts the host's memory, and overhead numbers are noisier than in Docker mode. A multi-node cluster on bare nodes would be the next step.

See [docs/methodology.md](docs/methodology.md#threats-to-validity) for the full list.

## Quick start

Requirements: a Linux host with a BTF-enabled kernel (5.8+), Docker Engine with Compose v2. Run on a dedicated machine or VM: the scenarios modify the victim containers and some tools run privileged.

```bash
docker compose build          # runner, victim, attacker, Kunai and Pulsar images
docker compose up tests       # unit tests
docker compose up -d bench    # full benchmark described in bench.yaml (several hours)
docker compose logs -f bench
```

`bench.yaml` keeps up to 15 million log lines (15 GiB) per tool stream in memory: KubeArmor and Kunai default produce millions of telemetry lines per deployment, and a lower cap drops their alerts. Plan for about 20 GiB of RAM for the runner on a fast host. Blocking profiles act on the whole host: Kunai and Tetragon enforce rules are scoped to container processes, keep that scope when you add rules.

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
