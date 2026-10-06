from mlx import Mlx
from screens.game_screen import GameScreen
from graphics.gfx import Gfx
from screens.main_menu import MainMenu


gfx = Gfx(Mlx(), "Pacman")
menu = MainMenu(gfx)
game_screen = GameScreen(gfx)

current_screen = "menu"


def loop() -> int:
    gfx.clear(0x000000)
    if current_screen == "menu":
        menu.draw()
    if current_screen == "game":
        game_screen.draw()

    gfx.render()
    return 0


def on_mouse(button: int, x: int, y: int) -> None:
    global current_screen
    if button != 1:
        return
    action = menu.handle_mouse(x, y)
    if action == "exit":
        gfx.stop()
    elif action == "start_game":
        current_screen = "game"

    elif action == "highscores":
        # Later
        pass

    elif action == "settings":
        # Later
        pass


def on_key(key: int) -> int:
    if key == 65307:
        gfx.stop()
    
    if current_screen == "game":
        game_screen.handle_key(key)
    return 0


gfx.on_loop(loop)
gfx.on_mouse(on_mouse)
gfx.on_key(on_key)
gfx.on_close(gfx.stop)

gfx.run()