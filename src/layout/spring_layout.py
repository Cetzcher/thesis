from layout.height_map_layout import HeightMapLayout
import networkx as nx
import math
from drawing.kernels import circle

    

class SpringHillLayout(HeightMapLayout):


    def __init__(self, graph, size, **params) -> None:
        super().__init__(graph, size, **params)
        self.use_log = params.get("use_log", False)
        self.use_agg = params.get("use_agg", False)


    def _get_graph(self) -> nx.DiGraph:
        return self.graph.agg if self.use_agg else self.graph.G

    def __preprocess(self):
        g = self._get_graph()
        if self.use_log:
            return log_weights(g)
        return g

    def layout(self):
        g = self.__preprocess()
        out = dict()
        pos = nx.spring_layout(g)
        def scale_pos(pos):
            x, y = pos
            x, y = (x + 1) / 2, (y + 1) / 2
            ms = self.size
            x = math.floor(x * ms)
            y = math.floor(y * ms)
            return x, y

        for node, pos in pos.items():
            pr = self.graph.Pr(node)
            radius = (self.size * pr) // 1
            hm_pos = scale_pos(pos)
            circle(self._height_map, hm_pos, radius, pr * 100)           
            out[node] = hm_pos

        return out
    

def log_weights(graph: nx.DiGraph):
    cpy = graph.copy()
    for u, v, data in cpy.edges(data=True):
        data["weight"] = math.log(data["weight"])
    return cpy
