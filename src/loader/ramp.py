from .graph_loader import DATA_PATH
from .ramp_base import RampLoader

class Loader(RampLoader):
    path = DATA_PATH / "ramp.txt"
