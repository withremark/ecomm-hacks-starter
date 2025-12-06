#!/usr/bin/env python3
"""
Download aesthetic/mood images from Unsplash.
Focus on: viby, atmospheric, artistic, emotionally resonant imagery.
NOT stock photo style.
"""

import requests
import time
from pathlib import Path

AESTHETICS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/aesthetics")
ACCESS_KEY = "jvgc33DGh0ybKSiU5tJ-Idl_8H_Z55YDjvcYX1eMcYo"

BASE_URL = "https://api.unsplash.com"
HEADERS = {
    "Authorization": f"Client-ID {ACCESS_KEY}",
    "Accept-Version": "v1",
}

# Artistic, atmospheric search queries - NOT stock photo style
# Each tuple: (search_query, filename_prefix, count)
AESTHETIC_SEARCHES = [
    # Moody & atmospheric
    ("moody interior dark shadows", "moody-interior", 2),
    ("cinematic lighting photography", "cinematic", 2),
    ("fog mist atmospheric landscape", "misty", 2),
    ("golden hour light shadows", "golden-light", 2),

    # Artistic & editorial
    ("fine art still life", "still-life", 2),
    ("abstract architecture lines", "abstract-arch", 2),
    ("minimalist aesthetic space", "minimalist", 2),
    ("editorial fashion artistic", "editorial", 2),

    # Textures & materials
    ("velvet fabric texture luxury", "velvet-texture", 2),
    ("marble stone texture", "marble-texture", 2),
    ("silk satin fabric", "silk-fabric", 2),

    # Spaces & environments
    ("museum gallery empty space", "gallery-space", 2),
    ("vintage antique aesthetic", "vintage", 2),
    ("dark academia library", "dark-academia", 2),
    ("greenhouse botanical", "botanical", 2),

    # Artistic mood
    ("melancholy aesthetic art", "melancholy", 2),
    ("dreamy ethereal soft", "ethereal", 2),
    ("dramatic chiaroscuro light", "chiaroscuro", 2),
]


def search_unsplash(query: str, per_page: int = 5) -> list:
    """Search Unsplash for images."""
    url = f"{BASE_URL}/search/photos"
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",  # Better for backgrounds/aesthetics
        "order_by": "relevant",
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        images = []
        for result in data.get("results", []):
            urls = result.get("urls", {})
            # Use 'regular' size (1080px width) - good quality, not too large
            img_url = urls.get("regular") or urls.get("small")
            if img_url:
                images.append({
                    "url": img_url,
                    "id": result.get("id"),
                    "description": result.get("description") or result.get("alt_description") or "",
                    "photographer": result.get("user", {}).get("name", "Unknown"),
                })
        return images
    except Exception as e:
        print(f"  Error searching '{query}': {e}")
        return []


def download_image(url: str, dest_path: Path) -> bool:
    """Download an image to the specified path."""
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        # Unsplash serves JPEGs
        final_path = dest_path.with_suffix(".jpg")
        final_path.write_bytes(resp.content)
        print(f"    ✓ {final_path.name} ({len(resp.content) // 1024}KB)")
        return True
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False


def get_unique_filename(base_name: str) -> str:
    """Generate a unique filename that doesn't exist yet."""
    # Check if base name already exists
    if not (AESTHETICS_DIR / f"{base_name}.jpg").exists():
        return base_name

    # Add number suffix
    counter = 2
    while (AESTHETICS_DIR / f"{base_name}-{counter}.jpg").exists():
        counter += 1
    return f"{base_name}-{counter}"


def main():
    print("=" * 60)
    print("Unsplash Aesthetic Image Downloader")
    print("=" * 60)
    print("Focus: viby, atmospheric, artistic, emotionally resonant")
    print("NOT stock photo style")
    print("=" * 60)

    downloaded = 0
    target = 30

    for search_query, name_prefix, count in AESTHETIC_SEARCHES:
        if downloaded >= target:
            break

        print(f"\n🔍 Search: {search_query}")
        images = search_unsplash(search_query, per_page=count + 2)  # Get extras in case some fail
        print(f"   Found {len(images)} results")

        for img in images[:count]:
            if downloaded >= target:
                break

            filename = get_unique_filename(name_prefix)
            dest = AESTHETICS_DIR / f"{filename}.jpg"

            print(f"   📸 {img['photographer']}: {img['description'][:50]}..." if img['description'] else f"   📸 {img['photographer']}")
            if download_image(img["url"], dest):
                downloaded += 1

            time.sleep(0.3)  # Rate limit: 50 req/hour for demo

    print("\n" + "=" * 60)
    print(f"COMPLETE: Downloaded {downloaded} aesthetic images")
    print("=" * 60)

    # Show new files
    print("\n📁 New aesthetic files:")
    for f in sorted(AESTHETICS_DIR.glob("*.jpg"))[-downloaded:]:
        print(f"   {f.name}")


if __name__ == "__main__":
    main()
