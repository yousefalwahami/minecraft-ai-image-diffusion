from fastapi import FastAPI
from pydantic import BaseModel
import os
import shutil

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str


def generate_dummy_voxels(size: int = 5) -> list[dict]:
    """Return a hollow-shell voxel grid for testing the 3D renderer."""
    voxels = []
    for x in range(size):
        for y in range(size):
            for z in range(size):
                # Keep only the outer shell (floor + four walls)
                if x == 0 or x == size - 1 or z == 0 or z == size - 1 or y == 0:
                    voxels.append({"x": x, "y": y, "z": z})
    return voxels


@app.post("/generate")
async def generate(data: GenerateRequest):
    print("Prompt:", data.prompt)

    # ── Test / demo shortcut ──────────────────────────────────────────────────
    if data.prompt == "test":
        voxels = generate_dummy_voxels(size=5)
        return {"schematic_path": None, "voxels": voxels, "test": True}
    # ─────────────────────────────────────────────────────────────────────────

    # Your real generation logic goes here
    schem_filename = "test.schem"
    # ... os.path logic here ...

    return {"schematic_path": schem_filename, "voxels": [{"x": 0, "y": 0, "z": 0}]}

@app.get("/test")
async def test():
    return {"message": "API is working!"}

# Vercel doesn't need uvicorn.run(), but your local test does:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5328)

