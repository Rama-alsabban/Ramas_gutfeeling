"""Clean, regular redraw of the two stacked pillows as vector paths, with the
standalone tassels placed on the corners."""
import re
import numpy as np

INK, CREAM, W_LINE = '#1e1e1d', '#f3eee4', 7

def P(x, y): return np.array([x, y], float)
def f(p): return f'{p[0]:.1f},{p[1]:.1f}'

def pillow(TL, TR, BR, BL, top_bow, side_bow, bot_bow):
    """Stuffed pillow: every edge bows outward, corners stay pinched to points."""
    w = TR[0] - TL[0]
    k = w * 0.30
    return (f'M{f(TL)} '
            f'C{f(TL + P(k, -top_bow))} {f(TR + P(-k, -top_bow))} {f(TR)} '
            f'C{f(TR + P(side_bow, (BR[1]-TR[1]) * 0.3))} {f(BR + P(side_bow, -(BR[1]-TR[1]) * 0.3))} {f(BR)} '
            f'C{f(BR + P(-k, bot_bow))} {f(BL + P(k, bot_bow))} {f(BL)} '
            f'C{f(BL + P(-side_bow, -(BL[1]-TL[1]) * 0.3))} {f(TL + P(-side_bow, (BL[1]-TL[1]) * 0.3))} {f(TL)}Z')

def seam(BL, BR, bot_bow, up, inset):
    """Piping line running just above the bottom edge."""
    a, b = BL + P(inset, -up), BR + P(-inset, -up)
    k = (b[0] - a[0]) * 0.30
    return f'M{f(a)} C{f(a + P(k, bot_bow))} {f(b + P(-k, bot_bow))} {f(b)}'

# geometry (px) — bottom pillow wider & flatter, top pillow plumper, resting on it
bTL, bTR, bBR, bBL = P(138, 326), P(882, 326), P(898, 476), P(122, 476)
tTL, tTR, tBR, tBL = P(186, 168), P(834, 168), P(820, 350), P(200, 350)

bottom = pillow(bTL, bTR, bBR, bBL, top_bow=6, side_bow=-12, bot_bow=30)
top = pillow(tTL, tTR, tBR, tBL, top_bow=44, side_bow=-18, bot_bow=24)
b_seam = seam(bBL, bBR, 30, 22, 26)
t_seam = seam(tBL, tBR, 24, 24, 24)

# tassels: reuse the traced standalone tassels (their own path data)
def load(name):
    s = open(name).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    body = s[s.index('<g>') + 3:s.index('</g>')]
    return vb, body
solid_vb, solid = load('final/TASSEL_SOLID.svg')
outl_vb, outl = load('final/TASSEL_OUTLINED.svg')

def place(vb, body, corner, angle, scale=1.0):
    # anchor = top centre of the loop (viewBox top + pad), rotate about it
    x0, y0, w, h = vb
    ax, ay = x0 + w / 2, y0 + 12 + 3
    return (f'<g transform="translate({corner[0]:.1f},{corner[1]:.1f}) rotate({angle}) '
            f'scale({scale}) translate({-ax:.1f},{-ay:.1f})">{body}</g>')

tassels = [
    place(solid_vb, solid, tTL + P(-2, 0), 28), place(solid_vb, solid, tTR + P(2, 0), -28),
    place(solid_vb, solid, tBL + P(2, -2), 8, 0.85), place(solid_vb, solid, tBR + P(-2, -2), -8, 0.85),
    place(outl_vb, outl, bBL + P(2, -2), 10), place(outl_vb, outl, bBR + P(-2, -2), -10),
]

stroke = f'fill="none" stroke="{INK}" stroke-width="{W_LINE}" stroke-linecap="round" stroke-linejoin="round"'
svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="40 40 940 560" width="940" height="560">
  <defs>
    <style>
      .st0 {{ fill: {CREAM}; }}
      .st1 {{ fill: {INK}; }}
    </style>
  </defs>
  <g id="bottom_pillow">
    <path class="st0" d="{bottom}"/>
    <path d="{b_seam}" {stroke}/>
    <path d="{bottom}" {stroke}/>
  </g>
  <g id="bottom_tassels">{tassels[4]}{tassels[5]}</g>
  <g id="top_pillow">
    <path class="st0" d="{top}"/>
    <path d="{t_seam}" {stroke}/>
    <path d="{top}" {stroke}/>
  </g>
  <g id="tassels">{"".join(tassels[:4])}</g>
</svg>
'''
open('final/PILLOWS_CLEAN.svg', 'w').write(svg)
print('ok')
