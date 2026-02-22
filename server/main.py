import os
import shutil
import tempfile

import nbtlib
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from retrieval.retrieve import index_size, load_index, retrieve
from retrieval.voxel_to_schem import voxel_to_schem

app = FastAPI()

WORLDEDIT_SCHEMATICS_DIR = os.path.expandvars(r"%APPDATA%\.minecraft\config\worldedit\schematics")


class GenerateRequest(BaseModel):
    prompt: str


def parse_schematic_blocks(path: str):
    try:
        schem = nbtlib.load(path)
        width  = int(schem["Width"])
        height = int(schem["Height"])
        length = int(schem["Length"])

        # Reverse palette: palette_id -> block state string
        palette = {int(v): k for k, v in schem["Palette"].items()}

        # Decode varint-encoded BlockData
        raw = bytes(schem["BlockData"])
        blocks = []
        i = 0
        idx = 0
        while i < len(raw):
            value = 0
            bits = 0
            while True:
                b = raw[i]; i += 1
                value |= (b & 0x7F) << bits
                bits += 7
                if not (b & 0x80):
                    break
            bx = idx % width
            bz = (idx // width) % length
            by = idx // (width * length)
            state = palette.get(value, "minecraft:air")
            if "air" not in state:
                blocks.append({"x": bx, "y": by, "z": bz, "b": state})
            idx += 1

        # Sort bottom to top for build-up animation
        blocks.sort(key=lambda b: b["y"])
        return blocks, width, height, length
    except Exception as e:
        print(f"Error parsing schematic: {e}")
        return [], 0, 0, 0


@app.on_event("startup")
async def startup():
    load_index()


@app.get("/health")
async def health():
    return {"status": "ok", "index_size": index_size()}


@app.post("/generate")
async def generate(data: GenerateRequest):
    print("Prompt:", data.prompt)

    dataset_idx = retrieve(data.prompt)
    print(f"Retrieved dataset index: {dataset_idx}")

    with tempfile.TemporaryDirectory() as tmpdir:
        schem_name = "generated"
        schem_path = os.path.join(tmpdir, f"{schem_name}.schem")

        voxel_to_schem(dataset_idx, schem_path)

        # Read schematic while the temp dir is still alive
        blocks, width, height, length = parse_schematic_blocks(schem_path)
        print(f"Schematic: {width}x{height}x{length}, {len(blocks)} non-air blocks")

        # Copy to WorldEdit schematics dir for in-game use
        dest_path = os.path.join(WORLDEDIT_SCHEMATICS_DIR, f"{schem_name}.schem")
        os.makedirs(WORLDEDIT_SCHEMATICS_DIR, exist_ok=True)
        shutil.copy2(schem_path, dest_path)

    return {
        "schematic_path": f"{schem_name}.schem",
        "width": width,
        "height": height,
        "length": length,
        "blocks": blocks,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
