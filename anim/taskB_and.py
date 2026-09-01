# -*- coding: utf-8 -*-
"""试最后一种合法组装: warp后 AND(双向一致) 而非 OR, 看能否去重影提F1."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from io_utils import load_rgb
from metrics import precision_recall_f1, chamfer_distance
from taskB_inbet import flow_between, warp_line_art_from_to, snap_palette

base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
ref=os.path.join(base,"成品","中割")
src=os.path.join(base,"源文件","中割")
a6=load_rgb(os.path.join(src,"A0006.png")); a9=load_rgb(os.path.join(src,"A0009.png"))

def interp_and(a,b,t):
    fAB=flow_between(a,b,31,4); fBA=flow_between(b,a,31,4)
    wA=warp_line_art_from_to(a,fAB,t); wB=warp_line_art_from_to(b,fBA,1-t)
    lA=(255-wA.min(axis=2)); lB=(255-wB.min(axis=2))
    # AND: 仅保留两方向都确认是线的像素
    mA=lA>25; mB=lB>25
    both=mA&mB
    out=np.full_like(a,255)
    out[both]=np.clip((wA[both].astype(np.float32)+wB[both].astype(np.float32))/2,0,255).astype(np.uint8)
    return snap_palette(out), both

for i,t in [(7,1/3),(8,2/3)]:
    rgb,both=interp_and(a6,a9,t)
    r7=load_rgb(os.path.join(ref,f"A000{i}.png"))
    mp=(rgb.max(axis=2)<250); mr=(r7.max(axis=2)<250)
    p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
    print(f"AND A000{i}: F1={f1:.3f} P={p:.3f} R={rec:.3f} Chamfer={cd:.2f} px={mp.sum()} (both交集={both.sum()})")