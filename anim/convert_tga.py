# -*- coding: utf-8 -*-
"""Batch convert all .tga files under the picture dir to .png, preserving relative structure."""
import os
import glob
from PIL import Image

SRC = r"D:\desktop\picture"
OUT = r"D:\desktop\mianshi\work\png"

def convert(src, out):
    os.makedirs(out, exist_ok=True)
    total = 0
    for path in glob.glob(os.path.join(src, "**", "*.tga"), recursive=True):
        rel = os.path.relpath(path, SRC)
        dst = os.path.join(OUT, os.path.splitext(rel)[0] + ".png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            im = Image.open(path)
            im.load()
            # Convert to RGB to drop alpha-dependent quirks; keep RGBA if present? Use RGB for safety.
            im = im.convert("RGB")
            im.save(dst)
            total += 1
        except Exception as e:
            print(f"FAIL {rel}: {e}")
    print(f"converted {total} tga -> png")


if __name__ == "__main__":
    convert(SRC, OUT)
