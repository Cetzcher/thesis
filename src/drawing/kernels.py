from skimage.draw import circle_perimeter
from drawing.map_operations import size
import numpy as np

def circle(data, center, radius, value, interpolation_function=None):
    """Draws a circle into the data by modifying the data directly the 
    the fall off will be linear i.e. value[x, y] = 1/distance_to_center * value"""
    if not interpolation_function:
        interpolation_function = lambda x: x
    s = size(data)
    Y, X = np.ogrid[:s, :s]
    dist = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    gain = value * 1 / interpolation_function(dist + 1)
    gain[dist > radius] = 0
    data += gain

def rect(data, center, size, value):
    x, y = center
    min_x, min_y = int(x - size), int(y - size)
    max_x, max_y = int(x + size), int(y + size)
    data[min_y:max_y, min_x:max_x] = value