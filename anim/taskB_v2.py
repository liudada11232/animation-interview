# -*- coding: utf-8 -*-
"""中割 v2 — 双模态融合插值: 小位移段用稠密光流, 大位移(旋转)段用刚体变换+光流残差.

A0006->A0009 头转 ~45°, 纯光流失效(Chamfer 15px). 方案:
  1. estimateAffinePartial2D (ORB 特征) 估计刚体全局变换 (旋转+平移+缩放) — 捕捉转头主运动
  2. 对刚体对齐后的残差用稠密光流修正 (局部非线性)
  3. 双向往返一致 + 骨架化后处理去碎片
先测单纯刚体插值的效果, 对比光流.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from io_utils import load_rgb, save_rgb
from metrics import precision_recall_f1, chamfer_distance
from thinning import zhang_suen
from scipy.ndimage import label as cc_label

def rigid_transform(imgA, imgB):
    """ORB+RANSAC 估计 A->B 的刚体变换 (2x3 相似变换)."""
    ga=cv2.cvtColor(imgA.astype(np.uint8),cv2.COLOR_RGB2GRAY)
    gb=cv2.cvtColor(imgB.astype(np.uint8),cv2.COLOR_RGB2GRAY)
    ia=255-ga; ib=255-gb
    ia=np.clip(ia*3,0,255).astype(np.uint8); ib=np.clip(ib*3,0,255).astype(np.uint8)
    orb=cv2.ORB_create(nfeatures=8000)
    ka,da=orb.detectAndCompute(ia,None); kb,db=orb.detectAndCompute(ib,None)
    if da is None or db is None or len(ka)<10 or len(kb)<10:
        return np.eye(2,3,dtype=np.float32)
    bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
    ms=sorted(bf.match(da,db),key=lambda m:m.distance)[:800]
    if len(ms)<10:
        return np.eye(2,3,dtype=np.float32)
    src=np.float32([ka[m.queryIdx].pt for m in ms]).reshape(-1,1,2)
    dst=np.float32([kb[m.trainIdx].pt for m in ms]).reshape(-1,1,2)
    M,inl=cv2.estimateAffinePartial2D(src,dst,None,cv2.RANSAC,3.0)
    if M is None:
        return np.eye(2,3,dtype=np.float32)
    return M

def interp_rigid(imgA, imgB, t):
    """刚体插值: 线性插值变换参数."""
    M=rigid_transform(imgA,imgB)
    Mt=np.zeros((2,3),np.float32)
    Mt[0,0]=1+(M[0,0]-1)*t; Mt[0,1]=M[0,1]*t; Mt[0,2]=M[0,2]*t
    Mt[1,0]=M[1,0]*t; Mt[1,1]=1+(M[1,1]-1)*t; Mt[1,2]=M[1,2]*t
    MB=cv2.invertAffineTransform(M)
    MtB=np.zeros((2,3),np.float32)
    MtB[0,0]=1+(MB[0,0]-1)*(1-t); MtB[0,1]=MB[0,1]*(1-t); MtB[0,2]=MB[0,2]*(1-t)
    MtB[1,0]=MB[1,0]*(1-t); MtB[1,1]=1+(MB[1,1]-1)*(1-t); MtB[1,2]=MB[1,2]*(1-t)
    h,w=imgA.shape[:2]
    wA=cv2.warpAffine(imgA.astype(np.uint8),Mt,(w,h),flags=cv2.INTER_LINEAR,
                      borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255))
    wB=cv2.warpAffine(imgB.astype(np.uint8),MtB,(w,h),flags=cv2.INTER_LINEAR,
                      borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255))
    lA=(255-wA.min(axis=2)); lB=(255-wB.min(axis=2))
    out=np.full_like(imgA,255); useA=lA>=lB
    out[useA]=wA[useA]; out[~useA]=wB[~useA]
    return out

PAL=np.array([[255,255,255],[0,0,0],[0,0,255],[255,0,0],[0,255,0]],np.float32)
def snap(img):
    flat=img.reshape(-1,3).astype(np.float32)
    d=np.linalg.norm(flat[:,None,:]-PAL[None,:,:],axis=2)
    return PAL[np.argmin(d,axis=1)].astype(np.uint8).reshape(img.shape)

def cleanup(img):
    """骨架化+去微小碎片+snap 回规范色."""
    flat=img.reshape(-1,3).astype(np.int32)
    lm=(255-flat.min(axis=1)>25).reshape(img.shape[:2])
    sk=zhang_suen(lm,max_iter=30)
    lab,n=cc_label(sk,np.ones((3,3)))
    sz=np.bincount(lab.ravel())
    keep=np.zeros(n+1,bool); keep[1:]=sz[1:]>=4
    sk=keep[lab]
    out=np.full_like(img,255)
    # 颜色从原图取 (骨架像素处的原色)
    r,g,b=img[...,0].astype(np.int32),img[...,1].astype(np.int32),img[...,2].astype(np.int32)
    lum=0.3*r+0.6*g+0.1*b; sat=img.max(axis=2).astype(np.int32)-img.min(axis=2).astype(np.int32)
    green=sk&(g>r+12)&(g>b+12)&(g>110)
    cyan=sk&(b>r+12)&(g>r+12)&(abs(g-b)<70)&(~green)
    red=sk&(r>g+12)&(r>b+12)&(r>120)
    struct=sk&(~green)&(~cyan)&(~red)
    out[green]=[0,255,0]; out[cyan]=[0,0,255]; out[red]=[255,0,0]; out[struct]=[0,0,0]
    return out

if __name__=="__main__":
    base=r"D:\desktop\mianshi\work\png\KTK_04_246B"
    src=os.path.join(base,"源文件","中割")
    ref=os.path.join(base,"成品","中割")
    a6=load_rgb(os.path.join(src,"A0006.png")); a9=load_rgb(os.path.join(src,"A0009.png"))
    for i,t in [(7,1/3),(8,2/3)]:
        raw=interp_rigid(a6,a9,t)
        rgb=snap(raw)
        r7=load_rgb(os.path.join(ref,f"A000{i}.png"))
        mp=(rgb.max(axis=2)<250); mr=(r7.max(axis=2)<250)
        p,rec,f1=precision_recall_f1(mp,mr,tol=3); cd=chamfer_distance(mp,mr)
        print(f"rigid A000{i}: F1={f1:.3f} P={p:.3f} R={rec:.3f} Chamfer={cd:.2f} px={mp.sum()}")
        cleanup_img=cleanup(rgb)
        mp2=(cleanup_img.max(axis=2)<250)
        p2,rec2,f12=precision_recall_f1(mp2,mr,tol=3)
        print(f"   +cleanup: F1={f12:.3f} P={p2:.3f} R={rec2:.3f} px={mp2.sum()}")