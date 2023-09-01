from src.config import NODE_PATH
from src.refactor.ConfigRefactor import ConfigRefactor

if __name__ == '__main__':
    config_refactor = ConfigRefactor(NODE_PATH)
    config_refactor.refactor()
