from fastapi import FastAPI
from pydantic import BaseModel
import shutil
import os
import nbtlib
import uvicorn

app = FastAPI()

WORLDEDIT_SCHEMATICS_DIR = os.path.expandvars(r"%APPDATA%\.minecraft\config\worldedit\schematics")
SCHEMATICS_SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

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

@app.post("/generate")
async def generate(data: GenerateRequest):
    print("Prompt:", data.prompt)

    schem_filename = "test.schem"
    source_path = os.path.join(SCHEMATICS_SOURCE_DIR, schem_filename)
    dest_path = os.path.join(WORLDEDIT_SCHEMATICS_DIR, schem_filename)
    os.makedirs(WORLDEDIT_SCHEMATICS_DIR, exist_ok=True)
    shutil.copy2(source_path, dest_path)

    blocks, width, height, length = parse_schematic_blocks(source_path)
    print(f"Schematic: {width}x{height}x{length}, {len(blocks)} non-air blocks")

    return {
        "schematic_path": schem_filename,
        "width": width,
        "height": height,
        "length": length,
        "blocks": blocks
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)