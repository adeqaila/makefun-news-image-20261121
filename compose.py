#!/usr/bin/env python3
"""Slot 1 — "The World in One Day" — news-image-20261121.

Renders entry.png (1024x1024 broadsheet) from 36 verified 21 Nov 2026 stories.
Stdlib + PIL only, no network, fully deterministic: the same input bytes
produce the same output bytes on every run. Run:  python3 compose.py [out.png]

Layout (the leader broadsheet pattern, redrawn from scratch):
  top line | masthead | subhead | 6-stat strip | 7-region bar |
  3 big stories with procedural visuals | 10 small stories in 5x2 |
  map + 23-more list | by-the-clock | date-check box | footer.
All 36 stories happened, or were first reported, on Saturday 21 Nov 2026.
See AUDIT.md for the per-story verification and the leader errors corrected.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 30, 36)
NAVY = (26, 42, 74)
GRAY = (96, 94, 88)
FAINT = (168, 164, 152)
RULE = (60, 58, 52)
GREEN = (28, 110, 58)
SEA = (206, 224, 234)
LAND = (232, 217, 172)
LAND_LINE = (176, 154, 106)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ISSUES = []


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- data
TOP_LEFT = "THE WORLD IN ONE DAY"
TOP_RIGHT = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
MASTHEAD = "Saturday 21 November 2026"
SUBHEAD = ("COP31 runs into overtime with no deal \u00b7 Russian strikes kill 12 in "
           "Ukraine \u00b7 Coalition downs three missiles over Riyadh")

STATS = [
    ("0", "climate deal agreed\nat COP31"),
    ("3", "missiles downed\nover Riyadh"),
    ("12", "killed in Ukraine\nstrikes in a day"),
    ("47", "injured in the\nKryvyi Rih strike"),
    ("8 yrs", "BepiColombo's voyage\nto Mercury"),
    ("6.7", "Peru quake\nmagnitude"),
]

REGIONS = [
    ("EUROPE", 9, (47, 90, 168)),
    ("ASIA", 6, (176, 30, 36)),
    ("MIDDLE EAST", 5, (138, 109, 59)),
    ("AFRICA", 3, (46, 125, 79)),
    ("AMERICAS", 8, (122, 31, 43)),
    ("OCEANIA", 4, (46, 127, 134)),
    ("SPACE", 1, (107, 107, 107)),
]

# Big stories: number, kicker, headline, body, visual kind, label, chip.
BIG = [
    dict(num=1, kicker="ANTALYA \u00b7 CLIMATE",
         headline="COP31 runs into overtime with no deal",
         body=("Talks suspended to Saturday after a revised draft dropped all "
               "fossil-fuel references and the $120bn-a-year adaptation "
               "target. (AP, Al Jazeera)"),
         visual="cop31", label="COP31: NO DEAL", chip="Overtime \u00b7 AP"),
    dict(num=2, kicker="KRYVYI RIH, UKRAINE \u00b7 WAR",
         headline="Russian strikes kill 12 in Ukraine",
         body=("Overnight barrage kills at least nine; two dead, 47 hurt in "
               "Kryvyi Rih. Kyiv counts 12 dead, 82 hurt in a day. "
               "(Kyiv Independent, BBC)"),
         visual="kryvyi", label="KRYVYI RIH", chip="12 dead in a day"),
    dict(num=3, kicker="RIYADH \u00b7 CONFLICT",
         headline="Coalition downs three missiles over Riyadh",
         body=("Saudi-led forces intercepted three Houthi ballistic missiles "
               "bound for the capital, the second attack in days after the "
               "PIF tower was hit. (Reuters)"),
         visual="riyadh", label="RIYADH: 3 DOWN",
         chip="Second attack \u00b7 Reuters"),
]

# Small stories: number, red label, kicker, headline, body, visual kind, chip.
SMALL = [
    dict(num=4, label="MERCURY: ARRIVED", kicker="MERCURY \u00b7 SPACE",
         headline="BepiColombo reaches Mercury",
         body="Thrusters fired 19:24 CET after an eight-year voyage. (ESA)",
         visual="mercury", chip="19:24 CET \u00b7 ESA"),
    dict(num=5, label="WARSAW: NATO", kicker="WARSAW \u00b7 NATO",
         headline="Rutte flies to Warsaw for NATO talks",
         body="After a missile lands in Poland, allies weigh defences. (AP)",
         visual="warsaw", chip="Saturday \u00b7 AP"),
    dict(num=6, label="RAHUL: 136", kicker="WELLINGTON \u00b7 CRICKET",
         headline="Rahul's 136 puts India ahead",
         body="India 486/4, a lead of 118, on day three at the Basin. (PTI)",
         visual="cricket", chip="Day 3 \u00b7 PTI"),
    dict(num=7, label="VEGAS: POLE", kicker="LAS VEGAS \u00b7 FORMULA 1",
         headline="Antonelli fastest, Verstappen takes pole",
         body="Antonelli fastest but penalised; Verstappen inherits pole. (F1)",
         visual="vegas", chip="Qualifying \u00b7 F1"),
    dict(num=8, label="PERU: 6.7", kicker="JUN\u00cdN, PERU \u00b7 QUAKE",
         headline="Magnitude 6.7 quake hits Peru",
         body="Deep tremor north of Jun\u00edn, felt in Lima; no deaths. (USGS)",
         visual="seismo", chip="00:09 UTC \u00b7 USGS"),
    dict(num=9, label="BAYELSA: 4 DEAD", kicker="BAYELSA, NIGERIA \u00b7 DISASTER",
         headline="Tinubu orders rescue after boat disaster",
         body="Four dead, 24 rescued; Tinubu orders a federal response. (Reuters)",
         visual="boat", chip="Saturday \u00b7 Reuters"),
    dict(num=10, label="UK\u2013EU: DEAL", kicker="LONDON \u00b7 BRUSSELS",
         headline="UK and EU seal a reset deal",
         body="Food trade, youth visas, carbon link; 100,000 a year. (AP)",
         visual="ukeu", chip="Agreed \u00b7 AP"),
    dict(num=11, label="IRAQ: ARMY IN", kicker="CENTRAL IRAQ \u00b7 SECURITY",
         headline="Iraqi forces hold Jurf al-Sakhar",
         body="Army holds the stronghold; Karbala road reopens today. (Reports)",
         visual="iraq", chip="Saturday \u00b7 Reports"),
    dict(num=12, label="ANC: 31%", kicker="SOUTH AFRICA \u00b7 POLITICS",
         headline="ANC scrambles for coalition partners",
         body="Worst result ever, 31%; coalition talks run to 27 Nov. (BBC)",
         visual="ballot", chip="Coalition talks \u00b7 BBC"),
    dict(num=13, label="TURIN: SEMI", kicker="TURIN \u00b7 TENNIS",
         headline="Medvedev meets Zverev tonight",
         body="Semi not before 20:30 CET; Zverev 3\u20130 in the group. (ATP)",
         visual="tennis", chip="20:30 CET \u00b7 ATP"),
]

# 23 more stories: (number, one line, source already inside).
ALSO = [
    (14, "Takaichi back home after frosty APEC welcome (AP)"),
    (15, "Palisades fire arsonist convicted by LA jury (AP)"),
    (16, "Halifax forum warns US leadership in doubt (AP)"),
    (17, "UN warns ISIS-K is building drone capability (UN)"),
    (18, "Lula advances protection for Raoni's lands (AP)"),
    (19, "Severe heatwave warning for Sydney to Monday (BoM)"),
    (20, "Indonesia passes asset-seizure law (AFP)"),
    (21, "SCO forum sessions open in New Delhi (PTI)"),
    (22, "Iran war cost the US $48.3bn, Pentagon says (AP)"),
    (23, "Ukraine hits three Russian missile launchers (Kyiv)"),
    (24, "'35 by 35' goal enters the COP31 text (Reuters)"),
    (25, "M4.7 quake strikes northern Chile; no damage (USGS)"),
    (26, "CONMEBOL backs Infantino in FIFA race (AP)"),
    (27, "Air Niugini jet lands in Davao; all 146 safe (AP)"),
    (28, "Freight train derails in Sejong; no one hurt (Yonhap)"),
    (29, "Hodeidah port strikes threaten the aid lifeline (UN)"),
    (30, "Australia chase 188 to beat England at the MCG (AFP)"),
    (31, "Israeli fire injures seven in Gaza despite truce (QNA)"),
    (32, "North Melbourne reach 4th straight AFLW final (AAP)"),
    (33, "Alcaraz faces Shelton in the first Turin semi (ATP)"),
    (34, "Trump orders contractors to alert White House (Rtrs)"),
    (35, "Mogadishu rallies back UAE envoy expulsion (Reports)"),
    (36, "Morocco, Mali win big at U-17 World Cup (CAF)"),
]

CLOCK = [
    ("00:09", "Peru quake strikes"),
    ("13:30", "Alcaraz faces Shelton in Turin"),
    ("18:24", "BepiColombo fires its thrusters"),
    ("19:30", "Medvedev meets Zverev in Turin"),
]

DATE_CHECK = (
    "Left out as other days\u2019 news: Russian missiles in Poland (Fri 20 Nov) "
    "\u00b7 Kyiv\u2019s bridges hit (Fri 20 Nov) \u00b7 Cyclone Akvan (Fri 20 Nov) "
    "\u00b7 the World Court\u2019s Myanmar ruling (Thu 19 Nov) \u00b7 the Virginia "
    "measles death (Fri 20 Nov) \u00b7 Wall Street\u2019s correction (Fri 20 Nov) "
    "\u00b7 the Shenzhen summit (Thu 19 Nov) \u00b7 Anthropic\u2019s debut "
    "(Thu 19 Nov) \u00b7 the GTA VI launch (Thu 19 Nov) \u00b7 Starc\u2019s 7/58 "
    "\u2014 the 2025 Ashes, a year ago. Late-Friday events below are shown as "
    "first reported on Saturday."
)

FOOTER_L = ("Every story here happened, or was first reported, on Saturday "
            "21 November 2026. Officials\u2019 counts are attributed.")
FOOTER_R = "Sources named beside each story \u00b7 original drawings"

# Map pins: story number -> (lon, lat, dx, dy) offset of the number badge.
# No. 4 is in space (Mercury) and gets no pin.
PINS = {
    1: (30.7, 36.9, 20, 18), 2: (33.4, 47.9, -24, -10),
    3: (46.7, 24.7, 10, 16), 5: (21.0, 52.2, -22, -12),
    6: (174.8, -41.3, -14, 0), 7: (-115.1, 36.2, 8, -14),
    8: (-75.2, -11.2, -20, 8), 9: (6.3, 4.8, -22, 14),
    10: (-0.1, 51.5, -20, 12), 11: (44.2, 32.9, 26, -12),
    12: (28.0, -26.2, 12, 0), 13: (7.7, 45.1, -18, 16),
}

# Rough continent outlines, (lon, lat) vertices, drawn by hand.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 44),
     (-75, 38), (-80, 32), (-81, 26), (-90, 21), (-95, 19), (-97, 16),
     (-92, 15), (-86, 13), (-83, 9), (-80, 8), (-85, 11), (-90, 14),
     (-97, 16), (-105, 20), (-110, 23), (-114, 29), (-120, 34), (-125, 40),
     (-124, 48), (-130, 55), (-145, 60), (-158, 58), (-165, 60)],
    [(-80, 8), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-70, -18),
     (-70, -23), (-65, -28), (-60, -35), (-57, -38), (-62, -41), (-65, -45),
     (-68, -52), (-70, -48), (-73, -44), (-73, -37), (-71, -30), (-70, -23),
     (-70, -18), (-77, -12), (-81, -6)],
    [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34),
     (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (40, 15), (43, 12),
     (48, 11), (51, 12), (44, 5), (41, 0), (40, -5), (36, -10), (35, -18),
     (32, -26), (28, -33), (20, -35), (17, -32), (15, -27), (12, -18),
     (12, -10), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
     (10, 59), (5, 60), (10, 62), (18, 69), (25, 71), (30, 70), (40, 68),
     (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 77), (110, 74),
     (120, 73), (130, 72), (140, 72), (150, 70), (160, 70), (170, 67),
     (178, 65), (178, 64), (170, 60), (162, 56), (158, 52), (150, 59),
     (142, 55), (140, 50), (135, 44), (130, 42), (127, 40), (122, 38),
     (120, 32), (122, 28), (118, 25), (110, 20), (108, 18), (105, 10),
     (103, 8), (100, 6), (98, 10), (95, 16), (92, 21), (89, 22), (86, 20),
     (82, 17), (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (61, 25), (58, 26), (56, 27), (52, 28), (50, 29), (48, 30), (44, 29),
     (40, 31), (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (22, 37),
     (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 37)],
    [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37), (141, 39),
     (141, 41), (142, 44), (144, 44), (141, 42), (140, 38), (138, 35),
     (135, 34), (132, 33)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (175, -40),
     (173, -42), (170, -44), (167, -46)],
]


# ---------------------------------------------------------------- helpers
def wrap_text(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, max_w, fill, leading, max_lines, tag):
    lines = wrap_text(d, text, fnt, max_w)
    if len(lines) > max_lines:
        ISSUES.append("%s: %d lines, kept %d: %r"
                      % (tag, len(lines), max_lines, text[:60]))
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def text_box(d, x, y, text, fnt, fg=(255, 255, 255), bg=RED, pad=4):
    w = int(d.textlength(text, font=fnt)) + 2 * pad
    h = fnt.size + 2 * pad - 2
    d.rectangle([x, y, x + w, y + h], fill=bg)
    d.text((x + pad, y + pad - 1), text, font=fnt, fill=fg)
    return w, h


def hline(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- big visuals
def draw_cop31(d, x, y, w, h):
    """COP31 hall at overtime: teal hall, delegate rows, podium, wall clock."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    d.rectangle([x, y, x + w, y + h], fill=(16, 62, 78))
    # back wall panel + stage floor
    d.rectangle([x, y, x + w, y + 34], fill=(24, 84, 102))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(10, 40, 52))
    # wall clock, hands at five to midnight, red rim
    cx, cy, r = x + w - 46, y + 52, 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 242, 235),
              outline=RED, width=3)
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang - 90)
        d.line([(cx + (r - 5) * math.cos(a), cy + (r - 5) * math.sin(a)),
                (cx + (r - 1) * math.cos(a), cy + (r - 1) * math.sin(a))],
               fill=(40, 40, 40), width=2)
    d.line([(cx, cy), (cx - 2, cy - 15)], fill=(20, 20, 20), width=3)
    d.line([(cx, cy), (cx + 12, cy - 4)], fill=(20, 20, 20), width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    # stage: long negotiation table with name plates
    d.rectangle([x + 18, y + 44, x + w - 18, y + 62], fill=(120, 84, 50))
    d.rectangle([x + 18, y + 44, x + w - 18, y + 48], fill=(150, 108, 66))
    for px in range(x + 34, x + w - 40, 44):
        d.rectangle([px, y + 52, px + 26, y + 60], fill=(245, 242, 235))
    # podium with microphone, centre stage
    d.polygon([(x + w // 2 - 22, y + 62), (x + w // 2 + 22, y + 62),
               (x + w // 2 + 14, y + h - 26), (x + w // 2 - 14, y + h - 26)],
              fill=(30, 52, 74))
    d.rectangle([x + w // 2 - 22, y + 62, x + w // 2 + 22, y + 68],
                fill=(40, 68, 96))
    d.line([(x + w // 2 + 8, y + 62), (x + w // 2 + 16, y + 48)],
           fill=(20, 20, 20), width=2)
    d.ellipse([x + w // 2 + 13, y + 44, x + w // 2 + 19, y + 50], fill=(20, 20, 20))
    # delegate rows: heads above seat backs, three rows deep.
    # Heads near the podium (centre) are skipped so they do not cover it.
    for row, ry in enumerate((84, 106, 126)):
        for sx in range(x + 22, x + w - 22, 30):
            if (sx // 30 + row) % 5 == 2:
                continue
            if abs(sx + 7 - (x + w // 2)) < 30:
                continue
            d.ellipse([sx, y + ry, sx + 14, y + ry + 13],
                      fill=(196, 168, 130) if row % 2 == 0 else (150, 120, 96))
            d.rectangle([sx - 2, y + ry + 13, sx + 16, y + ry + 20],
                        fill=(70, 90, 110) if row % 2 == 0 else (96, 70, 110))


def draw_kryvyi(d, x, y, w, h):
    """Night over Kryvyi Rih: skyline, bridge, missile streaks, fires."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    d.rectangle([x, y, x + w, y + h], fill=(14, 24, 52))
    # stars
    for sx, sy, r in [(22, 10, 1), (64, 24, 1), (118, 8, 2), (176, 20, 1),
                      (238, 12, 1), (288, 28, 2), (44, 42, 1), (148, 36, 1),
                      (208, 46, 1), (268, 6, 1), (92, 16, 1), (318, 38, 1),
                      (132, 4, 1), (202, 6, 1), (72, 32, 1), (302, 50, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(220, 225, 240))
    # moon
    d.ellipse([x + w - 56, y + 6, x + w - 22, y + 40], fill=(235, 228, 200))
    d.ellipse([x + w - 48, y + 14, x + w - 38, y + 24], fill=(208, 198, 162))
    # skyline: varied blocks, two chimneys, one dome
    for bx, bw, bh in [(0, 30, 40), (34, 24, 56), (62, 28, 36), (94, 20, 52),
                       (118, 34, 44), (156, 22, 60), (182, 28, 40), (214, 26, 54),
                       (244, 32, 38), (280, 26, 50), (310, 18, 44)]:
        d.rectangle([x + bx, y + h - 56 - bh, x + bx + bw, y + h - 56],
                    fill=(9, 14, 30))
        for wy in range(y + h - 56 - bh + 6, y + h - 58, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 10):
                if (wx * 5 + wy * 7) % 13 < 5:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    # dome on the 118-wide block, chimneys on two towers
    d.pieslice([x + 124, y + h - 56 - 44 - 12, x + 146, y + h - 56 - 44 + 4],
               180, 360, fill=(9, 14, 30))
    for ax in (46, 227):
        d.rectangle([x + ax, y + h - 56 - 68, x + ax + 4, y + h - 56 - 56],
                    fill=(9, 14, 30))
        d.ellipse([x + ax - 1, y + h - 56 - 72, x + ax + 5, y + h - 56 - 66],
                  fill=(255, 90, 70))
    # searchlight beams from two rooftops
    d.line([(x + 58, y + h - 56 - 54), (x + 18, y + 10)],
           fill=(190, 200, 228), width=2)
    d.line([(x + 262, y + h - 56 - 36), (x + 300, y + 6)],
           fill=(190, 200, 228), width=2)
    # river
    d.rectangle([x, y + h - 56, x + w, y + h], fill=(22, 48, 90))
    for rx in range(8, w, 26):
        d.line([(x + rx, y + h - 28), (x + rx + 14, y + h - 28)],
               fill=(70, 110, 170), width=2)
    # bridge deck + arches + cables
    by = y + h - 64
    d.rectangle([x, by, x + w, by + 7], fill=(8, 12, 26))
    for cx in (58, 164, 268):
        d.arc([x + cx - 40, by - 24, x + cx + 40, by + 8], 180, 360,
              fill=(200, 205, 220), width=3)
        d.line([(x + cx - 40, by), (x + cx - 40, by + 7)], fill=(200, 205, 220),
               width=3)
        d.line([(x + cx + 40, by), (x + cx + 40, by + 7)], fill=(200, 205, 220),
               width=3)
        for vx in (-26, -13, 0, 13, 26):
            d.line([(x + cx + vx, by - 13), (x + cx + vx, by)],
                   fill=(150, 158, 175), width=1)
    # missile streaks (dashed) + smoke puff at one trail end
    for (mx0, my0, mx1, my1) in [(296, 4, 166, 60), (248, 0, 60, 64),
                                 (326, 28, 270, 58), (108, 2, 50, 38)]:
        steps = 9
        for i in range(steps):
            if i % 2:
                continue
            t0 = i / steps
            t1 = (i + 0.7) / steps
            d.line([(x + mx0 + (mx1 - mx0) * t0, y + my0 + (my1 - my0) * t0),
                    (x + mx0 + (mx1 - mx0) * t1, y + my0 + (my1 - my0) * t1)],
                   fill=(255, 230, 150), width=2)
    d.ellipse([x + 292, y, x + 302, y + 10], fill=(120, 125, 140))
    # fireballs with layered glow on the bridge + river reflections
    for fx, fy in [(60, 60), (166, 56), (270, 54)]:
        d.ellipse([x + fx - 13, y + fy - 13, x + fx + 13, y + fy + 13],
                  fill=(200, 90, 20))
        d.ellipse([x + fx - 9, y + fy - 9, x + fx + 9, y + fy + 9],
                  fill=(255, 140, 30))
        d.ellipse([x + fx - 5, y + fy - 5, x + fx + 5, y + fy + 5],
                  fill=(255, 200, 80))
        d.ellipse([x + fx - 2, y + fy - 2, x + fx + 2, y + fy + 2],
                  fill=(255, 235, 150))
        for k, rw in enumerate((16, 11, 7)):
            d.line([(x + fx - rw // 2, y + h - 20 + k * 6),
                    (x + fx + rw // 2, y + h - 20 + k * 6)],
                   fill=(255, 160, 60), width=2)


def draw_riyadh(d, x, y, w, h):
    """Dawn over Riyadh: skyline with the Kingdom Centre tower, interceptors."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    # dawn sky: dark violet top, warm band at the horizon
    d.rectangle([x, y, x + w, y + h], fill=(44, 34, 74))
    d.rectangle([x, y + 52, x + w, y + 96], fill=(96, 58, 88))
    d.rectangle([x, y + 96, x + w, y + h], fill=(196, 118, 74))
    # crescent moon
    d.ellipse([x + 18, y + 8, x + 48, y + 38], fill=(240, 232, 200))
    d.ellipse([x + 28, y + 4, x + 54, y + 34], fill=(44, 34, 74))
    # skyline: blocks + the Kingdom Centre tower (inverted-arch top)
    for bx, bw, bh in [(0, 34, 34), (38, 26, 46), (68, 30, 30), (102, 22, 44),
                       (128, 36, 36), (196, 24, 50), (224, 30, 34), (258, 28, 44),
                       (290, 24, 38)]:
        d.rectangle([x + bx, y + h - 34 - bh, x + bx + bw, y + h - 34],
                    fill=(30, 22, 52))
        for wy in range(y + h - 34 - bh + 6, y + h - 36, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 10):
                if (wx * 7 + wy * 3) % 11 < 4:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    # Kingdom Centre tower, centre: tall shaft, parabolic arch opening
    tx = x + 168
    d.rectangle([tx, y + 8, tx + 26, y + h - 34], fill=(30, 22, 52))
    d.pieslice([tx + 2, y + 10, tx + 24, y + 44], 180, 360, fill=(196, 118, 74))
    d.rectangle([tx + 9, y + 20, tx + 17, y + 44], fill=(30, 22, 52))
    for wy in range(y + 52, y + h - 40, 14):
        d.rectangle([tx + 5, wy, tx + 9, wy + 5], fill=(255, 214, 120))
        d.rectangle([tx + 17, wy, tx + 21, wy + 5], fill=(255, 214, 120))
    # ground
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(24, 18, 44))
    # interceptor trails rising to three bursts
    for (bx0, by0, bx1, by1) in [(60, 128, 92, 34), (180, 128, 210, 26),
                                 (280, 128, 258, 44)]:
        steps = 10
        for i in range(steps):
            if i % 2:
                continue
            t0 = i / steps
            t1 = (i + 0.65) / steps
            d.line([(x + bx0 + (bx1 - bx0) * t0, y + by0 + (by1 - by0) * t0),
                    (x + bx0 + (bx1 - bx0) * t1, y + by0 + (by1 - by0) * t1)],
                   fill=(255, 240, 180), width=2)
    # bursts: layered star flashes
    for bx, by in [(92, 34), (210, 26), (258, 44)]:
        d.ellipse([x + bx - 14, y + by - 14, x + bx + 14, y + by + 14],
                  fill=(255, 160, 60))
        d.ellipse([x + bx - 8, y + by - 8, x + bx + 8, y + by + 8],
                  fill=(255, 220, 120))
        d.ellipse([x + bx - 4, y + by - 4, x + bx + 4, y + by + 4],
                  fill=(255, 245, 200))
        for dx, dy in [(-20, 0), (20, 0), (0, -20), (0, 20)]:
            d.line([(x + bx + dx // 2, y + by + dy // 2),
                    (x + bx + dx, y + by + dy)], fill=(255, 220, 120), width=2)


# ---------------------------------------------------------------- small icons
def _eu_stars(d, x, y, cx, cy, r, n=12):
    import math
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 215, 0))


def draw_icon(d, kind, x, y, w, h):
    """One thin illustrative strip for a small story."""
    x, y, w, h = int(x), int(y), int(w), int(h)
    if kind == "mercury":
        d.rectangle([x, y, x + w, y + h], fill=(12, 16, 34))
        for sx, sy in [(10, 4), (40, 8), (150, 5), (180, 14), (120, 20)]:
            d.ellipse([x + sx, y + sy, x + sx + 1, y + sy + 1],
                      fill=(220, 225, 240))
        d.ellipse([x + 12, y + 2, x + 42, y + h - 2], fill=(150, 140, 130))
        d.ellipse([x + 20, y + 8, x + 26, y + 14], fill=(110, 100, 92))
        d.ellipse([x + 30, y + 16, x + 34, y + 20], fill=(110, 100, 92))
        # probe: bus + two solar panels, on a dashed trajectory
        for i in range(0, 60, 8):
            d.line([(x + 70 + i, y + 18 - i // 6), (x + 74 + i, y + 16 - i // 6)],
                   fill=(200, 205, 220), width=1)
        d.rectangle([x + 128, y + 6, x + 140, y + 16], fill=(220, 225, 230))
        d.rectangle([x + 118, y + 9, x + 128, y + 13], fill=(40, 90, 180))
        d.rectangle([x + 140, y + 9, x + 150, y + 13], fill=(40, 90, 180))
    elif kind == "warsaw":
        d.rectangle([x, y, x + w, y + h // 2], fill=(255, 255, 255))
        d.rectangle([x, y + h // 2, x + w, y + h], fill=(220, 20, 60))
        d.ellipse([x + w - 40, y + 2, x + w - 12, y + h - 2], fill=(0, 51, 153))
        _eu_stars(d, x, y, w - 26, h // 2, 9, n=8)
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(64, 140, 80))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(190, 170, 120))
        d.polygon([(x + 60, y + 4), (x + 74, y + 8), (x + 130, y + h - 6),
                   (x + 116, y + h - 2)], fill=(190, 150, 100))
        d.ellipse([x + 140, y + 4, x + 152, y + 16], fill=(200, 40, 40))
        d.line([(x + 20, y + 6), (x + 40, y + 6)], fill=(255, 255, 255), width=2)
        d.line([(x + 20, y + 10), (x + 40, y + 10)], fill=(255, 255, 255), width=2)
    elif kind == "vegas":
        d.rectangle([x, y, x + w, y + h], fill=(14, 14, 18))
        for i in range(8):
            for j in range(2):
                if (i + j) % 2 == 0:
                    d.rectangle([x + 8 + i * 12, y + 4 + j * 9,
                                 x + 20 + i * 12, y + 13 + j * 9],
                                fill=(255, 255, 255))
        d.polygon([(x + 120, y + 6), (x + 150, y + 10), (x + 120, y + 20)],
                  fill=(220, 40, 60))
        d.rectangle([x + 120, y + 8, x + 180, y + 18], fill=(220, 40, 60))
        for wx in (126, 140, 154, 168):
            d.ellipse([x + wx, y + h - 8, x + wx + 8, y + h], fill=(20, 20, 20))
    elif kind == "seismo":
        d.rectangle([x, y, x + w, y + h], fill=(245, 242, 235))
        d.line([(x + 4, y + h // 2), (x + w - 4, y + h // 2)],
               fill=(200, 200, 190), width=1)
        pts = [(8, 13), (30, 13), (44, 13), (52, 4), (60, 22), (68, 8),
               (78, 16), (92, 13), (110, 13), (124, 6), (134, 20), (146, 12),
               (168, 13), (186, 13)]
        for (px0, py0), (px1, py1) in zip(pts, pts[1:]):
            d.line([(x + px0, y + py0), (x + px1, y + py1)],
                   fill=(20, 20, 20), width=2)
        d.ellipse([x + 50, y + 2, x + 54, y + 6], fill=RED)
    elif kind == "boat":
        d.rectangle([x, y, x + w, y + h], fill=(58, 122, 168))
        for wy in (16, 22):
            for wx in range(6, w, 24):
                d.arc([x + wx, y + wy - 4, x + wx + 16, y + wy + 4], 0, 180,
                      fill=(220, 235, 245), width=2)
        d.polygon([(x + 70, y + 4), (x + 130, y + 4), (x + 118, y + 16),
                   (x + 82, y + 16)], fill=(120, 84, 50))
        d.rectangle([x + 96, y - 2, x + 100, y + 6], fill=(90, 60, 40))
        d.polygon([(x + 100, y), (x + 118, y + 4), (x + 100, y + 6)],
                  fill=(255, 255, 255))
    elif kind == "ukeu":
        d.rectangle([x, y, x + w // 2, y + h], fill=(0, 51, 153))
        _eu_stars(d, x, y, w // 4, h // 2, 9)
        d.rectangle([x + w // 2, y, x + w, y + h], fill=(0, 36, 125))
        d.rectangle([x + w // 2, y + h // 2 - 3, x + w, y + h // 2 + 3],
                    fill=(255, 255, 255))
        d.rectangle([x + 3 * w // 4 - 3, y, x + 3 * w // 4 + 3, y + h],
                    fill=(255, 255, 255))
        d.rectangle([x + w // 2, y + h // 2 - 1, x + w, y + h // 2 + 1],
                    fill=(200, 16, 46))
        d.rectangle([x + 3 * w // 4 - 1, y, x + 3 * w // 4 + 1, y + h],
                    fill=(200, 16, 46))
    elif kind == "iraq":
        d.rectangle([x, y, x + w, y + h], fill=(222, 200, 150))
        d.rectangle([x + 20, y + 12, x + 120, y + h - 6], fill=(96, 104, 60))
        d.rectangle([x + 120, y + 8, x + 148, y + h - 6], fill=(80, 88, 52))
        for wx in (38, 70, 102, 132):
            d.ellipse([x + wx, y + h - 8, x + wx + 10, y + h + 2], fill=(20, 20, 20))
        d.rectangle([x + 158, y + 4, x + 162, y + h - 12], fill=(120, 84, 50))
        for fx, fy in [(150, 6), (162, 2), (172, 8), (166, 12)]:
            d.ellipse([x + fx - 6, y + fy - 2, x + fx + 6, y + fy + 2],
                      fill=(60, 130, 70))
    elif kind == "ballot":
        d.rectangle([x, y, x + w, y + h], fill=(24, 40, 60))
        d.rectangle([x + 70, y + 8, x + 130, y + h - 4], fill=(140, 110, 70))
        d.rectangle([x + 70, y + 8, x + 130, y + 12], fill=(110, 84, 50))
        d.rectangle([x + 92, y + 9, x + 108, y + 11], fill=(20, 20, 20))
        d.polygon([(x + 96, y + 2), (x + 104, y + 2), (x + 108, y + 9),
                   (x + 100, y + 9)], fill=(255, 255, 255))
        d.ellipse([x + 150, y + 4, x + 176, y + 22], fill=(0, 146, 70))
        d.ellipse([x + 158, y + 10, x + 168, y + 18], fill=(255, 215, 0))
    elif kind == "tennis":
        d.rectangle([x, y, x + w, y + h], fill=(40, 90, 140))
        d.rectangle([x, y, x + w, y + h // 2], fill=(64, 140, 80))
        d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(255, 255, 255),
               width=2)
        d.line([(x + w // 2, y), (x + w // 2, y + h)], fill=(255, 255, 255),
               width=1)
        d.ellipse([x + 20, y + 4, x + 44, y + h - 4], fill=(200, 220, 60))
        d.arc([x + 20, y + 4, x + 44, y + h - 4], 60, 300, fill=(255, 255, 255),
              width=2)
        d.ellipse([x + 150, y + 6, x + 168, y + 20], fill=(200, 220, 60))


# ---------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    """Simplified world map with numbered pins for stories 1-13 (no. 4 is space)."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    lat_top, lat_bot = 85.0, -60.0

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (lat_top - lat) / (lat_top - lat_bot) * h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    f_num = get_font(SANS_B, 9)
    for num in sorted(PINS):
        lon, lat, dx, dy = PINS[num]
        px, py = proj(lon, lat)
        bx, by = px + dx, py + dy
        d.line([(px, py), (bx, by)], fill=RED, width=1)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255))
        tw = d.textlength(str(num), font=f_num)
        d.text((bx - tw / 2, by - 6), str(num), font=f_num,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx, cw = 10, W - 20  # content x, content width

    # top line
    f_top = get_font(SANS_B, 13)
    d.text((mx, 8), TOP_LEFT, font=f_top, fill=RED)
    f_topr = get_font(SANS_B, 11)
    d.text((mx + cw - d.textlength(TOP_RIGHT, font=f_topr), 9), TOP_RIGHT,
           font=f_topr, fill=INK)
    hline(d, mx, mx + cw, 26, width=2)

    # masthead + subhead
    f_mast = get_font(SERIF_B, 54)
    tw = d.textlength(MASTHEAD, font=f_mast)
    d.text((mx + (cw - tw) / 2, 30), MASTHEAD, font=f_mast, fill=INK)
    f_sub = get_font(SERIF, 15)
    tw = d.textlength(SUBHEAD, font=f_sub)
    d.text((mx + (cw - tw) / 2, 92), SUBHEAD, font=f_sub, fill=INK)
    hline(d, mx, mx + cw, 112, width=2)

    # stat strip: 6 cells
    cell_w = cw / 6
    f_num = get_font(SERIF_B, 22)
    f_lab = get_font(SANS, 10)
    d.rectangle([mx, 116, mx + 4, 156], fill=RED)
    for i, (big, lab) in enumerate(STATS):
        cx = mx + i * cell_w + (8 if i == 0 else 12)
        d.text((cx, 116), big, font=f_num, fill=INK)
        for j, line in enumerate(lab.split("\n")):
            d.text((cx, 141 + j * 11), line, font=f_lab, fill=GRAY)
        if i:
            d.line([(mx + i * cell_w, 118), (mx + i * cell_w, 156)],
                   fill=FAINT, width=1)

    # region bar: 7 equal segments
    seg_w = cw / 7
    f_reg = get_font(SANS_B, 11)
    for i, (name, count, col) in enumerate(REGIONS):
        sx = mx + i * seg_w
        d.rectangle([sx, 164, sx + seg_w - 1, 184], fill=col)
        txt = "%s %d" % (name, count)
        tw = d.textlength(txt, font=f_reg)
        d.text((sx + (seg_w - tw) / 2, 167), txt, font=f_reg,
               fill=(255, 255, 255))

    # big 3
    f_kick = get_font(SANS_B, 11)
    f_head = get_font(SERIF_B, 19)
    f_body = get_font(SANS, 11)
    col_w = (cw - 16) // 3
    for i, st in enumerate(BIG):
        x = int(mx + i * (col_w + 8))
        y0 = 188
        vh = 148
        if st["visual"] == "cop31":
            draw_cop31(d, x, y0, col_w, vh)
        elif st["visual"] == "kryvyi":
            draw_kryvyi(d, x, y0, col_w, vh)
        else:
            draw_riyadh(d, x, y0, col_w, vh)
        text_box(d, x, y0, st["label"], get_font(SANS_B, 12))
        f_chip = get_font(SANS_B, 10)
        chip_w = int(d.textlength(st["chip"], font=f_chip)) + 8
        text_box(d, x, y0 + vh - 19, st["chip"], f_chip, bg=(20, 20, 20),
                 pad=3)
        d.text((x, y0 + 154), "%d %s" % (st["num"], st["kicker"]),
               font=f_kick, fill=RED)
        draw_wrapped(d, x, y0 + 170, st["headline"], f_head, col_w, INK, 22,
                     2, "BIG %d headline" % st["num"])
        draw_wrapped(d, x, y0 + 216, st["body"], f_body, col_w, INK, 14, 3,
                     "BIG %d body" % st["num"])
    hline(d, mx, mx + cw, 448, width=1)

    # small 10: 5 x 2
    f_slab = get_font(SANS_B, 10)
    f_skick = get_font(SANS_B, 10)
    f_shead = get_font(SERIF_B, 13)
    f_sbody = get_font(SANS, 10)
    scol_w = (cw - 32) // 5
    for i, st in enumerate(SMALL):
        col, row = i % 5, i // 5
        x = int(mx + col * (scol_w + 8))
        y0 = 452 + row * 92
        draw_icon(d, st["visual"], x, y0, scol_w, 26)
        text_box(d, x, y0, st["label"], f_slab, pad=3)
        f_chip = get_font(SANS_B, 9)
        chip_w = int(d.textlength(st["chip"], font=f_chip)) + 6
        text_box(d, x + scol_w - chip_w, y0 + 26 - 15, st["chip"], f_chip,
                 bg=(20, 20, 20), pad=3)
        d.text((x, y0 + 28), "%d %s" % (st["num"], st["kicker"]),
               font=f_skick, fill=RED)
        draw_wrapped(d, x, y0 + 41, st["headline"], f_shead, scol_w, INK, 14,
                     2, "SMALL %d headline" % st["num"])
        draw_wrapped(d, x, y0 + 70, st["body"], f_sbody, scol_w, INK, 11, 2,
                     "SMALL %d body" % st["num"])
    hline(d, mx, mx + cw, 640, width=1)

    # bottom: map + ALSO list
    f_sec = get_font(SANS_B, 13)
    d.text((mx, 644), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((mx + 402, 644), "ALSO ON SATURDAY 21 NOVEMBER \u2014 23 MORE STORIES",
           font=f_sec, fill=INK)
    draw_map(d, mx, 666, 392, 220)
    f_cap = get_font(SANS, 10)
    d.text((mx, 890), "Red numbers mark stories 1\u201313. No. 4 is in space: Mercury.",
           font=f_cap, fill=GRAY)
    # ALSO in two columns: 12 in col 1, 11 in col 2
    f_anum = get_font(SANS_B, 11)
    f_at = get_font(SANS, 10)
    for idx, (num, text) in enumerate(ALSO):
        col = 0 if idx < 12 else 1
        row = idx if idx < 12 else idx - 12
        ax = mx + 402 + col * 306
        ay = 666 + row * 20
        ntxt = "%d " % num
        nw = d.textlength(ntxt, font=f_anum)
        if d.textlength(text, font=f_at) > 296 - nw:
            ISSUES.append("ALSO %d wrapped: %r" % (num, text))
        d.text((ax, ay), ntxt, font=f_anum, fill=GREEN)
        d.text((ax + nw, ay), text, font=f_at, fill=INK)

    # by the clock
    f_clock = get_font(SANS, 11)
    f_clockb = get_font(SANS_B, 11)
    cx = mx
    d.text((cx, 906), "BY THE CLOCK \u00b7 UTC", font=f_clockb, fill=INK)
    cx += d.textlength("BY THE CLOCK \u00b7 UTC  ", font=f_clockb)
    for t, what in CLOCK:
        d.text((cx, 906), t, font=f_clockb, fill=RED)
        cx += d.textlength(t + " ", font=f_clockb)
        d.text((cx, 906), what, font=f_clock, fill=INK)
        cx += d.textlength(what + "   \u00b7   ", font=f_clock)

    # date check box: red title, text flowing after it on the same line
    d.rectangle([mx, 928, mx + cw, 998], outline=RED, width=2)
    f_dc = get_font(SANS_B, 11)
    d.text((mx + 8, 933), "DATE CHECK", font=f_dc, fill=RED)
    tw = d.textlength("DATE CHECK  ", font=f_dc)
    draw_wrapped(d, mx + 8 + tw, 933, DATE_CHECK, get_font(SANS, 11),
                 cw - 16 - tw, INK, 14, 4, "DATE CHECK")

    # footer
    f_foot = get_font(SANS, 10)
    d.text((mx, 1003), FOOTER_L, font=f_foot, fill=GRAY)
    d.text((mx + cw - d.textlength(FOOTER_R, font=f_foot), 1003), FOOTER_R,
           font=f_foot, fill=GRAY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out, format="PNG")
    import os
    print("wrote %s %dx%d %d bytes" % (out, img.width, img.height,
                                      os.path.getsize(out)))
    for w in ISSUES:
        print("ISSUE:", w)
    print("issues:", len(ISSUES))


if __name__ == "__main__":
    main()
