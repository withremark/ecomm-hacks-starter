#!/usr/bin/env python3
"""Test Nano Banana product integration - place product into scene with outline mask."""

import asyncio
import base64
import os
import httpx
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

async def download_image(url: str) -> bytes:
    """Download image from URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        resp = await client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            raise Exception(f"Failed to download {url}: {resp.status_code}")
        return resp.content

async def test_product_integration():
    """Test placing a product into a scene."""

    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"API Key: {api_key[:10]}..." if api_key else "NO API KEY!")

    client = genai.Client(api_key=api_key)
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    # Download product image (luxury handbag)
    product_url = "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600"
    print(f"\nDownloading product image (handbag)...")
    product_bytes = await download_image(product_url)
    print(f"Product image: {len(product_bytes)} bytes")

    # Save product for reference
    with open(output_dir / "product_original.jpg", "wb") as f:
        f.write(product_bytes)

    # Download background image (cafe setting you provided)
    bg_url = "https://www.coalesse.com/wp-content/uploads/2019/12/2019_CO_Blog-Cafe-Settings-crop-scaled.jpg"
    print(f"Downloading background image (cafe)...")
    bg_bytes = await download_image(bg_url)
    print(f"Background image: {len(bg_bytes)} bytes")

    # Save background for reference
    with open(output_dir / "background_original.jpg", "wb") as f:
        f.write(bg_bytes)

    # Step 1: Edit the background image to add the product
    print("\n--- Step 1: Place product into scene ---")

    # Very explicit prompt
    edit_prompt = """I am providing two images:
1. FIRST IMAGE: A luxury brown leather handbag (the PRODUCT to place)
2. SECOND IMAGE: A cafe setting with wooden tables (the BACKGROUND scene)

YOUR TASK: Edit the SECOND image (cafe scene) to ADD the handbag from the FIRST image.
Place the handbag naturally on one of the wooden tables in the cafe.
The handbag should be clearly visible, properly lit to match the scene, and look like it belongs there.
Keep the rest of the cafe scene intact - only add the handbag.
Output the edited cafe scene with the handbag placed in it."""

    print("Sending to Nano Banana...")
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=edit_prompt),
                    types.Part.from_bytes(data=product_bytes, mime_type="image/jpeg"),
                    types.Part.from_bytes(data=bg_bytes, mime_type="image/jpeg"),
                ],
            )
        ],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    integrated_bytes = None
    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                print(f"Response text: {part.text[:200]}...")
            if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                integrated_bytes = part.inline_data.data
                mime = part.inline_data.mime_type
                ext = "png" if "png" in mime else "jpg"
                path = output_dir / f"integrated_scene.{ext}"
                with open(path, "wb") as f:
                    f.write(integrated_bytes)
                print(f"Saved integrated scene: {path} ({len(integrated_bytes)} bytes)")

    if not integrated_bytes:
        print("ERROR: No integrated image generated!")
        return

    # Step 2: Generate mask for the handbag
    print("\n--- Step 2: Generate mask for hover detection ---")

    mask_prompt = """Look at this cafe scene image. There is a brown leather HANDBAG placed on one of the tables.

YOUR TASK: Generate a BLACK AND WHITE MASK image where:
- The HANDBAG area is pure WHITE (#FFFFFF)
- EVERYTHING ELSE (tables, chairs, background, floor, etc.) is pure BLACK (#000000)

This mask will be used for mouse hover detection on a website.
The mask should be the same dimensions as the input image.
Only the handbag should be white, nothing else."""

    print("Generating mask...")
    mask_response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=mask_prompt),
                    types.Part.from_bytes(data=integrated_bytes, mime_type="image/png"),
                ],
            )
        ],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    if mask_response.candidates and mask_response.candidates[0].content:
        for part in mask_response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                print(f"Mask response: {part.text[:200]}...")
            if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                mask_bytes = part.inline_data.data
                mime = part.inline_data.mime_type
                ext = "png" if "png" in mime else "jpg"
                path = output_dir / f"mask.{ext}"
                with open(path, "wb") as f:
                    f.write(mask_bytes)
                print(f"Saved mask: {path} ({len(mask_bytes)} bytes)")

    print("\n--- Done! Check test_output/ folder ---")

if __name__ == "__main__":
    asyncio.run(test_product_integration())
