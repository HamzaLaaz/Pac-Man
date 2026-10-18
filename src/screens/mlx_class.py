from mlx import Mlx


class MlxClass:
    def __init__(self, title, width=None, height=None):
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        _, sw, sh = self.mlx.mlx_get_screen_size(self.mlx_ptr)
        self.width = width if width is not None else sw
        self.height = height if height is not None else sh
        self.win = self.mlx.mlx_new_window(self.mlx_ptr, self.width, self.height, title)
        print(self.win)
        if not self.win:
            raise RuntimeError("could not create window")
        

    def stop(self):
        self.mlx.mlx_loop_exit(self.mlx_ptr)
