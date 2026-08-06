"""
M2.4 — Extract all periods from article search (2026 only first as test)
"""
import requests
import json
import time

base2 = "https://82hats7.66852.cc:8443/bible/h5"

periods_seen = set()
page = 1
total_count = None

while True:
    r = requests.get(base2 + "/article/search",
                     params={"type": 4, "year": 2026, "lotteryType": 2, "pageNum": page, "pageSize": 50},
                     timeout=15, verify=False)
    data = r.json()["data"]
    if total_count is None:
        total_count = data.get("count", 0)
        print(f"Total articles for 2026: {total_count}")

    if not data["list"]:
        break

    for article in data["list"]:
        p = article.get("period")
        if p:
            periods_seen.add(int(p))

    print(f"  page {page}: got {len(data['list'])} articles, total unique periods so far: {len(periods_seen)}")

    if len(periods_seen) > 100:  # Should have all 2026 periods by now (each period has ~20 articles)
        print("Breaking early — got enough to verify")
        break

    page += 1
    if page > 50:  # Safety
        print("Breaking — too many pages")
        break
    time.sleep(0.5)

print(f"\n=== Final ===")
print(f"Unique periods in 2026: {len(periods_seen)}")
print(f"Period range: {min(periods_seen)} to {max(periods_seen)}")
print(f"Sample: {sorted(periods_seen)[:30]}")