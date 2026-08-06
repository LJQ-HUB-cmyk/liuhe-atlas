"""
M2.4 — Try 49图库 (different domain, possibly different endpoints)
"""
import time
from playwright.sync_api import sync_playwright

ENTRY_URL = "https://j.manolotron.com:49/"

def discover():
    captured = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            url = response.url
            try:
                ctype = response.headers.get("content-type", "")
                if "application/json" in ctype:
                    body = response.json()
                    captured.append({"url": url, "status": response.status, "body": body})
            except Exception:
                pass

        page.on("response", handle_response)
        print(f"[INFO] Navigating to {ENTRY_URL}")
        page.goto(ENTRY_URL, wait_until="networkidle", timeout=60000)
        time.sleep(5)

        # Switch to Macau tab
        print("[INFO] Click 澳门...")
        page.evaluate("""() => {
            const el = [...document.querySelectorAll('*')].find(e => e.innerText && e.innerText.includes('澳彩') && e.children.length === 0);
            if (el) el.click();
        }""")
        time.sleep(3)

        # Click 查看历史记录 button
        for kw in ["查看历史记录", "历史记录", "历史", "开奖记录"]:
            try:
                clicked = page.evaluate(f"""() => {{
                    const el = [...document.querySelectorAll('a, div, span')].find(e => e.innerText && e.innerText.includes('{kw}') && e.children.length <= 1);
                    if (el) {{ el.click(); return true; }}
                    return false;
                }}""")
                if clicked:
                    print(f"  Clicked: {kw}")
                    time.sleep(3)
            except Exception as e:
                print(f"  [WARN] {kw}: {e}")

        # Try clicking year tabs
        for kw in ["2025年彩色", "2024年彩色", "2025年"]:
            try:
                clicked = page.evaluate(f"""() => {{
                    const el = [...document.querySelectorAll('*')].find(e => e.innerText === '{kw}' && e.children.length === 0);
                    if (el) {{ el.click(); return true; }}
                    return false;
                }}""")
                if clicked:
                    print(f"  Clicked: {kw}")
                    time.sleep(2)
            except Exception as e:
                print(f"  [WARN] {kw}: {e}")

        time.sleep(3)
        browser.close()

    print(f"\n[CAPTURED] {len(captured)} JSON responses\n")
    # Dedupe by URL
    seen = set()
    for c in captured:
        url = c["url"]
        # Shorten URL by removing common params
        key = url.split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        print(f"  [{c['status']}] {url[:130]}")
        body = c["body"]
        if isinstance(body, dict) and "data" in body:
            data = body["data"]
            if isinstance(data, dict):
                print(f"      data keys: {list(data.keys())[:10]}")
                for k in ["list", "period", "yearList", "year"]:
                    if k in data:
                        v = data[k]
                        if isinstance(v, list):
                            print(f"      {k}: list[{len(v)}], sample: {json.dumps(v[0], ensure_ascii=False)[:250] if v else 'empty'}")
                        elif isinstance(v, str):
                            print(f"      {k}: {v}")


import json

if __name__ == "__main__":
    discover()