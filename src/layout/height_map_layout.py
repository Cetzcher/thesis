from graph.graph import Graph
from layout.base import Layout
import numpy as np
from util.maths import clamp

class HeightMapLayout(Layout):
    
    def __init__(self, graph: Graph, size, **params) -> None:
        super().__init__(graph, size, **params)
        self._height_map = np.zeros((size, size), np.float64)
    
    def in_bounds(self, x, y):
        return x == clamp(x, 0, self.size) and y == clamp(x, 0, self.size)
