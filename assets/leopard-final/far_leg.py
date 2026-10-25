"""Build the far front leg from the near one (mirrored), as a separate layer that
sits behind the leopard. Outputs a 4x RGBA layer + a preview composite."""
import sys
import cv2, numpy as np

K = 4
base = cv2.imread('np4x.png', cv2.IMREAD_UNCHANGED)          # leopard, transparent bg
H, W = base.shape[:2]
INK = np.array([29, 30, 30, 255], np.uint8)                   # BGRA of #1e1e1d
CREAM = np.array([228, 238, 243, 255], np.uint8)              # BGRA of #f3eee4

# 1. near leg (lower leg + paw), outline included, cut off from the body
LEG = np.array([(742, 372), (778, 440), (815, 520), (836, 590), (836, 672),
                (985, 672), (985, 598), (952, 560), (916, 530), (912, 450), (906, 360)], float)
mask = np.zeros((H, W), np.uint8)
cv2.fillPoly(mask, [(LEG * K).astype(np.int32)], 255)
x, y, w, h = cv2.boundingRect((LEG * K).astype(np.int32))
patch = base[y:y + h, x:x + w].copy()
patch[..., 3] = np.minimum(patch[..., 3], mask[y:y + h, x:x + w])

# 2. mirror it, a touch smaller (it's the far side), and place it under the chest
FLIP, SCALE = True, float(sys.argv[1]) if len(sys.argv) > 1 else 0.96
DX, DY = (float(v) for v in (sys.argv[2:4] if len(sys.argv) > 3 else (-205, -14)))
if FLIP:
    patch = patch[:, ::-1]
patch = cv2.resize(patch, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
layer = np.zeros_like(base)
px, py = int(x + DX * K), int(y + DY * K + h * (1 - SCALE))   # keep the paw on the ground line
ph, pw = patch.shape[:2]
layer[py:py + ph, px:px + pw] = patch

# 3. upper leg / chest: fill from the leg's top up under the chin, with the leg's
#    front contour continued up to meet the jaw
pts = np.argwhere(layer[..., 3] > 0)
CHIN = np.array([float(v) for v in (sys.argv[4:6] if len(sys.argv) > 5 else (505, 291))])
ink = (layer[..., 3] > 200) & (layer[..., :3].max(2) < 90)
top_y = pts[:, 0].min()
def edge_x(yy, side):
    xs = np.nonzero(ink[int(yy)])[0]
    return (xs.min() if side < 0 else xs.max()) / K
# front contour: join the chest curve a little below the cut so the stroke overlaps
def first_run(yy):   # (start, end) of the left-most ink run in a row, in orig px
    xs = np.nonzero(ink[int(yy * K)])[0]
    e = xs[0]
    while e + 1 in set(xs[:200]): e += 1
    return xs[0] / K, e / K
fy = top_y / K + 30                     # below the hook where the leg met the body
a0, a1 = first_run(fy); g0, g1 = first_run(fy + 40)
start = np.array([(a0 + a1) / 2, fy])
tang = np.array([((g0 + g1) - (a0 + a1)) / 2, 40.0]); tang /= np.linalg.norm(tang)
ctrl = start - tang * 50                # arrive along the leg's own edge direction
# trim the hook/stub above the joint (the chest curve takes over there)
stub = np.zeros((H, W), bool)
stub[int(top_y):int((fy - 2) * K), :int((start[0] + 14) * K)] = True
layer[stub & (layer[..., 3] > 0)] = 0
t = np.linspace(0, 1, 60)[:, None]
curve = (1 - t) ** 2 * CHIN + 2 * (1 - t) * t * ctrl + t ** 2 * start
# back contour: continue it up along its own direction until it is behind the near leg
def T(p):   # original-image point -> far-leg position (orig px)
    X, Y = p
    c = (w - 1 - (X * K - x)) if FLIP else (X * K - x)
    return np.array([px + c * SCALE, py + (Y * K - y) * SCALE]) / K
# the near leg's front contour (mirrored, it becomes the far leg's back edge)
solid = layer[..., 3] > 128
def back_edge(yy):   # right-most opaque pixel of the placed leg = outer edge of its back contour
    return np.nonzero(solid[int(yy * K)])[0].max() / K - 4.5
ty = top_y / K
b0 = np.array([back_edge(ty + 14), ty + 14])
b1 = np.array([back_edge(ty + 34), ty + 34])
dirv = (b0 - b1) / np.linalg.norm(b0 - b1)
back_top = b0 + dirv * 70
# chest fill: generous, it all sits behind the near leg / head anyway
fillpoly = np.vstack([curve, [b1 + [-3, 0], b0 + [-3, 0], back_top + [-3, 0], back_top + [60, -60],
                              [CHIN[0] + 140, CHIN[1] - 40], [CHIN[0] + 10, CHIN[1] - 15]]])
fill_l = np.zeros((H, W), np.uint8)
cv2.fillPoly(fill_l, [(fillpoly * K).astype(np.int32)], 255, cv2.LINE_AA)
under = layer[..., 3] < 250   # includes the soft edge of the cut
layer[(fill_l > 127) & under] = CREAM
for seg in (curve, np.vstack([b1, b0, back_top])):
    cv2.polylines(layer, [(seg * K).astype(np.int32).reshape(-1, 1, 2)], False, INK.tolist(), 7 * K, cv2.LINE_AA)
# drop stray ink crumbs left by the cut
crumbs = ((layer[..., 3] > 0) & (layer[..., :3].max(2) < 90)).astype(np.uint8)
n, cl, st, _ = cv2.connectedComponentsWithStats(crumbs, connectivity=8)
for i in range(1, n):
    if st[i, 4] < 5 * K * K:   # real spots are bigger than ~5 px²
        layer[cv2.dilate((cl == i).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = CREAM
# the cut's top rows (between the two contours) are hidden chest: clean cream
y0c = int(top_y); y1c = int(top_y + 12 * K)
layer[y0c:y1c, int((start[0] + 14) * K):int((b0[0] - 8) * K)] = CREAM
start_dbg = start
cv2.imwrite('farleg4x.png', layer)
# preview: leg layer behind the leopard, on white
comp = np.full((H, W, 3), 255, np.uint8)
for lay in (layer, base):
    a = lay[..., 3:4] / 255.0
    comp = (comp * (1 - a) + lay[..., :3] * a).astype(np.uint8)
cv2.imwrite('farleg_preview.png', cv2.resize(comp, (W // K, H // K), interpolation=cv2.INTER_AREA))
print('start', start_dbg.round(1), 'back', back_top.round(1))
