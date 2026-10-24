"""Minimal leopard: outlines + face only, with the rosettes replaced by stars.

The outlines are one connected shape with rosettes and fur flicks hanging off it. Reduce it to a
centreline, prune short side branches (those are rosettes/flicks), and keep the original ink only
along the surviving lines, so the strokes keep their hand-drawn weight.
Writes src/ink_minimal_outline.png (2x) and src/star_spots.json (1x: x, y, size, rotation)."""
import json, random, cv2, numpy as np
from skimage.morphology import skeletonize, remove_small_holes
ink = 255 - cv2.imread('src/ink_final.png', cv2.IMREAD_GRAYSCALE)
disk = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
n, lab, st, cen = cv2.connectedComponentsWithStats(ink, 8)
main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
M = lab == main
# regions drawn as-is (1x boxes): face features, inner ear, paw pads, cushion tassels
PROTECT = [(345, 292, 520, 420), (590, 225, 650, 310), (1030, 650, 1140, 760), (95, 400, 260, 840), (900, 590, 1000, 700)]
prot = np.zeros_like(M)
for x0, y0, x1, y1 in PROTECT: prot[y0 * 2:y1 * 2, x0 * 2:x1 * 2] = True

skel = skeletonize(remove_small_holes(M, max_size=2500))           # rosette rings become solid, then single branches
K = 44                                                     # side branches shorter than this (2x px) go
nb = lambda s: cv2.filter2D(s.astype(np.uint8), -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT) - s
pr = skel.copy()
for _ in range(K):
    pr &= ~(pr & (nb(pr) <= 1))
ends = pr & (nb(pr) == 1)                                  # regrow the real line ends that pruning shortened
grow = ends.copy()
for _ in range(K):
    grow = (cv2.dilate(grow.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & skel & ~pr | grow
lines = pr | grow
out = M & (cv2.dilate(lines.astype(np.uint8), disk(5)) > 0)
out |= M & prot
# back + haunch: rosettes fused into the contour leave bumps, so redraw that contour from the silhouette
sil = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, disk(10))
ff = sil.copy(); cv2.floodFill(ff, np.zeros((sil.shape[0] + 2, sil.shape[1] + 2), np.uint8), (0, 0), 128)
inside = np.where(ff == 128, 0, 255).astype(np.uint8)
depth = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
back = np.zeros_like(M)
cv2.fillPoly(back.view(np.uint8), [(np.array([(640, 240), (1000, 260), (1330, 470), (1460, 640), (1400, 700), (1250, 560),
                                              (1060, 470), (760, 330), (640, 300)]) * 2).astype(np.int32)], 1)
out[back & (depth > 0) & (depth <= 34)] = False
out[back & (depth > 0) & (depth <= 9)] = True
for i in range(1, n):                                      # loose pieces inside protected boxes (eyes, nose)
    x, y, w, h, a = st[i]
    if i != main and any(x0 * 2 <= x and x + w <= x1 * 2 and y0 * 2 <= y and y + h <= y1 * 2 for x0, y0, x1, y1 in PROTECT):
        out |= lab == i
cn, clab, cst, _ = cv2.connectedComponentsWithStats(out.astype(np.uint8), 8)   # sweep up leftover specks
FACE_ONLY = PROTECT[0]
for i in range(1, cn):
    x, y, w, h, a = cst[i]
    in_face = FACE_ONLY[0] * 2 <= x and x + w <= FACE_ONLY[2] * 2 and FACE_ONLY[1] * 2 <= y and y + h <= FACE_ONLY[3] * 2
    if a < 260 and not in_face: out[clab == i] = False
cv2.imwrite('src/ink_minimal_outline.png', np.where(out, 0, 255).astype(np.uint8))

# where the spots were: loose spots + the rosettes just pruned off the outline
gone = ((ink > 0) & ~out & ~prot).astype(np.uint8)
gn, glab, gst, gcen = cv2.connectedComponentsWithStats(gone, 8)
spots = [(gcen[i][0] / 2, gcen[i][1] / 2, max(gst[i, 2], gst[i, 3]) / 2) for i in range(1, gn)
         if gst[i, cv2.CC_STAT_AREA] > 120 and (gcen[i][0] / 2 > 560 or gcen[i][1] / 2 < 330)]
random.seed(3)
cushion = np.zeros(M.shape, np.uint8)
cv2.fillPoly(cushion, [(np.array([(90, 380), (330, 380), (360, 445), (620, 445), (800, 470), (835, 490),
                                  (828, 840), (90, 840)]) * 2).astype(np.int32)], 1)
lines_dist = cv2.distanceTransform(np.where(out, 0, 255).astype(np.uint8), cv2.DIST_L2, 5) / 2   # 1x px to nearest line
body = (depth > 0) & (cushion == 0)
chosen = []
for x, y, s in sorted(spots, key=lambda p: -p[2]):
    size = float(min(max(s * .7, 8), 17)) * random.uniform(.7, 1.3)
    xi, yi = int(x * 2), int(y * 2)
    if not body[yi, xi] or lines_dist[yi, xi] < size * 1.25 + 5: continue        # inside the body, clear of lines
    if all((x - cx) ** 2 + (y - cy) ** 2 > 40 ** 2 for cx, cy, _, _ in chosen):
        chosen.append((float(x), float(y), size, random.uniform(-15, 15)))
# fill bare stretches (haunch, hind leg) at the same spacing
cand = [(x, y) for y in range(200, 840, 9) for x in range(540, 1460, 9)]
random.shuffle(cand)
for x, y in cand:
    size = random.uniform(7, 15)
    if not body[y * 2, x * 2] or lines_dist[y * 2, x * 2] < size * 1.1 + 3: continue
    if all((x - cx) ** 2 + (y - cy) ** 2 > 44 ** 2 for cx, cy, _, _ in chosen):
        chosen.append((float(x), float(y), size, random.uniform(-15, 15)))
json.dump(chosen, open('src/star_spots.json', 'w'))
print(len(spots), 'spots ->', len(chosen), 'stars')
