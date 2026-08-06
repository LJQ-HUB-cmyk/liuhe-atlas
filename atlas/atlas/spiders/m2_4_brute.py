"""
M2.4 — Last resort: brute-force probe various endpoints with year/period params
to find historical data fetch
"""
import requests

# 49图库 has /unite49/h5/index/lastLotteryRecord
# Test if it accepts any history-related param
base = "https://6xr4in4.xn--eck6e6bcfa3628cg56c.xn--q9jyb4c/unite49/h5/index"
lt = 2

print("=== lastLotteryRecord variations ===")
for params in [
    {"lotteryType": lt, "year": 2025},
    {"lotteryType": lt, "year": 2025, "period": 100},
    {"lotteryType": lt, "history": 1},
    {"lotteryType": lt, "before": 100},
    {"lotteryType": lt, "limit": 50},
    {"lotteryType": lt, "size": 50},
    {"lotteryType": lt, "page": 1},
    {"lotteryType": lt, "pageSize": 50, "pageNum": 1},
    {"lotteryType": lt, "sincePeriod": 1},
    {"lotteryType": lt, "fromPeriod": 1, "toPeriod": 100},
]:
    r = requests.get(base + "/lastLotteryRecord", params=params, timeout=10, verify=False)
    body = r.text
    print(f"  {params}: status={r.status_code}, len={len(body)}, contains_period_id={('2026' in body or '2025' in body)}")

print()
print("=== uniteInfo variations ===")
for params in [
    {"lotteryType": lt},
    {"lotteryType": lt, "year": 2025},
]:
    r = requests.get(base + "/uniteInfo", params=params, timeout=10, verify=False)
    body = r.text
    print(f"  {params}: status={r.status_code}, len={len(body)}")

print()
print("=== Try discover endpoint ===")
for url in [
    base + "/discover",
    base + "/discover/history",
    base + "/history",
    base + "/period/list",
    base + "/period/listYear",
    base + "/period/listByYear",
    base + "/lottery/history",
    base + "/lottery/listByYear",
]:
    r = requests.get(url, params={"lotteryType": lt, "year": 2025}, timeout=10, verify=False)
    body = r.text
    print(f"  {url.split('/')[-1]}: status={r.status_code}, len={len(body)}")