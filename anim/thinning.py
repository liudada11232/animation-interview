# -*- coding: utf-8 -*-
"""Zhang-Suen binary thinning (skeletonization), numpy implementation.
Works on a boolean image (True = foreground). Returns boolean skeleton (1px)."""
import numpy as np

def zhang_suen(img, max_iter=60):
    img = img.copy().astype(np.uint8)
    changed = True
    it = 0
    while changed and it < max_iter:
        changed = False
        it += 1
        # step 1
        p = _thin_pass(img)
        # step 2
        p = _thin_pass(p)
        if np.array_equal(p, img):
            changed = False
        img = p
    return img.astype(bool)

def _neighbors(P):
    """P: 2D uint8 binary. Return 8-neighbor values P2..P9 (clockwise from north)."""
    p2 = np.roll(P, -1, 0)          # north
    p3 = np.roll(np.roll(P, -1, 0), 1, 1)  # NE
    p4 = np.roll(P, 1, 1)           # east
    p5 = np.roll(np.roll(P, 1, 0), 1, 1)   # SE
    p6 = np.roll(P, 1, 0)           # south
    p7 = np.roll(np.roll(P, 1, 0), -1, 1)  # SW
    p8 = np.roll(P, -1, 1)          # west
    p9 = np.roll(np.roll(P, -1, 0), -1, 1) # NW
    return [p2, p3, p4, p5, p6, p7, p8, p9]

def _thin_pass(P):
    nbrs = _neighbors(P)
    P2, P3, P4, P5, P6, P7, P8, P9 = nbrs
    B = P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9
    # A(P): number of 0->1 transitions in sequence P2,P3,...,P9,P2
    seq = [P2, P3, P4, P5, P6, P7, P8, P9, P2]
    A = np.zeros_like(P, dtype=np.uint8)
    for i in range(8):
        A += ((seq[i] == 0) & (seq[i+1] == 1)).astype(np.uint8)
    cond = (P == 1) & (B >= 2) & (B <= 6) & (A == 1)
    # step conditions (parity of neighbors)
    m1 = (P2 * P4 * P6) == 0
    m2 = (P4 * P6 * P8) == 0
    m = cond & m1 & m2
    P1 = P.copy()
    P1[m] = 0
    # second sub-iteration uses parity-shifted conditions (transposed)
    nbrs2 = _neighbors(P1)
    Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9 = nbrs2
    B2 = Q2 + Q3 + Q4 + Q5 + Q6 + Q7 + Q8 + Q9
    seq2 = [Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q2]
    A2 = np.zeros_like(P1, dtype=np.uint8)
    for i in range(8):
        A2 += ((seq2[i] == 0) & (seq2[i+1] == 1)).astype(np.uint8)
    cond2 = (P1 == 1) & (B2 >= 2) & (B2 <= 6) & (A2 == 1)
    m1b = (Q2 * Q4 * Q8) == 0
    m2b = (Q4 * Q6 * Q8) == 0
    m2 = cond2 & m1b & m2b
    P1[m2] = 0
    return P1
