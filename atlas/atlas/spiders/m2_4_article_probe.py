"""
M2.4 — Try 全年资料 (articleTypeId=6852) which contains full year history
The article endpoint might include period numbers per article
"""
import requests
import json

base2 = "https://82hats7.66852.cc:8443/bible/h5"

# type=4 (or other) gives article search results
# Let's see what fields each article has
r = requests.get(base2 + "/article/search",
                 params={"type": 4, "year": 2026, "lotteryType": 2, "pageNum": 1, "pageSize": 5},
                 timeout=15, verify=False)
data = r.json()["data"]
print(f"list size (page 1): {len(data['list'])}")
print(f"Total count: {data.get('count')}")

print(f"\nFirst article full:")
print(json.dumps(data['list'][0], ensure_ascii=False, indent=2))

print(f"\nSecond article:")
print(json.dumps(data['list'][1], ensure_ascii=False, indent=2))

# Try type=2 (probably 历史开奖)
print("\n=== Try type=2 ===")
r = requests.get(base2 + "/article/search",
                 params={"type": 2, "year": 2026, "lotteryType": 2, "pageNum": 1, "pageSize": 5},
                 timeout=15, verify=False)
data = r.json()["data"]
print(f"count: {data.get('count')}, list size: {len(data['list'])}")
if data['list']:
    print(f"sample: {json.dumps(data['list'][0], ensure_ascii=False, indent=2)[:600]}")

# Try type=1
print("\n=== Try type=1 ===")
r = requests.get(base2 + "/article/search",
                 params={"type": 1, "year": 2026, "lotteryType": 2, "pageNum": 1, "pageSize": 5},
                 timeout=15, verify=False)
data = r.json()["data"]
print(f"count: {data.get('count')}, list size: {len(data['list'])}")
if data['list']:
    print(f"sample: {json.dumps(data['list'][0], ensure_ascii=False, indent=2)[:600]}")