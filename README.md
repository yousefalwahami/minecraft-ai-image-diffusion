# Minecraft AI Voxel Diffusion

A text-to-Minecraft-build system. Type `/build <prompt>` in-game and a structure is generated and placed in the world block by block, animated over ~10 seconds.

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
  Parses schematic / runs diffusion model
  Returns voxel block list as JSON
        │
        ▼
 Fabric Mod animates block placement in-world (~10 s)
```

---

## Requirements

| Tool                     | Version |
| ------------------------ | ------- |
| Java JDK                 | 21+     |
| Python                   | 3.11+   |
| Minecraft                | 1.21.11 |
| Fabric Loader            | 0.18.2+ |
| Node.js _(website only)_ | 20+     |

---

## Setup

### 1. Install Fabric

1. Download the Fabric Installer from [fabricmc.net/use/installer](https://fabricmc.net/use/installer/)
2. Run it, select Minecraft **1.21.11**, and click **Install**
3. Open the Minecraft Launcher and select the new **Fabric** profile

### 2. Install Required Mods

Copy these files from the `mods/` folder in this repo into your Minecraft mods folder:

- `fabric-api-0.141.3+1.21.11.jar`
- `worldedit-mod-7.4.0.jar`

**Mods folder location:**

- **Windows:** `%appdata%\.minecraft\mods\`
- **macOS:** `~/Library/Application Support/minecraft/mods/`
- **Linux:** `~/.minecraft/mods/`

> You can paste `%appdata%\.minecraft\mods\` directly into the Windows File Explorer address bar.

### 3. Build and Install the Fabric Mod

**Windows (CMD):**

```cmd
cd D:\path\to\minecraft-ai-image-diffusion
gradlew build
```

**Windows (PowerShell) / macOS / Linux:**

```bash
./gradlew build
```

This produces `build/libs/ai_voxel_image_diffusion-1.0.0.jar`.  
Copy that file into your Minecraft mods folder (same location as step 2).

> If you get `java is not recognized`, make sure Java 21 is installed and on your PATH, or use the full path e.g. `"C:\Program Files\Java\jdk-21\bin\java"`.

### 4. Start the Inference Server

```bash
cd server
pip install -r requirements.txt

# (First time only) Generate the test schematic:
python generate_test_schem.py

python main.py     # starts on http://localhost:8000
```

The server must be running before you use `/build` in-game.

### 5. Launch Minecraft

1. Open the Minecraft Launcher
2. Select the **Fabric 1.21.11** profile and click **Play**
3. Load a singleplayer world (or connect to a server with the mod installed)

---

## In-Game Usage

```
/build <description>
```

Examples:

```
/build a small stone house
/build medieval castle with towers
/build wooden cabin in a forest style
```

- Face the direction you want the building to appear
- The structure is placed **in front of you**, centered on your crosshair
- Blocks animate from the ground up over ~10 seconds

---

## Repository Structure

| Path                            | Description                                 |
| ------------------------------- | ------------------------------------------- |
| `src/`                          | Fabric mod source (Java, Minecraft 1.21.11) |
| `src/.../command/`              | `/build` command — HTTP, planner, animator  |
| `server/`                       | Python inference server (FastAPI)           |
| `server/main.py`                | Entry point — `POST /generate` endpoint     |
| `server/generate_test_schem.py` | Generates a test `.schem` schematic         |
| `mods/`                         | Pre-built mod JARs (Fabric API, WorldEdit)  |
| `website/`                      | Next.js + Three.js 3D web preview           |

---

## How the Mod Works

- **`BuildCommand`** — registers `/build <description>`, sends a `POST /generate` to the inference server asynchronously
- **`BuildPlanner`** — parses the JSON block list, snaps placement to the nearest 90° cardinal direction, and centres the structure in front of the player
- **`BuildAnimator`** — places blocks in batches (~200 ticks = 10 s) sorted bottom-to-top for the build-up effect

---

## Current Status

| Component                            | Status         |
| ------------------------------------ | -------------- |
| `/build` command + block animator    | ✅ Working     |
| `.schem` parsing & block placement   | ✅ Working     |
| Directional placement (faces player) | ✅ Working     |
| Three.js web preview                 | ✅ Working     |
| Schemgen colour → block pipeline     | ✅ Working     |
| Diffusion model (3D U-Net + CLIP)    | 🔄 In progress |
| Real inference endpoint              | 🔄 In progress |
| Dataset preprocessing / block2vec    | 🔄 In progress |

---

## Troubleshooting

| Problem                           | Fix                                                                         |
| --------------------------------- | --------------------------------------------------------------------------- |
| `java is not recognized`          | Install Java 21 and add it to your PATH, then restart your terminal/VS Code |
| `./gradlew` not recognized in CMD | Use `gradlew` (no `./`) in CMD; use `.\gradlew` in PowerShell               |
| `[Build] HTTP request failed`     | Make sure `python main.py` is running in the `server/` folder               |
| Mod doesn't appear in-game        | Check the jar is in `.minecraft/mods/` and Fabric Loader is installed       |
| Blocks place only 1 block         | Re-run `python generate_test_schem.py` to regenerate `test.schem`           |
