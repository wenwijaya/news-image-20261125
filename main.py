#!/usr/bin/env python3
"""news-image-20261125: one front-page image summing up Wednesday 25 November 2026.

Pure Python 3 standard library. Draws a 1024x1024 newspaper front page with a
5x7 bitmap font and a hand-written PNG encoder (zlib + struct), then writes it
to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Stories (all reported on 25 Nov 2026):
  LEAD  Ukraine strikes at sea - Zelenskiy confirms a drone hit on a Russian
        cargo ship in the Gulf of Finland; Kyiv also claims a warship sunk
        off Libya; Putin warns retaliation is inevitable.
  2     Houthi drone hits Riyadh's PIF Tower, 11 wounded - second strike
        in under a week.
  3     Huawei convicted in a sprawling US criminal trial over Iran business.
  4     Trump awards Rudy Giuliani the Medal of Freedom and pardons the
        Thanksgiving turkeys Freedom and Feathers.
  5     NATO to send early-warning aircraft to Poland; space-defence vow
        amid reports of a Russian nuclear-armed satellite.
  ALSO  CIA/ODNI cyber breach; tankers hit by mines in the Strait of Hormuz;
        Sarkozy corruption case to trial; UN court condemns Myanmar over
        the Rohingya; Waymo halts driverless taxis on US freeways;
        South Korea's education minister resigns; 25 Nov is the
        International Day for the Elimination of Violence against Women.

Deterministic: no clock, no randomness, no network, fixed zlib level, so two
runs write identical bytes.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 230)
INK = (22, 21, 19)
NAVY = (18, 57, 91)
NAVY_DARK = (11, 38, 62)
RED = (176, 42, 48)
TEAL = (14, 107, 107)
GOLD = (200, 155, 60)
SLATE = (61, 74, 87)
SKY = (168, 199, 224)
SKY_LIGHT = (205, 224, 240)
SEA = (23, 68, 104)
SEA_DARK = (13, 48, 76)
ORANGE = (224, 122, 42)
YELLOW = (240, 196, 66)
CREAM = (255, 251, 240)
WHITE = (255, 255, 255)
GREY_LINE = (120, 110, 95)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is clear.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "%": ("10001", "10010", "00010", "00100", "01000", "10001", "10001"),
    "$": ("00100", "01110", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given font scale (6 units per char)."""
    return len(text) * 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    """An RGB raster with rectangle/line/circle/polygon/text drawing."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with a square brush of side `thick`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        """Filled circle."""
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        """Circle outline."""
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= r * r:
                    self.set(xx, yy, color)

    def poly(self, points, color):
        """Filled polygon (scanline fill)."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for yy in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), yy, max(1, int(xs[k + 1]) - int(xs[k])), 1, color)

    def text(self, x, y, s, scale, color, align="left"):
        """Draw text; returns the x just past the last drawn character."""
        s = s.upper()
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale, scale, scale, color)
            cx += 6 * scale
        return cx

    def para(self, x, y, text, scale, color, max_width, leading=None):
        """Draw a wrapped paragraph; returns the y just past the last line."""
        lh = leading if leading is not None else 9 * scale
        for line in wrap_text(text, scale, max_width):
            self.text(x, y, line, scale, color)
            y += lh
        return y


def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    """Encode the canvas as a deterministic PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += png_chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- layout

def draw_sea_scene(cv, x, y, w, h):
    """Gulf of Finland: sky, sea, cargo ship, drones, explosion."""
    cv.rect(x, y, w, h, SKY_LIGHT)
    cv.rect(x, y + 58, w, 26, SKY)              # horizon haze
    cv.disc(x + w - 70, y + 34, 22, YELLOW)     # low sun
    cv.ring(x + w - 70, y + 34, 22, GOLD, 2)
    cv.rect(x, y + 84, w, h - 84, SEA)          # sea
    cv.rect(x, y + 84, w, 4, (140, 180, 210))   # horizon glint
    # wave strokes
    for wy, wl in ((y + 130, 60), (y + 168, 90), (y + 205, 50)):
        cv.hline(x + 24, wy, wl, (120, 170, 205))
        cv.hline(x + w - 120, wy + 12, 80, (120, 170, 205))
    # cargo ship (dark silhouette with containers)
    sx, sy = x + 52, y + h - 78
    cv.poly([(sx, sy), (sx + 210, sy), (sx + 190, sy + 34), (sx + 14, sy + 34)], INK)
    cv.rect(sx + 30, sy - 26, 34, 26, RED)
    cv.rect(sx + 70, sy - 26, 34, 26, GOLD)
    cv.rect(sx + 110, sy - 26, 34, 26, TEAL)
    cv.rect(sx + 150, sy - 26, 30, 26, CREAM)
    cv.rect(sx + 188, sy - 52, 6, 52, INK)      # mast
    cv.rect(sx + 182, sy - 58, 18, 6, INK)
    # explosion starburst above the bow
    ex, ey = sx + 208, sy - 46
    for ang in range(0, 360, 30):
        r1 = 34 if ang % 60 == 0 else 16
        x1 = ex + int(r1 * math.cos(math.radians(ang)))
        y1 = ey + int(r1 * math.sin(math.radians(ang)))
        cv.line(ex, ey, x1, y1, ORANGE, 5)
    cv.disc(ex, ey, 15, YELLOW)
    cv.disc(ex, ey, 8, WHITE)
    # three drones overhead
    for dx, dy in ((x + 90, y + 26), (x + 150, y + 14), (x + 210, y + 30)):
        cv.disc(dx, dy, 4, INK)
        cv.hline(dx - 10, dy - 2, 20, INK)
        cv.hline(dx - 10, dy + 2, 20, INK)
    cv.text(x + 12, y + h - 30, "THE GULF OF FINLAND", 2, CREAM)


def draw_tower(cv, x, y, w, h):
    """Riyadh's PIF Tower silhouette against a dusk sky."""
    cv.rect(x, y, w, h, (233, 214, 178))
    cv.disc(x + w - 34, y + 26, 16, YELLOW)
    # tower: tapering shaft with a spire
    cv.poly([(x + 66, y + h), (x + 78, y + 26), (x + 102, y + 26), (x + 114, y + h)], NAVY_DARK)
    cv.poly([(x + 84, y + 26), (x + 90, y + 2), (x + 96, y + 26)], NAVY_DARK)
    # lit windows
    for wy in range(y + 44, y + h - 12, 16):
        for wx in (x + 80, x + 92, x + 104):
            cv.rect(wx, wy, 4, 8, GOLD)
    # blast flash at the crown
    cv.disc(x + 90, y + 22, 12, ORANGE)
    cv.disc(x + 90, y + 22, 6, YELLOW)
    # ground line
    cv.rect(x, y + h - 8, w, 8, INK)


def draw_scales(cv, x, y, w, h):
    """Scales of justice for the Huawei trial panel."""
    cv.rect(x, y, w, h, (222, 228, 232))
    cx, cy = x + w // 2, y + 26
    cv.vline(cx, cy, h - 60, INK)
    cv.hline(cx - 52, cy + 6, 104, INK)
    cv.disc(cx, cy + 2, 6, INK)
    for side in (-1, 1):
        px = cx + side * 52
        cv.line(px, cy + 6, px - 16, cy + 52, INK, 2)
        cv.line(px, cy + 6, px + 16, cy + 52, INK, 2)
        cv.poly([(px - 20, cy + 52), (px + 20, cy + 52), (px, cy + 72)], GOLD)
    cv.rect(cx - 26, y + h - 30, 52, 8, INK)
    cv.rect(cx - 4, y + h - 52, 8, 22, INK)


def draw_front_page():
    cv = Canvas(W, H, PAPER)
    # frame
    cv.rect(0, 0, W, 10, NAVY)
    cv.rect(0, H - 10, W, 10, NAVY)
    cv.rect(0, 0, 10, H, NAVY)
    cv.rect(W - 10, 0, 10, H, NAVY)
    cv.rect(14, 14, W - 28, 2, GOLD)
    cv.rect(14, H - 16, W - 28, 2, GOLD)

    # ---- masthead ----
    cv.rect(24, 26, W - 48, 132, NAVY)
    cv.text(W // 2, 40, "THE WORLD", 9, WHITE, align="center")
    cv.hline(64, 108, W - 128, GOLD)
    cv.text(W // 2, 120, "WEDNESDAY 25 NOVEMBER 2026", 3, CREAM, align="center")
    cv.text(W // 2, 166, "ONE DAY IN PICTURES AND HEADLINES", 2, SLATE, align="center")
    cv.hline(24, 190, W - 48, INK)

    # ---- lead story: Kyiv strikes at sea ----
    cv.text(40, 206, "WAR IN EUROPE", 3, RED)
    cv.text(40, 232, "KYIV STRIKES", 6, INK)
    cv.text(40, 280, "AT SEA", 6, INK)
    cv.hline(40, 330, 180, RED)
    y = cv.para(40, 344, "ZELENSKIY CONFIRMS A DRONE HIT ON A RUSSIAN CARGO SHIP IN "
                 "THE GULF OF FINLAND. KYIV CLAIMS A WARSHIP SUNK OFF LIBYA.",
                3, INK, 560, leading=26)
    cv.text(40, y + 4, "PUTIN WARNS OF RETALIATION.", 2, RED)
    draw_sea_scene(cv, 640, 206, 344, 252)
    cv.rect(640, 458, 344, 3, INK)
    cv.hline(24, 486, W - 48, INK)

    # ---- middle row: Riyadh + Huawei ----
    # left: Riyadh tower hit
    cv.text(40, 504, "MIDDLE EAST", 3, RED)
    cv.text(40, 530, "RIYADH", 5, INK)
    cv.text(40, 566, "TOWER HIT", 5, INK)
    cv.para(40, 612, "A HOUTHI DRONE STRIKES THE PIF TOWER, THE CAPITAL'S TALLEST, "
             "WOUNDING 11. THE SECOND ATTACK IN UNDER A WEEK.",
            2, INK, 296, leading=18)
    draw_tower(cv, 356, 504, 146, 194)
    cv.vline(512, 504, 194, GREY_LINE)
    # right: Huawei guilty
    cv.text(536, 504, "TECH ON TRIAL", 3, RED)
    cv.text(536, 530, "HUAWEI", 5, INK)
    cv.text(536, 566, "GUILTY", 5, INK)
    cv.para(536, 612, "A US JURY CONVICTS CHINA'S HUAWEI OVER IRAN BUSINESS IN A "
             "SPRAWLING CRIMINAL TRIAL. THE RACKETEERING CHARGE FAILS.",
            2, INK, 296, leading=18)
    draw_scales(cv, 852, 504, 132, 194)
    cv.hline(24, 722, W - 48, INK)

    # ---- bottom row: three short stories ----
    cols = [
        (40, "WASHINGTON", "TRUMP'S TUESDAY",
         "GIULIANI GETS THE MEDAL OF FREEDOM. TURKEYS FREEDOM AND FEATHERS "
         "ARE PARDONED FOR THANKSGIVING."),
        (352, "ALLIANCE", "NATO ON ALERT",
         "EARLY-WARNING AIRCRAFT FOR POLAND. A SPACE-DEFENCE VOW AMID "
         "REPORTS OF A RUSSIAN NUCLEAR SATELLITE."),
        (664, "ALSO TODAY", "IN BRIEF",
         "CIA-ODNI BREACH. TANKERS HIT BY MINES IN HORMUZ. SARKOZY TO TRIAL. "
         "MYANMAR CONDEMNED. WAYMO HALTS FREEWAY ROBOTAXIS."),
    ]
    for cx, kicker, head, body in cols:
        cv.text(cx, 740, kicker, 2, RED)
        cv.text(cx, 762, head, 3, INK)
        cv.hline(cx, 794, 120, GOLD)
        cv.para(cx, 808, body, 2, INK, 288, leading=18)
    cv.vline(336, 740, 168, GREY_LINE)
    cv.vline(648, 740, 168, GREY_LINE)

    # ---- footer ----
    cv.hline(24, 934, W - 48, INK)
    cv.text(W // 2, 948, "25 NOV: INTERNATIONAL DAY FOR THE ELIMINATION "
             "OF VIOLENCE AGAINST WOMEN", 2, RED, align="center")
    cv.text(W // 2, 972, "DRAWN FROM THE DAY'S REPORTING  -  MAKE.FUN NEWS-IMAGE-20261125",
            2, SLATE, align="center")
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = encode_png(draw_front_page())
    with open(path, "wb") as fh:
        fh.write(data)
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass
    if len(data) > 1048576:
        print("error: entry.png is %d bytes, over the 1 MiB cap" % len(data),
              file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, 1024x1024)" % (path, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
