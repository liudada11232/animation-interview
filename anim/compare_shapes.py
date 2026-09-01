# -*- coding: utf-8 -*-
"""对比 A0006/A0007/A0009 的线形分布: 纵向(y)分布直方图, 看转头时形态是否真变."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb

base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
ref=os.path.join(base,"成品","中割")
for f in ["A0006","A0007","A0008","A0009"]:
    img=load_rgb(os.path.join(ref,f+".png"))
    m=(img.max(axis=2)<250)
    # 按 y 分 20 桶统计线密度
    H=m.shape[0]
    hist=np.zeros(20)
    yy,xx=np.where(m)
    bins=(yy*20//H)
    hist=np.bincount(bins,minlength=20)
    print(f"{f}: 线px={m.sum()} y分布={hist.astype(int).tolist()}")