from abc import ABC, abstractmethod
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data"
DATA_PATH = DATA_PATH.resolve().absolute()

class GraphLoader(ABC):
    """Loads and retunrs an instance of a graph using the supplied path parameter"""
    path = None

    def __init__(self, **kw) -> None:
        assert self.path

    @abstractmethod
    def load(self):
        pass
