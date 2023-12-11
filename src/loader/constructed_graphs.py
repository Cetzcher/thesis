import networkx as nx
from util.maths import RANDOM as R

def one_center(orbit_count, prefix):
    g = nx.DiGraph()
    center_node_name = f"{prefix}-center"
    g.add_node(center_node_name)
    for i in range(orbit_count):
        g.add_edge(
            center_node_name,
            f"{prefix}-{i}",
            weight=R.random()
        )
    return g

def many_centers(orbit_count, regions):
    g = nx.DiGraph()
    for i in range(regions):
        sub_graph = one_center(orbit_count, str(i))
        g.add_edges_from(sub_graph.edges(data=True))
    return g

def many_centers_connected(orbit_count, regions):
    g = nx.DiGraph()
    for i in range(regions):
        sub_graph = one_center(orbit_count, str(i))
        g.add_edges_from(sub_graph.edges(data=True))
    
    for start in range(regions):
        for end in range(regions):
            if start == end:
                continue
            g.add_edge(f"{start}-center", f"{end}-center", weight=R.random())
    return g