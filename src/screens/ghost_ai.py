from .classes.entities import Ghost, Pacman
from collections import deque
from .constants import N, S, E, W
import random


class GhostAI:
    """Decide the target and movement strategy for a ghost."""

    def __init__(
        self,
        ghost: Ghost,
        pacman: Pacman,
        screen: "GameScreen",
        blinky: Ghost | None = None,
    ) -> None:
        self.ghost = ghost
        self.pacman = pacman
        self.screen = screen
        self.blinky = blinky

    def _get_random_valid_tile(self) -> tuple[int, int]:
        """Return a random walkable tile inside the maze."""
        while True:
            rx = random.randint(0, self.screen.maze_width - 1)
            ry = random.randint(0, self.screen.maze_height - 1)
            cell = self.screen.maze_grid[ry][rx]
            if isinstance(cell, str):
                cell = int(cell, 16)
            # If not completely blocked on all 4 sides (15 == N|S|E|W)
            if cell != 15:
                return (rx, ry)

    def _get_flee_target(self) -> tuple[int, int]:
        """Calculate a target in the opposite direction of Pac-Man (Scared Mode)."""
        flee_x = self.ghost.x + (self.ghost.x - self.pacman.pacman_x) * 2
        flee_y = self.ghost.y + (self.ghost.y - self.pacman.pacman_y) * 2
        target_x = max(0, min(self.screen.maze_width - 1, flee_x))
        target_y = max(0, min(self.screen.maze_height - 1, flee_y))
        # If ghost is directly on Pac-Man, pick a random tile to scatter
        if (target_x, target_y) == (self.ghost.x, self.ghost.y):
            return self._get_random_valid_tile()
        return (target_x, target_y)

    def get_target(self) -> tuple[int, int]:
        """Return the target position for the ghost."""
        # 1. Scared / Edible State: All ghosts flee away from Pac-Man
        if self.ghost.edible:
            return self._get_flee_target()
        dir_map = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        dx, dy = dir_map.get(self.pacman.pacman_direction, (0, 0))
        # 2. Blinky: Always chase Pac-Man directly
        if self.ghost.name == "blinky":
            return (self.pacman.pacman_x, self.pacman.pacman_y)
        # 3. Pinky: Target 4 tiles ahead of Pac-Man
        if self.ghost.name == "pinky":
            target_x = max(
                0, min(self.screen.maze_width - 1, self.pacman.pacman_x + dx * 4)
            )
            target_y = max(
                0, min(self.screen.maze_height - 1, self.pacman.pacman_y + dy * 4)
            )
            return (target_x, target_y)
        # 4. Inky: Pivot vector using Blinky's position
        if self.ghost.name == "inky":
            if not self.blinky:
                return (self.pacman.pacman_x, self.pacman.pacman_y)
            two_ahead_x = self.pacman.pacman_x + dx * 2
            two_ahead_y = self.pacman.pacman_y + dy * 2
            vec_x = two_ahead_x - self.blinky.x
            vec_y = two_ahead_y - self.blinky.y
            target_x = max(
                0, min(self.screen.maze_width - 1, self.blinky.x + vec_x * 2)
            )
            target_y = max(
                0, min(self.screen.maze_height - 1, self.blinky.y + vec_y * 2)
            )
            return (target_x, target_y)
        # 5. Clyde: Chase like Red (Blinky) if > 8 cells away, run away like Scared mode if <= 8 cells
        if self.ghost.name == "clyde":
            dist = abs(self.ghost.x - self.pacman.pacman_x) + abs(
                self.ghost.y - self.pacman.pacman_y
            )
            if dist > 8:
                # Chase like Red (Blinky)
                return (self.pacman.pacman_x, self.pacman.pacman_y)
            else:
                # Run away like Scared mode
                return self._get_flee_target()
        return (self.pacman.pacman_x, self.pacman.pacman_y)

    def _find_short_path(self, start: tuple[int, int]) -> list[tuple[int, int]]:
        moves = [(0, -1, N), (1, 0, E), (0, 1, S), (-1, 0, W)]
        goal = self.get_target()
        queue = deque([(start, [])])
        visited = {start}
        closest_path: list[tuple[int, int]] = []
        min_dist = float("inf")
        while queue:
            (x, y), path = queue.popleft()
            # Track the closest walkable tile to the goal
            dist = abs(x - goal[0]) + abs(y - goal[1])
            if dist < min_dist:
                min_dist = dist
                closest_path = path
            if (x, y) == goal:
                return path
            for dx, dy, wall in moves:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.screen.maze_width and 0 <= ny < self.screen.maze_height):
                    continue
                cell = self.screen.maze_grid[y][x]
                if isinstance(cell, str):
                    cell = int(cell, 16)
                if cell & wall:
                    continue
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        # If goal was unreachable (inside a wall), return the path to the closest walkable tile
        return closest_path

    def get_next_move(self) -> tuple[int, int] | None:
        path = self._find_short_path((self.ghost.x, self.ghost.y))
        if path:
            return path[0]
        # Fallback: keep moving to any open adjacent tile if standing directly on target
        moves = [(0, -1, N), (1, 0, E), (0, 1, S), (-1, 0, W)]
        x, y = self.ghost.x, self.ghost.y
        for dx, dy, wall in moves:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < self.screen.maze_width
                and 0 <= ny < self.screen.maze_height
            ):
                cell = self.screen.maze_grid[y][x]
                if isinstance(cell, str):
                    cell = int(cell, 16)
                if not (cell & wall):
                    return (nx, ny)
        return None
