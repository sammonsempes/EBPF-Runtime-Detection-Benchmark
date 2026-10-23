# Kunai

- Upstream: https://github.com/kunai-project/kunai (GPL-3.0)
- Pinned version: **v0.6.2** (2025-11-12), the latest stable release. `v0.7.0-rc.1` (2026-03-11) is a pre-release and the
  `main` branch is `0.7.0-rc.1`; its event schema differs (for example `data.ancestors` becomes a JSON array), so the
  0.6 documentation (https://why.kunai.rocks, `kunai-doc/versioned_docs/version-0.6.0`) and the `v0.6.2` sources are the
  reference for everything below.

## Deployment

Kunai is distributed as a static musl binary, not as a container image. `Dockerfile` downloads the official asset and
verifies it against the SHA-256 digest GitHub reports for that asset:

| arch  | asset URL | sha256 |
|-------|-----------|--------|
| amd64 | https://github.com/kunai-project/kunai/releases/download/v0.6.2/kunai-amd64 | `cfcd7ee3594e1136290ef3327f1b5bfe550af0cda4fdf5cea46645254b3daba3` |
| arm64 | https://github.com/kunai-project/kunai/releases/download/v0.6.2/kunai-aarch64 | `fb14ac760c460dee7d43ee938a66e6f9ad5dba85571bf95ff24482ab8744aaf0` |

The release also ships `.asc` signatures and a `sha512.txt`. Build args: `KUNAI_VERSION`, `KUNAI_SHA256_AMD64`,
`KUNAI_SHA256_ARM64` (change all of them together), `TARGETARCH` (set by BuildKit).

The adapter (`runner/bench/adapters/kunai.py`) builds `ebpf-bench/kunai:0.6.2` from this directory and runs
`kunai run -c /etc/kunai/config.yaml` in a privileged container with host PID, network and cgroup namespaces and:

| host | container | mode |
|------|-----------|------|
| `tools/kunai/<profile>/` | `/etc/kunai` | ro |
| `/sys/kernel/debug` | `/sys/kernel/debug` | rw |
| `/sys/kernel/btf` | `/sys/kernel/btf` | ro |
| `/sys/fs/bpf` | `/sys/fs/bpf` | rw |

`/proc` is not bind mounted: with `pid: host` the container procfs already shows host processes, which is what Kunai
reads for process tables, executable hashing and `/proc/<pid>/root`.

Readiness: Kunai logs at WARN level by default (no info line without `-v`), so the ready signal is the `start` event
(id 1101) it always prints on stdout, even when rules filter everything else:
`"source":"kunai","id":1101,"name":"start"`. It is piped into the event pipeline before the probes are attached and
printed by the single-threaded event loop once the loader yields; a few events right after it may still be missed.

## Profiles

- `default/config.yaml`: the upstream default configuration of 0.6.2 (`Config::default()`, what `kunai config --dump`
  prints): output to `/dev/stdout`, every event enabled except `read`, `write` and `write_close`, **no rules, no IoCs, no
  YARA**. Kunai ships no detection rule in its repository or release (community rules live in the separate
  `kunai-project/community-rules` repository and are not installed by default, see the `community` profile). With no rule loaded, Kunai prints
  every telemetry event and none carries a `detection` section, so this profile honestly reports zero detections. It also
  produces a large volume of logs, which is the upstream default behavior.
- `tuned/config.yaml` + `tuned/rules.yaml`: same configuration with `write_close` enabled and `scanner.rules` pointing to
  `rules.yaml`, 40-odd detection rules written for the behaviors of the scenario catalog (reverse shells, interpreter
  spawned shells, tmpfs execution, downloads to tmpfs, cron/systemd/authorized_keys persistence, account creation,
  kernel modules, setuid, permission changes on account files, nsenter/mount/chroot escapes, history and log clearing,
  masquerading, memfd execution, shadow and credential file access, container API and discovery, system discovery, port
  scans, HTTP upload, miners, secure deletion). They match on executable paths, command lines, file paths and
  destination ports only, never on benchmark markers or scenario file names. Once rules are loaded Kunai only prints
  events matching a detection (severity >= `min_severity`, 0 here) or a filter, plus `start` and `event_loss`.
- `enforce/config.yaml` + `enforce/rules.yaml`: the tuned profile with `actions: [ kill ]` added to the rules that only
  match malicious behaviors. Rules that could match what benign scenarios need stay detection-only: `exec.from.tmpfs`,
  `download.to.tmpfs`, `chmod.exec.in.tmpfs` (a compiled or downloaded binary in `/tmp`), `defense_evasion.logs.clear`
  and `defense_evasion.logs.delete` (log rotation), `discovery.container.environment` and `discovery.system.information`
  (admin commands). Same rule set and severities as tuned, so detection results are comparable.
- `community/config.yaml` + `community/rules/`: the default configuration with `scanner.rules` set to the
  `/etc/kunai/rules` directory, which holds the upstream community rules verbatim (see below). No rule of ours.

## Community profile

- Source: https://github.com/kunai-project/community-rules, the rule repository of the Kunai GitHub organization
  ("Community-driven detection rules for Kunai"), not installed by Kunai. Rules live on one branch per Kunai version
  (`kunai-v0.4`, `kunai-v0.5`; `main` holds only the README). There is no `kunai-v0.6` branch, so the profile uses the
  head of `kunai-v0.5`, commit `9a2e1640781b6562eecbe8767a4cf6e6c638283a` (2025-01-29, "add: rule CI/CD workflow").
- Compatibility with 0.6.2: the repository CI runs `kunai test -r ./rules` with the latest `v0.5.x` tag, i.e. it loads
  the repository root as a rule directory. Kunai 0.6.2 loads a `scanner.rules` directory the same way
  (`compile_kunai_rules` in `kunai/src/bin/main.rs`): `.yaml`/`.yml` files as Gene templates first, then `.kun`,
  `.kunai`, `.gen`, `.gene` files in sorted order, so `00-dependencies.kun` is loaded before the rules that depend on it.
  The release notes of 0.6.0 to 0.6.2 list no rule format change, every event name used exists in 0.6.2 (only
  `task_sched`, unused here, was removed) and the fields used (`.data.ancestors` as a `|` separated string,
  `.data.exe.error`, `.data.mapped.error`, `.data.target.exe.path`, `.info.task.flags`, `.info.task.zombie`,
  `.info.host.container.type`, `.data.socket.domain`) exist in the v0.6.2 event structs. The 0.7 schema (ancestors as an
  array) would break `dep.run.tmpfs`, `dep.webservers` and `run.memfd`.
- Files (`community/sources.txt`, sha256 pinned, fetched by the `community-rules` compose service):
  `00-dependencies.kun`, `50-detections.kun`, `60-low-detections.kun`, `90-heuristics.kun`, `templates.yaml`, in
  `community/rules/`. The CI workflow, `.vscode` settings and test traces are not fetched.
- License: the repository has no `LICENSE` file and GitHub reports no license for it; the files are used unmodified
  and attributed to their author (`qjerome`, Kunai maintainer).
- Content: 22 detection rules and 7 dependency rules (`dep.*`, never printed on their own), plus 4 templates
  (`tmpfs-dir`, `important-dir`, `systemd-dir`, `kthread-names`). They target malware tradecraft seen in perfctl,
  BPFDoor and similar Linux samples: piped crontab, stopping/disabling auditd or AppArmor, shared objects or executables
  in tmpfs, memfd execution, one-liner droppers, timestomping with `touch -r`, kills of systemd or sshd, self-deleting
  executables, executables or shared objects deleted right after use, kernel thread masquerading, raw socket sniffing,
  webshell commands under web servers, chmod/chown/cp/touch on system directories and every `mprotect_exec` event
  (severity 5). Low severity rules (2 to 5) are designed to stack up: severities of matching rules are summed (cap 10).
- Behavior: rules are loaded, so Kunai only prints detections (`min_severity: 0`, so every match) plus `start` and
  `event_loss`. The default configuration keeps `write` and `write_close` disabled, so `dep.exe.dir`,
  `dep.config.dir` and `run.tmpfs.write.exe.dir` can never match in this profile; enabling those events would be a
  change of ours to the default configuration, which the profile excludes.

## Response (enforce profile)

Kunai 0.6.2 supports two rule actions, `kill` and `scan-files` (`kunai config --list-actions`). For a detection rule
with `kill`, the userland event loop sends `SIGKILL` to `info.task.pid` once the event has been read from the eBPF ring
buffer, reordered, enriched, scanned and printed (`handle_actions` in `kunai/src/bin/main.rs`). The kernel operation
that produced the event has already completed: this is an **asynchronous, after-the-fact response, not prevention**.
A process killed after `execve` may already have done its work, a file written to `/etc/cron.d` stays on disk, and
the killed task can be the scenario shell itself when the matching operation is a shell builtin (for example a
redirection into `authorized_keys`). Kill is skipped for kunai itself and for tasks already killed, and silently
ignored on filter rules.

Identifying an enforcement: the alert `raw.detection.actions` contains `"kill"` (union of the actions of the matching
rules). This is the configured action, not its outcome; the outcome is only logged on stderr at WARN level
(`sending SIGKILL to PID=<pid>`, or an error when the kill fails), which `parse` does not turn into an alert.

## Alerts

Alerts are read from the container stdout (one JSON event per line). An event is an alert when it has a `detection`
object (rule or IoC match) and `info.event.source == "kunai"`. Telemetry events, filter-only events (`filter` without
`detection`), the `start` event and stderr log lines return `None`.

| Alert field | Kunai field |
|-------------|-------------|
| `rule` | sorted `detection.rules` joined with `,` (or `ioc:<value>` for IoC-only matches) |
| `severity` | `detection.severity` (0-10, summed over matching rules, capped at 10) |
| `event_at` | `info.utc_time` (RFC 3339, nanoseconds) |
| `container_name` | `info.host.container.name` |
| `container_id` | `info.host.container.name` when it looks like a hex container id |
| `process` | `data.exe.path`, else `info.task.name` |
| `command_line` | `data.command_line` |
| `raw` | the whole event |

Container identification: Kunai emits `info.host.container` only when the task mount namespace differs from its own,
and the `name` is the UTS nodename of the task (`task->nsproxy->uts_ns->name.nodename`), i.e. the container hostname.
Docker sets it to the first 12 characters of the container id unless a hostname is configured, which is why it is
also mapped to `container_id` when it is hexadecimal. `type` (`docker`, `lxc`, `podman`, `firejail`) is a heuristic
and may be null.

## Fixtures

`runner/tests/fixtures/kunai/` contains no line captured from a running Kunai: upstream has no JSON sample in its
repository (no tests, examples or fixtures). The lines are assembled from the upstream 0.6 documentation examples and
the `v0.6.2` serialization structs (`kunai/src/events.rs`: `UserEvent { data, detection, filter, info }`,
`Detection`, `Filter`, `EventInfo`):

- `data` of `execve`, `connect` and `start` events: `kunai-doc/versioned_docs/version-0.6.0/events/execve.md`,
  `events/connect.md`, `events/start.md`;
- `info.host`, `info.task`, `info.parent_task`: `events/generalities.md` (the event pages replace them with `"..."`);
- `detection` (`mimic.kthread`, tags, attack, severity 10): `advanced/rule_configuration.md`;
- the IoC detection (`iocs` + severity), the filter-only event (`include.all.but.noisy` from the same page) and the
  reverse shell event with a hexadecimal hostname are built from the structs with documented values, to exercise IoC
  matches, filter events and container id mapping;
- `enforce.jsonl`: the reverse shell detection with `detection.actions: ["kill"]` (field from the v0.6.2 `Detection`
  struct);
- `logs.txt`: env_logger lines using messages from `kunai/src/bin/main.rs` (including the kill log) and malformed lines.

## Known limitations

- No container id, image or Kubernetes metadata: attribution relies on the hostname and on `BENCH_MARKER` in command
  lines. A victim started with a custom hostname is matched only when that hostname equals the container name.
- `read`, `write` and `write_close` are off by default; the tuned profile enables only `write_close`, so pure reads of
  files outside `/etc` (for example `~/.aws/credentials`) are only seen through command lines, and shell redirections
  inside a script (`: > /var/log/x`) are invisible.
- Shell builtins (`history -c`, `echo >`) never produce events.
- The default profile prints every event of the host, which inflates log volume and the measured overhead.
- Kunai refuses to start if another instance is running (pid file), and hardened mode is not used.
