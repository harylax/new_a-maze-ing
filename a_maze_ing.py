from config_parser import MazeConfig
from mazegen import MazeGenDFS
from output_writer import write_maze
from mlx_renderer import MazeMLX
# from ascii_renderer import MazeRenderer

if __name__ == "__main__":
    config = MazeConfig()
    config.parse_config()
    maze = MazeGenDFS(config)
    maze.generate()
    write_maze(maze)
    visual = MazeMLX(maze)
    # visual = MazeRenderer(maze)
    visual.render()
    # visual.display()

    def key_hook(keycode, param):
        if keycode == 65307:
            visual.mlx.mlx_loop_exit(visual.mlx_ptr)
        elif keycode in (ord('r'), ord('R')):
            config.seed += 1
            maze = MazeGenDFS(config)
            maze.generate()
            write_maze(maze)
            visual.maze = maze
            visual.render()
        elif keycode in (ord('p'), ord('P')):
            visual.show_solution = not visual.show_solution
            visual.render()
        return 0
    visual.mlx.mlx_key_hook(visual.win_ptr, key_hook, None)
    visual.mlx.mlx_loop(visual.mlx_ptr)
