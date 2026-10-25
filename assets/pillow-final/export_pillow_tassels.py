"""Trace the completed pillow and two standalone tassels into Illustrator-style SVGs."""
import re, subprocess, tempfile, os
import cv2, numpy as np
from scipy.ndimage import binary_fill_holes

K = 4
lines = (cv2.imread('pillow_lines.png', 0) < 128).astype(np.uint8)
fill = (cv2.imread('pillow_fill.png', 0) < 128).astype(np.uint8)
H, W = lines.shape
STYLE = '''  <defs>
    <style>
      .st0 { fill: #f3eee4; }
      .st1 { fill: #1e1e1d; }
    </style>
  </defs>'''

def trace(mask):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'm.pbm')
        cv2.imwrite(p, (1 - mask) * 255)
        svg = subprocess.run(['potrace', '-b', 'svg', '-t', '8', '-a', '1.0', '-O', '0.2', '-o', '-', p],
                             capture_output=True, text=True, check=True).stdout
    tr = re.search(r'<g transform="([^"]+)"', svg).group(1)
    return tr, ' '.join(x.replace('\n', ' ') for x in re.findall(r'<path d="([^"]+)"', svg))

def write_svg(name, ink, fil, pad=12):
    ys, xs = np.nonzero(ink | fil)
    x0, y0 = xs.min() / K - pad, ys.min() / K - pad
    w, h = xs.max() / K - x0 + pad, ys.max() / K - y0 + pad
    trf, df = trace(cv2.erode(fil, np.ones((3, 3), np.uint8)))
    trl, dl = trace(ink)
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
           f'viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">\n{STYLE}\n  <g>\n'
           f'    <path class="st0" transform="scale(0.25) {trf}" d="{df}"/>\n'
           f'    <path class="st1" transform="scale(0.25) {trl}" d="{dl}"/>\n  </g>\n</svg>\n')
    open(name, 'w').write(svg)

write_svg('PILLOWS.svg', lines, fill)

# ---- standalone tassels: take the clean left half, mirror it about the tassel's
# own axis (a hanging tassel is symmetric), add a hanging loop on top
def tassel(box, axis, top, loop_r, name, squeeze=1.0, strands=()):
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), np.uint8)
    m[int(y0 * K):int(y1 * K), int(x0 * K):int(axis * K)] = 1
    half = lines & m
    n, cl, st, _ = cv2.connectedComponentsWithStats(half, connectivity=8)
    half = np.isin(cl, [i for i in range(1, n) if st[i, 4] > 40 * K]).astype(np.uint8)
    ax = int(axis * K)
    ink = half.copy()
    seg = half[:, int(x0 * K):ax][:, ::-1]
    ink[:, ax:ax + seg.shape[1]] |= seg
    if squeeze != 1.0:   # narrow the skirt around the axis
        sub = ink[:, int(x0 * K):int((2 * axis - x0) * K)]
        w0 = sub.shape[1]
        nw = int(w0 * squeeze)
        sq = cv2.resize(sub, (nw, sub.shape[0]), interpolation=cv2.INTER_NEAREST)
        ink[:, int(x0 * K):int((2 * axis - x0) * K)] = 0
        off = int(x0 * K) + (w0 - nw) // 2
        ink[:, off:off + nw] = sq
    # strand lines (dx from the axis, y from, y to) — drawn symmetric
    for dx, ya, yb in strands:
        for sgn in ((-1, 1) if dx else (1,)):
            cv2.line(ink, (int((axis + sgn * dx) * K), int(ya * K)),
                     (int((axis + sgn * dx * 1.25) * K), int(yb * K)), 1, int(4.2 * K), cv2.LINE_AA)
    # loop on top, sitting on the knot
    cy = top - loop_r[1] + 2.5
    cv2.ellipse(ink, (int(axis * K), int(cy * K)), (int(loop_r[0] * K), int(loop_r[1] * K)),
                0, 0, 360, 1, int(5.5 * K), cv2.LINE_AA)
    fil = binary_fill_holes(ink).astype(np.uint8)
    hole = np.zeros_like(fil)
    cv2.ellipse(hole, (int(axis * K), int(cy * K)), (int((loop_r[0] - 2.8) * K), int((loop_r[1] - 2.8) * K)),
                0, 0, 360, 1, -1)
    fil[hole > 0] = 0
    write_svg(name, ink, fil)
    prev = np.full((H, W, 3), 255, np.uint8); prev[fil > 0] = (228, 238, 243); prev[ink > 0] = (29, 30, 30)
    ys, xs = np.nonzero(ink)
    cv2.imwrite(name.replace('.svg', '_prev.png'),
                cv2.resize(prev[ys.min() - 60:ys.max() + 60, xs.min() - 60:xs.max() + 60], None, fx=0.5, fy=0.5))

# solid black tassel (top-left corner of the pillow)
tassel((138, 287, 0, 392), axis=191.0, top=287, loop_r=(6.5, 8.0), name='TASSEL_SOLID.svg', squeeze=0.78)
# outlined tassel (bottom-left corner), from just under where it ties to the pillow
tassel((170, 583, 0, 672), axis=214.0, top=583, loop_r=(7.0, 8.5), name='TASSEL_OUTLINED.svg',
       strands=[(0, 596, 652), (11, 598, 648)])
print('done')
