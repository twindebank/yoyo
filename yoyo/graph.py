import json
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Set, Tuple

import networkx as nx
from loguru import logger
from yoyo.path_mapper import PathMap
from yoyo.service import Service
from yoyo.utils import load_module


@dataclass
class Graph:
    edges: Set[Tuple[str, str]]
    nodes: Set[str]

    @classmethod
    def from_json(cls, path: Path):
        graph_dict = json.loads(path.read_text())
        return cls(
            edges=set(tuple(edge) for edge in graph_dict['edges']),
            nodes=set(graph_dict['nodes'])
        )

    @classmethod
    def from_code_links(cls, path_map: PathMap):
        nodes = set(s.name for s in path_map.service_dirs)
        edges = set()
        for caller in path_map.service_dirs:
            links_module = load_module(caller, path_map.code_links_file(caller))
            if not links_module:
                continue
            for attr in dir(links_module):
                if isinstance(callee := getattr(links_module, attr), Service):
                    edges.add((caller.name, callee.name))
        return cls(
            nodes=nodes,
            edges=edges
        )

    def to_dict(self):
        return {
            "edges": [[caller, callee] for (caller, callee) in self.edges],
            "nodes": list(self.nodes)
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def write(self, path: Path):
        path.write_text(self.to_json())

    @cached_property
    def nx_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_nodes_from(self.nodes)
        graph.add_edges_from(self.edges)
        return graph

    def describe(self):
        logger.info(f"🕵️‍♀️ {len(self.nodes)} service(s) present.")
        for node in self.nodes:
            logger.debug(f" • {node}")
        logger.info(f"🔗 {len(self.edges)} link(s) between services.")
        for (caller, callee) in self.edges:
            logger.debug(f" • {caller} ➡️ {callee}")

    def search(self, find_expr):
        services = set()
        service_expressions = find_expr.split(' ')
        for expression in service_expressions:
            service = expression.strip('+')
            services.add(service)
            if expression.startswith('+'):
                services.update(nx.ancestors(self.nx_graph, service))
            if expression.endswith('+'):
                services.update(nx.descendants(self.nx_graph, service))
        return services
