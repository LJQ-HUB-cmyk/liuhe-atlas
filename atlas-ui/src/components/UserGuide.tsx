import { useState } from 'react';
import { useLocale } from '../lib/i18n';
import { ThemeSwitcher } from './ThemeSwitcher';
import { LanguageSwitcher } from './LanguageSwitcher';

/**
 * User Guide — plain-language, metaphor-heavy explanations.
 * Toggled by the 📖 button in the header.
 * No jargon. No formulas unless they're the one that matters.
 */

interface Section {
  id: string;
  title: { zh: string; en: string };
  body: { zh: React.ReactNode; en: React.ReactNode };
}

const SECTIONS: Section[] = [
  {
    id: 'overview',
    title: { zh: '这是个啥', en: 'What is this' },
    body: {
      zh: (
        <>
          <p>
            一句话：这是一台<strong>"彩票考古机"</strong>。
            它把过去开过的号码都翻出来，数一数谁出现得多、谁出现得少，然后画成图给你看。
          </p>
          <p>
            但记住一件事：开奖是<strong>摇奖机摇出来的，机器没有记性</strong>。
            就像抛硬币——就算连抛了 10 次正面，第 11 次还是五五开。
            所以这个工具只能让你"看看过去"，<strong>不能</strong>告诉你"下次开什么"。
          </p>
        </>
      ),
      en: (
        <>
          <p>
            In one line: this is a <strong>"lottery archaeology machine"</strong>.
            It digs up all past drawn numbers, counts how often each appears, and draws charts for you.
          </p>
          <p>
            But remember: draws come from a <strong>machine with no memory</strong>.
            Like a coin — even after 10 heads in a row, the 11th toss is still 50/50.
            So this tool only lets you "look at the past". It <strong>cannot</strong> tell you what comes next.
          </p>
        </>
      ),
    },
  },
  {
    id: 'topbar',
    title: { zh: '顶上一排按钮', en: 'Top bar buttons' },
    body: {
      zh: (
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>🌙 / ☀️</strong> 换皮肤（深色 / 浅色），纯好看。</li>
          <li><strong>中文 / English</strong> 换语言。</li>
          <li><strong>📋 复制号码</strong> 把你选中的号码复制走（带点说明文字）。</li>
          <li><strong>📄 导出 PDF</strong> 把当前分析打印成一张报告（新窗口 → Ctrl+P 保存成 PDF）。</li>
          <li><strong>刷新数据</strong> 重新读一次数据文件（数据每天自动更新，一般不用点）。</li>
          <li><strong>📖 使用指南</strong> 就是你现在看的这个。</li>
        </ul>
      ),
      en: (
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>🌙 / ☀️</strong> Change theme (dark/light). Just looks.</li>
          <li><strong>中文 / English</strong> Change language.</li>
          <li><strong>📋 Copy numbers</strong> Copy your selected numbers (with a header).</li>
          <li><strong>📄 Export PDF</strong> Print the analysis as a report (new window → Ctrl+P → Save as PDF).</li>
          <li><strong>Refresh data</strong> Re-read the data file. Usually not needed — it auto-updates daily.</li>
          <li><strong>📖 Guide</strong> The page you're reading right now.</li>
        </ul>
      ),
    },
  },
  {
    id: 'data-status',
    title: { zh: '① 仪表盘（数据状态条）', en: '① The dashboard (data status bar)' },
    body: {
      zh: (
        <>
          <p>就像车的仪表盘，告诉你车况：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>数据：21 期 · 147 个号码</strong> = 我们手里攒了多少历史记录。越多越好。</li>
            <li><strong>更新时间</strong> = 数据文件最后刷新时间。</li>
            <li><strong>模型：Bayesian L2</strong> = 用的什么算法。你不用懂，就当是"计算方式 A"。</li>
            <li>
              <strong>信号强度：中（KL=0.026）</strong> = 这堆数据里有没有"味道"。
              像闻一杯茶：数值越低越像白开水（完全随机），越高越像浓茶（有规律）。
              现在 0.026 是"有点味，但淡得很"——跟瞎猜差别不大。
            </li>
          </ul>
        </>
      ),
      en: (
        <>
          <p>Like a car dashboard — tells you how things are:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Data: 21 periods · 147 draws</strong> = how much history we have. More is better.</li>
            <li><strong>Updated</strong> = when the data file was last refreshed.</li>
            <li><strong>Model: Bayesian L2</strong> = which algorithm is used. Don't worry about it.</li>
            <li>
              <strong>Signal: moderate (KL=0.026)</strong> = whether this data has any "flavor".
              Like smelling tea: lower is closer to plain water (pure random), higher is strong tea (a real pattern).
              0.026 is "a hint of flavor" — barely better than guessing.
            </li>
          </ul>
        </>
      ),
    },
  },
  {
    id: 'countdown',
    title: { zh: '② 倒计时（下课铃）', en: '② Countdown (the school bell)' },
    body: {
      zh: (
        <p>
          就是"距离下次开奖还有多久"的下课铃。左边是开奖倒计时，右边是数据刷新倒计时。
          快开奖了数字会变红提醒你。想看最新数据就点"立即刷新"。
        </p>
      ),
      en: (
        <p>
          It's just the school bell for the next draw. Left: time until the next draw.
          Right: time until the next data refresh. Numbers turn red when a draw is close.
          Click "refresh now" to pull the newest data.
        </p>
      ),
    },
  },
  {
    id: 'selection',
    title: { zh: '③ 选号（点菜模式）', en: '③ Picking numbers (ordering food)' },
    body: {
      zh: (
        <>
          <p><strong>左边"选择模式"</strong>，就像你点菜：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Top-N</strong> = 点最热门的 N 道菜（算法觉得最可能出现的号码）。</li>
            <li><strong>Cover-N</strong> = 反过来，专点最冷门的 N 道。</li>
            <li>滑块 = 你要点几道（1 到 45）。</li>
            <li><strong>应用推荐</strong> = 一键把推荐菜全点上。<strong>重置</strong> = 清空重来。</li>
          </ul>
          <p className="mt-2"><strong>中间 49 个格子 = 菜单</strong>。每格一道"菜"（一个号码）。</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>格子底色 = 口味（金木水火土），字色 = 辣度（红蓝绿）。纯分类用的。</li>
            <li>带 ● 的 = 被推荐；点一下就"下单"（选中）。</li>
          </ul>
          <p className="mt-2"><strong>覆盖率</strong> = 你点的菜荤素搭不搭。它按生肖/五行/波色检查你有没有"偏食"。</p>
        </>
      ),
      en: (
        <>
          <p><strong>Left "mode" panel</strong> — like ordering food:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Top-N</strong> = order the N most popular dishes (numbers the model thinks most likely).</li>
            <li><strong>Cover-N</strong> = the opposite — order the N least popular.</li>
            <li>Slider = how many dishes (1–45).</li>
            <li><strong>Apply</strong> = order all recommended at once. <strong>Reset</strong> = start over.</li>
          </ul>
          <p className="mt-2"><strong>The 49-ball grid in the middle = the menu.</strong> Each cell is one dish.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Cell background = flavor (五行), text color = spice level (红蓝绿). Just classification.</li>
            <li>● dot = recommended; click to "order" (select).</li>
          </ul>
          <p className="mt-2"><strong>Coverage</strong> = whether your order is balanced. Checks zodiac/wuxing/wave so you're not "picky eating".</p>
        </>
      ),
    },
  },
  {
    id: 'autopick',
    title: { zh: '④ 智能点菜（自动选号）', en: '④ Auto-order (auto-pick)' },
    body: {
      zh: (
        <>
          <p>帮你自动点一桌菜，有 4 种点法：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>融合</strong> = 人气 + 口味综合打分（60% 看算法 + 40% 看历史次数）。</li>
            <li><strong>交集</strong> = 两本榜单都上榜的菜，两边都认可的。</li>
            <li><strong>模型</strong> = 只信算法，别的不管。</li>
            <li><strong>频率</strong> = 只信"过去谁出现最多"。</li>
          </ul>
          <p className="mt-2">
            <strong>为什么 4 种点出来数字都差不多？</strong> 因为数据太少！
            才 21 期，每颗球平均只出现过 3 次——就像全班刚上几天课，每个人的发言次数都差不多，
            根本排不出明显差别。想让数字不一样：把 N 调小，或者等数据攒到 50 期以上。
          </p>
        </>
      ),
      en: (
        <>
          <p>Auto-orders a table of food, 4 styles:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Combine</strong> = popularity + flavor combined (60% model + 40% history).</li>
            <li><strong>Intersection</strong> = dishes on BOTH ranking lists — both sides approve.</li>
            <li><strong>Model</strong> = trust the algorithm only.</li>
            <li><strong>Frequency</strong> = trust "who appeared most in the past" only.</li>
          </ul>
          <p className="mt-2">
            <strong>Why do all 4 give similar numbers?</strong> Not enough data!
            Only 21 periods — each ball has appeared ~3 times on average.
            It's like a class that just started: everyone has spoken about the same number of times,
            so there's no real ranking. To get different numbers: shrink N, or wait for 50+ periods.
          </p>
        </>
      ),
    },
  },
  {
    id: 'win-prob',
    title: { zh: '⑤ 中奖率（赢的概率）', en: '⑤ Win probability' },
    body: {
      zh: (
        <>
          <p>两个数字，两种算法：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>至少中 1 球：98%</strong> — 选 20 个号码，大概率能碰到开奖号里的一个。
              但"碰到"不等于"赢钱"。就像考试 100 道题你蒙对 1 道——概率很高，可那是蒙的。</li>
            <li><strong>中特码：40.8%</strong> — 第 7 个特殊号码的命中率。</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            ⚠️ 铁律：单张彩票中头奖的概率 = <strong>1/49 ≈ 2%</strong>，跟你选几个号没关系！
            选得越多，每张票的概率反而越被稀释。这张卡底下的红字就是这句话。
          </p>
        </>
      ),
      en: (
        <>
          <p>Two numbers, two formulas:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>At least 1 hit: 98%</strong> — pick 20 numbers and you'll probably match one drawn ball.
              But "matching" ≠ "winning money". Like a 100-question test where you guess 1 right — high chance, but it's a guess.</li>
            <li><strong>Hit special: 40.8%</strong> — chance of matching the 7th special ball.</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            ⚠️ Iron rule: the chance of winning the jackpot on one ticket is <strong>1/49 ≈ 2%</strong>,
            no matter how many numbers you pick! Picking more actually dilutes per-ticket odds.
            That's the red text at the bottom of the card.
          </p>
        </>
      ),
    },
  },
  {
    id: 'expected-loss',
    title: { zh: '⑥ 亏钱计算器（期望亏损）', en: '⑥ The loss calculator (expected loss)' },
    body: {
      zh: (
        <>
          <p><strong>这个最重要，先看这个。</strong>它算的是：长期买，你会亏多少。</p>
          <p>逻辑很简单——开奖时 49 颗球里抽 7 颗，所以中奖概率约 1/7。彩票给多少倍回本才不亏？</p>
          <p className="mt-1 font-medium">答案是 7 倍。派彩低于 7 倍，长期必亏，数学铁律。</p>
          <p className="mt-2">
            那为什么默认输入 45 倍时显示"赚 1736%"？因为 45 倍是<strong>理想世界</strong>——
            现实中没有任何彩票给 45 倍。就像"如果老虎机吐 45 倍你就能赢"，但老虎机是庄家设计的。
          </p>
          <p className="mt-2 text-red-400 font-medium">
            真实世界的彩票，这个计算器算出来是<strong>负数</strong>。
            你看到"赚"字，只是因为输入了一个现实中不存在的数字。
          </p>
        </>
      ),
      en: (
        <>
          <p><strong>Most important — read this first.</strong> It calculates: over the long run, how much you lose.</p>
          <p>The logic is simple — 7 balls are drawn from 49, so your win rate is ~1/7. What payout do you need to break even?</p>
          <p className="mt-1 font-medium">Answer: 7×. Below 7×, you lose long-term. Math, not opinion.</p>
          <p className="mt-2">
            So why does the default (45×) show "+1736%" profit? Because 45× is <strong>fantasy land</strong> —
            no real lottery pays 45×. Like "you'd win if the slot machine paid 45×" — but slots are designed by the house.
          </p>
          <p className="mt-2 text-red-400 font-medium">
            With a real lottery payout, this calculator shows a <strong>negative</strong> number.
            If you see "profit", it's only because someone typed in a number that doesn't exist in reality.
          </p>
        </>
      ),
    },
  },
  {
    id: 'strategy',
    title: { zh: '⑦ 考后对答案（回测）', en: '⑦ Grading your past answers (backtest)' },
    body: {
      zh: (
        <>
          <p>
            <strong>策略对比</strong> = 拿过去的开奖记录，假装"我当时用的是这个策略"，看能对几题。
            就像考完试对答案——考得好不好，得等对完才知道。
          </p>
          <p className="mt-2">
            <strong>滚动回测</strong> = 分三段对答案：最近 30 天、最近 90 天、全部历史。
            看看某个策略是"最近运气好"还是"一直都不错"。
          </p>
          <p className="mt-2">
            现在数据才 21 期，所有策略的命中率都在随机上下波动——没有一个明显跑赢"闭眼瞎选"。
            <strong>这是正常的</strong>，不是 bug。数据越多，回测越有意义。
          </p>
        </>
      ),
      en: (
        <>
          <p>
            <strong>Strategy comparison</strong> = take past draws, pretend "I used this strategy back then",
            and see how many you'd get right. Like checking answers after an exam — you only know how you did after grading.
          </p>
          <p className="mt-2">
            <strong>Rolling backtest</strong> = grade in three chunks: last 30 days, last 90 days, all history.
            See whether a strategy was "recently lucky" or "consistently okay".
          </p>
          <p className="mt-2">
            With only 21 periods, every strategy's hit rate bounces around random — none clearly beats "picking blind".
            <strong>That's normal</strong>, not a bug. More data → more meaningful backtest.
          </p>
        </>
      ),
    },
  },
  {
    id: 'stats',
    title: { zh: '⑧ 显微镜（统计深度）', en: '⑧ The microscope (statistical depth)' },
    body: {
      zh: (
        <>
          <p>这几个小图是给爱研究数据的人看的显微镜：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>频率条</strong> = 每个号码出现次数的排行榜，一眼看到谁"热"谁"冷"。</li>
            <li><strong>热力图</strong> = 每一期的生肖/五行/波色分布，像温度表看变化。</li>
            <li><strong>均匀性检验</strong> = "查作弊"的。如果开奖完全随机，数字应该很均匀；
              它算出来 p=0.99，意思是"完全看不出有鬼"，一切正常。</li>
            <li><strong>符号维度</strong> = 生肖/五行/波色里有没有"人气王"。</li>
          </ul>
        </>
      ),
      en: (
        <>
          <p>These small charts are a microscope for data nerds:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Frequency bars</strong> = ranking of how often each number appears. See "hot" vs "cold" at a glance.</li>
            <li><strong>Heatmap</strong> = per-period zodiac/wuxing/wave distribution, like a temperature chart.</li>
            <li><strong>Uniformity check</strong> = "cheating detector". If draws were truly random, numbers should be uniform;
              it computes p=0.99, meaning "no sign of anything fishy" — all normal.</li>
            <li><strong>Symbol breakdown</strong> = any "popular kid" among zodiac/wuxing/wave.</li>
          </ul>
        </>
      ),
    },
  },
  {
    id: 'disclaimer',
    title: { zh: '⑨ 最重要：别拿真钱玩', en: '⑨ Most important: don\'t use real money' },
    body: {
      zh: (
        <>
          <p>顶部那条红字不是装饰，是真心话：</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>这是<strong>学习统计的玩具</strong>，不是"赚钱机器"。</li>
            <li>开奖 = 随机，任何你看到的"规律"都只是巧合。</li>
            <li>长期买，期望必亏（不信去第 ⑥ 节按按计算器）。</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            真想拿真钱买？先用第 ⑥ 节的亏钱计算器算算你会亏多少，
            算完大概率就不想买了。这就是它存在的意义。
          </p>
        </>
      ),
      en: (
        <>
          <p>The red banner at the top isn't decoration — it's the truth:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>This is a <strong>toy for learning statistics</strong>, not a money machine.</li>
            <li>Draws are random. Any "pattern" you see is coincidence.</li>
            <li>Long-term, expected value is negative (check section ⑥ and click the calculator).</li>
          </ul>
          <p className="mt-2 text-red-400 font-medium">
            Thinking of using real money? First use the loss calculator in section ⑥ to see how much you'd lose.
            After that, you probably won't want to. That's its whole purpose.
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
              {isZh ? '使用指南（大白话版）' : 'User Guide (plain talk)'}
            </h1>
            <p className="text-xs text-ink-muted mt-0.5">
              {isZh
                ? '不整术语，全是比喻。30 秒看完。'
                : 'No jargon, all metaphors. 30 seconds to read.'}
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
              {isZh ? '← 返回' : '← Back'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-3">
        <div className="panel p-4 bg-amber-500/5 border-amber-500/20 text-sm text-amber-200">
          <strong>{isZh ? '先说结论' : 'TL;DR'}:</strong>{' '}
          {isZh
            ? '这是看历史的工具，不是算命工具。开奖没规律，任何"规律"都是巧合。按第 ⑥ 节能算出你长期亏多少。'
            : 'This is a history viewer, not a fortune teller. Draws have no pattern; any "pattern" is coincidence. Section ⑥ shows your long-run loss.'}
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

        <div className="text-center text-[10px] text-ink-dim py-6">
          {t('footer.disclaimer')}
        </div>
      </main>
    </div>
  );
}
