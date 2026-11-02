"""Pac-Man entry point: screen flow, levels and MLX hooks.

Usage: python3 pac-man.py <config.json>
"""
import sys
import time
from typing import Any
from config import Config
from highscores import Highscores
from screens.constants import ESC, FPS, HEIGHT, WIDTH, WINDOW_CLOSE_EVENT
from screens.end_screen import EndScreen
from screens.game_screen import GameScreen
from screens.highscores_screen import HighscoresScreen
from screens.instructions_screen import InstructionsScreen
from screens.main_menu import MainMenu
from screens.mlx_class import MlxClass
from screens.pause_screen import PauseScreen
from screens.text import TextDrawer



frame_duration = 1.0 / FPS
last_time = time.perf_counter()
config: Config
highscores: Highscores
mlx_class: MlxClass | None = None
text: TextDrawer
menu: MainMenu
pause_screen: PauseScreen
end_screen: EndScreen
highscores_screen: HighscoresScreen
instructions_screen: InstructionsScreen

# Game state
current_screen = "menu"
# to redraw static screens
redraw = True 
current_level = 0
game_screen: GameScreen | None = None


def switch_screen(name: str) -> None:
    """Change the current screen and  redraw."""
    global current_screen, redraw
    current_screen = name
    redraw = True


def create_level(level_index: int, score: int = 0, lives: int | None = None) -> GameScreen | None:
    """
    Build a level from the config
    """
    assert mlx_class is not None
    try:
        level = GameScreen(mlx_class, config, level_index, score, lives)
    except Exception as error:
        print(f"Error: cannot create level {level_index + 1}: {error}",
              file=sys.stderr)
        return None
    level.start_timer()
    return level


def close_game() -> None:
    global game_screen
    if game_screen is not None:
        game_screen.destroy()
        game_screen = None


def start_new_game() -> None:
    """Start from level 1 with the config lives and a score of 0."""
    global game_screen, current_level
    close_game()
    current_level = 0
    game_screen = create_level(0)
    if game_screen is not None:
        switch_screen("game")


def end_game(won: bool) -> None:
    """Show the victory / game over screen with the final score."""
    score = game_screen.current_score if game_screen is not None else 0
    close_game()
    end_screen.open(won, score)
    switch_screen("end")


def next_level() -> None:
    """Go to the next level, or win the game after the last one."""
    global game_screen, current_level
    if game_screen is None:
        return
    score = game_screen.current_score
    lives = game_screen.pacman.lives
    current_level += 1
    if current_level >= len(config.game_settings.levels):
        end_game(won=True)
        return
    close_game()
    game_screen = create_level(current_level, score, lives)


def update_game() -> None:
    """ start the game """
    if game_screen is None:
        switch_screen("menu")
        return
    game_screen.render()
    if game_screen.level_won:
        next_level()
    elif game_screen.game_over:
        end_game(won=False)


def loop(param: Any) -> None:
    """mlx main loop"""
    global last_time, redraw
    start_time = time.perf_counter()
    if current_screen == "menu":
        menu.on_motion()
        menu.render()
    elif current_screen == "game":
        update_game()
    elif redraw:
        if current_screen == "pause":
            pause_screen.render()
        elif current_screen == "end":
            end_screen.render()
        elif current_screen == "highscores":
            highscores_screen.render()
        elif current_screen == "instructions":
            instructions_screen.render()
        redraw = False
    elapsed_time = time.perf_counter() - start_time
    sleep_time = frame_duration - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)
    last_time = time.perf_counter()


def on_mouse(button: int, x: int, y: int, param: Any) -> None:
    """Handle clicks on the main menu buttons."""
    if button != 1 or current_screen != "menu":
        return
    action = menu.handle_mouse(x, y)
    if action == "exit":
        mlx_class.mlx.mlx_loop_exit(mlx_class.mlx_ptr)
    elif action == "start_game":
        start_new_game()
    elif action == "highscores":
        switch_screen("highscores")
    elif action == "instructions":
        switch_screen("instructions")


def on_key(key: int, param: Any) -> None:
    """Send the key to the current screen."""
    global redraw
    if current_screen == "menu":
        if key == ESC:
            mlx_class.mlx.mlx_loop_exit(mlx_class.mlx_ptr)
    elif current_screen == "game" and game_screen is not None:
        if key in (ESC, ord("p")):
            game_screen.pause()
            pause_screen.reset()
            switch_screen("pause")
        else:
            game_screen.handle_key(key)
    elif current_screen == "pause":
        action = pause_screen.handle_key(key)
        if action == "resume" and game_screen is not None:
            game_screen.resume()
            switch_screen("game")
        elif action == "menu":
            close_game()
            switch_screen("menu")
        redraw = True
    elif current_screen == "end":
        action = end_screen.handle_key(key)
        if action == "save":
            highscores.add(end_screen.name, end_screen.score)
            switch_screen("menu")
        elif action == "skip":
            switch_screen("menu")
        redraw = True
    elif current_screen == "highscores":
        if highscores_screen.handle_key(key) == "menu":
            switch_screen("menu")
    elif current_screen == "instructions":
        if instructions_screen.handle_key(key) == "menu":
            switch_screen("menu")


def on_close(param: Any) -> None:
    """Quit when the window is closed."""
    mlx_class.mlx.mlx_loop_exit(mlx_class.mlx_ptr)


def main(argv: list[str]) -> int:
    """Load the config, open the window and run the game loop."""
    global config, highscores, mlx_class, text, menu
    global pause_screen, end_screen, highscores_screen, instructions_screen

    if len(argv) != 1:
        print("Usage: python3 src/main.py  <config.json>")
        return 1
    try:
        config = Config.start(argv[0])
        highscores = Highscores(config.highscore_filename)
        window = MlxClass("Pac-Man", WIDTH, HEIGHT)
        mlx_class = window
        text = TextDrawer(window)
        menu = MainMenu(window)
        pause_screen = PauseScreen(window, text)
        end_screen = EndScreen(window, text)
        highscores_screen = HighscoresScreen(window, text, highscores)
        instructions_screen = InstructionsScreen(window, text)

        mlx = window.mlx
        mlx.mlx_mouse_hook(window.win, on_mouse, None)
        mlx.mlx_key_hook(window.win, on_key, None)
        mlx.mlx_loop_hook(window.mlx_ptr, loop, None)
        mlx.mlx_hook(window.win, WINDOW_CLOSE_EVENT, 0, on_close, None)
        mlx.mlx_loop(window.mlx_ptr)
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
