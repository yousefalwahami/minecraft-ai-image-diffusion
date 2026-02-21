"""
Script to extract required data from the Minecraft game jar file.
Extracts blockstates, models, and textures into separate zip files.

Set JAR_PATH below to your Minecraft jar file path, then run:
    python extract_from_jar.py
"""

import zipfile
from pathlib import Path
import os

# Get the directory where THIS script is located
root_dir = Path(__file__).parent

# Set this to your Minecraft jar path
# Common locations:
# Windows: C:/Users/<Username>/AppData/Roaming/.minecraft/versions/<version>/<version>.jar
# macOS: ~/Library/Application Support/minecraft/versions/<version>/<version>.jar
# Linux: ~/.minecraft/versions/<version>/<version>.jar
# JAR_PATH = os.environ.get("MINECRAFT_JAR", "minecraft.jar")
JAR_PATH = root_dir / "minecraft-1.21.5-client.jar"


def extract_from_jar():
    """Extract blockstates, models, and textures from Minecraft jar file."""
    jar_path = Path(JAR_PATH).expanduser()
    
    if not jar_path.exists():
        print(f"Error: Jar file not found at {jar_path}")
        print("\nPlease set JAR_PATH in this script to your Minecraft jar file.")
        print("You can also set the MINECRAFT_JAR environment variable.")
        return
    
    if not jar_path.suffix == '.jar':
        print(f"Warning: File doesn't have .jar extension: {jar_path}")
    
    output_dir = root_dir
    
    # Define source paths within the jar and output zip files
    extractions = [
        {
            'name': 'blockstates',
            'jar_prefix': 'assets/minecraft/blockstates/',
            'output_zip': output_dir / 'blockstates.zip'
        },
        {
            'name': 'model',
            'jar_prefix': 'assets/minecraft/models/block/',
            'output_zip': output_dir / 'model.zip'
        },
        {
            'name': 'texture',
            'jar_prefix': 'assets/minecraft/textures/block/',
            'output_zip': output_dir / 'texture.zip'
        }
    ]
    
    print(f"Opening jar file: {jar_path}")
    
    with zipfile.ZipFile(jar_path, 'r') as jar:
        jar_files = jar.namelist()
        
        for extraction in extractions:
            name = extraction['name']
            prefix = extraction['jar_prefix']
            output_zip = extraction['output_zip']
            
            print(f"\nExtracting {name}...")
            print(f"  Source: {prefix}")
            print(f"  Output: {output_zip}")
            
            # Find all files matching the prefix
            matching_files = [f for f in jar_files if f.startswith(prefix) and not f.endswith('/')]
            
            if not matching_files:
                print(f"  Warning: No files found in {prefix}")
                continue
            
            print(f"  Found {len(matching_files)} files")
            
            # Create output zip file
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for file_path in matching_files:
                    # Get the relative path (remove the prefix)
                    relative_path = file_path[len(prefix):]
                    
                    # Read from jar and write to output zip
                    file_data = jar.read(file_path)
                    out_zip.writestr(relative_path, file_data)
            
            print(f"  ✓ Created {output_zip.name} ({len(matching_files)} files)")
    
    print("\n✓ Extraction complete!")
    print(f"Output files saved to: {output_dir}")


if __name__ == '__main__':
    extract_from_jar()
