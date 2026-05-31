from mazegen import MazeGen
from mlx import Mlx  # type: ignore
from typing import cast


NORTH: int = 0b0001
EAST: int = 0b0010
SOUTH: int = 0b0100
WEST: int = 0b1000

BG_COLOR = 0xFF0F172A
WALL_COLOR = 0xFFFFFFFF
PATH_COLOR = 0xFF000000
ENTRY_COLOR = 0xFF60A5FA
EXIT_COLOR = 0xFFFB7185
P42_COLOR = 0xFFA855F7
TEXT_COLOR = 0xFFFFFFFF


class MazeMLX:
    def __init__(self, maze: MazeGen):
        self.maze: MazeGen = maze
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        max_cell_size = min(
            800 // maze.config.width, 600 // maze.config.height
            )
        self.cell_size = max(20, max_cell_size)
        self.win_width = maze.config.width * self.cell_size
        self.win_height = maze.config.height * self.cell_size + 100
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_width, self.win_height, "42 A-Maze-ing"
            )
        self.show_solution: bool = False
        self.img = None
        self.data = None
        self.sl = None
        self._create_image()

    def _create_image(self) -> None:
        self.img = self.mlx.mlx_new_image(
            self.mlx_ptr, self.win_width, self.win_height
            )
        self.data, _, self.sl, _ = self.mlx.mlx_get_data_addr(self.img)

    def _put_pixel(self, x, y, color) -> None:
        if not (
            0 <= x < self.win_width and 0 <= y < self.win_height
        ):
            return
        idx = (y * self.sl) + (x * 4)
        color_bytes = color.to_bytes(4, 'little')
        data = cast(bytearray, self.data)
        data[idx:idx + 4] = color_bytes

    def _draw_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        for i in range(h):
            for j in range(w):
                self._put_pixel(x + j, y + i, color)

    def _draw_maze(self):
        self._draw_rect(0, 0, self.win_width, self.win_height, BG_COLOR)
        c = self.cell_size
        for y in range(self.maze.config.height):
            for x in range(self.maze.config.width):
                px = x * c
                py = y * c
                cell = self.maze.grid[y][x]._walls
                cell_color = (
                    P42_COLOR if (x, y) in self.maze.pattern_42
                    else BG_COLOR
                )
                self._draw_rect(px + 1, py + 1, c - 2, c - 2, cell_color)
                if cell & NORTH:
                    self._draw_rect(px, py, c, 3, WALL_COLOR)
                if cell & EAST:
                    self._draw_rect(px + c - 3, py, 3, c, WALL_COLOR)
                if cell & SOUTH:
                    self._draw_rect(px, py + c - 3, c, 3, WALL_COLOR)
                if cell & WEST:
                    self._draw_rect(px, py, 3, c, WALL_COLOR)
        ex, ey = self.maze.config.entry
        sx, sy = self.maze.config.exit_
        self._draw_rect(ex * c + 4, ey * c + 4, c - 8, c - 8, ENTRY_COLOR)
        self._draw_rect(sx * c + 4, sy * c + 4, c - 8, c - 8, EXIT_COLOR)

    def _draw_solution(self) -> None:
        if not self.maze.solution:
            return
        c = self.cell_size
        for x, y in self.maze.solution:
            px = x * c + c // 4
            py = y * c + c // 4
            self._draw_rect(px, py, c // 2, c // 2, PATH_COLOR)

    def render(self) -> None:
        self._draw_maze()
        if self.show_solution:
            self._draw_solution()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img, 0, 0
            )
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            10,
            self.win_height - 30,
            TEXT_COLOR,
            f"Seed: {self.maze.config.seed} | R: Regenerate | "
            "P: Solution | ESC: Quit"
            )
