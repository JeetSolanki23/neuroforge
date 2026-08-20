from __future__ import annotations

import chromadb
from chromadb.utils import embedding_functions

from neuroforge.config import config

VALID_COLLECTIONS = [
    "agent_definitions",
    "tool_definitions",
    "project_memory",
    "learned_knowledge",
    "project_briefs",
]


def init_chroma() -> chromadb.ClientAPI:
    client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_PATH)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    for collection_name in VALID_COLLECTIONS:
        client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_fn,
        )
    return client


def get_collection(name: str) -> chromadb.Collection:
    if name not in VALID_COLLECTIONS:
        raise ValueError(f"Collection '{name}' is not a valid collection name.")
    client = init_chroma()
    return client.get_collection(name=name)


def health_check() -> bool:
    try:
        client = init_chroma()
        existing_collections = [col.name for col in client.list_collections()]
        return all(col_name in existing_collections for col_name in VALID_COLLECTIONS)
    except Exception:
        return False
