from dataclasses import dataclass
from typing import Tuple, Iterable, Set

from loguru import logger
from yoyo.exceptions import ServiceNotFound
from yoyo.path_mapper import PathMap


@dataclass
class ServiceSymlinkManager:
    path_map: PathMap

    def get_existing_symlinks(self) -> Set[Tuple[str, str]]:
        return set(
            (caller.name, callee.name)
            for caller in self.path_map.service_dirs
            for callee in self.path_map.get_linked_dirs(caller)
        )

    def link_services(self, links: Iterable[Tuple[str, str]]):
        for (caller, callee) in links:
            logger.info(f"✨ Creating link: {caller} ➡️ {callee}")
            callee_models = self.path_map.models_dir(callee)
            links_dir = self.path_map.links_dir(caller)
            links_dir.mkdir(exist_ok=True, parents=True)
            caller_link_path = self.path_map.make_relative(links_dir) / callee
            if not callee_models.exists():
                raise ServiceNotFound(f"Service '{caller}' references service '{callee}' which does not exist.")
            caller_link_path.symlink_to(callee_models, target_is_directory=True)

    def unlink_services(self, links: Iterable[Tuple[str, str]]):
        for (caller, callee) in links:
            logger.info(f"🗑 Deleting link: {caller} ❌ {callee}")
            caller_link_path = self.path_map.links_dir(caller) / callee
            caller_link_path.unlink()
