from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional, Set

import fire
import git
from loguru import logger
from yoyo.config import Config
from yoyo.graph import Graph
from yoyo.symlinks import ServiceSymlinkManager
from yoyo.targets.target_handler import TargetHandler


@dataclass
class CLI:
    """PoC tool for managing Python Microservices."""
    root_path: Path = Path(git.Repo('.', search_parent_directories=True).git.rev_parse("--show-toplevel"))
    config_path: Path = Path('yoyo.yml')
    find: Optional[str] = None
    services: Set[str] = None
    target: str = 'local'

    _target_descriptor: TargetDescriptor = field(init=False)

    def __post_init__(self):
        self._target_descriptor = TargetHandler.from_str(self.target)
        self._target_descriptor.add_target_commands_to_cli(self)
        self._parse_custom_arg_types()
        if not self.config_path.is_absolute():
            self.config_path = self.root_path / self.config_path
        self._set_dynamic_docs()
        if isinstance(self.services, str):
            self.services = {self.services}
        if not self.services:
            self.services = self._graph.search(self.find) if self.find else self._graph.nodes

    def _parse_custom_arg_types(self):
        """Fire only handles some arg types, make sure other arg types are parsed too."""
        for arg, arg_type in self.__annotations__.items():
            if arg_type == Path:
                setattr(self, arg, arg_type(getattr(self, arg)))

    def _set_dynamic_docs(self):
        """Extra helpful docstrings with vars in."""
        self.compile_graph.__func__.__doc__ = f"""
        Scan all {self._config.paths.link_spec_file} files within service directories to find service links and save 
        the results to '{self._absolute_paths.graph_file}'.
        """

    @cached_property
    def _config(self):
        return Config.from_yml(self.config_path)

    @cached_property
    def _absolute_paths(self):
        return self._config.absolute_paths(root=self.root_path)

    @cached_property
    def _graph(self):
        return Graph.from_code_links(self._absolute_paths)

    @cached_property
    def _symlink_manager(self):
        return ServiceSymlinkManager(self._absolute_paths)

    def init(self):
        """Run if using for first time to set up repo."""
        config = Config()
        config.to_yml(self.config_path)
        self._absolute_paths.create()
        self.sync()

    def sync(self):
        """Call compile_graph & sync."""
        self.compile_graph()
        self.link_services()

    def compile_graph(self):
        """Doc overridden in CLI._set_dynamic_docs."""
        logger.info("🏗 Compiling graph from code links...")
        self._graph.describe()
        self._graph.write(self._absolute_paths.graph_file)

    def link_services(self):
        """Given the graph compiled from code links, materialise the links as symlinks within service directories."""
        code_links = self._graph.edges
        symlinks = self._symlink_manager.get_existing_symlinks()

        to_create = code_links - symlinks
        self._symlink_manager.link_services(to_create)

        to_delete = symlinks - code_links
        self._symlink_manager.unlink_services(to_delete)

    def list(self):
        for service in self.services:
            logger.info(service)


def main():
    fire.Fire(CLI)


if __name__ == '__main__':
    CLI().up()
