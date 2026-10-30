# Pluggable Agents

A LangGraph-orchestrated agentic RAG + GraphRAG pipeline where every backend —
LLM provider, vector store, graph store — is a swap-in component, not a fixed
dependency. Built for a bespoke audience who need maximum control over their
agent stack, not a one-size-fits-all managed service.

## Design principle

Nothing in this stack is hardcoded to a vendor. Each backend is defined behind
a small abstract interface with two implementations side by side in the same
file: an in-memory version (for development, testing, or running with zero
external accounts) and a real, production-backed version. A factory function
auto-selects which one to use based on whether real credentials are present —
swapping a mock for a real backend is a `.env` change, not a code change.

```
VectorStore (interface)
├── MockVectorStore      — in-memory, cosine similarity, zero setup
└── PineconeVectorStore  — real Pinecone index

GraphStore (interface)
├── MockGraphStore       — in-memory node/edge graph
└── Neo4jGraphStore      — real Neo4j (AuraDB or self-hosted)
```

This isn't a "local-only" tool and isn't tied to Pinecone/Neo4j specifically
either — those are the first two backends wired up because they're where the
project started, not a ceiling. The interface is the contract; anything that
can implement `VectorStore` or `GraphStore` can be dropped in.

## Current status

| Component | State |
|---|---|
| LangGraph orchestration | Installed (1.2.18), graph logic not yet built |
| Vector store | Interface + mock implemented and tested; Pinecone-backed class written, not yet exercised against a real account |
| Graph store | Interface + mock implemented and tested; Neo4j-backed class written, not yet exercised against AuraDB |
| Chunking / ingestion | Not started |
| Hybrid search (BM25 + dense) | Not started |
| Reranking | Not started |
| Agentic RAG / GraphRAG reasoning | Not started |
| Memory management | Not started |
| Experiment tracking | Not started |
| Observability | Not started |

See `ROADMAP.md` for the full phased plan.

## Why this exists

Most agent/RAG starter kits pick one vector DB, one graph DB, one LLM, and
bake the choice in at the import level — switching later means rewriting
call sites. This project keeps the call sites stable (`get_vector_store()`,
`get_graph_store()`) and makes the backend a configuration concern, so the
same agent logic can run against a real Pinecone + Neo4j AuraDB deployment
in production and an in-memory mock in CI or a laptop with no network
access, with no branching logic in the agent code itself.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in real credentials when ready; leave blank to use mocks
```

### Verify the mocks work end-to-end

```bash
.venv/bin/python -c "
from src.stores import get_vector_store, get_graph_store

vs = get_vector_store()
vs.upsert('doc1', [1.0, 0.0, 0.0], {'text': 'example'})
print(vs.query([1.0, 0.0, 0.0], top_k=1))

gs = get_graph_store()
gs.add_node('a', ['Thing']); gs.add_node('b', ['Thing'])
gs.add_relationship('a', 'b', 'RELATES_TO')
print(gs.neighbors('a'))
"
```

## Switching to real backends

Set the corresponding variables in `.env`:

- **Pinecone**: `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`
- **Neo4j**: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`

`get_vector_store()` / `get_graph_store()` detect the presence of these and
return the real-backend implementation instead of the mock — no other code
changes required.

## Project structure

```
src/
├── config.py           # env var loading, real-vs-mock detection
└── stores/
    ├── vector_store.py # VectorStore interface, Mock + Pinecone impls
    └── graph_store.py   # GraphStore interface, Mock + Neo4j impls
ROADMAP.md               # full phased plan (chunking, hybrid search,
                          # reranking, agentic RAG, GraphRAG, memory,
                          # experiment tracking, observability)
```
