"""
M2.5 — Backfill synthetic 100 periods of 澳门 history.

WHY: The data sources (六合宝典 / 49图库) don't expose historical endpoint.
We can only fetch latest period. For UI demonstration of backtest chart,
generate synthetic past periods that respect the basic statistical properties
of the lottery (7 balls per period, ball range 1-49, year-aware zodiac mapping).

These are MARKED CLEARLY as `source = 'synthetic_backfill'` so the user knows
they're not real draws. The system can be told to ignore them for any real analysis.
"""
import json
import sqlite3
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent  # spiders → atlas → liuhe-atlas
DB_PATH = PROJECT_ROOT / "data" / "lotto.db"

LOTTERY_TYPE = 2  # 澳门 only


def backfill(n_periods: int = 100, seed: int = 42):
    """Insert n_periods synthetic periods for 澳门 2020-2025.

    Uses realistic distribution: 7 random balls per period, range 1-49.
    """
    random.seed(seed)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Map year ranges to period counts (mock distribution)
    # Real 六合 aggregates ~156 draws/year (3x/week)
    periods_per_year = {
        2020: n_periods // 6,
        2021: n_periods // 6,
        2022: n_periods // 6,
        2023: n_periods // 6,
        2024: n_periods // 6,
        2025: n_periods - 5 * (n_periods // 6),
    }

    base_date = datetime(2020, 1, 1)
    inserted = 0

    for year in sorted(periods_per_year.keys()):
        year_count = periods_per_year[year]
        for p in range(1, year_count + 1):
            period_id = year * 1000 + p
            # Real draws are ~2-3 per week; space them ~2-3 days apart
            draw_dt = base_date + timedelta(days=(year - 2020) * 365 + p * 2.5)
            draw_date = draw_dt.strftime("%Y年%m月%d日21时32分 星期") + ["一","二","三","四","五","六","日"][draw_dt.weekday()]
            balls = sorted(random.sample(range(1, 50), 7), key=lambda _: random.random())
            # source is the synthetic marker
            source = "synthetic_backfill_for_ui_demo"

            # Insert period
            cur.execute("""
                INSERT OR IGNORE INTO periods
                    (period_id, lottery_type, lottery_name, draw_date, source_domain, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                period_id, LOTTERY_TYPE, "澳门六合彩", draw_date,
                source, json.dumps({"synthetic": True, "note": "Mock data for UI demo only"}, ensure_ascii=False)
            ))
            if cur.rowcount == 0:
                continue

            # Insert numbers
            for position, ball in enumerate(balls, start=1):
                # Look up symbol from symbol_maps for the year
                cur.execute("""
                    SELECT zodiac, wuxing, wave_color, odd_even
                    FROM symbol_maps WHERE year = ? AND ball_number = ?
                """, (year, ball))
                row = cur.fetchone()
                zodiac, wuxing, wave, odd_even = row if row else (None, None, None, None)

                cur.execute("""
                    INSERT INTO numbers
                        (period_id, lottery_type, position, ball_number, zodiac, wuxing, wave_color, odd_even)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (period_id, LOTTERY_TYPE, position, ball, zodiac, wuxing, wave, odd_even))
            inserted += 1

    conn.commit()
    conn.close()

    print(f"[OK] Backfilled {inserted} synthetic periods (2020-2025)")
    print(f"     Source: synthetic_backfill_for_ui_demo")
    print(f"     Use 'source = real_*' queries to exclude these from real analysis.")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    backfill(n)