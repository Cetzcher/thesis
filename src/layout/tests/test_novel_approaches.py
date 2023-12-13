from layout.force_directed import ForceDirectedLayout
from layout.best_fit_markov_layout import BestFitMarkovLayout
from layout.random_layout import RandomLayout
from layout.traditional_spring_layout import TraditionalSpringLayout
from layout.random_hill_layout import RandomHillLayout
from layout.spring_layout import SpringHillLayout
from drawing.layout_drawer import LayoutDrawer, HillLayoutDrawer, AlphaHillLayoutDrawer
from util.paths import OUT_PATH
from graph.graph import Graph
from loader.constructed_graphs import many_centers_connected, one_center, barbell
from layout.density_layout import DensityLayout
from layout.density_layout_rect import DensityLayoutRect
from layout.density_layout_rect_pairwise import DensityLayoutRectPairwise
from layout.expectation_mean_layout import ExpecationMeanLayout
from layout.spring_layout import SpringHillLayout
from layout.spring_layout_hill_with_errosion import SpringHillLayoutErrosion

def test_novel_1_density():
    g = Graph(many_centers_connected(30, 10))
    layout = DensityLayout(g, 256)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_density_layout.png"))

def test_novel_2_density():
    g = Graph(many_centers_connected(30, 10))
    layout = DensityLayoutRect(g, 256)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_density_layout_rect.png"))


def test_novel_3_density():
    g = Graph(many_centers_connected(2, 10))
    layout = DensityLayoutRectPairwise(g, 256)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_density_layout_rect_pairs.png"))



def test_novel_1_density_barbell():
    g = Graph(barbell(30, 10))
    layout = DensityLayout(g, 256)
    drawer = AlphaHillLayoutDrawer(layout, draw_edges=True, draw_nodes=True, scale=False)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_density_layout_barbell.png"))

def test_novel_2_density_barbell():
    g = Graph(barbell(30, 10))
    layout = DensityLayoutRect(g, 256)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_density_layout_rect_barbell.png"))



def test_novel_3_density_ramp():
    g = Graph(barbell(20, 30))
    layout = DensityLayoutRectPairwise(g, 128)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False, scale=True)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_density_layout_rect_pairs_ramp.png"))


def test_novel_expectation_mean_layout():
    g = Graph(barbell(20, 30))
    layout = ExpecationMeanLayout(g, 128)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False, scale=True)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / "novel_expectation_mean_layout.png"))

def test_force_directed():
    g = Graph(barbell(12, 4))
    layout = ForceDirectedLayout(g, 512)
    drawer = HillLayoutDrawer(layout, draw_edges=True, draw_nodes=True, scale=True)
    for i in range(1000):
        if i == 999:
            layout.render_to_map()
        if i  % 250 == 0 or i == 999:
            im = drawer.draw()
            im.as_byte_image().save(str(OUT_PATH / f"force_directed_{i}.png"))
        else:
            layout.layout()

def test_force_directed_trad():
    g = Graph(barbell(64, 12))
    layout = SpringHillLayout(g, 512)
    drawer = HillLayoutDrawer(layout, draw_edges=True, draw_nodes=True, scale=True)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / f"force_directed_traditional.png"))


def test_force_directed_trad_errosion():
    g = Graph(barbell(64, 12))
    layout = SpringHillLayoutErrosion(g, 512)
    drawer = HillLayoutDrawer(layout, draw_edges=True, draw_nodes=True, scale=True)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / f"force_directed_errosion_barbell.png"))


def test_force_directed_trad_errosion_2():
    g = Graph(many_centers_connected(4, 60))
    layout = SpringHillLayoutErrosion(g, 512)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False, scale=True)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / f"force_directed_errosion_many_centers.png"))



def test_force_directed_trad_errosion_3():
    from loader.ramp import Loader
    g = Graph(Loader().load())
    layout = SpringHillLayoutErrosion(g, 512)
    drawer = HillLayoutDrawer(layout, draw_edges=False, draw_nodes=False, scale=True)
    im = drawer.draw()
    im.as_byte_image().save(str(OUT_PATH / f"force_directed_errosion_ramp.png"))