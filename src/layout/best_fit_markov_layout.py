from layout.base import Layout
from util.clustering import MarkovClustering


class BestFitMarkovLayout(Layout):

    def layout(self) -> dict:
        clustering = MarkovClustering(self.graph, {})
        clusters = clustering.compute_clustering()
        cnt = len(clusters)
        x_step = self.size / cnt
        y_mid = self.size // 2
        pos = {}
        for i, cluster in enumerate(clusters):
            for node in cluster:
                pos[node] = (int(i * x_step), y_mid)
        self._positions = pos
        return pos