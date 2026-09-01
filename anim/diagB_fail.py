# -*- coding: utf-8 -*-
"""量化 A0007/A0008 的失败构成:
  1. 线像素 vs 参考 (F1 分解)
  2. 连通域碎片数 (碎线头)
  3. 重影程度: 预测线是否偏离参考(Chamfer 分布)
  4. 单像素线比例 (线宽)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb
from scipy.ndimage import label as cc_label
from metrics import precision_recall_f1, chamfer_distance

BASE=r"D:\desktop\mianshi\work\png\KTK_04_246B"
REF=os.path.join(BASE,"成品","中割")
OUT=r"D:\desktop\mianshi\work\outB"
for f in ["A0007","A0008","A0005"]:
    pred=load_rgb(os.path.join(OUT,f+".png"))
    ref=load_rgb(os.path.join(REF,f+".png"))
    mp=(pred.max(axis=2)<250); mr=(ref.max(axis=2)<250)
    p,rec,f1=precision_recall_f1(mp,mr,tol=3)
    # connected components of pred lines
    lab,n=cc_label(mp,np.ones((3,3)))
    sizes=np.bincount(lab.ravel())[1:]
    tiny=(sizes<=5).sum()
    # line width: distance transform at pred
    from scipy.ndimage import distance_transform_edt
    dt=distance_transform_edt(mp)
    width=np.percentile(dt[mp],[50,90])
    # jitter: Chamfer pred->ref
    cd=chamfer_distance(mp,mr)
    print(f"{f}: F1={f1:.3f}(P={p:.3f} R={rec:.3f}) 线px={mp.sum()} 连通域={n} 微小碎片(≤5px)={tiny} "
          f"线宽p50/p90={width[0]:.1f}/{width[1]:.1f} Chamfer={cd:.1f}")