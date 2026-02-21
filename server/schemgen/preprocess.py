import colour
import numpy as np
from PIL import Image
import os
from sklearn.neighbors import KDTree
import json
from pathlib import Path
import pickle
import zipfile
from io import BytesIO

# 1. Get the directory where THIS script is located
root_dir = Path(__file__).parent

def preprocess():
    """Run preprocessing to generate pickle files from zip data"""
    print("Running preprocessing...")
    
    model_zip_path = root_dir / "model.zip"
    texture_zip_path = root_dir / "texture.zip"

    model_data = {}

    # Load model JSON files from zip
    with zipfile.ZipFile(model_zip_path, 'r') as zip_file:
        for filename in zip_file.namelist():
            if filename.endswith(".json"):
                try:
                    with zip_file.open(filename) as f:
                        model_data[os.path.splitext(os.path.basename(filename))[0]] = json.load(f)
                except Exception as e:
                    print(f"Error loading model file {filename}: {e}")

    average_oklab_colors = {}
    block_texture_colors = {}  # New dictionary to store both Oklab-Alpha and RGBA

    # Load texture files from zip
    with zipfile.ZipFile(texture_zip_path, 'r') as zip_file:
        for filename in zip_file.namelist():
            if filename.endswith(".png"):
                try:
                    # Read image data from zip into memory
                    with zip_file.open(filename) as f:
                        img_data = BytesIO(f.read())
                    
                    with Image.open(img_data) as img:
                        # Convert image to RGBA to ensure alpha channel is present
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")

                        pixels = np.array(img)

                        # Separate RGB and Alpha channels
                        rgb_pixels = pixels[:, :, :3]
                        alpha_channel = pixels[:, :, 3]

                        # Normalize RGB to [0, 1] for Oklab conversion
                        rgb_pixels_normalized = rgb_pixels / 255.0

                        # Convert all RGB pixels to Oklab
                        # Reshape for colour.convert, then reshape back
                        oklab_pixels_reshaped = colour.convert(
                            rgb_pixels_normalized.reshape(-1, 3), "sRGB", "Oklab"
                        )
                        oklab_pixels = oklab_pixels_reshaped.reshape(
                            rgb_pixels_normalized.shape
                        )  # Shape (height, width, 3)

                        # Normalize alpha to [0, 1]
                        alpha_normalized = (
                            alpha_channel.astype(np.float32) / 255.0
                        )  # Ensure float32 for consistency

                        # Combine Oklab channels with alpha channel
                        # Expand alpha_normalized to (height, width, 1) for concatenation
                        oklab_alpha_combined = np.concatenate(
                            (oklab_pixels, np.expand_dims(alpha_normalized, axis=2)), axis=2
                        )

                        # Calculate average Oklab-Alpha color for all pixels
                        avg_oklab_alpha = oklab_alpha_combined.mean(axis=(0, 1))

                        # Extract Oklab (L, a, b) and Alpha components
                        oklab_l, oklab_a, oklab_b = avg_oklab_alpha[:3]
                        alpha_component = avg_oklab_alpha[3]

                        # Convert Oklab (L, a, b) to sRGB
                        srgb_value = colour.convert(
                            np.array([oklab_l, oklab_a, oklab_b]), "Oklab", "sRGB"
                        )

                        # Clip sRGB values to [0, 1] range
                        srgb_value = np.clip(srgb_value, 0, 1)

                        # Combine sRGB with alpha to form RGBA
                        rgba_value = np.array(
                            [srgb_value[0], srgb_value[1], srgb_value[2], alpha_component],
                            dtype=np.float32,
                        )

                        # Store in dictionary (filename without extension)
                        name_without_extension = os.path.splitext(os.path.basename(filename))[0]
                        average_oklab_colors[name_without_extension] = avg_oklab_alpha.tolist()

                        # Store both Oklab-Alpha and RGBA in block_texture_colors
                        block_texture_colors[name_without_extension] = {
                            "oklab_alpha": avg_oklab_alpha.tolist(),
                            "rgba": rgba_value.tolist(),
                        }

                except Exception as e:
                    print(f"Could not process {filename}: {e}")

    def filter(k):
        model = model_data.get(k, None)
        return model != None and model.get("parent") == "minecraft:block/cube_all"

    filtered_colors = {k: v for k, v in average_oklab_colors.items() if filter(k)}

    col2tex_map = {}
    for k, v in filtered_colors.items():
        model = model_data.get(k, None)
        col2tex_map[tuple(v)] = k

    colors = np.array(list(filtered_colors.values()))
    tree = KDTree(colors)

    # Save the tree, colors, and col2tex_map to pickle files
    with open(root_dir / "kdtree.pkl", "wb") as f:
        pickle.dump(tree, f)

    with open(root_dir / "colors.pkl", "wb") as f:
        pickle.dump(colors, f)

    with open(root_dir / "col2tex_map.pkl", "wb") as f:
        pickle.dump(col2tex_map, f)
    
    print("Preprocessing complete! Pickle files saved.")


if __name__ == "__main__":
    preprocess()