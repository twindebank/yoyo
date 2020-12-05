from __future__ import annotations

import json
import os
from typing import Dict

DEFAULT_SERVICE_TARGET_ENV_VAR = "DEFAULT_SERVICE_TARGET"
SERVICE_TARGET_OVERRIDES_ENV_VAR = "SERVICE_TARGET_OVERRIDES"


class TargetHandler:
    @staticmethod
    def from_str(target: str):
        from yoyo.targets.target_descriptors import target_descriptor_lookup, null
        return target_descriptor_lookup.get(target, null)

    @staticmethod
    def from_cli_for_service(cli, service: str):
        return TargetHandler.for_service(
            service,
            default_target=cli.target,
            overrides=cli._get_service_target_overrides()
        )

    @staticmethod
    def to_env_from_cli(cli, process_env):
        process_env[DEFAULT_SERVICE_TARGET_ENV_VAR] = cli.target
        process_env[SERVICE_TARGET_OVERRIDES_ENV_VAR] = json.dumps(cli._get_service_target_overrides())

    @staticmethod
    def from_env_for_service(service: str):
        return TargetHandler.for_service(
            service,
            default_target=os.getenv(DEFAULT_SERVICE_TARGET_ENV_VAR, 'null'),
            overrides=json.loads(os.getenv(SERVICE_TARGET_OVERRIDES_ENV_VAR, "{}"))
        )

    @staticmethod
    def for_service(service: str, default_target: str, overrides: Dict[str, str]) -> TargetDescriptor:
        target = overrides.get(service, default_target)
        return TargetHandler.from_str(target)
