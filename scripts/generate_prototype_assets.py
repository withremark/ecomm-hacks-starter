"""Generate product and aesthetic images for the Paris Drafting Table prototype."""

import asyncio
import base64
import json
import httpx
from pathlib import Path

API_BASE = "http://localhost:8000"

# Product definitions
PRODUCTS = [
    {"id": "prada-1", "name": "Saffiano Leather Bag", "brand": "Prada", "description": "Classic black saffiano leather handbag with gold hardware"},
    {"id": "prada-2", "name": "Re-Nylon Backpack", "brand": "Prada", "description": "Black regenerated nylon backpack with triangle logo"},
    {"id": "prada-3", "name": "Triangle Logo Sunglasses", "brand": "Prada", "description": "Black acetate sunglasses with iconic triangle detail"},
    {"id": "lv-1", "name": "Neverfull MM", "brand": "Louis Vuitton", "description": "Monogram canvas tote bag with leather trim"},
    {"id": "lv-2", "name": "Keepall 45", "brand": "Louis Vuitton", "description": "Iconic monogram travel duffle bag"},
    {"id": "lv-3", "name": "Capucines Mini", "brand": "Louis Vuitton", "description": "Refined taurillon leather handbag in cream"},
    {"id": "acne-1", "name": "Musubi Bag", "brand": "Acne Studios", "description": "Knotted leather shoulder bag in tan"},
    {"id": "acne-2", "name": "Oversized Wool Scarf", "brand": "Acne Studios", "description": "Chunky knit wool scarf in camel"},
    {"id": "acne-3", "name": "Jensen Boots", "brand": "Acne Studios", "description": "Black leather pointed toe ankle boots"},
]

# Aesthetic prompts for Paris 4pm vibe
AESTHETIC_PROMPTS = [
    ("cafe-table", "A Parisian cafe table at 4pm golden hour, warm afternoon light streaming through lace curtains, marble tabletop with empty espresso cup, film grain texture, romantic nostalgic mood"),
    ("rain-window", "Rain-streaked window in a Paris apartment at dusk, soft diffused light, muted warm colors, impressionist mood, old leather-bound books on windowsill, melancholic beauty"),
    ("cobblestone", "Cobblestone street in Le Marais district Paris, 4pm sunlight casting long shadows, vintage cafe chairs, warm amber tones, expired film aesthetic"),
    ("seine-bank", "Seine riverbank at golden hour, iron bridge silhouette in background, soft focus, romantic atmosphere, nostalgic mood, warm sepia tones"),
    ("boutique", "Vintage Parisian boutique interior, art deco mirrors, soft warm lighting, matte textures, sophisticated elegance, afternoon light through tall windows"),
    ("tuileries", "Tuileries Garden bench in autumn, fallen leaves, late afternoon shadows, warm terracotta and gold tones, peaceful solitude, film photography aesthetic"),
    ("artist-studio", "Montmartre artist studio, large north-facing windows, natural afternoon light, canvases and paint brushes, creative bohemian atmosphere"),
    ("bookshop", "Left Bank bookshop Shakespeare and Company style, stacked leather-bound volumes, dust motes in golden sunlight, timeless intellectual charm"),
    ("palais-royal", "Palais Royal gardens at blue hour, classical columns and fountain, elegant tranquility, soft twilight, refined Parisian atmosphere"),
    ("rooftop", "Parisian rooftop terrace, zinc surfaces and chimney pots, distant Eiffel Tower silhouette, romantic evening light, warm amber glow"),
]

OUTPUT_DIR = Path("/Users/wz/Desktop/zPersonalProjects/StudioTenwu/ecomm-hacks-starter/public/prototype-assets")


async def generate_image(client: httpx.AsyncClient, prompt: str, filename: str, subdir: str) -> bool:
    """Generate a single image and save it."""
    try:
        response = await client.post(
            f"{API_BASE}/api/image/generate",
            json={
                "prompt": prompt,
                "model": "gemini-3-pro-image-preview",
            },
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("images") and len(data["images"]) > 0:
            img = data["images"][0]
            img_data = base64.b64decode(img["data"])

            # Determine extension from mime type
            mime = img.get("mime_type", "image/png")
            ext = "png" if "png" in mime else "jpg" if "jpeg" in mime or "jpg" in mime else "webp"

            output_path = OUTPUT_DIR / subdir / f"{filename}.{ext}"
            output_path.write_bytes(img_data)
            print(f"  Saved: {output_path.name}")
            return True
        else:
            print(f"  No image returned for {filename}")
            return False

    except Exception as e:
        print(f"  Error generating {filename}: {e}")
        return False


async def generate_products(client: httpx.AsyncClient):
    """Generate all product images."""
    print("\n=== Generating Product Images ===\n")

    for i, product in enumerate(PRODUCTS, 1):
        print(f"[{i}/{len(PRODUCTS)}] {product['brand']} - {product['name']}")

        prompt = f"""Professional product photography of a luxury {product['brand']} {product['name']}.
{product['description']}.
Shot on clean white seamless background, high-end fashion commercial photography style.
Soft studio lighting with subtle shadows, pristine product presentation.
No models, no text, no visible logos, just the beautiful product itself.
8K quality, sharp focus on product details."""

        await generate_image(client, prompt, product["id"], "products")


async def generate_aesthetics(client: httpx.AsyncClient):
    """Generate all aesthetic base images."""
    print("\n=== Generating Aesthetic Images ===\n")

    for i, (filename, prompt) in enumerate(AESTHETIC_PROMPTS, 1):
        print(f"[{i}/{len(AESTHETIC_PROMPTS)}] {filename}")

        full_prompt = f"""{prompt}

Artistic photography, cinematic composition, 3:2 aspect ratio.
Shot on medium format film, subtle grain, rich warm tones.
The scene should have an empty surface or space where a luxury product could naturally be placed.
No people, no text, atmospheric and evocative."""

        await generate_image(client, full_prompt, filename, "aesthetics")


async def main():
    """Generate all prototype assets."""
    print("Paris Drafting Table - Asset Generator")
    print("=" * 40)

    # Ensure directories exist
    (OUTPUT_DIR / "products").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "aesthetics").mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient() as client:
        # Check API health
        try:
            health = await client.get(f"{API_BASE}/")
            print(f"API Status: {health.json().get('status', 'unknown')}")
        except Exception as e:
            print(f"Warning: Could not reach API at {API_BASE}: {e}")
            return

        await generate_products(client)
        await generate_aesthetics(client)

    print("\n" + "=" * 40)
    print("Generation complete!")
    print(f"Products saved to: {OUTPUT_DIR / 'products'}")
    print(f"Aesthetics saved to: {OUTPUT_DIR / 'aesthetics'}")


if __name__ == "__main__":
    asyncio.run(main())
