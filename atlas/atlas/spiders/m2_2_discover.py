"""
M2.2-bis — Discovery spider
Instead of guessing apiHost, capture ALL network responses from the page
and find which one contains the lottery data we need.
"""
import json
import time
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "lotto.db"

ENTRY_URL = "https://82hats7.66852.cc:8443/"


def discover_api():
    """Open page, intercept all XHR/fetch, find lottery API."""
    captured = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        def handle_response(response):
            url = response.url
            try:
                ctype = response.headers.get("content-type", "")
                if "application/json" in ctype:
                    body = response.json()
                    captured.append({
                        "url": url,
                        "status": response.status,
                        "body": body,
                        "size": len(json.dumps(body)),
                    })
            except Exception:
                pass

        page.on("response", handle_response)
        page.on("request", lambda req: None)  # silence

        print(f"[INFO] Navigating to {ENTRY_URL}")
        page.goto(ENTRY_URL, wait_until="networkidle", timeout=60000)
        # Click on Macau tab to trigger lottery data fetch
        time.sleep(3)

        # Trigger interactions to load more API calls
        try:
            page.evaluate("""() => {
                // Click on Macau tab if exists
                const tabs = [...document.querySelectorAll('div, span')].filter(el => el.innerText === '澳门六合彩');
                if (tabs.length > 0) tabs[0].click();
            }""")
        except Exception:
            pass

        time.sleep(5)
        browser.close()

    print(f"\n[CAPTURED] {len(captured)} JSON responses\n")
    for c in captured[:30]:
        url_short = c["url"][:80]
        keys = list(c["body"].keys()) if isinstance(c["body"], dict) else f"type={type(c['body']).__name__}"
        print(f"  [{c['status']}] {url_short}")
        print(f"      keys: {keys[:10]}")
        # Print interesting ones
        if any(kw in str(c["body"]).lower() for kw in ["period", "lottery", "ball", "开奖", "号码", "result"]):
            print(f"      *** LOTTERY-DATA-LIKE ***")
            print(f"      body preview: {json.dumps(c['body'], ensure_ascii=False)[:500]}")


if __name__ == "__main__":
    discover_api()