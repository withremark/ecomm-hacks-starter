#!/usr/bin/env python3
"""
Download images from Are.na channels for prototype assets.
Organizes into products (by brand) and aesthetics (by mood/style).
"""

import requests
import os
import time
from pathlib import Path
from urllib.parse import urlparse
import json

BASE_URL = "https://api.are.na/v2"
PRODUCTS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/products")
AESTHETICS_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets/aesthetics")

# Channels to fetch from - curated list
PRODUCT_CHANNELS = [
    "jewelry-5kis7uizdlo",
    "jewelry-cfkrqjy3s6i",
    "jewelry-metalwork",
    "jewelry-inspo-oc3gz11e0xm",
    "jewelry-with-juice",
]

AESTHETIC_CHANNELS = [
    "interior-architecture-2ju5x_vf6sg",
]

# Additional search queries to find more channels
PRODUCT_SEARCHES = ["luxury bags", "designer accessories", "watches luxury", "fashion editorial"]
AESTHETIC_SEARCHES = ["brutalist architecture", "japanese interior", "art deco", "scandinavian design", "museum architecture"]


def get_channel_contents(slug: str, per: int = 100) -> list:
    """Fetch all image blocks from a channel."""
    url = f"{BASE_URL}/channels/{slug}/contents"
    params = {"per": per}

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Filter for image blocks only
        images = []
        contents = data.get("contents", [])
        for block in contents:
            if block.get("class") == "Image" and block.get("image"):
                img_data = block["image"]
                # Prefer display size, fall back to original
                img_url = img_data.get("display", {}).get("url") or img_data.get("original", {}).get("url")
                if img_url:
                    images.append({
                        "url": img_url,
                        "title": block.get("title") or block.get("generated_title") or "",
                        "id": block.get("id"),
                    })
        return images
    except Exception as e:
        print(f"  Error fetching channel {slug}: {e}")
        return []


def search_channels(query: str, per: int = 5) -> list:
    """Search for channels and return their slugs."""
    url = f"{BASE_URL}/search/channels"
    params = {"q": query, "per": per}

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        slugs = []
        for channel in data.get("channels", []):
            if channel.get("slug"):
                slugs.append(channel["slug"])
        return slugs
    except Exception as e:
        print(f"  Error searching for '{query}': {e}")
        return []


def download_image(url: str, dest_path: Path) -> bool:
    """Download an image to the specified path."""
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        # Determine extension from content type
        content_type = resp.headers.get("content-type", "image/jpeg")
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        else:
            ext = ".jpg"

        # Update extension if needed
        if dest_path.suffix != ext:
            dest_path = dest_path.with_suffix(ext)

        dest_path.write_bytes(resp.content)
        return True
    except Exception as e:
        print(f"    Failed to download: {e}")
        return False


def get_next_brand_number(brand: str) -> int:
    """Get the next available number for a brand."""
    existing = list(PRODUCTS_DIR.glob(f"{brand}-*"))
    if not existing:
        return 1

    numbers = []
    for f in existing:
        try:
            num = int(f.stem.split("-")[-1])
            numbers.append(num)
        except ValueError:
            pass

    return max(numbers, default=0) + 1


def get_next_aesthetic_name(base_name: str) -> str:
    """Generate a unique aesthetic filename."""
    # Clean the name
    name = base_name.lower().replace(" ", "-").replace("_", "-")
    name = "".join(c for c in name if c.isalnum() or c == "-")
    name = "-".join(filter(None, name.split("-")))  # Remove empty parts

    if not name:
        name = "aesthetic"

    # Check if exists
    test_path = AESTHETICS_DIR / f"{name}.jpg"
    if not test_path.exists():
        return name

    # Add number suffix
    counter = 2
    while (AESTHETICS_DIR / f"{name}-{counter}.jpg").exists():
        counter += 1
    return f"{name}-{counter}"


def main():
    print("=" * 60)
    print("Are.na Image Downloader for Prototype Assets")
    print("=" * 60)

    downloaded_products = 0
    downloaded_aesthetics = 0
    target_total = 30

    # Brand mapping for jewelry -> specific brands
    jewelry_brands = ["cartier", "bulgari", "tiffany", "van-cleef"]
    brand_index = 0

    # === PRODUCTS: Jewelry Channels ===
    print("\n[PRODUCTS] Fetching from jewelry channels...")

    for channel_slug in PRODUCT_CHANNELS:
        print(f"\n  Channel: {channel_slug}")
        images = get_channel_contents(channel_slug, per=20)
        print(f"    Found {len(images)} images")

        for img in images[:5]:  # Max 5 per channel
            brand = jewelry_brands[brand_index % len(jewelry_brands)]
            num = get_next_brand_number(brand)
            filename = f"{brand}-{num}"
            dest = PRODUCTS_DIR / f"{filename}.jpg"

            print(f"    Downloading as {filename}...")
            if download_image(img["url"], dest):
                downloaded_products += 1
                brand_index += 1

            time.sleep(0.3)  # Be nice to the API

            if downloaded_products >= 15:
                break

        if downloaded_products >= 15:
            break

    # === PRODUCTS: Search for more brands ===
    print("\n[PRODUCTS] Searching for luxury fashion channels...")

    # Map searches to brands
    search_brand_map = {
        "luxury bags": ["bottega", "balenciaga", "valentino"],
        "designer accessories": ["versace", "burberry", "ysl"],
        "watches luxury": ["patek", "audemars", "iwc"],
    }

    for search_query, brands in search_brand_map.items():
        if downloaded_products >= 20:
            break

        print(f"\n  Searching: {search_query}")
        channel_slugs = search_channels(search_query, per=3)

        for slug in channel_slugs:
            if downloaded_products >= 20:
                break

            images = get_channel_contents(slug, per=10)
            print(f"    Channel {slug}: {len(images)} images")

            for i, img in enumerate(images[:3]):
                brand = brands[i % len(brands)]
                num = get_next_brand_number(brand)
                filename = f"{brand}-{num}"
                dest = PRODUCTS_DIR / f"{filename}.jpg"

                print(f"      Downloading as {filename}...")
                if download_image(img["url"], dest):
                    downloaded_products += 1

                time.sleep(0.3)

    # === AESTHETICS ===
    print("\n[AESTHETICS] Fetching from architecture channels...")

    for channel_slug in AESTHETIC_CHANNELS:
        print(f"\n  Channel: {channel_slug}")
        images = get_channel_contents(channel_slug, per=30)
        print(f"    Found {len(images)} images")

        for img in images[:10]:
            title = img.get("title") or f"architecture-{img['id']}"
            name = get_next_aesthetic_name(title)
            dest = AESTHETICS_DIR / f"{name}.jpg"

            print(f"    Downloading as {name}...")
            if download_image(img["url"], dest):
                downloaded_aesthetics += 1

            time.sleep(0.3)

    # === AESTHETICS: Search for more styles ===
    print("\n[AESTHETICS] Searching for more aesthetic channels...")

    for search_query in AESTHETIC_SEARCHES:
        if downloaded_aesthetics >= 15:
            break

        print(f"\n  Searching: {search_query}")
        channel_slugs = search_channels(search_query, per=2)

        for slug in channel_slugs:
            if downloaded_aesthetics >= 15:
                break

            images = get_channel_contents(slug, per=10)
            print(f"    Channel {slug}: {len(images)} images")

            for img in images[:3]:
                title = img.get("title") or search_query.replace(" ", "-")
                name = get_next_aesthetic_name(title)
                dest = AESTHETICS_DIR / f"{name}.jpg"

                print(f"      Downloading as {name}...")
                if download_image(img["url"], dest):
                    downloaded_aesthetics += 1

                time.sleep(0.3)

    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Products downloaded: {downloaded_products}")
    print(f"Aesthetics downloaded: {downloaded_aesthetics}")
    print(f"Total: {downloaded_products + downloaded_aesthetics}")

    # List new files
    print("\n[NEW PRODUCT FILES]")
    for f in sorted(PRODUCTS_DIR.glob("*")):
        print(f"  {f.name}")

    print("\n[NEW AESTHETIC FILES]")
    for f in sorted(AESTHETICS_DIR.glob("*")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
