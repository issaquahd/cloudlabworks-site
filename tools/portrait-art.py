#!/Users/rebl/.local/share/imgtools/bin/python
"""portrait-art.py PHOTO OUTDIR NAME: three text-art portraits from one photo, for the JAX vault.
  NAME-ascii.txt        plain ASCII, 96 columns, the cream-paper ramp (paste anywhere)
  NAME-ascii.png        the same text set in Menlo on cream paper, ink
  NAME-matrix.png       the photo as green katakana and digits on black, glyph brightness = luminance
  NAME-matrix-rain.png  the same, with digital-rain columns falling through it (white heads)
Deterministic (seeded), no model, nothing leaves the box.
"""
import sys, os, random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

photo, outdir, name = sys.argv[1], sys.argv[2], sys.argv[3]
# --dark: the photo has a dark backdrop; the ASCII goes light-on-dark (bright = dense) and the matrix
# needs less mid-tone push. Default is a light backdrop (ink on cream, dark = dense).
DARK = "--dark" in sys.argv
random.seed(20260921)
src = ImageOps.autocontrast(ImageOps.exif_transpose(Image.open(photo)).convert("L"), cutoff=1)
def gamma(img, g):
    return img.point([int(255 * ((i / 255) ** g)) for i in range(256)])
# paper: only the truly dark tones should draw (hair, eyes, lips); lift the mids so the blurred room falls away
ascii_src = ImageOps.autocontrast(gamma(src, 0.8).filter(ImageFilter.UnsharpMask(radius=6, percent=180, threshold=2)), cutoff=2)
# matrix: the face is the bright thing; push the mids down so the room goes near-black
matrix_src = gamma(src, 1.0 if DARK else 2.2)
if DARK: ascii_src = ImageOps.autocontrast(gamma(src, 1.1).filter(ImageFilter.UnsharpMask(radius=6, percent=160, threshold=2)), cutoff=1)

# ---- ASCII (cream paper) ----
COLS = 110
RAMP = "  .'`:;-~=+*x%#@"
def ascii_lines(img, cols, ramp, aspect=0.5):
    w, h = img.size
    rows = max(1, int(h / w * cols * aspect))
    g = ImageEnhance.Contrast(img.resize((cols, rows), Image.LANCZOS)).enhance(1.25)
    px = g.load(); out = []
    for y in range(rows):
        out.append("".join(ramp[int(((px[x, y]) if DARK else (255 - px[x, y])) / 255 * (len(ramp) - 1))] for x in range(cols)))
    return out
lines = ascii_lines(ascii_src, COLS, RAMP)
open(os.path.join(outdir, f"{name}-ascii.txt"), "w").write("\n".join(lines) + "\n")

def text_png(lines, path, font_path, size, fg, bg, pad=40, line_h=None):
    font = ImageFont.truetype(font_path, size)
    cw = font.getlength("M"); lh = line_h or int(size * 1.02)
    W = int(pad * 2 + cw * max(len(l) for l in lines)); H = int(pad * 2 + lh * len(lines))
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines): d.text((pad, pad + i * lh), l, font=font, fill=fg)
    im.save(path, optimize=True)
text_png(lines, os.path.join(outdir, f"{name}-ascii.png"), "/System/Library/Fonts/Menlo.ttc", 16, *(((232, 224, 200), (12, 14, 18)) if DARK else ((31, 58, 58), (241, 227, 195))))

# ---- Matrix (green glyphs on black) ----
KATA = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:・"
def matrix(img, path, cols=110, cell=12, rain=False):
    w, h = img.size
    rows = int(h / w * cols * (cell / (cell * 1.0)))  # square cells: rows follow the photo's aspect
    g = ImageEnhance.Contrast(img.resize((cols, rows), Image.LANCZOS)).enhance(1.4)
    px = g.load()
    W, H = cols * cell, rows * cell
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", cell + 1)
    # rain: a few columns carry a falling streak; the head is white, the tail fades over ~14 cells
    streaks = {}
    if rain:
        for x in random.sample(range(cols), cols // 3):
            streaks[x] = (random.randint(0, rows - 1), random.randint(8, 18))
    for y in range(rows):
        for x in range(cols):
            v = px[x, y] / 255.0
            boost = 0.0; head = False
            if x in streaks:
                hy, ln = streaks[x]; dy = (hy - y) % rows
                if dy == 0: head = True
                elif dy < ln: boost = (1 - dy / ln) * 0.6
            lum = min(1.0, v * 0.95 + boost)
            if lum < 0.06 and not head: continue
            ch = random.choice(KATA)
            if head: col = (235, 255, 235)
            else:
                # dark green → bright green → pale for highlights
                gch = int(60 + 195 * lum); rch = int(10 + 120 * max(0, lum - 0.55) / 0.45); bch = int(20 + 90 * max(0, lum - 0.7) / 0.3)
                col = (min(255, rch), min(255, gch), min(255, bch))
            d.text((x * cell + 1, y * cell - 1), ch, font=font, fill=col)
    im.save(path, optimize=True)
matrix(matrix_src, os.path.join(outdir, f"{name}-matrix.png"))
matrix(matrix_src, os.path.join(outdir, f"{name}-matrix-rain.png"), rain=True)
print("wrote", name, "ascii", len(lines), "lines")
