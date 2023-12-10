from abc import ABC, abstractmethod

class GraphLoader(ABC):
    """Loads and retunrs an instance of a graph using the supplied path parameter"""
    path = None

    def __init__(self, **kw) -> None:
        assert self.path

    @abstractmethod
    def load(self):
        pass
