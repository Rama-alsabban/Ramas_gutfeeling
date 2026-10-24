"""Clean monoline leopard + skin pattern options. Writes leopard-skin-*.svg"""
import json, math, random
INK, PAPER, SW = '#1f1d1a', '#f3eee4', 8.5
LINES = json.load(open('src/lines.json'))
FILLS = json.load(open('src/fills.json'))
CLIP = json.load(open('src/body_clip.json'))
FACE = (352, 290, 515, 412)                         # keep the face clear of pattern

PADS = ('<ellipse cx="1092" cy="712" rx="27" ry="21" transform="rotate(-20 1092 712)"/>'
        '<circle cx="1043" cy="680" r="9.5"/><circle cx="1036" cy="711" r="9.5"/><circle cx="1047" cy="741" r="9"/>')

def doc(title, skin='', ink=INK, paper=PAPER):
    strokes = ''.join(f'<path d="{d}"/>' for d in LINES) + '<ellipse cx="1080" cy="703" rx="62" ry="50" transform="rotate(-22 1080 703)"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="1536" height="1024">\n<title>{title}</title>\n'
            f'<defs><clipPath id="body">{"".join(c.replace('transform="translate(', 'transform="scale(0.5) translate(') for c in CLIP)}</clipPath></defs>\n'
            f'<rect width="100%" height="100%" fill="{paper}"/>\n'
            f'<g id="skin" clip-path="url(#body)">{skin}</g>\n'
            f'<g id="lines" fill="none" stroke="{ink}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round">{strokes}</g>\n'
            f'<g id="fills" fill="{ink}"><g transform="scale(0.5)">{"".join(FILLS)}</g>{PADS}</g>\n</svg>\n')

import cv2, numpy as np
body = cv2.imread('src/body_mask.png', cv2.IMREAD_GRAYSCALE)[::2, ::2] > 0             # 1x
lines_px = cv2.imread('../leopard-lineart/src/ink_minimal_outline.png', cv2.IMREAD_GRAYSCALE)[::2, ::2] < 128
dist_line = cv2.distanceTransform(np.where(lines_px, 0, 255).astype(np.uint8), cv2.DIST_L2, 5)
dist_edge = cv2.distanceTransform(body.astype(np.uint8) * 255, cv2.DIST_L2, 5)
outer = ~body
def place(rmin, rmax, gap, seed, edge_cut=.25, face_pad=10):
    """Scatter (x, y, r) inside the body: clear of the face, off interior lines, allowed to be cut by the contour."""
    rnd = random.Random(seed); pts = []
    cand = [(x, y) for y in range(190, 850, 4) for x in range(330, 1460, 4) if body[y, x]]
    rnd.shuffle(cand)
    for x, y in cand:
        r = rnd.uniform(rmin, rmax)
        if FACE[0] - face_pad - r < x < FACE[2] + face_pad + r and FACE[1] - face_pad - r < y < FACE[3] + face_pad + r: continue
        if 1035 - r < x < 1130 + r and 655 - r < y < 755 + r: continue        # paw pads
        interior = dist_edge[y, x] > r * .9
        if interior and dist_line[y, x] < r * .8 + 3: continue
        if not interior and dist_edge[y, x] < r * edge_cut: continue
        if any((x - a) ** 2 + (y - b) ** 2 < (r + c + gap) ** 2 for a, b, c in pts): continue
        pts.append((x, y, r))
    return pts, rnd

def chunky_star(x, y, r, rnd):
    n = rnd.choice([6, 7, 8]); rot = rnd.uniform(0, math.pi); p = []
    for i in range(2 * n):
        a = rot + i * math.pi / n
        rr = r * rnd.uniform(.88, 1.1) if i % 2 == 0 else r * .44
        p.append(f'{x + rr * math.cos(a):.1f} {y + rr * math.sin(a):.1f}')
    return f'<path d="M{"L".join(p)}Z"/>'
def sparkle(x, y, r, rot=0):
    k = r * .13
    return (f'<path transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f})" d="M0 {-r:.1f}Q{k:.1f} {-k:.1f} {r*.8:.1f} 0Q{k:.1f} {k:.1f} 0 {r:.1f}'
            f'Q{-k:.1f} {k:.1f} {-r*.8:.1f} 0Q{-k:.1f} {-k:.1f} 0 {-r:.1f}Z"/>')
def crescent(x, y, r, rot):
    return (f'<path transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f})" '
            f'd="M0 {-r:.1f}A{r:.1f} {r:.1f} 0 1 0 0 {r:.1f}A{r*1.12:.1f} {r*1.12:.1f} 0 0 1 0 {-r:.1f}Z"/>')
def blob(x, y, r, rnd):
    """Soft organic patch (Catmull-Rom loop through jittered radii)."""
    k = 9; rot = rnd.uniform(0, 6.3)
    pts = [(x + r * rnd.uniform(.75, 1.15) * math.cos(rot + i * 2 * math.pi / k) * 1.25,
            y + r * rnd.uniform(.75, 1.15) * math.sin(rot + i * 2 * math.pi / k)) for i in range(k)]
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(k):
        p0, p1, p2, p3 = [np.array(pts[(i + j) % k]) for j in (-1, 0, 1, 2)]
        c1, c2 = p1 + (p2 - p0) / 6, p2 - (p3 - p1) / 6
        d += f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    return f'<path d="{d}Z"/>'

SKINS = {}
pts, rnd = place(28, 50, 34, 4)
SKINS['stars'] = ('Leopard with star skin', f'<g fill="{INK}">' + ''.join(chunky_star(x, y, r, rnd) for x, y, r in pts) + '</g>')
pts, rnd = place(8, 21, 17, 7)
SKINS['dots'] = ('Leopard with polka-dot skin', f'<g fill="{INK}">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r:.1f}"/>' for x, y, r in pts) + '</g>')
pts, rnd = place(16, 32, 28, 9)
cel = []
for i, (x, y, r) in enumerate(pts):
    cel.append(crescent(x, y, r, rnd.uniform(-40, 40)) if i % 3 == 0 else sparkle(x, y, r * 1.15, rnd.uniform(-12, 12)) if i % 3 == 1
               else f'<circle cx="{x}" cy="{y}" r="{max(r * .3, 3.5):.1f}"/>')
SKINS['celestial'] = ('Leopard with moons and sparkles', f'<g fill="{INK}">' + ''.join(cel) + '</g>')
def heart(x, y, r, rot):
    return (f'<path transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f}) scale({r / 10:.2f})" '
            'd="M0 9C-1 7.5-10 2-10-4C-10-9-3-11 0-5.5C3-11 10-9 10-4C10 2 1 7.5 0 9Z"/>')
pts, rnd = place(13, 24, 26, 12)
SKINS['hearts'] = ('Leopard with heart skin', f'<g fill="{INK}">' + ''.join(heart(x, y, r, rnd.uniform(-25, 25)) for x, y, r in pts) + '</g>')

open('leopard-monoline.svg', 'w').write(doc('Leopard — clean monoline'))
for k, (title, skin) in SKINS.items():
    open(f'leopard-skin-{k}.svg', 'w').write(doc(title, skin))


print({k: v[1].count('<') for k, v in SKINS.items()})
