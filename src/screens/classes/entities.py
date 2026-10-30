import time
from screens.constants import *
from screens.mlx_class import MlxClass


class Pacman:
    """Pac-Man: position, movement, animation and drawing."""

    def __init__(self, mlx_class: MlxClass, game_screen: "GameScreen"):
        self.mlx_class = mlx_class
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.game_screen = game_screen

        self.size = max(1, game_screen.cell_size - 6)
        self.sprites = {"up": [], "down": [], "left": [], "right": []}

        self.pacman_x, self.pacman_y = self.pacman_start()
        self.pacman_direction = "left"
        self.wanted_direction = "left"
        self.pacman_frame = 0
        self.pacman_frame_timer = 0
        self.pacman_move_timer = 0
        self.power_up_end_time = 0
        self.powerup_active = False
        self.lives = 3
        self.load_assets()

    def load_assets(self):
        """Load every frame and scale it once to the cell size."""
        for d in ("up", "down", "left", "right"):
            for i in (1, 2, 3):
                img, w, h = self.mlx.mlx_png_file_to_image(
                    self.mlx_ptr, f"assets/pacman-art/pacman-{d}/{d}_{i}.png")
                self.sprites[d].append(
                    self.game_screen.scale_image(img, w, h, self.size, self.size))

    def activate_power_up(self, ghosts):
        """Make all ghosts edible for a short time."""
        self.power_up_end_time = time.monotonic() + POWER_UP_DURATION
        self.powerup_active = True
        for ghost in ghosts:
            ghost.edible = not ghost.eaten

    def update_power_up(self, ghosts):
        """Update power up timer and revert ghosts when expired."""
        if self.powerup_active and time.monotonic() >= self.power_up_end_time:
            self.powerup_active = False
            self.power_up_end_time = 0
            for ghost in ghosts:
                ghost.edible = False

    def lose_life(self, ghosts):
        """Pac-Man loses a life and respawns."""
        self.lives -= 1
        self.powerup_active = False
        self.power_up_end_time = 0
        if self.lives <= 0:
            self.game_screen.game_over = True
            return
        self.pacman_x, self.pacman_y = self.pacman_start()
        self.pacman_direction = "left"
        self.wanted_direction = "left"
        self.pacman_move_timer = 0
        for ghost in ghosts:
            ghost.reset_ghost_position()
            ghost.edible = False
            ghost.eaten = False
            ghost.ghost_respawn_time = 0
            ghost.move_timer = 0

    def is_walkable(self, x, y):
        """Check if possible to acces a cell"""
        if x < 0 or x >= self.game_screen.maze_width :
            return False
        if y < 0 or y >= self.game_screen.maze_height:
            return False
        # 15
        val = self.game_screen.maze_grid[y][x]
        if isinstance(val, str):
            val = int(val, 16)
        if val == 15:
            return False
        return True

    def pacman_start(self):
        """Find a walkable cell close to the center."""
        center_x = self.game_screen.maze_width // 2
        center_y = self.game_screen.maze_height // 2

        # Start at the center and expand outward.
        for radius in range(max(self.game_screen.maze_height, self.game_screen.maze_width )):
            for y in range(
                center_y - radius,
                center_y + radius + 1
            ):
                for x in range(
                    center_x - radius,
                    center_x + radius + 1
                ):
                    if self.is_walkable(x, y):
                        return x, y
    def can_move(self, direction):
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

        x = self.pacman_x
        y = self.pacman_y
        new_x = x + dx
        new_y = y + dy

        if not self.is_walkable(new_x, new_y):
            return False

        cell = self.game_screen.maze_grid[y][x]
        if direction == "up" and cell & 1:
            return False
        if direction == "right" and cell & 2:
            return False
        if direction == "down" and cell & 4:
            return False
        if direction == "left" and cell & 8:
            return False

        return True

    def move_pacman(self, direction):
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

        if not self.can_move(direction):
            return False

        self.pacman_x += dx
        self.pacman_y += dy

        self.pacman_direction = direction
        return True

    def update_pacman(self):
        """Update movement"""

        self.pacman_move_timer += 1

        if self.pacman_move_timer < PACMAN_SPEED:
            return
        self.pacman_move_timer = 0
        if self.can_move(self.wanted_direction):
            self.move_pacman(self.wanted_direction)
        elif self.can_move(self.pacman_direction):
            self.move_pacman(self.pacman_direction)

        self.game_screen.dots.eat(self.pacman_x, self.pacman_y)

    def update_pacman_animation(self):
        """Change Pac-Man's animation frame."""

        self.pacman_frame_timer += 1
        if self.pacman_frame_timer >= PACMAN_FRAME_TIMER:
            self.pacman_frame_timer = 0
            self.pacman_frame += 1
            if self.pacman_frame >= 3:
                self.pacman_frame = 0

    def draw(self):
        margin = (self.game_screen.cell_size - self.size) // 2
        px = self.game_screen.offset_x + self.pacman_x * self.game_screen.cell_size + margin
        py = self.game_screen.offset_y + self.pacman_y * self.game_screen.cell_size + margin
        img = self.sprites[self.pacman_direction][self.pacman_frame]
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, px, py)
        self.update_pacman_animation()

    def handle_key(self, key):
        if key in (65362, ord("w")):
            self.wanted_direction = "up"

        elif key in (65364, ord("s")):
            self.wanted_direction = "down"

        elif key in (65361, ord("a")):
            self.wanted_direction = "left"

        elif key in (65363, ord("d")):
            self.wanted_direction = "right"


class Pacgums:
    """All the pacgums (dots) and super pacgums of the maze."""

    def __init__(self, screen: "Gamescreen", pacman):
        self.pacman = pacman
        self.game_screen = screen
        self.mlx_class = self.game_screen.mlx_class
        self.dots = set()
        self.super_pacgums = set()
        self.load_assets()
        self.create()
        self.build_dots_image()

    def create(self):
        """create the pacgums and the super pacgums."""
        self.create_dots()
        self.create_super_pacgums()

    def create_dots(self):
        """create a pacgums"""
        for y in range(self.game_screen.maze_height):
            for x in range(self.game_screen.maze_width):
                if self.pacman.is_walkable(x, y):
                    self.dots.add((x, y))

        # no dot under pacman
        self.dots.discard((self.pacman.pacman_x, self.pacman.pacman_y))

    def create_super_pacgums(self):
        """create super pacgums"""
        corners = [
                (0, 0),                                           # Top-left
                (self.game_screen.maze_width - 1, 0),                       # Top-right
                (0, self.game_screen.maze_height - 1),                      # Bottom-left
                (self.game_screen.maze_width - 1, self.game_screen.maze_height - 1)   # Bottom-right
            ]

        for position in corners:
            self.super_pacgums.add(position)
            self.dots.discard(position)

    def load_assets(self):
        """Load the pacgum sprites and remember their sizes."""
        self.pacgum = self.mlx_class.mlx.mlx_png_file_to_image(self.mlx_class.mlx_ptr, "assets/pacman-art/other/dot.png")
        self.super_pacgum = self.mlx_class.mlx.mlx_png_file_to_image(self.mlx_class.mlx_ptr, "assets/pacman-art/other/super_pacgum.png")

    def build_dots_image(self):
        """Render all dots into a single cached image the size of the maze."""
        w = self.game_screen.maze_width * self.game_screen.cell_size
        h = self.game_screen.maze_height * self.game_screen.cell_size
        self.dots_img = self.mlx_class.mlx.mlx_new_image(self.mlx_class.mlx_ptr, w, h)
        self.redraw_dots_image()

    def redraw_dots_image(self):
        """Re-render all remaining dots into the cached image."""
        data, bpp, line_size, _ = self.mlx_class.mlx.mlx_get_data_addr(self.dots_img)
        bypp = bpp // 8

        # Fill with transparent (or path color) background
        bg = 0x00000000.to_bytes(bypp, "little")
        pix_w = self.game_screen.maze_width * self.game_screen.cell_size
        pix_h = self.game_screen.maze_height * self.game_screen.cell_size
        for yy in range(pix_h):
            off = yy * line_size
            data[off:off + pix_w * bypp] = bg * pix_w

        # Draw each dot
        for x, y in self.dots:
            self.draw_dot_to_image(data, line_size, bypp, x, y, self.pacgum)
        for x, y in self.super_pacgums:
            self.draw_dot_to_image(data, line_size, bypp, x, y, self.super_pacgum)

    def draw_dot_to_image(self, data, line_size, bypp, cell_x, cell_y, dot_img):
        """Draw a single dot sprite into the cached image at the given cell."""
        img, w, h = dot_img
        src_data, src_bpp, src_ls, _ = self.mlx_class.mlx.mlx_get_data_addr(img)
        src_bypp = src_bpp // 8

        # Center the dot in the cell
        px = cell_x * self.game_screen.cell_size + (self.game_screen.cell_size - w) // 2
        py = cell_y * self.game_screen.cell_size + (self.game_screen.cell_size - h) // 2

        for yy in range(h):
            for xx in range(w):
                s = yy * src_ls + xx * src_bypp
                d = (py + yy) * line_size + (px + xx) * bypp
                data[d:d + bypp] = src_data[s:s + bypp]

    def eat(self, x, y):
        """Eat the gums at this cell."""
        if (x, y) in self.dots:
            self.dots.discard((x, y))
            self.redraw_dots_image()
            self.game_screen.add_score(POINTS_PER_PACGUM)
        if (x, y) in self.super_pacgums:
            self.super_pacgums.discard((x, y))
            self.redraw_dots_image()
            self.game_screen.add_score(POINTS_PER_SUPERPACGUM)
            # Activate power-up!
            self.pacman.activate_power_up(self.game_screen.ghosts)

    def draw(self):
        """Draw the pacgums, then the super pacgums."""
        self.mlx_class.mlx.mlx_put_image_to_window(self.mlx_class.mlx_ptr, self.mlx_class.win, self.dots_img, self.game_screen.offset_x, self.game_screen.offset_y)

class Ghost:
    def __init__(self, name, x, y, mlx_class: MlxClass, game_screen: "GameScreen"):
        self.mlx_class = mlx_class
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.game_screen = game_screen
        self.size = max(1, game_screen.cell_size - 6)

        self.name = name
        self.x = x
        self.y = y
        self.original_x =x
        self.original_y = y
        self.edible = False
        self.eaten = False
        self.sprite_width = 0
        self.sprite_height = 0
        self.sprites = {}
        self.ai = None  # Will be set by GameScreen
        self.move_timer = 0
        self.ghost_respawn_time = 0
        self.speed = GHOST_SPEED
        img, w, h = self.mlx.mlx_png_file_to_image(self.mlx_ptr, "assets/pacman-art/ghosts/blue_ghost.png")
        self.sprites["blue_ghost"] = (self.game_screen.scale_image(img, w, h, self.size, self.size), w, h)

    def load_assets(self):
        img, w, h = self.mlx.mlx_png_file_to_image(self.mlx_ptr, f"assets/pacman-art/ghosts/{self.name}.png")
        self.sprites[self.name] = (self.game_screen.scale_image(img, w, h, self.size, self.size), w, h)

    def reset_ghost_position(self):
        self.x = self.original_x
        self.y = self.original_y

    def eat_ghost(self):
        """Pac-Man eats an edible ghost."""
        if self.eaten or not self.edible:
            return False
        self.eaten = True
        self.edible = False
        self.reset_ghost_position()
        self.ghost_respawn_time = time.monotonic() + GHOST_RESPAWN_DELAY
        return True

    def update_ghost_respawns(self):
        """Update ghost respawn timers and bring them back."""
        if self.eaten and time.monotonic() >= self.ghost_respawn_time:
            self.eaten = False
            self.ghost_respawn_time = 0
            # A ghost returning during a power-up is still frightened.
            self.edible = False

    def update(self):
        self.update_ghost_respawns()
        if self.eaten:
            return
        # self.edible = self.game_screen.pacman.powerup_active
        self.move_timer += 1
        if self.move_timer < self.speed:
            return
        self.move_timer = 0

        ###### rmove this if u want to test

        if self.ai:
            next_move = self.ai.get_next_move()
            if next_move:
                self.x, self.y = next_move


    def draw(self):
        if self.edible:
            sprite_name = "blue_ghost"
        else:
            sprite_name = self.name
        margin = (self.game_screen.cell_size - self.size) // 2
        px = ((self.game_screen.offset_x + self.x * self.game_screen.cell_size) + (margin))
        py = ((self.game_screen.offset_y + self.y * self.game_screen.cell_size) + (margin))
        img, w, h = self.sprites[sprite_name]
        if not self.eaten and self.ghost_respawn_time == 0:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, px, py)
