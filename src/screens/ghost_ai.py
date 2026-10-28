from screens.classes.entities import Ghost, Pacman
from collections import deque

class GhostAI:
    """Decide the target and movement strategy for a ghost."""

    def __init__(self, ghost: Ghost, pacman: Pacman,
                  screen: "GameScreen", blinky: Ghost | None = None) -> None:
        self.ghost = ghost
        self.pacman = pacman
        self.screen = screen
        self.blinky = blinky

    def get_target(self) -> tuple[int, int]:
        """Return the target position for the ghost."""
        # Define home corners for scared state / Clyde retreat
        corners = {
            "blinky": (self.screen.maze_width - 1, 0),
            "pinky": (0, 0),
            "inky": (self.screen.maze_width - 1, self.screen.maze_height - 1),
            "clyde": (0, self.screen.maze_height - 1),
        }
        # 1. Scared / Edible State
        if self.ghost.edible:
            return corners.get(self.ghost.name, (0, 0))
        dir_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = dir_map.get(self.pacman.pacman_direction, (0, 0))
        if self.ghost.name == "blinky":
            return (self.pacman.pacman_x, self.pacman.pacman_y)
        if self.ghost.name == "pinky":
            return (self.pacman.pacman_x + dx * 4, self.pacman.pacman_y + dy * 4)
        if self.ghost.name == "inky":
            if not self.blinky:
                return (self.pacman.pacman_x, self.pacman.pacman_y)
            two_ahead_x = self.pacman.pacman_x + dx * 2
            two_ahead_y = self.pacman.pacman_y + dy * 2
            vec_x = two_ahead_x - self.blinky.x
            vec_y = two_ahead_y - self.blinky.y
            return (self.blinky.x + vec_x * 2, self.blinky.y + vec_y * 2)
        # 5. Clyde
        if self.ghost.name == "clyde":
            dist = abs(self.ghost.x - self.pacman.pacman_x) + abs(self.ghost.y - self.pacman.pacman_y)
            if dist > 8:
                return (self.pacman.pacman_x, self.pacman.pacman_y)
            return corners["clyde"]
        return (self.pacman.pacman_x, self.pacman.pacman_y)

    def _find_short_path(self, start: tuple[int, int]) -> list[tuple[int, int]]:
        moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        goal = self.get_target()
        queue = deque([start])
        visited = {start}
        parent = {}
        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
        if goal not in visited:
            return []
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path

    def get_next_move(self) -> tuple[int, int] | None:
        path = self._find_short_path((self.ghost.x, self.ghost.y))
        if path:
            return path[0]  # Next (x, y) tile to step on
        return None