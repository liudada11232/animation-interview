# -*- coding: utf-8 -*-
"""诊断上色失败类型: 把覆盖率/精确率的损失拆成三部分
  溢出(涂到参考没涂的地方) / 漏涂(参考涂了我没涂) / 错涂(都涂了但色不对)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb

BASE=r"D:\desktop\mianshi\work\png\KTK_04_246B"
SRC=os.path.join(BASE,"源文件","上色")
REF=os.path.join(BASE,"成品","上色")
OUT=r"D:\desktop\mianshi\work\outC"

tot_overflow=tot_under=tot_wrong=0
tot_pred_fill=tot_ref_fill=tot_match=0
for i in range(1,10):
    f=f"A000{i}"
    a=load_rgb(os.path.join(SRC,f+".png")).reshape(-1,3).astype(np.int32)
    r=load_rgb(os.path.join(REF,f+".png")).reshape(-1,3).astype(np.int32)
    p=load_rgb(os.path.join(OUT,f+".png")).reshape(-1,3).astype(np.int32)
    pf=~np.all(p==255,axis=1)      # 我涂了
    rf=~np.all(r==255,axis=1)      # 参考涂了
    # 线像素(both have line)排除
    line_mask=~np.all(a==255,axis=1)
    pf=pf&~line_mask; rf=rf&~line_mask
    overflow=int((pf&~rf).sum())       # 我涂了但参考白底 -> 溢出
    under=int((~pf&rf).sum())          # 参考涂了我白底 -> 漏涂
    both=pf&rf
    wrong=int((both&~np.all(p==r,axis=1)).sum())  # 都涂了但色不同
    match=int((both&np.all(p==r,axis=1)).sum())
    tot_overflow+=overflow; tot_under+=under; tot_wrong+=wrong
    tot_match+=match
    tot_pred_fill+=int(pf.sum()); tot_ref_fill+=int(rf.sum())
    print(f"{f}: 溢出={overflow:7d} 漏涂={under:7d} 错涂={wrong:7d} 正确={match}")

print(f"\n==== 汇总 ====")
print(f"预测填色总面积={tot_pred_fill}, 参考填色总面积={tot_ref_fill}")
print(f"溢出(涂出去)     : {tot_overflow:8d} = {tot_overflow/max(1,tot_pred_fill)*100:.1f}% of 预测填色")
print(f"漏涂(没涂到)     : {tot_under:8d} = {tot_under/max(1,tot_ref_fill)*100:.1f}% of 参考填色")
print(f"错涂(颜色不对)   : {tot_wrong:8d}")
# 我的精确率 = match/pred_fill ; 覆盖率 = match/ref_fill (匹配口径, 与 evalC 的容差口径略不同)
print(f"校验: 匹配/预测 = {tot_match/max(1,tot_pred_fill):.3f} (严格精确率), 匹配/参考 = {tot_match/max(1,tot_ref_fill):.3f} (严格覆盖率)")
print(f"\n注意: 溢出+漏涂+错涂 的占比决定了改进方向: 溢出大->闭区域有缺口; 漏涂大->区域判白; 错涂大->配色规则差")