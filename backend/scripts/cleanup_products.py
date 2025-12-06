#!/usr/bin/env python3
"""
Keep only original Banana-generated product images.
Delete all others (from Wikimedia/other sources).
"""

from pathlib import Path

PRODUCTS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/products")

# Original Banana products from earliest commits (400441a, c382d72)
BANANA_PRODUCTS = {
    "acne-1", "acne-2", "acne-3",
    "lv-1", "lv-2", "lv-3",
    "prada-1", "prada-2", "prada-3",
}

def main():
    print("Cleaning up product images - keeping only Banana originals")
    print("=" * 50)

    deleted = 0
    kept = 0

    for f in PRODUCTS_DIR.glob("*"):
        if f.is_file():
            stem = f.stem  # filename without extension
            if stem in BANANA_PRODUCTS:
                print(f"  ✓ KEEP: {f.name}")
                kept += 1
            else:
                print(f"  ✗ DELETE: {f.name}")
                f.unlink()
                deleted += 1

    print("=" * 50)
    print(f"Kept: {kept}, Deleted: {deleted}")

if __name__ == "__main__":
    main()
