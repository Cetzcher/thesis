from graph.graph import Graph
from .maths import RANDOM as R
import networkx as nx
import markov_clustering as mc

class Clustering:

    def __init__(self, graph: Graph, positions: dict) -> None:
        self._graph = graph
        self._pos = positions

    def compute_clustering(self) -> list[list]:
        # compute clusters for the given graph
        pass


class RandomClustering(Clustering):

    def compute_clustering(self) -> list[list]:
        nodes = set(self._graph.G.nodes)
        clusters = []
        while nodes:
            take_amnt = R.randint(1, len(nodes))
            cluster = []
            for _ in range(take_amnt):
                cluster.append(nodes.pop())
            clusters.append(cluster)
        return clusters
    

class MarkovClustering(Clustering):

    def compute_clustering(self) -> list[list]:
        A = nx.convert_matrix.to_numpy_array(self._graph.G)
        res = mc.run_mcl(A)
        clusters = mc.get_clusters(res)
        nodes = list(self._graph.G.nodes)
        
        # when the input graph has discontinuties in node ids the output will be malformed, so we need to remap the clusters.
        clusters_res = []
        global_node_id = 0
        for cluster in clusters:
            cur_cluster = []
            for _ in cluster:
                cur_cluster.append(nodes[global_node_id])
                global_node_id += 1
            clusters_res.append(cur_cluster)
        
        return clusters_res
    

class KMeansClustering(Clustering):

    def compute_clustering(self) -> list[list]:
        return super().compute_clustering()