"""Clean monoline vector of the original leopard drawing.

Same forms as the original (eye, nose, fur waves, toes), but every line becomes one true SVG stroke of
even width with round ends, like a clean ink pen. Thick ink (nose, paw pads, inner ear) stays as fills.
Also traces the leopard's body as a clip shape for the skin patterns.
Writes src/lines.json (stroke paths), src/fills.json (filled paths), src/body_clip.json (clip path)."""
import json, re, cv2, numpy as np, vtracer
from skan import Skeleton
from skimage.morphology import skeletonize
SC = 2
disk = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
ink = (cv2.imread('../leopard-lineart/src/ink_minimal_outline.png', cv2.IMREAD_GRAYSCALE) < 128).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(ink, 8)
ink = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 120]).astype(np.uint8)
H, W = ink.shape

# thick ink -> fills
blobs = cv2.morphologyEx(ink, cv2.MORPH_OPEN, disk(7))
n, lab, st, _ = cv2.connectedComponentsWithStats(blobs, 8)
fills = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 250]).astype(np.uint8)
fills = cv2.morphologyEx(cv2.bitwise_and(cv2.dilate(fills, disk(3)), ink), cv2.MORPH_CLOSE, disk(2))

# centrelines -> polylines
sk = skeletonize(ink > 0) & ~(cv2.erode(fills, disk(2)) > 0)
S = Skeleton(sk)
def rdp(p, eps):
    return cv2.approxPolyDP(p.astype(np.float32).reshape(-1, 1, 2), eps, False).reshape(-1, 2)
def smooth(p, k=5):
    if len(p) < k + 2: return p
    q = p.copy().astype(float)
    ker = np.ones(k) / k
    for d in range(2):
        pad = np.r_[[p[0, d]] * (k // 2), p[:, d], [p[-1, d]] * (k // 2)]
        q[:, d] = np.convolve(pad, ker, 'valid')
    q[0], q[-1] = p[0], p[-1]
    return q
def to_bezier(p):
    """Catmull-Rom through the points -> cubic Bezier path string (1x coords)."""
    if len(p) == 2: return f'M{p[0][0]:.1f} {p[0][1]:.1f}L{p[1][0]:.1f} {p[1][1]:.1f}'
    d = [f'M{p[0][0]:.1f} {p[0][1]:.1f}']
    for i in range(len(p) - 1):
        p0, p1, p2, p3 = p[max(i - 1, 0)], p[i], p[i + 1], p[min(i + 2, len(p) - 1)]
        c1, c2 = p1 + (p2 - p0) / 6, p2 - (p3 - p1) / 6
        d.append(f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    return ''.join(d)
FACE = (352, 290, 515, 412)
PAW = (1012, 640, 1148, 768)                               # hind paw pads: redrawn clean
inbox = lambda p, b: b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]
polys = []
deg = S.degrees
for i in range(S.n_paths):
    rc = S.path_coordinates(i)
    idx = S.path(i)
    free = (deg[idx[0]] == 1) + (deg[idx[-1]] == 1)
    p = rc[:, ::-1].astype(float) / SC
    if len(rc) < (14 if free else 3): continue              # skeleton whiskers from thick strokes
    mid = p[len(p) // 2]
    if free == 2 and len(rc) < 34 and not inbox(mid, FACE): continue   # stray marks
    if inbox(mid, (1034, 662, 1128, 750)) and inbox(p[0], (1030, 658, 1132, 754)) and inbox(p[-1], (1030, 658, 1132, 754)): continue
    polys.append(smooth(p))
# bridge small gaps between line ends (dashed piping, broken contours)
ends = [(k, e) for k in range(len(polys)) for e in (0, -1)]
used = set()
bridges = []
for a in range(len(ends)):
    for b in range(a + 1, len(ends)):
        (ka, ea), (kb, eb) = ends[a], ends[b]
        if ka == kb or a in used or b in used: continue
        pa, pb = polys[ka][ea], polys[kb][eb]
        gap = np.hypot(*(pa - pb))
        if gap < 1e-6: continue
        ta = pa - polys[ka][3 if ea == 0 else -4] if len(polys[ka]) > 4 else pa - polys[ka][1 if ea == 0 else -2]
        tb = pb - polys[kb][3 if eb == 0 else -4] if len(polys[kb]) > 4 else pb - polys[kb][1 if eb == 0 else -2]
        u = (pb - pa) / gap
        aligned = np.dot(ta, u) / (np.linalg.norm(ta) + 1e-6) > .8 and np.dot(tb, -u) / (np.linalg.norm(tb) + 1e-6) > .8
        if gap < 7 or (gap < 22 and aligned):
            bridges.append(np.array([pa, pb])); used |= {a, b}
paths = [to_bezier(rdp(p, .55)) for p in polys if len(rdp(p, .55)) >= 2] + [to_bezier(b) for b in bridges]
json.dump(paths, open('src/lines.json', 'w'))

def trace(mask, speckle=4):
    cv2.imwrite('src/_t.png', np.where(mask > 0, 0, 255).astype(np.uint8))
    vtracer.convert_image_to_svg_py('src/_t.png', 'src/_t.svg', colormode='binary', mode='spline',
        filter_speckle=speckle, corner_threshold=70, length_threshold=4, splice_threshold=45, path_precision=1)
    svg = open('src/_t.svg').read()
    return [f'<path d="{d}" transform="translate({x} {y})"/>' for d, x, y in
            re.findall(r'<path d="([^"]+)"[^>]*transform="translate\(([-\d.]+),([-\d.]+)\)"', svg)]
fills[PAW[1] * SC:PAW[3] * SC, PAW[0] * SC:PAW[2] * SC] = 0
json.dump(trace(fills), open('src/fills.json', 'w'))

# body clip: the leopard's regions (seeded), joined across their dividing lines
fat = cv2.dilate(ink * 255, disk(4))
n, lab, _, _ = cv2.connectedComponentsWithStats((fat == 0).astype(np.uint8), 4)
seeds = [(900, 450), (1130, 690), (370, 380), (375, 318)]
leo = np.isin(lab, [lab[y * SC, x * SC] for x, y in seeds]).astype(np.uint8)
leo = cv2.morphologyEx(leo, cv2.MORPH_CLOSE, disk(14))
ff = leo * 255; cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 128); leo = (ff != 128).astype(np.uint8)
leo = cv2.dilate(leo, disk(3))
json.dump(trace(leo, 30), open('src/body_clip.json', 'w'))
cv2.imwrite('src/body_mask.png', leo * 255)
import os; os.remove('src/_t.png'); os.remove('src/_t.svg')
print(len(paths), 'stroke paths')
