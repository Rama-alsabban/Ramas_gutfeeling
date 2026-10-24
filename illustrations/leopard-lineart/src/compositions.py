"""Leopard line art + decorative elements rendered in the same engraving technique. Writes compositions/*.svg

Principles: few elements at a confident scale; elements interlock with the figure (pass behind it,
cross in front of it, or get broken by it); tone comes from engraved line work, never flat cartoon outlines."""
import json, math, re, os
INK, PAPER = '#2c2b22', '#f1ebdf'
art = open('leopard-lineart-transparent.svg').read()
INK_G = re.search(r'<g id="ink".*?</g>', art, re.S).group()
STARRY_G = open('src/ink_stars_group.svgfrag').read()
SIL = f'<g id="silhouette" fill="{PAPER}" transform="scale(0.5)">' + ''.join(json.load(open('src/silhouette.json'))) + '</g>'

def stroke(w, join='round'): return f'fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="{join}"'
def P(p, close=True): return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in p) + ('Z' if close else '')
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def engraved_star(cx, cy, R, n=8, short=.5, inner=.2, rot=-90, lines=9):
    """Faceted star: every ray is split down its axis, one facet left in light, the other cut
    with lines converging on the tip - the way an engraver shades a carved star."""
    tips, valleys = [], []
    for i in range(n):
        a = math.radians(rot + i * 360 / n); r = R if i % 2 == 0 else R * short
        tips.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        b = a + math.pi / n
        valleys.append((cx + R * inner * math.cos(b), cy + R * inner * math.sin(b)))
    c = (cx, cy); out = []
    outline = []
    for i in range(n):
        outline += [tips[i], valleys[i]]
    out.append(f'<path d="{P(outline)}" fill="{PAPER}"/>')
    hatch = []
    for i in range(n):
        tip, v = tips[i], valleys[i]                       # shaded facet: centre - tip - next valley
        for k in range(1, lines + 1):
            b = lerp(c, v, k / (lines + 1))
            hatch.append(P([b, lerp(b, tip, .92 - .05 * k / lines)], False))
        out.append(f'<path d="{P([c, tip], False)}" {stroke(1.4)}/>')     # ridge line
    out.append(f'<path d="{"".join(hatch)}" {stroke(1.3)}/>')
    out.append(f'<path d="{P(outline)}" {stroke(3.2, "miter")}/>')
    return ''.join(out)

def twinkle(cx, cy, R, knock=False):
    k = R * .16
    d = (f'M{cx} {cy-R}Q{cx+k} {cy-k} {cx+R} {cy}Q{cx+k} {cy+k} {cx} {cy+R}Q{cx-k} {cy+k} {cx-R} {cy}Q{cx-k} {cy-k} {cx} {cy-R}Z')
    return f'<path d="{d}" fill="{PAPER}" ' + ('/>' if knock else f'stroke="{INK}" stroke-width="2"/>')

def hlines(x0, x1, y0, y1, sp, w=1.8, grad=None):
    """Horizontal engraving lines; grad spaces them closer toward the top (sky darkening)."""
    d, y = [], y0
    while y < y1:
        d.append(f'M{x0} {y:.1f}H{x1}')
        t = (y - y0) / (y1 - y0)
        y += sp * (0.75 + 0.9 * t if grad else 1)
    return f'<path d="{"".join(d)}" {stroke(w)}/>'

def ground(cx, y, half):
    """A quiet double rule that seats the cushions, the way a vignette sits on a printed page."""
    return f'<path d="M{cx-half} {y}H{cx+half}" {stroke(2.2)}/><path d="M{cx-half*.72:.0f} {y+9}H{cx+half*.72:.0f}" {stroke(1.2)}/>'

def doc(title, defs='', behind='', front='', ink=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="1536" height="1024">\n<title>{title}</title>\n'
            f'<defs>{defs}</defs>\n<rect width="100%" height="100%" fill="{PAPER}"/>\n<g id="behind">{behind}</g>\n'
            f'<g id="leopard">{SIL}{ink or INK_G}</g>\n<g id="front">{front}</g>\n</svg>\n')

C = {}

# A - two large engraved stars interlocking with the body, as in the reference
C['a-engraved-stars'] = doc('Leopard with engraved stars',
    behind=engraved_star(1120, 290, 255),
    front=engraved_star(655, 790, 160, rot=-78))

# B - an engraved night-sky medallion; the leopard sits in front of it and breaks its edge
cx, cy, r = 770, 430, 390
moon = f'M{1000} {170}A110 110 0 1 0 {1000} {390}A128 128 0 0 1 {1000} {170}Z'
sky = (f'<clipPath id="disc"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
       f'<g clip-path="url(#disc)">{hlines(cx-r, cx+r, cy-r+6, cy+r, 7.5, 1.7, grad=True)}'
       f'<path d="{moon}" fill="{PAPER}"/><path d="{moon}" {stroke(2)}/>'
       + ''.join(twinkle(x, y, s, knock=True) for x, y, s in [(560, 150, 20), (690, 105, 11), (480, 250, 9), (830, 205, 13), (1130, 330, 10), (395, 380, 12)]) +
       '</g>')
C['b-night-medallion'] = doc('Leopard before a night-sky medallion',
    behind=sky + f'<circle cx="{cx}" cy="{cy}" r="{r}" {stroke(3)}/><circle cx="{cx}" cy="{cy}" r="{r+12}" {stroke(1.4)}/>' + ground(775, 848, 700))
C['d-starry-medallion'] = doc('Starry leopard before a night-sky medallion', ink=STARRY_G,
    behind=sky + f'<circle cx="{cx}" cy="{cy}" r="{r}" {stroke(3)}/><circle cx="{cx}" cy="{cy}" r="{r+12}" {stroke(1.4)}/>' + ground(775, 848, 700))

# C - arched niche with a fine ray burst; tassels and paws break out of the frame
L, Rt, top, base, spring = 300, 1240, 95, 845, 470
arch = f'M{L} {base}V{spring}A{(Rt-L)/2} {spring-top} 0 0 1 {Rt} {spring}V{base}'
rays = []
for i in range(73):
    a = math.radians(180 + i * 2.5)
    rays.append(f'M{770+150*math.cos(a):.0f} {700+150*math.sin(a):.0f}L{770+1100*math.cos(a):.0f} {700+1100*math.sin(a):.0f}')
C['c-arched-niche'] = doc('Leopard in an arched niche',
    behind=(f'<clipPath id="arch"><path d="{arch}Z"/></clipPath>'
            f'<path d="{"".join(rays)}" {stroke(1.5)} clip-path="url(#arch)"/>'
            f'<path d="{arch}" {stroke(3.2)}/>'
            f'<path d="M{L-14} {base}V{spring}A{(Rt-L)/2+14} {spring-top+14} 0 0 1 {Rt+14} {spring}V{base}" {stroke(1.4)}/>'
            + engraved_star(770, top - 2, 46, inner=.14) +
            ground(775, base + 3, 700)))

os.makedirs('compositions', exist_ok=True)
for f in os.listdir('compositions'):
    if f.endswith('.svg'): os.remove(f'compositions/{f}')
for k, v in C.items(): open(f'compositions/{k}.svg', 'w').write(v)
