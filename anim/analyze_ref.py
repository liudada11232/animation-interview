# -*- coding: utf-8 -*-
"""Analyze pixel color distribution of reference line art + color art, to validate palette assumptions."""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from io_utils import load_rgb

def analyze(path, label):
    a = load_rgb(path)
    print(f"=== {label} : {a.shape}")
    flat = a.reshape(-1, 3).astype(np.int32)
    # unique colors and counts (quantized)
    uniq, cnt = np.unique(flat, axis=0, return_counts=True)
    order = np.argsort(-cnt)
    print(" top colors (RGB : count) :")
    for i in order[:12]:
        print(f"   {tuple(uniq[i])} : {cnt[i]}")
    # non-white ratio
    nw = (flat.max(axis=1) < 250)
    print(f"   non-white ratio: {nw.mean():.4f}  ({nw.sum()} px)")

if __name__ == "__main__":
    base = r"D:\desktop\mianshi\work\png"
    analyze(base + r"\KTK_04_246B\成品\描原\A0001.png", "描原成品 A0001")
    analyze(base + r"\KTK_04_246B\成品\上色\A0001.png", "上色成品 A0001")
    analyze(base + r"\KTK_04_246B\成品\中割\A0005.png", "中割成品 A0005")
