"""Remove the pillow from LEOPARD_FINAL.svg: keep only outline that borders a
leopard area; re-trace the outline + fill; keep every other path untouched."""
import re, sys, subprocess, tempfile, os
import cv2, numpy as np
from scipy.ndimage import binary_fill_holes

K = 4
PILLOW = {6, 8, 16, 17, 23, 26, 30, 31, 32, 13, 19, 20, 28}   # from the region map
BG = 1
# x0, y0, x1, y1 (orig px): leopard ink that touches only background — whiskers, back-paw pad
PROTECT = [(340, 170, 397, 222), (1012, 505, 1140, 606)]

o = cv2.imread('outline_only.png', 0)
L = (o < 128).astype(np.uint8)
lab = np.load('lab.npy')
H, W = L.shape
disc = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)
LEOPARD_BIG = {2, 5, 18, 27, 22, 25}   # body, upper lip, belly, back paw, tail pockets
POCKET = {14}                           # background enclosed by the tail curl
# small pockets (eye glints, tassel slits...) belong to whatever big area they sit beside
big_leo = np.isin(lab, list(LEOPARD_BIG)).astype(np.uint8)
near_leo = cv2.dilate(big_leo, disc(45))
small_leo = set()
for i in range(1, lab.max() + 1):
    if i in LEOPARD_BIG | PILLOW | POCKET or i == BG:
        continue
    if near_leo[lab == i].any() and not np.isin(lab, list(PILLOW))[
            cv2.dilate((lab == i).astype(np.uint8), disc(45)) > 0].any():
        small_leo.add(i)
print('small leopard pockets:', sorted(small_leo))
leopard = np.isin(lab, list(LEOPARD_BIG | small_leo)).astype(np.uint8)
near = cv2.dilate(leopard, disc(31))
keep = L & near
def protect(m):
    for box in PROTECT:
        x0, y0, x1, y1 = [v * K for v in box]
        m[y0:y1, x0:x1] = L[y0:y1, x0:x1]
protect(keep)
# drop any loose crumbs left from pillow lines
n, cl, st, _ = cv2.connectedComponentsWithStats(keep, connectivity=8)
keep = np.isin(cl, [i for i in range(1, n) if st[i, 4] > 400]).astype(np.uint8)
keep = cv2.morphologyEx(keep, cv2.MORPH_OPEN, disc(2))
# solid ink inside the leopard (e.g. the dark paw pad) is far from any open area:
# restore every line pixel enclosed by the kept outline
inside = binary_fill_holes(keep | leopard)
keep = (L & inside).astype(np.uint8) | keep
protect(keep)
cv2.imwrite('keep_lines.png', (1 - keep) * 255)

# new cream fill: everything enclosed by the leopard outline (minus the background
# pocket inside the tail curl), tucked slightly under the lines
fill = binary_fill_holes(keep | leopard).astype(np.uint8)
fill[np.isin(lab, list(POCKET))] = 0   # the background pocket between tail and body stays empty
fill = cv2.erode(fill, disc(6)) | (leopard & fill)

def trace(mask):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'm.pbm')
        cv2.imwrite(p, (1 - mask) * 255)
        svg = subprocess.run(['potrace', '-b', 'svg', '-t', '8', '-a', '1.0', '-O', '0.2',
                              '-o', '-', p], capture_output=True, text=True, check=True).stdout
    tr = re.search(r'<g transform="([^"]+)"', svg)
    ds = re.findall(r'<path d="([^"]+)"', svg)
    return (tr.group(1) if tr else None), ' '.join(x.replace('\n', ' ') for x in ds)

src = open('LEOPARD_FINAL.svg').read()
paths = re.findall(r'<path[^>]*/>', src)
# other paths: keep those whose centre lies on the leopard (drops tassel pieces)
centres = [tuple(map(float, c.split(','))) for c in sys.argv[1].split(';')]
silhouette = binary_fill_holes(keep | leopard)
kept_paths = [p for i, (p, (cx, cy)) in enumerate(zip(paths, centres))
              if i not in (0, 96) and silhouette[int(cy * K), int(cx * K)]]
print('other paths kept:', len(kept_paths), 'of', len(paths) - 2)

tr_l, d_l = trace(keep)
tr_f, d_f = trace(fill)
head = src[:src.index('</defs>') + len('</defs>')] + '\n  '
out = (head + '<g>\n'
       + f'    <path class="st0" transform="scale(0.25) {tr_f}" d="{d_f}"/>\n'
       + f'    <path class="st1" transform="scale(0.25) {tr_l}" d="{d_l}"/>\n'
       + '\n'.join('    ' + p for p in kept_paths) + '\n  </g>\n</svg>\n')
open('LEOPARD_NO_PILLOW.svg', 'w').write(out)
