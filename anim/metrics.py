# -*- coding: utf-8 -*-
"""Rigorous evaluation metrics for the three animation tasks.

All metrics are self-contained (numpy/scipy) so they can also be used to sanity
check against reference outputs. They are implemented to be BRUTALLY honest: e.g.
line-leak and region-mismatch are measured, not hand-waved.
"""
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_dilation, label as cc_label


# ---------------- Line-set metrics (题A 描原 / 题B 中割) ----------------

def chamfer_distance(mask_a, mask_b):
    """Symmetric (bidirectional) average Chamfer distance between two binary masks.
    Distance in pixels. Masks are boolean; a pixel is 'on' where True."""
    if mask_a.sum() == 0 or mask_b.sum() == 0:
        return float("inf")
    # distance from every pixel to nearest on-pixel of each set
    da = distance_transform_edt(~mask_a)   # distance to set a
    db = distance_transform_edt(~mask_b)   # distance to set b
    # for each on-pixel in b, nearest a; and vice versa
    d_b_to_a = da[mask_b].mean()
    d_a_to_b = db[mask_a].mean()
    return float((d_b_to_a + d_a_to_b) / 2.0)


def precision_recall_f1(pred, ref, tol=3):
    """Tolerance-dilated F1: pred line pixels matched within tol of ref, and vice versa.
    tol is the dilation radius in pixels."""
    kernel = np.zeros((2 * tol + 1, 2 * tol + 1), bool)
    yy, xx = np.mgrid[-tol:tol + 1, -tol:tol + 1]
    kernel[yy ** 2 + xx ** 2 <= tol ** 2] = True
    ref_dil = binary_dilation(ref, structure=kernel)
    pred_dil = binary_dilation(pred, structure=kernel)
    tp = (pred & ref_dil).sum()      # pred pixels near ref
    fp = (pred & ~ref_dil).sum()
    fn = (ref & ~pred_dil).sum()
    tp = float(tp)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


# ---------------- Region fill metrics (题A 闭合度 / 题C 上色) ----------------

def closed_region_stats(line_mask):
    """Robust region closure test.
    - Count closed (interior) regions and their total area.
    - Detect leakage: if all background merges with the outer background => huge outer => low closure.
    Returns dict."""
    free = ~line_mask
    lab, n = cc_label(free, structure=np.ones((3, 3)))
    border_labels = set(np.unique(np.concatenate([
        lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]])))
    border_labels.discard(0)
    areas = np.bincount(lab.ravel())
    outer_area = sum(areas[l] for l in border_labels)
    interior_area = int(free.sum()) - outer_area
    # number of interior regions
    interior_regions = sum(1 for l in range(1, n + 1) if areas[l] > 0 and l not in border_labels)
    # largest interior region (the 'main' closed shape)
    largest_interior = 0
    for l in range(1, n + 1):
        if areas[l] > 0 and l not in border_labels:
            largest_interior = max(largest_interior, int(areas[l]))
    return {
        "interior_area": interior_area,
        "interior_regions": interior_regions,
        "largest_interior": largest_interior,
        "outer_area": int(outer_area),
        "total_free": int(free.sum()),
    }


# ---------------- Color/region metrics (题C 上色) ----------------

def color_exact_agreement(pred_rgb, ref_rgb, fg_mask):
    """Among foreground (colored, non-divide) pixels, fraction where pred == ref exactly (RGB equal).
    Returns (exact_area, colored_area, agreement, mismatch_area)."""
    valid = fg_mask
    # only consider pixels where ref is actually a fill color (not white bg / not line)
    same = np.all(pred_rgb == ref_rgb, axis=2) & valid
    colored_area = int(valid.sum())
    exact = int(same.sum())
    agree = exact / colored_area if colored_area else 0.0
    return exact, colored_area, agree, colored_area - exact


def coverage(pred_rgb, ref_rgb, ref_nonwhite, tol=8):
    """Coverage: fraction of ref's colored area that our prediction matches (within tol color dist)."""
    # ref colored area: pixels whose color is not white and not near-black line
    ref_c = ref_rgb.astype(np.int32)
    pred_c = pred_rgb.astype(np.int32)
    d = np.sqrt(((ref_c - pred_c) ** 2).sum(axis=2))
    matched = (d <= tol) & ref_nonwhite
    return float(matched.sum() / max(1, int(ref_nonwhite.sum())))
