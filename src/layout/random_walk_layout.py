from layout.height_map_layout import HeightMapLayout
from collections import deque
from util.graph_utils import neighbor_nodes
from util.maths import random_position

class RandomWalkLayout(HeightMapLayout):

    def random_walk(self, node, start_point):
        MOVE_COST = 0.01
        KERNEL_WIDTH = 5  # kernel size
        LOOKOUT_SIZE = 10
        energy = self.graph.probabilites[node] * 100
        current_pos = start_point

        def choose_next_pos():
            x, y = current_pos
            xl, xh = x - LOOKOUT_SIZE, x + LOOKOUT_SIZE
            yl, yh = y - LOOKOUT_SIZE, y + LOOKOUT_SIZE
            closest_point = 0, 0
            closest_dist = 1000000
            for xi in range(xl, xh):
                for yi in range(yl, yh):
                    if not self.in_bounds(xi, yi):
                        continue
                    val = self._height_map[yi, xi]
                    dist = abs(energy - val)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_point = xi, yi
            return closest_point

        def apply_kernel():
            target_value = energy
            for x in range(-KERNEL_WIDTH, KERNEL_WIDTH):
                for y in range(-KERNEL_WIDTH, KERNEL_WIDTH):
                    xc, yc = x + current_pos[0], y + current_pos[1]
                    # pull the value at xc, yc towards energy.
                    # first get the mean value in that range
                    if self.in_bounds(xc, yc):
                        self._height_map[yc, xc] = target_value


        while energy > MOVE_COST:
            apply_kernel()
            current_pos = choose_next_pos()
            energy -= MOVE_COST            
        return current_pos

    def layout(self) -> dict:
        # sort all nodes by their probabilty from highest to lowest.
        # put this node at a region that best fits their probability
        # A) what to do if no such region exists ? 

        positions = {node: None for node in self.graph.G.nodes}
        # left side is high prob, right side is low prob.
        node_stack = deque(map(
            lambda item: item[0], 
            sorted(
                list(self.graph.probabilites.items()),
                key=lambda kv: kv[1],
                reverse=True)
        ))

        layouted_nodes = set()

        while node_stack:
            node = node_stack.popleft()
            if node in layouted_nodes:
                continue
            layouted_nodes.add(node)
            final_pos = self.random_walk(node, random_position(self.size))
            positions[node] = final_pos
            for neighbor in neighbor_nodes(self.graph.G, node):
                if neighbor not in layouted_nodes:
                    neighbor_pos = self.random_walk(neighbor, final_pos)
                    layouted_nodes.add(neighbor)
                    positions[neighbor] = neighbor_pos


        return positions