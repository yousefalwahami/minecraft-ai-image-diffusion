from col2block import col2block
import mcschematic


def make_schem(arr,path, name,version=mcschematic.Version.JE_1_21_5):
    """
    takes a (width, height, length, 4) array of normalised RGBA colors
    and creates a .schem file at the given path with the given name

    Note: we're using the latest game version possible in the entire data pipeline
    don't expect earlier versions to work properly. if you want to use an earlier version,
    provide the resource files for that version and rerun preprocess
    (or go write some new filtering logic ig)
    """
    schem = mcschematic.MCSchematic()
    for x in range(arr.shape[0]):
        for y in range(arr.shape[1]):
            for z in range(arr.shape[2]):
                color = arr[x, y, z]
                block_name = col2block(color)
                schem.setBlock((x, y, z), f"minecraft:{block_name}")
    # feels like just pushing the responsibility somewhere else but it is what it is
    schem.save(path,name,version)
