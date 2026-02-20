from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/generate")
async def generate(data: dict):
    print("Prompt:", data["prompt"])
    return {"schematic_path": "test.schem"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)