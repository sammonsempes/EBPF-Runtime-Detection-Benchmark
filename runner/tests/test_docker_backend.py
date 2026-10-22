from __future__ import annotations

import time
import urllib.error
from datetime import UTC, datetime
from pathlib import Path

import pytest
from docker.errors import APIError, ImageNotFound, NotFound

from bench.adapters.base import ContainerSpec, Mount
from bench.docker_backend import (
    ContainerRef,
    DockerBackend,
    HostCpuSampler,
    LineBuffer,
    ToolStartError,
    busy_percent,
    cpu_percent,
    read_cpu_times,
    memory_bytes,
    parse_docker_timestamp,
    pump_log_stream,
    split_timestamped,
    tail_file,
)


def test_parse_docker_timestamp_nanoseconds() -> None:
    expected = datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC).timestamp() + 0.123456789
    assert parse_docker_timestamp("2024-01-02T03:04:05.123456789Z") == pytest.approx(expected, abs=1e-6)
    assert parse_docker_timestamp("2024-01-02T05:04:05+02:00") == pytest.approx(expected - 0.123456789)
    assert parse_docker_timestamp("not-a-time") is None


def test_split_timestamped() -> None:
    stamp, line = split_timestamped("2024-01-02T03:04:05.5Z {\"rule\": \"x\"}\r")
    assert line == '{"rule": "x"}'
    assert stamp == pytest.approx(datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC).timestamp() + 0.5)
    before = time.time()
    stamp, line = split_timestamped("plain line")
    assert line == "plain line" and stamp >= before


def test_pump_log_stream_reassembles_lines() -> None:
    buffer = LineBuffer()
    chunks = [b"2024-01-02T03:04:05.1Z hel", b"lo\n2024-01-02T03:04:06.2Z wor", b"ld\n\n2024-01-02T03:04:07Z tail"]
    pump_log_stream(iter(chunks), buffer)
    assert [line for _, line in buffer.lines()] == ["hello", "world", "tail"]
    assert buffer.closed


def test_line_buffer_wait_for() -> None:
    buffer = LineBuffer()
    buffer.append(1.0, "starting")
    assert not buffer.wait_for("ready", 0.05)
    buffer.append(2.0, "Engine READY now")
    assert buffer.wait_for("(?i)ready", 0.05)
    buffer.close()
    assert buffer.wait_closed(0.1)


def test_tail_file(tmp_path: Path) -> None:
    path = tmp_path / "alerts.json"
    buffer = tail_file(path, clock=lambda: 42.0)
    time.sleep(0.3)
    path.write_text('{"a": 1}\n{"b"')
    time.sleep(0.5)
    with path.open("a") as handle:
        handle.write(": 2}\n")
    assert buffer.finish(5)
    assert buffer.lines() == [(42.0, '{"a": 1}'), (42.0, '{"b": 2}')]


def test_cpu_and_memory() -> None:
    sample = {
        "cpu_stats": {"cpu_usage": {"total_usage": 300, "percpu_usage": [1, 2, 3, 4]}, "system_cpu_usage": 2000},
        "precpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 1000},
        "memory_stats": {"usage": 5000, "stats": {"total_inactive_file": 1000}},
    }
    assert cpu_percent(sample) == pytest.approx(80.0)
    assert memory_bytes(sample) == 4000.0
    assert cpu_percent({"cpu_stats": {}, "precpu_stats": {}}) is None
    assert memory_bytes({"memory_stats": {}}) is None
    assert memory_bytes({"memory_stats": {"usage": 10, "stats": {"cache": 4}}}) == 6.0


class FakeContainer:
    def __init__(self, container_id: str) -> None:
        self.id = container_id


class FakeContainers:
    def __init__(self) -> None:
        self.runs: list[tuple[str, dict]] = []

    def get(self, name: str):
        raise NotFound(name)

    def run(self, image: str, **kwargs):
        self.runs.append((image, kwargs))
        return FakeContainer(f"id-{len(self.runs)}")


class FakeImages:
    def __init__(self, present: tuple[str, ...] = ("img",)) -> None:
        self.builds: list[dict] = []
        self.present = set(present)
        self.pulls: list[str] = []

    def build(self, **kwargs):
        self.builds.append(kwargs)

    def get(self, image: str):
        if image not in self.present:
            raise ImageNotFound(image)
        return image

    def pull(self, image: str):
        self.pulls.append(image)
        self.present.add(image)


class FakeClient:
    def __init__(self) -> None:
        self.containers = FakeContainers()
        self.images = FakeImages()


def test_local_path_maps_host_paths() -> None:
    backend = DockerBackend(Path("/bench"), Path("/home/me/repo"), client=FakeClient())
    assert backend.local_path("/home/me/repo/tools/kunai") == Path("/bench/tools/kunai")
    assert backend.local_path("tools/pulsar") == Path("/bench/tools/pulsar")
    assert backend.local_path("/elsewhere") == Path("/elsewhere")


def test_start_tool_translates_spec() -> None:
    client = FakeClient()
    backend = DockerBackend(Path("/bench"), Path("/home/me/repo"), client=client)
    spec = ContainerSpec(
        image="ebpf-bench/kunai:1",
        command=["run", "--json"],
        entrypoint=["/kunai"],
        build_context="/home/me/repo/tools/kunai",
        cap_add=["SYS_ADMIN"],
        security_opt=["apparmor=unconfined"],
        mounts=[Mount("/sys/kernel/debug", "/sys/kernel/debug"), Mount("/home/me/repo/results/x", "/out", False)],
        environment={"A": "1"},
    )
    ref = backend.start_tool("kunai", "default", spec)
    assert ref.name == "bench-tool-kunai-default"
    assert client.images.builds == [{"path": "/bench/tools/kunai", "tag": "ebpf-bench/kunai:1", "rm": True}]
    image, options = client.containers.runs[0]
    assert image == "ebpf-bench/kunai:1"
    assert options["volumes"] == ["/sys/kernel/debug:/sys/kernel/debug:ro", "/home/me/repo/results/x:/out:rw"]
    assert options["pid_mode"] == "host"
    assert options["network_mode"] == "host"
    assert options["cgroupns"] == "host"
    assert options["privileged"] is True
    assert options["command"] == ["run", "--json"]
    assert options["entrypoint"] == ["/kunai"]
    assert options["cap_add"] == ["SYS_ADMIN"]
    assert options["security_opt"] == ["apparmor=unconfined"]
    assert options["environment"] == {"A": "1"}
    assert options["detach"] is True
    assert options["labels"] == {"ebpf-bench.role": "tool"}


def test_start_tool_omits_unset_modes() -> None:
    client = FakeClient()
    backend = DockerBackend(Path("/bench"), Path("/host"), client=client)
    backend.start_tool("x", "default", ContainerSpec(image="img", pid_mode=None, network_mode=None, cgroupns_mode=None))
    _, options = client.containers.runs[0]
    assert not {"pid_mode", "network_mode", "cgroupns", "command", "entrypoint", "cap_add"} & set(options)
    assert client.images.builds == []
    assert client.images.pulls == []


def test_start_tool_pulls_missing_image() -> None:
    client = FakeClient()
    backend = DockerBackend(Path("/bench"), Path("/host"), client=client)
    backend.start_tool("pulsar", "default", ContainerSpec(image="ghcr.io/exein-io/pulsar:v0.10.1"))
    backend.start_tool("pulsar", "tuned", ContainerSpec(image="ghcr.io/exein-io/pulsar:v0.10.1"))
    assert client.images.pulls == ["ghcr.io/exein-io/pulsar:v0.10.1"]
    assert client.containers.runs[0][0] == "ghcr.io/exein-io/pulsar:v0.10.1"


def test_start_tool_reports_pull_failure() -> None:
    client = FakeClient()

    def fail(image: str):
        raise APIError("denied")

    client.images.pull = fail
    backend = DockerBackend(Path("/bench"), Path("/host"), client=client)
    with pytest.raises(ToolStartError, match="cannot pull image missing:1"):
        backend.start_tool("x", "default", ContainerSpec(image="missing:1"))
    assert client.containers.runs == []


def test_read_cpu_times_and_busy_percent(tmp_path: Path) -> None:
    stat = tmp_path / "stat"
    stat.write_text("cpu  100 0 50 800 50 0 0 0 0 0\ncpu0 1 2 3 4\n")
    assert read_cpu_times(stat) == (1000.0, 850.0)
    stat.write_text("intr 1 2 3\n")
    assert read_cpu_times(stat) is None
    assert read_cpu_times(tmp_path / "missing") is None
    assert busy_percent((1000.0, 850.0), (1200.0, 900.0)) == pytest.approx(75.0)
    assert busy_percent((1000.0, 850.0), (1000.0, 850.0)) is None


def test_host_cpu_sampler() -> None:
    readings = iter([(0.0, 0.0), (100.0, 50.0), (200.0, 150.0), None, (300.0, 200.0)] + [(400.0, 300.0)] * 100)
    sampler = HostCpuSampler(lambda: next(readings), interval=0.01)
    time.sleep(0.2)
    samples = sampler.stop()
    assert samples[:2] == [pytest.approx(50.0), pytest.approx(0.0)]
    assert len(samples) >= 3


def test_host_info_does_not_record_hostname() -> None:
    client = FakeClient()
    client.info = lambda: {"KernelVersion": "6.6.87", "Name": "secret-laptop", "NCPU": 8, "Architecture": "x86_64"}
    client.version = lambda: {"Version": "27.0", "ApiVersion": "1.46"}
    info = DockerBackend(Path("/bench"), Path("/host"), client=client).host_info()
    assert info["kernel"] == "6.6.87" and info["cpus"] == 8 and info["docker_version"] == "27.0"
    assert "hostname" not in info
    assert "secret-laptop" not in repr(info)


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        return None


class FakeRunning:
    status = "running"
    attrs: dict = {}

    def reload(self) -> None:
        return None


def test_wait_url_polls_until_healthy(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = [urllib.error.URLError("refused"), 503, 200]
    calls: list[str] = []

    def urlopen(url: str, timeout: float):
        calls.append(url)
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return FakeResponse(answer)

    monkeypatch.setattr("bench.docker_backend.URL_POLL_SECONDS", 0.01)
    backend = DockerBackend(Path("/bench"), Path("/host"), client=FakeClient(), urlopen=urlopen)
    ref = ContainerRef(id="tool", name="tool")
    backend._containers[ref.id] = FakeRunning()
    backend.wait_url(ref, LineBuffer(), "http://127.0.0.1:3366/healthz", 5)
    assert calls == ["http://127.0.0.1:3366/healthz"] * 3


def test_wait_url_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("bench.docker_backend.URL_POLL_SECONDS", 0.01)
    backend = DockerBackend(
        Path("/bench"), Path("/host"), client=FakeClient(), urlopen=lambda url, timeout: FakeResponse(500)
    )
    ref = ContainerRef(id="tool", name="tool")
    backend._containers[ref.id] = FakeRunning()
    with pytest.raises(ToolStartError, match="HTTP 500"):
        backend.wait_url(ref, LineBuffer(), "http://127.0.0.1:3366/healthz", 0.05)
