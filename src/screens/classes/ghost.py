from time import time
from screens.constants import GHOST_RESPAWN_DELAY

class Ghost:
    """A ghost: position, state and drawing."""

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.original_x =x
        self.original_y = y
        self.edible = False
        self.eaten = False
        self.sprite_width = 0
        self.sprite_height = 0
        # name: timestamp
        self.ghost_respawn_time = 0

    @staticmethod
    def load_assets(gfx):
        """Load the ghost sprites (shared by all ghosts)."""
        gfx.load_sprite("blinky", "../assets/pacman-art/ghosts/blinky.png")
        gfx.load_sprite("pinky", "../assets/pacman-art/ghosts/pinky.png")
        gfx.load_sprite("inky", "../assets/pacman-art/ghosts/inky.png")
        gfx.load_sprite("clyde", "../assets/pacman-art/ghosts/clyde.png")
        gfx.load_sprite("blue_ghost", "../assets/pacman-art/ghosts/blue_ghost.png")
        

    def draw(self, gfx, screen):
        """Draw this ghost."""
        if self.edible:
            sprite_name = "blue_ghost"
        else:
            sprite_name = self.name
        px = ((screen.offset_x + self.x * screen.cell_size) + screen.cell_size // 2)
        py = ((screen.offset_y + self.y * screen.cell_size) + screen.cell_size // 2)

        width, height = gfx.sprite_size(sprite_name)
        gfx.sprite(sprite_name, px - width // 2, py - height // 2)

    def reset_ghost_position(self):
        self.x = self.original_x
        self.y = self.original_y


    def eat_ghost(self):
        """Pac-Man eats an edible ghost."""
        self.eaten = True
        self.edible = False
        self.reset_ghost_position()
        self.ghost_respawn_time = time() + GHOST_RESPAWN_DELAY

    def update_ghost_respawns(self):
        """Update ghost respawn timers and bring them back."""
        if self.ghost_respawn_time == 0:  # Add this check
            return
        current_time = time()
        if current_time >= self.ghost_respawn_time:
            self.eaten = False
            self.ghost_respawn_time = 0
