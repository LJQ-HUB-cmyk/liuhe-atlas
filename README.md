# 六合图谱 · Atlas — Monorepo

> 澳门六合彩 · 统计分析研究项目
> ⚠️ **Simulation only. Not betting advice.**

```
liuhe/
├── atlas/        ← Python 后端: scraper + SQLite + cron + 模型
│   ├── atlas/spiders/        抓取脚本
│   ├── data/lotto.db         SQLite (gitignored)
│   ├── export_snapshot.py    DB → JSON
│   ├── logs/                 工作日志 (M1~M7)
│   └── .venv/                Python venv (gitignored)
│
└── atlas-ui/     ← Vite/React 前端
    ├── src/                  18 个组件 + lib
    ├── public/data/snapshot.json   ← 由 atlas cron 写入
    ├── dist/                 production build (gitignored)
    └── node_modules/         (gitignored)
```

## 部署架构 (Vercel + GitHub Actions)

```
[本机 cron 21:35]  ~/dev/liuhe/atlas/.venv/bin/python export_snapshot.py
                              ↓ writes
                    ~/dev/liuhe/atlas-ui/public/data/snapshot.json
                              ↓
              [GitHub Actions] commit + push to repo
                              ↓
                    [Vercel] detects push → auto-rebuild → CDN
                              ↓
                    https://liuhe-atlas.vercel.app
```

## 本地开发

```bash
# 后端
cd atlas
source .venv/bin/activate
python export_snapshot.py   # 写一次 snapshot 给前端

# 前端
cd ../atlas-ui
npm install
npm run dev    # http://localhost:5173
```

## 数据流详细

详见 `atlas-ui/USER_MANUAL.md` §6.

## Hosting 步骤 (一次性)

1. 把整个 `liuhe/` push 到 GitHub (repo 暂定 `liuhe-atlas`)
2. Vercel:
   - Import `liuhe-atlas` repo
   - Root directory: `atlas-ui`
   - Build command: `npm run build`
   - Output: `dist`
3. GitHub Actions:
   - 每天 22:00 UTC 自动 commit + push `atlas-ui/public/data/snapshot.json`
   - 触发 Vercel auto-rebuild

详见 `DEPLOY.md`.