from skimage.draw import circle_perimeter
from drawing.map_operations import size as _size
import numpy as np
from util.maths import vec_len
import vec

def circle(data, center, radius, value, interpolation_function=None):
    """Draws a circle into the data by modifying the data directly the 
    the fall off will be linear i.e. value[x, y] = 1/distance_to_center * value"""
    if not interpolation_function:
        interpolation_function = lambda x: x
    s = _size(data)
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


def cricle_with_overflow(data, center, radius, value, threshold=1, do_errode=False):
    """Adds 'height' to the data at center with the given radius, if the values 
    at the points overflow the threshold they are diffused to all points around it that are lower 
    than itself.
    
    
    Example:
    if our initial data looks like this 
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0

    and we add a value with radius = 1 to the middle we get
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0
    0 0 0 1 0 0 0
    0 0 1 1 1 0 0
    0 0 0 1 0 0 0
    0 0 0 0 0 0 0
    0 0 0 0 0 0 0

    
    if we now add it again we get
    0 0 0 0 0 0 0       =>  .0 .0 .0 .0 .0 .0 .0    =>  .0 .0 .0 .0 .0 .0 .0    =>  .0 .0 .0 .0 .0 .0 .0
    0 0 0 0 0 0 0       =>  .0 .0 .0 .3 .0 .0 .0    =>  .0 .0 .0 .3 .0 .0 .0    =>  .0 .0 .0 .3 .0 .0 .0
    0 0 0 2 0 0 0       =>  .0 .0 .6 01 .6 .0 .0    =>  .0 .0 .6 13 .6 .0 .0    =>  .0 .0 .7 01 .7 .0 .0
    0 0 2 2 2 0 0       =>  .0 .3 01 02 01 .3 .0    =>  .0 .3 13 01 13 .3 .0    =>  .0 .4 01 01 01 .4 .0
    0 0 0 2 0 0 0       =>  .0 .0 .6 01 .6 .0 .0    =>  .0 .0 .6 13 .6 .0 .0    =>  .0 .0 .7 01 .7 .0 .0
    0 0 0 0 0 0 0       =>  .0 .0 .0 .3 .0 .0 .0    =>  .0 .0 .0 .3 .0 .0 .0    =>  .0 .0 .0 .4 .0 .0 .0
    0 0 0 0 0 0 0       =>  .0 .0 .0 .0 .0 .0 .0    =>  .0 .0 .0 .0 .0 .0 .0    =>  .0 .0 .0 .0 .0 .0 .0
    
    when there is no way to reduce the value because all other neighbors already have the maximum value we do nothing.
    """

    size = _size(data)
    Y, X = np.ogrid[:size, :size]
    dist = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    data[dist <= radius] += value
    # after the data has been modified we can look at the entire grid and perform the errosion process
    # first collect all points that are in the radius that are overflowing+
    if do_errode:
        errode(data, threshold=threshold)

def errode(data, threshold=1, max_steps=200):
    size = _size(data)
    def find_points_exceeding_threshold() -> list[tuple[int, int]]:
        points = []
        for y in range(size):
            for x in range(size):
                if data[y, x] > threshold:
                    points.append((x, y))
        return points

    def in_bounds(x, y):
        return x >= 0 and x < size and y >= 0 and y < size

    def neighbor_points(x, y):
        # returns the position and the value at that pos as 3-tuple x, y, val
        p = [
            (x - 1, y),
            (x + 1, y),
            (x, y + 1),
            (x, y - 1),
            (x + 1, y + 1),
            (x - 1, y - 1),
            (x + 1, y - 1),
            (x - 1, y + 1)
        ]
        return [
            (pnt[0], pnt[1], data[pnt[1], pnt[0]])
            for pnt in p
            if in_bounds(*pnt)
        ]

    change = True
    step = 0
    while change or step == 0:
        if step >= max_steps:
            break
        step += 1
        change = False
        points = find_points_exceeding_threshold()
        for point in points:
            xp, yp = point
            point_value = data[yp, xp]
            excess = point_value - threshold
            neighbors = neighbor_points(xp, yp)
            smaller_neighbors = [
                n for n in neighbors if n[-1] < excess
            ]
            print(f"point ({xp, yp}) = {point_value} excess: {excess}")
            if not smaller_neighbors:
                continue
            errosion_per_neighbor = excess / len(smaller_neighbors)
            data[yp, xp] = threshold
            for n in smaller_neighbors:
                nx, ny, nv = n
                data[ny, nx] = nv + errosion_per_neighbor
                print(f"Adding {errosion_per_neighbor} to ({nx, ny}) -> {nv + errosion_per_neighbor}")
                change = True

            
