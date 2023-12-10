import networkx as nx

def remap_tuple_dict(d: dict):
    """Creates a list of dictionaries of the form {'key': str, 'value': any}"""
    return [{'key':k, 'value': v} for k, v in d.items()]

def reverse_mapping(d: list[dict]):
    out = {}
    for item in d:
        out[tuple(item["key"])] = item["value"]

def reweigh_graph(graph, use_self_loops):
    """Adjusts the weights on a graph.
    
    For each node in the graph we perfom the following operation:
    Sum all out edges of the node, if the sum is less than one and "use_self_loops" is True
    we add an edgen from the node to itself with weight = 1 - Sum.
    Otherwise if use_self_loops is False or the sum is > 1 we normalize the out edges.
    """
    for node in graph.nodes:
        out_edges = graph.out_edges(node, data=True)
        weight_sum = 0
        for u, v, data in out_edges:
            weight_sum += data["weight"]
        if use_self_loops and weight_sum < 1:
            graph.add_edge(node, node, weight=1 - weight_sum)
        elif weight_sum > 1 or not use_self_loops: # adjust all out edge weight if sum of weights is
            for u, v, data in out_edges:
                    data["weight"] = data["weight"] / weight_sum
        

def print_edges_with_weights(G: nx.DiGraph):
    print(G)
    digits = 6
    for u, v, data in G.edges(data=True):
        print(f"{' ' * (len(u) + 2)}{data['weight']:.06f}")
        print(f"{u}  {'-'  * (digits + 1)}>  {v}")