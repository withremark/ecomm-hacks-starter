#!/usr/bin/env python3
"""Test different image generation prompt variations.

Usage:
    cd backend
    uv run python scripts/test_image_prompts.py
"""

import asyncio
import base64
import os
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.gemini import GeminiService

# Load test context
CONTEXT_FILE = Path(__file__).parent.parent / "prompts" / "test_user_context.txt"
OUTPUT_DIR = Path(__file__).parent.parent / "test_outputs"

# Different prompt variations to test
PROMPT_VARIATIONS = {
    "v1_original": """Generate an evocative, artistic image that complements this creative context:

Context: {user_context}

Create a visually striking image that captures the mood and themes. The image should be:
- Atmospheric and emotionally resonant
- Artistic and creative (not stock photo style)
- Relevant to the writing context

Generate the image now.""",

    "v2_cinematic": """Create a cinematic still photograph inspired by this creative vision:

{user_context}

Style: Wong Kar Wai meets European art house. 4pm Paris light filtering through rain-streaked glass.
Film grain, muted warmth, the texture of memory. Impressionistic rather than sharp.
Aspect ratio 16:9, cinematic framing.""",

    "v3_minimal": """Generate an image: {user_context}

Style: 4pm Paris cafe light, matte paper texture, warm film grain, impressionist mood.""",

    "v4_structured": """<image_generation>
<context>{user_context}</context>
<visual_style>
- Lighting: Golden hour, 4pm Paris afternoon, warm diffused light through windows
- Texture: Matte paper, film grain, Moleskine notebook materiality
- Palette: Vermillion accents, muted sea greens, smoky blues, faded memory tones
- Mood: Mono no aware, nostalgic, impressionistic, like Wong Kar Wai cinematography
- Feel: Artist's drafting table, pencil sketches, creative workspace
</visual_style>
<output>Generate a single evocative photograph capturing this aesthetic</output>
</image_generation>""",

    "v5_persona": """You are an art director creating a mood board image for a design project.

The client's creative brief:
{user_context}

Create ONE photograph that captures this vision. Think:
- Wong Kar Wai's In the Mood for Love
- A Parisian cafe at 4pm
- An artist's drafting table with warm afternoon light
- Expired film stock, matte textures, vermillion accents

Generate the hero image now.""",

    "v6_direct": """4pm Paris cafe, golden afternoon light through rain-streaked window,
artist's drafting table with matte paper and pencils, warm film grain aesthetic,
vermillion and muted teal accents, impressionist mood, Wong Kar Wai cinematography style.
Based on: {user_context}""",

    "v7_extracted_keywords": """Generate an artistic photograph with these elements:

SETTING: Parisian cafe, artist's studio, drafting table
LIGHTING: 4pm golden hour, warm diffused, afternoon shadows
TEXTURE: Matte paper, film grain, Moleskine, waxed fabric
PALETTE: Vermillion red, Mediterranean turquoise, smoky grays, faded tones
MOOD: Nostalgic, impressionistic, mono no aware, memory-like
STYLE: Wong Kar Wai, expired film, materiality over minimalism

Inspiration: {user_context}""",
}


async def test_prompt_variation(gemini: GeminiService, name: str, prompt_template: str, context: str) -> dict:
    """Test a single prompt variation."""
    prompt = prompt_template.format(user_context=context)

    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(f"Prompt preview: {prompt[:200]}...")

    try:
        result = await gemini.generate_image(prompt=prompt)

        if result.images:
            return {
                "name": name,
                "success": True,
                "image_count": len(result.images),
                "text_response": result.text,
                "images": result.images,
            }
        else:
            return {
                "name": name,
                "success": False,
                "error": "No images generated",
                "text_response": result.text,
            }
    except Exception as e:
        return {
            "name": name,
            "success": False,
            "error": str(e),
        }


async def main():
    # Load context
    context = CONTEXT_FILE.read_text()
    print(f"Loaded context ({len(context)} chars)")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"run_{timestamp}"
    run_dir.mkdir()

    # Initialize Gemini
    gemini = GeminiService()

    # Test each variation
    results = []
    for name, template in PROMPT_VARIATIONS.items():
        result = await test_prompt_variation(gemini, name, template, context)
        results.append(result)

        # Save image if successful
        if result.get("success") and result.get("images"):
            for i, img in enumerate(result["images"]):
                ext = "jpg" if "jpeg" in img["mime_type"] else "png"
                img_path = run_dir / f"{name}_{i}.{ext}"
                img_data = base64.b64decode(img["data"])
                img_path.write_bytes(img_data)
                print(f"  Saved: {img_path}")

        # Small delay between requests
        await asyncio.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for r in results:
        status = "SUCCESS" if r.get("success") else "FAILED"
        print(f"{r['name']}: {status}")
        if r.get("error"):
            print(f"  Error: {r['error']}")
        if r.get("text_response"):
            print(f"  Response: {r['text_response'][:100]}...")

    print(f"\nImages saved to: {run_dir}")

    # Save prompts used for reference
    prompts_file = run_dir / "prompts_used.md"
    with open(prompts_file, "w") as f:
        f.write(f"# Prompt Variations Test - {timestamp}\n\n")
        for name, template in PROMPT_VARIATIONS.items():
            f.write(f"## {name}\n\n```\n{template}\n```\n\n")

    print(f"Prompts saved to: {prompts_file}")


if __name__ == "__main__":
    asyncio.run(main())
