import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .. import config


@dataclass
class VectorMatch:
    id: str
    score: float
    metadata: dict = field(default_factory=dict)


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, id: str, vector: list[float], metadata: dict | None = None) -> None: ...

    @abstractmethod
    def query(self, vector: list[float], top_k: int = 5) -> list[VectorMatch]: ...

    @abstractmethod
    def delete(self, id: str) -> None: ...


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class MockVectorStore(VectorStore):
    """In-memory vector store. Same interface as the real Pinecone-backed
    store below, so swapping in a real API key requires no call-site changes.
    """

    def __init__(self) -> None:
        self._records: dict[str, tuple[list[float], dict]] = {}

    def upsert(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        self._records[id] = (vector, metadata or {})

    def query(self, vector: list[float], top_k: int = 5) -> list[VectorMatch]:
        scored = [
            VectorMatch(id=rid, score=_cosine_similarity(vector, rvec), metadata=rmeta)
            for rid, (rvec, rmeta) in self._records.items()
        ]
        scored.sort(key=lambda m: m.score, reverse=True)
        return scored[:top_k]

    def delete(self, id: str) -> None:
        self._records.pop(id, None)


class PineconeVectorStore(VectorStore):
    """Real Pinecone-backed store. Only instantiated when PINECONE_API_KEY
    is set — see get_vector_store() below. Not yet exercised against a real
    account; wire up once a Pinecone API key is available.
    """

    def __init__(self, api_key: str, index_name: str) -> None:
        from pinecone import Pinecone

        self._client = Pinecone(api_key=api_key)
        self._index = self._client.Index(index_name)

    def upsert(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        self._index.upsert(vectors=[{"id": id, "values": vector, "metadata": metadata or {}}])

    def query(self, vector: list[float], top_k: int = 5) -> list[VectorMatch]:
        response = self._index.query(vector=vector, top_k=top_k, include_metadata=True)
        return [
            VectorMatch(id=m["id"], score=m["score"], metadata=m.get("metadata", {}))
            for m in response["matches"]
        ]

    def delete(self, id: str) -> None:
        self._index.delete(ids=[id])


def get_vector_store() -> VectorStore:
    if config.USING_REAL_PINECONE:
        return PineconeVectorStore(config.PINECONE_API_KEY, config.PINECONE_INDEX_NAME)
    return MockVectorStore()
