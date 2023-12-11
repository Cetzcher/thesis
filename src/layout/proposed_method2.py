from ..layout import Layout
from ..util import R, noise, remap, pick_random_truthy, clamp, vec_len


class ProposedMethod2(Layout):

    def __init__(self, name="ProposedMethod2") -> None:
        super().__init__(name=name)

    def layout(self):
        n = len(self.graph.G.nodes)
        size = self.height_map.size // n
        x = 0
        for node in self.graph.G.nodes:
            y = 0
            for other in self.graph.G.nodes:
                reach_prob = self.graph.path_probabilities.get(node, {}).get(other, 0)
                # draw a box of reach prob from (x * size, y * size) to ((x+1) * size, (y+1) * size)
                for xc in range(x * size, (x+1) * size):
                    for yc in range(y * size, (y+1) * size):
                        self.height_map.set_to(xc, yc, reach_prob)
                y += 1
            xcenter, ycenter = (((x * size) + (x+1) * size) / 2,  ((n/2 * size) + (n/2+1) * size) / 2)
            self._pos[node] = (int(xcenter), int(ycenter))
            x += 1


        return self._pos
    