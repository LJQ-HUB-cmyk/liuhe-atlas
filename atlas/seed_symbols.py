"""把静态符号映射灌进 SQLite"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from atlas.symbol_maps.static import (
    WUXING_MAP, WAVE_MAP, ODD_EVEN_MAP, NUMBER_TO_ZODIAC_2026
)

def seed_static_map(year: int = 2026):
    db_path = Path(__file__).parent / "data" / "lotto.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 清旧
    cur.execute("DELETE FROM symbol_maps WHERE year = ?", (year,))

    inserted = 0
    for ball in range(1, 50):
        wuxing = WUXING_MAP.get(ball, "?")
        wave = WAVE_MAP.get(ball, "?")
        odd_even = ODD_EVEN_MAP.get(ball, "?")
        zodiac = NUMBER_TO_ZODIAC_2026.get(ball, None)
        cur.execute("""
            INSERT OR IGNORE INTO symbol_maps
                (year, ball_number, zodiac, wuxing, wave_color, odd_even, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (year, ball, zodiac, wuxing, wave, odd_even, "static_seed_2026"))
        inserted += 1

    conn.commit()
    print(f"[OK] Inserted {inserted} symbol_map rows for year {year}")

    # 验证
    cur.execute("""
        SELECT zodiac, COUNT(*) FROM symbol_maps
        WHERE year = ?
        GROUP BY zodiac
        ORDER BY zodiac
    """, (year,))
    print("\n=== 12生肖分布 (2026) ===")
    for zodiac, cnt in cur.fetchall():
        print(f"  {zodiac or 'NULL'}: {cnt} 球")

    # 检查没有覆盖的号码
    cur.execute("""
        SELECT ball_number FROM symbol_maps
        WHERE year = ?
    """, (year,))
    covered = set(r[0] for r in cur.fetchall())
    missing = [n for n in range(1, 50) if n not in covered]
    print(f"\n=== 未覆盖号码: {missing if missing else 'None ✓'} ===")

    conn.close()

if __name__ == "__main__":
    seed_static_map(2026)