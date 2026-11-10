"""Game over / victory screen with name entry for the highscores."""
from src.highscores import Highscores

from .constants import (ESC, KEY_BACKSPACE, KEY_ENTER, KEY_KP_ENTER,
                        TEXT_YELLOW)
from .mlx_class import MlxClass
from .text import TextDrawer


class EndScreen:
    """Show the final score and let the player type a name."""

    def __init__(self, mlx_class: MlxClass, text: TextDrawer) -> None:
        """Keep references to the window and text drawer."""
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.text = text
        self.won = False
        self.score = 0
        self.name = ""
        self.background = self.mlx.mlx_xpm_file_to_image(
            self.mlx_ptr, "assets/main-menu/background.xpm")

    def open(self, won: bool, score: int) -> None:
        """Prepare the screen for a finished game."""
        self.won = won
        self.score = score
        self.name = ""

    def render(self) -> None:
        """Draw the result, the final score and the name being typed."""
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win,
                                         img, 0, 0)
        y = 200
        title = "YOU WIN!" if self.won else "GAME OVER"
        y += self.text.draw_centered(title, y, 7, TEXT_YELLOW) + 30
        if self.won:
            y += self.text.draw_centered(
                "Congratulations, all levels completed!", y, 3) + 30
        y += self.text.draw_centered(f"Final score: {self.score}",
                                     y, 4) + 80
        y += self.text.draw_centered("Enter your name:", y, 3) + 20
        shown = self.name + "_" * (10 - len(self.name))
        self.text.draw_centered(f"[{shown}]", y, 4, TEXT_YELLOW)
        self.text.draw_centered(
            "Letters, digits, spaces (max 10)  -  ENTER to save, "
            "ESC to skip", 950, 2)

    def handle_key(self, key: int) -> str | None:
        """Edit the name; return "save" or "skip" when done."""
        if key in (KEY_ENTER, KEY_KP_ENTER):
            return "save"
        if key == ESC:
            return "skip"
        if key == KEY_BACKSPACE:
            self.name = self.name[:-1]
        elif 0 < key < 0x110000 and len(self.name) < 10:
            char = chr(key)
            if Highscores.is_valid_char(char) and not (
                    char == " " and not self.name):
                self.name += char.upper()
        return None
