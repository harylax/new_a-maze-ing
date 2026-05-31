from mazegen import MazeGen

WALL = '\033[40m  \033[0m'
OPEN = '\033[47m  \033[0m'
ENTRY = '\033[45mEn\033[0m'
EXIT = '\033[41mEx\033[0m'
PATH = '\033[46m  \033[0m'
P42 = '\033[100m  \033[0m'

WALL_COLORS = [
    '\033[40m',    # fond noir (défaut)
    '\033[42m',    # fond vert
    '\033[43m',    # fond jaune
    '\033[44m',    # fond bleu
    '\033[45m',    # fond magenta
    '\033[46m',    # fond cyan
    '\033[41m',    # fond rouge
]


class MazeRenderer:
    def __init__(self, maze: MazeGen) -> None:
        self.maze: MazeGen = maze
        self.show_path: bool = False
        self.color_index: int = 0
        self.wall_color = WALL_COLORS[self.color_index]

    def _rotate_color(self) -> None:
        self.color_index = (self.color_index + 1) % len(WALL_COLORS)
        self.wall_color = WALL_COLORS[self.color_index]

    def render(self) -> str:
        grid = self.maze.grid
        width = self.maze.config.width
        height = self.maze.config.height

        path_set: set = set()
        if self.show_path:
            x, y = self.maze.config.entry
            path_set.add((x, y))
            for move in self.maze.solution:
                if move == 'N':
                    y -= 1
                elif move == 'S':
                    y += 1
                elif move == 'E':
                    x += 1
                elif move == 'W':
                    x -= 1
                path_set.add((x, y))
        lines = []
        wall = f"{self.wall_color}  \033[0m"
        for y in range(height):
            # ligne du haut (murs Nord)
            top = ''
            for x in range(width):
                top += wall
                top += wall if grid[y][x]._walls & 0x1 else OPEN
            top += wall
            lines.append(top)

            # ligne du milieu (murs Ouest/Est + intérieur)
            mid = ''
            for x in range(width):
                mid += wall if grid[y][x]._walls & 0x8 else OPEN
                # choisir la couleur de l'intérieur
                if (x, y) == self.maze.config.entry:
                    mid += ENTRY
                elif (x, y) == self.maze.config.exit_:
                    mid += EXIT
                elif (x, y) in path_set:
                    mid += PATH
                elif (x, y) in self.maze.pattern_42:
                    mid += P42
                else:
                    mid += OPEN
            mid += wall  # bord droit
            lines.append(mid)

        bottom = wall * (width * 2 + 1)
        lines.append(bottom)
        return '\n'.join(lines)

    def display(self) -> None:
        while True:
            print("\033[2J\033[H", end="")  # efface l'écran
            print(self.render())
            print("=== A-Maze-ing ===")
            print("[r] Re-générer")
            print("[p] Afficher/Cacher le chemin")
            print("[c] Changer les couleurs")
            print("[q] Quitter")
            choice = input("Choice (1-4): ").strip()

            if choice == 'r':
                if self.maze.config.seed is None:
                    self.maze.config.seed = 0
                self.maze.config.seed += 1
                self.maze.generate()
                self.show_path = False
            elif choice == 'p':
                if self.show_path:
                    self.show_path = False
                elif not self.show_path:
                    self.show_path = True
            elif choice == 'c':
                self._rotate_color()
            elif choice == 'q':
                break
