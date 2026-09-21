#!/Users/rebl/.local/share/imgtools/bin/python
"""Render a text file (ASCII art or a box diagram) to a PNG on the cream field: text2img.py IN.txt OUT.png
Monospace, ink on cream, generous margins; watermark.py takes it from there."""
import sys
from PIL import Image, ImageDraw, ImageFont

CREAM, INK = (241, 227, 195), (31, 58, 58)
FONT = "/System/Library/Fonts/Menlo.ttc"

src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().rstrip("\n").split("\n")
size = 34
font = ImageFont.truetype(FONT, size)
cw = font.getlength("M"); lh = int(size * 1.22)
w = int(max(len(l) for l in lines) * cw) + 160
h = lh * len(lines) + 300
im = Image.new("RGB", (w, h), CREAM)
d = ImageDraw.Draw(im)
for i, l in enumerate(lines):
    d.text((80, 80 + i * lh), l, font=font, fill=INK)
im.save(out, "PNG")
print(out, w, "x", h)
