from src.screens.classes.ghost import Ghost
from src.screens.classes.pacman import Pacman
from collections import deque

class GhostAI:
    """Decide the target and movement strategy for a ghost."""

    def __init__(self, ghost: Ghost, pacman: Pacman) -> None:
        self.ghost = ghost
        self.pacman = pacman

    def get_target(self) -> tuple[int, int]:
        """Return the target position for the ghost."""
        if self.ghost.name == "blinky":
            return (self.pacman.x, self.pacman.y)
        return (self.pacman.x, self.pacman.y)

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
