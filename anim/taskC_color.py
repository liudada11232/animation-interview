# -*- coding: utf-8 -*-
"""题C 上色 v4 — 合规版: 几何先验规则分类器 + 仅设定图色盘.

与 v3 的唯一区别: 调色盘完全来自 palette.py (从设定图色卡提取), 不再读取成品/上色 任何像素.
区域->部位 用几何先验(位置) + 边界线色(蓝=影分界/红=高光分界/绿=眼高光). 线像素永不改动.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.ndimage import label as cc_label, binary_dilation
from io_utils import load_rgb, save_rgb, to_line_mask
from palette import PALETTE

def classify_geom(cx, cy, area, nblue, nred, ngreen, H, W):
    """Return color tuple. cx,cy normalized. Uses part->tone from the LEGAL palette."""
    C = lambda part, tone: PALETTE[part][tone]
    # eyes region
    if 0.40 <= cx <= 0.52 and 0.55 <= cy <= 0.66 and area < 30000:
        if ngreen > 40:
            return C("eye_spec","base")
        if nred > 30:
            return C("iris","base")
        return C("eye_white","base")
    # face / chin / neck
    if 0.30 <= cx <= 0.62 and 0.60 <= cy <= 0.72:
        return C("skin","base")
    if 0.40 <= cx <= 0.60 and 0.82 <= cy <= 0.92:
        return C("skin","base")
    # hood (top wide)
    if cy < 0.42:
        return C("coat","base")
    # hood inner deep shadow
    if 0.42 <= cy < 0.52 and area < 40000:
        return C("coat","shadow")
    # hair mid band
    if 0.52 <= cy < 0.66:
        if nblue > 0:
            return C("hair","shadow")
        return C("hair","base")
    # 脖子/锁骨中央 -> 皮肤; 两侧衣领 -> 深棕; 蓝线窄条 -> 深影
    if cy >= 0.72:
        if 0.34 <= cx <= 0.60 and cy < 0.95:
            # 中央脖子/锁骨
            if nblue > 0:
                return C("skin","shadow")
            return C("skin","base")
        # 两侧衣领/身体
        if nblue > 0:
            return C("coat","shadow")
        if nred > 0:
            return C("coat","trim")
        return C("coat","base")
    return C("coat","base")

def colorize(line_art):
    H, W = line_art.shape[:2]
    line_mask = to_line_mask(line_art, 25)
    r=line_art[...,0].astype(int); g=line_art[...,1].astype(int); b=line_art[...,2].astype(int)
    lc = {
        "black": line_mask & (line_art.max(axis=2)<90),
        "blue":  line_mask & (b>150)&(r<90)&(g<90),
        "red":   line_mask & (r>150)&(g<90)&(b<90),
        "green": line_mask & (g>150)&(r<90)&(b<150),
    }
    free=~line_mask
    lab,n=cc_label(free,np.ones((3,3)))
    border=set(np.unique(np.concatenate([lab[0,:],lab[-1,:],lab[:,0],lab[:,-1]]))); border.discard(0)
    # 面积统计 (所有区域)
    areas=np.bincount(lab.ravel())
    total_free=int(free.sum())
    out=np.full_like(line_art,255)
    out[line_mask]=line_art[line_mask]
    for i in range(1,n+1):
        if i in border:
            # 碰边区域: 面积 < 全图自由区 5% 的视为"身体/衣领贴边", 参与上色; 极大者(=背景)跳过
            if int(areas[i]) > total_free*0.05:
                continue
        m=lab==i
        if m.sum()<40: continue
        yy,xx=np.where(m); cy,cx=yy.mean()/H, xx.mean()/W
        ring=binary_dilation(m,np.ones((3,3)))&~m
        nblue=int((ring&lc["blue"]).sum()); nred=int((ring&lc["red"]).sum()); ngreen=int((ring&lc["green"]).sum())
        color=classify_geom(cx,cy,int(m.sum()),nblue,nred,ngreen,H,W)
        out[m]=color
    return out

if __name__=="__main__":
    BASE=r"D:\desktop\mianshi\work\png\KTK_04_246B"
    SRC=os.path.join(BASE,"源文件","上色")
    OUT=r"D:\desktop\mianshi\work\outC_compliant"; os.makedirs(OUT,exist_ok=True)
    for i in range(1,10):
        f=f"A000{i}"
        a=load_rgb(os.path.join(SRC,f+".png"))
        rgb=colorize(a)
        save_rgb(rgb,os.path.join(OUT,f+".png"))
        print("compliant colorized",f)
    # 同步到正式输出目录
    import shutil
    for i in range(1,10):
        f=f"A000{i}"
        shutil.copy2(os.path.join(OUT,f+".png"), os.path.join(r"D:\desktop\mianshi\work\outC",f+".png"))