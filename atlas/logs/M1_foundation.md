# Working Log — M1: Foundation Layer

**Date:** 2026-07-13
**Author:** Hermes Agent
**Stage:** M1 (Project Foundation)
**Status:** ✅ COMPLETED

---

## Goals for this stage
1. Bootstrap project structure
2. Design normalized database schema for lottery history + symbol mappings + predictions
3. Encode the static symbol mappings (五行/波色/单双/生肖) from the photo you provided
4. Seed initial data into SQLite

---

## What I built

### Project tree
```
~/dev/liuhe-atlas/
├── README.md                  (placeholder)
├── scrapy.cfg                 (placeholder)
├── seed_symbols.py            ← CLI: seed static symbol data
├── analyzer/                  (empty — for stats + ML)
├── atlas/
│   ├── symbol_maps/static.py  ← 静态符号映射 (五行/波色/单双/生肖 2026)
│   ├── spiders/               (empty — M2 will populate)
├── data/
│   ├── schema.sql             ← 6 tables
│   └── lotto.db               ← SQLite (49 rows of symbol_maps)
├── logs/                      (working logs live here)
├── notebooks/                 (empty)
└── web/                       (empty — M6 visualization)
```

### Database schema (6 tables)
| Table | Purpose | Key fields |
|-------|---------|------------|
| `periods` | 每期开奖记录 | period_id, lottery_type, draw_date, source_domain |
| `numbers` | 每期的 7 个号码 | period_id, position (1-7), ball, zodiac, wuxing, wave_color |
| `symbol_maps` | 号码→符号映射 (每年一套) | year, ball_number, zodiac, wuxing, wave_color, odd_even |
| `predictions` | 预测记录 + 回测结果 | period_id, model_name, top_5_balls, full_distribution, actual_special, hit_top_5 |
| `backtest_runs` | 回测框架的运行历史 | model_name, train_start, train_end, metrics JSON |
| `sources` | 抓取源的健康状态 | domain, last_seen, status (active/dead/blocked) |

### Static symbol mappings (from your photo)

**Source:** `/Users/yimgao/Downloads/澳门六合彩借鉴图.jpg` (2026年VIP精华版) + 香港六合文化公开规则

**Layer 1 — Number-invariant mappings (don't change by year):**
- `WUXING_MAP`: 49 ball → 金/木/水/火/土 (10/10/9/12/8 balls)
- `WAVE_MAP`: 49 ball → 红/蓝/绿 (17/16/16 balls)
- `ODD_EVEN_MAP`: 49 ball → 单/双 (deterministic: n % 2)

**Layer 2 — Year-varying mappings (need annual update):**
- `ZODIAC_MAP_2026`: 12 生肖 → numbers (only 2026 version hardcoded; will fetch historical years in M2.4)
- `ZODIAC_ATTRIBUTES`: 12 生肖 → 8 semantic attributes (天肖/地肖/阴肖/阳肖/男肖/女肖/吉肖/凶肖)

### Current DB state
```
symbol_maps: 49 rows (year=2026, all 1-49 covered)
periods:     0 rows
numbers:     0 rows
predictions: 0 rows
backtest_runs: 0 rows
sources:     0 rows
```

---

## Issues encountered / open questions

### Issue 1: 生肖-号码映射 解读有歧义
你的照片里生肖表的每列号码数不等（鼠 7 个 vs 马 1 个），这在六合文化里其实是"刻意"的——不同网站/不同年份版本都略有差异。

**Resolution:** 我先用了一个合理解读入库（让 49 球全覆盖）。**真实做法是**：M2.5 抓到完整历史数据后，用每期开奖结果反推每个号码的"实际生肖归属"，反向修正 symbol_maps。

### Issue 2: 静态映射 vs 动态映射的边界
五行/波色/单双是**号码的固有属性**（不随年份变）。
生肖/天地肖/吉凶肖是**号码的年属性**（每年农历年变）。

这意味着 symbol_maps 表必须按 (year, ball_number) 做联合主键，跨年查询时要用当年映射。

### Issue 3: 你要 7 年数据 → 需要 14 张符号表
2026/2025/2024/2023/2022/2021/2020 = 7 张年份表，加上 2012-2019 = 14 张。
这些表不能都 hardcode —— 必须从 83191.com 之类的论坛站抓。**M2.4 阶段处理。**

---

## Next stage: M2 (Data Acquisition)

**M2.1 — Install:**
```bash
pip install scrapy playwright pandas numpy scipy scikit-learn
playwright install chrome
```

**M2.2 — First spider:**
Write `atlas/spiders/lotto_history.py` that:
1. Launches Playwright headless browser
2. Navigates to 49图库 / 六合寶典 entry URL
3. Waits for `localStorage["apihost"]` to be set
4. Extracts API base URL
5. Fetches `/index/lastLotteryRecord?lotteryType=2`
6. Parses + ingests into `periods` + `numbers` tables

**M2.3 — Verify:**
Check that the ingested data matches what we manually saw in browser (period 2026192).

**M2.4 — Reverse-engineer batch endpoint:**
Look for `/index/listYear`, `/discovery/list`, `/picture/pictureSeriesList` endpoints.
Find a way to enumerate all historical periods.

**M2.5 — Batch fetch:**
Run spider, target 7 years (~2500 periods), rate-limited to 1 req/2s.

---

## Honest disclaimer (will repeat in every stage)

This project is a **statistical learning research artifact**. The "prediction" output is:
- A probability distribution (not a guaranteed number)
- Backtested honestly (will report lift vs uniform even if it's negative)
- Accompanied by signal-strength scoring
- Designed to **NOT** encourage gambling

If at any point signal strength is too weak to justify prediction, I'll explicitly mark the model as "no signal" and skip the prediction output.

---

## Files for review

| File | Status | Notes |
|------|--------|-------|
| `~/dev/liuhe-atlas/data/schema.sql` | ✅ | 6 tables |
| `~/dev/liuhe-atlas/data/lotto.db` | ✅ | 49 rows |
| `~/dev/liuhe-atlas/atlas/symbol_maps/static.py` | ✅ | Static mappings |
| `~/dev/liuhe-atlas/seed_symbols.py` | ✅ | Seed script |
| `~/dev/liuhe-atlas/logs/M1_foundation.md` | ✅ | This file |