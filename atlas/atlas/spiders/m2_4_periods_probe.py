"""
M2.4 — Use search endpoint to extract ALL period IDs
"""
import requests
import json

base = "https://6xr4in4.xn--eck6e6bcfa3628cg56c.xn--q9jyb4c/unite49/h5/index"
lt = 2

# search returns all picture entries per year, each has periodStr
r = requests.get(base + "/search",
                 params={"year": 2026, "lotteryType": lt, "pageNum": 1, "pageSize": 1000},
                 timeout=15, verify=False)
print(f"Status: {r.status_code}, body len: {len(r.text)}")
data = r.json()["data"]
print(f"data keys: {list(data.keys())}")
print(f"list size: {len(data['list'])}")
print(f"\nFirst entry:")
print(json.dumps(data['list'][0], ensure_ascii=False, indent=2))

# Collect unique period IDs (across all entries)
periods = set()
for entry in data['list']:
    period_id = entry.get("period") or entry.get("periodStr")
    if period_id:
        periods.add(str(period_id))

print(f"\nUnique periods in this response: {len(periods)}")
print(f"Sample periods: {sorted([int(p) for p in periods if p.isdigit()])[:20]}")
print(f"Max period: {max(int(p) for p in periods if p.isdigit())}")
print(f"Min period: {min(int(p) for p in periods if p.isdigit())}")