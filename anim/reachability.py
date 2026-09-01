# -*- coding: utf-8 -*-
"""三关键帧轨迹法: A0001->A0006->A0009 拟合运动, 外推 A0007/A0008.
思路: A0001到A0006的位移场 D1, A0006到A0009的位移场 D2.
若转头近似匀速, A0007 的位移 ≈ D1 + (D2-D1)*(1/3)/(3帧跨度*0.5)... 需要仔细定义.
更实用: 分别算 A0006->A0007(预测) = 1/3*(A0006->A0009位移), 再用 A0001->A0006 的位移方向做先验校验.
先验证: 参考 A0007 的可达性到底如何 —— 用 A0006 的线 + 真实A0009位移的1/3, 看离 A0007 多远."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from io_utils import load_rgb
from metrics import precision_recall_f1, chamfer_distance

base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
ref=os.path.join(base,"成品","中割")
def lm(f): return (load_rgb(os.path.join(ref,f+".png")).max(axis=2)<250)

# 假设检验: 若 A0007 是 A0006 线沿流场移动 1/3 步到 A0009 的结果, 则 warp(A0006, flow*1/3) 应与 A0007 接近
# 但 A0007 是重画的, 我们量化这个 gap: warp6_7 over 每根线的位移方向一致度
r6,r7,r9=lm("A0006"),lm("A0007"),lm("A0009")
# 用骨架线集的最近邻距离: 把 A0006 的每条线匹配到 A0007, 看平均位移
from scipy.ndimage import distance_transform_edt
d7=distance_transform_edt(~r7)
# A0006 线像素到 A0007 最近线的距离分布
d6_to_7=d7[r6]
print(f"A0006 线 -> A0007 最近线距离: p50={np.percentile(d6_to_7,50):.1f} p90={np.percentile(d6_to_7,90):.1f}px")
print(f"  (若<2px 则可插值; 若>5px 则表示线被大量重画)")
# A0006 有多少线像素在 A0007 的 2px 内
print(f"  A0006 线落在 A0007 2px 内的比例: {(d6_to_7<=2).mean():.3f}")
print(f"  A0006 线落在 A0007 5px 内的比例: {(d6_to_7<=5).mean():.3f}")