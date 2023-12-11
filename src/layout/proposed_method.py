from ..layout import Layout
from ..util import R, noise, remap, pick_random_truthy, clamp, vec_len


class ProposedMethod(Layout):

    def __init__(self, inital_nodes=2, name="", selection_heurisitc=None, place_heurisitc=None) -> None:
        super().__init__(name=name)
        self.__initial_nodes = inital_nodes
        self.__select = selection_heurisitc
        self.__place = place_heurisitc



    def layout_initial_nodes(self, select_heuristic=None, place_heuristic=None):
        # use select heuristic to select some nodes
        # use place heuristic to place these
        # return the positions for these nodes and their id in the form of (pos, id)
        if not select_heuristic:
            select_heuristic = self.__select
        if not place_heuristic:
            place_heuristic = self.__place
        
        cnt = self.__initial_nodes
        init_nodes = select_heuristic(self, cnt)
        placements = place_heuristic(self, init_nodes)

        for node, pos in placements.items():
            self._hill(node, pos)
        
        return self._pos.copy(), init_nodes

    def layout(self, select_heuristic=None, place_heuristic=None):
        initial_nodes = self.layout_initial_nodes(select_heuristic=select_heuristic, place_heuristic=place_heuristic)[1]
        layouted = set(initial_nodes)
        unlayouted = set(self.graph.G.nodes).difference(layouted)
        
        # 1) expand the frontier i.e. add all nodes that 
        #   end in one of the already layouted nodes to a list
        #   sort this list by out degree of the node
        # 2) pick a node from the frontier (should include from where we got to this point)
        #    look at all nodes that we can reach from here
        # 2.1) if all nodes are layouted in this list look for a spot to put this node
        #     i.e. overlap the circles of the alrady layoute nodes and pick a position.
        # 2.2) if some nodes have not been layouted wait until they are
        # 2.3) if the nodes remain in this collection for too long i.e. no progress 
        #    was made ignore all nodes that still await placement.

        layouted = set(initial_nodes)
        frontier = set() # in the form of (node, target)

        def unlayouted_nodes():
            return set(self.graph.G.nodes).difference(layouted)

        def edges(node):
            # collect in and out edges in the from of node to other_node
            # as if the edges were undirected
            in_edges = self.graph.G.in_edges(node)
            out_edges = self.graph.G.out_edges(node)
            _edges = []
            for u, v in in_edges:
                assert v == node
                _edges.append((node, u))
            for u, v in out_edges:
                assert u == node
                _edges.append((node, v))
            return _edges

        def expand_frontier():
            for node in layouted:
                for v, u in edges(node):
                    # edge is u -> v i.e. v is in layouted
                    if u not in layouted:
                        frontier.add((u, v))
        
        def place_random(node, target):
            self._hill(node, self.height_map.rand_pos())

        def place_naive(node, target):
            # look for "best" spot around target and place node there.
            x, y = self._pos[target]
            tprob = self.graph.probabilites[target]
            tradius = self.radius_from_prob(tprob)
            nprob = self.graph.probabilites[node]
            nradius = self.radius_from_prob(nprob)
            # there are two options to look for a spot
            # either use the target prob and radius or the soruce prob and radius
            spots = self.height_map.find_spots_circ(x, y, tradius, nprob, eps=0.1)
            found, spot = pick_random_truthy(spots)
            if not found: 
                # search the entire map in this case
                spots = self.height_map.find_spots(nprob, eps=0.3)
                found, spot = pick_random_truthy(spots)
                if not found:
                    print("Cannot place node: ", node)
                    print("node has prob of", nprob, "tprob: ", tprob)
                    print("with radius nrad:", nradius, "trad:", tradius)
                    #raise Exception("Cannot place this")
            if found:
                self._hill(node, spot)
                #self.__positions[node] = spot
            else:
                self._hill(node, (0, 0))

        expand_frontier() 
    
        while (unlayouted := unlayouted_nodes()):
            if not frontier:
                break
            try:
                node, target = frontier.pop()
            except KeyError:
                continue
            
            if node in layouted:
                continue
            
            # naive approach first for 
            # place the node s.t. 
            place_naive(node, target)
            layouted.add(node)
            
            if not frontier:
                expand_frontier()


        return self._pos
        # after drawing reset the height map and draw nodes again in order of ascending prob.
        self.__map.reset()
        def mapfn(node):
            return self.__graph.probabilites[node], self.__positions[node], node
        for nprob, npos, nnode in sorted(map(mapfn, self.__graph.G.nodes), key=lambda x: x[0], reverse=True):
            self.__hill(nnode, npos, add_pos=False)

        return self.__positions.copy(), initial_nodes
    