"""
M2.5 — Test if period numbers reset per year
"""
import requests
import json

base = "https://82hats7.66852.cc:8443/bible/h5/index"
lt = 2

print("=== Test: does period reset per year? ===")
# If yes, period 1 of year 2024 should be different from period 1 of 2026
test_periods = [
    (2025, 1), (2025, 50), (2025, 100), (2025, 195), (2025, 196),
    (2024, 1), (2024, 50), (2024, 100), (2024, 150),
    (2023, 1), (2023, 100), (2023, 200),
    (2022, 1), (2022, 100), (2022, 200),
    (2021, 1), (2021, 100),
    (2020, 1), (2020, 100), (2020, 150),
]
seen = set()
for year, period in test_periods:
    try:
        r = requests.get(base + "/lastLotteryRecord",
                          params={"lotteryType": lt, "year": year, "period": period},
                          timeout=10, verify=False)
        d = r.json().get("data", {})
        p = d.get("period")
        y = d.get("year")
        balls = d.get("originalDataList", [])
        key = (y, p)
        # Track unique combos
        is_new = key not in seen
        seen.add(key)
        marker = " <NEW>" if is_new else ""
        print(f"  year={year} period={period}: returned year={y}, period={p}, balls={balls}{marker}")
    except Exception as e:
        print(f"  year={year} period={period}: ERROR {e}")