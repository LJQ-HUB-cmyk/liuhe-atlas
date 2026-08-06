"""
M2.4 — Discovery: Click "查看历史记录" or "历史" button, capture network calls
"""
import json
import time
from playwright.sync_api import sync_playwright

ENTRY_URL = "https://82hats7.66852.cc:8443/"

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
        time.sleep(2)

        # Switch to Macau tab
        print("[INFO] Clicking 澳门六合彩 tab...")
        try:
            page.evaluate("""() => {
                const el = [...document.querySelectorAll('*')].find(e => e.innerText === '澳门六合彩' && e.children.length === 0);
                if (el) el.click();
            }""")
        except Exception as e:
            print(f"[WARN] tab click failed: {e}")
        time.sleep(3)

        # Click on a year tab to trigger historical fetch
        for year in ["2026年", "2025年", "2024年"]:
            print(f"[INFO] Clicking {year} tab...")
            try:
                page.evaluate(f"""() => {{
                    const el = [...document.querySelectorAll('*')].find(e => e.innerText === '{year}' && e.children.length === 0);
                    if (el) el.click();
                }}""")
                time.sleep(2)
            except Exception as e:
                print(f"[WARN] click {year}: {e}")

        # Try clicking 资料大全 (data center) link
        print("[INFO] Clicking 资料大全 / 历史记录...")
        for kw in ["资料大全", "历史记录", "历史", "开奖记录", "开奖"]:
            try:
                page.evaluate(f"""() => {{
                    const el = [...document.querySelectorAll('a, div, span')].find(e => e.innerText === '{kw}' && e.children.length === 0);
                    if (el) el.click();
                }}""")
                time.sleep(2)
                print(f"  Clicked: {kw}")
            except Exception as e:
                print(f"  [WARN] {kw}: {e}")

        time.sleep(5)
        browser.close()

    print(f"\n[CAPTURED] {len(captured)} JSON responses\n")
    for c in captured:
        url = c["url"]
        # Skip static/config responses
        if any(skip in url for skip in ["apiHost", "popList", "noticeList", "listWheelAdvert", "share/info", "myIndex", "h5Url"]):
            continue
        print(f"  [{c['status']}] {url[:100]}")
        body = c["body"]
        if isinstance(body, dict) and "data" in body:
            data = body["data"]
            if isinstance(data, dict):
                print(f"      data keys: {list(data.keys())[:8]}")
                # Print interesting fields
                for k in ["list", "listYear", "period", "periodList"]:
                    if k in data:
                        v = data[k]
                        if isinstance(v, list):
                            print(f"      {k}: list[{len(v)}], first: {json.dumps(v[0], ensure_ascii=False)[:200] if v else 'empty'}")
                        else:
                            print(f"      {k}: {str(v)[:200]}")
            elif isinstance(data, list):
                print(f"      data: list[{len(data)}]")
                if data:
                    print(f"      first: {json.dumps(data[0], ensure_ascii=False)[:300]}")
        else:
            print(f"      body: {str(body)[:300]}")


if __name__ == "__main__":
    discover()