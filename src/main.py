import time
from screens.main_menu import MainMenu
from screens.mlx_class import MlxClass
from screens.game_screen import GameScreen
from screens.constants import *
from config import Config


frame_duration = 1.0 / FPS
last_time = time.perf_counter()
mlx_class = MlxClass("Pacman", 1920, 1080)
menu = MainMenu(mlx_class)
game_screen = GameScreen(15, 15, 42, mlx_class)
current_screen = "menu"
path = "src/config.json"
config = Config.start(path)


def loop(param) -> None:
    global last_time
    start_time = time.perf_counter()
    if current_screen == "menu":
        menu.on_motion()
        menu.render()
    elif current_screen == "game" and game_screen is not None:
        game_screen.render()
    elapsed_time = time.perf_counter() - start_time
    sleep_time = frame_duration - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)
    current_time = time.perf_counter()
    total_frame_time = current_time - last_time
    last_time = current_time
    actual_fps = 1.0 / total_frame_time
    


def on_mouse(button: int, x: int, y: int, param) -> None:
    global current_screen
    if button != 1 or current_screen != "menu":
        return
    action = menu.handle_mouse(x, y)
    if action == "exit":
        mlx_class.stop()
    elif action == "start_game" and game_screen is not None:
        game_screen.start_timer()
        current_screen = "game"


def on_key(key: int, param) -> None:
    if key == ESC:
        mlx_class.stop()
    elif current_screen == "game" and game_screen is not None:
        game_screen.handle_key(key)


def on_close(param) -> None:
    mlx_class.stop()


mlx_class.mlx.mlx_mouse_hook(mlx_class.win, on_mouse, None)
mlx_class.mlx.mlx_key_hook(mlx_class.win, on_key, None)
mlx_class.mlx.mlx_loop_hook(mlx_class.mlx_ptr, loop, None)
mlx_class.mlx.mlx_hook(mlx_class.win, 33, 0, on_close, None)
mlx_class.mlx.mlx_loop(mlx_class.mlx_ptr)