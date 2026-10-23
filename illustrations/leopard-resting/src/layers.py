"""Step 2: quantize the artwork into a small palette and trace each colour as a stacked vector layer.
Output: src/layers.json  -> [{"hex":..., "d":[path strings]}] ordered back-to-front."""
import json, re, cv2, numpy as np, vtracer, os, tempfile
K = int(os.environ.get('K', 14))
art = cv2.imread('src/art_prepped.png')
H, W = art.shape[:2]
lab = cv2.cvtColor(art, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
cv2.setRNGSeed(0)
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
_, lbl, cen = cv2.kmeans(lab[::7], K, None, crit, 3, cv2.KMEANS_PP_CENTERS)
d = ((lab[:, None, :] - cen[None]) ** 2).sum(-1); lbl = d.argmin(1).reshape(H, W)
# clean label map: mode filter via per-label median blur of one-hot
lbl = cv2.medianBlur(lbl.astype(np.uint8), 5)
order = np.argsort(-cen[:, 0])                     # light -> dark (paint order)
rank = np.empty(K, int); rank[order] = np.arange(K)
R = rank[lbl]
cols = cv2.cvtColor(cen[None].astype(np.uint8), cv2.COLOR_LAB2RGB)[0]
layers = []
tmp = tempfile.mkdtemp()
for r, k in enumerate(order):
    hexc = '#%02x%02x%02x' % tuple(int(v) for v in cols[k])
    if r == 0:
        layers.append({"hex": hexc, "d": [f"M0 0H{W}V{H}H0Z"], "bg": True}); continue
    mask = np.where(R >= r, 0, 255).astype(np.uint8)   # black = fill
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if r == 1:  # silhouette: fill interior highlights that match the paper colour
        ff = mask.copy(); cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 128)
        mask[ff == 255] = 0
    p_in, p_out = f'{tmp}/m{r}.png', f'{tmp}/m{r}.svg'
    cv2.imwrite(p_in, mask)
    vtracer.convert_image_to_svg_py(p_in, p_out, colormode='binary', mode='spline',
        filter_speckle=10, corner_threshold=60, length_threshold=4.0,
        splice_threshold=45, path_precision=1)
    svg = open(p_out).read()
    ds = []
    for m in re.finditer(r'<path d="([^"]+)"[^>]*transform="translate\(([-\d.]+),([-\d.]+)\)"', svg):
        ds.append((m.group(1), float(m.group(2)), float(m.group(3))))
    layers.append({"hex": hexc, "lum": float(cen[k][0]), "d": ds})
    print(r, hexc, len(ds), int((R >= r).sum()))
json.dump({"W": W, "H": H, "layers": layers}, open('src/layers.json', 'w'))
