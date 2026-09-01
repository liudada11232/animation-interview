# -*- coding: utf-8 -*-
"""题A 描原 v7 — color-region-boundary line extraction (closed, fillable) + semantic coloring.

Paradigm change: the reference clean line art is the *closed boundary outline* of the color regions
in the rough (each region boundary forms a fillable polygon). So we:
  1. segment the rough into color regions (k-means)
  2. take region boundaries (where adjacent labels differ) + strong dark strokes as the structure
  3. color each boundary pixel by the dominant hue of the two adjacent regions:
        cyan/blue hue      -> BLUE (shadow boundary)
        red/pink hue       -> RED (highlight boundary)
        green hue          -> GREEN (specular)
        dark/grey/neutral  -> BLACK (structure)
  4. this yields closed, fillable, semantic-colored line art.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from scipy.ndimage import label as cc_label
from io_utils import load_rgb, save_rgb
from metrics import precision_recall_f1, chamfer_distance, closed_region_stats

WHITE=(255,255,255); BLACK=(0,0,0); BLUE=(0,0,255); RED=(255,0,0); GREEN=(0,255,0)

def mask_regions(shape):
    H,W=shape[:2]; m=np.zeros(shape[:2],bool)
    m[40:70,260:390]=True; m[40:70,1700:1840]=True; m[40:70,990:1050]=True
    m[520:1400,1960:2340]=True; return m

def segment(a, K=5):
    flat=a.reshape(-1,3).astype(np.float32)
    crit=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,12,1.0)
    _,labels,centers=cv2.kmeans(flat,K,None,crit,3,cv2.KMEANS_PP_CENTERS)
    return labels.reshape(a.shape[:2]), centers.astype(np.int32)

def run(rough_path, out_path, K=5, black_lum=170):
    a=load_rgb(rough_path)
    H,W=a.shape[:2]
    labels,centers=segment(a,K)
    edge=np.zeros((H,W),bool)
    edge[:-1,:]|=labels[:-1,:]!=labels[1:,:]
    edge[:,:-1]|=labels[:,:-1]!=labels[:,1:]
    # add strong dark structural strokes (the outline stems of pencil lines)
    dark=(a.max(axis=2)<black_lum)
    cand=edge|dark
    cand&=~mask_regions(a.shape)
    lab,n=cc_label(cand,np.ones((3,3))); sz=np.bincount(lab.ravel())
    keep=np.zeros(n+1,bool); keep[1:]=sz[1:]>=6; cand=keep[lab]
    # color each candidate pixel by the hue at that location in the rough
    r,g,b=a[...,0].astype(np.int32),a[...,1].astype(np.int32),a[...,2].astype(np.int32)
    lum=0.3*r+0.6*g+0.1*b; sat=a.max(axis=2).astype(np.int32)-a.min(axis=2).astype(np.int32)
    out=np.full_like(a,WHITE)
    # classify each candidate pixel
    green=cand&(g>r+10)&(g>b+10)&(g>105)
    cyan=cand&(b>r+10)&(g>r+10)&(abs(g-b)<75)&(~green)
    red=cand&(r>g+10)&(r>b+10)&(r>115)
    # neutral/dark -> structure black; everything else not colored -> black
    struct=cand&(~green)&(~cyan)&(~red)
    out[green]=GREEN; out[cyan]=BLUE; out[red]=RED; out[struct]=BLACK
    save_rgb(out,out_path); return out

if __name__=="__main__":
    from paths import asset, data, out
    src=asset("KTK_04_246B","源文件","描原")
    base=data("KTK_04_246B")
    outdir=out("outA"); os.makedirs(outdir,exist_ok=True)
    tot_f1=0
    for rough,refn in {"A1.jpg":"A0001","A2.jpg":"A0006","A3.jpg":"A0009"}.items():
        outp=os.path.join(outdir,refn+".png")
        run(os.path.join(src,rough),outp)
        ref=load_rgb(os.path.join(base,"成品","描原",refn+".png"))
        pred=load_rgb(outp)
        mp=(pred.max(axis=2)<250); mr=(ref.max(axis=2)<250)
        p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
        st=closed_region_stats(mp); tot_f1+=f1
        print(f"{rough}->{refn}: P={p:.3f} R={rec:.3f} F1={f1:.3f} Chamfer={cd:.1f} px={mp.sum()} "
              f"闭合内区={st['interior_regions']} 内区面积={st['interior_area']} 封闭占比={st['interior_area']/max(1,mp.sum()):.3f}")
    print(f"平均F1={tot_f1/3:.3f}")
