from layout.best_fit_markov_layout import BestFitMarkovLayout
from layout.random_walk_layout import RandomWalkLayout
from layout.random_layout import RandomLayout
from layout.traditional_spring_layout import TraditionalSpringLayout
from layout.spring_layout import SpringHillLayout
from drawing.layout_drawer import LayoutDrawer, HillLayoutDrawer
from util.paths import OUT_PATH
from graph.graph import Graph
from loader import ramp


def test_best_fit_markov_layout():
    g = Graph(ramp.Loader().load())
    layout = BestFitMarkovLayout(g, 256)
    drawer = LayoutDrawer(layout)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "best_fit_markov_layout.png"))


def test_random_layout():
    g = Graph(ramp.Loader().load())
    layout = RandomLayout(g, 256)
    drawer = LayoutDrawer(layout)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "random_layout.png"))


def test_random_walk_layout():
    g = Graph(ramp.Loader().load())
    layout = RandomWalkLayout(g, 256)
    drawer = HillLayoutDrawer(layout)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "random_walk_layout.png"))


def test_expectation_mean_layout():
    g = Graph(ramp.Loader().load())
    layout = RandomWalkLayout(g, 256)
    drawer = HillLayoutDrawer(layout)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "expectation_mean_layout.png"))


def test_spring_layout():
    g = Graph(ramp.Loader().load())
    layout = TraditionalSpringLayout(g, 256)
    drawer = LayoutDrawer(layout)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "traditional_spring_layout.png"))


def test_spring_layout_with_height_map():
    g = Graph(ramp.Loader().load())
    layout = SpringHillLayout(g, 256)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "hill_spring_layout.png"))