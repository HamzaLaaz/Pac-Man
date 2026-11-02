"""Screen that explains the controls and rules."""
from .constants import ESC, KEY_ENTER, KEY_KP_ENTER, TEXT_YELLOW
from .mlx_class import MlxClass
from .text import TextDrawer

LINES = [
    ("CONTROLS", True),
    ("Arrows / WASD : move", False),
    ("P or ESC      : pause", False),
    ("", False),
    ("RULES", True),
    ("Eat every pacgum to win the level", False),
    ("Super-pacgums (corners) make ghosts edible", False),
    ("A ghost touching you costs one life", False),
    ("Each level has a time limit", False),
    ("Score and lives are kept between levels", False),
    ("", False),
    ("CHEAT MODE  (C to toggle in game)", True),
    ("N: skip level  I: invincible  F: freeze ghosts", False),
    ("L: extra life  O: fast pacman  T: reset timer", False),
]


class InstructionsScreen:
    """Display the controls, the rules and the cheat keys."""

    def __init__(self, mlx_class: MlxClass, text: TextDrawer) -> None:
        """Keep references to the window and text drawer."""
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.text = text
        self.background = self.mlx.mlx_xpm_file_to_image(
            self.mlx_ptr, "assets/main-menu/background.xpm")

    def render(self) -> None:
        """Draw the instructions."""
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win,
                                         img, 0, 0)
        y = 60
        y += self.text.draw_centered("INSTRUCTIONS", y, 5, TEXT_YELLOW) + 40
        for line, is_title in LINES:
            if not line:
                y += 25
                continue
            color = TEXT_YELLOW if is_title else 0xFFFFFFFF
            y += self.text.draw_centered(line, y, 2, color) + 12
        self.text.draw_centered("Press ENTER or ESC to go back", 980, 2)

    def handle_key(self, key: int) -> str | None:
        """Return "menu" when the player leaves the screen."""
        if key in (ESC, KEY_ENTER, KEY_KP_ENTER):
            return "menu"
        return None
