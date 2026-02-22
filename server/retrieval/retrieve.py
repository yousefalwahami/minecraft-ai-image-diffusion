"""
FAISS nearest-neighbour retrieval over clip_cache embeddings.

Call load_index() once at server startup, then retrieve(prompt) per request.
"""

import json
from pathlib import Path
from typing import Optional

import clip
import faiss
import numpy as np
import torch

_INDEX_PATH = Path(__file__).parent / "faiss.index"
_MAP_PATH = Path(__file__).parent / "index_map.json"

_index: Optional[faiss.Index] = None
_index_map: Optional[list] = None
_clip_model = None
_clip_device: Optional[str] = None


def load_index() -> None:
    """Load FAISS index, index map, and CLIP model. Call once at startup."""
    global _index, _index_map, _clip_model, _clip_device

    _index = faiss.read_index(str(_INDEX_PATH))
    with open(_MAP_PATH) as f:
        _index_map = json.load(f)

    _clip_device = "cuda" if torch.cuda.is_available() else "cpu"
    _clip_model, _ = clip.load("ViT-B/32", device=_clip_device)
    _clip_model.eval()

    print(f"[retrieval] Loaded FAISS index with {_index.ntotal} vectors "
          f"(CLIP on {_clip_device})")


def index_size() -> int:
    return _index.ntotal if _index is not None else 0


def retrieve(prompt: str, k: int = 1) -> int:
    """
    CLIP-encode prompt, query FAISS, return blockgen-3d dataset index
    of the nearest neighbour.
    """
    assert _index is not None, "Call load_index() before retrieve()"

    with torch.no_grad():
        tokens = clip.tokenize([prompt], truncate=True).to(_clip_device)
        embedding = _clip_model.encode_text(tokens).float()
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        vec = embedding.cpu().numpy().astype("float32")

    _, I = _index.search(vec, k)
    faiss_pos = int(I[0][0])
    return _index_map[faiss_pos]
