# -*- coding: utf-8 -*-
"""Detect the cyan-bordered color swatch chips in the character sheet and sample interior colors.

The character-sheet swatches are small rectangles outlined in a bright cyan/teal (#00E5xx).
We find those borders, then read the interior fill color of each chip and cluster them into a palette.
Coordinates are in ORIGINAL 4443x1900 space.
"""
from PIL import Image
import numpy as np
from scipy.ndimage import label as cc_label, find_objects

im = np.asarray(Image.open(r"D:\desktop\picture\KTK_04_246B\源文件\06_001_ミュイ.png").convert("RGB"))
H, W = im.shape[:2]
print("sheet", W, H)

r = im[..., 0].astype(int); g = im[..., 1].astype(int); b = im[..., 2].astype(int)
# cyan border: high G and B, low-ish R, and green/b blue similar
cyan = (g > 180) & (b > 150) & (r < 120) & (abs(g - b) < 90)
print("cyan px", cyan.sum())

lab, n = cc_label(cyan, structure=np.ones((3, 3)))
print("cyan components", n)

# collect chip interiors: dilate cyan border to fill, sample the enclosed area
from scipy.ndimage import binary_dilation, binary_fill_holes
filled = binary_fill_holes(binary_dilation(cyan, structure=np.ones((3, 3)), iterations=2))
lab2, n2 = cc_label(filled, structure=np.ones((3, 3)))
objs = find_objects(lab2)
chips = []
for i, sl in enumerate(objs):
    if sl is None:
        continue
    m = lab2[sl] == (i + 1)
    area = int(m.sum())
    if area < 40:   # skip specks
        continue
    # interior = filled minus cyan border
    interior = m & ~cyan[sl]
    if interior.sum() < 20:
        continue
    # sample mean color of interior
    sub = im[sl]
    cols = sub[interior]
    mean = cols.mean(axis=0).astype(int)
    yy, xx = np.where(m)
    cy = sl[0].start + yy.mean(); cx = sl[1].start + xx.mean()
    chips.append((int(cx), int(cy), int(area), tuple(mean)))

chips.sort(key=lambda c: (c[1] // 40, c[0]))
print(f"detected {len(chips)} chips")
for c in chips:
    print(f"  @({c[0]},{c[1]}) area={c[2]} RGB={c[3]}")

# cluster the chip colors
from collections import Counter
def q(c): return tuple(int(v // 8) * 8 for v in c)
cnt = Counter(q(c[3]) for c in chips)
print("\n clustered palette (quantized to /8):")
for col, k in cnt.most_common(30):
    print(f"   RGB~{col}  x{k}")
