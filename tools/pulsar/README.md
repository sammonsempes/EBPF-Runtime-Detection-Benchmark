# Pulsar

- Upstream: https://github.com/exein-io/pulsar (userspace Apache-2.0, eBPF probes GPL-2.0)
- Pinned version: **v0.10.1** (2026-09-30), the latest stable release. The cloned `main` branch is unreleased and
  breaks the configuration format (INI to TOML, `/var/lib/pulsar` to `/etc/pulsar`, YAML rules to TOML), so the `v0.10.1`
  tag is the reference: INI configuration at `/var/lib/pulsar/pulsar.ini`, YAML rules below `/var/lib/pulsar/rules`.

## Deployment

Pulsar has an official image, so there is no Dockerfile here: the release workflow (`.github/workflows/release.yaml`)
pushes `ghcr.io/exein-io/pulsar:<tag>` built from `.github/docker/Dockerfile` (debian, `pulsard` and `pulsar` binaries,
`.github/docker/pulsar.ini` and the repository `rules/` copied to `/var/lib/pulsar`, entrypoint `pulsard`). The
benchmark uses `ghcr.io/exein-io/pulsar:v0.10.1` (GitHub packages showed digest
`sha256:d59aac7906e8c8c611aed5cbd1565d08936e800683d9d38f96842d3b86816d18` for it when this was written). The equivalent
release binaries are `https://github.com/exein-io/pulsar/releases/download/v0.10.1/pulsard-x86_64` (and `-static`,
`-aarch64`, `-riscv64gc` variants, plus `pulsar-*` CLI and `pulsar-install.sh`).

The adapter (`runner/bench/adapters/pulsar.py`) runs `pulsard --config-file /etc/bench/pulsar/pulsar.ini` in a
privileged container with host PID, network and cgroup namespaces and:

| host | container | mode |
|------|-----------|------|
| `tools/pulsar/<profile>/` | `/etc/bench/pulsar` | ro |
| `tools/pulsar/<profile>/rules/` | `/var/lib/pulsar/rules/bench-<profile>` | ro |
| `/sys/kernel/debug` | `/sys/kernel/debug` | rw |
| `/sys/kernel/btf` | `/sys/kernel/btf` | ro |
| `/sys/fs/bpf` | `/sys/fs/bpf` | rw (maps are pinned) |
| `/var/lib/docker` | `/var/lib/docker` | ro |

`/var/lib/docker` is required for container enrichment: Pulsar reads
`/var/lib/docker/containers/<id>/config.v2.json` and the image layers to fill `header.container`. Hosts with another
Docker data root need this mount adapted. `/proc` comes from the host PID namespace.

Readiness: `pulsard` logs at INFO level on stderr and prints `Starting module <name>` for each enabled module
(`src/pulsard/daemon.rs`); nothing is logged once the probes are attached. The ready pattern is
`Starting module rules-engine`, so a short delay is still needed before the first scenario for the probes to load.

## Profiles

- `default/`: `pulsar.ini` is the upstream Docker image configuration (`.github/docker/pulsar.ini`: desktop and SMTP
  notifiers disabled) plus three threat-logger output settings (`console=true`, `syslog=false`, `output_format=json`) so
  alerts are printed as JSON on stdout instead of plaintext and nothing is sent to a missing syslog socket. Those
  settings do not change detection. Rules are the **upstream default rules baked in the image**
  (`/var/lib/pulsar/rules`, identical to `rules/` at tag `v0.10.1`, 47 files listed in
  `default/rules/upstream-rules.txt`). They are not copied in this repository: the image content is the exact shipped
  version, and the `main` branch rules already differ from it. `default/rules/` holds no rule; it only keeps the same
  mount layout for both profiles.
- `tuned/`: same `pulsar.ini`, the upstream default rules from the image, plus `tuned/rules/tuned-rules.yaml`, loaded
  because the rules-engine globs `**/*.yaml` recursively below `/var/lib/pulsar/rules`. The extra rules cover the
  scenario catalog behaviors the default set misses (shell network connections, inline interpreter code, tmpfs
  execution, systemd/authorized_keys/crontab persistence, account creation, setuid, permission changes on account
  files, nsenter/mount escapes, memfd execution, masquerading, log truncation commands, credential and service account
  token access, container socket and discovery, system discovery, port scans, HTTP upload, miners, secure deletion).
  They only use executable paths, argv elements, file paths, open flags and ports, never benchmark markers.

## Response

Pulsar 0.10.1 cannot respond to or block a threat. Its modules are process-monitor, file-system-monitor,
network-monitor, rules-engine, threat-logger, desktop-notifier and smtp-notifier; a rule has no action field
(`UserRule { name, type, condition, category, severity, description }`), and a match only produces a threat event
that is logged or notified. The adapter therefore keeps the two profiles `default` and `tuned`, and the benchmark has
no `enforce` profile for Pulsar.

## Alerts

`threat-logger` only prints events whose `header.threat` is set (rule engine matches). Each stdout line is the whole
`Event` serialized with serde (`{"header": {...}, "payload": {"type": ..., "content": {...}}}`); stderr carries the
env_logger lines. An alert is a JSON line with a non-null `header.threat`. The plaintext format
(`[time THREAT image (pid)] [source - rule] payload`) is also parsed as a fallback.

| Alert field | Pulsar field |
|-------------|--------------|
| `rule` | `header.threat.description` (the rule name set by the rules-engine) |
| `severity` | `header.threat.extra.severity` (`low`, `medium`, `high`, `critical`) |
| `event_at` | `header.timestamp` (`secs_since_epoch` + `nanos_since_epoch`) |
| `container_id` | `header.container.id` (full Docker id) |
| `container_name` | `header.container.name` |
| `process` | `header.image` |
| `command_line` | `payload.content.argv` joined with spaces for `Exec` payloads |
| `raw` | the whole event |

## Fixtures

Upstream contains no JSON threat sample (no `*.json`/`*.jsonl` in the tree, the threat-logger README shows none). The
only real sample is the plaintext line of the repository `README.md` Quickstart, copied verbatim in
`runner/tests/fixtures/pulsar/plaintext.txt` (first line). The JSON lines of `alerts.jsonl` are built strictly from the
`v0.10.1` serialization structs: `crates/pulsar-core/src/event.rs` (`Event`, `Header`, `Threat`, `Payload` with
`#[serde(tag = "type", content = "content")]`, `FileFlags(i32)`, `Argv(Vec<String>)`, `SystemTime` serde layout),
`crates/bpf-common/src/containers/mod.rs` (`ContainerInfo { id, name, image, image_digest, layers }`),
`crates/modules/rules-engine/src/engine.rs` (`Metadata { category, description, severity, condition }` sent as
`threat.extra`, rule name as `threat.description`, `source = "rules-engine"`) and
`crates/pulsar-core/src/pdk/module_context.rs` (`send_threat_derived` copies the header and payload of the matched
event). Rule names and conditions come from upstream rules (`README.md`, `rules/container-rules`,
`rules/execution/read_sensitive_file`); ids, pids and timestamps are illustrative. `logs.txt` uses the
`src/pulsard/daemon.rs` and `module_manager.rs` log messages with the env_logger default format, and the plaintext
`EVENT` format of `Event`'s `Display` implementation.

## Known limitations

- The rule DSL has no regex and argv `CONTAINS` matches whole arguments only, so command line patterns such as
  `/dev/tcp/...` inside `bash -c` strings cannot be expressed; the tuned profile detects the resulting connection instead.
- Events carry no process ancestry (only `parent_pid`) and no ATT&CK ids (only a category).
- Container enrichment depends on reading the Docker data root; without it `header.container` is null and attribution
  falls back to `BENCH_MARKER`.
- Upstream default rules are taken from the image, so this repository cannot show their diff; the `.new` / local-edit
  logic of the installer does not apply.
