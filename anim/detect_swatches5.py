# -*- coding: utf-8 -*-
"""为 KTK_05_140 蓝发角色重新检测色卡芯片并采样精确 RGB."""
from PIL import Image
import numpy as np
from scipy.ndimage import label as cc_label, find_objects, binary_dilation, binary_fill_holes

im=np.asarray(Image.open(r"D:\desktop\picture\KTK_05_140\源文件\06_001_ミュイ.png").convert("RGB"))
print("sheet", im.shape)
r=im[...,0].astype(int); g=im[...,1].astype(int); b=im[...,2].astype(int)
cyan=(g>180)&(b>150)&(r<120)&(abs(g-b)<90)
filled=binary_fill_holes(binary_dilation(cyan,np.ones((3,3)),iterations=2))
lab,n=cc_label(filled,np.ones((3,3)))
objs=find_objects(lab)
chips=[]
for i,sl in enumerate(objs):
    if sl is None: continue
    m=lab[sl]==(i+1); area=int(m.sum())
    if area<40: continue
    interior=m&~cyan[sl]
    if interior.sum()<20: continue
    cols=im[sl][interior]; mean=cols.mean(axis=0).astype(int)
    yy,xx=np.where(m)
    chips.append((int(sl[1].start+xx.mean()),int(sl[0].start+yy.mean()),int(area),tuple(int(v) for v in mean)))
chips.sort(key=lambda c:(c[1]//40,c[0]))
print(f"{len(chips)} chips:")
for c in chips:
    print(f"  ({c[0]},{c[1]}) a={c[2]} RGB={c[3]}")
