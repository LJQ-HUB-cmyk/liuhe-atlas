"""
M2.5 — Try 49图库 (unite49) endpoints for history
"""
import requests
import json

# Note: the 49图库 domain rotates (XOR obfuscation). Use the one we already saw.
base49 = "https://6xr4in4.xn--eck6e6bcfa3628cg56c.xn--q9jyb4c/unite49/h5"
lt = 2

# Known working: lastLotteryRecord
# Try: lastLotteryRecord with various params + discover others
print("=== lastLotteryRecord parameter probes (49图库) ===")
test_params = [
    {"lotteryType": lt, "year": 2025},
    {"lotteryType": lt, "year": 2024},
    {"lotteryType": lt, "year": 2024, "period": 100},
    {"lotteryType": lt, "period": 100},
    {"lotteryType": lt, "beforePeriod": 100},
    {"lotteryType": lt, "sincePeriod": 100},
    {"lotteryType": lt, "fromPeriod": 1, "toPeriod": 100},
    {"lotteryType": lt, "periodId": 2026194},
    {"lotteryType": lt, "periodId": 2025190},
    {"lotteryType": lt, "periodId": 2024190},
]
for params in test_params:
    try:
        r = requests.get(base49 + "/index/lastLotteryRecord", params=params, timeout=8, verify=False)
        d = r.json().get("data", {})
        pid = d.get("id") or d.get("periodId")
        period = d.get("period")
        year = d.get("year")
        lottery_time = d.get("lotteryTime")
        print(f"  {params}: year={year} period={period} id={pid} time={lottery_time}")
    except Exception as e:
        print(f"  {params}: ERROR {e}")

print()
print("=== Try other endpoints on 49图库 ===")
candidates = [
    "/index/lastLottery", "/index/historyList", "/index/periodList",
    "/index/periods", "/index/periodsList", "/index/allLottery",
    "/lottery/history", "/lottery/list", "/history",
    "/index/listHistory", "/index/lastResults", "/index/results",
    "/index/lotteryHistory", "/lottery/results", "/results",
    "/index/lotteryList", "/index/lotteryPeriods",
]
for ep in candidates:
    try:
        r = requests.get(base49 + ep, params={"lotteryType": lt}, timeout=8, verify=False)
        if r.status_code != 200:
            continue
        d = r.json()
        code = d.get("code")
        if code == 10000:
            data = d.get("data", {})
            keys = list(data.keys())[:8] if isinstance(data, dict) else f"type={type(data).__name__}"
            print(f"  {ep}: status=200, code=10000, keys={keys}")
    except Exception:
        pass