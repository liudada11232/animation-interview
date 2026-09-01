# -*- coding: utf-8 -*-
"""汇总所有最终指标, 输出到控制台, 供报告引用."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb
from metrics import precision_recall_f1, chamfer_distance, closed_region_stats

def line_metrics(predp, refp, tol=3):
    mp=(predp.max(axis=2)<250); mr=(refp.max(axis=2)<250)
    p,rec,f1=precision_recall_f1(mp,mr,tol=tol); cd=chamfer_distance(mp,mr)
    st=closed_region_stats(mp)
    return dict(P=p,R=rec,F1=f1,chamfer=cd,closure=st)

B4=r"D:\desktop\mianshi\work\png\KTK_04_246B"
print("="*70)
print("【题A 描原】KTK_04  (输出 outA, 参考 成品/描原)")
for rn in ["A0001","A0006","A0009"]:
    m=line_metrics(load_rgb(os.path.join(r"D:\desktop\mianshi\work\outA",rn+".png")),
                   load_rgb(os.path.join(B4,"成品","描原",rn+".png")))
    print(f"  {rn}: F1={m['F1']:.3f} P={m['P']:.3f} R={m['R']:.3f} Chamfer={m['chamfer']:.1f} "
          f"闭合={m['closure']['interior_area']}px")

print("\n【题B 中割】KTK_04  (输出 outB, 参考 成品/中割)")
for rn in [f"A000{i}" for i in range(1,10)]:
    m=line_metrics(load_rgb(os.path.join(r"D:\desktop\mianshi\work\outB",rn+".png")),
                   load_rgb(os.path.join(B4,"成品","中割",rn+".png")))
    print(f"  {rn}: F1={m['F1']:.3f} P={m['P']:.3f} R={m['R']:.3f} Chamfer={m['chamfer']:.2f}")
