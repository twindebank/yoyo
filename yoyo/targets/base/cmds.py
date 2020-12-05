from abc import abstractmethod
from typing import Optional

from yoyo.cli import CLI
from yoyo.service import Service
from yoyo.targets.target_handler import TargetHandler


class TargetCmds(CLI):
    @abstractmethod
    def up(self):
        """
        Bring up the service, including any deployment steps needed.
        """

    def call(self, service: str, method: str, path: str, args: Optional[dict] = None):
        """
        Call a service at the given target.
        """
        target = TargetHandler.from_cli_for_service(self, service)
        return Service(service, target_override=target).call(method, path, args)

    def _get_service_target_overrides(self):
        """
        Target overriding not supported yet so just return same target.
        todo: eventually support `yy up -s myservice --override-links prod`
        """
        return {s: self.target for s in self.services}
