"""
M7 — Zodiac table derivation (FINAL working version)

Builds valid 1-1 zodiac assignments for years 2020-2025 from a 2026 anchor.

Method:
1. Take photo's zodiac columns (鼠-猪 = 12 lists of balls)
2. Resolve conflicts via priority order (鼠 > 牛 > 虎 > 兔 > 龙 > 蛇 > 马 > 羊 > 猴 > 鸡 > 狗 > 猪)
3. Distribute remaining balls to lowest-population zodiacs
4. For each historical year, rotate the zodiac cycle backward by N years
   (this is a heuristic — real 六合 tables vary by publisher, but cycle rotation
   captures the dominant pattern observed in most aggregators)
"""
import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent / "data" / "lotto.db"

ZODIAC_CYCLE = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

# Photo raw assignments (some balls claimed by multiple zodiacs)
PHOTO_RAW_2026 = {
    "鼠": [7, 13, 19, 25, 31, 37, 43],
    "牛": [6, 18, 24, 30, 36, 42, 48],
    "虎": [5, 17, 23, 29, 35, 41, 47],
    "兔": [4, 16, 22, 28, 34, 40, 46],
    "龙": [3, 15, 21, 27, 33, 39, 45],
    "蛇": [2, 14, 26, 38],
    "马": [1, 49],
    "羊": [12, 36],
    "猴": [11, 35],
    "鸡": [10, 22, 34, 46],
    "狗": [9, 21, 33, 45],
    "猪": [8, 20, 32, 44],
}


def resolve_photo_to_1to1(photo: dict) -> dict:
    """Resolve photo's overlapping assignments into strict 1-ball-1-zodiac."""
    # Priority order: 鼠-猪 (column order in photo = priority)
    priority = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    used = set()
    out = {z: [] for z in priority}
    for z in priority:
        for b in photo[z]:
            if b not in used:
                out[z].append(b)
                used.add(b)
    # Distribute remaining balls to lowest-population zodiacs
    remaining = sorted(set(range(1, 50)) - used)
    for b in remaining:
        target = min(priority, key=lambda z: len(out[z]))
        out[target].append(b)
        out[target].sort()
    return out


def rotate_cycle(anchor_map: dict, years_back: int) -> dict:
    """Rotate zodiac mapping backward by N years.
    Convention: 2025 (one year before 2026) gets the balls that the NEXT zodiac
    in cycle had in 2026. This matches most 六合 aggregators' observed pattern.
    """
    if years_back == 0:
        return {z: list(balls) for z, balls in anchor_map.items()}
    out = {}
    for i, zodiac in enumerate(ZODIAC_CYCLE):
        source_idx = (i + years_back) % len(ZODIAC_CYCLE)
        source_zodiac = ZODIAC_CYCLE[source_idx]
        out[zodiac] = list(anchor_map[source_zodiac])
    return out


def derive_all_years(anchor_year=2026):
    """Derive zodiac maps for years 2020-2025 from 2026 anchor."""
    anchor_clean = resolve_photo_to_1to1(PHOTO_RAW_2026)
    maps = {anchor_year: anchor_clean}
    for y in range(2020, 2026):
        years_back = anchor_year - y
        maps[y] = rotate_cycle(anchor_clean, years_back)
    return maps


def validate_1to1(year_map: dict) -> bool:
    """Verify 49 balls covered exactly once."""
    seen = []
    for balls in year_map.values():
        seen.extend(balls)
    return sorted(seen) == list(range(1, 50))


def seed_yearly_maps(conn, maps: dict):
    cur = conn.cursor()
    # Pull year-invariant columns from 2026 row (already in DB)
    cur.execute("""
        SELECT ball_number, wuxing, wave_color, odd_even
        FROM symbol_maps WHERE year = 2026
    """)
    invariant = {row[0]: (row[1], row[2], row[3]) for row in cur.fetchall()}

    total = 0
    for year, ymap in sorted(maps.items()):
        cur.execute("DELETE FROM symbol_maps WHERE year = ?", (year,))
        for zodiac, balls in ymap.items():
            for ball in balls:
                wuxing, wave, odd_even = invariant.get(ball, (None, None, None))
                cur.execute("""
                    INSERT INTO symbol_maps
                        (year, ball_number, zodiac, wuxing, wave_color, odd_even, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    year, ball, zodiac, wuxing, wave, odd_even,
                    f"derived_from_2026_anchor (rotate_back={2026 - year})"
                ))
                total += 1
    conn.commit()
    return total


def main():
    print("=== Step 1: Resolve photo's 1-1 mapping for 2026 ===")
    anchor_clean = resolve_photo_to_1to1(PHOTO_RAW_2026)
    print(f"  2026 zodiac assignments:")
    for z in ZODIAC_CYCLE:
        print(f"    {z}: {anchor_clean[z]} ({len(anchor_clean[z])} balls)")
    print(f"  Valid 1-1: {validate_1to1(anchor_clean)}")

    print("\n=== Step 2: Derive 2020-2025 via cycle rotation ===")
    maps = derive_all_years(2026)
    for year in sorted(maps.keys()):
        valid = validate_1to1(maps[year])
        flag = "OK" if valid else "FAIL"
        print(f"  {year}: {flag}")
        # Print brief summary
        populations = [len(maps[year][z]) for z in ZODIAC_CYCLE]
        print(f"    populations: {populations}")

    print("\n=== Step 3: Seed into SQLite ===")
    conn = sqlite3.connect(DB_PATH)
    total = seed_yearly_maps(conn, maps)
    print(f"  Inserted {total} rows")

    cur = conn.cursor()
    cur.execute("SELECT year, COUNT(*) FROM symbol_maps GROUP BY year ORDER BY year")
    print("\n=== Final DB state ===")
    for year, cnt in cur.fetchall():
        print(f"  {year}: {cnt} rows")
    conn.close()


if __name__ == "__main__":
    main()