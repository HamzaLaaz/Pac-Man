from .constants import *
from .mlx_class import MlxClass
from mazegenerator import MazeGenerator
from .classes.entities import Pacman, Ghost
from .classes.entities import Pacgums
from .ghost_ai import GhostAI
from bdfparser import Font
from .text import TextDrawer
from config import Config
import time


class GameScreen:
    def __init__(self, mlx_class: MlxClass, config: Config, level_index: int = 0,
                 score: int = 0, lives: int | None = None):
        level = config.game_settings.levels[level_index]
        self.maze_width = level.width
        self.maze_height = level.height
        # First level uses the config seed, the next ones are random
        # (MazeGenerator treats seed 0 as "random").
        self.seed = config.game_settings.seed if level_index == 0 else 0
        self.mlx_class = mlx_class
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.x = 0
        self.y = 0
        self.level_index = level_index
        self.level_number = level_index + 1

        # values from the config
        self.max_lives = config.player.lives
        self.points_pacgum = config.score.pacgum
        self.points_super_pacgum = config.score.super_pacgum
        self.points_ghost = config.score.ghost

        # timer
        self.level_duration = config.game_settings.level_max_time
        self.level_start_time = time.monotonic()
        self.last_displayed_second = None

        self.game_over = False
        self.level_won = False
        self.needs_clear = True   # redraw the background on next frame
        self.paused_at = 0.0

        # cheat mode
        self.cheat_mode = False
        self.invincible = False
        self.ghosts_frozen = False

        try:
            self.maze_generator = MazeGenerator(
                size=(self.maze_width, self.maze_height),
                perfect=False, seed=self.seed)
            self.maze_grid = self.maze_generator.maze
        except Exception as error:
            raise RuntimeError(
                f"maze generator failed for level {self.level_number} "
                f"({self.maze_width}x{self.maze_height}): {error}"
            ) from error
        if (len(self.maze_grid) != self.maze_height
                or any(len(row) != self.maze_width
                       for row in self.maze_grid)):
            raise RuntimeError(
                f"maze generator returned a maze of the wrong size "
                f"for level {self.level_number}")
        self.maze_img = None
        self.cell_size = 0
        self.offset_x = 0
        self.offset_y = 0
        self.build_maze_image()
        # pacman
        self.pacman = Pacman(self.mlx_class, self)
        # lives are kept between levels
        self.pacman.lives = self.max_lives if lives is None else lives
        self.heart_slots = max(self.max_lives, self.pacman.lives)

        self.powerup_timer = 0
        # dots
        self.dots = Pacgums(self, self.pacman)
        # Ghost
        self.blinky = Ghost("blinky", self.maze_width - 2, 1, self.mlx_class, self)
        self.pinky = Ghost("pinky", 1, 1, self.mlx_class, self)
        self.inky = Ghost("inky", self.maze_width - 2, self.maze_height - 2, self.mlx_class, self)
        self.clyde = Ghost("clyde", 1, self.maze_height - 2, self.mlx_class, self)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
        self.blinky.load_assets()
        self.pinky.load_assets()
        self.inky.load_assets()
        self.clyde.load_assets()
        for ghost in self.ghosts:
            blinky_ref = self.blinky if ghost.name == "inky" else None
            ghost.ai = GhostAI(ghost, self.pacman, self, blinky_ref)



        self.background = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/background.xpm")
        self.heart = self.mlx.mlx_png_file_to_image(self.mlx_ptr, "assets/pacman-art/other/heart.png")
        self.heart_clear = self.mlx.mlx_png_file_to_image(self.mlx_ptr, "assets/pacman-art/other/heart_clear.png")
        self.font = Font("assets/10x20.bdf")
        minutes, seconds = divmod(self.level_duration, 60)
        self.last_timer = f"{minutes:02}:{seconds:02}"
        self.current_timer = f"{minutes:02}:{seconds:02}"
        self.timer_img = None
        self.score_img = None
        self.text = TextDrawer(mlx_class)
        # score is kept between levels
        self.current_score = score
        self.last_score = None

    def _fill_rect(self, data, line_size, bypp, x, y, w, h, color):
        row = color * w
        for yy in range(y, y + h):
            off = yy * line_size + x * bypp
            data[off:off + w * bypp] = row

    def scale_image(self, img, src_w, src_h, dst_w, dst_h):
        src, bpp, src_ls, _ = self.mlx.mlx_get_data_addr(img)
        bypp = bpp // 8
        new = self.mlx.mlx_new_image(self.mlx_ptr, dst_w, dst_h)
        dst, _, dst_ls, _ = self.mlx.mlx_get_data_addr(new)
        for y in range(dst_h):
            sy = y * src_h // dst_h
            for x in range(dst_w):
                sx = x * src_w // dst_w
                s = sy * src_ls + sx * bypp
                d = y * dst_ls + x * bypp
                dst[d:d + bypp] = src[s:s + bypp]
        return new

    def build_maze_image(self):
        free_w = self.mlx_class.width
        free_h = self.mlx_class.height - GAME_SCREEN_Y_MARGIN

        self.cell_size = min(free_w // self.maze_width, free_h // self.maze_height)
        pix_w = self.maze_width * self.cell_size
        pix_h = self.maze_height * self.cell_size
        self.offset_x = (free_w - pix_w) // 2
        self.offset_y = 70 + (free_h - pix_h) // 2
        thick = 2

        self.maze_img = self.mlx.mlx_new_image(self.mlx_ptr, pix_w, pix_h)
        data, bpp, line_size, _ = self.mlx.mlx_get_data_addr(self.maze_img)
        bypp = bpp // 8
        wall = WALL_COLOR.to_bytes(bypp, "little")
        path = PATH_COLOR.to_bytes(bypp, "little")

        self._fill_rect(data, line_size, bypp, 0, 0, pix_w, pix_h, path)
        s = self.cell_size
        for r, row in enumerate(self.maze_grid):
            for c, val in enumerate(row):
                if isinstance(val, str):
                    val = int(val, 16)
                x0, y0 = c * s, r * s
                if val & N:
                    self._fill_rect(data, line_size, bypp, x0, y0, s, thick, wall)
                if val & S:
                    self._fill_rect(data, line_size, bypp, x0, y0 + s - thick, s, thick, wall)
                if val & W:
                    self._fill_rect(data, line_size, bypp, x0, y0, thick, s, wall)
                if val & E:
                    self._fill_rect(data, line_size, bypp, x0 + s - thick, y0, thick, s, wall)

    def draw_maze(self):
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, self.maze_img, self.offset_x, self.offset_y)

    def draw_hearts(self):
        x = 0
        y = 0

        # heart_slots only grows, so hearts from extra lives get cleared
        self.heart_slots = max(self.heart_slots, self.pacman.lives)
        for i in range(self.heart_slots):
            if i < self.pacman.lives:
                img, w, h = self.heart
            else:
                img, w, h = self.heart_clear

            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.mlx_win, img, x, y
            )
            x += w + 10
    
    def draw_level(self):
        """Draw 'Level N' in the HUD."""
        self.text.draw(f"Level {self.level_number:<3}", 1050, 0)

    def draw_cheat_status(self):
        """Show which cheats are on (blank when cheat mode is off)."""
        status = ""
        if self.cheat_mode:
            status = "CHEAT"
            if self.invincible:
                status += " INV"
            if self.ghosts_frozen:
                status += " FRZ"
            if self.pacman.speed != PACMAN_SPEED:
                status += " FAST"
        self.text.draw(f"{status:<18}", 1650, 0, 2)

    def check_level_complete(self):
        """The level is won when every pacgum and super-pacgum is eaten."""
        if not self.dots.dots and not self.dots.super_pacgums:
            self.level_won = True

    def pause(self):
        """Remember when the game was paused."""
        self.paused_at = time.monotonic()

    def resume(self):
        """Shift every timer by the time spent in pause."""
        delta = time.monotonic() - self.paused_at
        self.level_start_time += delta
        if self.pacman.powerup_active:
            self.pacman.power_up_end_time += delta
        for ghost in self.ghosts:
            if ghost.ghost_respawn_time:
                ghost.ghost_respawn_time += delta
        self.needs_clear = True

    def destroy(self):
        """Free the images owned by this level before switching level."""
        for img in (self.maze_img, self.dots.dots_img, self.timer_img,
                    self.score_img):
            if img is not None:
                self.mlx.mlx_destroy_image(self.mlx_ptr, img)
        self.text.clear()

    def draw_score(self):
        score = f"Score: {self.current_score}"
        x = 174 + 500
        self.bdfs_writing_score(score, 3, x, 0)

    def bdfs_writing_score(self, text, scale, x, y):
        if text == self.last_score and self.score_img != None:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, self.score_img, x, 0)
        else:
            if self.score_img != None:
                self.mlx.mlx_destroy_image(self.mlx_ptr, self.score_img)
            bitmap = self.font.draw(text) * scale

            rows = bitmap.todata(2)
            text_width = bitmap.width()
            text_height = bitmap.height()

            self.score_img = self.mlx.mlx_new_image(self.mlx_ptr, text_width, text_height)

            data, bpp, line_size, img_format = self.mlx.mlx_get_data_addr(self.score_img)

            bytes_per_pixel = bpp // 8

            background = 0xFF0060B4
            color = 0xFFFFFFFF

            bg_bytes = background.to_bytes(
                bytes_per_pixel, "little"
            )
            fg_bytes = color.to_bytes(
                bytes_per_pixel, "little"
            )

            for py in range(text_height):
                for px in range(text_width):
                    offset = py * line_size + px * bytes_per_pixel
                    data[offset:offset + bytes_per_pixel] = bg_bytes

            for py, row in enumerate(rows):
                for px, pixel in enumerate(row):
                    if pixel:
                        offset = py * line_size + px * bytes_per_pixel
                        data[offset:offset + bytes_per_pixel] = fg_bytes
            self.last_score = text

            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, self.score_img, x, 0)

    def start_timer(self):
        self.level_start_time = time.monotonic()
        self.game_over = False

    def put_back(self):
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, 0, 0)

    def update_timer(self):
        elapsed = int(time.monotonic() - self.level_start_time)
        remaining = max(0, self.level_duration - elapsed)
        minutes, seconds = divmod(remaining, 60)
        self.current_timer = f"{minutes:02}:{seconds:02}"
        self.bdfs_writing_timer(self.current_timer, 3, 1400, 0)
        self.last_timer = self.current_timer

        if remaining == 0 and not self.game_over:
            #should display game over
            self.game_over = True

    def bdfs_writing_timer(self, text, scale, x, y):
        if self.current_timer == self.last_timer and self.timer_img != None:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, self.timer_img, x, 0)
        else:
            if self.timer_img != None:
                self.mlx.mlx_destroy_image(self.mlx_ptr, self.timer_img)
            bitmap = self.font.draw(text) * scale

            rows = bitmap.todata(2)
            text_width = bitmap.width()
            text_height = bitmap.height()

            self.timer_img = self.mlx.mlx_new_image(self.mlx_ptr, text_width, text_height)

            data, bpp, line_size, img_format = self.mlx.mlx_get_data_addr(self.timer_img)

            bytes_per_pixel = bpp // 8

            background = 0xFF0060B4
            color = 0xFFFFFFFF

            bg_bytes = background.to_bytes(
                bytes_per_pixel, "little"
            )
            fg_bytes = color.to_bytes(
                bytes_per_pixel, "little"
            )

            for py in range(text_height):
                for px in range(text_width):
                    offset = py * line_size + px * bytes_per_pixel
                    data[offset:offset + bytes_per_pixel] = bg_bytes

            for py, row in enumerate(rows):
                for px, pixel in enumerate(row):
                    if pixel:
                        offset = py * line_size + px * bytes_per_pixel
                        data[offset:offset + bytes_per_pixel] = fg_bytes

            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, self.timer_img, x, 0)

    def add_score(self, points: int):
        """Add points to current score."""
        self.current_score += points

    def check_colli(self):
        """Handle Pac-Man touching a ghost (eat it or lose a life)."""
        if self.game_over:
            return
        for ghost in self.ghosts:
            if ghost.eaten:
                continue
            if (self.pacman.pacman_x, self.pacman.pacman_y) != (ghost.x, ghost.y):
                continue
            if ghost.edible:
                if ghost.eat_ghost():
                    self.add_score(self.points_ghost)
            elif not self.invincible:
                self.pacman.lose_life(self.ghosts)
                break

    def render(self):
        """Update the game one frame and draw it.

        When the level is won or the game is over nothing is drawn:
        main.py checks `level_won` / `game_over` and changes screen.
        """
        if self.game_over or self.level_won:
            return
        if self.needs_clear:
            self.put_back()
            self.needs_clear = False

        self.pacman.update_pacman()
        self.pacman.update_power_up(self.ghosts)

        if not self.ghosts_frozen:
            for ghost in self.ghosts:
                ghost.update()
        else:
            for ghost in self.ghosts:
                ghost.update_ghost_respawns()

        self.check_colli()
        self.check_level_complete()
        if self.game_over or self.level_won:
            return

        self.draw_hearts()
        self.update_timer()
        # The timer may have ended the game
        if self.game_over:
            return

        self.draw_score()
        self.draw_level()
        self.draw_cheat_status()
        self.draw_maze()
        self.dots.draw()

        for ghost in self.ghosts:
            ghost.draw()

        self.pacman.draw()

    def handle_key(self, key):
        """Movement keys, plus the cheat keys when cheat mode is on."""
        if self.game_over:
            return
        if key == ord("c"):
            self.cheat_mode = not self.cheat_mode
            if not self.cheat_mode:
                self.invincible = False
                self.ghosts_frozen = False
                self.pacman.speed = PACMAN_SPEED
            return
        if self.cheat_mode:
            if key == ord("n"):           # skip level
                self.level_won = True
                return
            if key == ord("i"):           # invincibility
                self.invincible = not self.invincible
                return
            if key == ord("f"):           # freeze ghosts
                self.ghosts_frozen = not self.ghosts_frozen
                return
            if key == ord("l"):           # extra life
                self.pacman.lives += 1
                return
            if key == ord("o"):           # fast pacman
                fast = max(1, PACMAN_SPEED // 2)
                self.pacman.speed = (PACMAN_SPEED
                                     if self.pacman.speed == fast else fast)
                return
            if key == ord("t"):           # reset the level timer
                self.level_start_time = time.monotonic()
                return
        self.pacman.handle_key(key)
