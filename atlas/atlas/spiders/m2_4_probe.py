"""
M2.4 probe — try fetching old periods via period param
"""
import requests

# Main 49图库 endpoint pattern
base = "https://6xr4in4.xn--eck6e6bcfa3628cg56c.xn--q9jyb4c/unite49/h5/index"
lt = 2

print("=== Test: does period param work? ===")
for p in [193, 100, 50, 10]:
    url = f"{base}/lastLotteryRecord"
    try:
        r = requests.get(url, params={"lotteryType": lt, "period": p}, timeout=10, verify=False)
        print(f"  period={p}: status={r.status_code}, len={len(r.text)}, preview={r.text[:200]}")
    except Exception as e:
        print(f"  period={p}: ERROR {e}")

print()
print("=== Test: search endpoint with period ===")
url = f"{base}/search"
for params in [
    {"year": 2025, "keyword": "澳门", "color": 1, "lotteryType": lt},
    {"year": 2025, "lotteryType": lt, "period": 100},
    {"year": 2025, "lotteryType": lt, "pageNum": 1, "pageSize": 10},
]:
    try:
        r = requests.get(url, params=params, timeout=10, verify=False)
        print(f"  params={params}: status={r.status_code}, len={len(r.text)}, preview={r.text[:150]}")
    except Exception as e:
        print(f"  params={params}: ERROR {e}")

print()
print("=== Test: 六合宝典 /article/search with different params ===")
# Try finding 六合宝典's lottery-data endpoint
base2 = "https://82hats7.66852.cc:8443/bible/h5"
for url in [
    f"{base2}/index/lotteryRecord",  # possibly
    f"{base2}/index/period",  # possibly
    f"{base2}/lotteryRecord/list",  # possibly
    f"{base2}/article/history",  # possibly
]:
    try:
        r = requests.get(url, params={"lotteryType": lt, "year": 2026}, timeout=10, verify=False)
        print(f"  {url}: status={r.status_code}, len={len(r.text)}, preview={r.text[:150]}")
    except Exception as e:
        print(f"  {url}: ERROR {e}")