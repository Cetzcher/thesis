import colorsys
from util import RANDOM as R

def rgb_to_hex(r, g, b):
    r, g, b = int(r), int(g), int(b)
    r, g, b = min(r, 255), min(g, 255), min(b, 255)
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def hex_to_rgb(hex):
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
  
  return tuple(rgb)

def random_color():
    return rgb_to_hex(
        R.randint(0, 0xff),
        R.randint(0, 0xff),
        R.randint(0, 0xff)
    )

def rgb(r, g, b):
    return r, g, b

def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return r * 255, g * 255, b * 255

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r * 255, g * 255, b * 255