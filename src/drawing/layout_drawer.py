from __future__ import annotations
import cv2
from typing import TYPE_CHECKING
from drawing.image import Image
import numpy as np
from drawing.map_operations import invert, to_byte
from drawing.color_palettes import seaborn_like_128
from layout.base import Layout

if TYPE_CHECKING:
    from layout.base import Layout

class LayoutDrawer:

    def __init__(self, layout: Layout, draw_nodes=True, draw_edges=True, draw_lables=True) -> None:
        self.layout = layout
        self.draw_nodes = draw_nodes
        self.draw_edges = draw_edges
        self.draw_labels = draw_lables

    def init_image(self) -> Image:
        return Image(self.layout.size)

    def draw(self):
        pos: dict = self.layout.layout()
        assert isinstance(pos, dict), pos
        graph = self.layout.graph
        image = self.init_image()
        if self.draw_nodes:
            for node, node_pos in pos.items():
                self.draw_node(image, node_pos)
                if self.draw_labels:
                    self.draw_label(image, node_pos, node)
        if self.draw_edges:
            for u, v, data in graph.G.edges(data=True):
                start = pos[u]
                end = pos[v]
                w = data["weight"]
                self.draw_edge(image, start, end, w)

        return image
    
    def draw_node(self, image, position):
        x, y = position
        image.circle((x, y), self.layout.size // 100, 1)

    def draw_label(self, image, position, node):
        x, y = position
        image.text((x, y + ( self.layout.size // 100) + 2), f"{node}", 1)

    def draw_edge(self, image, start, end, weight):
        image.line(start, end, weight)


class HillLayoutDrawer(LayoutDrawer):

    def init_image(self) -> Image:
        hm = self.layout._height_map
        min_value = np.min(hm)
        max_val = np.max(hm)
        scaled = (hm - min_value) / max_val
        return Image(self.layout.size, init_data=scaled).as_byte_image().as_pallete(seaborn_like_128)

    def draw_edge(self, image, start, end, weight):
        image.line(start, end, [0, 0, 0, 3])

    def draw_node(self, image, position):
        x, y = position
        image.circle((x, y), 0, [0, 0, 0, 10])


class AlphaHillLayoutDrawer(LayoutDrawer):

    def __init__(self, layout: Layout, draw_nodes=True, draw_edges=True, draw_lables=True) -> None:
        super().__init__(layout, draw_nodes, draw_edges, draw_lables)
        self.__hill_drawer = HillLayoutDrawer(layout, False, False, False)
        self.__drawer = LayoutDrawer(layout, draw_nodes, draw_edges, draw_lables)

    def draw(self):
        nodes = self.__drawer.draw().data
        inv = to_byte(invert(nodes))
        nodes_mat = cv2.merge((inv, inv, inv))
        hills = self.__hill_drawer.draw().data
        alpha = 0.75
        beta = 1 - alpha
        out = cv2.addWeighted(hills, alpha, nodes_mat, beta, 0.0)
        return Image(
            self.layout.size,
            init_data=out,
            is_byte=True,
            is_rgb=True
        )