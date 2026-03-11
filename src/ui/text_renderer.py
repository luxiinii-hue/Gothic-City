"""Styled text utility."""

import os
import pygame
from config import WHITE, FONT_TITLE_PATH, FONT_BODY_PATH


_font_cache: dict[tuple[int, str], pygame.font.Font] = {}
_render_cache: dict[tuple, pygame.Surface] = {}


def get_font(size: int, font_type: str = "body") -> pygame.font.Font:
    key = (size, font_type)
    if key not in _font_cache:
        path = FONT_TITLE_PATH if font_type == "title" else FONT_BODY_PATH
        if os.path.exists(path):
            _font_cache[key] = pygame.font.Font(path, size)
        else:
            _font_cache[key] = pygame.font.Font(None, size)
    return _font_cache[key]


def draw_text(surface: pygame.Surface, text: str, x: int, y: int,
              size: int = 24, color=WHITE, center: bool = False,
              font_type: str = "body", shadow: bool = False):
    font = get_font(size, font_type)
    
    # Use render cache for static text to prevent frame-by-frame rendering overhead
    render_key = (text, size, color, font_type, shadow)
    if render_key not in _render_cache:
        text_surf = font.render(str(text), True, color)
        
        if shadow:
            shadow_surf = font.render(str(text), True, (0, 0, 0))
            combined_surf = pygame.Surface((text_surf.get_width() + 1, text_surf.get_height() + 1), pygame.SRCALPHA)
            combined_surf.blit(shadow_surf, (1, 1))
            combined_surf.blit(text_surf, (0, 0))
            _render_cache[render_key] = combined_surf
        else:
            _render_cache[render_key] = text_surf
            
    # Clear cache if it gets too large to prevent memory leaks
    if len(_render_cache) > 500:
        _render_cache.clear()
            
    final_surf = _render_cache[render_key]
    if center:
        rect = final_surf.get_rect(center=(x, y))
    else:
        rect = final_surf.get_rect(topleft=(x, y))
        
    surface.blit(final_surf, rect)
    return rect
