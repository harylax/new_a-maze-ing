from parser import MazeConfig


class MazeGenError(Exception):
    pass


class MazeGen:
    def __init__(self, config: MazeConfig) -> None:
        self.config: MazeConfig = config
        self.grid: list[list[int]] = []
        self.solution: list[int] = []
        self.pattern_42: list[tuple[int, int]] = []
