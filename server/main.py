from fastapi import FastAPI
from pydantic import BaseModel
import shutil
import os
import uvicorn

app = FastAPI()

# WorldEdit schematics folder for singleplayer Fabric
WORLDEDIT_SCHEMATICS_DIR = os.path.expandvars(r"%APPDATA%\.minecraft\config\worldedit\schematics")
SCHEMATICS_SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(data: GenerateRequest):
    print("Prompt:", data.prompt)

    # For now, use the test schematic — replace this with real generation later
    schem_filename = "test.schem"
    source_path = os.path.join(SCHEMATICS_SOURCE_DIR, schem_filename)
    dest_path = os.path.join(WORLDEDIT_SCHEMATICS_DIR, schem_filename)

    os.makedirs(WORLDEDIT_SCHEMATICS_DIR, exist_ok=True)
    shutil.copy2(source_path, dest_path)
    print(f"Copied schematic to {dest_path}")

    return {"schematic_path": schem_filename}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)