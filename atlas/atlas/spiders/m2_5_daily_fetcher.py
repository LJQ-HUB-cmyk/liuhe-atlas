"""
M2.5 — Daily lottery fetcher

Crawls 六合宝典 / 49图库 to get latest 澳门 (lotteryType=2) draw.
Designed to be run once per day via cron.

Idempotent: re-running the same day just updates today's record.
Cumulative: builds a long history over time.
"""
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent  # spiders/m2_5 → atlas → liuhe-atlas
DB_PATH = PROJECT_ROOT / "data" / "lotto.db"

# Sources (in priority order — first one that returns 200 + valid data wins)
SOURCES = [
    {
        "name": "六合宝典",
        "base": "https://82hats7.66852.cc:8443/bible/h5",
        "path": "/index/lastLotteryRecord",
        "data_keys": ("originalDataList", "period", "year"),
    },
    {
        "name": "49图库",
        "base": "https://6xr4in4.xn--eck6e6bcfa3628cg56c.xn--q9jyb4c/unite49/h5",
        "path": "/index/lastLotteryRecord",
        "data_keys": ("numberList", "period", "year"),  # different field name
    },
]

LOTTERY_TYPES = {2: "澳门六合彩", 1: "香港六合彩"}


def make_session():
    """Build a session with retry logic for transient failures."""
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1.5,
                    status_forcelist=[502, 503, 504, 408],
                    allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


def fetch_latest(src: dict, session: requests.Session, lottery_type: int = 2) -> dict:
    """Fetch the latest period for given lottery_type from source."""
    url = src["base"] + src["path"]
    resp = session.get(url, params={"lotteryType": lottery_type}, timeout=15, verify=False)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 10000:
        raise RuntimeError(f"{src['name']} API error: {payload}")
    return payload["data"]


def normalize(source_name: str, raw: dict, lottery_type: int) -> dict:
    """Normalize different source's data formats to a canonical shape."""
    if source_name == "六合宝典":
        period_id = raw["year"] * 1000 + raw["period"]
        balls = raw["originalDataList"]
        draw_date = raw.get("title", f"{raw.get('nextLotteryTime', '')} 21:32:00")
    elif source_name == "49图库":
        period_id = raw["year"] * 1000 + raw["period"]
        balls = raw["numberList"]
        draw_date = raw.get("lotteryTime", "") + " 21:32:00" if raw.get("lotteryTime") else ""
    else:
        raise ValueError(f"Unknown source: {source_name}")

    return {
        "period_id": period_id,
        "lottery_type": lottery_type,
        "lottery_name": LOTTERY_TYPES.get(lottery_type, "Unknown"),
        "draw_date": draw_date,
        "source_domain": src_base_for(source_name).split("//")[1].split("/")[0],
        "raw_payload": raw,
    }


def src_base_for(source_name: str) -> str:
    for s in SOURCES:
        if s["name"] == source_name:
            return s["base"]
    raise ValueError(f"Unknown source: {source_name}")


def ingest(conn, normalized: dict):
    """Insert period + 7 numbers into SQLite. Idempotent.

    Skips insertion if originalDataList contains non-numeric values (some 六合
    aggregators return Chinese text in originalDataList when they want to advertise
    upcoming draws, e.g. "六合宝典开奖快").
    """
    raw = normalized["raw_payload"]
    balls_field = "originalDataList" if "originalDataList" in raw else "numberList"
    raw_balls = raw.get(balls_field, [])

    # Validate: must have at least 7 entries that parse as integers 1-49
    valid_balls = []
    for b in raw_balls[:7]:
        try:
            n = int(b)
            if 1 <= n <= 49:
                valid_balls.append(n)
        except (ValueError, TypeError):
            continue

    if len(valid_balls) < 7:
        print(f"  [SKIP] Period {normalized['period_id']}: only {len(valid_balls)}/7 valid numeric balls (skipped — likely promo text)")
        return False

    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO periods
            (period_id, lottery_type, lottery_name, draw_date, source_domain, raw_payload)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        normalized["period_id"],
        normalized["lottery_type"],
        normalized["lottery_name"],
        normalized["draw_date"],
        normalized["source_domain"],
        json.dumps(normalized["raw_payload"], ensure_ascii=False),
    ))

    cur.execute("DELETE FROM numbers WHERE period_id = ? AND lottery_type = ?",
                (normalized["period_id"], normalized["lottery_type"]))

    # Use validated balls (don't re-validate during insert)
    year = normalized["period_id"] // 1000
    for position, ball_int in enumerate(valid_balls, start=1):
        cur.execute("""
            SELECT zodiac, wuxing, wave_color, odd_even
            FROM symbol_maps
            WHERE year = ? AND ball_number = ?
        """, (year, ball_int))
        row = cur.fetchone()
        zodiac, wuxing, wave, odd_even = row if row else (None, None, None, None)

        cur.execute("""
            INSERT INTO numbers
                (period_id, lottery_type, position, ball_number, zodiac, wuxing, wave_color, odd_even)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (normalized["period_id"], normalized["lottery_type"], position, ball_int,
              zodiac, wuxing, wave, odd_even))

    conn.commit()
    return True


def fetch_all(session: requests.Session, lottery_types: list[int], 
              max_retries: int = 1, retry_wait_seconds: int = 0) -> dict:
    """Try all sources × all lottery_types. Return successes.

    Staggered retry: if the latest period returns promo text (not numeric),
    wait + retry. Cron schedules should pass max_retries=1 (no in-process
    waiting) and rely on multiple cron schedules at different times.
    """
    results = {}
    for lt in lottery_types:
        for src in SOURCES:
            try:
                raw = fetch_latest(src, session, lt)

                # Check if numeric (not promo)
                balls_field = "originalDataList" if "originalDataList" in raw else "numberList"
                raw_balls = raw.get(balls_field, [])
                numeric_count = sum(
                    1 for b in raw_balls[:7]
                    if isinstance(b, str) and b.isdigit() and 1 <= int(b) <= 49
                )

                if numeric_count < 7 and max_retries > 1:
                    for attempt in range(2, max_retries + 1):
                        print(f"  [RETRY {attempt}/{max_retries}] {src['name']} lt={lt}: promo, wait {retry_wait_seconds}s...")
                        time.sleep(retry_wait_seconds)
                        try:
                            raw = fetch_latest(src, session, lt)
                            raw_balls = raw.get(balls_field, [])
                            numeric_count = sum(
                                1 for b in raw_balls[:7]
                                if isinstance(b, str) and b.isdigit() and 1 <= int(b) <= 49
                            )
                            if numeric_count >= 7:
                                break
                        except Exception as e:
                            print(f"  [RETRY FAILED] {e}")

                if numeric_count < 7:
                    print(f"  [SKIP] {src['name']} lt={lt}: promo, will retry on next cron run")
                    continue

                normalized = normalize(src["name"], raw, lt)
                results[lt] = normalized
                print(f"  [OK] {src['name']} → period {normalized['period_id']}")
                break
            except Exception as e:
                print(f"  [FAIL] {src['name']} lotteryType={lt}: {e}")
                continue
    return results


def main():
    print(f"[INFO] Daily lottery fetch — {datetime.now(timezone.utc).isoformat()}")
    session = make_session()
    conn = sqlite3.connect(DB_PATH)

    print("[INFO] Fetching 澳门 + 香港...")
    results = fetch_all(session, [2, 1])

    if not results:
        print("[FATAL] All sources failed. Will retry tomorrow.")
        return 1

    for lt, normalized in results.items():
        try:
            ingested = ingest(conn, normalized)
            if ingested is False:
                # Period was skipped (likely promo text in originalDataList)
                continue
            balls = normalized["raw_payload"].get("originalDataList") or normalized["raw_payload"].get("numberList")
            print(f"[OK] Ingested period {normalized['period_id']} ({normalized['lottery_name']}): balls={balls}")
        except Exception as e:
            print(f"[FAIL] Ingest period {normalized['period_id']}: {e}")

    # Summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), MIN(draw_date), MAX(draw_date) FROM periods WHERE lottery_type = 2")
    total, min_d, max_d = cur.fetchone()
    print(f"\n[SUMMARY] 澳门六合彩: {total} periods total ({min_d} → {max_d})")

    conn.close()
    return 0


if __name__ == "__main__":
    exit(main())