#!/usr/bin/env python3
"""
Build FAISS index from clip_cache.pt.
Run once as a standalone script before starting the server:
    python server/retrieval/build_index.py
"""

import json
import sys
from pathlib import Path

import faiss
import numpy as np
import torch

CACHE_PATH = Path(__file__).parent.parent / "clip_cache.pt"
INDEX_PATH = Path(__file__).parent / "faiss.index"
MAP_PATH = Path(__file__).parent / "index_map.json"


def build():
    print(f"Loading clip_cache.pt from {CACHE_PATH} ...")
    cache: dict = torch.load(CACHE_PATH, map_location="cpu", weights_only=True)

    # Ordered iteration (Python 3.7+ dicts preserve insertion order).
    # Position in the dict = position in the blockgen-3d train split.
    prompts = list(cache.keys())
    embeddings = np.stack([cache[p].float().numpy() for p in prompts]).astype("float32")

    n, dim = embeddings.shape
    print(f"  {n} vectors, dim={dim}")

    # Embeddings are already L2-normalised, so IndexFlatIP == cosine similarity.
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    print(f"Saved index  → {INDEX_PATH}")

    # index_map[faiss_position] = blockgen-3d dataset index (same as faiss position
    # because the cache is ordered to match the train split).
    index_map = list(range(n))
    with open(MAP_PATH, "w") as f:
        json.dump(index_map, f)
    print(f"Saved index_map → {MAP_PATH}")

    print(f"\nDone. {index.ntotal} vectors indexed.")


if __name__ == "__main__":
    build()
