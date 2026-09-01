# -*- coding: utf-8 -*-
"""Build the semantic palette. The reliable colors come from the chip detector (detect_swatches.py),
which sampled the actual chip interiors. Coordinates are in ORIGINAL sheet space (4443x1900).
We map detected chips to part labels using the layout structure we read, and output a clean palette.
"""
from PIL import Image
import numpy as np, json, os

im = np.asarray(Image.open(r"D:\desktop\picture\KTK_04_246B\源文件\06_001_ミュイ.png").convert("RGB"))

# ---- re-run chip detection (same logic as detect_swatches.py) ----
r = im[..., 0].astype(int); g = im[..., 1].astype(int); b = im[..., 2].astype(int)
cyan = (g > 180) & (b > 150) & (r < 120) & (abs(g - b) < 90)
from scipy.ndimage import label as cc_label, find_objects, binary_dilation, binary_fill_holes
filled = binary_fill_holes(binary_dilation(cyan, structure=np.ones((3, 3)), iterations=2))
lab, n = cc_label(filled, structure=np.ones((3, 3)))
objs = find_objects(lab)
chips = []
for i, sl in enumerate(objs):
    if sl is None:
        continue
    m = lab[sl] == (i + 1)
    area = int(m.sum())
    if area < 40:
        continue
    interior = m & ~cyan[sl]
    if interior.sum() < 20:
        continue
    cols = im[sl][interior]
    mean = cols.mean(axis=0).astype(int)
    yy, xx = np.where(m)
    chips.append((int(sl[1].start + xx.mean()), int(sl[0].start + yy.mean()), int(area),
                  tuple(int(v) for v in mean)))

print(f"chips: {len(chips)}")

# ---- classify by location: map to semantic part ----
# Build a map keyed by approximate region. We assign labels by position.
# Bottom-right eye-detail chips are at y>1180; the '影中' (shadow) row at y>1790.
palette = {}
for cx, cy, area, rgb in chips:
    if cy > 1790:
        if cx < 400: palette[f"eye_shadow_{cx}"] = rgb
        else: palette[f"shadow_{cx}"] = rgb
    elif cy > 1180 and cx < 1000:
        # normal eye details row
        palette[f"eye_{cx}"] = rgb
    elif cy < 260 and cx < 500:
        palette[f"face_top_{cx}_{cy}"] = rgb
    else:
        palette[f"part_{cx}_{cy}"] = rgb
    print(f"  ({cx},{cy}) a={area} RGB={rgb}")

# Convert numpy ints safely
palette = {k: [int(v) for v in val] for k, val in palette.items()}
out = r"D:\desktop\mianshi\work\palette_detected.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump({"source": "KTK_04_246B 06_001_ミュイ.png", "palette": palette}, f, ensure_ascii=False, indent=2)
print("saved", out)
