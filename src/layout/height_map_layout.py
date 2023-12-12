from graph.graph import Graph
from layout.base import Layout
import numpy as np
from util.maths import clamp

class HeightMapLayout(Layout):
    
    def __init__(self, graph: Graph, size, **params) -> None:
        super().__init__(graph, size, **params)
        self._height_map = np.zeros((size, size), np.float64)
    
    def in_bounds(self, x, y):
        return x >= 0 and x <= self.size and y >= 0 and y <= self.size
