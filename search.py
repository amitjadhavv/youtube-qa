"""Step 3b: query the index and print the top hits with timestamp links.

Usage:  python search.py "what is aliasing in python lists?" [top_k]
"""
import sys

import chromadb

from index import COLLECTION, DB_PATH, get_collection

if len(sys.argv) < 2:
    sys.exit('Usage: python search.py "your question" [top_k]')
query = sys.argv[1]
top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

col = get_collection(chromadb.PersistentClient(path=DB_PATH))
res = col.query(query_texts=[query], n_results=top_k)

for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
    start = meta["start"]
    print(f"[{dist:.3f}] {meta['title']}  @ {int(start // 60)}:{int(start % 60):02d}")
    print(f"        {meta['video_url']}#t={int(start)}")
    print(f"        {text[:220]}...\n")
