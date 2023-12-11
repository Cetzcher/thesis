from src.graph import Graph
from src.height_map import HeightMap
from ..layout import Layout
from ..util import R, remap, clamp
from ..graph_utils import neighbor_nodes
import vectormath as vec
import numpy as np

def midpoint(vecs: list[vec.Vector2]):
    x, y = sum(vecs) / len(vecs)
    return vec.Vector2(x, y)

def normalize(vec):
    if vec.length == 0:
        return vec
    return vec.normalize()

class ExpectationMeanLayout2(Layout):
    
    def __init__(self, name=None, iter_steps=10) -> None:
        if not name:
            name = f"ExpectationMeanLayout2 k={iter_steps}"
        super().__init__(name)
        self.__node_positions: dict[str, vec.Vector2] = {}
        self.iter_steps = iter_steps
        self.__current_step = 0
        self.forces = {}
        self.__precomputed_pairs = None

    def prepare(self, graph: Graph, hmap: HeightMap):
        ret = super().prepare(graph, hmap)
        # all positions are stored within [-1, 1]
        def rand_pos_vec():
            return vec.Vector2(R.random() * 2 - 1, R.random() * 2 -1)
        self.__node_positions = {k: rand_pos_vec() for k in self.graph.G.nodes}
        ypnts, xpnts = np.arange(self.height_map.size), np.arange(self.height_map.size)
        x2d, y2d = np.meshgrid(ypnts, xpnts)
        cols = np.column_stack((y2d.ravel(), x2d.ravel()))
        self.__precomputed_pairs = cols
        return ret
    
    def get_pos(self, node):
        return self.__node_positions[node]

    def __draw_to_heightmap(self):
        scale_factor = self.height_map.size - 1
        x_postions = list(map(lambda vec:  vec.x, self.__node_positions.values()))
        y_postions = list(map(lambda vec:  vec.y, self.__node_positions.values()))
        min_x = min(x_postions)
        max_x = max(x_postions)
        min_y = min(y_postions)
        max_y = max(y_postions)
        print("Min: ", min_x, min_y, "max", max_x, max_y)
        def scale_pos(node_pos: vec.Vector2):
            assert min_x <= node_pos.x
            assert max_x >= node_pos.x
            assert min_y <= node_pos.y
            assert max_y >= node_pos.y
            node_pos.x = (node_pos.x - min_x) / (max_x - min_x)
            node_pos.y = (node_pos.y - min_y) / (max_y - min_y)

            return vec.Vector2(node_pos.x * scale_factor, node_pos.y * scale_factor)
        


        # do the actual drawing here and then return new node positions.
        for k, v in self.__node_positions.items():
            x, y = scale_pos(v)
            self._pos[k] = (int(x), int(y))
            if not self.height_map.in_bounds(*self._pos[k]):
                raise Exception(f"node has coords: {self._pos[k]} shopuld be in [0, {scale_factor}]")
        
        vals = [self.compute_influence_single(node) for node in self.graph.G.nodes]
        cur = vals[0]
        for i in vals[1:]:
            cur += i
        cur /= len(self.graph.G.nodes)
        print("CUR MIN: ", np.min(cur), "MAX", np.max(cur))
        assert np.min(cur) >= 0
        assert np.max(cur) <= 1
        self.height_map.update(cur)

        return self._pos
    
    def compute_influence(self, pos: vec.Vector2, nodes):
        accum = 0
        for node in nodes:
            cur_pos = self.get_pos(node)
            dist = (cur_pos - pos).length
            prop = self.graph.Pr(node) / (dist + 1)
            accum += prop
        return accum / len(nodes)


    def on_draw(self, drawutils, mapstate):
        def to_int(xy):
            return int(xy[0]), int(xy[1])
        for node in self.graph.G.nodes:
            pos = self._pos[node]
            neighbor_force = self.forces[node]["single_neighbor"]
            neighborhood_force = self.forces[node]["neighborhood"]
            centrality_force = self.forces[node]["centrality"]
            random_force = self.forces[node]["random"]
            to_neighbor = normalize(pos + neighbor_force) * self.height_map.size // 100
            to_neighborhood = normalize(pos + neighborhood_force ) * self.height_map.size // 100
            to_center = normalize(pos + centrality_force ) * self.height_map.size // 100


            drawutils.draw_line(mapstate, to_int(pos), to_int(to_neighbor), (128, 0, 0))
            drawutils.draw_line(mapstate, to_int(pos), to_int(to_neighborhood), (0, 50, 0))
            drawutils.draw_line(mapstate, to_int(pos), to_int(to_center), (255, 10, 255))

        return mapstate


    
    def compute_influence_single(self, node):
        # computes the influence of this node to all other nodes.
        node_pos = self._pos[node]
        vals = np.linalg.norm(self.__precomputed_pairs - node_pos, axis=1).reshape((self.height_map.size, self.height_map.size))
        return self.graph.Pr(node)/(vals + 1) * 10

    def compute_single_neighbor_force(self, current, neighbor):
        c_pr = self.graph.Pr(current)
        current_pos = self.get_pos(current)
        neighbor_pr = self.graph.Pr(neighbor)
        neighbor_pos = self.get_pos(neighbor)
        try:
            direction_to_neighbor: vec.Vector2 = (neighbor_pos - current_pos)
        except Exception as e:
            raise Exception(f"Error: neighbor: {neighbor_pos} current: {current_pos}") from e
        cur_neig_mid = midpoint([current_pos, neighbor_pos])
        expectation = self.graph.Pr([current, neighbor])
        # TOOD: maybe only use neighbor and current for the actual value?
        actual = self.compute_influence(cur_neig_mid, [current, neighbor])
        #actual = self.compute_influence(cur_neig_mid, nodes)

        # now there are some cases to take care of 
        # if actual == expectation we don't need to care
        # if actual != expectation
        #   we need to figure out if we should move closer or further away
        #   if the value of cur is > actual we need to move away from the midpoint 
        #   otherwise we need to move closer 
        #   now to figure out how much we need to move we need to know the difference 
        #   of our node and the midpoint
        diff = actual - expectation
        if diff == 0:
            return vec.Vector2(0, 0)

        # if diff < 0 then actual < 
        if diff < 0:
            # actual < expectation
            # we need to increase the value of actual!
            # if cur drags the value down we do this by moving cur away
            # otherwise cur pulls the value up and we need to move it closer
            if c_pr < neighbor_pr:
                # actual is dragged down by current
                # we need to move away!
                # by how much do we need to move away?
                direction_to_neighbor = -direction_to_neighbor
                pass
            else:
                # actual is pulled up by cur so move it closer
                pass
        else:
            # diff > 0 => actual > expecation
            # if cur is larger than neighbor we need to move cur further away
            # otherwise cur is lower and we need to move it closer
            if c_pr < neighbor_pr:
                # move closer!
                pass
            else:
                # move away
                direction_to_neighbor = -direction_to_neighbor
        return direction_to_neighbor

    def compute_neighborhood_force(self, current, neighbors):
        current_pos = self.get_pos(current)
        c_pr = self.graph.Pr(current)
        neighbor_pos = [self.get_pos(n) for n in neighbors if n != current]
        force = vec.Vector2(0, 0)
        if neighbor_pos:
                nodes_to_include = neighbors + [current]
                center_of_neighbors = midpoint(neighbor_pos + [current])
                expected = self.graph.Pr(nodes_to_include)
                actual = self.compute_influence(center_of_neighbors, nodes_to_include)
                direction_to_center = normalize(center_of_neighbors - current_pos)

                if actual < expected:
                    if c_pr < expected:
                        # move closer
                        pass
                    else:
                        # move away
                        direction_to_center = -direction_to_center
                        pass
                else:
                    # actual > expected
                    if c_pr < expected:
                        # move away
                        direction_to_center = -direction_to_center
                    else:
                        # move closer
                        pass
                force += direction_to_center
        return force

    
    def compute_centrality_force(self, current):
        center_value = self.compute_influence(vec.Vector2(0, 0), self.graph.G.nodes)
        expected_value = self.graph.Pr(self.graph.G.nodes)
        c_pr = self.graph.Pr(current)
        direction_to_center = normalize(vec.Vector2(0, 0) - self.get_pos(current))
        if center_value < expected_value:
            # center value is too low, we want to increase it.
            if c_pr < expected_value:
                # move close 
                pass
            else:
                direction_to_center = -direction_to_center
        else:
            if c_pr < expected_value:
                # move away
                direction_to_center = -direction_to_center
            else:
                pass
        return direction_to_center

    def assign_force(self, node, name, value):
        d = self.forces.get(node, {})
        d[name] = value
        self.forces[node] = d
        return value.copy()

    def _iter_step(self, i):
        print(f"ITERATION #{i}")
        G = self.graph.G
        nodes = G.nodes
        # we want each node to be affected by forces.
        # 1) given node U and neighbor V and thier probabilites Pr[U], Pr[V]:
        #   check the value M_v at midpoint M. 
        #   move U such that M_v gets closer to (Pr[U] + Pr[V]) / 2
        # 2) for all neighbors of U with Pr[neighbors of U] 
        #  get midpoint of U and its neighbors M, and value of that M_v
        #  move U such that midpoint gets closer to the desired value
        # 3) get the center of all nodes move U such that center is closer to Pr[all nodes]
        for current in nodes:
            current_pos = self.get_pos(current)
            neighbors = list(G.neighbors(current))
            force = vec.Vector2(0, 0)
            rand_force_x = R.randint(int(-50/(i+1)), int(50/(i+1))) / 100
            rand_force_y = R.randint(int(-50/(i+1)), int(50/(i+1))) / 100
            rand_force = vec.Vector2(rand_force_x, rand_force_y)
            mag = 0.05 * (1/(i+1))
            for neighbor in neighbors:
                if current == neighbor:
                    continue
                force += self.compute_single_neighbor_force(current, neighbor)
            self.assign_force(current, "single_neighbor", force)
            # II) move to / away from center of neighbors:
            force += self.assign_force(current, "neighborhood", self.compute_neighborhood_force(current, neighbors))
            force += self.assign_force(current, "centrality", self.compute_centrality_force(current))
            force += self.assign_force(current, "random", rand_force)
            # move the node more into the center if it gets really close to one of the edges
            # a node is close to an edge if it's x or y is close to -1 or 1
            force = normalize(force)
            force *= mag

            # move the node
            self.__node_positions[current] = current_pos + force




        return 100 # always continue

    def layout(self) -> dict:
        MAX_ITER = self.iter_steps
        MOVEMENT_STOP = 10
        for i in range(MAX_ITER):
            movement = self._iter_step(i)
            if movement < MOVEMENT_STOP:
                break

        return self.__draw_to_heightmap()
    
    def step(self):
        self.forces = {}
        self._iter_step(self.__current_step)
        self.__current_step += 1
        return self.__draw_to_heightmap()
