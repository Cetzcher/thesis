import numpy as np
from PIL import Image


def size(arrmap):
    return np.shape(arrmap)[0]

def is_square(arrmap):
    x, y, *_ = np.shape(arrmap)
    return x == y

def normalize(arrmap):
    return arrmap / np.max(arrmap)

def invert(arrmap):
    return np.abs(arrmap - 1)

def to_byte(arrmap):
    arrmap[arrmap > 1] = 1.0
    arrmap = arrmap * ((2 ** 8) - 1)
    arrmap = arrmap.astype(np.uint8)
    return arrmap

def to_palette(arrmap, palette):
    # palette should be a sorted list of lists in the form
    # of [ [min, max, value] ...]
    # where values of arrmap >= min and arrmap <= max will be set to value
    # a copy is returned
    out_val = palette[0][2]
    out_shape = None
    if isinstance(out_val, (float, int)):
        out_shape = out_val
    else:
        out_shape = len(out_val)

    s = size(arrmap)
    rgb_img = np.zeros([s, s, out_shape], dtype=np.uint8)
    for (lower, upper, color) in palette:
        idx = (arrmap >= lower) & (arrmap <= upper)
        rgb_img[idx] = color
    return rgb_img


def set_gradient_colors(mapref, arrmap, color, cutoff_low=0.5, cutoff_high=0.6, n=4):
    cpy = np.copy(arrmap)
    g = mapref.gradient(n=n)
    cpy[(g >= cutoff_low) & (g < cutoff_high)] = color
    return cpy
    


def write(arrmap, path, mode="L"):
    im = Image.fromarray(arrmap)
    im.convert(mode)
    im.save(path)
