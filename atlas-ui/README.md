# 六合图谱 · Atlas — Frontend

> 澳门六合彩 · 统计分析研究项目 — Web UI
> ⚠️ **Simulation only. Not betting advice.** Statistical learning project. Real draws are i.i.d. uniform random — long-run expected ROI is negative regardless of model output. No real betting supported.

## 这是什么

Vite + React + TypeScript 前端。可视化展示 `liuhe-atlas` 数据层跑出来的
贝叶斯聚合概率分布，支持中英双语、深浅主题、自动选号、PDF 导出等。

## 状态

- ✅ 18 个组件全部就位 (M6 + M6P + M6P2)
- ✅ 中英双语 (24+ i18n keys)
- ✅ 深 / 浅主题切换
- ✅ 实时倒计时 (距下期开奖 / 下次 cron 刷新)
- ✅ ErrorBoundary 包裹 — 单组件崩溃不会黑屏
- ✅ 浏览器验证通过 — `npm run dev` → http://localhost:5173/ — 0 console errors

数据：当前 19 期真实数据 (snapshot.json ~69KB)
下游 cron 每小时跑一次，写入 `public/data/snapshot.json`。

## 开发

```bash
npm install
npm run dev      # http://localhost:5173/
npm run build
```

## 目录

```
src/
  App.tsx                  # 主组合
  main.tsx                 # 入口 + ErrorBoundary
  components/
    DisclaimerBanner       # 顶部红色 disclaimer
    DataStatusBar          # 数据条 (期数 / 时间 / 模型 / 信号强度)
    LanguageSwitcher       # 中 / 英
    ThemeSwitcher          # 深 / 浅主题
    CountdownTimer         # 倒计时
    Controls               # Top-N / Cover-N 模式 + 滑块
    BallGrid               # 49 球网格 (五行 + 波色)
    RecommendationPanel    # 当前已选号码
    AutoPick               # 4 模式自动选号 (融合 / 交集 / 模型 / 频率)
    CoverageAnalyzer       # 覆盖率分析
    NumberFrequencySparkline
    SymbolDimensionHeatmap # 符号维度热力图
    SymbolDimensionBreakdown
    UniformityCheck        # 均匀性检验
    BacktestChart          # 静态回测
    RollingWindowBacktest  # 滚动窗口回测
    WinProbabilityCard     # 至少中 1 球 / 中特码 概率
    ExpectedLossCard       # 期望亏损模拟器 (诚实数学)
    StrategyComparison     # Top-N vs Cover-N vs 随机基线
    ExportReport           # PDF 导出 (新窗口 + 浏览器打印)
    CopyNumbersWithMeta    # 富文本复制 (含模型 / 时间戳)
  lib/
    i18n.ts                # 翻译
    theme.ts               # 主题 singleton
  types.ts
  index.css                # 全 light theme 支持
public/
  data/snapshot.json       # 由 liuhe-atlas cron 导出 (69KB)
```

## 免责声明 (项目级)

本项目所有功能 — 包括 AutoPick、RecommendationPanel、WinProbabilityCard —
均为**统计学习 / 概率可视化**用途。真实开奖是 i.i.d. 均匀随机，
任意选号策略的长期期望 ROI 必为负，模型输出不影响这一事实。
`ExpectedLossCard` 已用默认派彩 45× 演示"什么条件下数学上正期望"，
真实私彩几乎不可能达到此派彩，结论：永远不要拿真钱试。

详见 `~/dev/liuhe-atlas/README.md` 和项目 logs/。