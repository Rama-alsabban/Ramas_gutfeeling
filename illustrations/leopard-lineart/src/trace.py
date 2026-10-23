"""Step 3: trace src/ink_final.png into a single-colour SVG in the original's ink and paper colours."""
import re, vtracer
INK, PAPER, SC = '#2c2b22', '#f1ebdf', 2
vtracer.convert_image_to_svg_py('src/ink_final.png', 'src/_traced.svg', colormode='binary', mode='spline',
    filter_speckle=6, corner_threshold=60, length_threshold=3.5, splice_threshold=45, path_precision=1)
svg = open('src/_traced.svg').read()
paths = ''.join(f'<path d="{d}" transform="translate({x},{y})"/>' for d, x, y in
                re.findall(r'<path d="([^"]+)"[^>]*transform="translate\(([-\d.]+),([-\d.]+)\)"', svg))
w, h = 1536, 1024
for name, bg in [('leopard-lineart', f'<rect id="paper" width="100%" height="100%" fill="{PAPER}"/>'),
                 ('leopard-lineart-transparent', '')]:
    open(f'{name}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
        f'<title>Resting leopard — line art</title>\n{bg}\n'
        f'<g id="ink" fill="{INK}" transform="scale({1/SC})">{paths}</g>\n</svg>\n')
