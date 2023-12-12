from layout.height_map_layout import HeightMapLayout
from drawing.kernels import rect
from util.maths import random_position
import numpy as np

class DensityLayoutRect(HeightMapLayout):

    def layout(self) -> dict:
        """The goal of this layout is to generate a height map such that
        nodes are placed at points that are closest to their probability of being reached.
        
        the reach prob here is defined by the graph objects Pr function in [0, 1]
        since the map is empty at the start we will never find such a spot and place a node randomly.
        when we place a node we not only add height to the coordinate we place it at, 
        but also to all coordinates around it. 

        for this layout we use the rect() function with no interpolation

        since the map we use is a float32 it will be rather hard to find exact matches,
        instead, we will look for the coordinate at which the map's value is closest to our 
        desired value, this is very slow but sufficent for a proof of concept
        """
        def find_closest_value(val) -> tuple[int, int]:
            # finds the coordinate at which map[x, y] - val is minimal
            best = (self.size // 2, self.size // 2)
            best_val = 10 # any value larger than 1 will do
            indicies = list(range(self.size))
            np.random.shuffle(indicies)
            # use random permutations for the indicies
            for y in indicies:
                for x in indicies:
                    at_coord = self._height_map[y, x]
                    distance_to_val = abs(at_coord - val)
                    if distance_to_val < best_val:
                        best_val = distance_to_val
                        best = x, y
            return best
        
        def place_at_coord(x, y, value):
            # since value is in [0, 1]
            # we want a node with pr = 1 to influnce the
            # entire map 
            assert value <= 1 and value >= 0
            bounds = (self.size * value) // 2
            rect(
                self._height_map,
                (x, y),
                bounds,
                value,
            )

        placements = {}
        for node in self.graph.G.nodes:
            xy = find_closest_value(self.graph.Pr(node))
            place_at_coord(*xy, self.graph.Pr(node))
            placements[node] = xy
        
        return placements
        