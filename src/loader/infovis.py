import networkx as nx

from . graph_loader import GraphLoader
from util.paths import DATA_PATH

class Loader(GraphLoader):
    path = DATA_PATH / "infovis_large.gml"

    def load(self):
        return self.load_infovis_graph()    
        
    def load_infovis_graph(self):
        current_paper = None
        next_line_is_header = False
        reading_citations = False
        graph = nx.DiGraph()

        with open(self.path) as infile:
            while (ln := infile.readline()):
                ln = ln.strip()
                    
                if ln.startswith("article"):
                    # start of data
                    next_line_is_header = True
                    continue

                if next_line_is_header:
                    # add the node to graph and map data
                    next_line_is_header = False
                    current_paper = ln
                    graph.add_node(current_paper)
                    continue

                
                if ln == "citations:":
                    reading_citations = True
                    continue

                
                if ln == "":
                    # end of data
                    reading_citations = False
                    current_paper = None
                    next_line_is_header = False
                    continue

                
                if reading_citations and ln.startswith("infovis"):
                    print("current line: ", ln, "paper: ", current_paper)
                    graph.add_edge(current_paper, ln, weight=1)
                    continue


        return graph