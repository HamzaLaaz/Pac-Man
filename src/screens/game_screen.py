from .constants import *
from .mlx_class import MlxClass
from mazegenerator import MazeGenerator
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
        
        # timer 
        self.level_duration = 10
        self.level_start_time = time.monotonic()
        self.last_displayed_second = None
        
        self.game_over = False
        
        self.pacman_lifes = 3
        
        self.maze_generator = MazeGenerator(size=(self.maze_width, self.maze_height), perfect=False, seed = self.seed)
        self.maze_grid = self.maze_generator.maze
        
        self.background = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/background.xpm")

    
    def draw_hearts(self):
        img, w, h = self.mlx.mlx_png_file_to_image(self.mlx_ptr, "assets/pacman-art/other/heart.png")
        self.x = 0
        for i in range(self.pacman_lifes):
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x, 0)
            self.x += w + 10
        
    def maze_getter(self):
        return self.maze_generator
    
    def draw_score(self, score):
        text = f"Score: {score}"
        x = self.x + 500
        self.bdfs_writing(text, 3, x, 0)
    
    def start_timer(self):
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update_timer, None)


    def update_timer(self, __param):
        elapsed = int(time.monotonic() - self.level_start_time)
        remaining = max(0, self.level_duration - elapsed)

        if remaining != self.last_displayed_second:
            self.last_displayed_second = remaining

            minutes, seconds = divmod(remaining, 60)
            timer_text = f"{minutes:02}:{seconds:02}"

            self.bdfs_writing(timer_text, 3, 1400, 0)

        if remaining == 0:
            #should display game over
            pass
    
    def put_back(self):
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, 0, 0)
    
    def bdfs_writing(self, text, scale, x, y):
        font = Font("assets/10x20.bdf")
        bitmap = font.draw(text) * scale

        rows = bitmap.todata(2)
        text_width = bitmap.width()
        text_height = bitmap.height()

        img = self.mlx.mlx_new_image(self.mlx_ptr, text_width, text_height)

        data, bpp, line_size, img_format = self.mlx.mlx_get_data_addr(img)

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

        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, x, 0)

    def render(self):
        self.put_back()
        self.draw_hearts()
        self.draw_score(20)
        


