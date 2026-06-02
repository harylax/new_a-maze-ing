from config_parser import MazeConfig
from mazegen import MazeGen, MazeGenDFS, MazeGenPrim
from output_writer import write_maze
from mlx_renderer import MazeMLX


if __name__ == "__main__":
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
