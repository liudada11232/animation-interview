# -*- coding: utf-8 -*-
"""素材转换脚本: 把试题包里的 tga 素材批量转成 png，供后续脚本使用。

用法:
    python convert_tga.py <素材目录> <输出目录>
示例:
    python convert_tga.py D:/path/to/2026.07.13解压目录 ./png
说明:
    - 递归转换该目录下所有 .tga
    - 输出保留相对目录结构, 即 <输出目录>/<相对路径>.png
"""
import os
import sys
import glob
from PIL import Image


def convert(src, out):
    os.makedirs(out, exist_ok=True)
    total = 0
    for path in glob.glob(os.path.join(src, "**", "*.tga"), recursive=True):
        rel = os.path.relpath(path, src)
        dst = os.path.join(out, os.path.splitext(rel)[0] + ".png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            im = Image.open(path)
            im.load()
            im = im.convert("RGB")
            im.save(dst)
            total += 1
        except Exception as e:
            print(f"FAIL {rel}: {e}")
    print(f"converted {total} tga -> png")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])