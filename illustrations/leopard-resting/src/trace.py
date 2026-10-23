"""Step 1: crop the artwork out of the source image and clean it up for tracing (writes src/art_prepped.png)."""
import cv2
im = cv2.imread('src/original.jpg')
art = im[100:690, 60:1130].copy()          # drop the cut-off bell on the left edge + the captions
art = cv2.resize(art, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
art = cv2.bilateralFilter(art, 9, 40, 9)   # smooth JPEG noise, keep edges
cv2.imwrite('src/art_prepped.png', art)
