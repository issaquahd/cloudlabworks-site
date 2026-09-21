#!/Users/rebl/.local/share/imgtools/bin/python
"""Bake a Cloud Lab Works watermark into an image for public display.

    watermark.py IN OUT.jpg [--width 1600] [--label "© Cloud Lab Works LLC"]

IN may be JPEG, PNG or SVG (SVG is rasterised with rsvg-convert). The output is always a JPEG
capped at --width, with two marks baked into the pixels: a diagonal lattice of the label at low
opacity across the whole frame, and a small opaque band in the bottom-right corner carrying the
orca mark, the label and the domain. Neither can be cropped or toggled away; the originals never
leave media/src/ (deploy-assets.sh uploads media/* flat, no subfolders). Used by build-art.sh for
the /art page and by ops/iam/publish.sh for the nightly piece.
"""
import math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
FONT = "/System/Library/Fonts/Supplemental/Futura.ttc"
ORCA = os.path.join(SITE, "media", "waku-orca-pale.svg")
RSVG = "/opt/homebrew/bin/rsvg-convert"
LABEL = "© Cloud Lab Works LLC"
DOMAIN = "cloudlabworks.dev"


def rasterise(path, width):
    """SVG → RGBA via rsvg-convert; raster formats open directly (EXIF orientation honoured)."""
    if path.lower().endswith(".svg"):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
            tmp = t.name
        subprocess.run([RSVG, "-w", str(width), "-o", tmp, path], check=True)
        im = Image.open(tmp).convert("RGBA")
        os.unlink(tmp)
        # SVG art has a transparent ground; give it the card's dark warm field so the mark reads.
        bg = Image.new("RGBA", im.size, (28, 20, 16, 255))
        return Image.alpha_composite(bg, im)
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im


def lattice(size, label):
    """Diagonal repeating label, white with a dark shadow so it reads on light and dark fields."""
    w, h = size
    fs = max(18, w // 26)
    font = ImageFont.truetype(FONT, fs)
    diag = int(math.hypot(w, h)) + fs * 4
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tw = d.textlength(label, font=font)
    stepx, stepy = int(tw + fs * 3), int(fs * 4.2)
    row = 0
    for y in range(0, diag, stepy):
        x0 = -(stepx // 2) if row % 2 else 0
        for x in range(x0, diag, stepx):
            d.text((x + 2, y + 2), label, font=font, fill=(10, 8, 6, 60))
            d.text((x, y), label, font=font, fill=(255, 255, 255, 58))
        row += 1
    layer = layer.rotate(30, resample=Image.BICUBIC, expand=False)
    ox, oy = (diag - w) // 2, (diag - h) // 2
    return layer.crop((ox, oy, ox + w, oy + h))


def corner(im, label):
    """Opaque band, bottom-right: orca mark, label, domain."""
    w, h = im.size
    fs = max(13, w // 60)
    font = ImageFont.truetype(FONT, fs)
    small = ImageFont.truetype(FONT, max(11, int(fs * 0.8)))
    d = ImageDraw.Draw(im)
    mark = int(fs * 2.6)
    tw = max(d.textlength(label, font=font), d.textlength(DOMAIN, font=small))
    pad = int(fs * 0.8)
    bw, bh = int(mark + tw + pad * 3), int(mark + pad * 2)
    x0, y0 = w - bw - pad, h - bh - pad
    band = Image.new("RGBA", (bw, bh), (11, 18, 32, 214))
    ImageDraw.Draw(band).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=pad, outline=(168, 205, 202, 140), width=1)
    im.alpha_composite(band, (x0, y0))
    if os.path.exists(ORCA):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
            tmp = t.name
        subprocess.run([RSVG, "-w", str(mark), "-h", str(mark), "-o", tmp, ORCA], check=True)
        orca = Image.open(tmp).convert("RGBA")
        os.unlink(tmp)
        im.alpha_composite(orca, (x0 + pad, y0 + pad))
    tx = x0 + pad * 2 + mark
    d.text((tx, y0 + pad), label, font=font, fill=(248, 250, 252, 255))
    d.text((tx, y0 + pad + fs + 4), DOMAIN, font=small, fill=(168, 205, 202, 255))
    return im


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    src, out = args[0], args[1]
    width, label = 1600, LABEL
    i = 2
    while i < len(args):
        if args[i] == "--width":
            width = int(args[i + 1]); i += 2
        elif args[i] == "--label":
            label = args[i + 1]; i += 2
        else:
            sys.exit("unknown option " + args[i])
    im = rasterise(src, width)
    im = Image.alpha_composite(im, lattice(im.size, label))
    im = corner(im, label)
    im.convert("RGB").save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print(out, im.size[0], "x", im.size[1])


if __name__ == "__main__":
    main()
