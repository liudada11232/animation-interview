# -*- coding: utf-8 -*-
"""读参考底部区域(y>0.72)的实际配色, 为贴边身体区域定规则."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb
from collections import Counter

BASE=r"D:\desktop\mianshi\work\png\KTK_04_246B"
REF=os.path.join(BASE,"成品","上色")
for f in ["A0001","A0005","A0009"]:
    r=load_rgb(os.path.join(REF,f+".png"))
    H,W=r.shape[:2]
    bottom=r[int(H*0.72):]
    flat=bottom.reshape(-1,3)
    dev=255-flat.min(axis=1)
    col=flat[dev>25]
    cnt=Counter(map(tuple,col))
    print(f"\n{f} 底部(y>0.72)参考主色:")
    for c,k in cnt.most_common(6):
        print(f"   {c} x{k}")