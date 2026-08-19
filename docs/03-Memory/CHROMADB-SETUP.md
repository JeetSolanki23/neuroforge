# ChromaDB Setup

tags: #memory #chromadb #setup

---

## Why ChromaDB

- Runs 100% locally — no server, no cloud account, no API key
- Python-native client (`chromadb` pip package)
- Persists to disk automatically
- Supports semantic search via embeddings
- Human-inspectable via CLI

---

## Collections

```python
import chromadb

client = chromadb.PersistentClient(path="./neuroforge-memory")

# Create collections (run once at setup)
collections = {
    "agent_definitions":  client.get_or_create_collection("agent_definitions"),
    "tool_definitions":   client.get_or_create_collection("tool_definitions"),
    "project_memory":     client.get_or_create_collection("project_memory"),
    "learned_knowledge":  client.get_or_create_collection("learned_knowledge"),
    "project_briefs":     client.get_or_create_collection("project_briefs"),
}
```

---

## Embedding Model

Use `sentence-transformers` locally — no API cost, fast on CPU:

```python
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # small, fast, good quality
)

# Pass to collection creation
client.get_or_create_collection(
    "learned_knowledge",
    embedding_function=embedding_fn
)
```

---

## Standard Query Pattern

```python
def query_memory(collection_name: str, query: str, n_results: int = 5, filters: dict = None):
    collection = collections[collection_name]
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=filters  # e.g. {"domain": "backend"}
    )
    return results
```

---

## Storage Location

```
neuroforge/
└── neuroforge-memory/          ← ChromaDB persists here
    ├── agent_definitions/
    ├── tool_definitions/
    ├── project_memory/
    ├── learned_knowledge/
    └── project_briefs/
```

---

## Related Notes

- [[MEMORY-ARCHITECTURE]]
- [[MARKDOWN-VAULT]]
- [[../01-Architecture/TECH-STACK]]
