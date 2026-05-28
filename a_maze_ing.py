from parser import MazeConfig
from mazegen import MazeGen


if __name__ == "__main__":
    config = MazeConfig()
    config.parse_config()
    maze = MazeGen(config)
    maze.generate()
    for line in maze.grid:
        for i in line:
            print(f"{i:X}", end="")
        print()
