from graph.graph import Graph	

class Layout:
    """A layout combines a graph and outputs the nodes positions"""

    def __init__(self, graph: Graph, size, **params) -> None:
        self.__graph = graph
        self.params = params
        self.size = size
        self._positions = []

    @property
    def positions(self):
        return self._positions
    
    @property
    def graph(self):
        return self.__graph

    def layout(self) -> dict:
        pass
