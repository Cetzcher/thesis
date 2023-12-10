import pytest
from ..graph import Graph
import networkx as nx
from ..util import print_edges_with_weights
from loader.random import generate_directed_graph
import time

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


@pytest.mark.skip
def test_graph_aggergation_performance():
    for i in range(10):
        node_count = (2 ** ( i + 1)) + 10 
        data = generate_directed_graph(node_count=node_count)
        start = time.time()
        graph = Graph(data)
        end = time.time() - start
        start_without_agg_compute = time.time()
        graph2 = Graph(data, autocompute=False)
        end_without_agg_compute = time.time() - start_without_agg_compute

        print(f"using {node_count}: {data}")
        print(f"with aggregation: {end}")
        print(f"without aggregation: {end_without_agg_compute}") 

