"""Shared SVG builder: turns the traced tone layers (src/layers.json) into styled SVGs."""
import json, re
L = json.load(open('src/layers.json'))
W, H = L['W'], L['H']
S = 1/3                       # trace was done at 3x; scale back to the original pixel size
NUM = re.compile(r'-?\d+(?:\.\d+)?')

def _bake(d, dx, dy):
    """Fold vtracer's translate() into the absolute M/C/Z coordinates."""
    i = [0]
    def f(m):
        v = float(m.group()) + (dx if i[0] % 2 == 0 else dy); i[0] += 1
        return f'{v:.1f}'.rstrip('0').rstrip('.')
    return NUM.sub(f, d)

LAYERS = [[_bake(*p) for p in lay['d']] if k else [] for k, lay in enumerate(L['layers'])]
ORIGINAL = [l['hex'] for l in L['layers']]
ORIGINAL[0] = '#eddfd2'
SERIF = "'Cormorant Garamond', Cormorant, Garamond, 'Liberation Serif', 'Times New Roman', serif"
ART_W, ART_H = W * S, H * S
CAP_H = 230

def layers_svg(fills, attrs=None, gid=''):
    """Tone layers back-to-front. fills[i] is a colour/url per layer; None skips it."""
    out = [f'<g {gid} transform="scale({S:.6f})">']
    for i in range(1, len(LAYERS)):
        f = fills[i]
        if f is None: continue
        a = (attrs or {}).get(i, '')
        out.append(f'<use href="#tone-{i:02d}" fill="{f}" {a}/>')
    out.append('</g>')
    return '\n'.join(out)

def caption(fill, font=SERIF, weight='400', size=(34, 24), spacing=(9, 6), extra=''):
    cx = ART_W / 2 - 30
    return (f'<g fill="{fill}" font-family="{font}" font-weight="{weight}" text-anchor="middle" {extra}>'
            f'<text x="{cx:.0f}" y="{ART_H + 110:.0f}" font-size="{size[0]}" letter-spacing="{spacing[0]}">06. RESTING</text>'
            f'<text x="{cx:.0f}" y="{ART_H + 172:.0f}" font-size="{size[1]}" letter-spacing="{spacing[1]}">COMPLETELY AT EASE</text></g>')

GEOMETRY = ''.join(f'<g id="tone-{i:02d}">' + ''.join(f'<path d="{d}"/>' for d in LAYERS[i]) + '</g>'
                   for i in range(1, len(LAYERS)))

def doc(title, body, defs='', bg='#eddfd2', geometry=True):
    w, h = ART_W, ART_H + CAP_H
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">\n'
            f'<title>{title}</title>\n<defs>{defs}{GEOMETRY if geometry else ""}</defs>\n'
            f'<rect width="100%" height="100%" fill="{bg}"/>\n{body}\n</svg>\n')
