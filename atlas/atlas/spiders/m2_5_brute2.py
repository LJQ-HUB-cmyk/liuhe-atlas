"""
M2.5 — Brute-force probe lastLotteryRecord for historical params
"""
import requests
import json

base = "https://82hats7.66852.cc:8443/bible/h5/index"
lt = 2

print("=== Try various historical query params on lastLotteryRecord ===")
test_cases = [
    {"year": 2025, "lotteryType": lt},
    {"year": 2025, "lotteryType": lt, "period": 1},
    {"year": 2025, "lotteryType": lt, "size": 10},
    {"year": 2024, "lotteryType": lt},
    {"year": 2023, "lotteryType": lt},
    {"year": 2020, "lotteryType": lt},
    {"year": 2020, "lotteryType": lt, "period": 365},
    {"lotteryType": lt, "beforePeriod": 365},
    {"lotteryType": lt, "from": 1, "to": 100},
    {"lotteryType": lt, "periodList": "1,2,3,4,5"},
    {"lotteryType": lt, "ids": "1,2,3"},
]
for params in test_cases:
    r = requests.get(base + "/lastLotteryRecord", params=params, timeout=10, verify=False)
    body = r.text
    if r.status_code != 200:
        print(f"  {params}: HTTP {r.status_code}")
        continue
    try:
        data = r.json()
        # Check if different from latest (which is period 194)
        d = data.get("data", {})
        period_in_resp = d.get("period") if isinstance(d, dict) else None
        year_in_resp = d.get("year") if isinstance(d, dict) else None
        is_latest = period_in_resp == 194 and year_in_resp == 2026
        marker = " <LATEST>" if is_latest else ""
        print(f"  {params}: status={r.status_code}, len={len(body)}, period={period_in_resp}, year={year_in_resp}{marker}")
        if not is_latest and period_in_resp is not None:
            print(f"    *** DIFFERENT FROM LATEST! Body: {body[:200]}")
    except Exception as e:
        print(f"  {params}: parse error: {e}, body: {body[:100]}")

print()
print("=== Try getting a list of all periods via 49图库 endpoint ===")
base49 = "https://6xr4in4.xn--eck6e6bcfa3628cg56c.xn--q9jyb4c/unite49/h5"
endpoints = [
    "/index/lastLotteryRecord",
    "/lottery/history",
    "/history/list",
    "/period/list",
    "/lottery/periodList",
    "/index/lastLottery",
    "/index/periodHistory",
    "/index/periods",
    "/index/lastPeriods",
]
for ep in endpoints:
    for params in [
        {"lotteryType": lt},
        {"lotteryType": lt, "year": 2020},
        {"lotteryType": lt, "limit": 100},
    ]:
        try:
            r = requests.get(base49 + ep, params=params, timeout=8, verify=False)
            if r.status_code == 200:
                try:
                    d = r.json()
                    if d.get("code") == 10000:
                        data = d.get("data", {})
                        if isinstance(data, dict) and "list" in data:
                            print(f"  {ep} {params}: list[{len(data['list'])}]")
                        elif isinstance(data, dict) and data:
                            print(f"  {ep} {params}: keys={list(data.keys())[:6]}")
                        else:
                            print(f"  {ep} {params}: data type={type(data).__name__}")
                    else:
                        pass  # skip non-10000
                except Exception:
                    pass
        except Exception:
            pass