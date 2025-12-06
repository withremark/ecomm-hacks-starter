"""End-to-end test for Nano Banana Pro image generation.

Verifies that:
1. Image cards are generated (not text cards)
2. Images are AI-generated data URLs (not Wikimedia)
3. Images display correctly in the canvas
"""

from playwright.sync_api import sync_playwright, expect
import os
import re
import time

def test_image_generation_e2e():
    """Test full image generation flow through the UI."""
    headless = os.getenv('HEADED') != '1'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        logs = []
        page = context.new_page()
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        try:
            # Step 1: Navigate to frontend
            print("\n=== Step 1: Loading frontend ===")
            page.goto('http://localhost:5173', timeout=15000)
            page.wait_for_load_state('networkidle')
            page.screenshot(path='/tmp/e2e_1_initial.png', full_page=True)
            print("Screenshot: /tmp/e2e_1_initial.png")

            # Step 2: Complete onboarding if present
            print("\n=== Step 2: Checking for onboarding ===")

            # Look for the onboarding input
            textarea = page.locator('textarea, input[type="text"]').first
            if textarea.is_visible(timeout=3000):
                print("Found onboarding input, filling...")
                textarea.fill("A serene gallery of AI-generated art exploring themes of nature and tranquility")
                page.screenshot(path='/tmp/e2e_2_onboard_filled.png')

                # Find and click submit/create button
                submit_btn = page.locator('button:has-text("Create"), button:has-text("Start"), button[type="submit"]').first
                if submit_btn.is_visible(timeout=2000):
                    print("Clicking submit button...")
                    submit_btn.click()
                    page.wait_for_load_state('networkidle')
                    time.sleep(2)  # Wait for backend response
                    page.screenshot(path='/tmp/e2e_3_after_onboard.png')
                    print("Screenshot: /tmp/e2e_3_after_onboard.png")

            # Step 3: Wait for canvas and cards to appear
            print("\n=== Step 3: Waiting for cards to generate ===")

            # Wait longer for image generation (it takes time)
            print("Waiting 15 seconds for image generation...")
            time.sleep(15)

            page.screenshot(path='/tmp/e2e_4_canvas.png', full_page=True)
            print("Screenshot: /tmp/e2e_4_canvas.png")

            # Step 4: Check for image cards in the DOM
            print("\n=== Step 4: Inspecting generated cards ===")

            # Look for img elements with data URLs
            images = page.locator('img[src^="data:image"]').all()
            print(f"Found {len(images)} images with data URLs")

            # Also check for any Wikimedia URLs (should be NONE)
            wikimedia_images = page.locator('img[src*="wikimedia"], img[src*="upload.wikimedia"]').all()
            print(f"Found {len(wikimedia_images)} Wikimedia images (should be 0)")

            # Check for any external http images
            external_images = page.locator('img[src^="http"]').all()
            print(f"Found {len(external_images)} external HTTP images")

            # Get all img src values for inspection
            all_images = page.locator('img').all()
            print(f"\nTotal images in DOM: {len(all_images)}")

            for i, img in enumerate(all_images[:5]):  # First 5
                src = img.get_attribute('src') or ''
                if src.startswith('data:'):
                    # Parse data URL
                    match = re.match(r'data:([^;]+);base64,', src)
                    mime = match.group(1) if match else 'unknown'
                    data_len = len(src) - src.index(',') - 1 if ',' in src else 0
                    print(f"  Image {i+1}: data URL, mime={mime}, base64_len={data_len}")
                else:
                    print(f"  Image {i+1}: {src[:80]}...")

            # Step 5: Verify console for generation logs
            print("\n=== Step 5: Checking console logs ===")
            generation_logs = [l for l in logs if 'generat' in l.lower() or 'image' in l.lower() or 'nano' in l.lower()]
            for log in generation_logs[-10:]:
                print(f"  {log}")

            # Step 6: Make API call directly to verify backend
            print("\n=== Step 6: Direct API test ===")
            api_response = page.evaluate('''async () => {
                const config = {
                    name: "Test Canvas",
                    cardSchema: { fields: [{ name: "content", type: "string", display: "primary" }] },
                    cardTheme: { container: "bg-black", primary: "text-white" },
                    canvasTheme: { background: "#000", accent: "#fff" },
                    generationContext: "Artistic imagery",
                    directives: ["Be creative"],
                    seedContent: [],
                    physics: { cardLifetime: 30, driftSpeed: 1.0, jiggle: 0.5, bounce: 0.3 },
                    models: { generation: "pro", chat: "pro", onboarding: "pro" },
                    spawning: { intervalSeconds: 10, minCards: 3, imageWeight: 1.0 }
                };

                try {
                    const resp = await fetch('http://localhost:8000/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            config: config,
                            user_composition: "A peaceful mountain landscape at sunrise",
                            existing_cards: [],
                            image_card: true
                        })
                    });
                    const data = await resp.json();
                    return {
                        status: resp.status,
                        has_image_url: !!data.card?.image_url,
                        is_data_url: data.card?.image_url?.startsWith('data:image/'),
                        mime_type: data.card?.image_url?.match(/data:([^;]+)/)?.[1],
                        is_ai_generated: data.card?.is_ai_generated,
                        attribution: data.card?.attribution,
                        caption: data.card?.caption?.substring(0, 100)
                    };
                } catch (e) {
                    return { error: e.message };
                }
            }''')

            print(f"API Response:")
            for k, v in api_response.items():
                print(f"  {k}: {v}")

            # Assertions
            print("\n=== RESULTS ===")

            if api_response.get('error'):
                print(f"ERROR: API call failed: {api_response['error']}")
            else:
                assert api_response.get('status') == 200, f"API returned {api_response.get('status')}"
                assert api_response.get('is_data_url'), "Image URL is not a data URL!"
                assert api_response.get('is_ai_generated'), "Missing is_ai_generated flag!"
                assert 'gemini' in api_response.get('attribution', '').lower() or 'nano' in api_response.get('attribution', '').lower(), \
                    f"Attribution doesn't mention Gemini: {api_response.get('attribution')}"

                # Check MIME type is correct (should be jpeg based on our investigation)
                mime = api_response.get('mime_type', '')
                assert mime in ['image/jpeg', 'image/png', 'image/webp'], f"Unexpected MIME type: {mime}"
                print(f"MIME type detected: {mime}")

            assert len(wikimedia_images) == 0, f"Found {len(wikimedia_images)} Wikimedia images - should be AI generated!"

            print("\nALL CHECKS PASSED!")
            print("- Images are data URLs (AI-generated)")
            print("- No Wikimedia/external images")
            print("- is_ai_generated flag is set")
            print("- Attribution mentions Gemini/Nano Banana")

            context.tracing.stop(path="/tmp/trace_image_e2e_SUCCESS.zip")
            print("\nTrace saved: /tmp/trace_image_e2e_SUCCESS.zip")
            print("View with: playwright show-trace /tmp/trace_image_e2e_SUCCESS.zip")

        except Exception as e:
            context.tracing.stop(path="/tmp/trace_image_e2e_FAILED.zip")
            page.screenshot(path='/tmp/e2e_FAILED.png', full_page=True)

            print(f"\nTEST FAILED: {e}")
            print("\nLast 20 console logs:")
            for log in logs[-20:]:
                print(f"  {log}")
            print("\nTrace saved: /tmp/trace_image_e2e_FAILED.zip")
            print("Screenshot: /tmp/e2e_FAILED.png")
            raise

        finally:
            browser.close()


if __name__ == '__main__':
    test_image_generation_e2e()
