from dataclasses import dataclass
from functools import cache
from pathlib import Path

import ruamel.yaml
from loguru import logger
from yoyo.path_mapper import PathMap

yaml = ruamel.yaml.YAML()


@dataclass(frozen=True, eq=True)
class Paths:
    services: Path = Path("services")
    generated: Path = Path("generated")
    service_links_subdir: Path = Path("symlinks")
    service_models_subdir: Path = Path("models")
    link_spec_file: Path = Path("links.py")
    graph_file: Path = Path("graph.json")

    def to_json_dict(self):
        return {k: str(getattr(self, k)) for k in self.__annotations__}

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: Path(v) for k, v in d.items()})


@dataclass(frozen=True, eq=True)
class Config:
    paths: Paths = Paths()

    @classmethod
    def from_yml(cls, config: Path):
        with config.open('r') as c:
            raw = yaml.load(c)
        return cls(
            paths=Paths.from_dict(raw['paths'])
        )

    def to_json_dict(self):
        return {
            "paths": self.paths.to_json_dict()
        }

    def to_yml(self, config: Path):
        logger.info(f"💾 Writing config to file '{config}'.")
        with config.open('w') as c:
            yaml.dump(self.to_json_dict(), c)

    @cache
    def absolute_paths(self, root):
        return PathMap(root, self.paths)
