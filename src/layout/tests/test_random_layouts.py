from layout.best_fit_markov_layout import BestFitMarkovLayout
from layout.random_layout import RandomLayout
from layout.traditional_spring_layout import TraditionalSpringLayout
from layout.random_hill_layout import RandomHillLayout
from layout.spring_layout import SpringHillLayout
from drawing.layout_drawer import LayoutDrawer, HillLayoutDrawer, AlphaHillLayoutDrawer
from util.paths import OUT_PATH
from graph.graph import Graph
from loader.constructed_graphs import one_center, many_centers, many_centers_connected


def test_random_layouts_with_constructed():
    graphs = {
        "one_center": one_center(40, "x"),
        "many_center": many_centers(10, 4),
        "many_centers_connected": many_centers_connected(10, 4)
    }
    for name, digraph in graphs.items():
        print("generate ", name)
        print(digraph)
        g = Graph(digraph)
        print(g.probabilites)
        layout = RandomHillLayout(g, 256)
        drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=True)
        im = drawer.draw()
        im.as_byte_image().save(str(OUT_PATH / f"random_{name}.png"))
        spring_layout = SpringHillLayout(g, 256)
        spring_drawer = HillLayoutDrawer(spring_layout, draw_edges=False, draw_nodes=True)
        im = spring_drawer.draw()
        im.as_byte_image().save(str(OUT_PATH / f"spring_{name}.png"))
        spring_layout = SpringHillLayout(g, 256, use_agg=True)
        spring_drawer = HillLayoutDrawer(spring_layout, draw_edges=False, draw_nodes=True)
        im = spring_drawer.draw()
        im.as_byte_image().save(str(OUT_PATH / f"spring_aggregated_{name}.png"))
