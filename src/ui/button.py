"""Clickable button with hover states."""

import pygame
from config import (
    WHITE, GRAY, DARK_GRAY, PANEL_BG, PANEL_BORDER,
    BUTTON_WIDTH, BUTTON_HEIGHT, FONT_SIZE_MEDIUM,
)


class Button:
    def __init__(self, x: int, y: int, text: str,
                 width: int = BUTTON_WIDTH, height: int = BUTTON_HEIGHT,
                 font_size: int = FONT_SIZE_MEDIUM,
                 color=PANEL_BG, hover_color=DARK_GRAY,
                 border_color=PANEL_BORDER, text_color=WHITE,
                 on_click=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.color = color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.on_click = on_click
        self.hovered = False
        self.clicked = False
        self._font = None

    @property
    def font(self):
        from src.ui.text_renderer import get_font
        if self._font is None:
            self._font = get_font(self.font_size, "body")
        return self._font

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked:
                self.clicked = False
                if self.rect.collidepoint(event.pos):
                    if self.on_click:
                        self.on_click()
                    return True
        return False

    def draw(self, surface: pygame.Surface):
        bg = self.hover_color if self.hovered else self.color
        
        draw_rect = self.rect.copy()
        if self.clicked:
            draw_rect.inflate_ip(-4, -4)
        elif self.hovered:
            draw_rect.inflate_ip(4, 4)
            
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(surface, (10, 10, 15), shadow_rect, border_radius=6)

        pygame.draw.rect(surface, bg, draw_rect, border_radius=6)
        pygame.draw.rect(surface, self.border_color, draw_rect, width=2, border_radius=6)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)
