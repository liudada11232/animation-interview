# -*- coding: utf-8 -*-
"""KTK_05_140 进阶 — 上色. Same character (ミュイ), reuse the geometric rule colorizer.
Colors A-layer (A0001-A0005) and B-layer (B0001-B0003). Evaluate precision/coverage/line-loss."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb, save_rgb
from taskC_color import colorize
from evalC import fill_mask

if __name__=="__main__":
    from paths import data, out
    base=data("KTK_05_140")
    src=os.path.join(base,"源文件","上色")
    refroot=os.path.join(base,"成品","上色")
    outdir=out("outC5"); os.makedirs(outdir,exist_ok=True)
    jobs=[("A","A0001"),("A","A0002"),("A","A0003"),("A","A0004"),("A","A0005"),
          ("B","B0001"),("B","B0002"),("B","B0003")]
    te=tp=tcn=tcd=tline=0
    for layer, f in jobs:
        inp=os.path.join(src,layer,f+".png")
        outp=os.path.join(outdir,f"{layer}_{f}.png")
        a=load_rgb(inp)
        rgb=colorize(a)
        save_rgb(rgb,outp)
        ref=load_rgb(os.path.join(refroot,layer,f+".png"))
        # eval
        pp=rgb.reshape(-1,3).astype(np.int32); rr=ref.reshape(-1,3).astype(np.int32)
        src_flat=a.reshape(-1,3).astype(np.int32)
        pf=fill_mask(pp)
        same=np.all(pp==rr,axis=1); exact=int((same&pf).sum())
        te+=exact; tp+=int(pf.sum())
        rfc=fill_mask(rr); d=np.sqrt(((rr[rfc]-pp[rfc])**2).sum(axis=1))
        m=int((d<=10).sum()); tcn+=m; tcd+=int(rfc.sum())
        src_line=(255-a.max(axis=2))>=25
        ld=int(np.sum((a[src_line]!=rgb[src_line]).any(axis=1)))
        tline+=ld
        print(f"{layer}_{f}: 精确率={exact/max(1,int(pf.sum())):.3f} 覆盖率={m/max(1,int(rfc.sum())):.3f} 线损={ld}")
    print(f"\nKTK_05 整体精确率(面积)={te/max(1,tp):.4f}  覆盖率={tcn/max(1,tcd):.4f}  线损={tline}")
