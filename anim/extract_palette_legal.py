# -*- coding: utf-8 -*-
"""合规调色盘提取: 只从设定图色卡(青色边框芯片)提取.
改进: 取芯片内部中位色(抗噪), 输出完整 [坐标,bbox,色值] 列表用于部位分组."""
from PIL import Image
import numpy as np
from scipy.ndimage import label as cc_label, find_objects, binary_dilation, binary_fill_holes

im = np.asarray(Image.open(r"D:\desktop\picture\KTK_04_246B\源文件\06_001_ミュイ.png").convert("RGB"))
H, W = im.shape[:2]
r=im[...,0].astype(int); g=im[...,1].astype(int); b=im[...,2].astype(int)
cyan=(g>180)&(b>150)&(r<120)&(abs(g-b)<90)
filled=binary_fill_holes(binary_dilation(cyan,np.ones((3,3)),iterations=2))
lab,n=cc_label(filled,np.ones((3,3)))
objs=find_objects(lab)
chips=[]
for i,sl in enumerate(objs):
    if sl is None: continue
    m=lab[sl]==(i+1)
    if int(m.sum())<40: continue
    interior=m&~cyan[sl]
    if interior.sum()<20: continue
    cols=im[sl][interior]
    med=tuple(int(v) for v in np.median(cols,axis=0))
    mean=tuple(int(v) for v in cols.mean(axis=0))
    yy,xx=np.where(m)
    cy=int(sl[0].start+yy.mean()); cx=int(sl[1].start+xx.mean())
    chips.append((cx,cy,med,mean,xx.min(),xx.max(),yy.min(),yy.max()))
chips.sort(key=lambda c:(c[1]//60,c[0]))
print(f"共 {len(chips)} 个色卡芯片 (坐标按行分组):")
for cx,cy,med,mean,x0,x1,y0,y1 in chips:
    print(f"  ({cx:4d},{cy:4d}) 中位RGB={med} 均值RGB={mean}  bbox x[{x0}-{x1}] y[{y0}-{y1}]")
import json
with open(r"D:\desktop\mianshi\work\sheet_chips.json","w",encoding="utf-8") as f:
    json.dump([{"cx":int(c[0]),"cy":int(c[1]),"median":[int(v) for v in c[2]],"mean":[int(v) for v in c[3]],"b":[int(v) for v in c[4:]]} for c in chips], f, ensure_ascii=False, indent=1)
print("saved sheet_chips.json")