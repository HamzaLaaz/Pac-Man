class Pacgums:
    """All the pacgums (dots) and super pacgums of the maze."""

    def __init__(self):
        self.dots = set()
        self.super_pacgums = set()
        self.pacgum_width = 0
        self.pacgum_height = 0
        self.super_pacgum_width = 0
        self.super_pacgum_height = 0
        self.power_up_end_time = 0

    def create(self, screen, pacman):
        """create the pacgums and the super pacgums."""
        self.create_dots(screen, pacman)
        self.create_super_pacgums(screen)

    def create_dots(self, screen, pacman):
        """create a pacgums"""
        for y in range(len(screen.maze)):
            for x in range(len(screen.maze[y])):
                if screen.is_walkable(x, y):
                    self.dots.add((x, y))

        # no dot under pacman
        self.dots.discard((pacman.x, pacman.y))

    def create_super_pacgums(self, screen):
        """create super pacgums"""
        corners = [
                (0, 0),                                           # Top-left
                (screen.maze_width - 1, 0),                       # Top-right
                (0, screen.maze_height - 1),                      # Bottom-left
                (screen.maze_width - 1, screen.maze_height - 1)   # Bottom-right
            ]

        for position in corners:
            self.super_pacgums.add(position)
            self.dots.discard(position)

    def load_assets(self, gfx):
        """Load the pacgum sprites and remember their sizes."""
        gfx.load_sprite("pacgum", "../assets/pacman-art/other/dot.png")
        gfx.load_sprite("super_pacgum", "../assets/pacman-art/other/super_pacgum.png")
        self.pacgum_width, self.pacgum_height = gfx.sprite_size("pacgum")
        self.super_pacgum_width, self.super_pacgum_height = gfx.sprite_size("super_pacgum")

    def eat(self, x, y):
        """Eat the gums at this cell."""
        self.dots.discard((x, y))
        self.super_pacgums.discard((x, y))

    def draw(self, gfx, screen):
        """Draw the pacgums, then the super pacgums."""
        self.draw_dots(gfx, screen)
        self.draw_super_pacgums(gfx, screen)

    def draw_dots(self, gfx, screen):
        """draw all remaining pacgums"""

        for x, y in self.dots:
            px = ((screen.offset_x + x * screen.cell_size) + screen.cell_size // 2)
            py = ((screen.offset_y + y * screen.cell_size) + screen.cell_size // 2)
            gfx.sprite("pacgum", px - self.pacgum_width // 2, py - self.pacgum_height // 2)

    def draw_super_pacgums(self, gfx, screen):
        """draw all remaining super pacgums"""
        for x, y in self.super_pacgums:
            px = screen.offset_x + x * screen.cell_size + screen.cell_size // 2
            py = screen.offset_y + y * screen.cell_size + screen.cell_size // 2
            gfx.sprite("super_pacgum", px - self.super_pacgum_width // 2, py - self.super_pacgum_height // 2)