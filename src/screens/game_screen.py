from mazegenerator import MazeGenerator
from screens import constants


class GameScreen:
    """Handle the gameplay screen and maze rendering."""

    def __init__(self, gfx, width: int =25, height: int =25, seed: int=42):
        self.gfx = gfx
        self.maze_width = width
        self.maze_height = height
        self.seed = seed
        self.maze_generator = MazeGenerator(size=(self.maze_width, self.maze_height), perfect=False, seed = self.seed)
        self.maze = self.maze_generator.maze
        print(self.maze)
        self.maze_copy: bytes | None = None
        # maze vars
        self.cell_size = 0
        self.offset_x = 0
        self.offset_y = 0
        self._calc_maze_dims()


        # pacman vars
        self.pacman_x, self.pacman_y = self.find_spawn_position()
        self.pacman_direction = "left"
        self.wanted_direction = "left"
        self.pacman_frame = 0
        self.pacman_frame_timer = 0
        self.pacman_move_timer = 0
        # Ghost starting positions.
        self.ghosts = [
            {"name": "blinky", "x": 0, "y": 0},
            {"name": "pinky", "x": self.maze_width - 1, "y": 0},
            {"name": "inky", "x": 0, "y": self.maze_height - 1},
            {"name": "clyde", "x": self.maze_width - 1, "y": self.maze_height - 1}]

        # Dots currently present in the maze.
        self.dots = set()
        self.create_dots()

        # load all the assets
        self.load_assets()
        self.pacgum_width, self.pacgum_height = self.gfx.sprite_size("pacgum")

    def _generate_maze(self):
        """Draw the maze once"""
        self.gfx.clear()
        self.draw_maze()
        self.maze_copy = bytes(self.gfx.data)

    def _copy_maze(self):
        """cope the maze into the backbuffer"""
        if self.maze_copy is None:
            self._generate_maze()
        else:
            self.gfx.data[:len(self.maze_copy)] = self.maze_copy

    def load_assets(self):
        """Load all game sprites."""
        # Pac-Man animation frames.
        self.pacman_sprites = {
            "up": [],
            "down": [],
            "left": [],
            "right": []}
        # up
        self.gfx.load_sprite("pacman_up_1", "../assets/pacman-art/pacman-up/up_1.png")
        self.gfx.load_sprite("pacman_up_2", "../assets/pacman-art/pacman-up/up_2.png")
        self.gfx.load_sprite("pacman_up_3", "../assets/pacman-art/pacman-up/up_3.png")
        self.pacman_sprites["up"].append("pacman_up_1")
        self.pacman_sprites["up"].append("pacman_up_2")
        self.pacman_sprites["up"].append("pacman_up_3")

        # # down
        self.gfx.load_sprite("pacman_down_1", "../assets/pacman-art/pacman-down/down_1.png")
        self.gfx.load_sprite("pacman_down_2", "../assets/pacman-art/pacman-down/down_2.png")
        self.gfx.load_sprite("pacman_down_3", "../assets/pacman-art/pacman-down/down_3.png")
        self.pacman_sprites["down"].append("pacman_down_1")
        self.pacman_sprites["down"].append("pacman_down_2")
        self.pacman_sprites["down"].append("pacman_down_3")

        # # left
        self.gfx.load_sprite("pacman_left_1", "../assets/pacman-art/pacman-left/left_1.png")
        self.gfx.load_sprite("pacman_left_2", "../assets/pacman-art/pacman-left/left_2.png")
        self.gfx.load_sprite("pacman_left_3", "../assets/pacman-art/pacman-left/left_3.png")
        self.pacman_sprites["left"].append("pacman_left_1")
        self.pacman_sprites["left"].append("pacman_left_2")
        self.pacman_sprites["left"].append("pacman_left_3")

        # # right
        self.gfx.load_sprite("pacman_right_1", "../assets/pacman-art/pacman-right/right_1.png")
        self.gfx.load_sprite("pacman_right_2", "../assets/pacman-art/pacman-right/right_2.png")
        self.gfx.load_sprite("pacman_right_3", "../assets/pacman-art/pacman-right/right_3.png")
        self.pacman_sprites["right"].append("pacman_right_1")
        self.pacman_sprites["right"].append("pacman_right_2")
        self.pacman_sprites["right"].append("pacman_right_3")

        # # Dots
        self.gfx.load_sprite("pacgum", "../assets/pacman-art/other/dot.png")

        ## Ghosts
        self.gfx.load_sprite("blinky", "../assets/pacman-art/ghosts/blinky.png")
        self.gfx.load_sprite("pinky", "../assets/pacman-art/ghosts/pinky.png")
        self.gfx.load_sprite("inky", "../assets/pacman-art/ghosts/inky.png")
        self.gfx.load_sprite("clyde", "../assets/pacman-art/ghosts/clyde.png")
        self.gfx.load_sprite("blue_ghost", "../assets/pacman-art/ghosts/blue_ghost.png")

    def find_spawn_position(self):
        """Find a walkable cell close to the center."""
        center_x = self.maze_width // 2
        center_y = self.maze_height // 2

        # Start at the center and expand outward.
        for radius in range(max(len(self.maze), len(self.maze[0]))):
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

        raise RuntimeError("Maze has no walkable cell")


    def create_dots(self):
        """Create a dot on every walkable cell."""
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.is_walkable(x, y):
                    self.dots.add((x, y))

        # Don't put a dot under Pac-Man.
        self.dots.discard((self.pacman_x, self.pacman_y))

    def is_walkable(self, x, y):
        """Check if possible to acces a cell"""
        if x < 0 or x >= len(self.maze[0]):
            return False
        if y < 0 or y >= len(self.maze):
            return False
        # 15
        if self.maze[y][x] == 15:
            return False
        return True

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
        cell = self.maze[y][x]
        if direction == "up" and cell & 1:
            return False
        if direction == "right" and cell & 2:
            return False
        if direction == "down" and cell & 4:
            return False
        if direction == "left" and cell & 8:
            return False

        return True

    def update_pacman(self):
        """Update movement"""

        self.pacman_move_timer += 1

        if self.pacman_move_timer < constants.PACMAN_SPEED:
            return
        self.pacman_move_timer = 0
        if self.can_move(self.wanted_direction):
            self.move_pacman(self.wanted_direction)
        elif self.can_move(self.pacman_direction):
            self.move_pacman(self.pacman_direction)

    def draw(self):
        """Draw the complete game screen."""
        self.update_pacman()
        self._copy_maze()
        self._draw_pacman()
        self._draw_dots()
        self._draw_ghosts()
        self.update_pacman_animation()

    def update_pacman_animation(self):
        """Change Pac-Man's animation frame."""

        self.pacman_frame_timer += 1
        if self.pacman_frame_timer >= constants.PACMAN_FRAME_TIMER:
            self.pacman_frame_timer = 0
            self.pacman_frame += 1
            if self.pacman_frame >= 3:
                self.pacman_frame = 0


    def _calc_maze_dims(self):
        """Calculate cell size and maze position."""
        # calculate the space that we can use
        available_width = self.gfx.width - constants.MARGIN * 2
        available_height = self.gfx.height - constants.MARGIN * 2
        print({self.gfx.width}, {self.gfx.height})
        print(f"available width:{available_width}, available height{available_height}")

        cell_width = available_width // self.maze_width
        cell_height = available_height // self.maze_height
        print(f"cell width: {cell_width}, cell height: {cell_height}")

        self.cell_size = min(cell_width, cell_height)
        print(f"cell size: {self.cell_size}")

        maze_pixel_width = (self.maze_width * self.cell_size)
        maze_pixel_height = (self.maze_height * self.cell_size)
        print(f"maze pixel width: {maze_pixel_width}, maze pixel height: {maze_pixel_height}")

        self.offset_x = (self.gfx.width - maze_pixel_width) // 2
        self.offset_y = (self.gfx.height - maze_pixel_height) // 2
        print(f"offset_x: {self.offset_x}, offset_y: {self.offset_y}")

    def draw_maze(self):
        """Draw the maze centered on the screen."""
        print("draw maze")
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                self.draw_cell(x,y)

    def draw_cell(self, x, y):
        value = self.maze[y][x]
        px = self.offset_x + (x * self.cell_size)
        py = self.offset_y + (y * self.cell_size)

        # North wall
        if value & 1:
            self.gfx.line(px, py, px + self.cell_size, py, 0x0000FF, thickness=2)
        # West wall
        if value & 8:
            self.gfx.line(px, py, px, py + self.cell_size, 0x0000FF, thickness=2)
        # East wall
        if x == self.maze_width - 1 and value & 2:
            self.gfx.line(px + self.cell_size, py, px + self.cell_size, py + self.cell_size, 0x0000FF, thickness=2)
        # South wall
        if y == self.maze_height - 1 and value & 4:
            self.gfx.line( px, py + self.cell_size, px + self.cell_size, py + self.cell_size, 0x0000FF, thickness=2)

    def _draw_pacman(self):
        """Draw Pac-Man."""
        sprite_name = self.pacman_sprites[self.pacman_direction][self.pacman_frame]
        px = (self.offset_x + self.pacman_x * self.cell_size + self.cell_size // 2)
        py = (self.offset_y + self.pacman_y * self.cell_size + self.cell_size // 2)
        width, height = self.gfx.sprite_size(sprite_name)
        self.gfx.sprite(sprite_name, px - width // 2, py - height // 2)

    def _draw_dots(self):
        """Draw all remaining dots."""

        for x, y in self.dots:
            px = ((self.offset_x + x * self.cell_size) + self.cell_size // 2)

            py = ((self.offset_y + y * self.cell_size) + self.cell_size // 2)
            self.gfx.sprite("pacgum", px - self.pacgum_width // 2, py - self.pacgum_height // 2)

    def _draw_ghosts(self):
        """Draw all ghosts."""

        for ghost in self.ghosts:
            sprite_name = ghost["name"]
            px = ((self.offset_x + ghost["x"] * self.cell_size) + self.cell_size // 2 )
            py = ((self.offset_y + ghost["y"] * self.cell_size) + self.cell_size // 2)

            width, height = self.gfx.sprite_size(sprite_name)
            self.gfx.sprite(sprite_name, px - width // 2, py - height // 2 )

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

        # Eat the dot.
        self.dots.discard(
            (self.pacman_x, self.pacman_y)
        )

        return True

    def handle_key(self, key):
        if key in (65362, ord("w")):
            self.wanted_direction = "up"

        elif key in (65364, ord("s")):
            self.wanted_direction = "down"

        elif key in (65361, ord("a")):
            self.wanted_direction = "left"

        elif key in (65363, ord("d")):
            self.wanted_direction = "right"
