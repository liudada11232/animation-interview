# -*- coding: utf-8 -*-
"""题C 评测: precision / coverage / line-preservation / cross-frame consistency.
Definitions (matching the brief):
  * precision  = area of pred colored pixels whose RGB EXACTLY equals the reference's / area pred colored.
  * coverage   = fraction of reference's colored area that pred matches (within small tol).
  * line-preservation = number of line-art pixels changed by the algorithm == 0 ideally.
  * cross-frame consistency = same-pixel color stability across frames.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from io_utils import load_rgb

BASE = r"D:\desktop\mianshi\work\png\KTK_04_246B"
SRC = os.path.join(BASE, "源文件", "上色")
REF = os.path.join(BASE, "成品", "上色")
OUT = r"D:\desktop\mianshi\work\outC"   # 合规版产物（仅设定图色卡）
frames = [f"A000{i}" for i in range(1, 10)]

def fill_mask(flat):
    """colored fill (non-white) mask over a flattened RGB array."""
    return ~np.all(flat == 255, axis=1)

read = {f: load_rgb(os.path.join(SRC, f + ".png")) for f in frames}
refr = {f: load_rgb(os.path.join(REF, f + ".png")) for f in frames}
pred = {f: load_rgb(os.path.join(OUT, f + ".png")) for f in frames}

tot_exact = tot_pred = tot_cover_n = tot_cover_d = tot_line = 0
for f in frames:
    s, rr, pp = read[f].reshape(-1, 3).astype(np.int32), refr[f].reshape(-1, 3).astype(np.int32), pred[f].reshape(-1, 3).astype(np.int32)
    # line preservation: line pixels of the INPUT line art must be unchanged in output.
    src = read[f]
    src_line = (255 - src.max(axis=2)) >= 25   # line-ish pixels of input (2D mask)
    line_changed = int(np.sum((src[src_line] != pred[f][src_line]).any(axis=1)))
    ld = line_changed
    tot_line += ld    # precision
    pf = fill_mask(pp)
    same = np.all(pp == rr, axis=1)
    exact = int((same & pf).sum())
    tot_exact += exact; tot_pred += int(pf.sum())
    prec = exact / max(1, int(pf.sum()))
    # coverage
    rfc = fill_mask(rr)
    refc = rr[rfc]; predc = pp[rfc]
    d = np.sqrt(((refc - predc) ** 2).sum(axis=1))
    matched = int((d <= 10).sum())
    tot_cover_n += matched; tot_cover_d += int(rfc.sum())
    cov = matched / max(1, int(rfc.sum()))
    print(f"{f}: 填色={int(pf.sum()):7d} 精确={exact:7d} 精确率={prec:.3f} 覆盖={matched:7d}/{int(rfc.sum()):7d} 覆盖率={cov:.3f} 线损={ld}")

print("\n==== 汇总 ====")
print(f"整体精确率(面积) = {tot_exact/max(1,tot_pred):.4f}  (填色总面积 {tot_pred})")
print(f"整体覆盖率(面积) = {tot_cover_n/max(1,tot_cover_d):.4f}")
print(f"线损总像素 = {tot_line} (应=0)")

# cross-frame stability: frame i vs frame 1 over pixels colored in both (pred)
print("\n跨帧一致性 (pred, vs A0001):")
base_flat = pred["A0001"].reshape(-1, 3).astype(np.int32)
for f in frames[1:]:
    bflat = pred[f].reshape(-1, 3).astype(np.int32)
    fillA = fill_mask(base_flat) & fill_mask(bflat)
    keep = int(np.all(base_flat[fillA] == bflat[fillA], axis=1).sum())
    print(f"  {f}: 帧1填色区颜色保持率 = {keep/max(1,int(fillA.sum())):.3f}")
