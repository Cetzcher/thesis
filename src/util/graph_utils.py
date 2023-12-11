
def get_in_nodes(G, node):
    nodes = set()
    for u, v in G.in_edges(node):
        assert v == node
        nodes.add(u)
    return nodes


def neighbor_nodes(G, node):
    inn = list(G.in_edges(node))
    outn = list(G.out_edges(node))
    # inn is x -> node
    # outn is node -> x
    return list(map(lambda xy: xy[0], inn)) + list(map(lambda xy: xy[1], outn))