"""Pause menu: resume the game or go back to the main menu."""
from .constants import (ESC, KEY_DOWN, KEY_ENTER, KEY_KP_ENTER, KEY_UP,
                        TEXT_YELLOW)
from .mlx_class import MlxClass
from .text import TextDrawer

OPTIONS = [("Resume", "resume"), ("Main menu", "menu")]


class PauseScreen:
    """Two-option pause menu controlled with the keyboard."""

    def __init__(self, mlx_class: MlxClass, text: TextDrawer) -> None:
        """Keep references to the window and text drawer."""
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.text = text
        self.selected = 0
        self.background = self.mlx.mlx_xpm_file_to_image(
            self.mlx_ptr, "assets/main-menu/background.xpm")

    def reset(self) -> None:
        """Select "Resume" when the menu opens."""
        self.selected = 0

    def render(self) -> None:
        """Draw the pause menu."""
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win,
                                         img, 0, 0)
        y = 300
        y += self.text.draw_centered("PAUSED", y, 6, TEXT_YELLOW) + 80
        for i, (label, _) in enumerate(OPTIONS):
            selected = i == self.selected
            line = f"> {label} <" if selected else f"  {label}  "
            color = TEXT_YELLOW if selected else 0xFFFFFFFF
            y += self.text.draw_centered(line, y, 4, color) + 30
        self.text.draw_centered("UP/DOWN to choose, ENTER to confirm",
                                900, 2)

    def handle_key(self, key: int) -> str | None:
        """Return "resume" or "menu" when an option is chosen."""
        if key in (KEY_UP, ord("w")):
            self.selected = (self.selected - 1) % len(OPTIONS)
        elif key in (KEY_DOWN, ord("s")):
            self.selected = (self.selected + 1) % len(OPTIONS)
        elif key in (KEY_ENTER, KEY_KP_ENTER):
            return OPTIONS[self.selected][1]
        elif key in (ESC, ord("p")):
            return "resume"
        return None
