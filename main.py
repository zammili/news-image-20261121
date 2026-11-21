#!/usr/bin/env python3
# THE DAILY LEDGER - a one-image front page summing up Saturday 21 November 2026.
# Original editorial illustration drawn entirely in code (pure stdlib):
# a night-sky scene of the missile barrage over the Ukraine-Poland border,
# set as a newspaper front page with the day's other leading stories.
# Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). Deterministic.

import os
import struct
import zlib

W, H = 1024, 768

# ---------------------------------------------------------------- palette
PAPER = (246, 239, 222)
INK = (24, 20, 16)
RED = (168, 32, 24)
GRAY = (96, 90, 80)
WHITE = (250, 247, 238)

# ---------------------------------------------------------------- 5x7 font
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "+": (".....", "..#..", "..#..", ".####", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return self.px[i], self.px[i + 1], self.px[i + 2]

    def blend(self, x, y, c, a):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            for k in range(3):
                self.px[i + k] = int(self.px[i + k] * (1 - a) + c[k] * a)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                base = yy * self.w
                for xx in range(max(0, x), min(self.w, x + w)):
                    i = (base + xx) * 3
                    self.px[i:i + 3] = bytes(c)

    def outline(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = t // 2
        for s in range(steps + 1):
            x = x0 + dx * s // steps
            y = y0 + dy * s // steps
            self.rect(x - r, y - r, t, t, c)

    def circle(self, cx, cy, r, c, blend_a=None):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    if blend_a is None:
                        self.set(xx, yy, c)
                    else:
                        self.blend(xx, yy, c, blend_a)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, c)


class Lcg:
    """Deterministic pseudo-random source (fixed seed -> same image)."""

    def __init__(self, seed):
        self.s = seed

    def next(self, mod):
        self.s = (self.s * 1103515245 + 12345) & 0x7FFFFFFF
        return self.s % mod


# ---------------------------------------------------------------- text
def text_width(s, scale, spacing=1):
    if not s:
        return 0
    return (len(s) - 1) * (5 + spacing) * scale + 5 * scale


def draw_text(cv, x, y, s, scale, c, bold=False, spacing=1):
    adv = (5 + spacing) * scale
    off = max(1, scale // 2) if bold else 0
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if g[row][col] == "#":
                    cv.rect(x + col * scale, y + row * scale, scale, scale, c)
                    if bold:
                        cv.rect(x + col * scale + off, y + row * scale,
                                scale, scale, c)
        x += adv
    return x


def draw_text_right(cv, xr, y, s, scale, c, bold=False, spacing=1):
    return draw_text(cv, xr - text_width(s, scale, spacing), y, s, scale, c,
                     bold, spacing)


def draw_text_center(cv, cx, y, s, scale, c, bold=False, spacing=1):
    return draw_text(cv, cx - text_width(s, scale, spacing) // 2, y, s, scale,
                     c, bold, spacing)


# ---------------------------------------------------------------- scene
def draw_night_panel(cv, x0, y0, w, h):
    """Night sky over the Ukraine-Poland border: missile trails, bursts,
    silhouetted rooftops, a dashed border with a fallen missile on the
    Polish side."""
    rng = Lcg(20261121)
    # sky gradient
    top, bot = (9, 13, 33), (30, 36, 62)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        cv.rect(x0, y0 + yy, w, 1, c)
    # stars
    for _ in range(110):
        sx = x0 + rng.next(w)
        sy = y0 + rng.next(h - 70)
        b = 120 + rng.next(120)
        cv.set(sx, sy, (b, b, b + 20))
        if rng.next(4) == 0:
            cv.set(sx + 1, sy, (b // 2, b // 2, b // 2 + 10))
    horizon = y0 + h - 46
    # distant fires' glow on the Ukrainian side
    for gx, gr in ((x0 + 120, 60), (x0 + 250, 44)):
        for r in range(gr, 0, -6):
            cv.circle(gx, horizon - 6, r, (255, 120, 30), blend_a=0.05)
    border_x = x0 + 402
    # missile trails: quadratic beziers from upper right down to the city
    def bez(p0, p1, p2, col, thick):
        steps = 260
        for i in range(steps + 1):
            t = i / steps
            x = int((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0])
            y = int((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            cv.rect(x - thick // 2, y - thick // 2, thick, thick, col)
            if i % 6 == 0:  # smoky, broken trail
                cv.blend(x + rng.next(5) - 2, y - 2, (170, 170, 180), 0.35)
        return p2

    smoke = (196, 198, 205)
    fire = (255, 176, 66)
    impacts = []
    trails = [
        ((x0 + 560, y0 + 8), (x0 + 470, y0 + 60), (x0 + 128, horizon - 4)),
        ((x0 + 520, y0 + 4), (x0 + 400, y0 + 44), (x0 + 252, horizon - 4)),
        ((x0 + 584, y0 + 30), (x0 + 520, y0 + 96), (x0 + 330, horizon - 6)),
    ]
    for p0, p1, p2 in trails:
        bez(p0, p1, p2, smoke, 3)
        end = bez(p0, p1, p2, fire, 1)
        cv.circle(end[0], end[1], 7, (255, 150, 50), blend_a=0.35)
        cv.circle(end[0], end[1], 4, (255, 220, 130))
        impacts.append(end)
    # explosion bursts at the impact points
    def burst(cx, cy, r_out, r_in, col):
        import math
        pts = []
        for i in range(16):
            ang = math.pi * i / 8
            r = r_out if i % 2 == 0 else r_in
            pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
        cv.poly(pts, col)

    for ix, iy in impacts[:2]:
        burst(ix, iy - 6, 17, 6, (238, 92, 26))
        burst(ix, iy - 6, 10, 4, (255, 178, 64))
        cv.circle(ix, iy - 6, 3, (255, 240, 200))
    ix, iy = impacts[2]
    burst(ix, iy - 4, 12, 5, (238, 92, 26))
    burst(ix, iy - 4, 7, 3, (255, 178, 64))
    # rooftops silhouette
    roof = (5, 6, 10)
    houses = [(0, 66, 26), (64, 52, 20), (118, 78, 30), (196, 58, 22),
              (256, 84, 28), (342, 60, 24), (404, 72, 26), (478, 56, 20),
              (536, 50, 24)]
    for hx, hw, hh in houses:
        bx = x0 + hx
        cv.rect(bx, horizon + 46 - hh, hw, hh, roof)
        cv.poly([(bx - 4, horizon + 46 - hh), (bx + hw // 2, horizon + 22 - hh),
                 (bx + hw + 4, horizon + 46 - hh)], roof)
        if hw > 56:
            cv.rect(bx + hw - 14, horizon + 30 - hh, 7, 12, roof)
    cv.rect(x0, horizon + 40, w, h - (horizon - y0) - 40, roof)
    # a few lit windows
    for wx, wy in ((x0 + 84, horizon + 22), (x0 + 150, horizon + 28),
                   (x0 + 300, horizon + 24), (x0 + 452, horizon + 26),
                   (x0 + 520, horizon + 30)):
        cv.rect(wx, wy, 5, 7, (255, 205, 92))
    # the border: dashed line, labels, fallen missile on the Polish side
    for yy in range(y0 + 26, horizon + 38, 12):
        cv.rect(border_x, yy, 3, 7, (240, 240, 240))
    draw_text(cv, x0 + 12, y0 + 10, "UKRAINE", 2, (235, 235, 245), bold=True)
    draw_text(cv, border_x + 12, y0 + 10, "POLAND", 2, (235, 235, 245),
              bold=True)
    # NATO four-point star beside the Poland label
    sx, sy = border_x + 112, y0 + 16
    cv.poly([(sx, sy - 8), (sx + 2, sy - 2), (sx + 8, sy), (sx + 2, sy + 2),
             (sx, sy + 8), (sx - 2, sy + 2), (sx - 8, sy), (sx - 2, sy - 2)],
            (240, 240, 240))
    # fallen missile on the Polish side: bright wreck, glow, smoke, crater
    mx, my = border_x + 92, horizon + 30
    cv.circle(mx + 26, my - 8, 13, (255, 130, 40), blend_a=0.30)
    cv.line(mx, my, mx + 40, my - 20, (228, 231, 236), 6)
    cv.line(mx, my, mx - 10, my + 8, (228, 231, 236), 5)
    cv.line(mx + 5, my - 3, mx - 5, my - 15, (228, 231, 236), 5)
    cv.poly([(mx + 40, my - 20), (mx + 50, my - 24), (mx + 44, my - 13)],
            (228, 231, 236))
    for i in range(9):  # smoke plume drifting up from the wreck
        cv.circle(mx + 30 + rng.next(9) - 4, my - 16 - i * 4, 3,
                  (150, 150, 158), blend_a=0.5)
    for dx in range(-20, 21):  # crater lip and scattered debris
        cv.set(mx + 16 + dx, horizon + 42 - abs(dx) // 5, (140, 130, 112))
        if dx % 4 == 0:
            cv.set(mx + 16 + dx * 2, horizon + 44, (140, 130, 112))
    cv.outline(x0, y0, w, h, INK, 3)


# ---------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    rng = Lcg(7)
    # faint paper speckle, deterministic
    for _ in range(2600):
        x, y = rng.next(W), rng.next(H)
        r, g, b = cv.get(x, y)
        d = rng.next(7) - 3
        cv.set(x, y, (r + d, g + d, b + d))

    # masthead
    cv.rect(28, 14, 968, 3, INK)
    cv.rect(28, 20, 968, 1, INK)
    draw_text_center(cv, W // 2, 28, "THE DAILY LEDGER", 9, INK, bold=True)
    cv.rect(28, 99, 968, 1, INK)
    # dateline bar
    cv.rect(28, 106, 968, 28, INK)
    draw_text(cv, 42, 113, "SATURDAY 21 NOVEMBER 2026", 2, WHITE, bold=True)
    draw_text_center(cv, W // 2, 113, "THE WORLD IN ONE PICTURE", 2, WHITE)
    draw_text_right(cv, 982, 113, "LATE EDITION", 2, WHITE, bold=True)
    # kicker
    draw_text(cv, 28, 148, "WAR IN EUROPE", 2, RED, bold=True)
    draw_text_right(cv, 996, 148, "KYIV - WARSAW - THE HAGUE - NEW YORK", 2,
                    GRAY)
    # lead headline
    draw_text(cv, 28, 170, "POLAND HIT BY", 9, INK, bold=True)
    draw_text(cv, 28, 241, "RUSSIAN MISSILES", 9, INK, bold=True)
    cv.rect(28, 314, 968, 4, RED)
    # lead picture + standfirst
    draw_night_panel(cv, 28, 326, 588, 192)
    draw_text(cv, 28, 526, "MISSILE TRAILS ARC OVER KYIV IN THE NIGHT'S "
              "BARRAGE - TWO MISSILES AND A", 1, GRAY)
    draw_text(cv, 28, 536, "DRONE CAME DOWN ON POLISH SOIL, ON NATO'S "
              "EASTERN FLANK.", 1, GRAY)
    sx = 640
    lead = [
        "RUSSIA FIRED 400+ DRONES",
        "AND 110 MISSILES AT",
        "UKRAINE OVERNIGHT - ONE",
        "OF ITS BIGGEST BARRAGES",
        "OF THE WAR. EIGHT DIED",
        "IN KYIV; BRIDGES HIT.",
        "",
        "TWO MISSILES AND A DRONE",
        "CAME DOWN IN POLAND. PM",
        "TUSK: A 'DELIBERATE",
        "PROVOCATION'. NATO",
        "SCRAMBLED ITS JETS.",
    ]
    for i, ln in enumerate(lead):
        if ln:
            draw_text(cv, sx, 328 + i * 16, ln, 2, INK)
    cv.rect(28, 556, 968, 2, INK)
    # three columns
    cols = [
        (28, "MARKETS - NEW YORK", "AI ROUT: WALL ST",
         "IN CORRECTION",
         ["S&P 500 FELL 3.7% AS AI",
          "STOCKS SOLD OFF; THE",
          "NASDAQ'S 2026 GAINS ARE",
          "GONE. NIKKEI -5%."]),
        (356, "JUSTICE - THE HAGUE", "GENOCIDE VERDICT",
         "AGAINST MYANMAR",
         ["FIRST-EVER ICJ VERDICT",
          "HOLDING A STATE GUILTY",
          "OF GENOCIDE. BRITAIN",
          "EXPELS MYANMAR ENVOY."]),
        (684, "DIPLOMACY - BERLIN", "EUROPE REJECTS A",
         "'NEW YALTA'",
         ["AFTER SHENZHEN SUMMIT,",
          "MERZ: NO CARVE-UP OF",
          "EUROPE. ZELENSKY ON",
          "PUTIN: 'HE'S A KILLER.'"]),
    ]
    for cx, label, h1, h2, body in cols:
        draw_text(cv, cx, 570, label, 2, RED, bold=True)
        draw_text(cv, cx, 592, h1, 3, INK, bold=True)
        draw_text(cv, cx, 617, h2, 3, INK, bold=True)
        for i, ln in enumerate(body):
            draw_text(cv, cx, 646 + i * 15, ln, 2, INK)
    cv.rect(348, 570, 1, 132, GRAY)
    cv.rect(676, 570, 1, 132, GRAY)
    # ticker
    cv.rect(28, 712, 968, 36, INK)
    draw_text(cv, 40, 719,
              "ALSO TODAY: COP31 CLIMATE TALKS DEADLOCKED IN ANTALYA - "
              "DRAFT DEAL SILENT ON FOSSIL FUELS", 1, WHITE)
    draw_text(cv, 40, 732,
              "CANCER PILL CLEARS TUMOURS IN 1 IN 12 PATIENTS - BEPICOLOMBO "
              "ORBITS MERCURY AFTER 8 YEARS - M6.7 QUAKE IN PERU", 1, WHITE)
    draw_text_center(cv, W // 2, 754,
                     "AN ORIGINAL ILLUSTRATION DRAWN IN CODE - NO PHOTOGRAPHS",
                     1, GRAY)
    return cv


def write_png(cv, path):
    raw = bytearray()
    row = bytes(cv.px[:0])
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    del row

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    n = write_png(build(), os.path.join(out_dir, "entry.png"))
    print("wrote entry.png", n, "bytes")


if __name__ == "__main__":
    main()
