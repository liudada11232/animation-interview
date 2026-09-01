# -*- coding: utf-8 -*-
"""分析漏涂区域: 参考涂了我没涂的像素, 分布在哪、属于什么区域、为什么被我判白."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb
from scipy.ndimage import label as cc_label

BASE=r"D:\desktop\mianshi\work\png\KTK_04_246B"
SRC=os.path.join(BASE,"源文件","上色")
REF=os.path.join(BASE,"成品","上色")
OUT=r"D:\desktop\mianshi\work\outC"

for f in ["A0001","A0009"]:
    a_im=load_rgb(os.path.join(SRC,f+".png"))
    r_im=load_rgb(os.path.join(REF,f+".png"))
    p_im=load_rgb(os.path.join(OUT,f+".png"))
    H,W=a_im.shape[:2]
    a=a_im.reshape(-1,3).astype(np.int32)
    r=r_im.reshape(-1,3).astype(np.int32)
    p=p_im.reshape(-1,3).astype(np.int32)
    pf=~np.all(p==255,axis=1)
    rf=~np.all(r==255,axis=1)
    line=~np.all(a==255,axis=1)
    under=(rf&~pf&~line)   # 参考涂了我没涂且不是线
    under_im=under.reshape(H,W)
    # 这些像素我输出成什么颜色了? (应该都是白)
    # 参考颜色分布
    rcols=r[under]
    from collections import Counter
    cnt=Counter(map(tuple,rcols))
    print(f"\n{f}: 漏涂={under.sum()}px, 参考漏涂区颜色分布:")
    for c,k in cnt.most_common(6):
        print(f"   {c} x{k}")
    # 漏涂像素的 y 分布
    yy,xx=np.where(under_im)
    if len(yy):
        print(f"   漏涂质心 y={yy.mean():.0f}/{H} ({yy.mean()/H:.2f}), x={xx.mean():.0f}/{W} ({xx.mean()/W:.2f})")
        print(f"   漏涂像素 y 分桶: {np.histogram(yy,bins=5,range=(0,H))[0].tolist()}")
    # 漏涂连通域
    lab,n=cc_label(under_im,np.ones((3,3)))
    sizes=np.bincount(lab.ravel())
    big=[int(s) for s in sizes if 500<s]
    print(f"   漏涂连通域数={n}, 大于500px的域: {sorted(big,reverse=True)[:8]}")