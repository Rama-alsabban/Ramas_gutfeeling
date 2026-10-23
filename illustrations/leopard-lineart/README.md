# Resting leopard — simplified line art (vector)

A vector version of the pen-and-ink leopard-on-cushions drawing with less detail, keeping the same hand-inked line.

![Original (top) and simplified vector (bottom)](preview.png)

- `leopard-lineart.svg`: ink `#2c2b22` on paper `#f1ebdf`
- `leopard-lineart-transparent.svg`: the same drawing with no background

What was simplified: the cushion hatching and the ornamental band are gone, and there are fewer fur flicks.
The outlines, spots, tassels, piping, face and whiskers stay as drawn. Every line is traced from the original
artwork, so the stroke weight still looks hand-drawn. The ink is one group (`#ink`), so you can recolour it in one place.

Regenerate (needs `pip install opencv-python-headless vtracer numpy`):

```sh
cd illustrations/leopard-lineart
python3 src/compose.py && python3 src/trace.py
```
`src/simplify.py` sets how much detail is removed (`LEVELS`). `src/compose.py` decides which level each region uses.

## Compositions with shapes

`compositions/` sets the leopard with decorative elements drawn in the same engraving technique. The approach:
use a few elements at a confident scale, make them interlock with the figure (behind it, in front of it, or broken
by it), and build tone from engraved line work rather than flat outlines. Each file has `behind`, `leopard` and
`front` groups. A solid silhouette (`src/silhouette.py`) stops anything behind the leopard from showing through.

![Compositions](compositions/preview.png)

- `a-engraved-stars.svg`: two large faceted stars, one behind the back and one crossing the cushion, as in the reference
- `b-night-medallion.svg`: an engraved night-sky disc with a knocked-out moon and stars; the leopard breaks its edge
- `c-arched-niche.svg`: an arched niche with a fine ray burst; tassels and paws break out of the frame

Shapes and positions are set in `src/compositions.py` (`python3 src/compositions.py`).
