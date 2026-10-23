"""Trace a solid outline of the leopard + cushions (src/silhouette.json, 1x coords) so shapes can sit behind it."""
import json, re, cv2, numpy as np, vtracer
ink = 255 - cv2.imread('src/ink_final.png', cv2.IMREAD_GRAYSCALE)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
m = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, k)
ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 128)
sil = np.where(ff == 128, 0, 255).astype(np.uint8)
sil = cv2.erode(sil, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))   # stay inside the outline
n, lab, st, _ = cv2.connectedComponentsWithStats(sil, 8)
sil = np.where(np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 4000]), 0, 255).astype(np.uint8)
cv2.imwrite('src/_sil.png', sil)
vtracer.convert_image_to_svg_py('src/_sil.png', 'src/_sil.svg', colormode='binary', mode='spline', filter_speckle=20, path_precision=1)
svg = open('src/_sil.svg').read()
json.dump([f'<path d="{d}" transform="translate({x},{y})"/>' for d, x, y in
           re.findall(r'<path d="([^"]+)"[^>]*transform="translate\(([-\d.]+),([-\d.]+)\)"', svg)], open('src/silhouette.json', 'w'))
ys, xs = np.where(sil == 0); print('bbox 1x:', xs.min()//2, ys.min()//2, xs.max()//2, ys.max()//2)
