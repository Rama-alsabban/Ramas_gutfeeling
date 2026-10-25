"""Trace the far-leg layer and insert it behind the leopard in the SVG."""
import re, subprocess, tempfile, os, sys
import cv2, numpy as np

K = 4
layer = cv2.imread('farleg4x.png', cv2.IMREAD_UNCHANGED)
a = layer[..., 3:4] / 255.0
on_cream = (layer[..., :3] * a + np.array([228, 238, 243]) * (1 - a)).astype(np.uint8)
ink = ((cv2.cvtColor(on_cream, cv2.COLOR_BGR2GRAY) < 120) & (layer[..., 3] > 0)).astype(np.uint8)
fill = (layer[..., 3] > 128).astype(np.uint8)
fill = cv2.erode(fill, np.ones((3, 3), np.uint8))   # stay inside the outline

def trace(mask):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'm.pbm')
        cv2.imwrite(p, (1 - mask) * 255)
        svg = subprocess.run(['potrace', '-b', 'svg', '-t', '8', '-a', '1.0', '-O', '0.2', '-o', '-', p],
                             capture_output=True, text=True, check=True).stdout
    tr = re.search(r'<g transform="([^"]+)"', svg).group(1)
    return tr, ' '.join(x.replace('\n', ' ') for x in re.findall(r'<path d="([^"]+)"', svg))

trf, df = trace(fill)
trl, dl = trace(ink)
src = open(sys.argv[1]).read()
i = src.index('<path class="st0"')
leg = (f'<g id="far_front_leg">\n'
       f'      <path class="st0" transform="scale(0.25) {trf}" d="{df}"/>\n'
       f'      <path class="st1" transform="scale(0.25) {trl}" d="{dl}"/>\n'
       f'    </g>\n    ')
open(sys.argv[2], 'w').write(src[:i] + leg + src[i:])
print('ok')
