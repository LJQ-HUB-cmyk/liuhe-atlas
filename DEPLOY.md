# 部署指南 (Vercel + GitHub Actions)

## 一次性配置 (~15 分钟)

### 1. ✅ GitHub Repo (已创建)
https://github.com/yimgao/liuhe-atlas — public, monorepo, initial commit pushed.

### 2. Vercel 导入

打开 https://vercel.com/new, 选 "Import Git Repository".

| 字段 | 值 |
|------|----|
| Repository | `yimgao/liuhe-atlas` |
| Root Directory | `atlas-ui` ← **关键, 不要选默认根** |
| Framework Preset | "Other" (不要选 Vite — Vercel 会用错路径) |
| Build Command | `npm run build` (vercel.json 已写) |
| Output Directory | `dist` (vercel.json 已写) |
| Install Command | `npm install` |

点 Deploy. ~1 分钟, 你会拿到一个 `*.vercel.app` 域名.

### 3. Vercel 环境变量 (可选)

Vercel → Project Settings → Environment Variables. 当前**不需要任何环境变量** (前端无 API key). 留空.

### 4. 触发首次 deploy

`atlas-ui/vercel.json` 已 commit. Vercel 会在第一次 push 自动 build.

## 数据流 (持续)

```
┌─────────────────────────────────────────────────────────────┐
│ 本机 (Mac) — ~/dev/liuhe/                                   │
│   cron 21:35                                                │
│     ├─ atlas/.venv/bin/python fetch_latest.py                │
│     ├─ export_snapshot.py → atlas-ui/public/data/snapshot.json
│     └─ (snapshot.json 已 commit 进 git, 本机不需要 push)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions — .github/workflows/refresh-snapshot.yml     │
│   每天 22:00 UTC (cron)                                      │
│     ├─ ubuntu runner                                         │
│     ├─ python fetch_latest.py (best-effort)                  │
│     ├─ python export_snapshot.py                             │
│     └─ 如果 snapshot.json 变化 → commit + push              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Vercel — 检测到 push → auto-rebuild                          │
│   atlas-ui/dist/ → CDN 全球                                 │
│   https://liuhe-atlas.vercel.app/data/snapshot.json (cached) │
└─────────────────────────────────────────────────────────────┘
```

⚠️ **两套 cron 互相覆盖**:
- 本机 21:35 EDT 跑一次 (快, 数据新鲜)
- GH Actions 22:00 UTC (≈ 18:00 EDT next day / 06:00 Beijing) 跑一次 (异地备份)
- 谁后跑谁说了算 — 通常 GH Actions 后跑, Vercel 上看到的是 GH Actions 导出的 snapshot

## 本地调试 vs 线上

| 场景 | 命令 | 数据源 |
|------|------|--------|
| 本地 dev | `cd atlas-ui && npm run dev` | `public/data/snapshot.json` |
| Vercel preview | push branch | `dist/data/snapshot.json` (从 public/data 复制) |
| Vercel production | merge to main | 同上 |

## 故障排查

| 现象 | 检查 |
|------|------|
| Vercel build fail | `vercel.json` + `Root Directory: atlas-ui` |
| Vercel 上 snapshot 还是旧的 | GH Actions 是否成功? 看 Actions tab 的运行历史 |
| 页面 404 | Vercel rewrites (`vercel.json`) 是否生效 |
| 数据是 mock | `public/data/snapshot.json` 是 synthetic? 看 meta.real_period_count |

## 域名 (可选)

Vercel → Settings → Domains. 加 `liuhe.yourdomain.com` 然后去 DNS 加 CNAME.
免费 SSL 自动签.

## 免责声明要求 (强制)

公网部署 ≠ 可以弱化 disclaimer. 顶部红色 DisclaimerBanner 必须保留原文.
不要去掉 "非投注建议" / "i.i.d. 均匀随机" / "长期期望 ROI 必为负".
这些不是装饰 — 是法律意义上的 "simulation only" 标识.