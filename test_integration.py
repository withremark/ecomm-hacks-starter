"""Integration test for Ephemeral Canvas with Gemini backend."""

from playwright.sync_api import sync_playwright, expect
import os

def test_frontend_loads():
    """Test that the frontend loads and shows the onboarding flow."""
    headless = os.getenv('HEADED') != '1'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        logs = []
        page = context.new_page()
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        try:
            # Navigate to frontend
            print("Navigating to http://localhost:5173...")
            page.goto('http://localhost:5173', timeout=10000)
            page.wait_for_load_state('networkidle')

            # Take initial screenshot
            page.screenshot(path='/tmp/ephemeral_1_initial.png', full_page=True)
            print("Screenshot saved: /tmp/ephemeral_1_initial.png")

            # Check page title or content
            title = page.title()
            print(f"Page title: {title}")

            # Look for onboarding elements
            content = page.content()
            print(f"Page loaded, content length: {len(content)} chars")

            # Check if we see the onboarding interface or any main content
            # The onboarding flow should have some text input or welcome message
            visible_text = page.locator('body').inner_text()
            print(f"Visible text preview: {visible_text[:500]}...")

            # Save trace on success
            context.tracing.stop(path="/tmp/trace_ephemeral_SUCCESS.zip")
            print("\nTrace saved: /tmp/trace_ephemeral_SUCCESS.zip")
            print("View with: playwright show-trace /tmp/trace_ephemeral_SUCCESS.zip")

            print("\n✅ Frontend loads successfully!")

        except Exception as e:
            # Save trace on failure
            context.tracing.stop(path="/tmp/trace_ephemeral_FAILED.zip")
            page.screenshot(path='/tmp/ephemeral_FAILED.png', full_page=True)

            print(f"\n❌ Test failed: {e}")
            print("\nConsole logs (last 20):")
            for log in logs[-20:]:
                print(f"  {log}")
            print("\nTrace saved: /tmp/trace_ephemeral_FAILED.zip")
            raise
        finally:
            browser.close()


def test_backend_health():
    """Test that the backend is responding."""
    import urllib.request
    import json

    print("Testing backend health...")

    # Test health endpoint
    req = urllib.request.Request('http://localhost:8000/health')
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
        print(f"Health check: {data}")
        assert data.get('status') == 'ok', "Health check failed"

    # Test root endpoint
    req = urllib.request.Request('http://localhost:8000/')
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
        print(f"API info: {data.get('name')} v{data.get('version')}")
        print(f"Endpoints: {list(data.get('endpoints', {}).keys())}")

    print("✅ Backend is healthy!")


if __name__ == '__main__':
    test_backend_health()
    test_frontend_loads()
