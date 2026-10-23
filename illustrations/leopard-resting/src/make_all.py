"""Step 3: generate every style variant. Run from illustrations/leopard-resting:  python3 src/make_all.py
Tone layer index -> what it mostly holds in the artwork:
 1 lightest fur / silhouette   2-5 fur shading   7, 9 warm brown shading
 6, 8, 10 cushion (light -> dark)   11-13 spots, outlines and darkest shadows"""
import sys; sys.path.insert(0, 'src')
from build import *

def pal(default, **by_idx):
    p = [default] * 14
    for k, v in by_idx.items():
        for i in k.split('_')[1:]: p[int(i)] = v
    return p

files = {}

# 01 — faithful vector: the 14 traced colours as-is
files['01-vector-faithful'] = doc('06. Resting — vector', layers_svg(ORIGINAL) + caption('#4a3a36'))

# 02 — flat poster: same shapes, collapsed to 6 flat colours
p = pal('#e9a964', l_1_2='#f6dcb3', l_3_4_5_7='#e2a35f', l_9='#b06a36',
        l_6_8='#b8566e', l_10='#8a3552', l_11_12_13='#2b1a14')
files['02-flat-poster'] = doc('06. Resting — flat poster', layers_svg(p) + caption('#2b1a14', weight='600'), bg='#f4e7d6')

# 03 — ink engraving: hatch density stands in for tone
ink, paper = '#1d1b1a', '#fbf8f1'
def hatch(id, sp, lw, angles):
    lines = ''.join(f'<path d="M-{sp} 0H{sp*2}" transform="rotate({a} {sp/2} {sp/2})" stroke="{ink}" stroke-width="{lw}"/>' for a in angles)
    return (f'<pattern id="{id}" width="{sp}" height="{sp}" patternUnits="userSpaceOnUse">'
            f'<rect width="{sp}" height="{sp}" fill="{paper}"/>{lines}</pattern>')
defs = (hatch('h1', 20, 2.2, [45]) + hatch('h2', 13, 2.6, [45]) + hatch('h3', 13, 2.6, [45, -45]) +
        hatch('h4', 9, 3, [45, -45]) + hatch('h5', 7, 3.2, [45, -45, 0]) + hatch('hc', 11, 2.6, [0]) + hatch('hc2', 8, 2.8, [0, 45]))
p = [None, paper, paper, 'url(#h1)', 'url(#h1)', 'url(#h2)', 'url(#hc)', 'url(#h3)', 'url(#hc2)', 'url(#h4)', 'url(#h5)', 'url(#h5)', ink, ink]
files['03-ink-engraving'] = doc('06. Resting — ink engraving',
    layers_svg(p, attrs={1: f'stroke="{ink}" stroke-width="5" stroke-linejoin="round"'}) + caption(ink), defs, bg=paper)

# 04 — risograph: two inks (fluoro pink + blue), multiplied and slightly mis-registered
def mix(c, a, base=(255, 255, 255)):
    c = [int(c[i:i+2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(b + (x - b) * a) for x, b in zip(c, base))
pink, blue, rpaper = '#ff48b0', '#0078bf', '#f5efe3'
pa = [0, .08, .18, .28, .38, .48, .85, .55, .95, .6, 1, .7, .8, .9]
ba = [0, 0, 0, .05, .1, .18, .05, .28, .15, .4, .35, .65, .85, 1]
defs = ('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="4"/>'
        '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 0.75"/></filter>')
body = (f'<g style="mix-blend-mode:multiply">{layers_svg([None] + [mix(pink, a) for a in pa[1:]])}</g>'
        f'<g style="mix-blend-mode:multiply" transform="translate(3 2)">{layers_svg([None] + [mix(blue, a) if a else None for a in ba[1:]])}</g>'
        + caption(blue, extra='style="mix-blend-mode:multiply"') +
        '<rect width="100%" height="100%" filter="url(#grain)" opacity=".35"/>')
files['04-risograph'] = doc('06. Resting — risograph', body, defs, bg=rpaper)

# 05 — pop art: loud flats, halftone dots, heavy outline
defs = ('<pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="#2ec4f1"/><circle cx="7" cy="7" r="2.6" fill="#1b9fd0"/></pattern>'
        '<pattern id="od" width="15" height="15" patternUnits="userSpaceOnUse"><rect width="15" height="15" fill="#ffb000"/><circle cx="7.5" cy="7.5" r="4.4" fill="#ff6a00"/></pattern>'
        '<pattern id="pd" width="15" height="15" patternUnits="userSpaceOnUse"><rect width="15" height="15" fill="#ff2d8a"/><circle cx="7.5" cy="7.5" r="4.4" fill="#c4006a"/></pattern>')
p = [None, '#ffe14d', '#ffe14d', '#ffd000', 'url(#od)', 'url(#od)', '#ff2d8a', '#ff6a00', 'url(#pd)', '#e04a00', '#a3005a', '#111', '#111', '#111']
files['05-pop-art'] = doc('06. Resting — pop art',
    layers_svg(p, attrs={1: 'stroke="#111" stroke-width="12" stroke-linejoin="round"'}) +
    caption('#111', font="Impact, 'Arial Black', 'Helvetica Neue', sans-serif", weight='900', size=(44, 28), spacing=(6, 4)),
    defs, bg='url(#dots)')

# 06 — art deco: gold-leaf leopard, emerald cushion, midnight ground, framed
navy, gold = '#0f1a2b', '#d8b35e'
p = [None, '#f6e6b8', '#ecd08a', '#dcb466', '#c79a4c', '#ad8139', '#2a8070', '#94692c', '#1d6657', '#74511f', '#124a3f', '#3a2a17', '#1c140b', '#0b0805']
fw, fh = ART_W, ART_H + CAP_H
frame = (f'<g fill="none" stroke="{gold}"><rect x="22" y="22" width="{fw-44:.0f}" height="{fh-44:.0f}" stroke-width="2"/>'
         f'<rect x="32" y="32" width="{fw-64:.0f}" height="{fh-64:.0f}" stroke-width="1"/></g>' +
         ''.join(f'<path d="M{x} {y}l{sx*40} 0M{x} {y}l0 {sy*40}M{x+sx*8} {y+sy*8}l{sx*22} 0M{x+sx*8} {y+sy*8}l0 {sy*22}" stroke="{gold}" stroke-width="3"/>'
                 for x, y, sx, sy in [(42, 42, 1, 1), (fw-42, 42, -1, 1), (42, fh-42, 1, -1), (fw-42, fh-42, -1, -1)]) +
         f'<path d="M{fw/2-30-160:.0f} {ART_H+138:.0f}h120M{fw/2-30+40:.0f} {ART_H+138:.0f}h120" stroke="{gold}" stroke-width="1"/>'
         f'<path d="M{fw/2-30:.0f} {ART_H+130:.0f}l8 8-8 8-8-8z" fill="{gold}"/>')
files['06-art-deco'] = doc('06. Resting — art deco', layers_svg(p) + frame + caption(gold), bg=navy)

# 07 — watercolour: pastel washes, wobbly edges, paper texture
defs = ('<filter id="wash" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="7" result="n"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="10" xChannelSelector="R" yChannelSelector="G" result="d"/><feGaussianBlur in="d" stdDeviation="0.7"/></filter>'
        '<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="2"/>'
        '<feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.30  0 0 0 -0.9 0.55"/></filter>')
p = [None, '#fde8cc', '#f9d6ad', '#f2c290', '#e9ad7c', '#da986b', '#e9aec4', '#c98761', '#dc8fae', '#b07258', '#c27397', '#8d6c7e', '#6e5069', '#56405b']
files['07-watercolour'] = doc('06. Resting — watercolour',
    f'<g filter="url(#wash)" opacity=".93">{layers_svg(p)}</g>' + caption('#6e5069', extra='font-style="italic"') +
    '<rect width="100%" height="100%" filter="url(#paper)" opacity=".5"/>', defs, bg='#fbf5ee')

# 08 — stencil: one dark silhouette, spots knocked out, cushion in a single flat tone
dark, cream = '#3a2420', '#eddfd2'
p = pal(dark, l_6_8_10='#9c5a63', l_11_12_13=cream)
files['08-stencil'] = doc('06. Resting — stencil', layers_svg(p) + caption(dark, weight='600'), bg=cream)


# 09 — pixel art: a 1-bit-era sprite built from <rect>s (a nod to the site's Win95 desktop)
import cv2, numpy as np
src = cv2.imread('src/original.jpg')[100:690, 60:1130]
PX = 9                                              # one sprite pixel = 9 original pixels
small = cv2.resize(src, (src.shape[1] // PX, src.shape[0] // PX), interpolation=cv2.INTER_AREA)
pix = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).reshape(-1, 3).astype(np.float32)
sprite_pal = np.array([[237, 223, 210], [246, 226, 190], [226, 186, 135], [190, 140, 92], [140, 96, 60],
                       [168, 92, 104], [128, 64, 80], [90, 44, 58], [62, 36, 24], [28, 16, 10]], np.float32)
idx = ((pix[:, None] - sprite_pal[None]) ** 2).sum(-1).argmin(1).reshape(small.shape[:2])
rects = []
for y, row in enumerate(idx):
    x = 0
    while x < len(row):
        k, x0 = row[x], x
        while x < len(row) and row[x] == k: x += 1
        if k: rects.append(f'<rect x="{x0*PX}" y="{y*PX}" width="{(x-x0)*PX}" height="{PX}" fill="#%02x%02x%02x"/>' % tuple(int(v) for v in sprite_pal[k]))
pixfont = "'Press Start 2P', 'VT323', 'Courier New', monospace"
files['09-pixel-art'] = doc('06. Resting — pixel art',
    f'<g shape-rendering="crispEdges">{"".join(rects)}</g>' +
    caption('#1c100a', font=pixfont, weight='700', size=(30, 20), spacing=(4, 3)), bg='#eddfd2', geometry=False)

for name, svg in files.items():
    open(f'{name}.svg', 'w').write(svg)
    print(name, len(svg) // 1024, 'KB')
