"""
Generates a test.schem (Sponge Schematic v2) — a small 7x5x7 stone house
with oak plank floor, glass windows, and oak log corners.

Run: python generate_test_schem.py
Requires: pip install nbtlib
"""

import nbtlib

W, H, L = 7, 5, 7  # width, height, length

def block(x, y, z):
    """Return the block state string for this position."""
    on_floor = (y == 0)
    on_ceiling = (y == H - 1)
    on_x_wall = (x == 0 or x == W - 1)
    on_z_wall = (z == 0 or z == L - 1)
    on_corner = (x == 0 or x == W - 1) and (z == 0 or z == L - 1)
    on_wall = on_x_wall or on_z_wall
    is_door = (x == W // 2 and z == 0 and y in (1, 2))
    is_window = (on_wall and not on_corner and y in (2, 3) and not is_door)

    if on_floor:
        return "minecraft:oak_planks"
    if on_ceiling:
        return "minecraft:stone_bricks"
    if on_corner:
        return "minecraft:oak_log"
    if is_door:
        return "minecraft:air"
    if is_window:
        return "minecraft:glass"
    if on_wall:
        return "minecraft:stone_bricks"
    return "minecraft:air"  # interior

def encode_varint(value):
    out = []
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return out

def main():
    # Build the palette from all unique block states used
    palette_set = set()
    grid = []
    for y in range(H):
        for z in range(L):
            for x in range(W):
                b = block(x, y, z)
                palette_set.add(b)
                grid.append(b)

    palette_list = sorted(palette_set)
    palette_map  = {b: i for i, b in enumerate(palette_list)}

    block_data = []
    for b in grid:
        block_data.extend(encode_varint(palette_map[b]))

    schem = nbtlib.Compound({
        "Version":     nbtlib.Int(2),
        "DataVersion": nbtlib.Int(3953),
        "Width":       nbtlib.Short(W),
        "Height":      nbtlib.Short(H),
        "Length":      nbtlib.Short(L),
        "PaletteMax":  nbtlib.Int(len(palette_list)),
        "Palette":     nbtlib.Compound({b: nbtlib.Int(i) for b, i in palette_map.items()}),
        "BlockData":   nbtlib.ByteArray([b if b < 128 else b - 256 for b in block_data]),
        "Offset":      nbtlib.IntArray([0, 0, 0]),
    })

    nbt_file = nbtlib.File(schem, gzipped=True)
    nbt_file.save("test.schem")
    print(f"Saved test.schem  ({W}x{H}x{L}, {sum(1 for b in grid if b != 'minecraft:air')} non-air blocks)")

if __name__ == "__main__":
    main()
