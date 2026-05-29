import random
import sys
from config_parser import MazeConfig
from .solver import solve


NORTH: int = 0b0001
EAST: int = 0b0010
SOUTH: int = 0b0100
WEST: int = 0b1000


class MazeGenError(Exception):
    pass


class MazeGen:
    def __init__(self, config: MazeConfig) -> None:
        self.config: MazeConfig = config
        self.grid: list[list[int]] = []
        self.solution: list[tuple[int, int]] = []
        self.pattern_42: set[tuple[int, int]] = set()

    def generate(self) -> None:
        if self.config.seed is not None:
            random.seed(self.config.seed)
        self._init_grid()
        self.pattern_42 = self.draw_42()
        if self.config.entry in self.pattern_42:
            raise MazeGenError(
                "Invalid ENTRY coordinates, got "
                f"{self.config.entry} inside the 42 pattern"
                )
        if self.config.exit_ in self.pattern_42:
            raise MazeGenError(
                "Invalid EXIT coordinates, got "
                f"{self.config.exit_} inside the 42 pattern"
                )
        self._carve_passages(self.config.entry[0], self.config.entry[1])
        self.solution = solve(
            self.grid,
            self.config.width,
            self.config.height,
            self.config.entry,
            self.config.exit_
            )

    def _init_grid(self) -> None:
        for _ in range(self.config.height):
            row: list[int] = []
            for _ in range(self.config.width):
                row.append(0b1111)
            self.grid.append(row)

    def draw_42(self) -> set[tuple[int, int]]:
        if self.config.width < 9 or self.config.height < 7:
            print("Maze size is too small for the 42 pattern", file=sys.stderr)
            return set()
        grid_42: list[list[int]] = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]
        grid_center: tuple[int, int] = (
            self.config.width // 2,
            self.config.height // 2
            )
        x, y = grid_center
        offset = x - 3, y - 2
        dx, dy = offset
        pattern: set[tuple[int, int]] = set()
        for row, line in enumerate(grid_42):
            for col, element in enumerate(line):
                if element == 1:
                    pattern.add((col + dx, row + dy))
        return pattern

    def _remove_wall(self, x: int, y: int, nx: int, ny: int) -> None:
        if x < nx:
            self.grid[y][x] &= ~EAST
            self.grid[ny][nx] &= ~WEST
        elif x > nx:
            self.grid[y][x] &= ~WEST
            self.grid[ny][nx] &= ~EAST
        elif y < ny:
            self.grid[y][x] &= ~SOUTH
            self.grid[ny][nx] &= ~NORTH
        elif y > ny:
            self.grid[y][x] &= ~NORTH
            self.grid[ny][nx] &= ~SOUTH

    def _carve_passages(
            self, x: int, y: int,
            visited: set[tuple[int, int]] | None = None
            ) -> None:
        if visited is None:
            visited = set()
        visited.add((x, y))
        directions: list[tuple[int, int]] = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not 0 <= nx < self.config.width:
                continue
            if not 0 <= ny < self.config.height:
                continue
            if (nx, ny) in visited:
                continue
            if (nx, ny) in self.pattern_42:
                continue
            self._remove_wall(x, y, nx, ny)
            self._carve_passages(nx, ny, visited)
