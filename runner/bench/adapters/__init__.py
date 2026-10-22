from __future__ import annotations

from importlib import import_module

from bench.adapters.base import ContainerSpec, Mount, ToolAdapter

TOOLS = ("falco", "tetragon", "tracee", "kubearmor", "kunai", "pulsar")


def get_adapter(name: str) -> ToolAdapter:
    if name not in TOOLS:
        raise KeyError(f"unknown tool: {name}")
    module = import_module(f"bench.adapters.{name}")
    return module.Adapter()


__all__ = ["TOOLS", "ContainerSpec", "Mount", "ToolAdapter", "get_adapter"]
