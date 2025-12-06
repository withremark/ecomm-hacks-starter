#!/usr/bin/env python3
"""
Download images from Wikimedia Commons for prototype assets.
Uses the free Wikimedia API which doesn't require authentication.
"""

import requests
import os
import time
from pathlib import Path
from urllib.parse import quote

PRODUCTS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/products")
AESTHETICS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/aesthetics")

HEADERS = {
    "User-Agent": "PrototypeAssetDownloader/1.0 (educational project; contact@example.com)"
}

# Product searches mapped to brand names
PRODUCT_SEARCHES = [
    ("Cartier jewelry", ["cartier"]),
    ("Bulgari jewelry", ["bulgari"]),
    ("Van Cleef Arpels", ["van-cleef"]),
    ("Patek Philippe watch", ["patek"]),
    ("Audemars Piguet watch", ["audemars"]),
    ("IWC watch", ["iwc"]),
    ("Bottega Veneta bag", ["bottega"]),
    ("Balenciaga bag", ["balenciaga"]),
    ("Valentino fashion", ["valentino"]),
    ("YSL Saint Laurent", ["ysl"]),
    ("Burberry fashion", ["burberry"]),
    ("Versace fashion", ["versace"]),
]

# Aesthetic searches mapped to name prefixes
AESTHETIC_SEARCHES = [
    ("brutalist architecture building", "brutalist"),
    ("art deco interior", "art-deco"),
    ("japanese minimalist interior", "japanese"),
    ("scandinavian design interior", "scandinavian"),
    ("museum interior architecture", "museum"),
    ("luxury hotel lobby", "hotel-lobby"),
    ("modern gallery interior", "gallery"),
    ("marble architecture", "marble"),
    ("glass architecture modern", "glass-modern"),
    ("industrial loft interior", "industrial"),
]


def search_wikimedia(query: str, limit: int = 5) -> list:
    """Search Wikimedia Commons for images."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # File namespace
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "format": "json",
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        images = []
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            imageinfo = page.get("imageinfo", [])
            if imageinfo:
                info = imageinfo[0]
                mime = info.get("mime", "")
                # Only get actual images (not SVG, PDF, etc.)
                if mime.startswith("image/") and "svg" not in mime:
                    images.append({
                        "url": info.get("url"),
                        "title": page.get("title", ""),
                        "width": info.get("width"),
                        "height": info.get("height"),
                    })
        return images
    except Exception as e:
        print(f"  Error searching for '{query}': {e}")
        return []


def download_image(url: str, dest_path: Path) -> bool:
    """Download an image to the specified path."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()

        # Determine extension from content type
        content_type = resp.headers.get("content-type", "image/jpeg")
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        else:
            ext = ".jpg"

        # Update extension if needed
        final_path = dest_path.with_suffix(ext)
        final_path.write_bytes(resp.content)
        print(f"    ✓ Saved: {final_path.name} ({len(resp.content) // 1024}KB)")
        return True
    except Exception as e:
        print(f"    ✗ Failed to download: {e}")
        return False


def get_next_number(directory: Path, prefix: str) -> int:
    """Get the next available number for a filename prefix."""
    existing = list(directory.glob(f"{prefix}-*"))
    if not existing:
        return 1

    numbers = []
    for f in existing:
        try:
            # Extract number from filename like "brand-3.jpg"
            name = f.stem  # e.g., "brand-3"
            num_part = name.replace(f"{prefix}-", "")
            num = int(num_part)
            numbers.append(num)
        except ValueError:
            pass

    return max(numbers, default=0) + 1


def main():
    print("=" * 60)
    print("Wikimedia Commons Image Downloader")
    print("=" * 60)

    downloaded_products = 0
    downloaded_aesthetics = 0

    # === PRODUCTS ===
    print("\n[PRODUCTS] Searching Wikimedia Commons...")

    for search_query, brands in PRODUCT_SEARCHES:
        print(f"\n  Search: {search_query}")
        images = search_wikimedia(search_query, limit=3)
        print(f"    Found {len(images)} images")

        for i, img in enumerate(images[:2]):  # Max 2 per search
            brand = brands[i % len(brands)]
            num = get_next_number(PRODUCTS_DIR, brand)
            filename = f"{brand}-{num}"
            dest = PRODUCTS_DIR / f"{filename}.jpg"

            if download_image(img["url"], dest):
                downloaded_products += 1

            time.sleep(0.5)  # Be nice to the API

    # === AESTHETICS ===
    print("\n[AESTHETICS] Searching Wikimedia Commons...")

    for search_query, name_prefix in AESTHETIC_SEARCHES:
        print(f"\n  Search: {search_query}")
        images = search_wikimedia(search_query, limit=4)
        print(f"    Found {len(images)} images")

        for i, img in enumerate(images[:2]):  # Max 2 per search
            num = get_next_number(AESTHETICS_DIR, name_prefix)
            if num == 1:
                filename = name_prefix
            else:
                filename = f"{name_prefix}-{num}"
            dest = AESTHETICS_DIR / f"{filename}.jpg"

            if download_image(img["url"], dest):
                downloaded_aesthetics += 1

            time.sleep(0.5)

    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Products downloaded: {downloaded_products}")
    print(f"Aesthetics downloaded: {downloaded_aesthetics}")
    print(f"Total: {downloaded_products + downloaded_aesthetics}")


if __name__ == "__main__":
    main()
