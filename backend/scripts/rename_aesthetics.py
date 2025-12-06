#!/usr/bin/env python3
"""
Rename aesthetic images with source prefix:
- banana- for Gemini/Banana generated images (early commits)
- unsplash- for Unsplash downloaded images (later commits)
"""

import os
from pathlib import Path

AESTHETICS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/aesthetics")

# Files from early commits (400441a and 17296b4) - Banana/Gemini generated
BANANA_FILES = [
    # From 400441a
    "artist-studio", "bookshop", "boutique", "cafe-table", "cobblestone",
    "palais-royal", "rain-window", "rooftop", "seine-bank", "tuileries",
    # From 17296b4
    "amalfi", "atomic-age", "bamboo-grove", "beach-sunset", "botanical-garden",
    "brutalist", "cafe-paris", "chandelier", "coastal-living", "courtyard",
    "eames-chair", "fashion-runway", "fountain-plaza", "gallery-modern",
    "garden-french", "gothic-arch", "grand-lobby", "hotel-lobby", "interior-luxury",
    "library-classic", "louvre", "maldives-water", "marble-floor", "midcentury-living",
    "montmartre", "neon-tokyo", "opera-hall", "paris-eiffel", "penthouse-view",
    "pont-neuf", "silk-texture", "staircase", "stone-texture", "terrace-view",
    "tropical-palm", "velvet-drape", "vintage-mirror", "window-light", "wood-grain",
]

def main():
    print("=" * 60)
    print("Renaming aesthetic images with source prefixes")
    print("=" * 60)

    renamed_banana = 0
    renamed_unsplash = 0
    skipped = 0

    # Get all jpg files
    all_files = list(AESTHETICS_DIR.glob("*.jpg"))

    for filepath in all_files:
        filename = filepath.stem  # without extension

        # Skip if already prefixed
        if filename.startswith("banana-") or filename.startswith("unsplash-"):
            skipped += 1
            continue

        # Check if it's a banana file
        is_banana = any(filename == bf or filename.startswith(bf + "-") for bf in BANANA_FILES)

        if is_banana:
            new_name = f"banana-{filename}.jpg"
            prefix = "banana"
            renamed_banana += 1
        else:
            new_name = f"unsplash-{filename}.jpg"
            prefix = "unsplash"
            renamed_unsplash += 1

        new_path = AESTHETICS_DIR / new_name

        print(f"  {prefix}: {filename}.jpg -> {new_name}")
        filepath.rename(new_path)

    print("\n" + "=" * 60)
    print(f"COMPLETE")
    print(f"  Renamed to banana-*: {renamed_banana}")
    print(f"  Renamed to unsplash-*: {renamed_unsplash}")
    print(f"  Already prefixed (skipped): {skipped}")
    print("=" * 60)

if __name__ == "__main__":
    main()
