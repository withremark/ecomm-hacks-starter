"""
Playwright test for Parisian Atelier Console
Tests the three-panel layout, product selection, audience targeting, and generate flow.
"""

import os
from playwright.sync_api import sync_playwright, expect

def test_parisian_atelier():
    headless = os.getenv('HEADED') != '1'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        logs = []
        page = context.new_page()
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        try:
            # Navigate to console
            print("1. Navigating to /console...")
            page.goto('http://localhost:5173/console')
            page.wait_for_load_state('networkidle')
            page.screenshot(path='/tmp/pa_01_initial.png', full_page=True)

            # Verify three panels exist
            print("2. Verifying three-panel layout...")
            collection_panel = page.locator('.pa-panel-collection')
            audience_panel = page.locator('.pa-panel-audience')
            placements_panel = page.locator('.pa-panel-placements')

            expect(collection_panel).to_be_visible(timeout=5000)
            expect(audience_panel).to_be_visible(timeout=5000)
            expect(placements_panel).to_be_visible(timeout=5000)
            print("   ✓ All three panels visible")

            # Verify products are displayed
            print("3. Checking product tiles...")
            product_tiles = page.locator('.pa-product-tile')
            expect(product_tiles.first).to_be_visible(timeout=5000)
            product_count = product_tiles.count()
            print(f"   ✓ Found {product_count} product tiles")

            # Verify products are pre-selected
            selected_products = page.locator('.pa-product-tile.selected')
            selected_count = selected_products.count()
            print(f"   ✓ {selected_count} products pre-selected")

            # Toggle a product selection
            print("4. Testing product toggle...")
            first_product = product_tiles.first
            was_selected = 'selected' in (first_product.get_attribute('class') or '')
            first_product.click()
            page.wait_for_timeout(300)
            is_selected = 'selected' in (first_product.get_attribute('class') or '')
            assert was_selected != is_selected, "Product toggle should change selection state"
            print(f"   ✓ Product toggled from {was_selected} to {is_selected}")

            # Re-select if we deselected
            if not is_selected:
                first_product.click()
                page.wait_for_timeout(300)

            # Test demographics radio
            print("5. Testing demographics selection...")
            age_radio = page.locator('input[name="age"][value="35-44"]')
            age_radio.click()
            expect(age_radio).to_be_checked()
            print("   ✓ Age 35-44 selected")

            # Test interests pills
            print("6. Testing interest pills...")
            art_pill = page.locator('.pa-pill:has-text("Art")')
            expect(art_pill).to_be_visible(timeout=5000)
            art_pill.click()
            page.wait_for_timeout(300)
            assert 'selected' in (art_pill.get_attribute('class') or ''), "Art pill should be selected"
            print("   ✓ Art interest selected")

            # Test add interest button
            print("7. Testing add interest functionality...")
            add_interest_btn = page.locator('.pa-pill.add-btn').first
            add_interest_btn.click()
            page.wait_for_timeout(300)

            interest_input = page.locator('.pa-add-input').first
            expect(interest_input).to_be_visible(timeout=5000)
            interest_input.fill('Photography')

            add_confirm = page.locator('.pa-add-confirm').first
            add_confirm.click()
            page.wait_for_timeout(500)

            # Verify new interest was added
            new_interest = page.locator('.pa-pill:has-text("Photography")')
            expect(new_interest).to_be_visible(timeout=5000)
            print("   ✓ 'Photography' interest added")

            page.screenshot(path='/tmp/pa_02_interests.png', full_page=True)

            # Test scene chips
            print("8. Testing scene chips...")
            street_chip = page.locator('.pa-scene-chip:has-text("Street")')
            expect(street_chip).to_be_visible(timeout=5000)
            street_chip.click()
            page.wait_for_timeout(300)
            assert 'selected' in (street_chip.get_attribute('class') or ''), "Street chip should be selected"
            print("   ✓ Street scene selected")

            # Test add scene button
            print("9. Testing add scene functionality...")
            add_scene_btn = page.locator('.pa-scene-chip.add-btn')
            add_scene_btn.click()
            page.wait_for_timeout(300)

            # The scene add input is now the visible one (interest one is hidden)
            scene_input = page.locator('.pa-add-input:visible')
            expect(scene_input).to_be_visible(timeout=5000)
            scene_input.fill('Museum')

            scene_confirm = page.locator('.pa-add-confirm:visible')
            scene_confirm.click()
            page.wait_for_timeout(500)

            # Verify new scene was added
            new_scene = page.locator('.pa-scene-chip:has-text("Museum")')
            expect(new_scene).to_be_visible(timeout=5000)
            print("   ✓ 'Museum' scene added")

            # Test semantic description
            print("10. Testing semantic input...")
            semantic_input = page.locator('.pa-semantic-input')
            semantic_input.fill('Elegant Parisian afternoon with soft natural lighting')
            page.wait_for_timeout(300)
            print("   ✓ Semantic description entered")

            page.screenshot(path='/tmp/pa_03_configured.png', full_page=True)

            # Test generate button
            print("11. Testing generate posts...")
            generate_btn = page.locator('.pa-btn-primary:has-text("Generate Posts")')
            expect(generate_btn).to_be_visible(timeout=5000)
            expect(generate_btn).to_be_enabled(timeout=5000)
            generate_btn.click()

            # Wait for generating state
            page.wait_for_timeout(500)
            page.screenshot(path='/tmp/pa_04_generating.png', full_page=True)

            # Wait for placements to appear
            print("12. Waiting for placements...")
            placement_card = page.locator('.pa-placement-card').first
            expect(placement_card).to_be_visible(timeout=10000)

            placement_count = page.locator('.pa-placement-card').count()
            print(f"   ✓ {placement_count} placements generated")

            page.screenshot(path='/tmp/pa_05_placements.png', full_page=True)

            # Test clicking a placement to open modal
            print("13. Testing placement modal...")
            placement_card.click()
            page.wait_for_timeout(500)

            modal = page.locator('.pa-modal')
            expect(modal).to_be_visible(timeout=5000)
            print("   ✓ Modal opened")

            page.screenshot(path='/tmp/pa_06_modal.png', full_page=True)

            # Close modal
            close_btn = page.locator('.pa-modal-close')
            close_btn.click()
            page.wait_for_timeout(300)
            expect(modal).not_to_be_visible()
            print("   ✓ Modal closed")

            # Verify deploy button is now enabled
            print("14. Checking deploy button...")
            deploy_btn = page.locator('.pa-btn-secondary:has-text("Deploy Campaign")')
            expect(deploy_btn).to_be_enabled(timeout=5000)
            print("   ✓ Deploy button enabled")

            page.screenshot(path='/tmp/pa_07_final.png', full_page=True)

            print("\n" + "="*50)
            print("ALL TESTS PASSED!")
            print("="*50)

            context.tracing.stop(path="/tmp/trace_parisian_atelier_SUCCESS.zip")

        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            page.screenshot(path='/tmp/pa_FAILED.png', full_page=True)
            context.tracing.stop(path="/tmp/trace_parisian_atelier_FAILED.zip")

            print("\nConsole logs (last 20):")
            for log in logs[-20:]:
                print(f"  {log}")

            raise

        finally:
            browser.close()

if __name__ == '__main__':
    test_parisian_atelier()
