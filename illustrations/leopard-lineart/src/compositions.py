"""Leopard line art + decorative shapes drawn in the same ink style. Writes compositions/*.svg"""
import json, math, re, os
INK, PAPER, SW = '#2c2b22', '#f1ebdf', 4.5
art = open('leopard-lineart-transparent.svg').read()
INK_G = re.search(r'<g id="ink".*?</g>', art, re.S).group()
SIL = f'<g id="silhouette" fill="{PAPER}" transform="scale(0.5)">' + ''.join(json.load(open('src/silhouette.json'))) + '</g>'
LEOPARD = SIL + INK_G
def line(w=SW, join='round'): return f'stroke="{INK}" stroke-width="{w}" stroke-linejoin="{join}" stroke-linecap="round"'
def shape(w=SW, join='round'): return f'fill="{PAPER}" {line(w, join)}'

def pts(p): return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in p) + 'Z'

def sparkle(cx, cy, R, n=8, short=.55, inner=.14, rot=-90):
    """Thin-rayed star like the reference: n rays alternating long/short."""
    p = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        r = (R if (i // 2) % 2 == 0 else R * short) if i % 2 == 0 else R * inner
        p.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return f'<path d="{pts(p)}" {shape(join="miter")}/>'

def twinkle(cx, cy, R):          # small 4-point star with curved sides
    k = R * .18
    return (f'<path d="M{cx} {cy-R}Q{cx+k} {cy-k} {cx+R} {cy}Q{cx+k} {cy+k} {cx} {cy+R}'
            f'Q{cx-k} {cy+k} {cx-R} {cy}Q{cx-k} {cy-k} {cx} {cy-R}Z" {shape()}/>')

def dot(cx, cy, r=5): return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}"/>'

def hatch_clip(id, d, x0, y0, x1, y1, sp=9, ang=-35):
    """Engraving-style shading: parallel ink lines clipped to a shape."""
    L = []; w = x1 - x0
    for i in range(-int(w * 1.5 / sp), int(w * 1.5 / sp)):
        x = x0 + i * sp
        L.append(f'M{x} {y0}l{(y1-y0) * math.tan(math.radians(ang)):.1f} {y1-y0}')
    return (f'<clipPath id="{id}"><path d="{d}"/></clipPath>'
            f'<path d="{"".join(L)}" clip-path="url(#{id})" stroke="{INK}" stroke-width="2.2" fill="none"/>')

def heart(cx, cy, s, rot=0, shade=True, id='h'):
    d = (f'M0 {0.35*s}C{-0.05*s} {0.25*s} {-0.55*s} {-0.05*s} {-0.5*s} {-0.32*s}C{-0.45*s} {-0.6*s} {-0.08*s} {-0.62*s} 0 {-0.33*s}'
         f'C{0.08*s} {-0.62*s} {0.45*s} {-0.6*s} {0.5*s} {-0.32*s}C{0.55*s} {-0.05*s} {0.05*s} {0.25*s} 0 {0.35*s}Z')
    shading = ''
    if shade:   # crescent of hatching on the right side, like a tattoo-flash heart
        inner = f'M{0.5*s} {-0.6*s}L{0.6*s} {0.4*s}L{0.1*s} {0.4*s}C{0.38*s} {0.05*s} {0.42*s} {-0.2*s} {0.3*s} {-0.42*s}Z'
        shading = f'<clipPath id="{id}c"><path d="{d}"/></clipPath><g clip-path="url(#{id}c)">' + \
                  hatch_clip(id + 'i', inner, -s, -s, s, s, sp=8, ang=-30) + '</g>'
    return (f'<g transform="translate({cx} {cy}) rotate({rot})"><path d="{d}" {shape()}/>{shading}'
            f'<path d="M{-0.33*s} {-0.3*s}Q{-0.3*s} {-0.42*s} {-0.18*s} {-0.44*s}" fill="none" {line(3)}/></g>')

def bolt(cx, cy, s, rot=0):
    p = [(-.12, -.5), (.22, -.5), (.05, -.1), (.25, -.1), (-.15, .5), (-.02, .05), (-.2, .05)]
    return f'<g transform="translate({cx} {cy}) rotate({rot})"><path d="{pts([(x*s, y*s) for x, y in p])}" {shape(join="miter")}/></g>'

def moon(cx, cy, R):
    """Crescent opening to the right, with hatching along the inner edge."""
    Ri = R * 1.15                    # inner circle passes through both horns, offset to the right
    d = f'M{cx} {cy-R}A{R} {R} 0 0 0 {cx} {cy+R}A{Ri:.1f} {Ri:.1f} 0 0 1 {cx} {cy-R}Z'
    return f'<path d="{d}" {shape()}/>' + hatch_clip('mh', d, cx - R, cy - R, cx + R, cy + R, sp=10, ang=-25) + \
           f'<path d="{d}" fill="none" {line()}/>'

def sunburst(cx, cy, r0, r1, n=56):
    rays = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = r1 if i % 2 == 0 else r0 + (r1 - r0) * .62
        w = .018 if i % 2 == 0 else .012
        rays.append(pts([(cx + r0 * math.cos(a - w), cy + r0 * math.sin(a - w)), (cx + r * math.cos(a), cy + r * math.sin(a)),
                         (cx + r0 * math.cos(a + w), cy + r0 * math.sin(a + w))]))
    return f'<path d="{"".join(rays)}" {shape(3.5, "miter")}/>'

def zzz():
    f = "'Cormorant Garamond', 'Liberation Serif', Georgia, serif"
    return (f'<g fill="{INK}" font-family="{f}" font-style="italic" font-weight="600">'
            f'<text x="455" y="205" font-size="44">z</text><text x="500" y="160" font-size="62">z</text>'
            f'<text x="560" y="100" font-size="84">Z</text></g>')

def doc(title, behind='', front=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="1536" height="1024">\n<title>{title}</title>\n'
            f'<rect width="100%" height="100%" fill="{PAPER}"/>\n<g id="behind">{behind}</g>\n<g id="leopard">{LEOPARD}</g>\n<g id="front">{front}</g>\n</svg>\n')

C = {
 'a-sparkles': doc('Leopard with sparkles',
     behind=sparkle(1160, 250, 190) + sparkle(250, 190, 95, short=.5),
     front=sparkle(690, 800, 165) + sparkle(1400, 610, 70) + twinkle(560, 160, 22) + twinkle(1330, 900, 18)),
 'b-moon-and-stars': doc('Leopard with moon and stars',
     behind=moon(250, 230, 120) + twinkle(1180, 210, 30) + twinkle(1320, 330, 18) + twinkle(130, 470, 16) +
            twinkle(980, 160, 14) + ''.join(dot(x, y, r) for x, y, r in [(1080, 250, 5), (1250, 150, 4), (1420, 250, 5), (90, 330, 4), (400, 120, 4)]),
     front=zzz()),
 'c-sunburst': doc('Leopard with sunburst', behind=sunburst(775, 530, 120, 470) +
     f'<circle cx="775" cy="530" r="490" fill="none" {line(2.5)} stroke-dasharray="2 12"/>'),
 'd-hearts-and-bolts': doc('Leopard with hearts and lightning',
     behind=heart(1210, 230, 170, rot=14, id='h1') + bolt(260, 190, 190, rot=12) + twinkle(1400, 120, 22) + dot(150, 130, 5) + dot(1330, 380, 4),
     front=heart(700, 840, 120, rot=-12, id='h2') + bolt(1420, 700, 110, rot=-18) + twinkle(560, 170, 20)),
}
os.makedirs('compositions', exist_ok=True)
for k, v in C.items(): open(f'compositions/{k}.svg', 'w').write(v)
