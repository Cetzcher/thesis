import networkx as nx
import numpy as np
import random
import math
import copy

R = random.Random(100)
np.random.seed(100)

W_KEY = "weight"
AVG_LEN_KEY = "avg_len"
PROB_KEY = "probability"


def remap_tuple_dict(d: dict):
    return [{'key':k, 'value': v} for k, v in d.items()]

def reverse_mapping(d: list[dict]):
    out = {}
    for item in d:
        out[tuple(item["key"])] = item["value"]

def generate_directed_graph(node_count=100, mean_num_connections=3, connection_std=1):
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

def reweigh_graph(graph, use_self_loops):
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
        
            

class Graph:

    def __init__(self, network_x_graph_obj: nx.DiGraph, autocompute=True, loaded_later=False) -> None:
        self.__raw = network_x_graph_obj
        if not loaded_later:
            reweigh_graph(self.__raw, True)
        if not loaded_later:
            self.__paths = nx.shortest_path(self.__raw, weight=None)
        else:
            self.__paths = {}
        self.__probabilites = {}
        self.__probabilites_along_paths = {}
        self.__probabilites_along_paths_reversed = {}
        self.__path_cache = {}
        self.__seed_nodes = []
        self.__k_seeds = None
        if autocompute and not loaded_later:
            self.__aggregated_graph = self.__aggregate_graph()
            self.__compute_total_prob()


    def Pr(self, nodes) -> float:
        try:
            acc = 0
            for n in nodes:
                acc += self.probabilites[n]
            return acc / len(nodes)
        except TypeError:
            return self.__probabilites[nodes]

    @property
    def seeds(self):
        return self.__seed_nodes

    @property
    def k_seeds(self):
        return self.__k_seeds

    def serialize(self) -> dict:
        return {
            "paths": self.__paths,
            "probabilites": self.__probabilites,
            "probabilites_along_paths": self.__probabilites_along_paths,
            "probabilites_along_paths_reversed": self.__probabilites_along_paths_reversed,
            "path_cache": remap_tuple_dict(self.__path_cache),
            "seed": self.__seed_nodes,
            "k_seeds": self.__k_seeds
        }

    def deserialize(self, data: dict, graphobj, agg) -> None:
        self.__paths = data["paths"]
        self.__probabilites = data["probabilites"]
        self.__probabilites_along_paths = data["probabilites_along_paths"]
        self.__probabilites_along_paths_reversed = data["probabilites_along_paths_reversed"]
        self.__path_cache = reverse_mapping(data["path_cache"])
        self.__seed_nodes = data["seed"]
        self.__k_seeds = data["k_seeds"]
        self.__raw = graphobj
        self.__aggregated_graph = agg

    @property
    def G(self):
        return self.__raw

    @property
    def agg(self) -> nx.DiGraph:
        return self.__aggregated_graph

    @property
    def probabilites(self):
        return self.__probabilites

    @property
    def path_probabilities(self):
        return self.__probabilites_along_paths

    def has_edge(self, u, v):
        return self.__raw.has_edge(u, v)
    
    def has_agg_edge(self, u, v):
        return self.__aggregated_graph.has_edge(u, v)

    def probability_along_path(self, path, graph=None):
        #if self.__aggregated_graph is None:
        #    self.__aggregated_graph = self.__aggregate_graph()
        # this can be optimized by working backwards
        if not graph:
            graph = self.__aggregated_graph
        if len(path) == 1:
            raise ValueError("Path cannot have length 1")

        if (val := self.__path_cache.get((path[0], path[-1]), None)) is not None:
            return val
        
        if len(path) == 2:
            r = graph.edges[path[0], path[1]][W_KEY]
            self.__path_cache[(path[0], path[1])] = r
            return r
        else:
            start, *middle, end = path
            last_leg = graph.edges[middle[-1], end][W_KEY]
            val = self.probability_along_path([start] + middle, graph=graph)
            total = val * last_leg
            self.__path_cache[(start, end)] = total
            return total
        """
        accum = 1
        prev, *path = path
        while path:
            cur, *path = path
            edge = graph.edges[prev, cur]
            accum *= edge[W_KEY]
            prev = cur
        return accum
        """

    def __compute_total_prob(self):
        self.__probabilites = {}
        graph = self.__aggregated_graph
        paths = self.__paths
        
        for start_node, path in paths.items():
            for end_node, between in path.items():
                if start_node == end_node:
                    continue
                val = self.probability_along_path(between)
                
                prob = self.__probabilites_along_paths.get(start_node, dict())
                prob[end_node] = val
                self.__probabilites_along_paths[start_node] = prob

                prob_r = self.__probabilites_along_paths_reversed.get(end_node, dict())
                prob_r[start_node] = val
                self.__probabilites_along_paths_reversed[end_node] = prob_r 
        
        for node, came_from in self.__probabilites_along_paths_reversed.items():
            vals = came_from.values()
            accum = sum(vals)
            total_pahts = len(vals)
            if total_pahts > 0:
                self.__probabilites[node] = accum / total_pahts
            else:
                self.__probabilites[node] = 0

        for node in graph.nodes:
            if node not in self.__probabilites:
                self.__probabilites[node] = 0
            

    def __aggregate_graph(self):
        G = copy.deepcopy(self.__raw.copy())
        # compute graph with added edges that show the weights after t timesteps
        # compute paths from all nodes to all nodes.
        paths = self.__paths
        for start, to in self.__paths.items():
            for goal, nodes_between in to.items():
                if start == goal:
                    continue
                G.add_edge(start, goal, weight=self.probability_along_path(nodes_between, self.__raw))
        
        return G
        for start in paths.keys():
            for end in paths[start].keys():
                path = paths[start][end][1:]
                #path_mod = path[1:]
                #print("START", start, "END", end, "PATH", path, "mod", path_mod)
                #path = path_mod
                if start == end:
                    continue
                first_node, *rest = path
                prev_node = first_node
                accum = G.edges[start, first_node][W_KEY]
                path_length = 1
                for node in rest:
                    accum *= G.edges[prev_node, node][W_KEY]
                    if G.has_edge(start, node):
                        accum = (G.edges[start, node][W_KEY] + accum) / 2
                        path_length = (G.edges[start, node][AVG_LEN_KEY] + path_length) / 2
                    else:
                        G.add_edge(start, node, weight=accum, avg_len=path_length, edge_type="agg")
                    prev_node = node
                    path_length += 1
        return G





