# Minecraft AI Voxel Diffusion

A text-to-Minecraft-build system. Type `/build <prompt>` in-game and a 3D diffusion model generates a voxel structure that is placed in the world, block by block, in real time. A Next.js web app provides a Three.js preview of the same output.

---

## How It Works

```
/build "a medieval castle"
        │
        ▼
 Fabric Mod (Java)
  POST /generate → localhost:8000
        │
        ▼
 Inference Server (Python / FastAPI)
  3D U-Net diffusion model + CLIP conditioning
  returns voxel grid as JSON
        │
        ├──► Fabric Mod animates block placement in-world (~10 s)
        │
        └──► Web preview renders voxels in Three.js
```

---

## Repository Structure

| Path | Description |
|---|---|
| `src/` | Fabric mod (Java, Minecraft 1.21.11) |
| `src/.../command/` | `/build` command — HTTP client, planner, animator |
| `server/` | Python inference server (FastAPI) |
| `server/schemgen/` | Color → block mapping and `.schem` generation utilities |
| `website/` | Next.js 16 frontend with Three.js 3D preview |
| `website/api/` | FastAPI backend for the website |

---

## Components

### 1. Fabric Mod — In-Game `/build` Command

The mod registers a `/build <description>` command (Minecraft 1.21.11, Fabric Loader 0.18.2).

- **`BuildCommand`** — sends a `POST /generate` request to the inference server asynchronously, giving in-game feedback (`Sending request...`, `Placing X blocks...`, `Done!`).
- **`BuildPlanner`** — parses the JSON response, snaps to the player's facing direction (nearest 90°), and centres the structure `PLACE_DISTANCE` blocks ahead of the player.
- **`BuildAnimator`** — places blocks in batches of ~1 batch per tick (50 ms), spreading the full build over ≈ 200 ticks (10 s) so the server doesn't spike.

### 2. Inference Server

`server/main.py` — FastAPI app that:

1. Accepts `POST /generate` with `{ "prompt": "..." }`.
2. *(Currently)* loads a test `.schem` file and parses it into a sorted block list.
3. *(Target)* runs the diffusion model and returns the generated voxel grid.
4. Returns `{ blocks, width, height, length }` — the exact format the Fabric mod expects.

Dependencies: `fastapi`, `uvicorn`, `nbtlib`, `mcschematic`, `scikit-learn`, `colour-science`.

### 3. Schemgen Pipeline

`server/schemgen/` converts ML model output into Minecraft schematics:

- **`col2block.py`** — maps a normalised RGBA colour to the closest Minecraft block using the pre-extracted block colour data in `schemgen/1.21.11/`.
- **`schemgen.py`** — takes a `(W, H, L, 4)` colour array and writes a `.schem` file via `mcschematic`.
- **`preprocess.py`** / **`extract_from_jar.py`** — data-pipeline helpers for extracting block textures and building the colour lookup table from a Minecraft JAR.

### 4. Website

`website/` — Next.js 16 + TypeScript + Tailwind CSS front end.

- Prompt input → `POST /generate` to the FastAPI backend (`website/api/server.py`).
- Three.js scene renders the returned voxel list as instanced cubes with orbit controls.
- The API backend mirrors the inference server interface and can point at the real model or return dummy geometry for testing.

---

## Roles & Workstreams

> The project is split across five overlapping workstreams.

| # | Area | Key tasks |
|---|---|---|
| 1 | **ML / Model** | Design and train the 3D U-Net diffusion model; CLIP text conditioning; DDIM sampling pipeline (noisy grid → clean voxel output) |
| 2 | **Data Processing** | Load/clean the Kaggle Minecraft builds dataset; use `block2vec` from [text2mc-dataprocessor](https://github.com/text2mc/text2mc-dataprocessor) to convert builds to tensors; pre-compute CLIP embeddings; data augmentation (rotations, flips) |
| 3 | **Inference Server** | Keep the model loaded in memory; expose `POST /generate`; handle request queuing so concurrent `/build` calls don't crash the process |
| 4 | **Minecraft Integration** | Minecraft 1.21.11 server with Fabric + WorldEdit; `.schem` → world pipeline; correct block placement; clear old builds before new ones |
| 5 | **Fabric Mod / In-Game UX** | `/build` command; HTTP client to inference server; animated block placement; in-game feedback messages |

---

## Setup

### Prerequisites

- Java 21+
- Python 3.11+
- Node.js 20+
- Minecraft 1.21.11 with Fabric Loader 0.18.2

### Inference Server

```bash
cd server
pip install -r requirements.txt
python main.py          # starts on http://localhost:8000
```

### Fabric Mod

```bash
# from repo root
./gradlew build
# copy build/libs/<mod>.jar into your Minecraft mods/ folder
```

### Website

```bash
cd website
npm install
npm run dev             # Next.js on http://localhost:3000
                        # FastAPI on http://localhost:5328 (via next.config.ts rewrites)
```

---

## Current Status

| Component | Status |
|---|---|
| `/build` command + block animator | Working |
| `.schem` parsing & block placement | Working |
| Three.js web preview | Working |
| Schemgen colour→block pipeline | Working |
| Diffusion model (3D U-Net + CLIP) | In progress |
| Real inference endpoint | In progress |
| Dataset preprocessing / block2vec | In progress |
