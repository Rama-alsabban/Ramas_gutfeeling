"""Replace the flat S-stroke tail with an illustrated leopard tail that follows
the exact same S path, then save a 4x raster ready for vectorizing."""
import sys
import cv2, numpy as np
from scipy.interpolate import splprep, splev
from skimage.morphology import skeletonize

src, out = sys.argv[1], sys.argv[2]
K = 4                      # working scale
OUT_W = 7                  # outline width of the drawing (orig px)
TAIL_W = 32                # full tail width incl. outline (orig px)
INK = (30, 30, 29)
FILL = (234, 212, 195)     # BGR of the leopard's light blue

im0 = cv2.imread(src)
H0, W0 = im0.shape[:2]
g0 = cv2.cvtColor(im0, cv2.COLOR_BGR2GRAY)
dark0 = (g0 < 70).astype(np.uint8)
blue0 = (g0 > 150).astype(np.uint8)

# --- 1. isolate the drawn S tail (dark pixels well away from any blue fill)
near_blue = cv2.dilate(blue0, np.ones((2 * 9 + 1,) * 2, np.uint8))
tail0 = dark0 & (1 - near_blue)
tail0[:, :1150] = 0
n, lab, st, _ = cv2.connectedComponentsWithStats(tail0, connectivity=8)
tail0 = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)

# --- 2. its centerline, ordered base -> tip, smoothed
sk = skeletonize(cv2.dilate(tail0, np.ones((3, 3), np.uint8)) > 0)
pts = {tuple(p) for p in np.argwhere(sk)}
nbrs = lambda p: [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dy or dx) and (p[0] + dy, p[1] + dx) in pts]
ends = [p for p in pts if len(nbrs(p)) == 1]
start = min(ends, key=lambda p: p[1])          # base = left-most end
# longest path from the base (BFS) to drop skeleton spurs
from collections import deque
prev = {start: None}; q = deque([start]); last = start
while q:
    p = q.popleft(); last = p
    for nb in nbrs(p):
        if nb not in prev:
            prev[nb] = p; q.append(nb)
path = []
p = last
while p is not None:
    path.append(p); p = prev[p]
path = np.array(path[::-1], float)[:, ::-1]     # (x, y), base -> tip
path = path[::3]
tck, _ = splprep(path.T, s=len(path) * 1.5)
u = np.linspace(0, 1, 600)
cx, cy = splev(u, tck)
C = np.stack([cx, cy], 1)
# extend the base back into the body along its tangent so it grows out of it
t0 = C[0] - C[6]; t0 /= np.linalg.norm(t0)
C = np.vstack([[C[0] + t0 * s for s in np.linspace(45, 1, 20)], C])
seg = np.linalg.norm(np.diff(C, axis=0), axis=1)
arc = np.concatenate([[0], np.cumsum(seg)])
L = arc[-1]

# --- 3. work at K x
im = cv2.resize(im0, (W0 * K, H0 * K), interpolation=cv2.INTER_CUBIC)
body_mask0 = ((g0 > 150) | (dark0 & near_blue)).astype(np.uint8)   # leopard + its outline
body_mask0 = cv2.morphologyEx(body_mask0, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
body = cv2.resize(body_mask0, (W0 * K, H0 * K), interpolation=cv2.INTER_NEAREST)

# erase the old tail (paint background grey)
bg = np.array(im0[5, 5], np.uint8)
old = cv2.resize(cv2.dilate(tail0, np.ones((5, 5), np.uint8)), (W0 * K, H0 * K),
                 interpolation=cv2.INTER_NEAREST)
im[(old > 0) & (body == 0)] = bg

def poly(c):
    return (c * K).astype(np.int32).reshape(-1, 1, 2)

def stroke(mask, c, w):
    cv2.polylines(mask, [poly(c)], False, 255, int(round(w * K)), cv2.LINE_AA)
    for e in (c[0], c[-1]):   # round caps
        cv2.circle(mask, tuple((e * K).astype(int)), int(round(w * K / 2)), 255, -1, cv2.LINE_AA)

outer = np.zeros(im.shape[:2], np.uint8); stroke(outer, C, TAIL_W)
inner = np.zeros(im.shape[:2], np.uint8); stroke(inner, C, TAIL_W - 2 * OUT_W)

# soft fillet where the tail leaves the rump, so the outline flows into the back
fil = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (14 * K + 1,) * 2)
sil = cv2.morphologyEx(((body > 0) * 255 | outer).astype(np.uint8), cv2.MORPH_CLOSE, fil)
root = np.zeros_like(outer)
cv2.circle(root, tuple((C[20] * K).astype(int)), 40 * K, 255, -1)
fillet = (sil > 127) & (body == 0) & (root > 0)
outer = np.maximum(outer, fillet.astype(np.uint8) * 255)

ink = np.array(INK, np.uint8); fill = np.array(FILL, np.uint8)
# outline only outside the body; fill everywhere (covers body outline at the join)
inner_ext = np.maximum(inner, cv2.erode(outer, cv2.getStructuringElement(
    cv2.MORPH_ELLIPSE, (2 * OUT_W * K + 1,) * 2)))
o = (outer > 127) & (body == 0)
im[o] = ink
im[inner_ext > 127] = fill

# --- 4. markings: borrow real rosettes from the leopard's flank as stamps
gK = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
n, lab0, st0, _ = cv2.connectedComponentsWithStats(dark0, connectivity=8)
stamps = []
for i in range(1, n):
    x, y, w, h, a = st0[i]
    if 650 < x < 1300 and 100 < y < 500 and 16 <= w <= 30 and 12 <= h <= 26 and a / (w * h) < 0.6:
        crop = (lab0[y - 1:y + h + 1, x - 1:x + w + 1] == i).astype(np.uint8) * 255
        stamps.append(cv2.resize(crop, None, fx=K, fy=K, interpolation=cv2.INTER_CUBIC))
print("rosette stamps:", len(stamps))

def at(s):   # point + unit tangent at arc length s
    i = np.searchsorted(arc, s).clip(1, len(C) - 1)
    t = C[i] - C[i - 1]; t /= np.linalg.norm(t) + 1e-9
    return C[i], t

inner_m = inner_ext > 127
rng = np.random.default_rng(7)
base_s = 60          # first marking just past the rump
tip_band = L - 95    # rings + black tip after this
s = base_s; k = 0
while s < tip_band:
    p, t = at(s); nrm = np.array([-t[1], t[0]])
    side = (1 if k % 2 else -1) * 3.5
    st_ = stamps[rng.integers(len(stamps))]
    scale = np.interp(s, [base_s, tip_band], [0.95, 0.7])
    ang = np.degrees(np.arctan2(t[1], t[0])) + rng.uniform(-25, 25)
    M = cv2.getRotationMatrix2D((st_.shape[1] / 2, st_.shape[0] / 2), -ang, scale)
    big = int(max(st_.shape) * 1.5)
    M[:, 2] += (big - np.array(st_.shape[::-1])) / 2
    r = cv2.warpAffine(st_, M, (big, big))
    c = ((p + nrm * side) * K).astype(int) - big // 2
    sub = (slice(c[1], c[1] + big), slice(c[0], c[0] + big))
    m = (r > 110) & inner_m[sub]
    im[sub][m] = ink
    s += np.interp(s, [base_s, tip_band], [36, 30]); k += 1

# two rings, then a solid dark tip (classic leopard tail end; echoes the logo terminal)
# arc-length map: which point of the centerline each tail pixel belongs to
amap = np.full(im.shape[:2], -1, np.int32)
for i in range(len(C) - 1):
    cv2.line(amap, tuple((C[i] * K).astype(int)), tuple((C[i + 1] * K).astype(int)),
             int(i), int(TAIL_W * K))
cv2.circle(amap, tuple((C[-1] * K).astype(int)), int(TAIL_W * K / 2), len(C) - 1, -1)
amap_arc = np.where(amap >= 0, arc[amap.clip(0)], -1)

def band(s0, s1):
    im[(amap_arc >= s0) & (amap_arc <= s1) & inner_m] = ink
band(L - 92, L - 80)
band(L - 62, L - 48)
band(L - 26, L + 30)

cv2.imwrite(out, im)
np.save(out + ".center.npy", C)
print("tail length px:", round(L))
