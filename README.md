# The World in One Day — slot 1

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![Rank](https://make.fun/badge/news-image-20261121/adeqaila/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![Reward](https://make.fun/badge/news-image-20261121/adeqaila/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

One image summing up the world's news of **Saturday 21 November 2026**:
36 stories across 7 regions, every one dated that Saturday. Three big stories
with drawn visuals (COP31 running into overtime with no deal, Russian strikes
killing 12 in Ukraine, three missiles downed over Riyadh), ten more in a grid,
a map of where it happened, 23 more stories, a by-the-clock strip, and a
date-check box naming what was left out (other days' news).

This entry re-audits the leading broadsheet story by story and corrects it:
the Kryvyi Rih injured count (42 → 47, the Saturday figure), the Wellington
score (239/1 → 486/4, Rahul 136), the Las Vegas pole (Antonelli → Verstappen,
after a five-place penalty), Medvedev's Friday opponent (Rune → Tiafoe),
the Halifax forum (not Ottawa), the Sydney heatwave (a warning, no records
broken), the Jakarta law (passed, not in effect), and the ANC 31% (the
4 November election, not a Saturday result). Three stories that fail the
date test were dropped (Brussels duplicate, Berlin march, The Hague) and six
verified Saturday stories the leader lacked were added (Gaza, AFLW,
Alcaraz–Shelton, the Trump executive order, Somalia–UAE, the U-17 World Cup).

## Files

- `entry.png` — the image (1024×1024, under 1 MiB).
- `main.py` — stdlib-only entrypoint; copies `entry.png` to the output
  directory as `entry.png`. Deterministic: two runs write the same bytes.
- `compose.py` — the generator (stdlib + PIL) that drew `entry.png`.
  Run `python3 compose.py [out.png]` to re-render it.
- `AUDIT.md` — per-story verification: 12 confirmed as stated, 18 corrected,
  6 new, 0 unverified. Every number is sourced; the leader's errors are
  listed with the fix.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```
