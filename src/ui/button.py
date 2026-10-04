class Button:
    """Represent a clickable rectangular UI element."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        action: str
    ) -> None:
        """Initialize a button."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action

    def contains(self, px: int, py: int) -> bool:
        """Return whether a point is inside the button."""
        return (
            self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )