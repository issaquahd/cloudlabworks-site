#!/Users/rebl/.local/share/imgtools/bin/python
"""pad.py IMG top right bottom left: add cream margins in place (room for the watermark band)."""
import sys
from PIL import Image
p, t, r, b, l = sys.argv[1], *map(int, sys.argv[2:6])
im = Image.open(p).convert("RGB")
out = Image.new("RGB", (im.width + l + r, im.height + t + b), (241, 227, 195))
out.paste(im, (l, t)); out.save(p)
