"""
Generates a minimal valid test.schem (Sponge Schematic v2) containing
a single stone block. Place the output in your WorldEdit schematics folder:

  - Fabric server:  <server_dir>/config/worldedit/schematics/test.schem
  - Single-player:  <minecraft_dir>/config/worldedit/schematics/test.schem

Run: python generate_test_schem.py
Requires: pip install nbtlib
"""

import nbtlib
import numpy as np

def main():
    # A 1x1x1 schematic with a single minecraft:stone block
    schem = nbtlib.Compound({
        "Version":     nbtlib.Int(2),
        "DataVersion": nbtlib.Int(2975),   # MC 1.20.1
        "Width":       nbtlib.Short(1),
        "Height":      nbtlib.Short(1),
        "Length":      nbtlib.Short(1),
        "PaletteMax":  nbtlib.Int(1),
        "Palette": nbtlib.Compound({
            "minecraft:stone": nbtlib.Int(0),
        }),
        # BlockData is a varint-encoded byte array; 0 = our only palette entry
        "BlockData": nbtlib.ByteArray([0]),
        "Offset": nbtlib.IntArray([0, 0, 0]),
    })

    # Sponge schematics are saved as a GZip-compressed unnamed NBT root
    nbt_file = nbtlib.File(schem, gzipped=True)
    output = "test.schem"
    nbt_file.save(output)
    print(f"Saved {output}")
    print("Copy it to:  <server>/config/worldedit/schematics/test.schem")

if __name__ == "__main__":
    main()
