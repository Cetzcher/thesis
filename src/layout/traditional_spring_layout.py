from layout.base import Layout
import networkx as nx
import math

class TraditionalSpringLayout(Layout):

    def layout(self) -> dict:
        def scale_pos(pos):
            x, y = pos
            x, y = (x + 1) / 2, (y + 1) / 2
            ms = self.size
            x = math.floor(x * ms)
            y = math.floor(y * ms)
            return x, y
        return {node: scale_pos(pos) for node, pos in nx.spring_layout(self.graph.G).items()}