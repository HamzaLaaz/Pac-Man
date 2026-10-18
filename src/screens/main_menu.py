from .mlx_class import MlxClass
from .constants import *
import time



class Button:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize a button."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = 0

    def contains(self, px: int, py: int) -> bool:
        """Return whether a point is inside the button."""
        return (self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height)


class MainMenu:
    def __init__(self, mlx_class: MlxClass):
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.x_start = 0
        self.y_start = 0
        self.width = mlx_class.width
        self.height = mlx_class.height
        self.selected = 0
        self.hover = -1                      # index of hovered button, -1 = none
        self.index = 0
        self.title = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/pac-man_title.xpm")
        self.background = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/background.xpm")
        self.start_open_button = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/start_open.xpm")        
        self.start_closed_button = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/start_closed.xpm")        
        self.high_scorers = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/high_scorers.xpm")
        self.instructions = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/instructions.xpm")
        self.exit = self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, "assets/main-menu/exit.xpm")
        _, tw, th = self.title
        self.title_x = (self.width - tw) // 2
        self.title_y = int(self.height * 0.08)
        x = (self.width - BTN_WIDTH) // 2
        y = self.title_y + th
        self.buttons = []
        for _ in ACTIONS:
            self.buttons.append(Button(x, y, BTN_WIDTH, BTN_HEIGHT))
            y += BTN_HEIGHT + GAP
        

    
    def put_back(self):
        img, _, _ = self.background
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, 0, 0)

              
    def put_title(self):
        img, w, h = self.title
        self.x_start = (WIDTH - w) // 2
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x_start, int(HEIGHT * 0.08))
        self.y_start = int(HEIGHT * 0.08) + h
        self.start_button = Button(self.x_start, self.y_start, 581, 146)

    
    def draw_buttons(self):
        width = 581
        height = 146
        self.x_start = (WIDTH - width) // 2
        holder = self.y_start
        # start
        if self.hover == False:
            if self.index % 2 == 0:
                time.sleep(0.1)
                img, w, h = self.start_closed_button
                self.index += 1
            else:
                time.sleep(0.1)
                img, w, h = self.start_open_button
                self.index += 1
        else:
            img, w, h = self.start_open_button

        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x_start, holder)
        holder += height + 5
        # highscorers
        img, w, h = self.high_scorers
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x_start, holder)
        holder += height + GAP
        # instructions
        img, w, h = self.instructions
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x_start, holder)
        holder += height + GAP
        # exit
        img, w, h = self.exit
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win, img, self.x_start, holder)
        holder += height + GAP


    def render(self):
        self.put_back()
        self.put_title()
        self.draw_buttons()
    
    def on_motion(self):
        """
         self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        """
        _, mx, my = self.mlx.mlx_mouse_get_pos(self.mlx_win)
        self.hover = -1
        for i, btn in enumerate(self.buttons):
            if btn.contains(mx, my):
                self.hover = i
    
    def handle_mouse(self, x, y):
        for btn, action in zip(self.buttons, ACTIONS):
            if btn.contains(x, y):
                return action
        return None
        

    def on_key(self, keycode, _):
        if keycode == 65362:      # up
            self.selected = (self.selected - 1) % 4
        elif keycode == 65364:    # down
            self.selected = (self.selected + 1) % 4
        elif keycode == 65293:    # enter
            if self.selected == 3:
                self.mlx.mlx_loop_exit(self.mlx_ptr)
        elif keycode == 65307:    # esc
            self.mlx.mlx_loop_exit(self.mlx_ptr)
        self.render()
