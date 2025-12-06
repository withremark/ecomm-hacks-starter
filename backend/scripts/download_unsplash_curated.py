#!/usr/bin/env python3
"""
Download curated aesthetic images from Unsplash.
Aligned with Warren's aesthetic manifesto:
- 4pm Paris golden light
- Wong Kar Wai cinematic
- Matte paper / drafting table feel
- Vermillion accents, warm muted tones
- Mono no aware (bittersweet impermanence)
- East meets West
- NOT stock photo style
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

# Curated searches based on Warren's aesthetic manifesto
AESTHETIC_SEARCHES = [
    # 4pm Paris / Golden Hour Interior
    ("afternoon light window interior", "afternoon-window", 3),
    ("golden hour room shadows", "golden-room", 2),
    ("paris cafe interior vintage", "paris-cafe", 3),
    ("window light curtain soft", "window-curtain", 2),

    # Wong Kar Wai / Cinematic
    ("neon rain night moody", "neon-rain", 2),
    ("film noir shadows", "film-noir", 2),
    ("hong kong night cinematic", "hk-night", 2),
    ("rainy window reflection", "rain-glass", 3),

    # Texture / Materiality / Drafting Table
    ("old paper texture vintage", "paper-texture", 2),
    ("pencil sketch drawing", "pencil-sketch", 2),
    ("aged leather book", "aged-leather", 2),
    ("linen fabric texture natural", "linen-texture", 2),
    ("wooden desk workspace artist", "artist-desk", 2),

    # Vermillion / Warm Muted
    ("red silk chinese", "red-silk", 2),
    ("terracotta warm interior", "terracotta", 2),
    ("rust color texture", "rust-warm", 2),
    ("burgundy velvet dark", "burgundy-dark", 2),

    # East Meets West
    ("japanese interior minimal wood", "japanese-interior", 3),
    ("zen garden stones", "zen-garden", 2),
    ("shanghai architecture vintage", "shanghai-vintage", 2),
    ("chinese calligraphy ink", "calligraphy", 2),
    ("tatami room light", "tatami-light", 2),

    # Mono no Aware / Melancholy
    ("autumn leaves melancholy", "autumn-mood", 2),
    ("foggy morning solitude", "foggy-solitude", 2),
    ("abandoned piano room", "piano-room", 2),
    ("faded photograph vintage", "faded-photo", 2),
    ("empty chair window", "empty-chair", 2),

    # Architectural / Contemplative Space
    ("museum empty light", "museum-light", 2),
    ("staircase shadow light", "staircase-light", 2),
    ("courtyard european light", "courtyard-euro", 2),
    ("archway shadow stone", "archway-shadow", 2),

    # Artistic / Painterly
    ("oil painting texture", "oil-paint", 2),
    ("watercolor wash abstract", "watercolor", 2),
    ("impressionist light blur", "impressionist", 2),
    ("chiaroscuro portrait", "chiaroscuro", 2),
]

request_count = 0
MAX_REQUESTS = 48  # Leave buffer for rate limit (50/hr)


def search_unsplash(query: str, per_page: int = 5) -> list:
    """Search Unsplash for images."""
    global request_count

    if request_count >= MAX_REQUESTS:
        print(f"  ⚠️  Rate limit approaching ({request_count} requests), stopping")
        return []

    url = f"{BASE_URL}/search/photos"
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "order_by": "relevant",
    }

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        request_count += 1

        if resp.status_code == 403:
            print(f"  ⚠️  Rate limited! Stopping downloads.")
            return []

        resp.raise_for_status()
        data = resp.json()

        images = []
        for result in data.get("results", []):
            urls = result.get("urls", {})
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
        print(f"  Error: {e}")
        return []


def download_image(url: str, dest_path: Path) -> bool:
    """Download an image to the specified path."""
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        final_path = dest_path.with_suffix(".jpg")
        final_path.write_bytes(resp.content)
        print(f"    ✓ {final_path.name} ({len(resp.content) // 1024}KB)")
        return True
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False


def get_unique_filename(base_name: str) -> str:
    """Generate a unique filename that doesn't exist yet."""
    if not (AESTHETICS_DIR / f"{base_name}.jpg").exists():
        return base_name
    counter = 2
    while (AESTHETICS_DIR / f"{base_name}-{counter}.jpg").exists():
        counter += 1
    return f"{base_name}-{counter}"


def main():
    global request_count

    print("=" * 60)
    print("Unsplash Curated Aesthetic Downloader")
    print("=" * 60)
    print("Warren's Aesthetic: 4pm Paris, Wong Kar Wai, mono no aware")
    print(f"Rate limit: {MAX_REQUESTS} requests")
    print("=" * 60)

    downloaded = 0

    for search_query, name_prefix, count in AESTHETIC_SEARCHES:
        if request_count >= MAX_REQUESTS:
            print("\n⚠️  Reached rate limit, stopping.")
            break

        print(f"\n🔍 {search_query}")
        images = search_unsplash(search_query, per_page=count + 1)

        if not images:
            continue

        print(f"   Found {len(images)} results (request #{request_count})")

        for img in images[:count]:
            if request_count >= MAX_REQUESTS:
                break

            filename = get_unique_filename(name_prefix)
            dest = AESTHETICS_DIR / f"{filename}.jpg"

            desc = img['description'][:40] + "..." if len(img['description']) > 40 else img['description']
            print(f"   📸 {img['photographer']}: {desc}")

            if download_image(img["url"], dest):
                downloaded += 1

            time.sleep(0.2)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Downloaded {downloaded} images")
    print(f"API requests used: {request_count}/{MAX_REQUESTS}")
    print("=" * 60)

    # List all files
    all_files = sorted(AESTHETICS_DIR.glob("*.jpg"))
    print(f"\n📁 Total aesthetic images: {len(all_files)}")


if __name__ == "__main__":
    main()
