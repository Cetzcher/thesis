from graph.graph import Graph
from layout.height_map_layout import HeightMapLayout
from util.maths import random_position, clamp, vec_len, vec_norm
import numpy as np
import vec
from typing import Any

class ForceDirectedTraditionalLayout(HeightMapLayout):
    """Force directed layout using just the edge weights and using only connected nodes"""

    def __init__(self, graph: Graph, size, **params) -> None:
        super().__init__(graph, size, **params)
        self.force = None
        self.GRAVITY = 20
        self.MASS_MULT = 10
        self.REPULSION_FORCE = 9
            
    def radius_from_prob(self, prob):
        return (self.size * prob) * 8

    def compute_influence(self, x, y, nodes):
        if not self.in_bounds(x, y):
            raise Exception("Out of bounds")
        def map_node_pos(node):
            return self.positions.get(node, None), node
        
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

    @property
    def positions(self) -> dict[Any, vec.Vector2]:
        return super().positions


    def compute_gravity(self, node):
        node_pos = vec.Vector2(self.positions[node])
        center = vec.Vector2(self.size / 2, self.size / 2)
        to_center = center - node_pos
        direction = vec.Vector2(*vec_norm(to_center))
        return direction * self.GRAVITY #* (vec_len(to_center) / 16)
    
    def compute_repulsion(self, node, other):
        # repulsion is large for large diferences in 'mass' 
        # ie the respective probs.
        node_mass, other_mass = self.graph.Pr(node) * self.MASS_MULT, self.graph.Pr(other) * self.MASS_MULT
        node_pos, other_pos = self.positions[node], self.positions[other]
        mass_diff = abs(node_mass - other_mass) + 0.0001  # add a tiny amount so that even equal mass repulse

        direction = vec.Vector2(*vec_norm(other_pos - node_pos))
        force = direction * mass_diff * self.REPULSION_FORCE
        # the orignial force was constructed from node_pos to other_pos
        # sicne we want to push them apart we return it inverted
        return force * -1, force 


    def compute_attraction(self, node, other):
        # if the nodes are directly connected then we can just use their node weight
        # as if it was an undirected graph, if both edges exist then we take the mean.
        node_is_connected_to_other = self.graph.G.has_edge(node, other)
        other_is_connected_to_node = self.graph.G.has_edge(other, node)
        weight = 0
        if node_is_connected_to_other:
            weight = self.graph.G.edges[node, other]["weight"]
        if other_is_connected_to_node:
            conn_w = self.graph.G.edges[other, node]["weight"]
            if weight == 0:
                weight = (weight + conn_w) / 2
            else:
                weight = conn_w

        to_node = self.positions[node] - self.positions[other]
        # when weight is large that means the nodes should be close together
        # because they are simillar.
        # if it is small they should be further apart
        ideal_distance = clamp(8, self.size, 1/weight,)
        to_node_distance = vec_len(to_node)
        factor = ideal_distance / (to_node_distance + 0.00001)
        direction = vec.Vector2(*vec_norm(to_node))
        return -direction * factor, direction * factor

    def apply_forces(self):
        for node in self.graph.G.nodes:
            pos = self.positions[node]
            mass = 1 + self.graph.Pr(node) * self.MASS_MULT
            force = self.force[node]
            velocity = force / mass
            new_pos = pos + velocity
            xpos = int(new_pos[0])
            ypos = int(new_pos[1])
            xpos = clamp(0, self.size, xpos)
            ypos = clamp(0, self.size, ypos)
            self.positions[node] = vec.Vector2(xpos, ypos)

    def layout(self) -> dict:
        if not self.positions:
            self._positions = {
                node: vec.Vector2(random_position(self.size)) 
                for node in self.graph.G.nodes
            }
            self.force = {
                node: vec.Vector2(0, 0)
                for node in self.graph.G.nodes
            }

        size = self.size
        #  reset map each frame
        self._height_map = np.zeros((size, size), np.float64)

        for node in self.graph.G.nodes:
            gravity = self.compute_gravity(node)
            print(gravity)
            self.force[node] = gravity
            for other in self.graph.G.nodes:
                if other == node:
                    continue
                node_repulsion, other_repulsion = self.compute_repulsion(node, other)
                node_attraction, other_attraction = self.compute_attraction(node, other)
                self.force[node] += node_repulsion + node_attraction
                self.force[other] += other_repulsion + other_attraction
        
        self.apply_forces()
        return self.positions
    
    def render_to_map(self):
        for x in range(self.size):
            for y in range(self.size):
                self._height_map[x, y] = self.compute_influence(x, y, self.graph.G.nodes)

    def layout_iter(self, steps):
        for _ in range(steps):
            res = self.layout()
        return res