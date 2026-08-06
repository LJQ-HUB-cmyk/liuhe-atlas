import { useState } from 'react';
import { useLocale } from '../lib/i18n';
import { ThemeSwitcher } from './ThemeSwitcher';
import { LanguageSwitcher } from './LanguageSwitcher';

/**
 * User Guide — explains every section of the app.
 * Toggled by the 📖 Guide button in the header.
 *
 * Bilingual content lives inline (no i18n dependency) for simplicity —
 * the button label uses the i18n key 'app.guide'.
 */

interface Section {
  id: string;
  title: { zh: string; en: string };
  body: { zh: React.ReactNode; en: React.ReactNode };
}

const SECTIONS: Section[] = [
  {
    id: 'overview',
    title: { zh: '这是什么', en: 'What this is' },
    body: {
      zh: (
        <>
          <p>
            六合图谱 · Atlas 是一个<strong>统计学习 demo</strong>，不是预测服务。
            它的作用是把历史开奖数据按多种维度（数字、生肖、五行、波色）做概率分布估计，
            让你<strong>看到数据里的模式</strong>，并思考"如果用这模式选号，长期 ROI 是什么"。
          </p>
          <p>
            ⚠️ 真实澳门 / 香港 / 任何彩票开奖都是 <strong>i.i.d. 均匀随机</strong>，
            也就是说<strong>历史不会影响未来</strong>。本工具展示的所有"信号"在数学上长期都不会赢过随机选号。
            详见顶部红色 DisclaimerBanner 和"期望亏损模拟器"。
          </p>
        </>
      ),
      en: (
        <>
          <p>
            六合图谱 · Atlas is a <strong>statistical-learning demo</strong>, not a prediction service.
            It estimates probability distributions over historical lottery draws across multiple
            dimensions (numbers, zodiac, wuxing, wave) so you can <strong>see the patterns in the data</strong>
            and reason about long-run ROI if you were to bet using those patterns.
          </p>
          <p>
            ⚠️ Real Macau / HK / any lottery draw is <strong>i.i.d. uniform random</strong> —
            the past does <strong>not</strong> influence the future. Every "signal" this tool shows
            is mathematically guaranteed to lose to random picking over the long run.
            See the red DisclaimerBanner at the top and the Expected-Loss card below.
          </p>
        </>
      ),
    },
  },
  {
    id: 'topbar',
    title: { zh: '顶部按钮', en: 'Top bar buttons' },
    body: {
      zh: (
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>🌙 / ☀️ 主题切换</strong>：深色 / 浅色模式，localStorage 记忆。</li>
          <li><strong>中文 / English</strong>：i18n 全文翻译。</li>
          <li><strong>📋 复制号码</strong>：复制当前选中的号码，含模型名 + 时间戳的富文本。</li>
          <li><strong>📄 导出 PDF</strong>：新窗口打开打印版 HTML 报告，用浏览器原生 Ctrl+P → "保存为 PDF"。</li>
          <li><strong>刷新数据</strong>：重新 fetch <code>/data/snapshot.json</code>。不会重跑模型。</li>
          <li><strong>📖 使用指南</strong>：就是你现在看到的这个页面。</li>
        </ul>
      ),
      en: (
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>🌙 / ☀️ Theme</strong>: dark / light toggle, persisted in localStorage.</li>
          <li><strong>中文 / English</strong>: full i18n switch.</li>
          <li><strong>📋 Copy numbers</strong>: copies your current selection as rich text including model name + timestamp.</li>
          <li><strong>📄 Export PDF</strong>: opens a new window with a print-optimized HTML report — use the browser's native Ctrl+P → "Save as PDF".</li>
          <li><strong>Refresh data</strong>: re-fetches <code>/data/snapshot.json</code>. Does NOT re-run the model.</li>
          <li><strong>📖 Guide</strong>: this page you're reading right now.</li>
        </ul>
      ),
    },
  },
  {
    id: 'data-status',
    title: { zh: '① 数据状态条 (DataStatusBar)', en: '① Data status bar' },
    body: {
      zh: (
        <>
          <p>顶部数据条告诉你：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>数据</strong>: 彩票名 / 当前期数 / 总开奖号码数。</li>
            <li><strong>更新时间</strong>: snapshot.json 上次导出的时间。</li>
            <li><strong>模型</strong>: 当前用的 Bayesian L2 (symbol-aggregated)。</li>
            <li><strong>信号强度</strong>: KL 散度，量化模型跟均匀分布的偏离程度：
              <ul className="list-circle pl-5 mt-1">
                <li>&lt; 0.005 = 无信号 (no-signal)</li>
                <li>0.005 – 0.02 = 弱 (weak)</li>
                <li>0.02 – 0.05 = 中 (moderate) — 当前 0.0268</li>
                <li>&gt; 0.05 = 强 (strong)</li>
              </ul>
            </li>
          </ul>
        </>
      ),
      en: (
        <>
          <p>The top data strip tells you:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Data</strong>: lottery name / period count / total draws.</li>
            <li><strong>Updated</strong>: when snapshot.json was last exported.</li>
            <li><strong>Model</strong>: current Bayesian L2 (symbol-aggregated).</li>
            <li><strong>Signal strength</strong>: KL divergence — how far the model deviates from uniform:
              <ul className="list-circle pl-5 mt-1">
                <li>&lt; 0.005 = no-signal</li>
                <li>0.005 – 0.02 = weak</li>
                <li>0.02 – 0.05 = moderate — currently 0.0268</li>
                <li>&gt; 0.05 = strong</li>
              </ul>
            </li>
          </ul>
        </>
      ),
    },
  },
  {
    id: 'countdown',
    title: { zh: '② 倒计时 (CountdownTimer)', en: '② Countdown timer' },
    body: {
      zh: (
        <p>
          实时倒计时到下一期澳门开奖 (21:32 每天) 和下一次 cron 数据刷新。
          ≤ 10 分钟时数字会变红色提醒。
          点 <strong>立即刷新</strong> 立即重新 fetch snapshot.json。
        </p>
      ),
      en: (
        <p>
          Real-time countdown to the next Macau draw (21:32 daily) and the next cron refresh.
          Numbers turn red when ≤ 10 min to draw.
          Click <strong>立即刷新 / Refresh now</strong> to refetch snapshot.json immediately.
        </p>
      ),
    },
  },
  {
    id: 'selection',
    title: { zh: '③ 选号控制 (Controls) + 49 球网格 + 覆盖率', en: '③ Selection controls + Ball grid + Coverage' },
    body: {
      zh: (
        <>
          <p><strong>左栏 Controls</strong>：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Top-N</strong>：用模型概率排序，取前 N 个球。</li>
            <li><strong>Cover-N</strong>：反向，取模型认为最不该选的 N 个。</li>
            <li>滑块 1-45 (留 4 个"未选")。</li>
            <li><strong>应用推荐</strong>：把当前模式的 Top-N/Cover-N 一次性填入选中。</li>
            <li><strong>重置</strong>：清空选中。</li>
          </ul>
          <p className="mt-2"><strong>中间 49 球网格 (BallGrid)</strong>：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>背景色 = 五行 (金木水火土)，文字色 = 波色 (红蓝绿)。</li>
            <li>圆点 ● 表示推荐 (Top-N 或 Cover-N 取决于模式)。</li>
            <li>点击球切换"已选"。</li>
          </ul>
          <p className="mt-2"><strong>覆盖率 (CoverageAnalyzer)</strong>：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>按生肖 / 五行 / 波色三个维度看你选中的球分布是否"均匀"。</li>
            <li>选中越多球覆盖率越高。</li>
          </ul>
        </>
      ),
      en: (
        <>
          <p><strong>Left column Controls</strong>:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Top-N</strong>: take top N balls by model probability.</li>
            <li><strong>Cover-N</strong>: invert — take the N balls the model considers least likely.</li>
            <li>Slider 1–45 (leaves 4 "not picked").</li>
            <li><strong>Apply recommendation</strong>: fill your selection with the current mode's output.</li>
            <li><strong>Reset</strong>: clear selection.</li>
          </ul>
          <p className="mt-2"><strong>Middle 49-ball grid (BallGrid)</strong>:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Background color = wuxing (金木水火土), text color = wave (红蓝绿).</li>
            <li>● dot = recommended under current mode (Top-N or Cover-N).</li>
            <li>Click a ball to toggle "selected".</li>
          </ul>
          <p className="mt-2"><strong>Coverage analyzer</strong>:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Per-dimension (zodiac / wuxing / wave) coverage of your selection.</li>
            <li>More balls picked → higher coverage.</li>
          </ul>
        </>
      ),
    },
  },
  {
    id: 'autopick',
    title: { zh: '④ 自动选号 (AutoPick)', en: '④ Auto-pick' },
    body: {
      zh: (
        <>
          <p>4 种信号融合方式：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>融合 (combine)</strong>：60% 模型 + 40% 频率，归一化后取前 N (默认)。</li>
            <li><strong>交集 (intersection)</strong>：同时在模型 Top-N 和频率 Top-N 的球 — 两边都认可。</li>
            <li><strong>模型 (model)</strong>：纯 Bayesian L2 Top-N。</li>
            <li><strong>频率 (frequency)</strong>：纯历史 raw count Top-N。</li>
          </ul>
          <p className="mt-2">
            ⚠️ 当前数据 <strong>20 期 / 140 球</strong>，每球被抽 2-3 次。
            四个模式选出来的 Top-20 <strong>高度重叠</strong>，差异在统计噪声内。
            想数字不一样 → 调小 N / 切 Cover-N / 等 50+ 期。
          </p>
        </>
      ),
      en: (
        <>
          <p>4 signal-fusion modes:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Combine</strong>: 60% model + 40% frequency, normalized, top N (default).</li>
            <li><strong>Intersection</strong>: balls in BOTH model Top-N and frequency Top-N.</li>
            <li><strong>Model</strong>: pure Bayesian L2 Top-N.</li>
            <li><strong>Frequency</strong>: pure raw-count ranking.</li>
          </ul>
          <p className="mt-2">
            ⚠️ Current data: <strong>20 periods / 140 draws</strong> ≈ 2.8 draws per ball.
            All four modes' Top-20 outputs <strong>heavily overlap</strong> — the differences are within statistical noise.
            To get different numbers: shrink N / switch to Cover-N / wait until 50+ periods.
          </p>
        </>
      ),
    },
  },
  {
    id: 'win-prob',
    title: { zh: '⑤ 赢的概率 (WinProbabilityCard)', en: '⑤ Win probability' },
    body: {
      zh: (
        <>
          <p>两条不同口径的概率公式 (都是均匀 i.i.d. 假设)：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>至少中 1 球</strong>: <code>1 − C(42,7) / C(49,7) ≈ 98.18%</code>。选 20 个号时几乎必中普通 6+1 球，但<strong>不等于赚钱</strong>。</li>
            <li><strong>中特码 (第 7 球)</strong>: <code>N / 49</code>。选 20 个时 40.82%。</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            ⚠️ 真实单注单期中奖概率 ≤ 1/49 = 2.04%，与 N 无关 — 选越多反而稀释。
            卡片底部的红字就是这个铁律。
          </p>
        </>
      ),
      en: (
        <>
          <p>Two probability formulas (both uniform-i.i.d. assumption):</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>At least 1 hit</strong>: <code>1 − C(42,7) / C(49,7) ≈ 98.18%</code>. With 20 picks you almost always hit a regular 6+1 ball — but <strong>that doesn't mean you make money</strong>.</li>
            <li><strong>Hit special (7th ball)</strong>: <code>N / 49</code>. 40.82% with 20 picks.</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            ⚠️ Real per-ticket per-draw win rate ≤ 1/49 = 2.04%, independent of N — picking more <em>dilutes</em> your per-ticket odds.
            The red text at the bottom of the card is exactly this iron rule.
          </p>
        </>
      ),
    },
  },
  {
    id: 'expected-loss',
    title: { zh: '⑥ 期望亏损模拟器 (ExpectedLossCard)', en: '⑥ Expected-loss simulator' },
    body: {
      zh: (
        <>
          <p>默认输入: 派彩 45×, 每年 156 期, 10 年。</p>
          <pre className="bg-bg-base border border-line-default rounded p-3 text-xs num">
{`总投注    = 期数 × 年数 × 1 (每期 1 元)
期望回报  = 总投注 × 派彩 × (7/49)
期望盈亏  = 期望回报 − 总投注
ROI       = 期望盈亏 / 总投注`}
          </pre>
          <p className="mt-2">
            ⚠️ <strong>关键认知</strong>:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>派彩 ≥ 49/7 ≈ 7× 时，<strong>纯随机选号就已经正期望</strong>。</li>
            <li>派彩 45× &lt; 7× — 长期<strong>数学上负期望</strong>。</li>
            <li>你看到的默认 ROI +1736.7% 是因为派彩假设 45 — 真实私彩几乎不可能达到。</li>
            <li><strong>结论写在卡片底下</strong>: "真实私彩几乎不可能达到派彩 45"。</li>
          </ul>
          <p className="mt-2">
            这块组件是<strong>反讽设计</strong> — 让"看起来很赚"的数字自带 disclaimer。
          </p>
        </>
      ),
      en: (
        <>
          <p>Defaults: payout 45×, 156 draws/year, 10 years.</p>
          <pre className="bg-bg-base border border-line-default rounded p-3 text-xs num">
{`Total bet     = draws × years × 1
Expected ret  = Total bet × payout × (7/49)
Expected PnL  = Expected ret − Total bet
ROI           = Expected PnL / Total bet`}
          </pre>
          <p className="mt-2">
            ⚠️ <strong>Key insights</strong>:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Payout ≥ 49/7 ≈ 7× → even pure random picks have <strong>positive expected value</strong>.</li>
            <li>Payout 45× &lt; 7× → long-run <strong>negative expected value</strong> regardless of strategy.</li>
            <li>The default ROI +1736.7% assumes a payout of 45 — real private books rarely offer that.</li>
            <li><strong>Card bottom explicitly says</strong> "真实私彩几乎不可能达到派彩 45".</li>
          </ul>
          <p className="mt-2">
            This component is <strong>intentionally ironic</strong> — the "looks profitable" numbers come with a built-in disclaimer.
          </p>
        </>
      ),
    },
  },
  {
    id: 'strategy',
    title: { zh: '⑦ 策略对比 + 滚动回测', en: '⑦ Strategy comparison + Rolling backtest' },
    body: {
      zh: (
        <>
          <p><strong>StrategyComparison</strong>: 把 Top-N / Cover-N / 随机基线三种策略在历史数据上"模拟选号"，比较命中率。</p>
          <p className="mt-2">
            <strong>RollingWindowBacktest</strong>: 在最近 30 / 90 / 全期三个时间窗口上分别跑回测，
            让你看到<strong>短窗口运气 vs 长期回归</strong>。
          </p>
          <p className="mt-2">
            当前 20 期数据下，所有策略命中率都在 ±2× random 范围内波动 — 没有任何模型显著优于随机。
            这是<strong>预期行为</strong>，不是 bug。
          </p>
        </>
      ),
      en: (
        <>
          <p><strong>StrategyComparison</strong>: simulate three strategies on historical data — Top-N, Cover-N, and a random baseline — and compare hit rates.</p>
          <p className="mt-2">
            <strong>RollingWindowBacktest</strong>: runs the same backtest on 3 windows — last 30, last 90, full history —
            so you can see <strong>short-window luck vs long-run mean-reversion</strong>.
          </p>
          <p className="mt-2">
            At 20 periods, all strategies oscillate within ±2× of random — no model significantly beats random.
            This is <strong>expected</strong>, not a bug.
          </p>
        </>
      ),
    },
  },
  {
    id: 'stats',
    title: { zh: '⑧ 统计深度 (频率条 + 符号维度热力图 + 均匀性检验)', en: '⑧ Statistical depth (frequency + heatmap + uniformity)' },
    body: {
      zh: (
        <>
          <p><strong>NumberFrequencySparkline</strong>：每个球的历史出现频率条 + 均匀期望线。可以一眼看出哪些球"热"哪些"冷"。</p>
          <p className="mt-2">
            <strong>SymbolDimensionHeatmap</strong>：每个 period × 生肖/五行/波色的热力图，模式随时间的演化。
          </p>
          <p className="mt-2">
            <strong>UniformityCheck</strong>：卡方检验 (df = n_categories - 1)，
            p-value &lt; 0.05 才拒绝"均匀"假设。当前 20 期 p ≈ 0.99 — 完全没法拒绝均匀。
          </p>
          <p className="mt-2">
            <strong>SymbolDimensionBreakdown</strong>：比较 3 个符号维度 (生肖/五行/波色) vs 49 球随机基线，
            哪个维度提供最强信号 (lift%)。当前都是 ±5% 噪声内。
          </p>
        </>
      ),
      en: (
        <>
          <p><strong>NumberFrequencySparkline</strong>: per-ball historical frequency bars + uniform expectation line. At-a-glance view of "hot" vs "cold" balls.</p>
          <p className="mt-2">
            <strong>SymbolDimensionHeatmap</strong>: period × zodiac/wuxing/wave heatmap showing pattern evolution over time.
          </p>
          <p className="mt-2">
            <strong>UniformityCheck</strong>: chi-square goodness-of-fit test (df = n_categories − 1).
            Only p &lt; 0.05 lets you reject "uniform". Current p ≈ 0.99 — uniform cannot be rejected.
          </p>
          <p className="mt-2">
            <strong>SymbolDimensionBreakdown</strong>: compares 3 symbol dimensions (zodiac / wuxing / wave) vs the 49-ball random baseline, showing which dimension provides the strongest signal (lift %). All currently within ±5% noise.
          </p>
        </>
      ),
    },
  },
  {
    id: 'disclaimer',
    title: { zh: '⑨ 最重要的一块: 顶部 Disclaimer', en: '⑨ The most important piece: top disclaimer' },
    body: {
      zh: (
        <>
          <p>
            页面顶部那条<strong>红色 DisclaimerBanner</strong>不是装饰。它写明：
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>本工具是"统计学习项目"，不是"预测服务"。</li>
            <li>真实开奖是 i.i.d. 均匀随机 — 长期期望 ROI 必为负。</li>
            <li>不提供也不支持任何真实下注。</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            不要拿真钱试。
            如果你想理解自己的赌博行为模式，建议用 (b) budget tracker 之类工具监控实际花费，
            而不是用本工具追踪下注结果 — 那会让"亏的钱可视化"，强化赌徒谬误。
          </p>
        </>
      ),
      en: (
        <>
          <p>
            The <strong>red DisclaimerBanner</strong> at the very top of the page is NOT decorative. It states:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>This is a "statistical-learning project", not a "prediction service".</li>
            <li>Real draws are i.i.d. uniform random — long-run expected ROI is negative.</li>
            <li>No real betting is supported or endorsed.</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            Do not gamble with real money.
            If you want to understand your gambling behavior, use a budget-tracker to monitor actual spend —
            not this tool's tracking features. That would just make losses visible, reinforcing gambler's fallacy.
          </p>
        </>
      ),
    },
  },
];

export function UserGuide({ onClose }: { onClose: () => void }) {
  const { t, locale } = useLocale();
  const [openId, setOpenId] = useState<string | null>('overview');
  const isZh = locale === 'zh-CN';

  return (
    <div className="min-h-screen bg-bg-base">
      <header className="border-b border-line-subtle">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-ink-primary">
              {isZh ? '使用指南 · User Guide' : 'User Guide · 使用指南'}
            </h1>
            <p className="text-xs text-ink-muted mt-0.5">
              {isZh
                ? '每个区域的功能与算法 · 读一遍再开始'
                : 'What every section does + the math behind it · read before using'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <button
              type="button"
              onClick={onClose}
              className="
                px-3 py-1.5 rounded text-xs font-medium
                bg-emerald-500/15 border border-emerald-500/40 text-emerald-200
                hover:bg-emerald-500/25 transition
              "
            >
              {isZh ? '← 返回主界面' : '← Back to app'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-3">
        <div className="panel p-4 bg-amber-500/5 border-amber-500/20 text-sm text-amber-200">
          <strong>{isZh ? '先读' : 'Read first'}:</strong>{' '}
          {isZh
            ? '本指南按页面从上到下的顺序解释。跳到任意一节:'
            : 'This guide follows the page top-to-bottom. Jump to any section:'}
        </div>

        <nav className="flex flex-wrap gap-1.5 text-xs">
          {SECTIONS.map(s => (
            <button
              key={s.id}
              type="button"
              onClick={() => setOpenId(s.id)}
              className={`
                px-2.5 py-1 rounded border transition
                ${openId === s.id
                  ? 'bg-emerald-500/20 border-emerald-500/60 text-emerald-200'
                  : 'bg-bg-raised border-line-default text-ink-secondary hover:border-line-strong'
                }
              `}
            >
              {isZh ? s.title.zh : s.title.en}
            </button>
          ))}
        </nav>

        <div className="space-y-2">
          {SECTIONS.map(s => {
            const isOpen = openId === s.id;
            return (
              <section key={s.id} className="panel">
                <button
                  type="button"
                  onClick={() => setOpenId(isOpen ? null : s.id)}
                  className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left"
                >
                  <h2 className="text-sm font-semibold text-ink-primary">
                    {isZh ? s.title.zh : s.title.en}
                  </h2>
                  <span className="text-ink-muted text-xs">{isOpen ? '−' : '+'}</span>
                </button>
                {isOpen && (
                  <div className="px-4 pb-4 text-sm text-ink-secondary space-y-2 leading-relaxed">
                    {isZh ? s.body.zh : s.body.en}
                  </div>
                )}
              </section>
            );
          })}
        </div>

        <div className="panel p-4 bg-bg-raised">
          <h3 className="label mb-2">
            {isZh ? '调试速查 (代码路径)' : 'Debug cheatsheet (code paths)'}
          </h3>
          <ul className="text-xs font-mono text-ink-secondary space-y-1">
            <li>• Bayesian L2 predictor → <code>src/lib/predictor.ts:81</code></li>
            <li>• AutoPick 4 modes → <code>src/components/AutoPick.tsx</code></li>
            <li>• Ball frequency stats → <code>src/lib/statistics.ts:20</code></li>
            <li>• Chi-square test → <code>src/lib/statistics.ts:63</code></li>
            <li>• Expected loss math → <code>src/components/ExpectedLossCard.tsx</code></li>
            <li>• Cron pipeline log → <code>~/dev/liuhe/atlas/logs/cron-pipeline.log</code></li>
            <li>• Project history → <code>~/dev/liuhe/atlas/logs/M*.md</code></li>
            <li>• Backend DB export → <code>~/dev/liuhe/atlas/export_snapshot.py</code></li>
          </ul>
        </div>

        <div className="text-center text-[10px] text-ink-dim py-6">
          {t('footer.disclaimer')}
        </div>
      </main>
    </div>
  );
}
