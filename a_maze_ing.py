from config_parser import MazeConfig, ConfigError
from mazegen import MazeGen, MazeGenDFS, MazeGenPrim, MazeGenError
from output_writer import write_maze
from mlx_renderer import MazeMLX, MazeRendererError
from sys import stderr


def main() -> None:
    config = MazeConfig()
    config.parse_config()
    if config.algo.lower() == 'prim':
        maze: MazeGen = MazeGenPrim(config)
    else:
        maze = MazeGenDFS(config)
    maze.generate()
    write_maze(maze)
    visual = MazeMLX(maze)
    visual.render()
    visual.run()


if __name__ == "__main__":
    try:
        main()
    except ConfigError as err:
        print(f"Configuration Error: {err}", file=stderr)
    except MazeGenError as err:
        print(f"Maze Generation Error: {err}", file=stderr)
    except MazeRendererError as err:
        print(f"Minilibx Error: {err}", file=stderr)
