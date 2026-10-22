from __future__ import annotations

import os
import platform
import re
import signal
import threading
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

import docker
from docker.errors import APIError, DockerException, ImageNotFound, NotFound

from bench.adapters.base import ContainerSpec

NETWORK = "bench-net"
LABEL = "ebpf-bench.role"
VICTIM_IMAGE = "ebpf-bench/victim:latest"
ATTACKER_IMAGE = "ebpf-bench/attacker:latest"
VICTIM_NAME = "bench-victim"
PRIVILEGED_VICTIM_NAME = "bench-victim-priv"
ATTACKER_NAME = "attacker"
WORKLOAD_HOST_NAME = "bench-workload"
SCENARIOS_TARGET = "/scenarios"
TIMEOUT_EXIT_CODE = 124
TOOL_STOP_TIMEOUT = 15
TARGET_STOP_TIMEOUT = 2
LOG_DRAIN_TIMEOUT = 10.0
TAIL_POLL_SECONDS = 0.2
PROC_STAT = Path("/proc/stat")
HOST_CPU_INTERVAL = 1.0
CPU_TIME_FIELDS = 8
URL_PROBE_TIMEOUT = 2.0
URL_POLL_SECONDS = 1.0
TIMESTAMP_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$")


class ToolStartError(RuntimeError):
    pass


@dataclass(frozen=True)
class ContainerRef:
    id: str
    name: str


@dataclass(frozen=True)
class Targets:
    victim: ContainerRef
    victim_privileged: ContainerRef
    attacker: ContainerRef


@dataclass(frozen=True)
class ExecResult:
    exit_code: int
    output: str
    started_at: float
    ended_at: float


class LineBuffer:
    def __init__(self) -> None:
        self._lines: list[tuple[float, str]] = []
        self._condition = threading.Condition()
        self._closed = False
        self.stop_requested = threading.Event()

    def append(self, emitted_at: float, line: str) -> None:
        with self._condition:
            self._lines.append((emitted_at, line))
            self._condition.notify_all()

    def close(self) -> None:
        with self._condition:
            self._closed = True
            self._condition.notify_all()

    @property
    def closed(self) -> bool:
        with self._condition:
            return self._closed

    def lines(self) -> list[tuple[float, str]]:
        with self._condition:
            return list(self._lines)

    def wait_for(self, pattern: str, timeout: float) -> bool:
        regex = re.compile(pattern)
        deadline = time.monotonic() + timeout
        index = 0
        with self._condition:
            while True:
                while index < len(self._lines):
                    if regex.search(self._lines[index][1]):
                        return True
                    index += 1
                remaining = deadline - time.monotonic()
                if remaining <= 0 or self._closed:
                    return False
                self._condition.wait(remaining)

    def wait_closed(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        with self._condition:
            while not self._closed:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._condition.wait(remaining)
            return True

    def finish(self, timeout: float = LOG_DRAIN_TIMEOUT) -> bool:
        self.stop_requested.set()
        return self.wait_closed(timeout)


def parse_docker_timestamp(text: str) -> float | None:
    match = TIMESTAMP_PATTERN.match(text.strip())
    if not match:
        return None
    base, digits, zone = match.groups()
    zone = "+00:00" if zone == "Z" else zone
    seconds = datetime.fromisoformat(base + zone).timestamp()
    return seconds + (float(f"0.{digits}") if digits else 0.0)


def split_timestamped(line: str) -> tuple[float, str]:
    line = line.rstrip("\r")
    head, _, rest = line.partition(" ")
    stamp = parse_docker_timestamp(head)
    if stamp is None:
        return time.time(), line
    return stamp, rest


def pump_log_stream(chunks: Iterable[bytes], buffer: LineBuffer) -> None:
    pending = b""
    try:
        for chunk in chunks:
            pending += chunk
            *complete, pending = pending.split(b"\n")
            for raw in complete:
                if raw.strip():
                    buffer.append(*split_timestamped(raw.decode("utf-8", errors="replace")))
    except Exception:
        pass
    finally:
        if pending.strip():
            buffer.append(*split_timestamped(pending.decode("utf-8", errors="replace")))
        buffer.close()


def tail_file(path: Path, clock: Callable[[], float] = time.time) -> LineBuffer:
    buffer = LineBuffer()

    def pump() -> None:
        handle = None
        pending = ""
        try:
            while True:
                stopping = buffer.stop_requested.is_set()
                if handle is None and path.is_file():
                    handle = path.open("r", encoding="utf-8", errors="replace")
                chunk = handle.read() if handle is not None else ""
                if chunk:
                    now = clock()
                    pending += chunk
                    *complete, pending = pending.split("\n")
                    for line in complete:
                        if line.strip():
                            buffer.append(now, line.rstrip("\r"))
                elif stopping:
                    break
                else:
                    time.sleep(TAIL_POLL_SECONDS)
        except Exception:
            pass
        finally:
            if pending.strip():
                buffer.append(clock(), pending.rstrip("\r"))
            if handle is not None:
                handle.close()
            buffer.close()

    threading.Thread(target=pump, name=f"tail-{path.name}", daemon=True).start()
    return buffer


def cpu_percent(stats: dict[str, Any]) -> float | None:
    current = stats.get("cpu_stats") or {}
    previous = stats.get("precpu_stats") or {}
    cpu_delta = (current.get("cpu_usage") or {}).get("total_usage", 0) - (previous.get("cpu_usage") or {}).get(
        "total_usage", 0
    )
    system_delta = current.get("system_cpu_usage", 0) - previous.get("system_cpu_usage", 0)
    if not previous.get("system_cpu_usage") or system_delta <= 0 or cpu_delta < 0:
        return None
    cpus = current.get("online_cpus") or len((current.get("cpu_usage") or {}).get("percpu_usage") or []) or 1
    return cpu_delta / system_delta * cpus * 100.0


def memory_bytes(stats: dict[str, Any]) -> float | None:
    memory = stats.get("memory_stats") or {}
    usage = memory.get("usage")
    if usage is None:
        return None
    details = memory.get("stats") or {}
    for key in ("inactive_file", "total_inactive_file", "cache"):
        if key in details:
            return float(max(usage - details[key], 0))
    return float(usage)


class StatsSampler:
    def __init__(self, source: Callable[[], Iterable[dict[str, Any]]]) -> None:
        self.cpu_percent: list[float] = []
        self.memory_bytes: list[float] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(source,), name="stats", daemon=True)
        self._thread.start()

    def _run(self, source: Callable[[], Iterable[dict[str, Any]]]) -> None:
        try:
            for sample in source():
                if self._stop.is_set():
                    break
                cpu = cpu_percent(sample)
                memory = memory_bytes(sample)
                with self._lock:
                    if cpu is not None:
                        self.cpu_percent.append(cpu)
                    if memory is not None:
                        self.memory_bytes.append(memory)
        except Exception:
            pass

    def stop(self) -> tuple[list[float], list[float]]:
        self._stop.set()
        self._thread.join(1.5)
        with self._lock:
            return list(self.cpu_percent), list(self.memory_bytes)


def read_cpu_times(path: Path = PROC_STAT) -> tuple[float, float] | None:
    try:
        first = path.read_text(encoding="utf-8").splitlines()[0]
        fields = first.split()
        if not fields or fields[0] != "cpu":
            return None
        values = [float(value) for value in fields[1 : CPU_TIME_FIELDS + 1]]
    except (OSError, IndexError, ValueError):
        return None
    if len(values) < 4:
        return None
    idle = values[3] + (values[4] if len(values) > 4 else 0.0)
    return sum(values), idle


def busy_percent(previous: tuple[float, float], current: tuple[float, float]) -> float | None:
    total = current[0] - previous[0]
    idle = current[1] - previous[1]
    if total <= 0 or idle < 0:
        return None
    return max(0.0, min(100.0, (1.0 - idle / total) * 100.0))


class HostCpuSampler:
    def __init__(
        self,
        reader: Callable[[], tuple[float, float] | None] = read_cpu_times,
        interval: float = HOST_CPU_INTERVAL,
    ) -> None:
        self.samples: list[float] = []
        self._interval = interval
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(reader,), name="host-cpu", daemon=True)
        self._thread.start()

    def _run(self, reader: Callable[[], tuple[float, float] | None]) -> None:
        try:
            previous = reader()
            while not self._stop.wait(self._interval):
                current = reader()
                if previous is not None and current is not None:
                    value = busy_percent(previous, current)
                    if value is not None:
                        with self._lock:
                            self.samples.append(value)
                previous = current
        except Exception:
            pass

    def stop(self) -> list[float]:
        self._stop.set()
        self._thread.join(self._interval + 1.0)
        with self._lock:
            return list(self.samples)


class Backend(ABC):
    def start_host_stats(self) -> HostCpuSampler | None:
        return None

    def wait_url(self, ref: ContainerRef, logs: LineBuffer, url: str, timeout: float) -> None:
        return None

    @abstractmethod
    def prepare(self) -> None: ...

    @abstractmethod
    def start_targets(self) -> Targets: ...

    @abstractmethod
    def start_workload_host(self) -> ContainerRef: ...

    @abstractmethod
    def start_tool(self, tool: str, profile: str, spec: ContainerSpec) -> ContainerRef: ...

    @abstractmethod
    def follow_logs(self, ref: ContainerRef) -> LineBuffer: ...

    @abstractmethod
    def tail_file(self, path: Path) -> LineBuffer: ...

    @abstractmethod
    def wait_ready(self, ref: ContainerRef, logs: LineBuffer, pattern: str | None, timeout: float) -> None: ...

    @abstractmethod
    def exec(self, ref: ContainerRef, command: list[str], environment: dict[str, str], timeout: float) -> ExecResult: ...

    @abstractmethod
    def start_stats(self, ref: ContainerRef) -> StatsSampler: ...

    @abstractmethod
    def stop(self, ref: ContainerRef) -> None: ...

    @abstractmethod
    def cleanup(self) -> None: ...

    @abstractmethod
    def host_info(self) -> dict[str, Any]: ...


class DockerBackend(Backend):
    def __init__(
        self,
        repo_root: Path,
        host_repo_root: Path,
        client: Any = None,
        urlopen: Callable[..., Any] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.host_repo_root = Path(host_repo_root)
        self.client = client or docker.from_env(timeout=600)
        self.urlopen = urlopen or urllib.request.build_opener(urllib.request.ProxyHandler({})).open
        self._containers: dict[str, Any] = {}
        self._stop_timeouts: dict[str, int] = {}
        self._buffers: dict[str, list[LineBuffer]] = {}

    def local_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            return self.repo_root / path
        try:
            return self.repo_root / path.relative_to(self.host_repo_root)
        except ValueError:
            return path

    def prepare(self) -> None:
        self._remove_labelled()
        if not self.client.networks.list(names=[NETWORK]):
            self.client.networks.create(NETWORK, driver="bridge", labels={LABEL: "network"})

    def _remove_labelled(self) -> None:
        for container in self.client.containers.list(all=True, filters={"label": LABEL}):
            try:
                container.remove(force=True)
            except DockerException:
                pass

    def _remove_named(self, name: str) -> None:
        try:
            self.client.containers.get(name).remove(force=True)
        except NotFound:
            pass

    def _run(self, name: str, image: str, role: str, stop_timeout: int, **kwargs: Any) -> ContainerRef:
        self._remove_named(name)
        container = self.client.containers.run(image, name=name, detach=True, labels={LABEL: role}, **kwargs)
        self._containers[container.id] = container
        self._stop_timeouts[container.id] = stop_timeout
        return ContainerRef(id=container.id, name=name)

    def _scenarios_volume(self) -> list[str]:
        return [f"{self.host_repo_root / 'scenarios'}:{SCENARIOS_TARGET}:ro"]

    def start_targets(self) -> Targets:
        attacker = self._run(
            ATTACKER_NAME,
            ATTACKER_IMAGE,
            "attacker",
            TARGET_STOP_TIMEOUT,
            hostname=ATTACKER_NAME,
            network=NETWORK,
            volumes=self._scenarios_volume(),
        )
        victim = self._run(
            VICTIM_NAME,
            VICTIM_IMAGE,
            "victim",
            TARGET_STOP_TIMEOUT,
            hostname=VICTIM_NAME,
            network=NETWORK,
            volumes=self._scenarios_volume(),
        )
        privileged = self._run(
            PRIVILEGED_VICTIM_NAME,
            VICTIM_IMAGE,
            "victim",
            TARGET_STOP_TIMEOUT,
            hostname=PRIVILEGED_VICTIM_NAME,
            network=NETWORK,
            privileged=True,
            volumes=self._scenarios_volume(),
        )
        return Targets(victim=victim, victim_privileged=privileged, attacker=attacker)

    def start_workload_host(self) -> ContainerRef:
        return self._run(
            WORKLOAD_HOST_NAME,
            VICTIM_IMAGE,
            "workload",
            TARGET_STOP_TIMEOUT,
            hostname=WORKLOAD_HOST_NAME,
            network=NETWORK,
        )

    def _ensure_image(self, image: str) -> None:
        try:
            self.client.images.get(image)
            return
        except ImageNotFound:
            pass
        try:
            self.client.images.pull(image)
        except DockerException as error:
            raise ToolStartError(f"cannot pull image {image}: {error}") from error

    def start_tool(self, tool: str, profile: str, spec: ContainerSpec) -> ContainerRef:
        if spec.build_context:
            self.client.images.build(path=str(self.local_path(spec.build_context)), tag=spec.image, rm=True)
        else:
            self._ensure_image(spec.image)
        options: dict[str, Any] = {
            "privileged": spec.privileged,
            "environment": dict(spec.environment),
            "volumes": [f"{mount.source}:{mount.target}:{'ro' if mount.read_only else 'rw'}" for mount in spec.mounts],
        }
        if spec.command:
            options["command"] = list(spec.command)
        if spec.entrypoint is not None:
            options["entrypoint"] = list(spec.entrypoint)
        if spec.pid_mode:
            options["pid_mode"] = spec.pid_mode
        if spec.network_mode:
            options["network_mode"] = spec.network_mode
        if spec.cgroupns_mode:
            options["cgroupns"] = spec.cgroupns_mode
        if spec.cap_add:
            options["cap_add"] = list(spec.cap_add)
        if spec.security_opt:
            options["security_opt"] = list(spec.security_opt)
        return self._run(f"bench-tool-{tool}-{profile}", spec.image, "tool", TOOL_STOP_TIMEOUT, **options)

    def _container(self, ref: ContainerRef) -> Any:
        container = self._containers.get(ref.id)
        return container if container is not None else self.client.containers.get(ref.id)

    def follow_logs(self, ref: ContainerRef) -> LineBuffer:
        buffer = LineBuffer()
        stream = self._container(ref).logs(stream=True, follow=True, timestamps=True)
        threading.Thread(target=pump_log_stream, args=(stream, buffer), name=f"logs-{ref.name}", daemon=True).start()
        self._buffers.setdefault(ref.id, []).append(buffer)
        return buffer

    def tail_file(self, path: Path) -> LineBuffer:
        return tail_file(path)

    def _log_tail(self, logs: LineBuffer, count: int = 20) -> str:
        return "\n".join(line for _, line in logs.lines()[-count:])

    def _ensure_running(self, ref: ContainerRef, logs: LineBuffer) -> None:
        container = self._container(ref)
        container.reload()
        if container.status in ("exited", "dead"):
            code = container.attrs.get("State", {}).get("ExitCode")
            raise ToolStartError(f"container {ref.name} exited with code {code}; last logs:\n{self._log_tail(logs)}")

    def wait_ready(self, ref: ContainerRef, logs: LineBuffer, pattern: str | None, timeout: float) -> None:
        if pattern is None:
            time.sleep(min(3.0, timeout))
            self._ensure_running(ref, logs)
            return
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            if logs.wait_for(pattern, min(2.0, remaining)):
                return
            self._ensure_running(ref, logs)
            if logs.closed:
                time.sleep(min(1.0, max(remaining, 0)))
        raise ToolStartError(
            f"ready pattern {pattern!r} not seen within {timeout:.0f}s; last logs:\n{self._log_tail(logs)}"
        )

    def _probe_url(self, url: str) -> str | None:
        try:
            with self.urlopen(url, timeout=URL_PROBE_TIMEOUT) as response:
                status = getattr(response, "status", None) or response.getcode()
                return None if status == 200 else f"HTTP {status}"
        except urllib.error.HTTPError as error:
            return f"HTTP {error.code}"
        except (urllib.error.URLError, OSError, ValueError) as error:
            return str(error)

    def wait_url(self, ref: ContainerRef, logs: LineBuffer, url: str, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while True:
            failure = self._probe_url(url)
            if failure is None:
                return
            self._ensure_running(ref, logs)
            if time.monotonic() >= deadline:
                raise ToolStartError(f"{url} did not return HTTP 200 within {timeout:.0f}s: {failure}")
            time.sleep(URL_POLL_SECONDS)

    def start_host_stats(self) -> HostCpuSampler | None:
        return HostCpuSampler() if read_cpu_times() is not None else None

    def exec(self, ref: ContainerRef, command: list[str], environment: dict[str, str], timeout: float) -> ExecResult:
        api = self.client.api
        exec_id = api.exec_create(ref.id, command, environment=environment or None)["Id"]
        box: dict[str, Any] = {}

        def target() -> None:
            try:
                box["output"] = api.exec_start(exec_id)
            except Exception as error:
                box["error"] = error

        thread = threading.Thread(target=target, name=f"exec-{ref.name}", daemon=True)
        started_at = time.time()
        thread.start()
        thread.join(timeout)
        ended_at = time.time()
        timed_out = thread.is_alive()
        if timed_out:
            self._kill_exec(exec_id)
            thread.join(5)
        raw = box.get("output") or b""
        output = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
        if "error" in box:
            output += f"\n[bench] exec error: {box['error']}"
        if timed_out:
            return ExecResult(TIMEOUT_EXIT_CODE, output + f"\n[bench] timed out after {timeout:g}s", started_at, ended_at)
        exit_code = api.exec_inspect(exec_id).get("ExitCode")
        return ExecResult(exit_code if isinstance(exit_code, int) else -1, output, started_at, ended_at)

    def _kill_exec(self, exec_id: str) -> None:
        try:
            pid = self.client.api.exec_inspect(exec_id).get("Pid")
            if pid:
                os.kill(pid, signal.SIGKILL)
        except (OSError, DockerException):
            pass

    def start_stats(self, ref: ContainerRef) -> StatsSampler:
        container = self._container(ref)
        return StatsSampler(lambda: container.stats(stream=True, decode=True))

    def stop(self, ref: ContainerRef) -> None:
        container = self._containers.pop(ref.id, None)
        timeout = self._stop_timeouts.pop(ref.id, TARGET_STOP_TIMEOUT)
        if container is None:
            try:
                container = self.client.containers.get(ref.id)
            except NotFound:
                return
        try:
            container.stop(timeout=timeout)
        except (APIError, NotFound):
            pass
        for buffer in self._buffers.pop(ref.id, []):
            buffer.wait_closed(LOG_DRAIN_TIMEOUT)
        try:
            container.remove(force=True)
        except (APIError, NotFound):
            pass

    def cleanup(self) -> None:
        for container_id in list(self._containers):
            try:
                self.stop(ContainerRef(id=container_id, name=container_id))
            except DockerException:
                pass
        self._remove_labelled()
        try:
            for network in self.client.networks.list(names=[NETWORK]):
                network.remove()
        except DockerException:
            pass

    def host_info(self) -> dict[str, Any]:
        info = self.client.info()
        version = self.client.version()
        return {
            "kernel": info.get("KernelVersion") or platform.release(),
            "operating_system": info.get("OperatingSystem"),
            "architecture": info.get("Architecture") or platform.machine(),
            "cpus": info.get("NCPU") or os.cpu_count(),
            "memory_bytes": info.get("MemTotal"),
            "hostname": info.get("Name"),
            "docker_version": version.get("Version"),
            "docker_api_version": version.get("ApiVersion"),
            "cgroup_version": info.get("CgroupVersion"),
            "cgroup_driver": info.get("CgroupDriver"),
            "storage_driver": info.get("Driver"),
            "runner_python": platform.python_version(),
        }
