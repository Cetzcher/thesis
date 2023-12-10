import networkx as nx
from .graph_loader import GraphLoader

class RampLoader(GraphLoader):
    
    def load(self):
        return self.load_ramp_graph()

    def load_ramp_graph(self):
        filepath = self.path
        dg = nx.DiGraph()
        
        def parse_node(seq: str):
            seq = seq.strip()
            if "(" not in seq:
                raise Exception("No ( found")
            
            name, time = seq[:-1].split("(")
            return int(name), int(time)

        def parse_tree(lines: list[str]):
            for line in lines:
                infector, infectees = line.split("-")[-2:]
                infectees = infectees.replace("[", "").replace("]", "")
                infector = infector.replace("-", "")
                infector_name, infector_time = parse_node(infector)
                dg.add_node(infector_name, infection_time=infector_time)
                for infected in infectees.split(","):
                    infected_name, infected_time = parse_node(infected)
                    delta_time = infected_time - infector_time
                    assert delta_time > 0
                    dg.add_node(infected_name, infection_time=infected_time)
                    dg.add_edge(infector_name, infected_name, weight=1/delta_time)
        
        buffer = []
        with open(filepath, "r") as infile:
            while (ln := infile.readline()):
                ln = ln.strip().replace(">", "")  # drop the > char
                if ln == "":
                    parse_tree(buffer)
                    buffer = []
                else:
                    buffer.append(ln)
            
            if buffer: # EOF
                parse_tree(buffer)
        
        return dg

