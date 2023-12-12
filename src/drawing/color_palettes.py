import colorsys
from util.maths import lerp, clamp
from util.color import rgb, hsl 
import math

INTERPOLATE_HUE = 1
INTERPOLATE_VALUE = 2
INTERPOLATE_LIGHTNESS = 2
INTERPOLATE_SATURATION = 4
INTERPOLATE_ALL = INTERPOLATE_SATURATION | INTERPOLATE_VALUE | INTERPOLATE_HUE

def palletize(start, end, start_hsv, end_hsv, num_buckets, interpolation_mode=INTERPOLATE_ALL):
    sh, ss, sv = start_hsv
    eh, es, ev = end_hsv
    distance = end - start
    bucket_size = distance / num_buckets
    inter_hue = INTERPOLATE_HUE & interpolation_mode
    inter_val = INTERPOLATE_VALUE & interpolation_mode
    inter_sat = INTERPOLATE_SATURATION & interpolation_mode
    buckets = []
    for step in range(num_buckets):
        frac = step / num_buckets
        ih = lerp(sh, eh, frac) if inter_hue else eh
        iss = lerp(ss, es, frac) if inter_sat else es
        iv = lerp(sv, ev, frac) if inter_val else ev
        bucket_start = start + bucket_size * step
        bucket_end = start + (bucket_size * (step + 1))
        bucket_end = clamp(start, end, bucket_end)

        buckets.append([math.floor(bucket_start), math.ceil(bucket_end), (ih, iss, iv)])

    return buckets


seaborn_like_manual = [
    [0, 50, (255, 255, 255)],  # white at 0
    [50, 120, rgb(204, 225, 255)],
    [120, 180, rgb(102, 166, 255)], 
    [180, 220, rgb(51, 136, 255)],
    [220, 255, rgb(0, 108, 255)],  # max sat
]

seaborn_like_hsl = [
    [start, end, vals] 
    for (start, end, vals) in palletize(
        0, 255, (215/360, 0.99, 0.99), (215/360, 0.99, 0.5), 12, interpolation_mode=INTERPOLATE_LIGHTNESS
        )
]

seaborn_like = [[a, b, hsl(*c)] for a, b, c in seaborn_like_hsl]
seaborn_like_128 = [[start, end, hsl(*vals)] for (start, end, vals) in palletize(
        0, 255, (215/360, 0.99, 0.99), (215/360, 0.99, 0.5), 128, interpolation_mode=INTERPOLATE_LIGHTNESS
        )]

seaborn_like_250 = [[start, end, hsl(*vals)] for (start, end, vals) in palletize(
        0, 255, (215/360, 0.99, 0.99), (215/360, 0.99, 0.5), 250, interpolation_mode=INTERPOLATE_LIGHTNESS
        )]

grayscale = [[a, b, c] for a, b, c in palletize(0, 255, (0, 0, 0), (255, 255, 255), interpolation_mode=INTERPOLATE_ALL, num_buckets=6)]
