from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Optional
from urllib.parse import urljoin

from loguru import logger
from requests import request
from yoyo.targets.target_handler import TargetHandler


@dataclass
class Service:
    """Use to call one service from another service or from the CLI."""
    name: str
    target_override: Optional[TargetDescriptor] = None

    def __hash__(self):
        return hash(self.name)

    @cached_property
    def target_descriptor(self) -> TargetDescriptor:
        if self.target_override is not None:
            return self.target_override
        return TargetHandler.from_env_for_service(self.name)

    def call(self, method: str, path: str, args: dict, expected_response_cls=None):
        full_path = urljoin(self.url, path)
        r = request(method, full_path, json=args)
        r.raise_for_status()
        if expected_response_cls is None:
            return r.json()
        return expected_response_cls.parse_object(r.json())

    @cached_property
    def url(self) -> str:
        logger.debug(f"Discovering service '{self.name}'...")
        return self.target_descriptor.discover(self.name)
