import math
from functools import partial    
import networkx as nx
    # SELECT HEURISTICS:
    # return list of len num nodes by some heurisitc 



def select_nodes_by_prob(layout, num_nodes=0):
    items = sorted(layout.graph.probabilites.items(), key=lambda x: x[1], reverse=True)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_nodes_by_prob_low(layout, num_nodes=0):
    items = sorted(layout.graph.probabilites.items(), key=lambda x: x[1], reverse=False)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_highest_in_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.in_degree(), key=lambda x: x[1], reverse=True)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_lowest_in_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.in_degree(), key=lambda x: x[1], reverse=False)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_highest_out_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.out_degree(), key=lambda x: x[1], reverse=True)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_lowest_out_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.out_degree(), key=lambda x: x[1], reverse=False)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_lowest_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.degree(), key=lambda x: x[1], reverse=False)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_highest_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.degree(), key=lambda x: x[1], reverse=True)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_lowest_weight_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.degree(weight="weight"), key=lambda x: x[1], reverse=False)
    return list(map(lambda n: n[0], items[0:num_nodes]))


def select_by_highest_weight_degree(layout, num_nodes=0):
    items = sorted(layout.graph.G.degree(weight="weight"), key=lambda x: x[1], reverse=True)
    return list(map(lambda n: n[0], items[0:num_nodes]))




    # place nodes
    # take the node names / idx and place them 
    # to soem pos by returning a dict of the form node -> (x, y)


def place_nodes_random(layout, nodes):
    positions = {}
    for node in nodes:
        pos = layout.height_map.rand_pos()
        positions[node] = pos
    return positions
    
def place_nodes_spring(layout, nodes):
    subg = layout.graph.G.subgraph(nodes)
    print("Subgraph: ", subg)
    size = layout.height_map.size
    hs = size // 2
    pos = nx.spring_layout(subg)
    pos = {n: (round(((x[0] + 1) / 2) * size), round(((x[1] + 1) / 2) * size)) for n, x in pos.items()}
    print(pos)
    return pos
    
def place_nodes_circ_factory(dist=0):
    # place nodes at equi-angles around point away from center with radius dist
    def inner(layout, nodes):
        return place_nodes_circ(layout, nodes, dist=dist)
    return inner

def place_nodes_circ(layout, nodes, dist=15):
    # first sort nodes s.t. if two nodes share an edge they are 
    # next to each other
    sorted_by_shared_edges = []
    for cur in nodes:
        if cur not in sorted_by_shared_edges:
            sorted_by_shared_edges.append(cur)
            # add edges of cur if they are in nodes
            shared = list(layout.graph.G.in_edges(cur)) + list(layout.graph.G.out_edges(cur))
            shared = filter(lambda n: n in nodes and n not in sorted_by_shared_edges, shared)
            append = True
            for n in shared:
                if append:
                    sorted_by_shared_edges.append(n)
                else:
                    sorted_by_shared_edges = sorted_by_shared_edges[:-2] + [n] + sorted_by_shared_edges[-1]
                append = not append

    dof = 2 * math.pi / len(nodes)
    pos = {}
    center = layout.height_map.size // 2
    for i, node in enumerate(sorted_by_shared_edges):
        # place node at dist=dist and angle i * dof
        angle = i * dof
        x = center + round(dist * math.cos(angle))
        y = center + round(dist * math.sin(angle))
        pos[node] = (x, y)
    print(pos)
    return pos
