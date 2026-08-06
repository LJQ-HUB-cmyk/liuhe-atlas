"""
Liuhe-Atlas cleanup utility.

When you have enough REAL data (>= 30 periods, ~1 month), remove the synthetic
backfill so the backtest chart shows real performance only.

Usage:
    python cleanup_synthetic.py [--dry-run]
"""
import sqlite3
import argparse
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent
DB_PATH = PROJECT_ROOT / "data" / "lotto.db"


def main():
    parser = argparse.ArgumentParser(description="Clean synthetic periods from liuhe-atlas DB")
    parser.add_argument("--dry-run", action="store_true", help="Count only, don't delete")
    parser.add_argument("--threshold", type=int, default=30,
                        help="Minimum real periods before cleaning (default: 30)")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""SELECT COUNT(*) FROM periods
                   WHERE lottery_type=2 AND source_domain NOT LIKE 'synthetic%'""")
    real_count = cur.fetchone()[0]
    cur.execute("""SELECT COUNT(*) FROM periods
                   WHERE lottery_type=2 AND source_domain LIKE 'synthetic%'""")
    syn_count = cur.fetchone()[0]

    print(f"Current state:")
    print(f"  Real periods: {real_count}")
    print(f"  Synthetic periods: {syn_count}")
    print(f"  Threshold for cleanup: {args.threshold}")

    if real_count < args.threshold:
        print(f"\n⚠️ Real count ({real_count}) below threshold ({args.threshold}).")
        print(f"   Continue accumulating via daily fetcher.")
        print(f"   Cleanup will happen automatically once you have enough real data.")
        return

    if syn_count == 0:
        print(f"\n✓ No synthetic data to remove.")
        return

    if args.dry_run:
        print(f"\n[DRY-RUN] Would delete {syn_count} synthetic periods.")
        return

    # Delete synthetic periods and their numbers
    cur.execute("""SELECT period_id FROM periods
                   WHERE lottery_type=2 AND source_domain LIKE 'synthetic%'""")
    syn_period_ids = [r[0] for r in cur.fetchall()]

    print(f"\nDeleting {syn_count} synthetic periods ({len(syn_period_ids)} IDs)...")
    cur.execute("""DELETE FROM numbers
                   WHERE period_id IN (
                       SELECT period_id FROM periods
                       WHERE lottery_type=2 AND source_domain LIKE 'synthetic%'
                   )""")
    cur.execute("""DELETE FROM periods
                   WHERE lottery_type=2 AND source_domain LIKE 'synthetic%'""")
    conn.commit()
    print(f"✓ Deleted {syn_count} periods + their numbers.")

    # Verify
    cur.execute("""SELECT COUNT(*) FROM periods WHERE lottery_type=2""")
    remaining = cur.fetchone()[0]
    print(f"  Remaining 澳门 periods: {remaining} (all real)")

    print("\n⚠️ Don't forget to re-export snapshot.json:")
    print("   python export_snapshot.py")

    conn.close()


if __name__ == "__main__":
    main()