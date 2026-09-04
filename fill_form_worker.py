"""
fill_form_worker.py

Standalone worker script for filling job application forms with Playwright.
Runs as a completely separate process from Streamlit, called via subprocess.

Why this exists: calling Playwright's sync API directly inside Streamlit on
Windows causes a NotImplementedError, because Playwright needs to spawn an
internal subprocess and that requires Windows' "Proactor" event loop, which
conflicts with the event loop Streamlit already has running. Running this
as a fully separate process avoids the conflict entirely, since this script
gets its own fresh process with no inherited event loop.

Usage:
    python fill_form_worker.py <job_url> <name> <email> <phone> <screenshot_output_path>

Prints ONE line of JSON to stdout:
    {"filled": [...], "screenshot_path": "...", "error": null}
"""
import sys
import json


def main():
    if len(sys.argv) < 6:
        print(json.dumps({"filled": [], "screenshot_path": None, "error": "Missing arguments"}))
        return

    job_url, name, email, phone, screenshot_path = sys.argv[1:6]

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(job_url, timeout=30000)

            field_map = {
                'name': (['input[name*="name" i]', 'input[id*="name" i]'], name),
                'email': (['input[type="email"]', 'input[name*="email" i]'], email),
                'phone': (['input[type="tel"]', 'input[name*="phone" i]'], phone),
            }

            filled = []
            for field_key, (selectors, value) in field_map.items():
                for selector in selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            page.fill(selector, value)
                            filled.append(field_key)
                            break
                    except Exception:
                        continue

            page.screenshot(path=screenshot_path, full_page=True)
            browser.close()

        print(json.dumps({"filled": filled, "screenshot_path": screenshot_path, "error": None}))

    except Exception as e:
        print(json.dumps({"filled": [], "screenshot_path": None, "error": str(e)}))


if __name__ == "__main__":
    main()