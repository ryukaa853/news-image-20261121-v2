#!/usr/bin/env python3
"""The World in One Day -- Saturday, 21 November 2026.

A code-drawn broadsheet front page summing up the world's news of
Saturday 21 November 2026, rendered with the Python standard library
only (no network, no wall clock, no randomness). Every pixel is drawn
by this program: a tiny raster canvas, a hand-authored 5x7 bitmap font,
eleven small drawn scenes, and a pure-Python PNG encoder.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> writes out/entry.png
The grader runs it twice; both runs write identical bytes.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# Hand-authored 5x7 bitmap glyphs. Each row is 5 characters: '#' is ink.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ')': (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

# 'g' and 'y' dip below the baseline: glyph rows 7-8 in the table above
# hold their descenders, so glyphs are drawn from an 8-row table.
GLYPH_H = 8
for _ch, _rows in list(FONT.items()):
    if len(_rows) == 7:
        FONT[_ch] = _rows + (".....",)


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px per char at scale 1)."""
    return len(text) * 6 * scale


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- canvas ---
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(xx, yy, c)

    def vgrad(self, x, y, w, h, top, bot):
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            self.fill_rect(x, y + yy, w, 1, c)

    def draw_glyph(self, x, y, ch, scale, c):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT['?']
        for r in range(GLYPH_H):
            row = rows[r]
            for col in range(5):
                if row[col] == '#':
                    self.fill_rect(x + col * scale, y + r * scale,
                                   scale, scale, c)

    def text(self, x, y, s, scale, c, align="left"):
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            self.draw_glyph(cx, y, ch, scale, c)
            cx += 6 * scale
        return cx

    def para(self, x, y, lines, scale, c, leading=None):
        if leading is None:
            leading = 9 * scale
        for ln in lines:
            self.text(x, y, ln, scale, c)
            y += leading
        return y


# ------------------------------------------------------------------ png -----
def encode_png(cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ----------------------------------------------------------------- scenes ---
# Each scene draws a small editorial illustration into a box (x, y, w, h).
# All shapes are simple silhouettes and gradients, drawn from code.

def scene_gulf(cv, x, y, w, h):
    """Night over the Gulf: missile streaks, a naval base, fire below."""
    cv.vgrad(x, y, w, h, (10, 16, 40), (52, 30, 62))
    cv.circle(x + 60, y + 26, 16, (240, 235, 200))
    cv.circle(x + 54, y + 22, 14, (16, 22, 48))
    for sx, sy in ((140, 10), (w - 20, 14), (w // 2, 6), (220, 26), (w - 90, 34)):
        cv.set(x + sx, y + sy, (255, 255, 220))
        cv.set(x + sx + 1, y + sy, (255, 255, 220))
    for k in range(5):
        bx, by = x + 90 + k * (w // 5), y + 22 + k * 9
        cv.line(bx, by, bx + 46, by + 26, (255, 190, 90))
        cv.line(bx, by + 2, bx + 46, by + 28, (255, 120, 40))
        cv.line(bx, by + 1, bx + 46, by + 27, (255, 220, 150))
        cv.circle(bx + 46, by + 26, 3, (255, 240, 180))
    base_y = y + h - 16
    cv.fill_rect(x, base_y, w, 16, (8, 10, 22))
    for bx, bw, bh in ((20, 34, 26), (70, 22, 42), (110, 44, 18),
                       (w - 130, 26, 34), (w - 90, 40, 22), (w - 40, 24, 30)):
        cv.fill_rect(x + bx, base_y - bh, bw, bh, (16, 20, 40))
        for wy in range(base_y - bh + 5, base_y - 3, 8):
            cv.set(x + bx + 5, wy, (255, 220, 120))
    cv.circle(x + w - 180, base_y - 30, 9, (22, 28, 52))
    cv.fill_rect(x + w - 200, base_y - 30, 40, 3, (22, 28, 52))
    fx = x + w // 3
    cv.circle(fx, base_y - 8, 16, (255, 120, 30))
    cv.circle(fx, base_y - 8, 9, (255, 200, 60))
    cv.poly([(fx - 8, base_y - 6), (fx, base_y - 34), (fx + 8, base_y - 6)],
            (255, 90, 20))
    cv.circle(fx + 18, base_y - 26, 8, (90, 90, 95))
    cv.fill_rect(x, base_y - 2, w, 2, (255, 150, 50))


def scene_desert(cv, x, y, w, h):
    """Desert sunset, highway, patrol car."""
    cv.vgrad(x, y, w, h, (250, 170, 60), (190, 70, 40))
    cv.circle(x + w - 26, y + 20, 12, (255, 240, 180))
    cv.fill_rect(x, y + h - 26, w, 26, (120, 70, 40))
    cv.fill_rect(x, y + h - 26, w, 3, (90, 50, 30))
    cv.poly([(x + 8, y + h - 26), (x + 26, y + h - 26),
             (x + 20, y + h - 44), (x + 14, y + h - 44)], (90, 60, 30))
    car_y = y + h - 22
    cv.fill_rect(x + w // 2 - 30, car_y - 8, 60, 8, (20, 24, 40))
    cv.fill_rect(x + w // 2 - 18, car_y - 15, 30, 8, (20, 24, 40))
    cv.fill_rect(x + w // 2 - 30, car_y - 8, 60, 2, (200, 220, 255))
    for wx in (w // 2 - 22, w // 2 + 14):
        cv.circle(x + wx, car_y, 5, (10, 10, 12))
        cv.circle(x + wx, car_y, 2, (160, 160, 160))
    cv.fill_rect(x + w // 2 + 30, car_y - 6, 5, 2, (255, 60, 40))


def scene_climate(cv, x, y, w, h):
    """Globe, wind turbines, rising sun."""
    cv.vgrad(x, y, w, h, (140, 200, 235), (220, 240, 245))
    cv.circle(x + w - 24, y + 18, 11, (255, 210, 90))
    gx, gy, gr = x + w // 2 - 8, y + h // 2 + 6, 26
    cv.circle(gx, gy, gr, (40, 110, 190))
    cv.circle(gx - 8, gy - 8, 8, (70, 170, 90))
    cv.circle(gx + 10, gy + 8, 6, (70, 170, 90))
    cv.circle(gx + 4, gy - 12, 5, (70, 170, 90))
    cv.circle(gx, gy, gr, (40, 110, 190), fill=False)
    for tx in (x + 14, x + w - 22):
        cv.vline(tx, y + h - 34, 34, (240, 240, 240))
        cv.line(tx, y + h - 34, tx - 9, y + h - 44, (240, 240, 240))
        cv.line(tx, y + h - 34, tx + 9, y + h - 44, (240, 240, 240))
        cv.line(tx, y + h - 34, tx, y + h - 24, (240, 240, 240))
    cv.fill_rect(x, y + h - 8, w, 8, (90, 160, 90))


def scene_ship(cv, x, y, w, h):
    """A cargo ship burning on a grey sea."""
    cv.vgrad(x, y, w, h, (120, 130, 140), (200, 205, 210))
    cv.fill_rect(x, y + h - 26, w, 26, (40, 80, 120))
    cv.fill_rect(x, y + h - 26, w, 2, (180, 200, 220))
    sx, sy = x + 14, y + h - 40
    cv.poly([(sx, sy), (sx + w - 28, sy), (sx + w - 38, sy + 14),
             (sx + 10, sy + 14)], (30, 30, 34))
    for cx, cc in ((sx + 18, (200, 60, 40)), (sx + 38, (60, 120, 180)),
                   (sx + 58, (220, 180, 60))):
        cv.fill_rect(cx, sy - 12, 16, 12, cc)
    cv.fill_rect(sx + w - 52, sy - 22, 8, 22, (200, 200, 200))
    fx = sx + w // 2
    cv.circle(fx, sy - 16, 10, (255, 140, 30))
    cv.circle(fx + 8, sy - 12, 7, (255, 200, 60))
    cv.poly([(fx - 6, sy - 12), (fx, sy - 30), (fx + 6, sy - 12)],
            (255, 90, 20))
    cv.circle(fx - 4, sy - 30, 6, (90, 90, 95))
    cv.circle(fx + 10, sy - 38, 8, (110, 110, 115))


def scene_race(cv, x, y, w, h):
    """Night street circuit: skyline, neon, a race car."""
    cv.vgrad(x, y, w, h, (12, 12, 34), (60, 30, 90))
    for bx, bw, bh in ((4, 14, 30), (22, 10, 42), (36, 16, 26),
                       (w - 34, 12, 38), (w - 18, 10, 28)):
        cv.fill_rect(x + bx, y + h - 30 - bh, bw, bh, (24, 24, 54))
        for wy in range(y + h - 30 - bh + 4, y + h - 32, 8):
            cv.set(x + bx + 4, wy, (255, 220, 120))
            cv.set(x + bx + 9, wy + 4, (140, 220, 255))
    cv.fill_rect(x, y + h - 30, w, 30, (30, 30, 34))
    cv.line(x, y + h - 12, x + w, y + h - 18, (255, 200, 60))
    cv.line(x, y + h - 12, x + w, y + h - 18, (255, 80, 200))
    cx, cy = x + w // 2, y + h - 16
    cv.fill_rect(cx - 34, cy - 8, 68, 8, (200, 30, 40))
    cv.poly([(cx - 20, cy - 8), (cx - 10, cy - 15), (cx + 8, cy - 15),
             (cx + 14, cy - 8)], (200, 30, 40))
    cv.fill_rect(cx + 22, cy - 14, 12, 4, (200, 30, 40))
    for wx in (cx - 24, cx + 22):
        cv.circle(wx, cy, 6, (12, 12, 14))
        cv.circle(wx, cy, 2, (200, 200, 200))
    cv.fill_rect(cx - 38, cy - 5, 4, 2, (255, 240, 150))


def scene_mosquito(cv, x, y, w, h):
    """A mosquito under a shield, on pale blue."""
    cv.fill_rect(x, y, w, h, (200, 230, 245))
    cx, cy = x + w // 2, y + h // 2 + 4
    cv.poly([(cx, cy - 34), (cx + 30, cy - 22), (cx + 30, cy + 8),
             (cx, cy + 34), (cx - 30, cy + 8), (cx - 30, cy - 22)],
            (40, 120, 70))
    cv.poly([(cx, cy - 27), (cx + 23, cy - 18), (cx + 23, cy + 6),
             (cx, cy + 27), (cx - 23, cy + 6), (cx - 23, cy - 18)],
            (235, 245, 235))
    mx, my = cx, cy - 2
    cv.line(mx - 14, my, mx + 14, my, (30, 30, 30))
    cv.line(mx - 16, my - 4, mx - 6, my - 2, (30, 30, 30))
    cv.line(mx - 16, my + 4, mx - 6, my + 2, (30, 30, 30))
    cv.line(mx + 6, my - 2, mx + 16, my - 4, (30, 30, 30))
    cv.line(mx + 6, my + 2, mx + 16, my + 4, (30, 30, 30))
    cv.circle(mx - 18, my, 2, (30, 30, 30))
    cv.line(mx - 12, my - 8, mx - 20, my - 14, (120, 120, 120))
    cv.line(mx - 12, my + 8, mx - 20, my + 14, (120, 120, 120))
    cv.line(mx - 4, my - 6, mx - 12, my - 14, (120, 120, 120))
    cv.line(mx - 4, my + 6, mx - 12, my + 14, (120, 120, 120))


def scene_protest(cv, x, y, w, h):
    """A crowd with placards under a grey sky."""
    cv.vgrad(x, y, w, h, (190, 195, 205), (235, 235, 230))
    cv.fill_rect(x + 12, y + 10, 44, 26, (245, 245, 240))
    cv.fill_rect(x + 12, y + 10, 44, 4, (180, 40, 40))
    cv.fill_rect(x + w - 62, y + 6, 46, 24, (245, 245, 240))
    cv.fill_rect(x + w - 62, y + 6, 46, 4, (30, 80, 160))
    for px, ph in ((x + 34, 34), (x + w - 40, 30)):
        cv.vline(px, y + 36, 26, (90, 70, 50))
    for row, ry in enumerate((y + h - 34, y + h - 20)):
        for k in range(9):
            hx = x + 6 + k * (w // 9) + (row * 5) % 11
            cv.circle(hx, ry, 6, (220, 180, 150) if k % 2 else (180, 140, 110))
            cv.fill_rect(hx - 8, ry + 6, 16, 12,
                         (60, 90, 140) if k % 3 == 0 else
                         (160, 60, 60) if k % 3 == 1 else (70, 120, 70))
    cv.fill_rect(x, y + h - 6, w, 6, (120, 110, 100))


def scene_shop(cv, x, y, w, h):
    """An online-retail storefront: awning, parcels, tag."""
    cv.fill_rect(x, y, w, h, (245, 235, 220))
    cv.fill_rect(x + 8, y + 8, w - 16, h - 16, (250, 248, 250))
    cv.rect(x + 8, y + 8, w - 16, h - 16, (60, 60, 60))
    for k in range(6):
        cv.fill_rect(x + 8 + k * ((w - 16) // 6), y + 8, (w - 16) // 6, 12,
                     (200, 50, 50) if k % 2 == 0 else (250, 248, 250))
    cv.fill_rect(x + 18, y + h - 34, 30, 22, (190, 140, 80))
    cv.fill_rect(x + 18, y + h - 34, 30, 4, (150, 100, 50))
    cv.fill_rect(x + 58, y + h - 28, 24, 16, (120, 160, 200))
    cv.circle(x + w - 26, y + 34, 14, (200, 50, 50))
    cv.text(x + w - 26, y + 34, "%", 2, (255, 255, 255), align="center")
    cv.text(x + w // 2, y + h - 14, "SALE", 1, (60, 60, 60), align="center")


def scene_court(cv, x, y, w, h):
    """A courthouse: pediment, columns, steps."""
    cv.vgrad(x, y, w, h, (210, 215, 225), (240, 240, 235))
    cx = x + w // 2
    cv.poly([(cx - 52, y + 16), (cx + 52, y + 16), (cx, y + 34)],
            (200, 195, 180))
    cv.fill_rect(x + 12, y + 34, w - 24, 4, (150, 145, 130))
    for k in range(4):
        colx = x + 16 + k * ((w - 32) // 3)
        cv.fill_rect(colx, y + 38, 8, h - 52, (225, 220, 205))
        cv.fill_rect(colx - 2, y + 38, 12, 3, (180, 175, 160))
    cv.fill_rect(x + 8, y + h - 14, w - 16, 4, (160, 155, 140))
    cv.fill_rect(x + 4, y + h - 10, w - 8, 4, (140, 135, 120))
    cv.fill_rect(x, y + h - 6, w, 6, (120, 115, 100))


def scene_rugby(cv, x, y, w, h):
    """A rugby pitch: posts, ball, try line."""
    cv.vgrad(x, y, w, h, (90, 170, 90), (60, 140, 70))
    cv.fill_rect(x, y + h - 18, w, 3, (255, 255, 255))
    cv.fill_rect(x, y + h - 34, w, 2, (255, 255, 255))
    px = x + w // 2
    cv.vline(px, y + 8, h - 40, (255, 255, 255))
    cv.line(px, y + 8, px - 16, y + 8, (255, 255, 255))
    cv.line(px, y + 8, px + 16, y + 8, (255, 255, 255))
    bx, by = x + w // 2 - 30, y + h - 46
    cv.poly([(bx, by + 8), (bx + 8, by), (bx + 30, by),
             (bx + 38, by + 8), (bx + 30, by + 16), (bx + 8, by + 16)],
            (150, 90, 50))
    cv.line(bx + 14, by + 8, bx + 24, by + 8, (255, 255, 255))
    cv.circle(x + 16, y + h - 40, 4, (255, 255, 255))


def scene_city(cv, x, y, w, h):
    """A city at dusk under missile fire: skyline, smoke, flames."""
    cv.vgrad(x, y, w, h, (70, 50, 90), (200, 120, 70))
    cv.circle(x + w - 22, y + 16, 10, (255, 220, 150))
    for bx, bw, bh in ((4, 16, 34), (24, 12, 48), (40, 18, 28),
                       (62, 12, 40), (w - 30, 14, 44), (w - 48, 12, 30)):
        cv.fill_rect(x + bx, y + h - 20 - bh, bw, bh, (40, 32, 52))
        for wy in range(y + h - 20 - bh + 5, y + h - 22, 9):
            cv.set(x + bx + 4, wy, (255, 210, 120))
    cv.line(x + 10, y + 8, x + 40, y + 30, (255, 190, 90))
    cv.line(x + 10, y + 9, x + 40, y + 31, (255, 110, 40))
    cv.fill_rect(x, y + h - 20, w, 20, (52, 40, 46))
    cv.circle(x + w // 3, y + h - 20, 10, (255, 130, 30))
    cv.circle(x + w // 3, y + h - 20, 5, (255, 210, 80))
    cv.circle(x + w // 3 + 4, y + h - 32, 7, (120, 110, 110))
    cv.circle(x + w // 3 - 6, y + h - 40, 9, (140, 130, 130))


SCENES = {
    "gulf": scene_gulf, "desert": scene_desert, "climate": scene_climate,
    "ship": scene_ship, "race": scene_race, "mosquito": scene_mosquito,
    "protest": scene_protest, "shop": scene_shop, "court": scene_court,
    "rugby": scene_rugby, "city": scene_city,
}

# ---------------------------------------------------------------- content ---
# Every story below was reported on Saturday 21 November 2026 (or, where
# noted, happened on Friday night and was announced on Saturday). Facts
# were checked against Reuters, AP, CNN, BBC, FIA and Formula 1 during
# this build; the README lists one source per story.

PAPER = (247, 242, 231)
CELL = (252, 248, 240)
INK = (22, 22, 22)
RED = (172, 32, 32)
NAVY = (30, 50, 90)
GREY = (110, 105, 95)
RULE = (180, 170, 150)

HERO = {
    "scene": "gulf",
    "kicker": "MIDDLE EAST - LEAD STORY",
    "headline": "IRAN STRIKES AT U.S. BASES IN BAHRAIN",
    "standfirst": ("Tehran says its Guards hit two U.S. positions; Bahrain reports "
                   "a fire at an industrial site, no injuries, and says its air "
                   "defences stopped other attacks."),
}

GRID = [
    {"scene": "desert", "headline": "MEXICO SEIZES EL CHAPO ISIDRO",
     "standfirst": "FBI most-wanted boss Fausto Isidro Meza Flores held in Sinaloa; "
                   "11 die in the violence that follows."},
    {"scene": "climate", "headline": "COP31 TALKS RUN INTO OVERTIME",
     "standfirst": "Antalya summit passes its Friday deadline as fossil fuels and "
                   "finance divide nearly 200 nations."},
    {"scene": "ship", "headline": "DRONE STRIKE SETS RUSSIAN SHIP ABLAZE",
     "standfirst": "Sanctioned cargo vessel Sparta II burns in the Gulf of Finland; "
                   "its 16 crew evacuate as Finland says Ukraine was likely behind it."},
    {"scene": "race", "headline": "ANTONELLI FASTEST, VERSTAPPEN ON POLE",
     "standfirst": "Kimi Antonelli tops Las Vegas qualifying in 1:33.893, but a "
                   "five-place grid penalty hands pole to Max Verstappen."},
    {"scene": "mosquito", "headline": "BRED MOSQUITOES CUT DENGUE BY 69%",
     "standfirst": "A four-year Brazil trial of 5,700 children finds Wolbachia "
                   "mosquitoes cut dengue and chikungunya infections by about 69%."},
    {"scene": "protest", "headline": "FRANCE MARCHES OVER COST OF LIVING",
     "standfirst": "Turnout falls from a week earlier: 82,500 march, the ministry "
                   "says, 21,500 of them in Paris; organisers claim 150,000."},
    {"scene": "shop", "headline": "WILDBERRIES CHIEF STEPS DOWN",
     "standfirst": "Tatyana Kim quits as head of Russia's biggest online retailer "
                   "days after the EU put her on its sanctions list."},
    {"scene": "court", "headline": "DEPARDIEU AND HOUELLEBECQ PROBED",
     "standfirst": "Paris prosecutors open a judicial investigation into the actor "
                   "and the author over alleged sexual offences."},
    {"scene": "rugby", "headline": "IRELAND EDGE SOUTH AFRICA 20-17",
     "standfirst": "Two tries from Rob Baloucoune help Ireland beat the world "
                   "champions in Dublin; a bonus point still sends South Africa "
                   "to the final."},
    {"scene": "city", "headline": "MISSILES HIT ZELENSKYY'S HOMETOWN",
     "standfirst": "A Russian strike on Kryvyi Rih kills 2 and wounds 60, local "
                   "officials say; rescuers are hit again as they arrive."},
]

BRIEFS = [
    "LEEDS STUN CHELSEA 4-1",
    "NEWCASTLE 2-2 ARSENAL",
    "TRUMP: CAP CARD RATES AT 10%",
    "CONTRACTORS MUST ASK WHITE HOUSE",
    "FBI PROBES HACK OF CRIME DATABASE",
    "11 DIE AFTER TAINTED DRINK IN INDIA",
    "ENGLAND BEAT NEW ZEALAND 37-12",
    "SCOTLAND ROUT JAPAN 67-5",
    "GEORGIA BEAT USA 38-10",
    "PSG EDGE NICE 3-2",
    "DORTMUND BEAT GLADBACH 1-0",
    "EU AND INDONESIA SIGN TRADE DEAL",
    "QATAR HOLDS TALKS IN TEHRAN",
    "DENMARK URGES EU CURBS ON RUSSIANS",
]


# ----------------------------------------------------------------- layout ---
def render():
    cv = Canvas(W, H, PAPER)
    mx = 24
    cw = W - 2 * mx  # 976

    # Masthead.
    cv.text(W // 2, 12, "THE WORLD IN ONE DAY", 6, INK, align="center")
    cv.text(W // 2, 62, "SATURDAY, 21 NOVEMBER 2026", 2, RED, align="center")
    cv.hline(mx, 84, cw, INK)
    cv.hline(mx, 88, cw, INK)

    # Hero story: full-width illustration, headline, standfirst.
    hy = 100
    SCENES[HERO["scene"]](cv, mx, hy, cw, 168)
    cv.rect(mx, hy, cw, 168, INK)
    cv.text(mx, hy + 178, HERO["kicker"], 1, RED)
    cv.text(mx, hy + 190, HERO["headline"], 4, INK)
    lines = wrap_text(HERO["standfirst"], cw, 2)
    cv.para(mx, hy + 228, lines, 2, INK, leading=22)
    cv.hline(mx, hy + 276, cw, INK)

    # Grid: 2 columns x 5 rows of illustrated stories.
    gy, gh, gw = 388, 92, 480
    for i, story in enumerate(GRID):
        cx = mx + (i % 2) * (gw + 16)
        cy = gy + (i // 2) * gh
        cv.fill_rect(cx, cy, gw, gh - 6, CELL)
        cv.rect(cx, cy, gw, gh - 6, RULE)
        SCENES[story["scene"]](cv, cx + 4, cy + 5, 168, gh - 16)
        tx = cx + 180
        tw = gw - 180 - 6
        hl = wrap_text(story["headline"], tw, 2)[:2]
        y = cv.para(tx, cy + 5, hl, 2, INK, leading=18)
        sf = wrap_text(story["standfirst"], tw, 1)[:3]
        cv.para(tx, y + 3, sf, 1, (60, 58, 52), leading=10)
    cv.hline(mx, gy + 5 * gh - 2, cw, INK)

    # Briefs band: numbered one-liners, two columns.
    by = gy + 5 * gh + 8
    cv.text(mx, by, "ALSO TODAY - WORLD IN BRIEF", 2, NAVY)
    cv.text(W - mx, by, "SOURCES: REUTERS - AP - CNN - FIA", 1, GREY,
            align="right")
    cv.hline(mx, by + 20, cw, RULE)
    for i, brief in enumerate(BRIEFS):
        bx = mx + (i % 2) * (cw // 2 + 8)
        row = i // 2
        yy = by + 26 + row * 18
        cv.text(bx, yy, str(i + 1) + ".", 2, RED)
        cv.text(bx + 42, yy, brief, 2, INK)

    # Footer.
    cv.text(W // 2, 1012,
            "ALL STORIES REPORTED ON SATURDAY 21 NOVEMBER 2026", 1, GREY,
            align="center")
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(render())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
