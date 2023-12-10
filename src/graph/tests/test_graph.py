from ..graph import Graph
import networkx as nx
from ..util import print_edges_with_weights

def test_graph_can_be_inited():
    data = nx.DiGraph()
    data.add_edge("A", "B", weight=0.5)
    data.add_edge("B", "C", weight=0.7)
    data.add_edge("C", "A", weight=0.3)
    g = Graph(
        data
    )

    print_edges_with_weights(g.G)
    print_edges_with_weights(g.agg)