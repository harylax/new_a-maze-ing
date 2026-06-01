from mazegen import MazeGen, MazeGenDFS
from mlx import Mlx  # type: ignore
from typing import Any
from output_writer import write_maze
import random


NORTH: int = 0b0001
EAST:  int = 0b0010
SOUTH: int = 0b0100
WEST:  int = 0b1000

BG_COLOR:    int = 0xFF0F172A
CELL_COLOR:  int = 0xFF222222
ENTRY_COLOR: int = 0xFF60A5FA
EXIT_COLOR:  int = 0xFFFB7185
PATH_COLOR:  int = 0xFF22C55E
P42_COLOR:   int = 0xFFA855F7
TEXT_COLOR:  int = 0xFFFFFFFF

WALL_COLORS: list[int] = [
    0xFFFFFFFF,
    0xFFFF00FF,
    0xFFFF0000,
    0xFFFFFF00,
    0xFF0000FF,
    0xFF00FFFF
]


class MazeMLX:
    def __init__(self, maze: MazeGen) -> None:
        self.maze: MazeGen = maze
        self.mlx: Mlx = Mlx()
        self.mlx_ptr: Any = self.mlx.mlx_init()
        self.cell_size: int = self._cell_size()
        self.win_width: int = self.maze.config.width * self.cell_size
        self.win_height: int = self.maze.config.height * self.cell_size + 50
        self.win_ptr: Any = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_width,
            self.win_height, "Ayano.Rai"
            )
        self.data: Any
        self.bpp: int
        self.line_size: int
        self.fmt: int
        self.img_ptr: Any = self._create_image()
        self.show_solution: bool = False
        self._animation_index: int = 0
        self._path_displayed: bool = False
        self.wall_color: int = WALL_COLORS[0]

    def _cell_size(self) -> int:
        width = self.maze.config.width
        height = self.maze.config.height
        _, screen_w, screen_h = self.mlx.mlx_get_screen_size(
            self.mlx_ptr
            )
        cell_size: int = max(16, min(
            (screen_w // 2) // width,
            (screen_h // 2) // height
            ))
        return cell_size

    def _create_image(self) -> Any:
        img_ptr: Any = self.mlx.mlx_new_image(
            self.mlx_ptr, self.win_width, self.win_height
            )
        self.data, self.bpp, self.line_size, self.fmt = \
            self.mlx.mlx_get_data_addr(img_ptr)
        return img_ptr

    def render(self) -> None:
        self._fill_background()
        self._set_animation(self._maze_animation)

    def show_path(self) -> None:
        if not self._path_displayed:
            self._fill_background()
            self._draw_full_maze()
            self._animation_index = 0
            self._set_animation(self._path_animation)
            self._path_displayed = True
        else:
            self._fill_background()
            self._draw_full_maze()
            self._path_displayed = False
            self._animation_index = 0

    def _set_animation(self, callback: Any) -> None:
        self._animation_index = 0
        self.mlx.mlx_loop_hook(self.mlx_ptr, None, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, callback, None)

    def _put_pixel(self, x: int, y: int, color: int) -> None:
        if not (0 <= x < self.win_width and 0 <= y < self.win_height):
            return
        i = self.bpp // 8
        offset = y * self.line_size + x * i
        color_bytes = color.to_bytes(i, 'little')
        self.data[offset:offset + i] = color_bytes

    def _fill_background(self) -> None:
        for y in range(self.win_height):
            for x in range(self.win_width):
                self._put_pixel(x, y, BG_COLOR)

    def _draw_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        for j in range(y, y + h):
            for i in range(x, x + w):
                self._put_pixel(i, j, color)

    def _draw_cell(self, cx: int, cy: int, color: int) -> None:
        margin = 0
        px = cx * self.cell_size + margin
        py = cy * self.cell_size + margin
        self._draw_rect(
            px, py,
            self.cell_size - margin * 2,
            self.cell_size - margin * 2,
            color
            )

    def _draw_full_maze(self) -> None:
        for y in range(self.maze.config.height):
            for x in range(self.maze.config.width):
                self._draw_cell(x, y, CELL_COLOR)
                self._draw_walls(x, y, self.wall_color)
        self._draw_42_pattern()
        self._draw_entry_exit()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self._interactive_str()

    def _show_path_without_animation(self) -> None:
        for y in range(self.maze.config.height):
            for x in range(self.maze.config.width):
                self._draw_cell(x, y, CELL_COLOR)
                self._draw_walls(x, y, self.wall_color)
        self._draw_42_pattern()
        for x, y in self.maze.solution:
            self._draw_cell(x, y, PATH_COLOR)
            self._draw_walls(x, y, self.wall_color)
        self._draw_entry_exit
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self._interactive_str()

    def _maze_animation(self, param: Any) -> None:
        if self._animation_index > len(self.maze.history) - 1:
            self._draw_42_pattern()
            self._draw_entry_exit()
            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
                )
            self._interactive_str()
            self.mlx.mlx_loop_hook(self.mlx_ptr, None, None)
            return
        current, neighbor = self.maze.history[self._animation_index]
        cx, cy = current
        nx, ny = neighbor
        self._draw_cell(cx, cy, CELL_COLOR)
        self._draw_walls(cx, cy, self.wall_color)
        self._draw_cell(nx, ny, CELL_COLOR)
        self._draw_walls(nx, ny, self.wall_color)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self._interactive_str()
        self._animation_index += 1

    def _path_animation(self, param: Any) -> None:
        if self._animation_index > len(self.maze.solution) - 1:
            self._draw_entry_exit()
            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
                )
            self._interactive_str()
            self.mlx.mlx_loop_hook(self.mlx_ptr, None, None)
            return
        x, y = self.maze.solution[self._animation_index]
        self._draw_cell(x, y, PATH_COLOR)
        self._draw_walls(x, y, self.wall_color)
        self._draw_entry_exit()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self._interactive_str()
        self._animation_index += 1

    def _interactive_str(self) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            60,
            self.win_height - 30,
            TEXT_COLOR,
            "[r] regenerate | [p] path | [c] color | [esc] quit"
            )

    def _draw_42_pattern(self) -> None:
        for px, py in self.maze.pattern_42:
            self._draw_cell(px, py, P42_COLOR)

    def _draw_walls(self, cx: int, cy: int, color: int) -> None:
        cell: int = self.maze.grid[cy][cx]._walls
        cs = self.cell_size
        x = cx * cs
        y = cy * cs
        wall: int = cs // 7
        if cell & NORTH:
            self._draw_rect(x, y, cs, wall, color)
        if cell & EAST:
            self._draw_rect(x + cs - wall, y, wall, cs, color)
        if cell & SOUTH:
            self._draw_rect(x, y + cs - wall, cs, wall, color)
        if cell & WEST:
            self._draw_rect(x, y, wall, cs, color)

    def _draw_entry_exit(self) -> None:
        sx, sy = self.maze.config.entry
        ex, ey = self.maze.config.exit_
        self._draw_cell(sx, sy, ENTRY_COLOR)
        self._draw_cell(ex, ey, EXIT_COLOR)

    def _key_hook(self, keycode: int, param: Any) -> int:
        if keycode == 65307:
            self.mlx.mlx_loop_exit(self.mlx_ptr)
        elif keycode in (ord('r'), ord('R')):
            self._regenerate()
        elif keycode in (ord('p'), ord('P')):
            if self.maze.solution:
                self.show_path()
        elif keycode in (ord('c'), ord('C')):
            self.wall_color = random.choice(WALL_COLORS)
            self._draw_full_maze()
        elif keycode in [65293, 65421]:
            if self._path_displayed:
                self._show_path_without_animation()
                self._path_displayed = True
                self._animation_index = 0
            else:
                self._draw_full_maze()
        return 0

    def _regenerate(self) -> None:
        self.maze = MazeGenDFS(self.maze.config)
        if self.maze.config.seed is None:
            self.maze.config.seed = 0
        self.maze.config.seed += 1
        self.maze.generate()
        self._animation_index = 0
        self._path_displayed = False
        write_maze(self.maze)
        self.render()

    def run(self) -> None:
        self.mlx.mlx_key_hook(self.win_ptr, self._key_hook, None)
        self.mlx.mlx_loop(self.mlx_ptr)
