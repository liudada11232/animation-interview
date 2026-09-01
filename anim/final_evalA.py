# -*- coding: utf-8 -*-
"""题A 最终评测: 在 KTK_04 上跑 v6 描原, 输出完整指标 (F1/Chamfer/闭合度/色占比)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb
from metrics import precision_recall_f1, chamfer_distance, closed_region_stats

base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
outdir=r"D:\desktop\mianshi\work\outA"
print("KTK_04 题A 描原 最终评测:")
tot_f1=0
for rn in ["A0001","A0006","A0009"]:
    pred=load_rgb(os.path.join(outdir,rn+".png"))
    ref=load_rgb(os.path.join(base,"成品","描原",rn+".png"))
    mp=(pred.max(axis=2)<250); mr=(ref.max(axis=2)<250)
    p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
    st=closed_region_stats(mp)
    # 闭合度: 内部(封闭)区域面积 / 总前景面积. 若线闭合良好, 内部区域大且漏很少
    # 漏进背景的前景: 通过"与边界相连的背景"反推. 简化为: 封闭区域占比
    interior_ratio = st['interior_area']/max(1,mp.sum())
    # color composition
    flat=pred.reshape(-1,3).astype(np.int32)
    nblack=int((np.all(flat==0,1)).sum())
    nblue=int(((flat[:,2]>150)&(flat[:,0]<90)&(flat[:,1]<90)).sum())
    nred=int(((flat[:,0]>150)&(flat[:,1]<90)&(flat[:,2]<90)).sum())
    tot_f1+=f1
    print(f"  {rn}: P={p:.3f} R={rec:.3f} F1={f1:.3f} Chamfer={cd:.1f} 线px={mp.sum()} "
          f"闭合内区={st['interior_regions']} 内区面积={st['interior_area']} 封闭占比={interior_ratio:.3f} 黑/蓝/红={nblack}/{nblue}/{nred}")
print(f"  平均F1 = {tot_f1/3:.3f}")
