from ui.button import Button


class MainMenu:
    def __init__(self, gfx):
        """Initialize the main menu."""
        self.gfx = gfx
        self.buttons: list[Button] = []
        self._load_assets()

    def _load_assets(self) -> None:
        """Load all main-menu sprites."""
        self.gfx.load_sprite("pacman_title", "../assets/main-menu/pac-man_title.png")
        self.gfx.load_sprite("made_by_sign", "../assets/main-menu/made_by_sign_fixed.png")
        self.gfx.load_sprite("start", "../assets/main-menu/start.png")
        self.gfx.load_sprite("high_scorers", "../assets/main-menu/high_scorers.png")
        self.gfx.load_sprite("settings", "../assets/main-menu/settings.png")
        self.gfx.load_sprite("exit", "../assets/main-menu/exit.png")

    def _center_x(self, sprite_name: str) -> int:
        """Return the X coordinate needed to center a sprite."""
        width, _ = self.gfx.sprite_size(sprite_name)
        return (self.gfx.width - width) // 2

    def draw(self) -> None:
        """Draw the complete main menu."""
        self.buttons.clear()
        self._draw_title()
        self._draw_buttons()

    def _draw_title(self) -> None:
        """Draw the title and credits."""
        title_width, title_height = self.gfx.sprite_size("pacman_title")

        title_x = (self.gfx.width - title_width) // 2
        title_y = int(self.gfx.height * 0.08)

        self.gfx.sprite("pacman_title", title_x, title_y)

        credits_width, credits_height = self.gfx.sprite_size("made_by_sign")

        credits_x = (self.gfx.width - credits_width) // 2
        credits_y = title_y + title_height - 20

        self.gfx.sprite("made_by_sign", credits_x, credits_y)
        self._button_start_y = credits_y + credits_height + 20

    def _draw_buttons(self) -> None:
        """Draw all main-menu buttons."""
        width = 400
        height = 70
        gap = 40

        x = (self.gfx.width - width) // 2
        y = self._button_start_y

        self._add_button(x, y, width, height, 0xFFD700, "start", "start_game")
        y += height + gap

        self._add_button(x, y, width, height, 0x00A8FF, "high_scorers", "highscores")
        y += height + gap

        self._add_button(x, y, width, height, 0x32CD32, "settings", "settings")
        y += height + gap

        self._add_button(x, y, width, height, 0xFF4444, "exit", "exit")

    def _add_button(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: int,
        sprite: str,
        action: str) -> None:
        """Draw a menu button and register its hitbox."""
        
        self.gfx.rect(x, y, width, height, color, fill=True)
        self.gfx.sprite(sprite, x, y)
        self.buttons.append(Button(x, y, width, height, action))

    def handle_mouse(self, x: int, y: int) -> str | None:
        """Return the action associated with a clicked button."""
        for button in self.buttons:
            if button.contains(x, y):
                return button.action

        return None