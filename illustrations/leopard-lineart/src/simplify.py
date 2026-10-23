"""Step 1: pull the ink out of the drawing and drop the fine detail.
Strokes thinner than the outline pen (hatching, ornament, fur flicks) are removed by a
morphological opening; the surviving strokes are then grown back inside the original ink
so outlines keep their hand-drawn shape. Writes src/ink_<level>.png at 2x scale."""
import sys, cv2, numpy as np
SC = 2
im = cv2.imread('src/original.jpg', cv2.IMREAD_GRAYSCALE)
im = cv2.resize(im, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
im = cv2.GaussianBlur(im, (3, 3), 0)
ink = (im < 120).astype(np.uint8) * 255                      # paper ~235, ink ~40
ink[:, :int(60 * SC)] = 0                                     # nothing on the far left/right margins
disk = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))

def level(r_open, grow, min_area):
    core = cv2.morphologyEx(ink, cv2.MORPH_OPEN, disk(r_open))
    out = core
    for _ in range(grow):                                      # geodesic dilation, capped by real ink
        out = cv2.min(cv2.dilate(out, disk(1)), ink)
    n, lab, st, _ = cv2.connectedComponentsWithStats(out, 8)
    keep = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= min_area])
    out = np.where(keep, 255, 0).astype(np.uint8)
    return cv2.morphologyEx(out, cv2.MORPH_CLOSE, disk(1))

LEVELS = {'medium': (2, 6, 60), 'minimal': (3, 8, 120)}
if __name__ == '__main__':
    cv2.imwrite('src/ink_full.png', 255 - ink)
    for name, args in LEVELS.items():
        cv2.imwrite(f'src/ink_{name}.png', 255 - level(*args))
