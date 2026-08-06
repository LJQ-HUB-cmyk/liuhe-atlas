"""
M2.2 — Single Period Spider (FINAL WORKING VERSION)

Real API endpoint discovered:
  GET https://82hats7.66852.cc:8443/bible/h5/index/lastLotteryRecord?lotteryType=2

Response format:
{
  "code": 10000,
  "data": {
    "period": 194,
    "year": 2026,
    "originalDataList": ["30", "21", "22", "15", "04", "34", "26"],
    "nextLotteryTime": "2026-07-14",
    "title": "2026年07月14日21时32分 星期二",
    "lotteryType": 2,
    "recommendList": [...],
    "id": 20261942
  }
}
"""
import json
import sqlite3
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "lotto.db"

API_BASE = "https://82hats7.66852.cc:8443/bible/h5"
SOURCE_DOMAIN = "82hats7.66852.cc:8443"

LOTTERY_TYPES = {
    1: "香港六合彩",
    2: "澳门六合彩",
}


def fetch_latest(lottery_type: int = 2) -> dict:
    """Fetch latest period data from real API."""
    url = f"{API_BASE}/index/lastLotteryRecord"
    resp = requests.get(url, params={"lotteryType": lottery_type}, timeout=15, verify=False)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 10000:
        raise RuntimeError(f"API error: {payload}")
    return payload["data"]


def ingest(data: dict, lottery_type: int):
    """Insert period + 7 numbers into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    period_year = data["year"]
    period_seq = data["period"]
    # Build period_id: year*1000 + seq (e.g., 2026194)
    period_id = period_year * 1000 + period_seq

    lottery_name = LOTTERY_TYPES.get(lottery_type, f"Type{lottery_type}")
    draw_date_str = data.get("nextLotteryTime", "")
    # Convert "2026-07-14" to "2026-07-14 21:32:00"
    title = data.get("title", "")
    draw_date = title if title else f"{draw_date_str} 21:30:00"

    # First delete old numbers (cleanup if re-running)
    cur.execute("""
        DELETE FROM numbers WHERE period_id = ? AND lottery_type = ?
    """, (period_id, lottery_type))

    # Upsert period (using OR IGNORE for simplicity since period_id is primary key)
    cur.execute("""
        INSERT OR REPLACE INTO periods
            (period_id, lottery_type, lottery_name, draw_date, source_domain, raw_payload)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (period_id, lottery_type, lottery_name, draw_date, SOURCE_DOMAIN,
          json.dumps(data, ensure_ascii=False)))

    ball_strings = data["originalDataList"][:7]
    for position, ball_str in enumerate(ball_strings, start=1):
        ball_int = int(ball_str)
        # Lookup 2026 symbol mapping
        cur.execute("""
            SELECT zodiac, wuxing, wave_color, odd_even
            FROM symbol_maps WHERE year = 2026 AND ball_number = ?
        """, (ball_int,))
        row = cur.fetchone()
        zodiac, wuxing, wave, odd_even = row if row else (None, None, None, None)

        cur.execute("""
            INSERT INTO numbers
                (period_id, lottery_type, position, ball_number, zodiac, wuxing, wave_color, odd_even)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (period_id, lottery_type, position, ball_int, zodiac, wuxing, wave, odd_even))

    conn.commit()
    conn.close()
    return period_id, ball_strings


def main():
    print(f"{'='*60}")
    print("[M2.2] Single Period Validation")
    print('='*60)

    for lt in [2, 1]:  # Try 澳门 first (user's primary interest)
        try:
            print(f"\n[FETCH] lotteryType={lt} ({LOTTERY_TYPES[lt]})")
            data = fetch_latest(lt)
            period_id, balls = ingest(data, lt)
            print(f"[OK] Period {period_id} ingested")
            print(f"     Balls: {balls}")
        except Exception as e:
            print(f"[FAIL] lotteryType={lt}: {e}")

    # Verify in DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print(f"\n{'='*60}")
    print("[VERIFY] Database state after ingestion")
    print('='*60)
    for lt in [1, 2]:
        cur.execute("""
            SELECT p.period_id, p.lottery_name, p.draw_date, n.ball_number, n.zodiac, n.wuxing, n.wave_color, n.position
            FROM periods p
            JOIN numbers n ON p.period_id = n.period_id AND p.lottery_type = n.lottery_type
            WHERE p.lottery_type = ?
            ORDER BY p.period_id DESC, n.position
            LIMIT 8
        """, (lt,))
        rows = cur.fetchall()
        print(f"\n  {LOTTERY_TYPES[lt]} (latest):")
        for r in rows:
            print(f"    P{r[0]} | pos={r[7]} | ball={r[3]:02d} | {r[4] or '?':<4} | {r[5] or '?':<2} | {r[6] or '?'}")
    conn.close()


if __name__ == "__main__":
    main()