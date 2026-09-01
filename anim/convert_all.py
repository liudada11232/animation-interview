# -*- coding: utf-8 -*-
"""补齐素材库: 把源库的所有图片(jpg/png/tga)统一转换/复制为 png 格式, 镜像目录结构.
确保 work\png 与 D:\desktop\picture 一一对应."""
import os, glob, shutil
from PIL import Image

SRC = r"D:\desktop\picture"
OUT = r"D:\desktop\mianshi\work\png"

def conv(path, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(path)
    im.load()
    im = im.convert("RGB")
    im.save(dst)
    return True

count = 0
for ext in ["*.jpg", "*.jpeg", "*.png", "*.tga"]:
    for path in glob.glob(os.path.join(SRC, "**", ext), recursive=True):
        rel = os.path.relpath(path, SRC)
        base = os.path.splitext(rel)[0]
        dst = os.path.join(OUT, base + ".png")
        if os.path.exists(dst):
            continue
        try:
            conv(path, dst)
            count += 1
        except Exception as e:
            print(f"FAIL {rel}: {e}")
print(f"补齐 {count} 个文件")