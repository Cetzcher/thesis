from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent

SRC_PATH = (BASE_PATH / "src").resolve().absolute()
DATA_PATH = (BASE_PATH / "data").resolve().absolute()
OUT_PATH = (BASE_PATH / "out").resolve().absolute()

