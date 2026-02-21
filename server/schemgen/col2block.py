import colour
import numpy as np
import pickle
from pathlib import Path
from typing import Any

root_dir = Path(__file__).parent

# Pickle file paths
kdtree_path = root_dir / "kdtree.pkl"
colors_path = root_dir / "colors.pkl"
col2tex_map_path = root_dir / "col2tex_map.pkl"

# Global variables for the loaded data
tree: Any = None
colors: Any = None
col2tex_map: Any = None


def load_pickle_data(force_preprocess=False):
    """Load pickle data, running preprocessing if needed or forced"""
    global tree, colors, col2tex_map

    # Check if pickle files exist
    files_exist = (
        kdtree_path.exists() and colors_path.exists() and col2tex_map_path.exists()
    )

    if force_preprocess or not files_exist:
        if force_preprocess:
            print("Force preprocessing enabled, regenerating pickle files...")
        else:
            print("Pickle files not found, running preprocessing...")

        # Import and run preprocessing
        try:
            from . import preprocess
        except ImportError:
            # Fallback for when running as script
            import preprocess
        preprocess.preprocess()

    # Load the pickle files
    with open(kdtree_path, "rb") as f:
        tree = pickle.load(f)

    with open(colors_path, "rb") as f:
        colors = pickle.load(f)

    with open(col2tex_map_path, "rb") as f:
        col2tex_map = pickle.load(f)


# Load data on module import
load_pickle_data()


def col2block(color) -> str:
    """
    takes a normalised RGBA color and returns the closest matching block name
    """
    oklab_value = colour.convert(np.array(color[:3]), "sRGB", "Oklab")
    oklab_value = np.array(
        [oklab_value[0], oklab_value[1], oklab_value[2], color[3]], dtype=np.float32
    )

    dist, ind = tree.query([oklab_value])

    return col2tex_map[tuple(*colors[ind][0])]
