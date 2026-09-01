# -*- coding: utf-8 -*-
"""KTK_05_140 进阶 — 描原. Reuse taskA v6 (dark-skeleton + colored edges).
Map: 源文件/描原/{A0001,A0002,B0001,B0002}.tga -> 成品/描原/{A/A0001,A/A0005,B/B0001,B/B0003}.png"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from scipy.ndimage import label as cc_label
from thinning import zhang_suen
from io_utils import load_rgb, save_rgb
from metrics import precision_recall_f1, chamfer_distance, closed_region_stats

WHITE=(255,255,255); BLACK=(0,0,0); BLUE=(0,0,255); RED=(255,0,0); GREEN=(0,255,0)

def mask_regions(shape):
    H,W=shape[:2]; m=np.zeros(shape[:2],bool)
    m[40:75,255:400]=True; m[40:75,1690:1850]=True; m[40:75,985:1060]=True
    m[400:1300,1960:2340]=True   # watermark right
    return m

def run(rough_path, out_path):
    a=load_rgb(rough_path)
    flat=a.reshape(-1,3).astype(np.int32)
    r,g,b=flat[:,0],flat[:,1],flat[:,2]
    lum=0.3*r+0.6*g+0.1*b; sat=flat.max(axis=1)-flat.min(axis=1)
    ink=(255-flat.min(axis=1)>18)
    ink=ink.reshape(a.shape[:2]); ink&=~mask_regions(a.shape)
    lab,n=cc_label(ink,np.ones((3,3))); sz=np.bincount(lab.ravel())
    keep=np.zeros(n+1,bool); keep[1:]=sz[1:]>=5; ink=keep[lab]
    dark=ink&(lum.reshape(a.shape[:2])<210)&(sat.reshape(a.shape[:2])<80)
    dark_skel=zhang_suen(dark, max_iter=30)
    gray=cv2.cvtColor(a.astype(np.uint8),cv2.COLOR_RGB2GRAY)
    edges=(cv2.Canny(gray,50,150)>0)&ink
    rr,gg,bb=a[...,0].astype(np.int32),a[...,1].astype(np.int32),a[...,2].astype(np.int32)
    green=edges&(gg>rr+12)&(gg>bb+12)&(gg>110)&~dark_skel
    cyan=edges&(bb>rr+12)&(gg>rr+12)&(abs(gg-bb)<70)&~green&~dark_skel
    red=edges&(rr>gg+12)&(rr>bb+12)&(rr>120)&~green&~cyan&~dark_skel
    out=np.full_like(a,WHITE)
    out[dark_skel]=BLACK
    out[edges&green]=GREEN; out[edges&cyan]=BLUE; out[edges&red]=RED
    out[edges&~green&~cyan&~red]=BLACK
    save_rgb(out,out_path); return out

if __name__=="__main__":
    src=r"D:\desktop\mianshi\work\png\KTK_05_140\源文件\描原"
    refroot=r"D:\desktop\mianshi\work\png\KTK_05_140\成品\描原"
    outdir=r"D:\desktop\mianshi\work\outA5"; os.makedirs(outdir,exist_ok=True)
    # A layer
    for inp, refn in [("A0001","A0001"),("A0002","A0005")]:
        outp=os.path.join(outdir,"A_"+refn+".png")
        run(os.path.join(src,inp+".png"),outp)
        ref=load_rgb(os.path.join(refroot,"A",refn+".png"))
        pred=load_rgb(outp)
        mp=(pred.max(axis=2)<250); mr=(ref.max(axis=2)<250)
        p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
        st=closed_region_stats(mp)
        print(f"src/{inp}->A/{refn}: P={p:.3f} R={rec:.3f} F1={f1:.3f} Chamfer={cd:.2f} 闭合内区={st['interior_regions']}")
    # B layer
    for inp, refn in [("B0001","B0001"),("B0002","B0003")]:
        outp=os.path.join(outdir,"B_"+refn+".png")
        run(os.path.join(src,inp+".png"),outp)
        ref=load_rgb(os.path.join(refroot,"B",refn+".png"))
        pred=load_rgb(outp)
        mp=(pred.max(axis=2)<250); mr=(ref.max(axis=2)<250)
        p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
        print(f"src/{inp}->B/{refn}: P={p:.3f} R={rec:.3f} F1={f1:.3f} Chamfer={cd:.2f}")
