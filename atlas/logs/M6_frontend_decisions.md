# Working Log — M6: Frontend UI (Atlas Visualizer)

**Date:** 2026-07-13
**Stage:** M6 — Frontend build
**Status:** 🚧 IN PROGRESS

---

## User decisions (locked in)

| # | Decision | Choice | Notes |
|---|----------|--------|-------|
| Q1 | Data scope | **A** — 澳门 only (lotteryType=2) | 单一彩种专注 |
| Q2 | Selection mode | **Both** — Top-N + Cover-N | 两种都给 |
| Q3 | Frequency strategy | **d** — auto + manual + daily snapshot | 全做 |
| Q4 | Frontend stack | **b** — Vite + React + TypeScript | 专业工程化 |
| Q5 | Data gap handling | **a** — wait for real batch data first | M2.5 在做批量抓取 |
| Q6 | GO? | **GO** | 已启动 |

## Hard boundaries (will be enforced in UI)

1. ❌ No real-money betting integration (no API to external bookies)
2. ❌ No "guaranteed hit" copy — all probability language is scientific
3. ✅ Disclaimer banner is **always visible**, not dismissable
4. ✅ "Expected loss" calculator shown on every selection

## Project layout (planned)

```
~/dev/liuhe-atlas-ui/             ← New sibling repo (keeps scraper separate)
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── index.html
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── DisclaimerBanner.tsx     ← always visible top
│   │   ├── ModeSwitcher.tsx         ← Top-N vs Cover-N
│   │   ├── CountSlider.tsx          ← 1-45 selector
│   │   ├── BallGrid.tsx             ← 49-ball interactive grid
│   │   ├── RecommendationPanel.tsx  ← ranked list
│   │   ├── CoverageAnalyzer.tsx     ← symbol coverage stats
│   │   ├── BacktestChart.tsx        ← historical hit rate
│   │   ├── ExpectedLossCard.tsx     ← sobering math
│   │   └── DataStatusBar.tsx        ← last update / data scope
│   ├── lib/
│   │   ├── predictor.ts             ← Bayesian L2 (TS port)
│   │   ├── dataLoader.ts            ← load lotto.db snapshots
│   │   ├── coverage.ts              ← symbol aggregations
│   │   └── backtest.ts              ← simulator
│   ├── types.ts
│   └── styles.css                   ← dark theme tokens
└── data/
    └── snapshot.json                ← exported from lotto.db
```

## Data flow

```
lotto.db (Python)
   ↓ (export script)
data/snapshot.json (static JSON, loaded by browser)
   ↓
predictor.ts → ranked balls with probability
   ↓
UI components render

Refresh cycle: Python export script → snapshot.json → Vite dev server reload
```

---

## Notes for next step

- M6.1: Scaffold Vite project. Will use `npm create vite@latest` with React+TS template.
- M6.5 design: Use SVG for the 49-ball grid (cleaner than divs + Tailwind, easier animations).
- M6.10 disclaimer: Cannot be closed. Will use position:sticky + z-index high. Visible on all viewports.