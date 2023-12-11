from layout.base import Layout
from util.maths import random_position

class RandomLayout(Layout):

    def layout(self):
        self._positions = {node: random_position(self.size) for node in self.graph.G.nodes}
        return self._positions