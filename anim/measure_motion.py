# -*- coding: utf-8 -*-
"""测量 A0006->A0009 的真实运动: 位移场统计 + 逐块校验.
目的: 判断是'大位移'还是'非刚体'导致 Previous flow 失败."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from io_utils import load_rgb

base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
src=os.path.join(base,"源文件","中割")
a6=load_rgb(os.path.join(src,"A0006.png")); a9=load_rgb(os.path.join(src,"A0009.png"))
ga=cv2.cvtColor(a6.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)/255
gb=cv2.cvtColor(a9.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)/255
# 放大线条信号 (线是暗的, 增强对比)
def boost(g):
    return np.clip((1-g)*4,0,1)
ba=boost(ga); bb=boost(gb)
flow=cv2.calcOpticalFlowFarneback((ba*255).astype(np.uint8),(bb*255).astype(np.uint8),None,
                                  pyr_scale=0.5,levels=4,winsize=31,iterations=4,poly_n=7,poly_sigma=1.5,flags=0)
mag=np.sqrt(flow[...,0]**2+flow[...,1]**2)
lines_a=(ba>0.15)
print(f"A0006 线像素数: {lines_a.sum()}")
print(f"线处的位移幅度: p50={np.percentile(mag[lines_a],50):.1f} p90={np.percentile(mag[lines_a],90):.1f} "
      f"p99={np.percentile(mag[lines_a],99):.1f} max={mag.max():.1f}")
# 位移方向是否一致 (旋转变会有方向差异)
ang=np.arctan2(flow[...,1],flow[...,0])
ang_line=ang[lines_a]
hist=np.histogram(ang_line[np.isfinite(ang_line)],bins=8,range=(-np.pi,np.pi))[0]
print("线处位移方向直方图(8桶):",hist)
# 位移大小分布
print("位移>10px 的线像素占比:",(mag[lines_a]>10).mean())
print("位移>20px 的线像素占比:",(mag[lines_a]>20).mean())