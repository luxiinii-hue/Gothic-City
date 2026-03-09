"""HP bars, energy pips, block display."""

import pygame
from config import (
    RED, DARK_RED, GREEN, DARK_GREEN, BLUE, WHITE, GRAY, GOLD,
    FONT_SIZE_SMALL,
)
from src.ui.text_renderer import draw_text


def draw_health_bar(surface: pygame.Surface, x: int, y: int,
                    width: int, height: int,
                    current: int, maximum: int,
                    color=RED, bg_color=DARK_RED):
    # Background
    pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=3)
    # Fill
    if maximum > 0:
        fill_w = max(0, int(width * current / maximum))
        pygame.draw.rect(surface, color, (x, y, fill_w, height), border_radius=3)
    # Border
    pygame.draw.rect(surface, GRAY, (x, y, width, height), width=1, border_radius=3)
    # Text
    text = f"{current}/{maximum}"
    draw_text(surface, text, x + width // 2, y + height // 2,
              size=FONT_SIZE_SMALL, color=WHITE, center=True)


def draw_energy_pips(surface: pygame.Surface, x: int, y: int,
                     current: int, maximum: int):
    pip_size = 20
    gap = 6
    for i in range(maximum):
        px = x + i * (pip_size + gap)
        color = GOLD if i < current else DARK_RED
        pygame.draw.circle(surface, color, (px + pip_size // 2, y + pip_size // 2),
                           pip_size // 2)
        pygame.draw.circle(surface, WHITE, (px + pip_size // 2, y + pip_size // 2),
                           pip_size // 2, width=1)


def draw_block_indicator(surface: pygame.Surface, x: int, y: int,
                         block: int):
    if block <= 0:
        return
    # Shield shape
    pygame.draw.circle(surface, BLUE, (x, y), 16)
    pygame.draw.circle(surface, WHITE, (x, y), 16, width=1)
    draw_text(surface, str(block), x, y,
              size=FONT_SIZE_SMALL, color=WHITE, center=True)
