"""Draw text in the window with the BDF font."""
from typing import Any

from bdfparser import Font

from .constants import TEXT_BG_COLOR, TEXT_COLOR
from .mlx_class import MlxClass

FONT_PATH = "assets/10x20.bdf"
MAX_CACHE = 200


class TextDrawer:
    """Render strings to MLX images and cache them.

    The same text (with the same scale and colors) is only rendered
    once; after that the cached image is just put to the window.
    """

    def __init__(self, mlx_class: MlxClass) -> None:
        """Load the font."""
        self.mlx_class = mlx_class
        self.mlx = mlx_class.mlx
        self.mlx_ptr = mlx_class.mlx_ptr
        self.mlx_win = mlx_class.win
        self.font = Font(FONT_PATH)
        self.cache: dict[tuple[str, int, int, int], tuple[Any, int, int]] = {}

    def render(self, text: str, scale: int, color: int,
               background: int) -> tuple[Any, int, int]:
        key = (text, scale, color, background)
        if key in self.cache:
            return self.cache[key]
        if len(self.cache) >= MAX_CACHE:
            self.clear()

        bitmap = self.font.draw(text if text else " ") * scale
        rows = bitmap.todata(2)
        width = bitmap.width()
        height = bitmap.height()
        img = self.mlx.mlx_new_image(self.mlx_ptr, width, height)
        data, bpp, line_size, _ = self.mlx.mlx_get_data_addr(img)
        bypp = bpp // 8
        fg_bytes = color.to_bytes(bypp, "little")
        bg_bytes = background.to_bytes(bypp, "little")
        for y, row in enumerate(rows):
            for x, pixel in enumerate(row):
                offset = y * line_size + x * bypp
                data[offset:offset + bypp] = fg_bytes if pixel else bg_bytes
        self.cache[key] = (img, width, height)
        return self.cache[key]

    def draw(self, text: str, x: int, y: int, scale: int = 3,
             color: int = TEXT_COLOR,
             background: int = TEXT_BG_COLOR) -> tuple[int, int]:
        """Draw text with its top-left corner at (x, y); return its size."""
        img, width, height = self.render(text, scale, color, background)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.mlx_win,
                                         img, x, y)
        return width, height

    def draw_centered(self, text: str, y: int, scale: int = 3,
                      color: int = TEXT_COLOR,
                      background: int = TEXT_BG_COLOR) -> int:
        """Draw text centered horizontally; return its height."""
        _, width, height = self.render(text, scale, color, background)
        x = (self.mlx_class.width - width) // 2
        self.draw(text, x, y, scale, color, background)
        return height

    def clear(self) -> None:
        """Destroy every cached image."""
        for img, _, _ in self.cache.values():
            self.mlx.mlx_destroy_image(self.mlx_ptr, img)
        self.cache.clear()
