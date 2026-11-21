#!/usr/bin/env python3
"""Render the approved 'World in One Day' front page for 21 November 2026.

Fresh rewrite: every line authored here, layout measured from the approved
reference image. Produces entry.png (1024x1024) deterministically.
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 30, 36)
RULE = (60, 58, 52)
MUTE = (96, 94, 88)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

DJ = "/usr/share/fonts/truetype/dejavu/"
DJ_SANS = DJ + "DejaVuSans.ttf"
DJ_SANS_B = DJ + "DejaVuSans-Bold.ttf"
DJ_SERIF_B = DJ + "DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


_ink_cache = {}


def ink_box(text, fnt):
    """Rasterised ink bbox of text, relative to the draw origin.

    Uses a real render + pixel scan, because font metrics (textbbox) can sit
    1-3 px away from where the ink actually lands after hinting.
    """
    key = (text, fnt.path, fnt.size)
    hit = _ink_cache.get(key)
    if hit is not None:
        return hit
    tmp = Image.new("L", (1400, 200), 0)
    d = ImageDraw.Draw(tmp)
    d.text((20, 20), text, font=fnt, fill=255)
    box = tmp.getbbox()
    if box is None:
        res = (0, 0, 0, 0)
    else:
        res = (box[0] - 20, box[1] - 20, box[2] - 20, box[3] - 20)
    _ink_cache[key] = res
    return res


def place_text(canvas, text, fnt, color, ink_x, ink_y):
    """Draw text so that its ink bounding box starts at (ink_x, ink_y)."""
    d = ImageDraw.Draw(canvas)
    ox, oy, _, _ = ink_box(text, fnt)
    d.text((ink_x - ox, ink_y - oy), text, font=fnt, fill=color)


def place_text_box(canvas, text, fnt, color, ink_x, ink_y):
    """Draw text using the font's own bbox (draw-position placement).

    Body copy in the reference was laid out this way: the draw origin, not
    the rasterised ink, sits on the grid, so forcing the ink onto the grid
    shifts it a pixel or two away from the original.
    """
    d = ImageDraw.Draw(canvas)
    box = d.textbbox((0, 0), text, font=fnt)
    d.text((ink_x - box[0], ink_y - box[1]), text, font=fnt, fill=color)


def text_w(text, fnt):
    return fnt.getlength(text)


def wrap_lines(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def hline(canvas, x0, x1, y, color, thick=1):
    d = ImageDraw.Draw(canvas)
    d.rectangle([x0, y, x1, y + thick - 1], fill=color)


def vline(canvas, x, y0, y1, color, thick=1):
    d = ImageDraw.Draw(canvas)
    d.rectangle([x, y0, x + thick - 1, y1], fill=color)


def rect(canvas, x0, y0, x1, y1, color):
    d = ImageDraw.Draw(canvas)
    d.rectangle([x0, y0, x1, y1], fill=color)


def centred_text(canvas, text, fnt, color, cx, ink_y):
    """Draw text horizontally centred on cx, ink top at ink_y."""
    d = ImageDraw.Draw(canvas)
    ox, oy, rx, _ = ink_box(text, fnt)
    w = rx - ox
    d.text((cx - w // 2 - ox, ink_y - oy), text, font=fnt, fill=color)


def draw_header(canvas):
    hline(canvas, 10, 1014, 26, RULE, 2)
    place_text(canvas, "THE WORLD IN ONE DAY", font(DJ_SANS_B, 13), RED, 11, 12)
    place_text(
        canvas,
        "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026",
        font(DJ_SANS_B, 11),
        INK,
        541,
        12,
    )
    place_text(canvas, "Saturday 21 November 2026", font(DJ_SERIF_B, 54), INK, 84, 40)
    place_text(
        canvas,
        "COP31 runs into overtime with no deal \u00b7 Russian strikes kill 12 in Ukraine "
        "\u00b7 Coalition downs three missiles over Riyadh",
        font(DJ_SANS, 13),
        INK,
        58,
        94,
    )
    hline(canvas, 10, 1014, 112, RULE, 2)


STAT_NUMBERS = [
    ("0", 19, 22, "climate deal agreed", "at COP31"),
    ("3", 191, 20, "missiles downed", "over Riyadh"),
    ("12", 360, 21, "killed in Ukraine", "strikes in a day"),
    ("47", 525, 20, "injured in the", "Kryvyi Rih strike"),
    ("8 yrs", 692, 22, "BepiColombo's voyage", "to Mercury"),
    ("6.7", 861, 21, "Peru quake", "magnitude"),
]
STAT_CAP_X = [18, 189, 357, 524, 691, 859]


def draw_stat_strip(canvas):
    rect(canvas, 10, 116, 14, 156, RED)
    for (num, nx, size, cap1, cap2), cx in zip(STAT_NUMBERS, STAT_CAP_X):
        place_text(canvas, num, font(DJ_SERIF_B, size), INK, nx, 121)
        place_text(canvas, cap1, font(DJ_SANS, 10), MUTE, cx, 143)
        place_text(canvas, cap2, font(DJ_SANS, 10), MUTE, cx, 155)
    for sx in (177, 344, 512, 679, 846):
        vline(canvas, sx, 118, 156, (168, 164, 152), 1)


REGIONS = [
    ("EUROPE 9", 10, 152, (47, 90, 168)),
    ("ASIA 6", 153, 295, RED),
    ("MIDDLE EAST 5", 296, 439, (138, 109, 59)),
    ("AFRICA 3", 440, 582, (46, 125, 79)),
    ("AMERICAS 8", 583, 726, (122, 31, 43)),
    ("OCEANIA 4", 727, 869, (46, 127, 134)),
    ("SPACE 1", 870, 1012, (107, 107, 107)),
]


def draw_region_strip(canvas):
    for label, x0, x1, color in REGIONS:
        rect(canvas, x0, 164, x1, 184, color)
        centred_text(canvas, label, font(DJ_SANS_B, 11), WHITE, (x0 + x1) // 2, 170)


# ---------------------------------------------------------------- hero panels
PANELS = [(10, 339), (347, 676), (684, 1013)]
HERO_CHIPS = ["COP31: NO DEAL", "KRYVYI RIH", "RIYADH: 3 DOWN"]
HERO_CAPS = ["Overtime \u00b7 AP", "12 dead in a day", "Second attack \u00b7 Reuters"]


def hero_chip(canvas, x0, label):
    fnt = font(DJ_SANS_B, 11)
    w = int(text_w(label, fnt)) + 10
    rect(canvas, x0, 188, x0 + w - 1, 206, RED)
    place_text(canvas, label, fnt, WHITE, x0 + 5, 193)


def hero_bar(canvas, x0, label):
    fnt = font(DJ_SANS_B, 10)
    w = int(text_w(label, fnt)) + 9
    rect(canvas, x0, 317, x0 + w - 1, 331, BLACK)
    place_text(canvas, label, fnt, WHITE, x0 + 4, 321)


def draw_hero_cop31(canvas):
    x0, x1 = PANELS[0]
    d = ImageDraw.Draw(canvas)
    rect(canvas, x0, 188, x1, 336, (24, 84, 102))
    # wall clock, upper right: red rim, white face, black hands
    d.ellipse([271, 216, 315, 259], fill=RED)
    d.ellipse([274, 219, 312, 256], fill=(245, 242, 235))
    for a in range(12):
        import math
        ang = a * math.pi / 6
        px = 293 + int(16 * math.cos(ang))
        py = 237 + int(16 * math.sin(ang))
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(17, 17, 17))
    d.line([293, 237, 293, 224], fill=(17, 17, 17), width=2)
    d.line([293, 237, 302, 241], fill=(17, 17, 17), width=2)
    # long table with white papers
    rect(canvas, 28, 237, 321, 250, (120, 84, 50))
    rect(canvas, 28, 237, 321, 241, (150, 108, 66))
    for px0 in (44, 78, 150, 196, 236):
        rect(canvas, px0, 224, px0 + 24, 236, (245, 242, 235))
    # central podium
    d.polygon([(160, 255), (185, 255), (200, 310), (145, 310)], fill=(30, 52, 74))
    rect(canvas, x0, 300, x1, 336, (10, 40, 52))
    # two rows of delegates
    bodies = [(70, 90, 110), (150, 120, 96), (96, 70, 110)]
    for row_y, heads in ((272, range(30, 330, 30)), (314, range(40, 330, 30))):
        for k, cx in enumerate(heads):
            d.ellipse([cx - 7, row_y, cx + 7, row_y + 13], fill=(196, 168, 130))
            d.rectangle([cx - 11, row_y + 14, cx + 11, row_y + 22],
                        fill=bodies[k % 3])


def draw_hero_kryvyi(canvas):
    x0, x1 = PANELS[1]
    rect(canvas, x0, 188, x1, 336, (14, 24, 52))
    d = ImageDraw.Draw(canvas)
    # stars
    for sx, sy in ((360, 196), (395, 210), (440, 192), (480, 205), (530, 198),
                   (580, 212), (620, 196), (655, 208), (410, 225), (560, 222)):
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=(200, 205, 220))
    # big pale moon, upper right
    d.ellipse([602, 230, 638, 266], fill=(240, 232, 200))
    d.ellipse([610, 238, 630, 258], fill=(255, 245, 200))
    # skyline silhouettes with lit windows
    import math
    for bx0, bx1, top in ((347, 377, 236), (381, 396, 244), (441, 461, 240),
                          (465, 499, 232), (529, 557, 238), (561, 587, 234),
                          (631, 675, 234)):
        rect(canvas, bx0, top, bx1, 300, (9, 14, 30))
        for wy in range(top + 10, 296, 12):
            for wx in range(bx0 + 6, bx1 - 4, 14):
                d.ellipse([wx, wy, wx + 2, wy + 2], fill=(255, 220, 120))
    # three starburst explosions
    for ex, ey in ((407, 248), (513, 244), (617, 242)):
        for a in range(8):
            ang = a * math.pi / 4 + 0.4
            d.line([ex, ey, ex + int(20 * math.cos(ang)), ey + int(20 * math.sin(ang))],
                   fill=(255, 160, 60), width=2)
        d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=(200, 90, 20))
        d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(255, 140, 30))
        d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 200, 80))
    # embers drifting
    for ex, ey in ((430, 265), (470, 272), (545, 268), (590, 275), (650, 262)):
        d.ellipse([ex, ey, ex + 2, ey + 2], fill=(255, 140, 30))
    rect(canvas, x0, 300, x1, 336, (22, 48, 90))
    for dx in range(x0 + 8, x1 - 8, 22):
        rect(canvas, dx, 324, dx + 12, 326, (200, 205, 220))


def draw_hero_riyadh(canvas):
    x0, x1 = PANELS[2]
    rect(canvas, x0, 188, x1, 336, (44, 34, 74))
    d = ImageDraw.Draw(canvas)
    import math
    # crescent moon, upper left
    d.ellipse([694, 214, 718, 238], fill=(255, 245, 200))
    d.ellipse([700, 210, 724, 234], fill=(44, 34, 74))
    # skyline: mauve blocks with dark towers and lit windows
    rect(canvas, x0, 240, x1, 300, (96, 58, 88))
    for bx0, bx1, top in ((684, 718, 252), (722, 748, 246), (752, 776, 250),
                          (786, 800, 244), (812, 848, 248), (852, 878, 228),
                          (880, 904, 250), (908, 938, 246), (942, 952, 252),
                          (974, 998, 250)):
        rect(canvas, bx0, top, bx1, 300, (30, 22, 52))
        for wy in range(top + 8, 296, 12):
            for wx in range(bx0 + 5, bx1 - 3, 13):
                d.ellipse([wx, wy, wx + 2, wy + 2], fill=(255, 220, 120))
    # two interceptor starbursts with streaks falling away
    for ex, ey in ((760, 228), (925, 222)):
        for a in range(8):
            ang = a * math.pi / 4 + 0.2
            d.line([ex, ey, ex + int(22 * math.cos(ang)), ey + int(22 * math.sin(ang))],
                   fill=(255, 160, 60), width=2)
        d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=(255, 160, 60))
        d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(255, 220, 120))
        d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 245, 200))
        d.line([ex - 6, ey + 14, ex - 16, ey + 44], fill=(255, 220, 120), width=2)
        d.line([ex + 8, ey + 12, ex + 18, ey + 40], fill=(255, 245, 200), width=1)
    rect(canvas, x0, 300, x1, 336, (24, 18, 44))
    for dx in range(x0 + 8, x1 - 8, 22):
        rect(canvas, dx, 324, dx + 12, 326, (200, 205, 220))


def draw_hero(canvas):
    draw_hero_cop31(canvas)
    draw_hero_kryvyi(canvas)
    draw_hero_riyadh(canvas)
    for (x0, _), label in zip(PANELS, HERO_CHIPS):
        hero_chip(canvas, x0, label)
    for (x0, _), label in zip(PANELS, HERO_CAPS):
        hero_bar(canvas, x0, label)


# ---------------------------------------------------------------- big stories
BIG = [
    ("1 ANTALYA \u00b7 CLIMATE",
     ["COP31 runs into overtime", "with no deal"],
     "Talks suspended to Saturday after a revised draft dropped all fossil-fuel "
     "references and the $120bn-a-year adaptation target. (AP, Al Jazeera)"),
    ("2 KRYVYI RIH, UKRAINE \u00b7 WAR",
     ["Russian strikes kill 12", "in Ukraine"],
     "Overnight barrage kills at least nine; two dead, 47 hurt in Kryvyi Rih. "
     "Kyiv counts 12 dead, 82 hurt in a day. (Kyiv Independent, BBC)"),
    ("3 RIYADH \u00b7 CONFLICT",
     ["Coalition downs three missiles", "over Riyadh"],
     "Saudi-led forces intercepted three Houthi ballistic missiles bound for the "
     "capital, the second attack in days after the PIF tower was hit. (Reuters)"),
]


def draw_big_stories(canvas):
    for (numline, headline, deck), (x0, _) in zip(BIG, PANELS):
        place_text(canvas, numline, font(DJ_SANS_B, 11), RED, x0 + 1, 345)
        for i, line in enumerate(headline):
            place_text_box(canvas, line, font(DJ_SANS_B, 19), INK, x0, 362 + i * 22)
        for i, line in enumerate(wrap_lines(deck, font(DJ_SANS, 11), 330)):
            place_text_box(canvas, line, font(DJ_SANS, 11), INK, x0, 406 + i * 14)


# ---------------------------------------------------------------- small stories
SMALL_COLS = [(10, 204), (212, 406), (414, 608), (616, 810), (818, 1012)]
SMALL = [
    ("4 MERCURY \u00b7 SPACE", "MERCURY: ARRIVED", "19:24 CET \u00b7 ESA",
     "BepiColombo reaches Mercury",
     "Thrusters fired 19:24 CET after an eight-year voyage. (ESA)"),
    ("5 WARSAW \u00b7 NATO", "WARSAW: NATO", "Saturday \u00b7 AP",
     "Rutte flies to Warsaw for NATO talks",
     "After a missile lands in Poland, allies weigh defences. (AP)"),
    ("6 WELLINGTON \u00b7 CRICKET", "RAHUL: 136", "Day 3 \u00b7 PTI",
     "Rahul's 136 puts India ahead",
     "India 486/4, a lead of 118, on day three at the Basin. (PTI)"),
    ("7 LAS VEGAS \u00b7 FORMULA 1", "VEGAS: POLE", "Qualifying \u00b7 F1",
     "Antonelli fastest, Verstappen takes pole",
     "Antonelli fastest but penalised; Verstappen inherits pole. (F1)"),
    ("8 JUN\u00cdN, PERU \u00b7 QUAKE", "PERU: 6.7", "00:09 UTC \u00b7 USGS",
     "Magnitude 6.7 quake hits Peru",
     "Deep tremor north of Jun\u00edn, felt in Lima; no deaths. (USGS)"),
    ("9 BAYELSA, NIGERIA \u00b7 DISASTER", "BAYELSA: 4 DEAD", "Saturday \u00b7 Reuters",
     "Tinubu orders rescue after boat disaster",
     "Four dead, 24 rescued; Tinubu orders a federal response. (Reuters)"),
    ("10 LONDON \u00b7 BRUSSELS", "UK\u2013EU: DEAL", "Agreed \u00b7 AP",
     "UK and EU seal a reset deal",
     "Food trade, youth visas, carbon link; 100,000 a year. (AP)"),
    ("11 CENTRAL IRAQ \u00b7 SECURITY", "IRAQ: ARMY IN", "Saturday \u00b7 Reports",
     "Iraqi forces hold Jurf al-Sakhar",
     "Army holds the stronghold; Karbala road reopens today. (Reports)"),
    ("12 SOUTH AFRICA \u00b7 POLITICS", "ANC: 31%", "Coalition talks \u00b7 BBC",
     "ANC scrambles for coalition partners",
     "Worst result ever, 31%; coalition talks run to 27 Nov. (BBC)"),
    ("13 TURIN \u00b7 TENNIS", "TURIN: SEMI", "20:30 CET \u00b7 ATP",
     "Medvedev meets Zverev tonight",
     "Semi not before 20:30 CET; Zverev 3\u20130 in the group. (ATP)"),
]


def draw_strip_scene(canvas, n, x0, x1, y0, y1):
    d = ImageDraw.Draw(canvas)
    if n == 4:  # Mercury: dark space, pale planet
        rect(canvas, x0, y0, x1, y1, (12, 16, 34))
        for sx, sy in ((x0 + 20, y0 + 5), (x0 + 60, y0 + 3), (x0 + 150, y0 + 6)):
            d.ellipse([sx, sy, sx + 1, sy + 1], fill=WHITE)
        d.ellipse([x1 - 70, y0 + 2, x1 - 40, y1 - 2], fill=(150, 140, 130))
        d.ellipse([x1 - 66, y0 + 4, x1 - 48, y0 + 12], fill=(220, 225, 230))
        d.ellipse([x0 + 90, y0 + 16, x0 + 110, y1 - 4], fill=(40, 90, 180))
    elif n == 5:  # Warsaw: red field, EU disc
        rect(canvas, x0, y0, x1, y1, (220, 20, 60))
        d.ellipse([x0 + 60, y0 + 2, x0 + 100, y1 - 2], fill=WHITE)
        d.ellipse([x0 + 68, y0 + 5, x0 + 92, y1 - 5], fill=(0, 51, 153))
        for a in range(12):
            import math
            ang = a * math.pi / 6
            px = x0 + 80 + int(9 * math.cos(ang))
            py = y0 + 13 + int(9 * math.sin(ang))
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 215, 0))
    elif n == 6:  # cricket: green outfield, tan pitch, red ball
        rect(canvas, x0, y0, x1, y1, (64, 140, 80))
        rect(canvas, x0 + 70, y0 + 4, x0 + 130, y1 - 4, (190, 170, 120))
        rect(canvas, x0 + 70, y0 + 4, x0 + 130, y0 + 8, (190, 150, 100))
        d.ellipse([x1 - 30, y0 + 8, x1 - 18, y0 + 20], fill=(200, 40, 40))
    elif n == 7:  # Vegas: night, chequered flag, red streak
        rect(canvas, x0, y0, x1, y1, (14, 14, 18))
        for r in range(3):
            for c in range(6):
                if (r + c) % 2 == 0:
                    rect(canvas, x0 + 8 + c * 9, y0 + 3 + r * 7,
                         x0 + 16 + c * 9, y0 + 9 + r * 7, WHITE)
        d.line([x0 + 90, y1 - 4, x1 - 10, y0 + 6], fill=(220, 40, 60), width=3)
    elif n == 8:  # Peru: pale paper, black seismograph trace
        rect(canvas, x0, y0, x1, y1, (245, 242, 235))
        pts = [(x0 + 6, y0 + 14), (x0 + 30, y0 + 14), (x0 + 40, y0 + 4),
               (x0 + 48, y0 + 24), (x0 + 56, y0 + 8), (x0 + 66, y0 + 20),
               (x0 + 76, y0 + 14), (x0 + 110, y0 + 14), (x0 + 120, y0 + 6),
               (x0 + 130, y0 + 22), (x0 + 140, y0 + 14), (x1 - 6, y0 + 14)]
        d.line(pts, fill=BLACK, width=2)
    elif n == 9:  # Bayelsa: blue water, pale waves, brown boat
        rect(canvas, x0, y0, x1, y1, (58, 122, 168))
        for wy in (y0 + 8, y0 + 16, y1 - 6):
            d.line([x0 + 4, wy, x1 - 4, wy], fill=(220, 235, 245), width=2)
        rect(canvas, x0 + 80, y0 + 10, x0 + 120, y0 + 18, (120, 84, 50))
    elif n == 10:  # UK-EU: blue field, white cross, red saltire hint
        rect(canvas, x0, y0, x1, y1, (0, 51, 153))
        rect(canvas, x0 + 100, y0, x1, y1, (0, 36, 125))
        d.line([x0 + 100, y0, x1, y1], fill=WHITE, width=3)
        d.line([x0 + 100, y1, x1, y0], fill=WHITE, width=3)
        d.line([x0 + 100, y0, x1, y1], fill=(200, 16, 46), width=1)
        for a in range(8):
            import math
            ang = a * math.pi / 4
            px = x0 + 50 + int(12 * math.cos(ang))
            py = y0 + 13 + int(10 * math.sin(ang))
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 215, 0))
    elif n == 11:  # Iraq: desert, olive berm, dark vehicle
        rect(canvas, x0, y0, x1, y1, (222, 200, 150))
        rect(canvas, x0, y1 - 10, x1, y1, (96, 104, 60))
        rect(canvas, x0 + 70, y0 + 8, x0 + 120, y0 + 18, BLACK)
        rect(canvas, x0 + 88, y0 + 4, x0 + 102, y0 + 8, BLACK)
        rect(canvas, x0 + 130, y0 + 14, x0 + 160, y0 + 20, (60, 130, 70))
    elif n == 12:  # ANC: dark hall, brown shape, green band
        rect(canvas, x0, y0, x1, y1, (24, 40, 60))
        d.polygon([(x0 + 40, y1), (x0 + 70, y0 + 4), (x0 + 110, y1)], fill=(110, 84, 50))
        rect(canvas, x0, y0 + 6, x1, y0 + 10, (0, 146, 70))
        d.ellipse([x1 - 30, y0 + 14, x1 - 18, y1 - 4], fill=(140, 110, 70))
    else:  # Turin: green court, blue surround, yellow ball
        rect(canvas, x0, y0, x1, y1, (64, 140, 80))
        rect(canvas, x0 + 60, y0 + 4, x0 + 140, y1 - 4, (40, 90, 140))
        d.line([x0 + 60, y0 + 13, x0 + 140, y0 + 13], fill=WHITE, width=1)
        d.ellipse([x1 - 34, y0 + 8, x1 - 20, y0 + 22], fill=(200, 220, 60))


def draw_small_stories(canvas):
    hline(canvas, 10, 1014, 448, RULE, 1)
    hline(canvas, 10, 1014, 640, RULE, 1)
    for idx, (numline, chip, cap, headline, deck) in enumerate(SMALL):
        n = idx + 4
        row = idx // 5
        col = idx % 5
        x0, x1 = SMALL_COLS[col]
        sy = 452 if row == 0 else 544
        ey = 478 if row == 0 else 570
        draw_strip_scene(canvas, n, x0, x1, sy, ey)
        # red chip, top-left of the strip
        cf = font(DJ_SANS_B, 10)
        cw = int(text_w(chip, cf)) + 9
        rect(canvas, x0, sy, x0 + cw - 1, sy + 14, RED)
        place_text(canvas, chip, cf, WHITE, x0 + 4, sy + 5)
        # black caption bar, bottom-right of the strip
        bf = font(DJ_SANS_B, 10)
        bw = int(text_w(cap, bf)) + 9
        bx = x1 - bw + 1
        by = sy + 11
        rect(canvas, bx, by, x1, by + 13, BLACK)
        place_text(canvas, cap, bf, WHITE, bx + 4, by + 4)
        # text block below the strip
        ny = 483 if row == 0 else 575
        hy = 496 if row == 0 else 588
        dy = 524 if row == 0 else 616
        place_text_box(canvas, numline, font(DJ_SANS_B, 10), RED, x0, ny)
        for i, line in enumerate(wrap_lines(headline, font(DJ_SANS_B, 13), 195)):
            place_text_box(canvas, line, font(DJ_SANS_B, 13), INK, x0, hy + i * 15)
        for i, line in enumerate(wrap_lines(deck, font(DJ_SANS, 10), 195)):
            place_text_box(canvas, line, font(DJ_SANS, 10), INK, x0, dy + i * 11)


# ---------------------------------------------------------------- map
SEA = (206, 224, 234)
LAND = (232, 217, 172)
MAP_DOT = (176, 30, 36)
MAP_GREEN = (28, 110, 58)
# landmass scanlines, sampled every 6 px: (y, [(x0, x1), ...])
LAND_RUNS = [
    (684, [(295, 333)]),
    (690, [(46, 79), (116, 121), (227, 243), (273, 383)]),
    (696, [(25, 125), (221, 397)]),
    (702, [(27, 131), (215, 391)]),
    (708, [(60, 138), (226, 363), (372, 383)]),
    (714, [(67, 143), (231, 358), (377, 378)]),
    (720, [(70, 82), (94, 142), (203, 215), (221, 236), (244, 356)]),
    (726, [(71, 79), (97, 134), (200, 211), (217, 275), (285, 353)]),
    (732, [(70, 82), (94, 126), (197, 206), (226, 271), (289, 345)]),
    (738, [(73, 78), (82, 122), (230, 268), (287, 337)]),
    (744, [(77, 118), (205, 218), (248, 335)]),
    (750, [(82, 117), (199, 241), (265, 336)]),
    (756, [(85, 115), (192, 244), (272, 334)]),
    (762, [(90, 108), (189, 245), (283, 326)]),
    (768, [(98, 100), (188, 247), (286, 322)]),
    (774, [(188, 250), (287, 320)]),
    (780, [(191, 257), (313, 318)]),
    (786, [(119, 120), (197, 253)]),
    (792, [(119, 120), (216, 250)]),
    (798, [(217, 248)]),
    (804, [(118, 118), (218, 247)]),
    (810, [(220, 244)]),
    (816, [(220, 243), (345, 359)]),
    (822, [(220, 243), (337, 362)]),
    (828, [(221, 241), (331, 367)]),
    (834, [(130, 132), (223, 233), (330, 370)]),
    (840, [(129, 135), (224, 237), (331, 371)]),
    (846, [(128, 138), (227, 231), (334, 370)]),
    (852, [(127, 142)]),
    (858, [(127, 136)]),
    (864, [(128, 134)]),
    (870, [(131, 131)]),
]
# (story number, dot centre, small location dot)
MAP_PINS = [
    (1, (259, 756), (244, 743)),
    (2, (222, 711), (244, 718)),
    (3, (266, 773), (260, 755)),
    (5, (206, 704), (200, 718)),
    (6, (382, 857), (394, 857)),
    (7, (88, 726), (80, 738)),
    (8, (104, 819), (120, 812)),
    (9, (190, 801), (206, 790)),
    (10, (185, 728), (196, 720)),
    (11, (280, 733), (262, 742)),
    (12, (248, 834), (236, 834)),
    (13, (196, 742), (209, 730)),
]


def draw_map(canvas):
    d = ImageDraw.Draw(canvas)
    rect(canvas, 10, 666, 402, 886, SEA)
    for y, runs in LAND_RUNS:
        for x0, x1 in runs:
            rect(canvas, x0, y, x1, y + 5, LAND)
    # dashed leaders from each numbered dot to its small location dot
    for _num, (cx, cy), (sx, sy) in MAP_PINS:
        steps = 8
        for i in range(steps):
            if i % 2 == 0:
                px = cx + (sx - cx) * i // steps
                py = cy + (sy - cy) * i // steps
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=MAP_DOT)
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=MAP_DOT)
    # numbered dots: white ring, red disc, white number
    for num, (cx, cy), _ in MAP_PINS:
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=WHITE)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=MAP_DOT)
        centred_text(canvas, str(num), font(DJ_SANS_B, 10), WHITE, cx, cy - 5)
    place_text(canvas, "WHERE IT HAPPENED", font(DJ_SANS_B, 13), INK, 10, 648)
    place_text_box(
        canvas,
        "Red numbers mark stories 1\u201313. No. 4 is in space. Mercury.",
        font(DJ_SANS, 10),
        MUTE,
        10,
        892,
    )


# ---------------------------------------------------------------- also on saturday
ALSO_LEFT = [
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
    (24, "\u201935 by 35\u2019 goal enters the COP31 text (Reuters)"),
    (25, "M4.7 quake strikes northern Chile; no damage (USGS)"),
]
ALSO_RIGHT = [
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


def draw_also(canvas):
    place_text(
        canvas,
        "ALSO ON SATURDAY 21 NOVEMBER \u2014 23 MORE STORIES",
        font(DJ_SANS_B, 13),
        INK,
        412,
        648,
    )
    nf = font(DJ_SANS_B, 10)
    tf = font(DJ_SANS, 10)
    for col_x, items in ((412, ALSO_LEFT), (718, ALSO_RIGHT)):
        for i, (num, text) in enumerate(items):
            y = 668 + i * 20
            place_text_box(canvas, str(num), nf, MAP_GREEN, col_x, y)
            nox, _, nrx, _ = ink_box(str(num), nf)
            place_text_box(canvas, text, tf, INK, col_x + (nrx - nox) + 5, y)


# ---------------------------------------------------------------- clock + date check + footer
CLOCK_ITEMS = [
    ("00:09", "Peru quake strikes"),
    ("13:30", "Alcaraz faces Shelton in Turin"),
    ("18:24", "BepiColombo fires its thrusters"),
    ("19:30", "Medvedev meets Zverev in Turin"),
]

DATE_CHECK_TEXT = (
    "Left out as other days\u2019 news: Russian missiles in Poland (Fri 20 Nov) \u00b7 "
    "Kyiv\u2019s bridges hit (Fri 20 Nov) \u00b7 Cyclone Akvan (Fri 20 Nov) \u00b7 the "
    "World Court\u2019s Myanmar ruling (Thu 19 Nov) \u00b7 the Virginia measles death "
    "(Fri 20 Nov) \u00b7 Wall Street\u2019s correction (Fri 20 Nov) \u00b7 the Shenzhen "
    "summit (Thu 19 Nov) \u00b7 Anthropic\u2019s debut (Thu 19 Nov) \u00b7 the GTA VI "
    "launch (Thu 19 Nov) \u00b7 Starc\u2019s 7/58 \u2014 the 2025 Ashes, a year ago. "
    "Late-Friday events below are shown as first reported on Saturday."
)


def draw_clock(canvas):
    lab = "BY THE CLOCK \u00b7 UTC"
    lf = font(DJ_SANS_B, 11)
    place_text_box(canvas, lab, lf, INK, 11, 908)
    x = 11 + int(text_w(lab, lf)) + 7
    tf = font(DJ_SANS_B, 11)
    df = font(DJ_SANS, 11)
    for i, (tm, desc) in enumerate(CLOCK_ITEMS):
        if i > 0:
            place_text_box(canvas, "\u00b7", df, INK, x, 908)
            x += int(text_w("\u00b7", df)) + 11
        place_text_box(canvas, tm, tf, RED, x, 908)
        x += int(text_w(tm, tf)) + 4
        place_text_box(canvas, desc, df, INK, x, 908)
        x += int(text_w(desc, df)) + 11


def draw_date_check(canvas):
    rect(canvas, 10, 928, 1013, 929, RED)
    rect(canvas, 10, 997, 1013, 998, RED)
    rect(canvas, 10, 928, 11, 998, RED)
    rect(canvas, 1012, 928, 1013, 998, RED)
    place_text(canvas, "DATE CHECK", font(DJ_SANS_B, 11), RED, 19, 936)
    for i, line in enumerate(wrap_lines(DATE_CHECK_TEXT, font(DJ_SANS, 11), 905)):
        place_text_box(canvas, line, font(DJ_SANS, 11), INK, 103, 935 + i * 14)


def draw_footer(canvas):
    fnt = font(DJ_SANS, 10)
    place_text(
        canvas,
        "Every story here happened, or was first reported, on Saturday 21 November "
        "2026. Officials\u2019 counts are attributed.",
        fnt,
        MUTE,
        10,
        1005,
    )
    right = "Sources named beside each story \u00b7 original drawings"
    ox, oy, rx, _ = ink_box(right, fnt)
    w = rx - ox
    d = ImageDraw.Draw(canvas)
    d.text((1014 - w - ox, 1005 - oy), right, font=fnt, fill=MUTE)


def build_page():
    img = Image.new("RGB", (W, H), PAPER)
    draw_header(img)
    draw_stat_strip(img)
    draw_region_strip(img)
    draw_hero(img)
    draw_big_stories(img)
    draw_small_stories(img)
    draw_map(img)
    draw_also(img)
    draw_clock(img)
    draw_date_check(img)
    draw_footer(img)
    return img


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    page = build_page()
    page.save(out)
    print("wrote", out, page.size)
