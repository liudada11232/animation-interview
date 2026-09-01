# -*- coding: utf-8 -*-
"""题B 中割评测:
  * 逐帧与参考: 线集 Chamfer 距离 / 容差膨胀 F1 (主指标)
  * 序列连贯性: 相邻帧差分的运动平滑度
  * 结构保持: 角色部件 (连通域) 不凭空增减/断裂 — compare connected-component counts & area.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb, to_line_mask
from scipy.ndimage import label as cc_label

BASE = r"D:\desktop\mianshi\work\png\KTK_04_246B"
SRC = os.path.join(BASE, "源文件", "中割")
REF = os.path.join(BASE, "成品", "中割")
OUT = r"D:\desktop\mianshi\work\outB"
frames = [f"A000{i}" for i in range(1, 10)]

def line_intensity(img):
    return (255 - img.min(axis=2)).astype(np.float32)

f1s = {}; cham = {}
for f in frames:
    pred = load_rgb(os.path.join(OUT, f + ".png"))
    ref = load_rgb(os.path.join(REF, f + ".png"))
    mp = (pred.max(axis=2) < 250); mr = (ref.max(axis=2) < 250)
    # F1 tol 3
    from metrics import precision_recall_f1, chamfer_distance
    p, r, f1 = precision_recall_f1(mp, mr, tol=3)
    cd = chamfer_distance(mp, mr)
    f1s[f] = f1; cham[f] = cd
    print(f"{f}: P={p:.3f} R={r:.3f} F1={f1:.3f} Chamfer={cd:.2f} pxl={mp.sum()} refpx={mr.sum()}")

print("\n平均 F1 (关键帧+中间帧):", np.mean(list(f1s.values())))
print("平均 Chamfer:", np.mean(list(cham.values())))

# 序列连贯性: sum of absolute frame differences across the PREDICTED sequence - lower=quieter
print("\n序列连贯性 (相邻帧差分强度, 理想平滑):")
seq = [load_rgb(os.path.join(OUT, f + ".png")) for f in frames]
prev = None
for f, s in zip(frames, seq):
    li = line_intensity(s)
    if prev is not None:
        diff = np.abs(li - prev).mean()
        print(f"  {f}: |Δ|={diff:.2f}")
    prev = li

# 结构保持: connected-component count and total line area per frame (drifting cc count = structure break)
print("\n结构保持 (连通域数量/面积, 相邻帧应平滑):")
for f, s in zip(frames, seq):
    li = line_intensity(s)
    m = (li > 25)
    lab, n = cc_label(m, np.ones((3,3)))
    print(f"  {f}: 线连通域={n}, 线面积={int(m.sum())}")
