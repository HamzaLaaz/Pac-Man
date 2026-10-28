from .constants import *
from .mlx_class import MlxClass
from mazegenerator import MazeGenerator
from .classes.entities import Pacman, Ghost
from .classes.entities import Pacgums
from .ghost_ai import GhostAI
from bdfparser import Font
import time


class GameScreen:
    def __init__(self, maze_x: int, maze_y: int, seed: int, mlx_class: MlxClass):
        self.maze_width = maze_x
        self.maze_height = maze_y
        self.seed = seed
        self.mlx_class = mlx_class
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.x = 0
        self.y = 0
        
        # timer 
        self.level_duration = 90
        self.level_start_time = time.monotonic()
        self.last_displayed_second = None
        
        self.game_over = False
        
        self.maze_generator = MazeGenerator(size=(self.maze_width, self.maze_height), perfect=False, seed = self.seed)
        self.maze_grid = self.maze_generator.maze
        self.maze_img = None
        self.cell_size = 0
        self.offset_x = 0
        self.offset_y = 0
        self.build_maze_image()
        # pacman
        self.pacman_lifes = 3
        self.pacman = Pacman(self.pacman_lifes, self.mlx_class, self)
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
        self.font = Font("assets/10x20.bdf")
        minutes, seconds = divmod(self.level_duration, 60)
        self.last_timer = f"{minutes:02}:{seconds:02}"
        self.current_timer = f"{minutes:02}:{seconds:02}"
        self.timer_img = None
        self.score_img = None
        self.current_score = 0
        self.last_score = 0
        
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
        img, w, h = self.heart
        self.x = 0
        for i in range(self.pacman_lifes):
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x, 0)
            self.x += w + 10
    
    def draw_score(self, score):
        self.current_score = f"Score: {score}"
        x = self.x + 500
        self.last_score = self.current_score
        self.bdfs_writing_score(self.current_score, 3, x, 0)
    
    def bdfs_writing_score(self, text, scale, x, y):
        if self.current_score == self.last_score and self.score_img != None:
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

        if remaining == 0:
            #should display game over
            pass
    
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
        # self.mlx.mlx_destroy_image(self.mlx_ptr, img)

    def render(self):
        # self.put_back()
        self.draw_hearts()
        self.update_timer()
        self.draw_score(20)
        self.draw_maze()
        self.dots.draw()
        self.pacman.draw()
        for ghost in self.ghosts:
            ghost.draw()
    
    def handle_key(self, key):
        if not self.game_over:
            self.pacman.handle_key(key)

    


