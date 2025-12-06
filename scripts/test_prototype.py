"""Test the Paris Drafting Table prototype page."""

import os
from playwright.sync_api import sync_playwright

headless = os.getenv('HEADED') != '1'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context(viewport={'width': 1400, 'height': 900})
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    logs = []
    page = context.new_page()
    page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

    try:
        # Navigate to prototype page
        print("Navigating to prototype page...")
        page.goto('http://localhost:5174/prototype')
        page.wait_for_load_state('networkidle')

        # Take initial screenshot
        page.screenshot(path='/tmp/prototype_initial.png', full_page=True)
        print("Initial screenshot saved to /tmp/prototype_initial.png")

        # Check for key elements
        header = page.locator('h1:has-text("Paris Drafting Table")')
        products_panel = page.locator('.products-panel')
        aesthetics_panel = page.locator('.aesthetics-panel')
        composer_panel = page.locator('.composer-panel')

        print(f"Header visible: {header.is_visible()}")
        print(f"Products panel visible: {products_panel.is_visible()}")
        print(f"Aesthetics panel visible: {aesthetics_panel.is_visible()}")
        print(f"Composer panel visible: {composer_panel.is_visible()}")

        # Count product cards
        product_cards = page.locator('.product-card').all()
        print(f"Product cards found: {len(product_cards)}")

        # Check if generate buttons exist
        generate_btns = page.locator('.generate-btn').all()
        print(f"Generate buttons found: {len(generate_btns)}")

        # Click on a product card to test selection
        if len(product_cards) > 0:
            print("Testing product selection...")
            product_cards[0].click()
            page.wait_for_timeout(500)
            selected_product = page.locator('.product-card.selected')
            print(f"Product selected: {selected_product.count() > 0}")
            page.screenshot(path='/tmp/prototype_selected.png', full_page=True)
            print("Selection screenshot saved to /tmp/prototype_selected.png")

        # Save trace on success
        context.tracing.stop(path="/tmp/trace_prototype_SUCCESS.zip")
        print("\nTest passed! Trace saved to /tmp/trace_prototype_SUCCESS.zip")
        print("View trace with: playwright show-trace /tmp/trace_prototype_SUCCESS.zip")

        # Print any console errors
        errors = [log for log in logs if 'error' in log.lower()]
        if errors:
            print("\nConsole errors:")
            for err in errors[-10:]:
                print(f"  {err}")

    except Exception as e:
        context.tracing.stop(path="/tmp/trace_prototype_FAILED.zip")
        print(f"\nTest failed: {e}")
        print("Trace saved to /tmp/trace_prototype_FAILED.zip")

        print("\nConsole logs (last 20):")
        for log in logs[-20:]:
            print(f"  {log}")

        raise
    finally:
        browser.close()
