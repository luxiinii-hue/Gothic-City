"""Hoverable tooltip for abilities and keywords."""

import pygame
from src.ui.text_renderer import draw_text, get_font
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, GOLD,
    PANEL_BG, PANEL_BORDER, FONT_SIZE_SMALL,
)


class Tooltip:
    """Floating info box that appears near the mouse on hover."""

    def __init__(self):
        self.visible = False
        self.x = 0
        self.y = 0
        self.title = ""
        self.lines: list[tuple[str, tuple]] = []
        self.icon: pygame.Surface | None = None
        self._width = 0
        self._height = 0

    def show(self, mx: int, my: int, title: str,
             lines: list[tuple[str, tuple]],
             icon: pygame.Surface | None = None):
        """Show tooltip near mouse position."""
        self.visible = True
        self.title = title
        self.lines = lines
        self.icon = icon

        # Calculate size
        font = get_font(FONT_SIZE_SMALL)
        title_w = font.size(title)[0]
        max_line_w = max((font.size(text)[0] for text, _ in lines), default=0)
        self._width = max(title_w, max_line_w) + 30
        if icon:
            self._width += 36
        self._height = 30 + len(lines) * 20 + 10

        # Position with edge clamping
        self.x = min(mx + 15, SCREEN_WIDTH - self._width - 5)
        self.y = max(5, my - self._height - 10)
        if self.y < 5:
            self.y = my + 20

    def hide(self):
        self.visible = False

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        rect = pygame.Rect(self.x, self.y, self._width, self._height)

        # Shadow
        shadow = rect.copy()
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(surface, (10, 10, 15), shadow, border_radius=6)

        # Background
        pygame.draw.rect(surface, PANEL_BG, rect, border_radius=6)
        pygame.draw.rect(surface, PANEL_BORDER, rect, width=1, border_radius=6)

        tx = rect.x + 10
        ty = rect.y + 8

        # Icon
        if self.icon:
            icon_scaled = pygame.transform.smoothscale(self.icon, (24, 24))
            surface.blit(icon_scaled, (tx, ty))
            tx += 30

        # Title
        draw_text(surface, self.title, tx, ty, size=FONT_SIZE_SMALL, color=GOLD)
        ty += 24

        # Content lines
        tx = rect.x + 10
        for text, color in self.lines:
            draw_text(surface, text, tx, ty, size=FONT_SIZE_SMALL, color=color)
            ty += 20
