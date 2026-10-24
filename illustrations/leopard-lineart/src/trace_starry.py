"""Trace the minimal outline and lay stars where the rosettes were. Writes leopard-stars*.svg"""
import json, math, re, vtracer
INK, PAPER = '#2c2b22', '#f1ebdf'
vtracer.convert_image_to_svg_py('src/ink_minimal_outline.png', 'src/_m.svg', colormode='binary', mode='spline',
    filter_speckle=8, corner_threshold=60, length_threshold=3.5, splice_threshold=45, path_precision=1)
svg = open('src/_m.svg').read()
paths = ''.join(f'<path d="{d}" transform="translate({x},{y})"/>' for d, x, y in
                re.findall(r'<path d="([^"]+)"[^>]*transform="translate\(([-\d.]+),([-\d.]+)\)"', svg))

def star(cx, cy, R, rot):
    """Solid 4-point star with gently concave sides; the vertical ray a little longer."""
    k = R * .2; v = R * 1.25
    d = (f'M0 {-v:.1f}Q{k:.1f} {-k:.1f} {R:.1f} 0Q{k:.1f} {k:.1f} 0 {v:.1f}Q{-k:.1f} {k:.1f} {-R:.1f} 0Q{-k:.1f} {-k:.1f} 0 {-v:.1f}Z')
    return f'<path transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.1f})" d="{d}"/>'
stars = ''.join(star(x, y, s * .62, r) for x, y, s, r in json.load(open('src/star_spots.json')))
INK_G = f'<g id="ink" fill="{INK}"><g transform="scale(0.5)">{paths}</g><g id="stars">{stars}</g></g>'
open('src/ink_stars_group.svgfrag', 'w').write(INK_G)
for name, bg in [('leopard-stars', f'<rect id="paper" width="100%" height="100%" fill="{PAPER}"/>'), ('leopard-stars-transparent', '')]:
    open(f'{name}.svg', 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="1536" height="1024">\n'
                                   f'<title>Starry leopard — minimal line art</title>\n{bg}\n{INK_G}\n</svg>\n')
