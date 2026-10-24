# Falco

- Version: **0.45.0** (latest release in `falco/CHANGELOG.md`, released 2026-09-21). Image `docker.io/falcosecurity/falco:0.45.0`.
- Bundled rules: `falco_rules.yaml` from **falco-rules 5.2.0** (`cmake/modules/rules.cmake`, CHANGELOG entry "update falco rules to version 5.2.0"), installed by the package in `/etc/falco/falco_rules.yaml`.
- Container metadata: container plugin 0.7.5 (`CMakeLists.txt`), enabled by the packaged `/etc/falco/config.d/falco.container_plugin.yaml`.
- License: Apache-2.0.

## Deployment in this benchmark

One privileged container (host PID and network, from `ContainerSpec` defaults) running `/usr/bin/falco` from the official image, with:

| Host path | Container path | Why |
| --- | --- | --- |
| `tools/falco/<profile>/` | `/etc/falco/bench` (ro) | profile configuration and rules |
| `tools/falco/<profile>/falco.bench.yaml` | `/etc/falco/config.d/zz-bench.yaml` (ro) | configuration drop-in |
| `/var/run/docker.sock` | `/host/var/run/docker.sock` | container plugin (Docker engine) |
| `/proc` | `/host/proc` (ro) | process table under `HOST_ROOT=/host` |
| `/etc` | `/host/etc` (ro) | host information, as in the image usage label |

The image keeps its own upstream `/etc/falco/falco.yaml` (the 0.45.0 `falco.yaml`, unmodified) and its `config.d` files (container plugin, ISO 8601 time). The profile is applied as a `config.d` drop-in, the mechanism used by upstream `docker/docker-compose/docker-compose.yaml`. The drop-in only sets output and driver options: `json_output: true` (with output, output_fields and tags properties), unbuffered stdout output, syslog output and syslog logging disabled (no syslog socket in the container), and `engine.kind: modern_ebpf` (already the upstream default, pinned explicitly). No driver loader or kernel headers are needed; the kernel must expose BTF.

## Profiles

- `default`: upstream `falco.yaml` plus upstream stable rules `falco_rules.yaml` (falco-rules 5.2.0) as shipped in the pinned image, plus the drop-in above. The rules file is not vendored in this repository because the falcosecurity/rules submodule is not part of the local upstream clone; the image is the source of truth for that exact version.
- `tuned`: `default` plus `rules.d/custom_rules.yaml`, appended to `rules_files` by the drop-in (config_files `append` strategy). The tuned rules reuse upstream macros (`spawned_process`, `open_write`, `open_read`, `container`, `shell_binaries`) and target behaviours of the scenario catalog: shell outbound connections, shells spawned by interpreters, execution from temporary directories, cron/systemd/authorized_keys/account database writes, account management commands, kernel module load attempts, setuid bits and sensitive chmod, host disk mounts and namespace changes from containers, history and log tampering, daemon-name masquerading, credential and service account token reads with generic tools, container runtime socket access, container and system discovery commands, network scanners, HTTP uploads with curl/wget, miner pool ports and miner process names. They contain no benchmark tokens and were checked against the benign scenarios (`cat /etc/os-release`, logrotate with gzip, tar backups, gcc, python http.server with curl, dpkg/apt-cache).
- `community`: `default` plus the upstream incubating and sandbox rule files, verbatim, appended to `rules_files` exactly like `tuned` (see below). No rule written by us.
- No `enforce` profile: Falco has no in-kernel blocking (see `operational.yaml`, `response`).

## Community profile

- Source: [falcosecurity/rules](https://github.com/falcosecurity/rules), the Falco project's own rules repository, which publishes one file per maturity level (`rules/falco_rules.yaml` stable, `rules/falco-incubating_rules.yaml`, `rules/falco-sandbox_rules.yaml`). Only the stable file is bundled in the Falco package; the other two are optional rule sets maintained by the same project. A `deprecated` maturity level exists but has no rule file in `rules/` at this commit.
- Commit: `80880bd59906ee9619dedc6cd60f6603252052f6`, the commit of tag `falco-rules-5.2.0`, i.e. the same release as the stable rules bundled with Falco 0.45.0 (`cmake/modules/rules.cmake`, `FALCOSECURITY_RULES_FALCO_VERSION falco-rules-5.2.0`).
- License: Apache-2.0 (SPDX header of each file, Copyright The Falco Authors).
- Files, downloaded by the `community-rules` service from `sources.txt` (URLs pinned to the commit, sha256 verified) into `rules.d/`, unmodified:

| File | Maturity tag | Rules | Enabled by the file | Disabled by the file (`enabled: false`) |
| --- | --- | --- | --- | --- |
| `rules.d/falco-incubating_rules.yaml` | `maturity_incubating` | 31 | 31 | 0 |
| `rules.d/falco-sandbox_rules.yaml` | `maturity_sandbox` | 39 | 25 | 14 |

- Loading: the drop-in appends `/etc/falco/bench/rules.d` to the image's `rules_files`; Falco loads `/etc/falco/falco_rules.yaml` (stable, from the image) first, then the directory in lexical order (incubating, then sandbox). Rules disabled upstream stay disabled (they are disabled because they need environment-specific tuning, e.g. allow lists or GPU workloads), as a user enabling these files would get them.
- Requirements: both files declare `required_engine_version: 0.57.0` (Falco 0.45.0 has engine 0.65.0, `userspace/engine/falco_engine_version.h`) and `required_plugin_versions: container >= 0.4.0` (the image ships container plugin 0.7.5). They only use the `syscall` source with container plugin fields (`container.*`, `k8s.ns.name`, `k8s.pod.name`); no k8saudit, cloudtrail or other plugin is needed, so no file was dropped.
- Like the stable file, each file redefines shared macros and lists (`open_write`, `container`, `shell_binaries`, `docker_binaries`...); the last definition loaded wins for all files, including stable rules. The incubating and sandbox copies are identical to each other; they were not diffed against the stable file in the image, so a differing stable definition would be replaced by the community one (upstream intends the files to be loaded together in this order).
- Expected noise (not tuned, by design): broad auditing rules such as `Write below etc`, `Write below root`, `Change thread namespace`, `Unexpected UDP Traffic`, `Launch Privileged Container`, `Launch Excessively Capable Container`, `Launch Sensitive Mount Container` and `Container Access to Host Sensitive Paths` can fire on benign scenarios, on the benchmark's own containers and possibly on the Falco container itself (it is privileged and reads `/host/proc`). `Exfiltrating Artifacts via Kubernetes Control Plane` fires on any non-interactive `tar` started directly by the container runtime.
- Not validated with `falco --dry-run` against the image in this environment (same caveat as `tuned`); a load error would show at startup in the container logs before the ready pattern.

## Alert collection

Falco writes alerts as JSON lines on stdout and its own logs on stderr; the runner reads both from the container logs. `Adapter.parse` keeps only JSON objects with `rule` and `priority`, drops `source: internal` messages (for example `Falco internal: syscall event drop`) and maps:

| Alert | Falco JSON |
| --- | --- |
| `rule` | `rule` |
| `severity` | `priority`, lowercased |
| `event_at` | `time` (event time, ISO 8601 ns) |
| `container_id` / `container_name` | `output_fields["container.id"]` / `["container.name"]` (`host` becomes null) |
| `process` | `output_fields["proc.name"]`, else `proc.exepath` |
| `command_line` | `output_fields["proc.cmdline"]` |
| `raw` | the whole JSON alert |

Every rule match is an alert. `ready_pattern` is `Opening 'syscall' source with modern BPF probe`, logged by `userspace/falco/app/actions/helpers_inspector.cpp` right before the probe is opened.

## Kubernetes mode

Falco is installed with the `falcosecurity/falco` chart 9.1.0. The image's `config.d/falco.container_plugin.yaml` and the chart both load the container plugin, which makes Falco abort (`found another plugin with name container`); the values mount an `emptyDir` over `/etc/falco/config.d` so only the chart's container plugin configuration (containerd sockets) is loaded, and the benchmark drop-in is still mounted at `/etc/falco/config.d/zz-bench.yaml`. With that fix, the shadow-read scenario was detected and attributed to the victim pod on kind under WSL2. Details: `deploy/kubernetes/README.md`, "Validated on kind / WSL2".

## Fixtures

`runner/tests/fixtures/falco/alerts.jsonl`:

- log lines 1 to 4 are copied verbatim from `chart/falco/README.gotmpl`; lines 5 and 6 are the messages of `helpers_inspector.cpp` with the ISO 8601 prefix produced by `userspace/engine/logger.cpp`;
- the JSON alerts follow the exact structure built by `userspace/engine/formats.cpp` (keys `hostname`, `output`, `output_fields`, `priority`, `rule`, `source`, `tags`, `time`, sorted as nlohmann::json dumps them), with rule names, priorities and output fields taken from `e2e_tests/evtgen_suite/fileless_execution_via_memfd_create.yaml` and `clear_log_activities.yaml`; the internal message follows `falco_outputs.cpp` (`handle_msg`) and `event_drops.cpp`.

The local upstream tree contains no verbatim JSON alert line, so field values (ids, times, command lines) are illustrative; they should be replaced by lines captured from a real run.

## Known limitations

- `ready_pattern` fires just before the modern BPF probe is attached; events from the first few hundred milliseconds may be missed.
- `rule_matching: first` (upstream default) means only the first matching rule fires per event; a stable rule can shadow a tuned rule on the same event (the alert is still attributed).
- Container names come from the container plugin through the Docker socket; if the socket is unavailable only `container.id` is known.
- The tuned rules and the drop-in were not validated with `falco --dry-run` against the real image in this environment; run `docker run --rm -v $PWD/tools/falco/tuned:/etc/falco/bench -v $PWD/tools/falco/tuned/falco.bench.yaml:/etc/falco/config.d/zz-bench.yaml falcosecurity/falco:0.45.0 falco --dry-run` before the first benchmark.
- Rules relying on command-line options (`proc.args contains`) can be bypassed by reordering options; they are behaviour heuristics.
