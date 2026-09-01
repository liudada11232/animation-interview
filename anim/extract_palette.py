# -*- coding: utf-8 -*-
"""Extract the character's semantic color palette from the sheet.

We detected 45 cyan-bordered chips. Now we map their (x,y) to semantic parts based on the
layout we read from the sheet. The layout (in ORIGINAL 4443x1900 coords):
  Left panel columns:
  - 髪(hair) column  x~346, y~200 (stack)
  - 毛先(hair tip)   x~383, y~369
  - 肌(skin)         x~328-345, y~530-680
  - 頬/唇 etc around x~63-218, y~355
  - eye swatches around x~361-524, y~1190-1290 (normal) and y~1810 (影中)
We produce a readable palette json + print.
"""
from PIL import Image
import numpy as np, json

im = np.asarray(Image.open(r"D:\desktop\picture\KTK_04_246B\源文件\06_001_ミュイ.png").convert("RGB"))

def chip(cx, cy, label, r=8):
    patch = im[cy-r:cy+r, cx-r:cx+r].reshape(-1,3).astype(np.float32)
    return tuple(patch.mean(axis=0).astype(int))

# Row bands (from detection) - we assign by x,y proximity
sw = [
    (346,201,"髪(hair) base"),    # top of hair stack
    (346,380,"髪(hair) mid"),
    (346,560,"髪(hair) low"),
    (432,213,"髪の毛ライン(hairline)"),
    (383,369,"毛先(hair tip)"),
    (329,530,"肌(skin) base"),
    (345,620,"肌(skin) mid"),
    (141,355,"頬(cheek) base"),
    (218,353,"頬(cheek) mid"),
    (63,355,"白目/まつ毛 area"),
    (1331,504,"瞳(iris) normal"),
    (1411,504,"まぶたライン(eyeline)"),
    (361,1203,"目の白/虹彩 (normal)"),
    (441,1201,"色HI (normal)"),
    (515,1203,"瞳 normal"),
    (357,1816,"目の白 (影中)"),
    (440,1813,"色HI (影中)"),
    (524,1812,"瞳 (影中)"),
]
palette = {}
for cx,cy,lab in sw:
    palette[lab] = chip(cx,cy,lab)
    print(f"  {lab:24s} RGB={palette[lab]}")

print("\nFULL detected-chip dump (for manual mapping):")
# Show all 45 with coords so we can finalize labels
print("saved palette to palette.json")
with open(r"D:\desktop\mianshi\work\palette.json","w",encoding="utf-8") as f:
    json.dump(palette, f, ensure_ascii=False, indent=2)
