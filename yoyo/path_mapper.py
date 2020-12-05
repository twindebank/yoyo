from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Generator


@dataclass(frozen=True, eq=True)
class PathMap:
    root: Path
    paths: ConfigPaths

    @property
    def generated_dir(self) -> Path:
        return self.root / self.paths.generated

    @property
    def services_dir(self) -> Path:
        return self.root / self.paths.services

    def service_dir(self, service: Path) -> Path:
        return self.services_dir / service

    @property
    def service_dirs(self) -> Generator[Path]:
        return (s for s in self.services_dir.iterdir() if is_service_dir(s))

    def get_linked_dirs(self, service: Path) -> Tuple[Path]:
        try:
            return tuple(
                s for s in self.links_dir(service).iterdir()
                if is_service_dir(s)
            )
        except FileNotFoundError:
            return tuple()

    @property
    def graph_file(self):
        return self.generated_dir / self.paths.graph_file

    def links_dir(self, service: Path) -> Path:
        return self.service_dir(service) / self.paths.service_links_subdir

    def code_links_file(self, service: Path) -> Path:
        return self.service_dir(service) / self.paths.link_spec_file

    def models_dir(self, service: Path) -> Path:
        return self.service_dir(service) / self.paths.service_models_subdir

    def main_file(self, service: Path) -> Path:
        return self.service_dir(service) / Path("main.py")

    def create(self):
        self.services_dir.mkdir(exist_ok=True, parents=True)
        self.generated_dir.mkdir(exist_ok=True, parents=True)

    def make_relative(self, absolute: Path):
        return absolute.relative_to(self.root)


def is_service_dir(service: Path):
    return service.is_dir() or service.is_symlink() and not service.name.startswith("_")
