from fastapi import FastAPI
from pydantic import BaseModel
import os
import shutil

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(data: GenerateRequest):
    
    # Your logic from the image
    schem_filename = "test.schem"
    # ... os.path logic here ...
    
    print("Prompt:", data.prompt)
    return {"schematic_path": schem_filename, "voxels": [{"x":0, "y":0, "z":0}]}

@app.get("/test")
async def test():
    return {"message": "API is working!"}

# Vercel doesn't need uvicorn.run(), but your local test does:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5328)

