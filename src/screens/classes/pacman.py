from time import time
from screens import constants
from screens.constants import POWER_UP_DURATION


class Pacman:
    """Pac-Man: position, movement, animation and drawing."""

    def __init__(self, x, y, lives):
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.lives = lives
        self.direction = "left"
        self.wanted_direction = "left"
        self.frame = 0
        self.frame_timer = 0
        self.move_timer = 0
        self.power_up_end_time = 0 
        self.game_over = False
        self.sprites = {
            "up": [],
            "down": [],
            "left": [],
            "right": []}

    def activate_power_up(self, ghosts):
        """Make all ghosts edible for a short time."""
        self.power_up_end_time = time() + POWER_UP_DURATION
        
        for ghost in ghosts:
            if not ghost.eaten:
                ghost.edible = True

    def update_power_up(self, ghosts):
        """Update power up timer and revert ghosts when expired."""
        if self.power_up_end_time == 0:
            return
        
        if time() >= self.power_up_end_time:
            for ghost in ghosts:
                ghost.edible = False
            self.power_up_end_time = 0

    def lose_life(self, ghosts):
        """Pac-Man loses a life and respawns."""
        self.lives -= 1
        
        if self.lives <= 0:
            self.game_over = True
            return
        
        self.x, self.y = self.original_x, self.original_y
        self.pacman_direction = "left"
        self.wanted_direction = "left"
        
        for ghost in ghosts:
            ghost.reset_ghost_position()
            ghost.edible = False
            ghost.eaten = False
            ghost.ghost_respawn_times = 0
        self.power_up_end_time = 0 

    
    def load_assets(self, gfx):
        """Load Pac-Man animation frames."""
        # up
        gfx.load_sprite("pacman_up_1", "../assets/pacman-art/pacman-up/up_1.png")
        gfx.load_sprite("pacman_up_2", "../assets/pacman-art/pacman-up/up_2.png")
        gfx.load_sprite("pacman_up_3", "../assets/pacman-art/pacman-up/up_3.png")
        self.sprites["up"].append("pacman_up_1")
        self.sprites["up"].append("pacman_up_2")
        self.sprites["up"].append("pacman_up_3")

        # # down
        gfx.load_sprite("pacman_down_1", "../assets/pacman-art/pacman-down/down_1.png")
        gfx.load_sprite("pacman_down_2", "../assets/pacman-art/pacman-down/down_2.png")
        gfx.load_sprite("pacman_down_3", "../assets/pacman-art/pacman-down/down_3.png")
        self.sprites["down"].append("pacman_down_1")
        self.sprites["down"].append("pacman_down_2")
        self.sprites["down"].append("pacman_down_3")

        # # left
        gfx.load_sprite("pacman_left_1", "../assets/pacman-art/pacman-left/left_1.png")
        gfx.load_sprite("pacman_left_2", "../assets/pacman-art/pacman-left/left_2.png")
        gfx.load_sprite("pacman_left_3", "../assets/pacman-art/pacman-left/left_3.png")
        self.sprites["left"].append("pacman_left_1")
        self.sprites["left"].append("pacman_left_2")
        self.sprites["left"].append("pacman_left_3")

        # # right
        gfx.load_sprite("pacman_right_1", "../assets/pacman-art/pacman-right/right_1.png")
        gfx.load_sprite("pacman_right_2", "../assets/pacman-art/pacman-right/right_2.png")
        gfx.load_sprite("pacman_right_3", "../assets/pacman-art/pacman-right/right_3.png")
        self.sprites["right"].append("pacman_right_1")
        self.sprites["right"].append("pacman_right_2")
        self.sprites["right"].append("pacman_right_3")

    def can_move(self, direction, screen):
        """Check whether pacman can move in a direction."""
        dx = 0
        dy = 0

        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1

        x = self.x
        y = self.y
        new_x = x + dx
        new_y = y + dy

        if not screen.is_walkable(new_x, new_y):
            return False
        cell = screen.maze[y][x]
        if direction == "up" and cell & 1:
            return False
        if direction == "right" and cell & 2:
            return False
        if direction == "down" and cell & 4:
            return False
        if direction == "left" and cell & 8:
            return False

        return True

    def move(self, direction, screen):
        """Move Pac-Man in the given direction."""

        dx = 0
        dy = 0

        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1

        if not self.can_move(direction, screen):
            return False

        self.x += dx
        self.y += dy

        self.direction = direction

        return True

    def update(self, screen):
        """Update movement. Returns True if Pac-Man moved to a new cell."""

        self.move_timer += 1

        if self.move_timer < constants.PACMAN_SPEED:
            return False
        self.move_timer = 0
        if self.can_move(self.wanted_direction, screen):
            return self.move(self.wanted_direction, screen)
        elif self.can_move(self.direction, screen):
            return self.move(self.direction, screen)
        return False

    def update_animation(self):
        """Change Pac-Man's animation frame."""

        self.frame_timer += 1
        if self.frame_timer >= constants.PACMAN_FRAME_TIMER:
            self.frame_timer = 0
            self.frame += 1
            if self.frame >= 3:
                self.frame = 0

    def handle_key(self, key):
        """Handle Pac-Man direction input."""
        if key in (65362, ord("w")):
            self.wanted_direction = "up"

        elif key in (65364, ord("s")):
            self.wanted_direction = "down"

        elif key in (65361, ord("a")):
            self.wanted_direction = "left"

        elif key in (65363, ord("d")):
            self.wanted_direction = "right"

    def draw(self, gfx, screen):
        """Draw Pac-Man."""
        sprite_name = self.sprites[self.direction][self.frame]
        px = (screen.offset_x + self.x * screen.cell_size + screen.cell_size // 2)
        py = (screen.offset_y + self.y * screen.cell_size + screen.cell_size // 2)
        width, height = gfx.sprite_size(sprite_name)
        gfx.sprite(sprite_name, px - width // 2, py - height // 2)

    