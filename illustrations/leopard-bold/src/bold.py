"""Vector of the bold-outline region map: the minimal line art thickened evenly, plus every enclosed
region as its own fillable shape (no colours, cream by default). Writes leopard-bold*.svg"""
import re, cv2, numpy as np, vtracer, os
INK, PAPER = '#1f1d1a', '#f3eee4'
disk = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
src = 255 - cv2.imread('../leopard-lineart/src/ink_minimal_outline.png', cv2.IMREAD_GRAYSCALE)
fat = cv2.dilate(src, disk(4))                                   # same thickening as the region map
fat = cv2.morphologyEx(fat, cv2.MORPH_OPEN, disk(1))

# relaxed, satisfied eye: replace the narrowed eye wedge with a soft closed-eye curve
def bez(p0, p1, p2, p3, n=60):
    u = np.linspace(0, 1, n)[:, None]; p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return (1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3
fat[2 * 290:2 * 336, 2 * 436:2 * 526] = 0
lid = bez((444, 309), (462, 326), (494, 327), (512, 307))                       # closed lid, bowing down
flick = bez((512, 307), (515, 303), (518, 300), (521, 298), 12)                  # outer corner lifts gently
for curve, w in [(lid, 17), (flick, 13)]:
    cv2.polylines(fat, [np.round(curve * 2).astype(np.int32)], False, 255, w, cv2.LINE_AA)
fat = np.where(fat > 127, 255, 0).astype(np.uint8)

def trace(mask, speckle):
    cv2.imwrite('src/_t.png', np.where(mask > 0, 0, 255).astype(np.uint8))
    vtracer.convert_image_to_svg_py('src/_t.png', 'src/_t.svg', colormode='binary', mode='spline', filter_speckle=speckle,
                                    corner_threshold=60, length_threshold=4, splice_threshold=45, path_precision=1)
    out = [f'<path d="{d}" transform="translate({x} {y})"/>' for d, x, y in
           re.findall(r'<path d="([^"]+)"[^>]*transform="translate\(([-\d.]+),([-\d.]+)\)"', open('src/_t.svg').read())]
    os.remove('src/_t.png'); os.remove('src/_t.svg')
    return ''.join(out)

ink_paths = trace(fat, 6)
# enclosed regions (leopard, cushions, tassels...) as separate shapes, grown under the line so no gaps show
n, lab, st, _ = cv2.connectedComponentsWithStats((fat == 0).astype(np.uint8), 4)
bg = lab[0, 0]
regions = []
for i in range(1, n):
    if i == bg or st[i, 4] < 1500: continue
    m = cv2.dilate((lab == i).astype(np.uint8), disk(5))
    regions.append(f'<g id="region-{len(regions) + 1:02d}">{trace(m, 4)}</g>')
print(len(regions), 'regions')

def doc(title, bg=True, fills=True):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="1536" height="1024">\n<title>{title}</title>\n'
            + (f'<rect id="paper" width="100%" height="100%" fill="{PAPER}"/>\n' if bg else '')
            + (f'<g id="regions" fill="{PAPER}" transform="scale(0.5)">{"".join(regions)}</g>\n' if fills else '')
            + f'<g id="ink" fill="{INK}" transform="scale(0.5)">{ink_paths}</g>\n</svg>\n')
open('leopard-bold.svg', 'w').write(doc('Leopard — bold outline'))
open('leopard-bold-transparent.svg', 'w').write(doc('Leopard — bold outline', bg=False))
