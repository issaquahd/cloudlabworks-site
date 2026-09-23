#!/Users/rebl/.local/share/imgtools/bin/python
"""sleeve-cut.py SRC OUT.png --pick <rule> [--rot deg] [--grow 1.05] [--wb 0.5]

Cut one sticker out of a binder photo shot through a clear plastic sleeve, where Vision and a
plain colour mask both grab the sleeve instead of the sticker (2026-09-22 lesson).

Method: build a mask of the sticker's *printed colour*, keep the largest connected blob, take the
convex hull of it (most die-cut silhouettes are convex or near enough), grow the hull to take in
the white rim, then reject anything dark inside that rim ring so the sleeve's shadow is dropped.

--pick rules select the printed colour:
  red, blue, green, teal, orange, purple, dark, saturated
Combine with '+' (e.g. blue+dark). --rot is measured separately and passed in; a minimum-area
rectangle lies about tilt on anything that is not a rectangle.
"""
import argparse, numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from collections import deque

def masks(a):
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    return {
        "red":       (R > 110) & (R - G > 45) & (R - B > 45),
        "blue":      (B > 90) & (B - R > 40) & (B - G > 20),
        "green":     (G > 80) & (G - R > 30) & (G - B > 25),
        "teal":      (G > 80) & (B > 80) & (G - R > 25) & (B - R > 25),
        "orange":    (R > 140) & (R - B > 70) & (G > 80) & (G < R - 30),
        "purple":    (B > 80) & (B - G > 30) & (R - G > 15),
        "dark":      (mx < 100),
        "saturated": (sat > 0.35) & (mx > 90),
    }

def blobs(m, step=37):
    """All connected components, largest first. A wordmark printed beside a logo is its own
    component, so taking only the biggest silently clips the sticker (2026-09-22)."""
    H, W = m.shape
    seen = np.zeros_like(m, bool); out = []
    ys, xs = np.nonzero(m)
    for sy, sx in zip(ys[::step], xs[::step]):
        if seen[sy, sx]: continue
        q = deque([(sy, sx)]); seen[sy, sx] = True; pts = []
        while q:
            y, x = q.popleft(); pts.append((y, x))
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; q.append((ny, nx))
        out.append(np.array(pts))
    out.sort(key=len, reverse=True)
    return out

def pick_parts(m, frac, near, step=37):
    """Largest component plus every other one that is a real part of the same sticker: at least
    `frac` of its size and with a centroid within `near` radii of it. The distance test is what
    keeps a neighbouring sticker in the next pocket out of the hull."""
    bs = blobs(m, step)
    if not bs: return np.zeros((0, 2), int)
    main = bs[0]
    c = main.mean(0); r = np.sqrt(len(main) / np.pi)
    keep = [main]
    for b in bs[1:]:
        if len(b) < frac * len(main): continue
        if np.hypot(*(b.mean(0) - c)) > near * r: continue
        keep.append(b)
    return np.vstack(keep)

def hull(P):
    P = sorted(map(tuple, P))
    def half(P):
        h = []
        for p in P:
            while len(h) > 1 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    return half(P)[:-1] + half(P[::-1])[:-1]

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--pick", required=True)
ap.add_argument("--rot", type=float, default=0.0)
ap.add_argument("--grow", type=float, default=1.05)
ap.add_argument("--wb", type=float, default=0.5)
ap.add_argument("--rim-dark", type=int, default=128)
ap.add_argument("--frac", type=float, default=0.12, help="min size of a secondary part, vs the main blob")
ap.add_argument("--near", type=float, default=3.0, help="max centroid distance, in main-blob radii")
a_ = ap.parse_args()

im = ImageOps.exif_transpose(Image.open(a_.src)).convert("RGB")
arr = np.asarray(im).astype(int)
M = masks(arr)
sel = np.zeros(arr.shape[:2], bool)
for k in a_.pick.split("+"):
    sel |= M[k]
blob = pick_parts(sel, a_.frac, a_.near)
pts = blob[:, ::-1]
Hu = hull(pts)
cx, cy = np.mean([p[0] for p in Hu]), np.mean([p[1] for p in Hu])
poly = lambda s: [(cx + (x-cx)*s, cy + (y-cy)*s) for x, y in Hu]
inner = Image.new("L", im.size, 0); ImageDraw.Draw(inner).polygon(poly(1.005), fill=255)
outer = Image.new("L", im.size, 0); ImageDraw.Draw(outer).polygon(poly(a_.grow), fill=255)
inn, out_ = np.asarray(inner) > 0, np.asarray(outer) > 0
lum = arr.mean(2)
keep = out_.copy(); keep[(out_ & ~inn) & (lum < a_.rim_dark)] = False
m = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))

bright = inn & (lum > 150)
if bright.sum() > 200 and a_.wb > 0:
    mean = arr[bright].reshape(-1, 3).mean(0)
    gain = 1 + (mean.mean() / mean - 1) * a_.wb
    arr = np.clip(arr * gain, 0, 255)
o = Image.fromarray(arr.astype(np.uint8)).convert("RGBA"); o.putalpha(m)
if a_.rot: o = o.rotate(a_.rot, resample=Image.BICUBIC, expand=True)
o = o.crop(o.split()[3].point(lambda v: 255 if v > 10 else 0).getbbox())
o.save(a_.out)
print(f"{a_.out} {o.size[0]}x{o.size[1]} from {len(blob)} px")
