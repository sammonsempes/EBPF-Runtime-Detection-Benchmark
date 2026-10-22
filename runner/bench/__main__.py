from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from bench.adapters import TOOLS, get_adapter
from bench.config import Config, load_config
from bench.scenarios import load_scenarios, select_scenarios

if TYPE_CHECKING:
    from bench.docker_backend import Backend

DEFAULT_GRACE_SECONDS = 10.0


def _interrupt(signum: int, frame: object) -> NoReturn:
    raise KeyboardInterrupt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bench", description="eBPF runtime detection benchmark")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="run the benchmark")
    run.add_argument("--config", type=Path, default=Path("bench.yaml"))
    run.add_argument("--tools", nargs="+")
    run.add_argument("--profiles", nargs="+")
    run.add_argument("--scenarios", nargs="+")
    run.add_argument("--repetitions", type=int)
    run.add_argument("--skip-overhead", action="store_true")
    run.add_argument("--skip-control", action="store_true")
    run.add_argument("--backend", choices=["docker", "kubernetes"])

    score = commands.add_parser("score", help="score an existing results directory")
    score.add_argument("results_dir", type=Path)
    score.add_argument("--grace", type=float)

    report = commands.add_parser("report", help="write the report of a results directory")
    report.add_argument("results_dir", type=Path)

    listing = commands.add_parser("list", help="list scenarios or tools")
    listing.add_argument("what", choices=["scenarios", "tools"])
    listing.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser


def build_backend(config: Config, repo_root: Path, host_repo_root: Path) -> Backend:
    if config.backend == "kubernetes":
        from bench.k8s_backend import KubernetesBackend

        return KubernetesBackend(repo_root, host_repo_root, config.kubernetes)
    from bench.docker_backend import DockerBackend

    return DockerBackend(repo_root, host_repo_root)


def command_run(args: argparse.Namespace) -> int:
    from bench.orchestrator import Orchestrator

    config = load_config(args.config)
    overrides = {}
    if args.tools:
        overrides["tools"] = tuple(args.tools)
    if args.profiles:
        overrides["profiles"] = tuple(args.profiles)
    if args.scenarios:
        overrides["scenarios"] = tuple(args.scenarios)
    if args.repetitions is not None:
        overrides["repetitions"] = args.repetitions
    if args.skip_overhead:
        overrides["overhead"] = replace(config.overhead, enabled=False)
    if args.skip_control:
        overrides["control_scenarios"] = False
    if args.backend:
        overrides["backend"] = args.backend
    config = replace(config, **overrides)
    repo_root = args.config.resolve().parent
    host_repo_root = Path(os.environ.get("BENCH_HOST_ROOT") or repo_root)
    scenarios = select_scenarios(load_scenarios(repo_root / "scenarios"), config.scenarios)
    backend = build_backend(config, repo_root, host_repo_root)
    signal.signal(signal.SIGTERM, _interrupt)
    results = Orchestrator(config, scenarios, backend, repo_root, host_repo_root).run()
    print(results)
    return 0


def _grace_from_metadata(results_dir: Path) -> float:
    try:
        metadata = json.loads((results_dir / "metadata.json").read_text(encoding="utf-8"))
        return float(metadata["config"]["grace_seconds"])
    except (OSError, KeyError, TypeError, ValueError):
        return DEFAULT_GRACE_SECONDS


def command_score(args: argparse.Namespace) -> int:
    from bench.scoring import score_results

    grace = args.grace if args.grace is not None else _grace_from_metadata(args.results_dir)
    score_results(args.results_dir, grace)
    print(args.results_dir / "score.json")
    return 0


def command_report(args: argparse.Namespace) -> int:
    from bench.report import write_report

    print(write_report(args.results_dir))
    return 0


def command_list(args: argparse.Namespace) -> int:
    if args.what == "scenarios":
        for scenario in load_scenarios(args.repo_root / "scenarios"):
            technique = scenario.technique or "-"
            print(f"{scenario.id}\t{scenario.kind.value}\t{technique}\t{scenario.name}")
        return 0
    for tool in TOOLS:
        try:
            adapter = get_adapter(tool)
        except Exception as error:
            print(f"{tool}\tunavailable\t{type(error).__name__}: {error}")
            continue
        print(f"{tool}\t{adapter.version}\t{','.join(adapter.profiles)}")
    return 0


COMMANDS = {"run": command_run, "score": command_score, "report": command_report, "list": command_list}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
