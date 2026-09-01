# -*- coding: utf-8 -*-
"""测量粗稿 ink 的局部宽度分布, 分离'线'(窄)与'面'(宽).
用距离变换: 每个 ink 像素到背景的距离近似半宽. 结构线宽度~1-2, 填充块宽度大."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.ndimage import distance_transform_edt
from io_utils import load_rgb

a = load_rgb(r"D:\desktop\picture\KTK_04_246B\源文件\描原\A1.jpg")
flat = a.reshape(-1,3).astype(np.int32)
ink = (255 - flat.min(axis=1) > 18).reshape(a.shape[:2])
dt = distance_transform_edt(ink)
print("ink px", ink.sum())
print("dt (half-width) at ink pixels: p50=%.1f p75=%.1f p90=%.1f p95=%.1f p99=%.1f max=%.1f" % (
    np.percentile(dt[ink],50),np.percentile(dt[ink],75),np.percentile(dt[ink],90),
    np.percentile(dt[ink],95),np.percentile(dt[ink],99),dt.max()))
# histogram
import numpy as np
for lo in range(0, 8):
    m = (dt[ink]>=lo)&(dt[ink]<lo+1)
    print(f"  halfwidth {lo}-{lo+1}: {m.sum():8d} ({m.mean()*100:5.2f}%)")
