from config_parser import MazeConfig
from mazegen import MazeGen
from output_writer import write_maze


if __name__ == "__main__":
    config = MazeConfig()
    config.parse_config()
    maze = MazeGen(config)
    maze.generate()
    write_maze(maze)
