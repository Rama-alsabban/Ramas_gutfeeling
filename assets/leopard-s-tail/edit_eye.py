"""Redraw the far (left) eye as a heavy-lidded, content half-blink that
matches the near eye. Works on the 4x composed raster."""
import sys
import cv2, numpy as np

src, out = sys.argv[1], sys.argv[2]
K = 4
INK = (30, 30, 29)
FILL = (234, 212, 195)       # face light blue (BGR)
GLINT = (226, 238, 244)      # same cream as the near eye's highlight

im = cv2.imread(src)
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# 1. erase the old eye: everything dark right of the face silhouette in the eye box
# left edge of the face silhouette line (orig px), measured from the drawing
SIL = np.array([(96, 375), (108, 369), (114, 367), (120, 365), (123, 363), (126, 361),
                (129, 360), (132, 359), (135, 358), (141, 358), (144, 357), (147, 358), (157, 358)])
SIL_W = 9.5  # silhouette line width
for y in range(106 * K, 157 * K):  # down to where the old line met the muzzle
    x_cut = int(round((np.interp(y / K, SIL[:, 0], SIL[:, 1]) + SIL_W) * K))
    im[y, x_cut:404 * K] = FILL   # right of the silhouette is all face

# 2. new eye: almond from outer corner (at the silhouette) to inner corner
def bez(p0, c, p1, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t ** 2 * p1

O = np.array([372.5, 113.5])    # outer corner, tucked into the silhouette line
I = np.array([401.0, 125.5])    # inner corner
T = np.array([406.0, 131.0])    # little tear-duct flick toward the nose, like the near eye
top = bez(O, np.array([388.0, 106.5]), I)          # heavy upper lid
bot = bez(I, np.array([386.0, 128.0]), O)          # nearly flat lower lid
flick_top = bez(I, np.array([404.0, 127.0]), T, 12)
flick_bot = bez(T, np.array([402.0, 129.5]), I - [3.0, -1.0], 12)
shape = np.vstack([top, flick_top, flick_bot, bot])
cv2.fillPoly(im, [(shape * K).astype(np.int32)], INK, cv2.LINE_AA)

# 3. a sliver of glint under the lid: a calm, half-closed look
gl = bez(np.array([386.0, 118.8]), np.array([389.0, 119.2]), np.array([392.0, 120.6]), 30)
cv2.polylines(im, [(gl * K).astype(np.int32)], False, GLINT, int(1.6 * K), cv2.LINE_AA)

cv2.imwrite(out, im)
