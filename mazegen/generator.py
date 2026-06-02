import random
import sys
from config_parser import MazeConfig
from .solver import solve
from abc import ABC, abstractmethod
from heapq import heappush, heappop
from .pattern_42 import draw_42

sys.setrecursionlimit(100000)


class MazeGenError(Exception):
    pass


class Cell:
    def __init__(self) -> None:
        self._walls: int = 0b1111
        self.visited: bool = False

    def open_wall(self, direction: str) -> None:
        dir_str: str = direction.capitalize()
        if dir_str in ['North', 'N']:
            self._walls &= ~0b0001
        elif dir_str in ['East', 'E']:
            self._walls &= ~0b0010
        elif dir_str in ['South', 'S']:
            self._walls &= ~0b0100
        elif dir_str in ['West', 'W']:
            self._walls &= ~0b1000

    def close_wall(self, direction: str) -> None:
        dir_str: str = direction.capitalize()
        if dir_str in ['North', 'N']:
            self._walls |= 0b0001
        elif dir_str in ['East', 'E']:
            self._walls |= 0b0010
        elif dir_str in ['South', 'S']:
            self._walls |= 0b0100
        elif dir_str in ['West', 'W']:
            self._walls |= 0b1000


class MazeGen(ABC):
    def __init__(self, config: MazeConfig) -> None:
        self.config: MazeConfig = config
        self.grid: list[list[Cell]] = []
        self.solution: list[tuple[int, int]] = []
        self.pattern_42: set[tuple[int, int]] = set()
        self.history: list[tuple[tuple[int, int], tuple[int, int]]] = []

    def generate(self) -> None:
        if self.config.seed is not None:
            random.seed(self.config.seed)
        self._init_grid()
        self.pattern_42 = draw_42(self.config.width, self.config.height)
        self._validate_entry_exit()
        self._apply_pattern_42()
        self._carve_passages()
        if not self.config.perfect:
            self._add_loops()
        self._close_all_borders()
        self.solution = solve(
            self._get_final_grid(),
            self.config.width,
            self.config.height,
            self.config.entry,
            self.config.exit_
            )

    def _add_loops(self) -> None:
        cells: list[tuple[int, int]] = []
        for y in range(self.config.height):
            for x in range(self.config.width):
                if (x, y) in self.pattern_42:
                    continue
                cells.append((x, y))
        random.shuffle(cells)
        num_loops: int = len(cells) // 10
        count: int = 0
        for x, y in cells:
            if count >= num_loops:
                return
            directions: list[tuple[int, int]] = [(1, 0), (0, 1)]
            dx, dy = random.choice(directions)
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.pattern_42:
                continue
            if not self._is_valid_cell(nx, ny):
                continue
            self._remove_wall((x, y), (nx, ny))
            count += 1

    def _get_final_grid(self) -> list[list[int]]:
        final_grid: list[list[int]] = []
        for row in self.grid:
            current_row: list[int] = []
            for cell in row:
                current_row.append(cell._walls)
            final_grid.append(current_row)
        return final_grid

    def _is_valid_cell(self, x: int, y: int) -> bool:
        return 0 <= x < self.config.width and 0 <= y < self.config.height

    def _validate_entry_exit(self) -> None:
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

    def _init_grid(self) -> None:
        for _ in range(self.config.height):
            row: list[Cell] = []
            for _ in range(self.config.width):
                cell = Cell()
                row.append(cell)
            self.grid.append(row)

    @abstractmethod
    def _carve_passages(self) -> None:
        pass

    def _close_all_borders(self) -> None:
        for y in range(self.config.height):
            for x in range(self.config.width):
                if y == 0:
                    self.grid[y][x].close_wall('North')
                if y == self.config.height - 1:
                    self.grid[y][x].close_wall('South')
                if x == 0:
                    self.grid[y][x].close_wall('West')
                if x == self.config.width - 1:
                    self.grid[y][x].close_wall('East')

    def _apply_pattern_42(self) -> None:
        directions: list[tuple[int, int, str]] = [
            (0, -1, 'South'),
            (0, 1, 'North'),
            (-1, 0, 'East'),
            (1, 0, 'West')
        ]
        for (px, py) in self.pattern_42:
            self.grid[py][px].visited = True
            for dx, dy, wall_to_close in directions:
                nx, ny = px + dx, py + dy
                if not self._is_valid_cell(nx, ny):
                    continue
                if (nx, ny) in self.pattern_42:
                    continue
                self.grid[ny][nx].close_wall(wall_to_close)

    def _remove_wall(self,
                     current: tuple[int, int],
                     neighbor: tuple[int, int]
                     ) -> None:
        x, y = current
        nx, ny = neighbor
        if x > nx:
            self.grid[y][x].open_wall('West')
            self.grid[ny][nx].open_wall('East')
        if x < nx:
            self.grid[y][x].open_wall('East')
            self.grid[ny][nx].open_wall('West')
        if y > ny:
            self.grid[y][x].open_wall('North')
            self.grid[ny][nx].open_wall('South')
        if y < ny:
            self.grid[y][x].open_wall('South')
            self.grid[ny][nx].open_wall('North')
        self.history.append((current, neighbor))


class MazeGenDFS(MazeGen):
    def _carve_passages(self) -> None:
        self._dfs_recursive(self.config.entry)

    def _dfs_recursive(self, current: tuple[int, int]) -> None:
        x, y = current
        self.grid[y][x].visited = True
        directions: list[tuple[int, int]] = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not self._is_valid_cell(nx, ny):
                continue
            if self.grid[ny][nx].visited:
                continue
            if (nx, ny) in self.pattern_42:
                continue
            self._remove_wall(current, (nx, ny))
            self._dfs_recursive((nx, ny))


class MazeGenPrim(MazeGen):
    def _carve_passages(self) -> None:
        self._prim()

    def _get_neighbors(
            self, current: tuple[int, int]
            ) -> list[tuple[int, int]]:
        directions: list[tuple[int, int]] = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        neighbors: list[tuple[int, int]] = []
        x, y = current
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not self._is_valid_cell(nx, ny):
                continue
            if (nx, ny) in self.pattern_42:
                continue
            neighbors.append((nx, ny))
        return neighbors

    def _prim(self) -> None:
        x, y = self.config.entry
        self.grid[y][x].visited = True
        walls: list[tuple[float, tuple[int, int], tuple[int, int]]] = []
        for (nx, ny) in self._get_neighbors((x, y)):
            if (nx, ny) in self.pattern_42:
                continue
            heappush(walls, (random.random(), (x, y), (nx, ny)))
        while walls:
            _, current, neighbor = heappop(walls)
            nx, ny = neighbor
            if self.grid[ny][nx].visited:
                continue
            self.grid[ny][nx].visited = True
            self._remove_wall(current, neighbor)
            for nnx, nny in self._get_neighbors(neighbor):
                if self.grid[nny][nnx].visited:
                    continue
                if (nnx, nny) in self.pattern_42:
                    continue
                heappush(walls, (random.random(), (nx, ny), (nnx, nny)))
