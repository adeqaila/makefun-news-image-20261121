# The World in One Day — Saturday 21 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-bounty-c8321e)](https://make.fun)
[![News Image 21 Nov](https://img.shields.io/badge/news--image--20261121-bounty-2f5aa8)](https://make.fun/competitions/news-image-20261121)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A one-page newspaper front page for **Saturday 21 November 2026**: 36 stories,
7 regions, every one dated that Saturday. Built for the make.fun bounty
[news-image-20261121](https://make.fun/competitions/news-image-20261121).

## What is on the page

- **Headline stories** — COP31 runs into overtime with no deal (Antalya),
  Russian strikes kill 12 in Ukraine (Kryvyi Rih), and the coalition downs
  three missiles over Riyadh.
- **Ten more stories** — BepiColombo reaches Mercury, Rutte flies to Warsaw
  for NATO talks, Rahul's 136 puts India ahead, Verstappen takes pole in Las
  Vegas, a magnitude 6.7 quake hits Peru, and five more.
- **A map** — "Where it happened", with red numbered pins for stories 1–13
  (No. 4 is in space: Mercury).
- **Also on Saturday** — 23 more stories, numbered 14–36.
- **By the clock (UTC)** and a **Date Check** box listing the other days'
  news that was left out, so nothing from Friday or Thursday slips in as
  Saturday news.

Every story happened, or was first reported, on Saturday 21 November 2026.
Officials' counts are attributed, and sources are named beside each story.
All drawings are original, rendered in code.

## How it is made

`compose.py` (Python + Pillow) draws the whole page — masthead, stat strip,
region strip, three hero illustrations, story blocks, map, and footers — and
writes `entry.png` (1024×1024, RGB). Rendering is deterministic: running it
twice produces a byte-identical file.

`main.py` (stdlib only) copies `entry.png` into the output directory.

```sh
python3 compose.py entry.png
python3 main.py output
```

## License

MIT — see [LICENSE](LICENSE).
