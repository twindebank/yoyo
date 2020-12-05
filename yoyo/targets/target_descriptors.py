from __future__ import annotations

from dataclasses import dataclass
from typing import Type, Optional, Callable

from yoyo.targets.base.cmds import TargetCmds
from yoyo.targets.cloud_run.cmds import CloudRunCmds
from yoyo.targets.local.cmds import LocalCmds
from yoyo.targets.local.discovery import discover_local


@dataclass
class TargetDescriptor:
    name: str
    cmds_cls: Optional[Type[TargetCmds]]
    discovery_func: Optional[Callable[[str], str]]

    def discover(self, service: str):
        return self.discovery_func(service)

    def add_target_commands_to_cli(self, cli):
        cli.__class__ = self.cmds_cls


null = TargetDescriptor(
    name='null',
    cmds_cls=None,
    discovery_func=None
)

local = TargetDescriptor(
    name='local',
    cmds_cls=LocalCmds,
    discovery_func=discover_local
)

cloud_run = TargetDescriptor(
    name='cloud_run',
    cmds_cls=CloudRunCmds,
    discovery_func=discover_local
)

target_descriptor_lookup = {k: v for k, v in locals().items() if isinstance(v, TargetDescriptor)}
