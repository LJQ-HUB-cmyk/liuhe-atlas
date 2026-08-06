# Liuhe-Atlas — Operational Runbook

**Date:** 2026-07-13
**Stage:** DEPLOY (Production deployment)
**Status:** ✅ COMPLETED

---

## What's running

1. **Hermes cron job** `liuhe-atlas daily pipeline` runs daily at **21:35** (after Macau draw at 21:32)
2. **Wrapper script** `~/.hermes/scripts/liuhe-atlas-daily.sh` orchestrates: fetch → export → log → Sunday cleanup
3. **Daily fetcher** `~/dev/liuhe-atlas/atlas/spiders/m2_5_daily_fetcher.py` is idempotent + defensive

## Data flow (production)

```
[21:35 daily] cron fires
    ↓
~/.hermes/scripts/liuhe-atlas-daily.sh
    ↓
Step 1: python atlas/spiders/m2_5_daily_fetcher.py
    ├─ Try 六合宝典 first (https://82hats7.66852.cc:8443)
    ├─ Fallback 49图库 (https://6xr4in4.xn--...)
    ├─ Validate originalDataList has 7 valid numeric balls
    ├─ Skip periods with promo text (e.g. "六 合 宝 典 开 奖 快")
    └─ INSERT OR REPLACE (idempotent)
    ↓
Step 2: python export_snapshot.py
    ├─ Pull all real + synthetic periods from DB
    ├─ Bundle zodiac_maps for years 2020-2026
    └─ Write ~/dev/liuhe-atlas-ui/public/data/snapshot.json
    ↓
[Sunday only] Step 4: python cleanup_synthetic.py
    └─ If real periods >= 30, delete synthetic ones
    ↓
Log everything to ~/dev/liuhe-atlas/logs/cron-pipeline.log
```

## Cron schedule

| Job | Schedule | Purpose |
|-----|----------|---------|
| `liuhe-atlas daily pipeline` | `35 21 * * *` | Fetch + export (daily) |
| _implicit_ | `Sunday only` | cleanup_synthetic.py (auto-runs in wrapper) |

## How data accumulates

| Day | Real periods | Synthetic | Notes |
|-----|--------------|-----------|-------|
| Day 1 (today) | 2 | 100 | Already have 2 real (7/14, 7/16) + 100 mock |
| Day 7 | ~5 | 100 | ~3 more real per week (avg) |
| Day 30 | ~15 | 100 | Cleanup script will NOT trigger (threshold=30) |
| Day 45 | ~25 | 100 | Still under threshold |
| Day 60 | ~32 | 0 | Sunday auto-cleanup triggers, all 100 synthetic deleted |

After ~60 days, you have ~30 real periods + 0 synthetic.

## Manual operations

### Check current data state
```bash
sqlite3 ~/dev/liuhe-atlas/data/lotto.db "
  SELECT 'Real periods:', COUNT(*) FROM periods WHERE lottery_type=2 AND source_domain NOT LIKE 'synthetic%';
  SELECT 'Synthetic:', COUNT(*) FROM periods WHERE lottery_type=2 AND source_domain LIKE 'synthetic%';
"
```

### Force run pipeline now (skip cron)
```bash
/Users/yimgao/.hermes/scripts/liuhe-atlas-daily.sh
```

### Manual cleanup (skip Sunday wait)
```bash
cd ~/dev/liuhe-atlas
.venv/bin/python cleanup_synthetic.py --dry-run   # preview
.venv/bin/python cleanup_synthetic.py              # actually delete
.venv/bin/python export_snapshot.py                # refresh UI
```

### Re-backfill synthetic data (if you accidentally deleted and want demo back)
```bash
cd ~/dev/liuhe-atlas
.venv/bin/python atlas/spiders/m2_5_backfill_synthetic.py 100
.venv/bin/python export_snapshot.py
```

### Check cron logs
```bash
tail -50 ~/dev/liuhe-atlas/logs/cron-pipeline.log
```

### List all Hermes cron jobs
```bash
hermes cronjob list
```

## Known bugs fixed during deployment

1. **Non-numeric data bug**: API sometimes returns promo Chinese text in `originalDataList`
   (e.g. "六 合 宝 典 开 奖 快") when `display=1`. Fixed by validating that all 7 balls
   parse as integers 1-49 before inserting. Skipped periods print `[SKIP]` log line.

2. **`display` field is unreliable**: originally used as a "skip if promo" signal, but
   period 196 had `display=1` with valid numeric balls. Now we use direct validation
   of the ball values themselves, which is the source of truth.

3. **Shadowed variable**: `source` parameter shadowed outer-scope `source` dict in
   fetch loop. Renamed to `src`.

4. **Stale DB rows**: previously-inserted invalid period 2026197 deleted manually.

## Honest limitations

1. **Real data accumulation is slow**: ~3 real draws/week × 4 weeks = ~12/month.
   Need ~30+ real periods for statistically meaningful backtest. Expect ~2-3 months.

2. **API sources rotate domains**: 六合宝典 / 49图库 use XOR-encoded domain obfuscation.
   Our hardcoded base URLs (`82hats7.66852.cc:8443`, `6xr4in4.xn--...`) may go dead.
   Daily fetcher will then silently fail — check logs.

3. **Zodiac tables are derived, not authoritative**: We synthesized 2020-2025 zodiac
   mappings from 2026 anchor via cycle rotation. Real 六合 publishers publish
   different tables; cycle rotation captures dominant pattern but isn't perfect.

4. **Signal is weak**: Even with 30 real periods, lift vs uniform is likely < 1pp.
   Don't expect the model to actually beat baseline — it provides a probability
   distribution for educational/exploratory purposes, not for placing bets.

## Files for review

| File | Status | Purpose |
|------|--------|---------|
| `~/dev/liuhe-atlas/atlas/spiders/m2_5_daily_fetcher.py` | ✅ | Idempotent daily fetcher |
| `~/dev/liuhe-atlas/atlas/spiders/m2_5_backfill_synthetic.py` | ✅ | 100 mock periods for demo |
| `~/dev/liuhe-atlas/cleanup_synthetic.py` | ✅ | Remove synthetic when real ≥ 30 |
| `~/dev/liuhe-atlas/export_snapshot.py` | ✅ | DB → JSON snapshot |
| `~/dev/liuhe-atlas/derive_zodiac.py` | ✅ | Year-aware zodiac derivation |
| `~/.hermes/scripts/liuhe-atlas-daily.sh` | ✅ | Wrapper (fetch + export + cleanup) |
| Cron `liuhe-atlas daily pipeline` | ✅ | 21:35 daily |
| `~/dev/liuhe-atlas/logs/M7_M2.5_backfill.md` | ✅ | Previous stage log |
| `~/dev/liuhe-atlas/logs/DEPLOY_runbook.md` | ✅ | This file |