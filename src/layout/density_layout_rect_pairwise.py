from layout.height_map_layout import HeightMapLayout
from drawing.kernels import rect
from util.maths import random_position
import numpy as np

class DensityLayoutRectPairwise(HeightMapLayout):

    def layout(self) -> dict:
        """The goal of this layout is to generate a height map such that
        they are arranged at cols / rows that determine the liklehood of going from A -> B
        """

        placements = {}
        col_size = self.size // len(self.graph.G.nodes)
        print("seize: ", self.size, "node count: ", len(self.graph.G.nodes))
        assert col_size > 0
        for col_idx, start_node in enumerate(self.graph.G.nodes):
            for row_idx, end_node in enumerate(self.graph.G.nodes):
                if start_node == end_node:
                    value = 0
                    placements[start_node] = col_idx * col_size
                else:
                    value = self.graph.path_probabilities.get(start_node, {}).get(end_node, 0)
                    if value != 0:
                        print(start_node, "->", end_node, "=", value)
                start_x = col_idx * col_size
                end_x = (col_idx + 1) * col_size
                start_y = row_idx * col_size
                end_y = (row_idx + 1) * col_size
                center_x = int(start_x + end_x) // 2
                center_y = int(start_y + end_y) // 2
                rect(self._height_map, (center_x, center_y), col_size, value)
        
        return placements
        