"""Pillows alone, completed: drop the leopard, keep the visible left half of the
pillow drawing, mirror it for the hidden right half, and close the top edge
where the head was. Works on the 4x renders of LEOPARD_FINAL.svg."""
import sys
import cv2, numpy as np
from scipy.ndimage import binary_fill_holes

K = 4
AXIS = float(sys.argv[1]) if len(sys.argv) > 1 else 560.0     # mirror line (orig px)
PILLOW = {6, 8, 16, 17, 23, 26, 30, 31, 32, 13, 19, 20, 28}
BG = 1
LEOPARD_BIG = {2, 5, 18, 27, 22, 25, 14}

outline = cv2.imread('outline_only.png', 0) < 128
spots = cv2.imread('spots_only.png', 0) < 128
L = (outline | spots).astype(np.uint8)
lab = np.load('lab.npy')
H, W = L.shape
disc = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)

pillow_area = np.isin(lab, list(PILLOW)).astype(np.uint8)
leopard_area = np.isin(lab, list(LEOPARD_BIG)).astype(np.uint8)
# small pockets (tassel slits etc.) that sit next to the pillow count as pillow
n = lab.max() + 1
near_leo = cv2.dilate(leopard_area, disc(45)) > 0
for i in range(1, n):
    if i in PILLOW | LEOPARD_BIG or i == BG:
        continue
    m = lab == i
    if not near_leo[m].any():
        pillow_area[m] = 1

# pillow ink = lines next to a pillow area and not part of the leopard's contour
# (whole ink shapes connected to the pillow are kept, so solid tassels stay solid)
cand = (L & ~(cv2.dilate(leopard_area, disc(30)) > 0)).astype(np.uint8)
touch = cand & (cv2.dilate(pillow_area, disc(31)) > 0)
nn, cl, st, _ = cv2.connectedComponentsWithStats(cand, connectivity=8)
ids = set(np.unique(cl[touch > 0])) - {0}
lines = np.isin(cl, [i for i in ids if st[i, 4] > 300]).astype(np.uint8)

# keep the left half, mirror it to the right
ax = int(round(AXIS * K))
left = lines.copy(); left[:, ax:] = 0
full = left.copy()
mir = left[:, :ax][:, ::-1]
full[:, ax:ax + mir.shape[1]] |= mir[:, :W - ax]

# smooth every line across the mirror line: replace the middle with a symmetric
# cubic that keeps each stroke's own slope (no V-kinks at the centre)
WIN = 90.0
xa, xb = AXIS - WIN, AXIS - WIN - 30
def runs(col, mask):
    c = mask[:, int(col * K)].astype(np.int8)
    d = np.diff(np.concatenate([[0], c, [0]]))
    return [((a + b) / 2 / K) for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0])]
ra, rb = runs(xa, left), runs(xb, left)
full[:, int(xa * K) + 1:int((2 * AXIS - xa) * K)] = 0
mirror = lambda p: np.array([2 * AXIS - p[0], p[1]])
for ya in ra:
    if ya < 330:    # the top edge is rebuilt below
        continue
    yb = min(rb, key=lambda v: abs(v - ya))
    P0 = np.array([xa, ya]); tan = np.array([xa - xb, ya - yb]); tan /= np.linalg.norm(tan)
    P1 = P0 + tan * WIN * 0.55
    t = np.linspace(0, 1, 200)[:, None]
    c = ((1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * mirror(P1) + t ** 3 * mirror(P0))
    cv2.polylines(full, [(c * K).astype(np.int32).reshape(-1, 1, 2)], False, 1, int(7.5 * K), cv2.LINE_8)

# close the top edge across where the head was: smooth symmetric arc
def endpoint_of_top_edge():
    # top-most pillow ink per column on the left half; the top edge ends where it stops
    ys = [(x, np.nonzero(left[:, x])[0].min()) for x in range(int(250 * K), ax) if left[:, x].any()]
    xs = np.array(ys, float)
    # top edge = columns whose top ink is above the first seam (y < 330)
    edge = xs[xs[:, 1] < 330 * K]
    end = edge[edge[:, 0].argmax()]
    back = edge[np.abs(edge[:, 0] - (end[0] - 45 * K)).argmin()]
    return end / K, back / K
(ex, ey), (bx, by) = endpoint_of_top_edge()
# centre of the stroke at its end (the top ink is its upper edge)
P0 = np.array([bx + 4, by + 3.8]); Pb = np.array([bx, by + 3.5])   # start inside the drawn line: no seam
# drop whatever the face left behind near the end of the top edge (whiskers, muzzle stub);
# the arc takes over from P0
for img in (left, full):
    img[:int(330 * K), int((P0[0] + 2) * K):int((2 * AXIS - P0[0] - 2) * K)] = 0
    # whisker tips poking above the top edge just before the arc starts
    img[:int((P0[1] - 9) * K), int(330 * K):int((2 * AXIS - 330) * K)] = 0
tan = (P0 - Pb) / np.linalg.norm(P0 - Pb)
Lh = (AXIS - P0[0]) * 0.55
P1 = P0 + tan * Lh + np.array([0, -14])   # gentle dome, like a plumped pillow
mirror = lambda p: np.array([2 * AXIS - p[0], p[1]])
P2, P3 = mirror(P1), mirror(P0)
t = np.linspace(0, 1, 200)[:, None]
arc = ((1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3)
cv2.polylines(full, [(arc * K).astype(np.int32).reshape(-1, 1, 2)], False, 1, int(7.8 * K), cv2.LINE_8)

fill = binary_fill_holes(full).astype(np.uint8)
cv2.imwrite('pillow_lines.png', (1 - full) * 255)
cv2.imwrite('pillow_fill.png', (1 - fill) * 255)
prev = np.full((H, W, 3), 255, np.uint8)
prev[fill > 0] = (228, 238, 243)
prev[full > 0] = (29, 30, 30)
cv2.imwrite('pillow_preview.png', cv2.resize(prev, (W // K, H // K), interpolation=cv2.INTER_AREA))
print('top edge end', P0.round(1), 'tangent', tan.round(2))
