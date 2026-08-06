# Working Log — M2: Data Acquisition (single-period)

**Date:** 2026-07-13
**Stage:** M2 (Data Acquisition) — first milestone
**Status:** ✅ COMPLETED (single period validation)

---

## Goals
1. Install all dependencies (scrapy, playwright, etc.)
2. Discover the real API endpoint for lottery data
3. Fetch the latest period of 澳门六合彩 + 香港六合彩
4. Ingest into SQLite with all symbol attributes joined

---

## What I built

### M2.1 — Dependencies installed
- scrapy 2.17.0
- playwright 1.61.0 (+ chromium browser)
- pandas 3.0.3, numpy 2.4.6, scipy 1.17.1, scikit-learn 1.9.0
- venv: `~/dev/liuhe-atlas/.venv/`

### M2.2 — Discovery & working spider
Created `atlas/spiders/m2_2_single_period.py` that:
1. Calls `GET https://82hats7.66852.cc:8443/bible/h5/index/lastLotteryRecord?lotteryType=N`
2. Parses JSON response
3. Ingests into `periods` + `numbers` tables
4. Joins with `symbol_maps` to populate zodiac/wuxing/wave_color/odd_even

### M2.3 — Validation passed
Latest data successfully ingested:

**澳门六合彩 — Period 2026194 (2026-07-12)**
| Pos | Ball | Zodiac | Wuxing | Wave | Odd/Even |
|-----|------|--------|--------|------|----------|
| 1   | 30   | 牛     | 水     | 红   | 双 |
| 2   | 21   | 狗     | 土     | 绿   | 单 |
| 3   | 22   | 鸡     | 水     | 绿   | 双 |
| 4   | 15   | 龙     | 水     | 蓝   | 单 |
| 5   | 04   | 兔     | 金     | 蓝   | 双 |
| 6   | 34   | 鸡     | 金     | 红   | 双 |
| 7   | 26   | 蛇     | 金     | 蓝   | 双 |  ← 特码

**香港六合彩 — Period 2026075 (2026-07-12)**
| Pos | Ball | Zodiac | Wuxing | Wave | Odd/Even |
|-----|------|--------|--------|------|----------|
| 1   | 05   | 虎     | 金     | 绿   | 单 |
| 2   | 02   | 蛇     | 火     | 红   | 双 |
| 3   | 07   | 鼠     | 土     | 红   | 单 |
| 4   | 11   | 猴     | 火     | 绿   | 单 |
| 5   | 41   | 虎     | 火     | 蓝   | 单 |
| 6   | 46   | 鸡     | 木     | 红   | 双 |
| 7   | 43   | 鼠     | 金     | 绿   | 单 |  ← 特码

---

## Issues encountered & solutions

### Issue 1: Wrong API path
Initial guess was `/index/lastLotteryRecord` — turned out the real path is `/bible/h5/index/lastLotteryRecord`.
**Solution:** Wrote `m2_2_discover.py` (now archived) that captures ALL network responses from the page. Found the real endpoints by sniffing traffic.

### Issue 2: Wrong data field names
Initial code expected `data["balls"]` / `data["periodId"]` — actual fields are `originalDataList` / `period`.
**Solution:** Direct curl to the API endpoint + visual inspection of JSON.

### Issue 3: SQLite ON CONFLICT error
`period_id INTEGER PRIMARY KEY` is auto rowid alias; `ON CONFLICT(period_id, lottery_type)` requires the UNIQUE index to be named/structured differently than expected by SQLite.
**Solution:** Switched to `INSERT OR REPLACE` (simpler, works correctly for our upsert pattern).

### Issue 4: Initial wrong assumption about response structure
The `/index/apiHost` endpoint doesn't actually return the apiHost base URL — that's a legacy misnomer. The real API host is the same domain we're already calling (no redirect needed).

---

## API endpoints discovered (M2.4 will use these)

```
GET  /bible/h5/index/lastLotteryRecord?lotteryType=N  → latest period (lotteryType 1 or 2)
GET  /bible/h5/index/apiHost                          → config object (not needed for our use)
GET  /bible/h5/picturenew/listYear                    → years available for pictures
GET  /bible/h5/picturenew/listPicture?pageNum=&lotteryType= → picture list
POST /bible/h5/discovery/list                         → discovery list (probably year list)
```

**For M2.5 batch fetch, I need to find:**
- An endpoint that returns historical periods by date or period_id range
- The discovery endpoint pattern (`/discovery/list?year=&lotteryType=`)

---

## Next stage: M2.5 (batch fetch)

**Plan:**
1. Test `GET /bible/h5/discovery/list?year=2026&lotteryType=2` — if works, returns all periods of 2026
2. Test with year=2025, 2024, ... backwards
3. For each period returned, fetch detailed data (might be the same as `lastLotteryRecord` but with period param)
4. Parallelize with asyncio + semaphore (1 req/2s rate limit)
5. Save progress to SQLite as we go (no in-memory batching)

**Estimated time:** 2-3 hours for full 7-year batch.

---

## Files for review

| File | Status | Notes |
|------|--------|-------|
| `~/dev/liuhe-atlas/atlas/spiders/m2_2_single_period.py` | ✅ | Working single-period spider |
| `~/dev/liuhe-atlas/atlas/spiders/m2_2_discover.py` | ✅ | Network sniffer (used once, kept for reference) |
| `~/dev/liuhe-atlas/data/lotto.db` | ✅ | 2 periods ingested |
| `~/dev/liuhe-atlas/logs/M2_data_acquisition.md` | ✅ | This file |