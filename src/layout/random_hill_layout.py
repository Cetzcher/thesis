from layout.height_map_layout import HeightMapLayout
from util.maths import random_position
from drawing.kernels import circle

class RandomHillLayout(HeightMapLayout):

    def layout(self):
        pos = {node: random_position(self.size) for node in self.graph.G.nodes}
        assert pos.items()
        for n, npos in pos.items():
            radius = (self.graph.Pr(n) * self.size) // 1
            value = self.graph.Pr(n) * 1000
            circle(
                self._height_map,
                npos,
                radius,
                value,
                lambda x: x ** (1)
            )
        return pos