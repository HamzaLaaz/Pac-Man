"""
Graphical effect wrapper (gfx) is thin wrapper built around python-mlx
u can find the original one here: https://github.com/42school/mlx_CLXV.git
you can even find the the original one written in C
why : i made it as a helper to help me while making pacman
and also why not
what his wrapper:
  1. creates one off-screen image the size of the window (a "backbuffer")
  2. lets you draw into it directly since it's faster than pixel_put alone
  3. blits the whole thing to the window in one call via render().
  4. shapes ready to render in one call

Explanation of what is the backbuffer:
    -it's like a 2d array that maps ur screen pixels
    each position (a pixel) stores it's color infos
    after filling the whole buffer with the needed frame
    we render it which is way faster than drawing each pixel 1 by 1
"""

def _pack(color):
    """Pack 0xAARRGGBB into little-endian ARGB bytes for the buffer."""
    if color <= 0xFFFFFF:
        color |= 0xFF000000
    return color.to_bytes(4, "little")


class Gfx:
    def __init__(self, mlx, title, width=None, height=None):
        """construct the graphics window and its backbuffer."""
        self.mlx = mlx
        
        # Initialize the MLX connection with X server
        self.mlx_ptr = mlx.mlx_init()
        
        # dynamic way of getting the screen dimensions 
        # The first returned value is ignored because we only need width and height.
        _, screen_width, screen_height = mlx.mlx_get_screen_size(self.mlx_ptr)
        
        # if a static dimensions is needed just pass it as arguments
        self.width = width if width is not None else screen_width
        self.height = height if height is not None else screen_height
        
        # initialize the mlx window
        self.win = mlx.mlx_new_window(self.mlx_ptr, self.width, self.height, title)
        if not self.win:
            raise RuntimeError("Gfx: could not create window")

        # initialize the img with the same size as the screen
        # this is our backbuffer so we can draw fast as fuck
        self.img = mlx.mlx_new_image(self.mlx_ptr, self.width, self.height)
        if not self.img:
            raise RuntimeError("Gfx: could not create backbuffer image")

        # Get direct access to the image's pixel data and its memory layout.
        # data: pixel buffer
        # bpp: bits used to represent one pixel
        # sl: number of bytes occupied by one image row
        # fmt: byte order information (i have no fucking clue what it's used for but it's useless)
        self.data, self.bpp, self.sl, self.fmt = mlx.mlx_get_data_addr(self.img)
        # move from bites per pixel to byte per pixel
        self.bypp = self.bpp // 8 if self.bpp >= 8 else 4

        # dict of sprites
        self._sprites = {}  # name -> (img, w, h, data, sl, bypp)
    
    """
    Pixels handling: 
    """
    def pixel(self, x, y, color):
        """Write a single pixel into the backbuffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = y * self.sl + x * self.bypp
            self.data[offset:offset + 4] = _pack(color)
    
    def clear(self, color=0x000000):
        """Fill the whole backbuffer with one color default is black"""
        row = _pack(color) * self.width
        for y in range(self.height):
            offset = y * self.sl
            self.data[offset:offset + self.width * 4] = row
            
    """
    draw a line function
    """
    def line(self, x0, y0, x1, y1, color, thickness=1):
        """
        Bresenham algo from (x0,y0) to (x1,y1).
        check <https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm>
        thickness > 1 stamps a small filled square at each step instead of a
        single pixel. That keeps the line solid at any angle without gaps,
        and easier since i use the same function inside rect function
        """
        # first we calculate Δx (Horizontal distance between the 2 points)
        dx = abs(x1 - x0)
        # and Δy (vertical distance between the 2 points)
        dy = -abs(y1 - y0)
        # sx and sy let us knwo which direction we moving to
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        # err let us fall back to the other side when we start to diverge away in one side
        err = dx + dy
        half = thickness // 2

        while True:
            if thickness <= 1:
                self.pixel(x0, y0, color)
            else:
                self.rect(x0 - half, y0 - half, thickness, thickness, color, fill=True)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
    
    """
    draw a rectangle function
    """
    def rect(self, x, y, w, h, color, fill=True):
        """Rectangle with top-left corner at (x,y), width w, height h."""
        if fill:
            packed = _pack(color)
            row_len = w * 4
            for j in range(max(0, y), min(self.height, y + h)):
                offset = j * self.sl + max(0, x) * self.bypp
                start_x = max(0, x)
                end_x = min(self.width, x + w)
                if end_x > start_x:
                    self.data[offset:offset + (end_x - start_x) * 4] = packed * (end_x - start_x)
        else:
            self.line(x, y, x + w, y, color)
            self.line(x, y + h, x + w, y + h, color)
            self.line(x, y, x, y + h, color)
            self.line(x + w, y, x + w, y + h, color)

    """
    draw a circle function
    """
    def circle(self, cx, cy, r, color, fill=False):
        """Midpoint circle algorithm, centered at (cx,cy) with radius r."""
        cx, cy, r = int(cx), int(cy), int(r)
        x, y = r, 0
        err = 0

        def plot(px, py):
            if fill:
                self.line(cx - px, cy + py, cx + px, cy + py, color)
                self.line(cx - px, cy - py, cx + px, cy - py, color)
            else:
                for a, b in ((px, py), (-px, py), (px, -py), (-px, -py),
                             (py, px), (-py, px), (py, -px), (-py, -px)):
                    self.pixel(cx + a, cy + b, color)

        while x >= y:
            plot(x, y)
            y += 1
            if err <= 0:
                err += 2 * y + 1
            if err > 0:
                x -= 1
                err -= 2 * x + 1
                
    """
    Sprites
    """               
    def load_sprite(self, name, path, kind="png"):
        """Load a PNG or XPM file and keep it around under `name` for sprite()."""
        result = self.mlx.mlx_png_file_to_image(self.mlx_ptr, path) if kind == "png" else self.mlx.mlx_xpm_file_to_image(self.mlx_ptr, path)
        if not result:
            raise RuntimeError(f"Gfx: could not load sprite '{path}'")
        img, w, h = result
        data, bpp, sl, _fmt = self.mlx.mlx_get_data_addr(img)
        self._sprites[name] = (img, w, h, data, sl, bpp // 8 if bpp >= 8 else 4)
        return name

    def sprite(self, name, x, y, transparent=None):
        """
        plot a previously loaded sprite into the backbuffer at (x, y).
        """
        img, w, h, sdata, ssl, sbypp = self._sprites[name]
        for j in range(h):
            dy = y + j
            if not (0 <= dy < self.height):
                continue
            src_row = j * ssl
            for i in range(w):
                dx = x + i
                if not (0 <= dx < self.width):
                    continue
                o = src_row + i * sbypp
                px = int.from_bytes(sdata[o:o + 4], "little")
                if transparent is not None and (px & 0xFFFFFF) == transparent:
                    continue
                self.pixel(dx, dy, px)

    def sprite_size(self, name):
        # return a sprite dimensions
        _, w, h, *_ = self._sprites[name]
        return w, h
    
    """
    Text
    """ 
    def text(self, x, y, s, color=0xFFFFFFFF):
        """
        Draws directly to the window, on top of whatever was last rendered
        !!!! caution call this after render()
        """
        self.mlx.mlx_string_put(self.mlx_ptr, self.win, x, y, color, s)
        
    """
    Utils
    """ 
    def render(self):
        """Push the backbuffer to the window. Call once per frame."""
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win, self.img, 0, 0)

    def on_loop(self, fn):
        """fn() is called every loop"""
        self.mlx.mlx_loop_hook(self.mlx_ptr, lambda _p: fn(), None)

    def on_key(self, fn):
        """fn(keycode) is called on key press."""
        self.mlx.mlx_key_hook(self.win, lambda key, _p: fn(key), None)

    def on_close(self, fn):
        """fn() is called when the close button is clicked."""
        self.mlx.mlx_hook(self.win, 33, 0, lambda _p: fn(), None)

    def on_mouse(self, fn):
        """
        fn(button, x, y) is called on mouse button press
        Mouse Button Integer Mapping:
        1 = Left Click
        3 = Right Click
        2 = Middle Click
        4 = Scroll Up
        5 = Scroll Down
        """
        self.mlx.mlx_mouse_hook(self.win, lambda button, x, y, _p: fn(button, x, y), None)

    def stop(self):
        # exit the loop safly
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def run(self):
        # keeps the loop runing untill it quit after an event decided
        self.mlx.mlx_loop(self.mlx_ptr)

    def destroy(self):
        """
        destroy all the rss recursivly so we it don't leak
        !! yes it fucking leaks
        """
        for img, *_ in self._sprites.values():
            self.mlx.mlx_destroy_image(self.mlx_ptr, img)
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win)
        self.mlx.mlx_release(self.mlx_ptr)
