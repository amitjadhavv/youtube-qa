"""Step 3: embed data/chunks_XX.json into a persistent Chroma collection (db/).

Usage:  python index.py     # rebuilds the collection from every data/chunks_XX.json
Embeds `embed_text` (title + neighbor context) with Chroma's default local MiniLM
model, but stores the clean `text` as the document so results show only what the
lecturer said.
"""
import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DATA = Path("data")
DB_PATH = "db"
COLLECTION = "lectures"

embed = DefaultEmbeddingFunction()


def get_collection(client):
    return client.get_or_create_collection(
        COLLECTION, embedding_function=embed, configuration={"hnsw": {"space": "cosine"}}
    )


if __name__ == "__main__":
    paths = sorted(DATA.glob("chunks_*.json"))
    if not paths:
        raise SystemExit("No data/chunks_XX.json found. Run chunk.py first.")

    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection(COLLECTION)  # rebuild from scratch so re-runs never duplicate
    except Exception:
        pass
    col = get_collection(client)

    for path in paths:
        chunks = json.loads(path.read_text(encoding="utf-8"))
        col.add(
            ids=[f"L{c['lecture']:02d}-{c['start']:.2f}" for c in chunks],
            documents=[c["text"] for c in chunks],
            embeddings=embed([c["embed_text"] for c in chunks]),
            metadatas=[{
                "lecture": c["lecture"], "title": c["title"], "video_url": c["video_url"],
                "start": c["start"], "end": c["end"],
            } for c in chunks],
        )
        print(f"{path.name}: indexed {len(chunks)} chunks")

    print(f"Done. {col.count()} chunks in '{COLLECTION}' ({DB_PATH}/)")
