import random
import math
import numpy as np
RANDOM = random.Random()

def clamp(minv, maxv, val):
    clamped_value = min(maxv, max(minv, val))
    return clamped_value

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


def random_position(size):
    return (RANDOM.randint(0, size - 1), RANDOM.randint(0, size - 1))

def point_dist(src, target):
    # a and b are length 2
    return math.sqrt(vec_len((target[0] - src[0], target[1] - src[1])))

def vec_len(vec):
    return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

def vec_mid(vec1, vec2):
    return (vec1[0] + vec2[0]) / 2, (vec1[1] + vec2[1])

def midpoint(vectors):
    xpos = list(map(lambda vec: vec[0], vectors))
    ypos = list(map(lambda vec: vec[1], vectors))
    return sum(xpos) / len(xpos), sum(ypos) / len(ypos)

def vec_op(a, b, op):
    if op == "+":
        return a[0] + b[0], a[1] + b[1]
    elif op == "*":
        return a[0] * b[0], a[1] * b[1]
    elif op == "/":
        return a[0] / b[0], a[1] / b[1]
    elif op == "-":
        return a[0] - b[0], a[1] - b[1]
        

def vec_neg(vec):
    return -vec[0], -vec[1]

def vec_norm(vec):
    vlen = vec_len(vec)
    if vlen == 0:
        return vec
    return vec[0] / vlen, vec[1] / vlen

def vec_sub(a, b):
    return vec_op(a, b, "-")

def vec_add(a, b):
    return vec_op(a, b, "+")

def int_vec(vec):
    return int(vec[0]), int(vec[1])


def gkern(l=5, sig=1.):
    """creates gaussian kernel with side length `l` and a sigma of `sig`
    """
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)

def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (v - a) / (b - a)


def remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.
    Examples
    --------
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)
    """
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))


def pick_random_truthy(arr):
    truthy = np.argwhere(arr)
    if not truthy.any():
        return False, None
    else:
        random_idx = RANDOM.randint(0, len(truthy) - 1)
        return True, truthy[random_idx]