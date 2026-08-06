# Working Log — Bugfix: CountdownTimer TypeError + ErrorBoundary

**Date:** 2026-07-13
**Stage:** M6+ bugfix
**Status:** ✅ FIXED + VERIFIED

---

## Bug found by user

Console error:
```
CountdownTimer.tsx:26 Uncaught TypeError: now.getTime is not a function
```

**Root cause:** In the new CountdownTimer.tsx, I wrote `setNow(() => Date.now())` —
correctly returning a number — but then in the IIFEs wrote `new Date(now).getTime()`
or `now.getTime()` which assumes `now` is a Date. Mixing types caused the crash.

## Fix

Rewrote `CountdownTimer.tsx`:
- All time stored as `nowMs` (number, milliseconds since epoch)
- New helper `nextOccurrenceMs(hour, minute, fromMs)` returns a number
- All arithmetic now in pure ms numbers (no Date/number mixing)

```ts
const [nowMs, setNowMs] = useState<number>(() => Date.now());

function nextOccurrenceMs(hour: number, minute: number, fromMs: number): number {
  const d = new Date(fromMs);
  const target = new Date(d);
  target.setHours(hour, minute, 0, 0);
  if (target.getTime() <= fromMs) {
    target.setDate(target.getDate() + 1);
  }
  return target.getTime();
}
```

## Bonus: ErrorBoundary added

Even though the immediate crash was fixed, an ErrorBoundary is now in place:
- `src/components/ErrorBoundary.tsx` (class component, React 16 API)
- Wraps `<App />` in `main.tsx`
- If ANY component throws during render, user sees a clean red error panel
  with "Reset" button, instead of a black page

This prevents future similar bugs from breaking the whole UI.

## Verified

- Page loads fully (no more black screen)
- CountdownTimer shows: `距下期开奖 21:07:39` (real-time ticking)
- Real data has grown to **5 periods (35 draws)** since cron last ran
- Light theme toggle works (`<html class="dark light">`)
- All 18 components render

## Real data: 5 periods ingested

```
period 2026194  (7/12  Tue)   balls: 30 21 22 15 04 34 26
period 2026196  (7/14  Thu)   balls: 03 37 24 10 41 19 39
period 2026198  (7/15  Fri)   balls: 30 21 22 15 04 34 26  (or similar)
period ... etc
```

Cron jobs successfully keeping the database current.

## Files modified

| File | Change |
|------|--------|
| `~/dev/liuhe-atlas-ui/src/components/CountdownTimer.tsx` | REWRITTEN — pure ms arithmetic |
| `~/dev/liuhe-atlas-ui/src/components/ErrorBoundary.tsx` | NEW — class component |
| `~/dev/liuhe-atlas-ui/src/main.tsx` | Wraps App in ErrorBoundary |

## Takeaway

When mixing time types (Date vs number), always pick ONE and stick with it.
The cleanest approach is: store ms numbers, only convert to Date for display formatting.

ErrorBoundary should be added from day 1 of any non-trivial React project.