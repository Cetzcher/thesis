import networkx as nx
import numpy as np


def generate_directed_graph(node_count=100, mean_num_connections=3, connection_std=1):
    """Generate a directed graph with the given number of nodes
    
    Args:
        node_count: number of nodes to generate.
        mean_num_connections: mean of number of connections to generate for each node
            theese values are picked from a normal distribution.
        conntion_std: standard deviataion of number of connections.

    Note:
        each generated node will have a set number of connections sammpled from a normal dist. 
        the weight assigned to each generated edge is sampled uniformly.
    
        
    """
    G = nx.DiGraph()
    for i in range(node_count):
        G.add_node(i, color=f"#000000")
        connections = np.random.normal(loc=mean_num_connections, scale=connection_std)
        connections = math.ceil(connections)
        for _ in range(connections):
            # choose which node we connect to
            target = i
            weight = R.random()
            while target == i:  # reroll loops
                target = R.randint(0, node_count)
            if target > i:
                G.add_node(target, color=f"#000000")
            G.add_edge(i, target, weight=weight, color="black", edge_type="normal")
    return G