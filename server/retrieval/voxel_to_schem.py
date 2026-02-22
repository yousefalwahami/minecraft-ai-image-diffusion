"""
Convert a blockgen-3d dataset sample to a Minecraft .schem file.

The blockgen-3d dataset is loaded once at module import.
"""

import sys
from pathlib import Path

import mcschematic
import numpy as np
from datasets import load_dataset

# Make schemgen importable without modifying its internals.
_SCHEMGEN_DIR = Path(__file__).parent.parent / "schemgen"
if str(_SCHEMGEN_DIR) not in sys.path:
    sys.path.insert(0, str(_SCHEMGEN_DIR))

from col2block import col2block  # noqa: E402 (needs sys.path patch above)

# ---------------------------------------------------------------------------
# Dataset – loaded once at module level
# ---------------------------------------------------------------------------

print("[voxel_to_schem] Loading PeterAM4/blockgen-3d train split ...")
_dataset = load_dataset("PeterAM4/blockgen-3d", split="train")
print(f"[voxel_to_schem] Dataset ready – {len(_dataset)} samples")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _center_voxels(
    colors: np.ndarray, occ: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Shift the occupied mass to the grid centre (16, 16, 16) using np.roll,
    matching the centring logic used during training.

    colors : float32 [3, 32, 32, 32]
    occ    : float32 [1, 32, 32, 32]
    """
    occupied = occ[0] > 0.5
    coords = np.argwhere(occupied)
    if len(coords) == 0:
        return colors, occ

    centroid = coords.mean(axis=0).astype(int)  # (cx, cy, cz)
    grid_center = np.array([16, 16, 16])
    shift = grid_center - centroid

    for ax, s in enumerate(shift):
        colors = np.roll(colors, int(s), axis=ax + 1)
        occ = np.roll(occ, int(s), axis=ax + 1)

    return colors, occ


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def voxel_to_schem(dataset_idx: int, out_path: str) -> None:
    """
    Load the sample at dataset_idx, centre its voxel mass, convert each
    occupied voxel to a Minecraft block via the existing col2block KDTree
    matcher, and write a .schem file to out_path.

    out_path  full path including .schem extension,
              e.g. "/tmp/gen_abc123/generated.schem"
    """
    sample = _dataset[dataset_idx]

    colors = np.array(sample["voxels_colors"], dtype=np.float32)    # [3,32,32,32]
    occ = np.array(sample["voxels_occupancy"], dtype=np.float32)    # [1,32,32,32]

    colors, occ = _center_voxels(colors, occ)

    schem = mcschematic.MCSchematic()
    occupied_mask = occ[0] > 0.5

    for x in range(32):
        for y in range(32):
            for z in range(32):
                if occupied_mask[x, y, z]:
                    r = float(colors[0, x, y, z])
                    g = float(colors[1, x, y, z])
                    b = float(colors[2, x, y, z])
                    block_name = col2block([r, g, b, 1.0])
                    schem.setBlock((x, y, z), f"minecraft:{block_name}")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # mcschematic.save(directory, name, version) appends .schem automatically.
    schem.save(str(out.parent), out.stem, mcschematic.Version.JE_1_21_5)
