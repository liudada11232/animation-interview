# -*- coding: utf-8 -*-
"""Shared IO + palette constants for the animation pipeline."""
import numpy as np
from PIL import Image


# ---- 4-color line spec (题A/B) ----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LINE_COLORS = {"white": WHITE, "black": BLACK, "blue": BLUE, "red": RED}


def load_rgb(path):
    """Load any image (png/jpg/tga) as an RGB uint8 array."""
    im = Image.open(path)
    im.load()
    return np.asarray(im.convert("RGB"), dtype=np.uint8)


def save_rgb(arr, path):
    Image.fromarray(np.asarray(arr, dtype=np.uint8), "RGB").save(path)


def to_line_mask(arr, non_white_thresh=25):
    """Return boolean mask of 'line' pixels (anything not near-white background)."""
    r = arr[..., 0].astype(np.int16)
    g = arr[..., 1].astype(np.int16)
    b = arr[..., 2].astype(np.int16)
    # distance from white
    d = np.maximum(np.maximum(255 - r, 255 - g), 255 - b)
    return d >= non_white_thresh


def color_decompose(arr, tol=60):
    """Decompose a 4-color line art into named boolean masks.
    Returns dict color->bool mask. Uses nearest-palette assignment."""
    flat = arr.reshape(-1, 3).astype(np.int32)
    names = ["white", "black", "blue", "red"]
    palette = np.array([WHITE, BLACK, BLUE, RED], dtype=np.int32)
    d = np.linalg.norm(flat[:, None, :] - palette[None, :, :], axis=2)
    idx = np.argmin(d, axis=1)
    masks = {}
    for k, name in enumerate(names):
        masks[name] = (idx == k).reshape(arr.shape[:2])
    return masks


def u8(arr):
    return np.asarray(arr, dtype=np.uint8)
