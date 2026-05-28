from parser import MazeConfig
from mazegen import MazeGen
from mazegen.solver import path_to_directions


if __name__ == "__main__":
    config = MazeConfig()
    config.parse_config()
    maze = MazeGen(config)
    maze.generate()
    for line in maze.grid:
        for i in line:
            print(f"{i:X}", end="")
        print()
    print()
    print(f"{config.entry[0]},{config.entry[1]}")
    print(f"{config.exit_[0]},{config.exit_[1]}")
    print(path_to_directions(maze.solution))
