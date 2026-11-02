"""Screen that shows the top 10 highscores."""
from highscores import Highscores

from .constants import ESC, KEY_ENTER, KEY_KP_ENTER, TEXT_YELLOW
from .mlx_class import MlxClass
from .text import TextDrawer


class HighscoresScreen:
    """Display the top 10 players and their scores."""

    def __init__(self, mlx_class: MlxClass, text: TextDrawer,
                 highscores: Highscores) -> None:
        """Keep references to the window, text drawer and table."""
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.text = text
        self.highscores = highscores
        self.background = self.mlx.mlx_xpm_file_to_image(
            self.mlx_ptr, "assets/main-menu/background.xpm")

    def render(self) -> None:
        """Draw the highscore table."""
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win,
                                         img, 0, 0)
        y = 80
        y += self.text.draw_centered("HIGHSCORES", y, 6, TEXT_YELLOW) + 60
        if not self.highscores.entries:
            self.text.draw_centered("No highscores yet", y, 3)
        for rank, (name, score) in enumerate(self.highscores.entries, 1):
            line = f"{rank:>2}. {name:<10}  {score:>8}"
            y += self.text.draw_centered(line, y, 3) + 15
        self.text.draw_centered("Press ENTER or ESC to go back", 950, 2)

    def handle_key(self, key: int) -> str | None:
        """Return "menu" when the player leaves the screen."""
        if key in (ESC, KEY_ENTER, KEY_KP_ENTER):
            return "menu"
        return None
