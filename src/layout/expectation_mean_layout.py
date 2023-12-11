from layout.height_map_layout import HeightMapLayout
from util.maths import random_position, clamp, vec_len, vec_add, vec_neg, vec_norm, vec_sub, int_vec, midpoint

class ExpecationMeanLayout(HeightMapLayout):

    def mean(self, nodes): 
        """Computes the mean of the bunch of nodes"""
        return sum(map(lambda n: self.__graph.probabilites[n], nodes)) / len(nodes)

    def compute_influence(self, x, y, nodes):
        if not self.in_bounds(x, y):
            raise Exception("Out of bounds")
        def map_node_pos(node):
            return self._pos.get(node, None), node
        
        # map node_pos, node
        node_pos = filter(lambda v: v[0] != None, map(map_node_pos, nodes))
        
        def map_node_dist(item):
            pos, node = item
            return vec_len((x - pos[0], y - pos[1])), node

        # map distance, node
        nodes_distance = map(map_node_dist, node_pos)

        # remove all nodes that cannot influence the point
        nodes_distance = filter(
                lambda item: 
                    item[0] < self.radius_from_prob(self.graph.probabilites[item[1]]) 
                    and item[0] > 0,
                nodes_distance)

        # influence is now the weighted sum of inverse distace * prob
        nodes_distance = list(nodes_distance)
        if len(nodes_distance) == 0:
            #print("Influence for ", (x, y), "=", 0)
            return 0
        influence = sum(map(lambda item: 1/item[0] * self.graph.probabilites[item[1]], nodes_distance)) / len(nodes_distance)
        #print("Influence for ", (x, y), "=", influence)

        return influence
    
    def layout(self) -> dict:
        
        # put all nodes at random positions at first.
        for node in self.graph.G.nodes:
            self._pos[node] = random_position()
        
        MAX_ITER = 1000
        for i in range(MAX_ITER):
            for node in self.graph.G.nodes:
                print("Tweak ", node)
                selfpos = self._pos[node]
                self_value = self.graph.probabilites[node]
                direction = 0, 0
                magnitude = 0
                for neighbor in self.graph.G.neighbors(node):
                    print("Visit neighbor", neighbor)
                    neighborpos = self._pos[neighbor]
                    neighbor_value = self.graph.probabilites[neighbor]
                    direction_to_neighbor = vec_norm( vec_sub(neighborpos, selfpos))
                    center = int_vec(midpoint([selfpos, neighborpos]))

                    actual_value = self.compute_influence(center[0], center[1], self.graph.G.nodes)
                    expected_value = (self_value + neighbor_value) / 2
                    difference = actual_value - expected_value
                    
                    diff_to_self = abs(self_value - expected_value)
                    diff_to_neighbor = abs(neighbor_value - expected_value)
                    mag = abs(difference) * 10

                    if diff_to_self > diff_to_neighbor:
                        # move towards neighbor
                        direction = vec_add(direction, direction_to_neighbor)
                        magnitude += mag
                    elif diff_to_self < diff_to_neighbor:
                        # move away from neighbor
                        direction = vec_add(direction, vec_neg(direction_to_neighbor))
                        magnitude += mag
                    else:
                        # do not modify anything
                        continue
                print("Moving node ", node, "in the direction of ", direction, "with mag", magnitude)
                direction = vec_norm(direction)
                newpos = vec_add(selfpos, (direction[0] * magnitude, direction[1] * magnitude))
                if not self.in_bounds(*newpos):
                    newpos = (
                        clamp(0, self.size - 1, newpos[0]),
                        clamp(0, self.size - 1, newpos[1])
                    )
                self._pos[node] = int_vec(newpos)
        
        # we are done now set the values according to influence
        for x in range(self.size-1):
            for y in range(self.size-1):
                inf = self.compute_influence(x, y, self.graph.G.nodes)
                self._height_map[y, x] = inf
        
        return self._pos
