import sys, re, subprocess, tempfile, os
import cv2, numpy as np

src, out, preview = sys.argv[1], sys.argv[2], sys.argv[3]
S = 4  # input is already rendered at 4x
CLOSE_R = 4 * S // 2 + 2  # gap-closing radius (in upscaled px)

col = cv2.imread(src)
g = cv2.cvtColor(col, cv2.COLOR_BGR2GRAY)
H0, W0 = g.shape[0] // S, g.shape[1] // S
bg_bgr = col[5, 5]
g = cv2.GaussianBlur(g, (0, 0), S * 0.5)
lines = (g < 62).astype(np.uint8)
lines = cv2.morphologyEx(lines, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
H, W = lines.shape

disc = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
closed = cv2.morphologyEx(lines, cv2.MORPH_CLOSE, disc(CLOSE_R))
from scipy.ndimage import binary_fill_holes

# Bridge open stroke ends: extend each skeleton endpoint along its direction
# until it meets another line (within MAX_GAP), so regions become sealed.
from skimage.morphology import skeletonize
MAX_GAP = 28 * S
sk = skeletonize(lines > 0).astype(np.uint8)
nb = cv2.filter2D(sk, -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT) - sk
ends = np.argwhere((sk == 1) & (nb == 1))
# Spots and tiny fur marks are not boundaries: ignore them as bridge sources/targets.
nc, clab, cst, _ = cv2.connectedComponentsWithStats(lines, connectivity=8)
big = np.hypot(cst[:, 2], cst[:, 3]) >= 45 * S
big[0] = False
structural = big[clab].astype(np.uint8)
bridges = 0
for (y, x) in ends:
    # walk back along the skeleton to estimate stroke direction
    path = [(y, x)]; prev = None; cy, cx = y, x
    for _ in range(10 * S):
        nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = cy + dy, cx + dx
                if (dy or dx) and 0 <= ny < H and 0 <= nx < W and sk[ny, nx] and (ny, nx) not in path:
                    nxt = (ny, nx); break
            if nxt: break
        if not nxt: break
        path.append(nxt); cy, cx = nxt
    if not structural[y, x] or len(path) < 4 * S:
        continue  # tiny speck / dot, not a stroke
    d = np.array([y - cy, x - cx], float); d /= np.linalg.norm(d) + 1e-9
    best = None
    for ang in np.radians(np.arange(-35, 36, 5)):
        c, s_ = np.cos(ang), np.sin(ang)
        v = np.array([c * d[0] - s_ * d[1], s_ * d[0] + c * d[1]])
        left = False
        for t in range(1, MAX_GAP):
            py, px = int(round(y + v[0] * t)), int(round(x + v[1] * t))
            if not (0 <= py < H and 0 <= px < W): break
            if not structural[py, px]: left = True
            elif left:
                if best is None or t < best[0]: best = (t, py, px)
                break
    if best:
        cv2.line(closed, (int(x), int(y)), (best[2], best[1]), 1, 2 * S)
        bridges += 1
print("bridges:", bridges)
closed = cv2.dilate(closed, disc(1))
free = (1 - closed).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(free, connectivity=4)


def trace(mask, turd=4, alpha=1.0):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "m.pbm")
        cv2.imwrite(p, (1 - mask) * 255)
        svg = subprocess.run(["potrace", "-s", "-t", str(turd), "-a", str(alpha),
                              "-O", "0.4", "-o", "-", p],
                             capture_output=True, text=True, check=True).stdout
    tr = re.search(r'<g transform="([^"]+)"', svg).group(1)
    ds = re.findall(r'<path d="([^"]+)"', svg)
    return tr, " ".join(d.replace("\n", " ") for d in ds)


min_area = 8 * S * S
regions = []
for i in range(1, n):
    x, y, w, h, a = stats[i]
    if a < min_area or x == 0 or y == 0 or x + w >= W or y + h >= H:
        continue  # skip specks and the outside background
    m = binary_fill_holes(lab == i).astype(np.uint8)  # spots sit on top, no holes needed
    m = cv2.dilate(m, disc(CLOSE_R + 3))  # tuck region edges under the lines
    fillc = np.median(col[lab == i], axis=0).astype(int)
    regions.append((a, m, fillc))
regions.sort(key=lambda r: -r[0])  # big first, small on top

# tiny openings in the line art (e.g. thin eye highlights) that gap-closing
# swallowed: give each its own small shape in its original colour
covered = np.zeros_like(lines)
for _, m, _ in regions:
    covered |= m
leftover = ((1 - lines) & (1 - covered)).astype(np.uint8)
n2, lab2, st2, _ = cv2.connectedComponentsWithStats(leftover, connectivity=4)
for i in range(1, n2):
    if st2[i, 4] < 3 * S * S:
        continue
    fillc = np.median(col[lab2 == i], axis=0).astype(int)
    if np.abs(fillc - bg_bgr.astype(int)).sum() < 30:
        continue  # it's just background showing between lines
    m = cv2.dilate((lab2 == i).astype(np.uint8), disc(2))
    regions.append((st2[i, 4], m, fillc))

parts = []
hexc = lambda c: "#%02X%02X%02X" % (c[2], c[1], c[0])
for k, (a, m, fillc) in enumerate(regions):
    tr, d = trace(m, turd=20)
    parts.append(f'    <path id="region-{k+1:03d}" fill="{hexc(fillc)}" transform="{tr}" d="{d}"/>')
tr, d = trace(lines, turd=6, alpha=1.0)

sc = 1 / S
svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W0}" height="{H0}" viewBox="0 0 {W0} {H0}">
  <g id="Background"><rect width="{W0}" height="{H0}" fill="{hexc(bg_bgr)}"/></g>
  <g id="Color_Regions" transform="scale({sc})">
{chr(10).join(parts)}
  </g>
  <g id="Line_Art" transform="scale({sc})">
    <path id="lines" fill="#1E1E1D" transform="{tr}" d="{d}"/>
  </g>
</svg>
'''
open(out, "w").write(svg)
print("regions:", len(regions))

# preview: color regions randomly to verify closure
rng = np.random.default_rng(1)
pv = np.full((H, W, 3), (212, 230, 241), np.uint8)
for a, m, _ in regions:
    pv[m > 0] = rng.integers(90, 255, 3)
pv[lines > 0] = (28, 36, 43)
cv2.imwrite(preview, cv2.resize(pv, (W0, H0), interpolation=cv2.INTER_AREA))
