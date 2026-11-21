#!/usr/bin/env python3
"""News image: one image summing up the world news of Friday 20 November 2026.

Draws a 1024x1024 newspaper-style front page in pure stdlib Python
(zlib + struct PNG encoder, 5x7 bitmap font, procedural icons) and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Deterministic: no randomness, no clock, no network. Two runs write the
same bytes. Only verified stories of 20 November 2026 are shown.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 247, 240)
INK = (26, 26, 26)
BODY = (68, 68, 68)
NAVY = (22, 35, 63)
CREAM = (245, 238, 218)
RED = (179, 35, 27)
RULE = (200, 192, 178)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 chars, '#' = on, '.' = off.
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
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", ".##.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", ".##.."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}

# ---------------------------------------------------------------- framebuffer
buf = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = color
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = r, g, b


def line(x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, color):
    x, y, d = 0, r, 3 - 2 * r
    while y >= x:
        for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                       (x, -y), (y, -x), (-x, -y), (-y, -x)):
            px(cx + sx, cy + sy, color)
        x += 1
        if d > 0:
            y -= 1
            d += 4 * (x - y) + 10
        else:
            d += 4 * x + 6


def filled_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cx, y, s, scale, color):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    """Greedy word wrap to lines no wider than max_w px."""
    words = s.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
# Each icon draws inside a 100x100 box at (x, y) in one accent color.


def icon_bridge(x, y, c):
    # deck
    fill_rect(x + 6, y + 58, 88, 5, c)
    # towers
    fill_rect(x + 18, y + 22, 6, 42, c)
    fill_rect(x + 76, y + 22, 6, 42, c)
    # cables
    line(x + 21, y + 24, x + 50, y + 58, c)
    line(x + 79, y + 24, x + 50, y + 58, c)
    line(x + 21, y + 24, x + 8, y + 58, c)
    line(x + 79, y + 24, x + 92, y + 58, c)
    # blast marks above deck
    fill_rect(x + 44, y + 40, 4, 4, c)
    fill_rect(x + 56, y + 34, 4, 4, c)
    # water
    line(x + 6, y + 74, x + 94, y + 74, c)
    line(x + 16, y + 82, x + 84, y + 82, c)


def icon_tanker(x, y, c):
    # hull
    fill_rect(x + 10, y + 58, 76, 16, c)
    fill_rect(x + 86, y + 62, 8, 12, c)
    # deckhouse + stack
    fill_rect(x + 16, y + 42, 18, 16, c)
    fill_rect(x + 66, y + 36, 10, 22, c)
    # smoke
    filled_circle(x + 71, y + 28, 5, c)
    filled_circle(x + 78, y + 20, 4, c)
    # waves
    line(x + 6, y + 82, x + 30, y + 82, c)
    line(x + 38, y + 82, x + 62, y + 82, c)
    line(x + 70, y + 82, x + 94, y + 82, c)
    line(x + 16, y + 90, x + 84, y + 90, c)


def icon_chart_up(x, y, c):
    line(x + 14, y + 86, x + 14, y + 18, c)
    line(x + 14, y + 86, x + 90, y + 86, c)
    pts = [(18, 76), (34, 66), (48, 70), (64, 48), (80, 30)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(x + ax, y + ay, x + bx, y + by, c)
    line(x + 80, y + 30, x + 72, y + 32, c)
    line(x + 80, y + 30, x + 78, y + 40, c)
    fill_rect(x + 76, y + 26, 4, 4, c)


def icon_chart_down(x, y, c):
    line(x + 14, y + 86, x + 14, y + 18, c)
    line(x + 14, y + 86, x + 90, y + 86, c)
    pts = [(18, 30), (34, 40), (48, 36), (64, 58), (80, 76)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(x + ax, y + ay, x + bx, y + by, c)
    line(x + 80, y + 76, x + 72, y + 74, c)
    line(x + 80, y + 76, x + 78, y + 66, c)
    fill_rect(x + 76, y + 72, 4, 4, c)


def icon_globe(x, y, c):
    circle(x + 50, y + 50, 32, c)
    line(x + 18, y + 50, x + 82, y + 50, c)
    line(x + 24, y + 34, x + 76, y + 34, c)
    line(x + 24, y + 66, x + 76, y + 66, c)
    # longitude ellipse (approx with two arcs of lines)
    for t in range(0, 33):
        yy = y + 18 + t
        dx = int(10 * (1 - ((t - 16) / 16.0) ** 2) ** 0.5) if abs(t - 16) < 16 else 0
        px(x + 50 - dx, yy, c)
        px(x + 50 + dx, yy, c)


def icon_chip(x, y, c):
    fill_rect(x + 30, y + 30, 40, 40, c)
    fill_rect(x + 40, y + 40, 20, 20, PAPER)
    fill_rect(x + 46, y + 46, 8, 8, c)
    for i in range(4):
        off = 34 + i * 11
        fill_rect(x + off, y + 18, 4, 12, c)
        fill_rect(x + off, y + 70, 4, 12, c)
        fill_rect(x + 18, y + off, 12, 4, c)
        fill_rect(x + 70, y + off, 12, 4, c)


# ---------------------------------------------------------------- stories
# (headline, summary, icon, accent color)
STORIES = [
    ("RUSSIA STRIKES KYIV BRIDGES",
     "400+ drones and 110 missiles hit Ukraine; 3 bridges over the Dnipro struck, 8 killed; missiles also fell in Poland.",
     icon_bridge, (179, 35, 27)),
    ("HORMUZ BLOCKADE DEEPENS",
     "US Navy blocks Iranian shipping; tankers catch fire. The IEA calls it the largest energy shock on record.",
     icon_tanker, (196, 110, 20)),
    ("ANTHROPIC IPO SOARS 17%",
     "Debuts on Nasdaq, closing 17% above its $83 IPO price; $81.3B raised, the largest IPO on record.",
     icon_chart_up, (34, 120, 70)),
    ("MARKETS FALL FOR 6TH DAY",
     "US stocks fall a sixth straight day as the AI trade unwinds; Bitcoin drops near $61,700.",
     icon_chart_down, (40, 80, 160)),
    ("COP31 DEADLOCK IN ANTALYA",
     "Climate summit runs past its deadline; activists protest a draft deal that omits fossil fuels.",
     icon_globe, (20, 120, 110)),
    ("CHIP CURBS HIT CHINA SALES",
     "TSMC and Samsung pause advanced chip sales to China after new US export curbs.",
     icon_chip, (110, 70, 150)),
]

# ---------------------------------------------------------------- layout
fill_rect(0, 0, W, H, PAPER)

# Header band
fill_rect(0, 0, W, 132, NAVY)
draw_text_centered(W // 2, 18, "FRIDAY  -  THE WORLD IN BRIEF", 2, CREAM)
draw_text_centered(W // 2, 48, "20 NOVEMBER 2026", 8, CREAM)
fill_rect(0, 132, W, 6, RED)

# Story rows: 6 rows, each 138 tall, starting at y=138
ROW_H = 138
TOP = 138
for i, (head, summary, icon, accent) in enumerate(STORIES):
    y0 = TOP + i * ROW_H
    # icon disc
    filled_circle(96, y0 + ROW_H // 2, 52, (238, 232, 220))
    circle(96, y0 + ROW_H // 2, 52, RULE)
    icon(96 - 50, y0 + ROW_H // 2 - 50, accent)
    # headline
    draw_text(176, y0 + 16, head, 4, INK)
    # red underline under headline
    fill_rect(176, y0 + 16 + 32, 64, 4, accent)
    # summary, wrapped to 3 lines (nothing cut off mid-sentence)
    lines = wrap(summary, 1024 - 176 - 40, 3)
    ly = y0 + 58
    for ln in lines[:3]:
        draw_text(176, ly, ln, 3, BODY)
        ly += 24
    # rule between rows
    if i < len(STORIES) - 1:
        fill_rect(40, y0 + ROW_H - 1, W - 80, 1, RULE)

# Footer
fill_rect(0, 966, W, 58, NAVY)
draw_text_centered(W // 2, 984, "COMPILED FROM WIRE REPORTS  -  20 NOVEMBER 2026", 2, CREAM)

# ---------------------------------------------------------------- PNG encode


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path}: {len(data)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
