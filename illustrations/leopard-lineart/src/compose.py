"""Step 2: combine detail levels by region and trace the result to SVG.
 - leopard: 'minimal' (outlines + spots, fewer fur flicks)
 - whiskers: kept from 'medium'
 - cushions: only long strokes survive (outlines, piping, tassels); hatching and ornament go."""
import sys, cv2, numpy as np
sys.path.insert(0, 'src')
from simplify import level, LEVELS, SC, ink
med, mini = level(*LEVELS['medium']), level(*LEVELS['minimal'])
H, W = ink.shape
out = mini.copy()
y0, y1, x0, x1 = [int(v * SC) for v in (290, 410, 270, 395)]          # whisker box
out[y0:y1, x0:x1] = med[y0:y1, x0:x1]
pillow = np.zeros_like(ink)
cv2.fillPoly(pillow, [(np.array([(90, 400), (330, 400), (360, 445), (620, 445), (800, 470), (835, 490),
                                 (828, 800), (90, 800)]) * SC).astype(np.int32)], 255)
cush = cv2.bitwise_and(med, pillow)
n, lab, st, _ = cv2.connectedComponentsWithStats(cush, 8)
big = np.isin(lab, [i for i in range(1, n) if max(st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]) >= 70 * SC])
out[pillow > 0] = 0
out[big] = 255
band = np.zeros_like(ink)                                               # inside of the ornament band
cv2.fillPoly(band, [(np.array([(252, 621), (500, 621), (752, 620), (772, 650), (788, 700), (792, 719), (252, 719)]) * SC).astype(np.int32)], 255)
out[band > 0] = 0
cv2.imwrite('src/ink_final.png', 255 - out)
