from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .. import config


@dataclass
class GraphNode:
    id: str
    labels: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)


class GraphStore(ABC):
    @abstractmethod
    def add_node(self, id: str, labels: list[str], properties: dict | None = None) -> None: ...

    @abstractmethod
    def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: dict | None = None) -> None: ...

    @abstractmethod
    def neighbors(self, id: str, rel_type: str | None = None) -> list[GraphNode]: ...


class MockGraphStore(GraphStore):
    """In-memory graph store. Same interface as the real Neo4j-backed store
    below, so swapping in real AuraDB credentials requires no call-site
    changes.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[tuple[str, str, str, dict]] = []  # (from, to, rel_type, props)

    def add_node(self, id: str, labels: list[str], properties: dict | None = None) -> None:
        self._nodes[id] = GraphNode(id=id, labels=labels, properties=properties or {})

    def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: dict | None = None) -> None:
        self._edges.append((from_id, to_id, rel_type, properties or {}))

    def neighbors(self, id: str, rel_type: str | None = None) -> list[GraphNode]:
        result = []
        for from_id, to_id, edge_type, _ in self._edges:
            if from_id != id:
                continue
            if rel_type is not None and edge_type != rel_type:
                continue
            node = self._nodes.get(to_id)
            if node is not None:
                result.append(node)
        return result


class Neo4jGraphStore(GraphStore):
    """Real Neo4j AuraDB-backed store. Only instantiated when NEO4J_URI /
    NEO4J_USERNAME / NEO4J_PASSWORD are all set — see get_graph_store() below.
    Not yet exercised against a real AuraDB instance; wire up once credentials
    are available.
    """

    def __init__(self, uri: str, username: str, password: str) -> None:
        from neo4j import GraphDatabase

        self._driver = GraphDatabase.driver(uri, auth=(username, password))

    def add_node(self, id: str, labels: list[str], properties: dict | None = None) -> None:
        label_str = ":".join(labels) if labels else "Node"
        with self._driver.session() as session:
            session.run(
                f"MERGE (n:{label_str} {{id: $id}}) SET n += $props",
                id=id,
                props=properties or {},
            )

    def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: dict | None = None) -> None:
        with self._driver.session() as session:
            session.run(
                "MATCH (a {id: $from_id}), (b {id: $to_id}) "
                f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props",
                from_id=from_id,
                to_id=to_id,
                props=properties or {},
            )

    def neighbors(self, id: str, rel_type: str | None = None) -> list[GraphNode]:
        rel_clause = f":{rel_type}" if rel_type else ""
        with self._driver.session() as session:
            result = session.run(
                f"MATCH (a {{id: $id}})-[{rel_clause}]->(b) RETURN b",
                id=id,
            )
            return [
                GraphNode(id=record["b"]["id"], labels=list(record["b"].labels), properties=dict(record["b"]))
                for record in result
            ]


def get_graph_store() -> GraphStore:
    if config.USING_REAL_NEO4J:
        return Neo4jGraphStore(config.NEO4J_URI, config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    return MockGraphStore()
