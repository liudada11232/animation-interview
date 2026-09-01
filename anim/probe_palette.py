# -*- coding: utf-8 -*-
"""Sample exact RGB from the character-sheet color swatches.

Coordinates are in ORIGINAL 4443x1900 space. I calibrated them from the 1100x1900
left-panel crop (palette_left.png) and the full sheet. Each swatch column is a small
stack of 2-4 color chips; we sample the CENTER of each chip and report its RGB.
"""
from PIL import Image
import numpy as np

im = np.asarray(Image.open(r"D:\desktop\picture\KTK_04_246B\源文件\06_001_ミュイ.png").convert("RGB"))
H, W = im.shape[:2]
print("sheet", W, H)

def chip(x, y, label, r=6):
    """Average a small patch around (x,y) - coordinates in ORIGINAL px."""
    patch = im[y - r:y + r, x - r:x + r].reshape(-1, 3).astype(np.float32)
    avg = patch.mean(axis=0).astype(int)
    print(f"{label:28s} @({x},{y}) RGB={tuple(avg)}")
    return tuple(avg)

# The left panel crop was 1100x1900 from (0,0). Coordinates there = original.
# "髪" swatch column near x~285, rows around y~110-260. Let me probe a grid.
def probe_col(x, y0, y1, n, label):
    print(f"-- {label} col x={x} --")
    for i in range(n):
        y = y0 + int((y1 - y0) * (i + 0.5) / n)
        chip(x, y, f"{label}[{i}]")

# hair column (left side of 髪 label at ~ (285, 115)) - vertical stack below
# From full-sheet view, hair swatch ~ x 270-300, y 95-260
probe_col(285, 100, 260, 4, "髪/hair")
# 毛先 (hair tip) lower ~ x 270-300, y 265-330
probe_col(285, 268, 330, 3, "毛先")
# 肌 (skin) ~ x 340, y 550-700
probe_col(345, 560, 690, 3, "肌/skin")
