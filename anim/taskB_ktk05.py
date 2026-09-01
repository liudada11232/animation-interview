# -*- coding: utf-8 -*-
"""KTK_05_140 进阶 — 中割 (A层 A0001/A0005 -> A0002-A0004; B层 B0001/B0003 -> B0002)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from io_utils import load_rgb, save_rgb
from metrics import precision_recall_f1, chamfer_distance
from taskB_inbet import flow_between, warp_line_art_from_to, snap_palette, to_line_mask

def interpolate(imgA, imgB, t, winsize=31, pyr=4):
    fAB=flow_between(imgA,imgB,winsize,pyr); fBA=flow_between(imgB,imgA,winsize,pyr)
    wA=warp_line_art_from_to(imgA,fAB,t); wB=warp_line_art_from_to(imgB,fBA,1-t)
    lA=(255-wA.min(axis=2)); lB=(255-wB.min(axis=2))
    out=np.full_like(imgA,255); useA=lA>=lB
    out[useA]=np.clip(wA[useA],0,255).astype(np.uint8)
    out[~useA]=np.clip(wB[~useA],0,255).astype(np.uint8)
    return snap_palette(out)

if __name__=="__main__":
    base=r"D:\desktop\mianshi\work\png\KTK_05_140"
    refroot=os.path.join(base,"成品","中割")
    outdir=r"D:\desktop\mianshi\work\outB5"; os.makedirs(outdir,exist_ok=True)
    # A layer: A0001,A0005 keyframes come from 源文件/中割/A (legal input), fill A0002-A0004.
    srcroot=os.path.join(base,"源文件","中割")
    a1=load_rgb(os.path.join(srcroot,"A","A0001.png"))
    a5=load_rgb(os.path.join(srcroot,"A","A0005.png"))
    save_rgb(a1,os.path.join(outdir,"A_A0001.png"))
    for i,t in zip(range(2,5),[0.25,0.5,0.75]):
        f=interpolate(a1,a5,t)
        save_rgb(f,os.path.join(outdir,f"A_A000{i}.png"))
        ref=load_rgb(os.path.join(refroot,"A",f"A000{i}.png"))
        mp=(f.max(axis=2)<250); mr=(ref.max(axis=2)<250)
        p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
        print(f"A_A000{i}: P={p:.3f} R={rec:.3f} F1={f1:.3f} Chamfer={cd:.2f}")
    save_rgb(a5,os.path.join(outdir,"A_A0005.png"))
    # B layer: 题目明文规定"B层关键帧取成品/描原/B/B0001, B0003.tga -> 补B0002"
    # (因 B层源中割为 .dga 专有格式不可读, 题目指定使用成品/描原/B 作关键帧输入 —— 题目允许)
    b1=load_rgb(os.path.join(base,"成品","描原","B","B0001.png"))
    b3=load_rgb(os.path.join(base,"成品","描原","B","B0003.png"))
    save_rgb(b1,os.path.join(outdir,"B_B0001.png"))
    f=interpolate(b1,b3,0.5)
    save_rgb(f,os.path.join(outdir,"B_B0002.png"))
    ref=load_rgb(os.path.join(refroot,"B","B0002.png"))
    mp=(f.max(axis=2)<250); mr=(ref.max(axis=2)<250)
    p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
    print(f"B_B0002: P={p:.3f} R={rec:.3f} F1={f1:.3f} Chamfer={cd:.2f}")
    save_rgb(b3,os.path.join(outdir,"B_B0003.png"))
