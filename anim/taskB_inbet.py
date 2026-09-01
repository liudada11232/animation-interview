# -*- coding: utf-8 -*-
"""题B 中割 (in-between) core — flow-based line-art interpolation.

Keyframes are 4-color line art (white bg + black/blue/red/green 1px lines). We produce intermediate
frames that stay in that same line-art form (NOT rendered fills). Approach:
  * estimate dense optical flow between consecutive keyframes (Farneback on the line mask / grayscale)
  * for each in-between time t, warp the two endpoint line-art images by (1-t)*flow and t*flow and
    combine (union of warped line pixels, colored by their own line color).
Motion is assumed equal-interval (the 律表 gives no readable timing) — stated in the report.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from io_utils import load_rgb, save_rgb, to_line_mask

def flow_between(imgA, imgB, winsize=21, pyr=4):
    ga = cv2.cvtColor(imgA.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(imgB.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    flow = cv2.calcOpticalFlowFarneback(ga, gb, None, pyr_scale=0.5, levels=pyr, winsize=winsize,
                                        iterations=4, poly_n=7, poly_sigma=1.5, flags=0)
    return flow

def warp_line_art_from_to(img, flow, t):
    """Warp line art img BY t*flow (interpolation toward the target at time t in [0,1]).
    Returns warped RGB image (float)."""
    H, W = img.shape[:2]
    # sample target grid, look back into source
    grid_y, grid_x = np.mgrid[0:H, 0:W].astype(np.float32)
    src_x = grid_x - t * flow[..., 0]
    src_y = grid_y - t * flow[..., 1]
    map_x = np.clip(src_x, 0, W - 1)
    map_y = np.clip(src_y, 0, H - 1)
    out = np.zeros_like(img, dtype=np.float32)
    for c in range(3):
        out[..., c] = cv2.remap(img[..., c].astype(np.float32), map_x, map_y, cv2.INTER_LINEAR)
    return out

def interpolate(imgA, imgB, t, winsize=21, pyr=4):
    """Produce the in-between frame at fraction t between line arts imgA and imgB."""
    flow_AB = flow_between(imgA, imgB, winsize, pyr)
    flow_BA = flow_between(imgB, imgA, winsize, pyr)
    # warp both endpoints toward the middle
    wA = warp_line_art_from_to(imgA, flow_AB, t)   # move A by t*flow_AB
    wB = warp_line_art_from_to(imgB, flow_BA, 1 - t)  # move B by (1-t)*flow_BA
    # combine: a target pixel is a line if either warped endpoint has a line there; take the
    # higher-contrast (darker / more saturated) one.
    def line_strength(im):
        return (255 - im.min(axis=2)).astype(np.float32)
    sA = line_strength(wA); sB = line_strength(wB)
    lwA = (sA > 25); lwB = (sB > 25)
    out = np.full_like(imgA, 255, dtype=np.uint8)
    both = lwA & lwB
    onlyA = lwA & ~lwB
    onlyB = lwB & ~lwA
    for mask in [both, onlyA, onlyB]:
        pass
    # priority: if both agree use A's color; if only one, use that.
    use_A = lwA
    out[use_A] = np.clip(wA[use_A], 0, 255).astype(np.uint8)
    onlyB_mask = (~use_A) & lwB
    out[onlyB_mask] = np.clip(wB[onlyB_mask], 0, 255).astype(np.uint8)
    # snap to the 4-color + green palette
    out = snap_palette(out)
    return out

PAL = np.array([[255,255,255],[0,0,0],[0,0,255],[255,0,0],[0,255,0]], dtype=np.float32)

def snap_palette(img):
    flat = img.reshape(-1,3).astype(np.float32)
    d = np.linalg.norm(flat[:,None,:]-PAL[None,:,:], axis=2)
    idx = np.argmin(d, axis=1)
    return PAL[idx].astype(np.uint8).reshape(img.shape)

if __name__ == "__main__":
    from paths import data, out
    base = data("KTK_04_246B")
    src = os.path.join(base, "源文件", "中割")
    outdir = out("outB")
    os.makedirs(outdir, exist_ok=True)
    def K(n): return load_rgb(os.path.join(src, n + ".png"))
    a1, a6, a9 = K("A0001"), K("A0006"), K("A0009")
    # Save keyframes unchanged
    for n, im in [("A0001",a1),("A0006",a6),("A0009",a9)]:
        save_rgb(im, os.path.join(outdir, n+".png"))
    # A0002-A0005 between A0001 and A0006 (small motion -> winsize 21)
    for i, t in zip(range(2,6), [0.2,0.4,0.6,0.8]):
        f = interpolate(a1, a6, t, winsize=21, pyr=4)
        save_rgb(f, os.path.join(outdir, f"A000{i}.png"))
    # A0007-A0008 between A0006 and A0009 (large head rotation -> bigger winsize)
    for i, t in zip(range(7,9), [1/3, 2/3]):
        f = interpolate(a6, a9, t, winsize=31, pyr=4)
        save_rgb(f, os.path.join(outdir, f"A000{i}.png"))
    print("done")
