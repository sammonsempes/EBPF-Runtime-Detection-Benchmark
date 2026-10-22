from __future__ import annotations

import hashlib
import re
import socket
import time
import uuid
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import yaml

from bench.adapters import get_adapter
from bench.adapters.base import ToolAdapter
from bench.config import CONTROL_PROFILE, CONTROL_TOOL, ENFORCE_PROFILES, Config
from bench.docker_backend import ATTACKER_NAME, Backend, ContainerRef, ExecResult, LineBuffer, Targets
from bench.metrics import run_workload
from bench.model import Alert, Scenario, ScenarioRun
from bench.serialization import append_jsonl, hostname_pattern, redact, to_jsonable, write_json, write_jsonl

MAX_OUTPUT_CHARS = 65536
FILE_DRAIN_TIMEOUT = 10.0
CHECK_SCRIPT = "check.sh"
CLEANUP_SCRIPT = "cleanup.sh"
CHECK_TIMEOUT = 30.0
CLEANUP_TIMEOUT = 60.0
ACTION_PATTERN = re.compile(r"^BENCH_ACTION\s+(\d+(?:\.\d+)?)\s*$", re.MULTILINE)
ENFORCEMENT_LABEL = "enforce"


@dataclass
class Deployment:
    tool: str
    profile: str
    status: str = "pending"
    error: str | None = None
    errors: list[str] = field(default_factory=list)
    container_id: str | None = None
    started_at: float | None = None
    container_started_at: float | None = None
    ready_at: float | None = None
    time_to_ready: float | None = None
    workloads_started_at: float | None = None
    workloads_ended_at: float | None = None
    scenarios_started_at: float | None = None
    scenarios_ended_at: float | None = None
    ended_at: float | None = None
    runs: int = 0
    log_lines: int = 0
    log_bytes: int = 0
    alerts_file_lines: int = 0
    alerts_file_bytes: int = 0
    alerts: int = 0
    parse_errors: int = 0
    cleanup_failures: int = 0
    enforce: bool = False
    enforcement_verified: bool | None = None
    enforcement_alerts: int = 0
    confirmed_enforcements: list[float] = field(default_factory=list)


def describe(error: BaseException) -> str:
    return f"{type(error).__name__}: {error}"


def parse_action_at(output: str) -> float | None:
    match = ACTION_PATTERN.search(output or "")
    return float(match.group(1)) if match else None


def byte_count(lines: list[tuple[float, str]]) -> int:
    return sum(len(line.encode("utf-8", errors="replace")) + 1 for _, line in lines)


def hash_directory(path: Path) -> str | None:
    if not path.is_dir():
        return None
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(file.relative_to(path).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()


def load_operational(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return {"error": describe(error)}


def new_run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


class Orchestrator:
    def __init__(
        self,
        config: Config,
        scenarios: list[Scenario],
        backend: Backend,
        repo_root: Path,
        host_repo_root: Path | None = None,
        adapter_factory: Callable[[str], ToolAdapter] = get_adapter,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
        log: Callable[[str], None] | None = None,
        finalize: bool = True,
        run_id: str | None = None,
        hostname: str | None = None,
    ) -> None:
        self.config = config
        self.hostname_pattern = hostname_pattern(socket.gethostname() if hostname is None else hostname)
        self.scenarios = list(scenarios)
        self.backend = backend
        self.repo_root = Path(repo_root)
        self.host_repo_root = Path(host_repo_root) if host_repo_root else self.repo_root
        self.adapter_factory = adapter_factory
        self.sleep = sleep
        self.clock = clock
        self.log = log or (lambda message: print(message, flush=True))
        self.finalize = finalize
        self.run_id = run_id or new_run_id()
        results_root = config.results_dir if config.results_dir.is_absolute() else self.repo_root / config.results_dir
        self.results_dir = results_root / self.run_id
        self.adapters: dict[str, ToolAdapter] = {}
        self.deployments: dict[str, Deployment] = {}
        self.control: Deployment | None = None
        self.metadata: dict[str, Any] = {}

    @property
    def runs_path(self) -> Path:
        return self.results_dir / "runs.jsonl"

    @property
    def workloads_path(self) -> Path:
        return self.results_dir / "workloads.jsonl"

    def alerts_path(self, key: str) -> Path:
        return self.results_dir / "alerts" / f"{key}.jsonl"

    def host_path(self, local: Path) -> Path:
        try:
            return self.host_repo_root / local.resolve().relative_to(self.repo_root.resolve())
        except ValueError:
            return local

    def run(self) -> Path:
        (self.results_dir / "alerts").mkdir(parents=True, exist_ok=True)
        (self.results_dir / "raw").mkdir(parents=True, exist_ok=True)
        self.runs_path.touch()
        self.workloads_path.touch()
        self._load_adapters()
        self.metadata = self._initial_metadata()
        self._write_metadata()
        self.log(f"run {self.run_id}: results in {self.results_dir}")
        status = "failed"
        try:
            self.backend.prepare()
            if self.config.overhead.enabled:
                self._run_baseline()
            if self.control is not None:
                self._run_control()
            for tool in self.config.tools:
                for profile in self.config.profiles:
                    self._run_deployment(f"{tool}-{profile}")
            status = "completed"
        except KeyboardInterrupt:
            status = "interrupted"
            raise
        finally:
            self._safely("cleanup", self.backend.cleanup)
            self.metadata["status"] = status
            self.metadata["finished_at"] = self.clock()
            self._write_metadata()
        if self.finalize:
            self._finalize()
        return self.results_dir

    def _safely(self, label: str, action: Callable[..., Any], *args: Any) -> None:
        try:
            action(*args)
        except Exception as error:
            self.log(f"{label} failed: {describe(error)}")

    def _load_adapters(self) -> None:
        for tool in self.config.tools:
            error = None
            try:
                adapter = self.adapter_factory(tool)
                self.adapters[tool] = adapter
            except Exception as failure:
                adapter = None
                error = f"adapter unavailable: {describe(failure)}"
            for profile in self.config.profiles:
                deployment = Deployment(tool=tool, profile=profile)
                if adapter is None:
                    deployment.status = "failed"
                    deployment.error = error
                elif profile not in adapter.profiles:
                    deployment.status = "skipped"
                    deployment.error = f"profile {profile!r} not supported by adapter"
                deployment.enforce = profile in ENFORCE_PROFILES
                self.deployments[f"{tool}-{profile}"] = deployment
        if self.config.control_scenarios and self.scenarios:
            self.control = Deployment(tool=CONTROL_TOOL, profile=CONTROL_PROFILE)

    def _tool_metadata(self, tool: str) -> dict[str, Any]:
        adapter = self.adapters.get(tool)
        hashes = {}
        for profile in self.config.profiles:
            directory = (
                adapter.config_dir(self.repo_root, profile) if adapter else self.repo_root / "tools" / tool / profile
            )
            hashes[profile] = hash_directory(directory)
        return {
            "name": getattr(adapter, "name", tool),
            "version": getattr(adapter, "version", None),
            "profiles": [profile for profile in self.config.profiles if profile in getattr(adapter, "profiles", ())],
            "supported_profiles": list(getattr(adapter, "profiles", ())),
            "config_sha256": hashes,
            "available": adapter is not None,
        }

    def _host_info(self) -> dict[str, Any]:
        try:
            return self.backend.host_info()
        except Exception as error:
            return {"error": describe(error)}

    def _initial_metadata(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": "running",
            "started_at": self.clock(),
            "finished_at": None,
            "host": self._host_info(),
            "host_repo_root": str(self.host_repo_root),
            "config": self.config.as_dict(),
            "bench_yaml": self.config.source,
            "tools": {tool: self._tool_metadata(tool) for tool in self.config.tools},
            "operational": {
                tool: load_operational(self.repo_root / "tools" / tool / "operational.yaml")
                for tool in self.config.tools
                if (self.repo_root / "tools" / tool / "operational.yaml").is_file()
            },
            "scenarios": [to_jsonable(scenario) for scenario in self.scenarios],
            "baseline": {"status": "pending" if self.config.overhead.enabled else "skipped", "errors": []},
            "control": {"status": "skipped"},
            "deployments": {},
        }

    def _tool_status(self, tool: str) -> tuple[str, str | None]:
        deployments = [item for item in self.deployments.values() if item.tool == tool and item.status != "skipped"]
        statuses = {item.status for item in deployments}
        errors = [f"{item.profile}: {item.error}" for item in deployments if item.error]
        if not deployments or statuses <= {"pending"}:
            return "pending", None
        if statuses <= {"failed"}:
            return "failed", "; ".join(errors) or None
        if statuses <= {"completed"}:
            return "ok", None
        if statuses & {"failed", "error", "interrupted"}:
            return "partial", "; ".join(errors) or None
        return "running", None

    def _write_metadata(self) -> None:
        self.metadata["deployments"] = {key: asdict(value) for key, value in self.deployments.items()}
        if self.control is not None:
            self.metadata["control"] = asdict(self.control)
        for tool, info in self.metadata.get("tools", {}).items():
            info["status"], info["error"] = self._tool_status(tool)
        write_json(self.results_dir / "metadata.json", self.metadata)

    def _workloads(
        self,
        host: ContainerRef,
        errors: list[str],
        tool: str | None = None,
        profile: str | None = None,
        tool_container: ContainerRef | None = None,
    ) -> None:
        overhead = self.config.overhead
        for repetition in range(overhead.repetitions):
            for name in overhead.workloads:
                label = f"{tool or 'baseline'}{'-' + profile if profile else ''}"
                self.log(f"[{label}] workload {name} #{repetition}")
                try:
                    result = run_workload(
                        self.backend,
                        host,
                        name,
                        overhead.duration_seconds,
                        repetition,
                        tool=tool,
                        profile=profile,
                        tool_container=tool_container,
                    )
                except Exception as error:
                    errors.append(f"workload {name} #{repetition}: {describe(error)}")
                    self.log(f"[{label}] workload {name} #{repetition} failed: {describe(error)}")
                    continue
                append_jsonl(self.workloads_path, [result])

    def _run_baseline(self) -> None:
        baseline = self.metadata["baseline"]
        if not self.config.overhead.workloads:
            baseline["status"] = "skipped"
            return
        baseline.update(status="running", started_at=self.clock())
        host = None
        try:
            host = self.backend.start_workload_host()
            self._workloads(host, baseline["errors"])
            baseline["status"] = "completed"
        except Exception as error:
            baseline.update(status="failed", error=describe(error))
            self.log(f"baseline failed: {describe(error)}")
        finally:
            if host is not None:
                self._safely("stop workload host", self.backend.stop, host)
            baseline["ended_at"] = self.clock()
            self._write_metadata()

    def _run_control(self) -> None:
        control = self.control
        started: list[ContainerRef] = []
        control.status = "running"
        control.started_at = self.clock()
        self._write_metadata()
        self.log(f"[{CONTROL_TOOL}-{CONTROL_PROFILE}] control scenarios without any tool")
        try:
            self._run_scenarios(control, started)
            control.status = "completed"
        except Exception as error:
            control.status = "failed"
            control.error = describe(error)
            self.log(f"control failed: {control.error}")
        finally:
            if control.status == "running":
                control.status = "interrupted"
            for ref in reversed(started):
                self._safely(f"stop {ref.name}", self.backend.stop, ref)
            control.ended_at = self.clock()
            self._write_metadata()

    def _run_deployment(self, key: str) -> None:
        deployment = self.deployments[key]
        if deployment.status != "pending":
            self.log(f"[{key}] {deployment.status}: {deployment.error}")
            return
        adapter = self.adapters[deployment.tool]
        raw_dir = self.results_dir / "raw" / key
        raw_dir.mkdir(parents=True, exist_ok=True)
        started: list[ContainerRef] = []
        tool_ref: ContainerRef | None = None
        logs: LineBuffer | None = None
        alerts_source: LineBuffer | None = None
        self.log(f"[{key}] starting {deployment.tool} {getattr(adapter, 'version', '')}")
        try:
            try:
                spec = adapter.container_spec(self.host_repo_root, deployment.profile, self.host_path(raw_dir))
                deployment.started_at = self.clock()
                tool_ref = self.backend.start_tool(deployment.tool, deployment.profile, spec)
                deployment.container_started_at = self.clock()
                deployment.container_id = tool_ref.id
                logs = self.backend.follow_logs(tool_ref)
                if spec.alerts_file:
                    alerts_source = self.backend.tail_file(raw_dir / spec.alerts_file)
                self.backend.wait_ready(tool_ref, logs, spec.ready_pattern, spec.startup_timeout)
                if spec.ready_url:
                    elapsed = self.clock() - deployment.container_started_at
                    self.backend.wait_url(tool_ref, logs, spec.ready_url, max(spec.startup_timeout - elapsed, 1.0))
                deployment.ready_at = self.clock()
                deployment.time_to_ready = deployment.ready_at - deployment.container_started_at
                if spec.settle_seconds > 0:
                    self.sleep(spec.settle_seconds)
            except Exception as error:
                deployment.status = "failed"
                deployment.error = describe(error)
                self.log(f"[{key}] failed to start: {deployment.error}")
                return
            deployment.status = "running"
            self._write_metadata()
            try:
                if self.config.overhead.enabled and self.config.overhead.workloads:
                    try:
                        self._run_tool_workloads(deployment, tool_ref, started)
                    except Exception as error:
                        deployment.errors.append(f"workloads: {describe(error)}")
                        self.log(f"[{key}] workloads failed: {describe(error)}")
                self._run_scenarios(deployment, started)
                deployment.status = "completed"
            except Exception as error:
                deployment.status = "error"
                deployment.error = describe(error)
                self.log(f"[{key}] aborted: {deployment.error}")
        finally:
            if deployment.status == "running":
                deployment.status = "interrupted"
            for ref in reversed(started):
                self._safely(f"stop {ref.name}", self.backend.stop, ref)
            if tool_ref is not None:
                self._safely(f"stop {tool_ref.name}", self.backend.stop, tool_ref)
            if alerts_source is not None:
                alerts_source.finish(FILE_DRAIN_TIMEOUT)
            deployment.ended_at = self.clock()
            self._collect(deployment, adapter, raw_dir, logs, alerts_source)
            self._write_metadata()

    def _run_tool_workloads(self, deployment: Deployment, tool_ref: ContainerRef, started: list[ContainerRef]) -> None:
        deployment.workloads_started_at = self.clock()
        host = self.backend.start_workload_host()
        started.append(host)
        self._workloads(host, deployment.errors, deployment.tool, deployment.profile, tool_ref)
        started.remove(host)
        self._safely("stop workload host", self.backend.stop, host)
        deployment.workloads_ended_at = self.clock()

    def _run_scenarios(self, deployment: Deployment, started: list[ContainerRef]) -> None:
        if not self.scenarios:
            return
        targets = self.backend.start_targets()
        started.extend([targets.attacker, targets.victim, targets.victim_privileged])
        deployment.scenarios_started_at = self.clock()
        total = self.config.repetitions * len(self.scenarios)
        done = 0
        for repetition in range(self.config.repetitions):
            for scenario in self.scenarios:
                run = self._run_scenario(deployment, scenario, repetition, targets)
                append_jsonl(self.runs_path, [run])
                deployment.runs += 1
                done += 1
                if done < total:
                    self.sleep(self.config.idle_seconds)
        self.sleep(self.config.grace_seconds)
        deployment.scenarios_ended_at = self.clock()

    def _exec_script(
        self, victim: ContainerRef, scenario: Scenario, script: str, environment: dict[str, str], timeout: float
    ) -> ExecResult:
        command = ["sh", f"/scenarios/{scenario.id}/{script}"]
        try:
            return self.backend.exec(victim, command, environment, timeout)
        except Exception as error:
            now = self.clock()
            return ExecResult(-1, f"[bench] exec failed: {describe(error)}", now, now)

    def _has_script(self, scenario: Scenario, script: str) -> bool:
        return (Path(scenario.path) / script).is_file()

    def _run_scenario(self, deployment: Deployment, scenario: Scenario, repetition: int, targets: Targets) -> ScenarioRun:
        marker = uuid.uuid4().hex[:12]
        victim = targets.victim_privileged if "privileged" in scenario.requires else targets.victim
        environment = {"BENCH_MARKER": marker, "BENCH_ATTACKER": ATTACKER_NAME}
        result = self._exec_script(victim, scenario, "run.sh", environment, scenario.timeout)
        effect_achieved = None
        check_exit_code = None
        if self._has_script(scenario, CHECK_SCRIPT):
            check = self._exec_script(victim, scenario, CHECK_SCRIPT, environment, CHECK_TIMEOUT)
            check_exit_code = check.exit_code
            effect_achieved = {0: True, 1: False}.get(check.exit_code)
        cleanup_exit_code = None
        if self._has_script(scenario, CLEANUP_SCRIPT):
            cleanup = self._exec_script(victim, scenario, CLEANUP_SCRIPT, environment, CLEANUP_TIMEOUT)
            cleanup_exit_code = cleanup.exit_code
            if cleanup.exit_code != 0:
                deployment.cleanup_failures += 1
                deployment.errors.append(
                    f"cleanup {scenario.id} #{repetition} exit={cleanup.exit_code}: {cleanup.output[-200:]}"
                )
        self.log(
            f"[{deployment.tool}-{deployment.profile}] {scenario.id} #{repetition} "
            f"exit={result.exit_code} effect={effect_achieved} {result.ended_at - result.started_at:.2f}s"
        )
        return ScenarioRun(
            scenario_id=scenario.id,
            tool=deployment.tool,
            profile=deployment.profile,
            repetition=repetition,
            marker=marker,
            victim_container_id=victim.id,
            started_at=result.started_at,
            ended_at=result.ended_at,
            exit_code=result.exit_code,
            output=result.output[-MAX_OUTPUT_CHARS:],
            action_at=parse_action_at(result.output),
            effect_achieved=effect_achieved,
            check_exit_code=check_exit_code,
            cleanup_exit_code=cleanup_exit_code,
        )

    def _collect(
        self,
        deployment: Deployment,
        adapter: ToolAdapter,
        raw_dir: Path,
        logs: LineBuffer | None,
        alerts_source: LineBuffer | None,
    ) -> None:
        log_lines = logs.lines() if logs is not None else []
        file_lines = alerts_source.lines() if alerts_source is not None else []
        deployment.log_lines = len(log_lines)
        deployment.log_bytes = byte_count(log_lines)
        deployment.alerts_file_lines = len(file_lines)
        deployment.alerts_file_bytes = byte_count(file_lines)
        with (raw_dir / "container.log").open("w", encoding="utf-8") as handle:
            for emitted_at, line in log_lines:
                handle.write(f"{emitted_at:.6f} {redact(line, self.hostname_pattern)}\n")
        source_lines = file_lines if alerts_source is not None else log_lines
        alerts: list[Alert] = []
        for emitted_at, line in source_lines:
            try:
                alert = adapter.parse(line, emitted_at)
            except Exception:
                deployment.parse_errors += 1
                continue
            if alert is None:
                continue
            if alert.action is None and self._is_enforcement(adapter, alert):
                alert = replace(alert, action=ENFORCEMENT_LABEL)
            alerts.append(alert)
        write_jsonl(
            self.alerts_path(f"{deployment.tool}-{deployment.profile}"),
            [redact(to_jsonable(alert), self.hostname_pattern) for alert in alerts],
        )
        deployment.alerts = len(alerts)
        deployment.enforcement_alerts = sum(1 for alert in alerts if alert.action is not None)
        if deployment.enforce:
            self._verify_enforcement(deployment, adapter, log_lines + file_lines)
        self.log(f"[{deployment.tool}-{deployment.profile}] {deployment.status}: {len(alerts)} alerts")

    @staticmethod
    def _is_enforcement(adapter: ToolAdapter, alert: Alert) -> bool:
        try:
            return bool(adapter.is_enforcement(alert))
        except Exception:
            return False

    def _verify_enforcement(self, deployment: Deployment, adapter: ToolAdapter, lines: list[tuple[float, str]]) -> None:
        try:
            deployment.enforcement_verified = adapter.enforcement_check([line for _, line in lines])
        except Exception as error:
            deployment.errors.append(f"enforcement_check: {describe(error)}")
        try:
            deployment.confirmed_enforcements = sorted(float(value) for value in adapter.confirmed_enforcements(lines))
        except Exception as error:
            deployment.errors.append(f"confirmed_enforcements: {describe(error)}")

    def _finalize(self) -> None:
        try:
            from bench.scoring import score_results

            score_results(self.results_dir, self.config.grace_seconds)
            self.log(f"score written to {self.results_dir / 'score.json'}")
        except Exception as error:
            self.log(f"scoring failed: {describe(error)}")
            return
        try:
            from bench.report import write_report

            self.log(f"report written to {write_report(self.results_dir)}")
        except Exception as error:
            self.log(f"report failed: {describe(error)}")
