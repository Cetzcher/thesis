import networkx as nx
import tempfile
from pathlib import Path
from .graph_loader import GraphLoader
from util.paths import DATA_PATH


class Loader(GraphLoader):
    path = DATA_PATH / "pgp.gml"

    def load(self):
        return self.load_pgp_network()

    def load_pgp_network(self):
        path = self.path
        with open(path, "r") as infile:
            with open(str(path) + ".tmp", "w+") as outfile:
                lns = []
                reading_nodes = True
                for line in infile.readlines():
                    if "type.1" not in line:
                        lns.append(line)
                        if reading_nodes and "id" in line:
                            node_id = int(line.split("id")[1].strip())
                            lns.append(f"\t\tlabel {node_id}\n")
                        if "edge" in line:
                            reading_nodes = False
                outfile.writelines(lns)
                outfile.flush()
                graph = nx.readwrite.gml.read_gml(str(path) +  ".tmp")
                dg = nx.DiGraph(graph)
                for u, v, data in dg.edges(data=True):
                    data["weight"] = data["value"]
                return dg
        
