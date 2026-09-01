# -*- coding: utf-8 -*-
"""关键假设检验: 参考中间帧 A0007/8 是'插值'还是'重画'?
若 A0007 与 A0006/A0009 的 Chamfer 距离都很小且对称, 说明是插值; 若都大, 是重画.
同时测: A0006 和 A0009 直接插值到 A0007 位置, 与参考 A0007 的 F1 上限在哪."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb
from metrics import precision_recall_f1, chamfer_distance

base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
ref=os.path.join(base,"成品","中割")
def lm(f): return (load_rgb(os.path.join(ref,f+".png")).max(axis=2)<250)
r6,r7,r8,r9=lm("A0006"),lm("A0007"),lm("A0008"),lm("A0009")
print(f"A0007 vs A0006: F1={precision_recall_f1(r7,r6,tol=3)[2]:.3f} Chamfer={chamfer_distance(r7,r6):.2f}")
print(f"A0007 vs A0009: F1={precision_recall_f1(r7,r9,tol=3)[2]:.3f} Chamfer={chamfer_distance(r7,r9):.2f}")
print(f"A0008 vs A0006: F1={precision_recall_f1(r8,r6,tol=3)[2]:.3f} Chamfer={chamfer_distance(r8,r6):.2f}")
print(f"A0008 vs A0009: F1={precision_recall_f1(r8,r9,tol=3)[2]:.3f} Chamfer={chamfer_distance(r8,r9):.2f}")
# A0007 与两端的平均 Chamfer, 判断位置
print(f"\nA0007 更接近 A0006 还是 A0009? {chamfer_distance(r7,r6):.1f} vs {chamfer_distance(r7,r9):.1f}")
print(f"A0008 更接近 A0006 还是 A0009? {chamfer_distance(r8,r6):.1f} vs {chamfer_distance(r8,r9):.1f}")