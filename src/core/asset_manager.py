"""Load, scale, cache PNGs and fonts."""

import os
import json
import pygame
from config import ASSET_DIR, DATA_DIR


class AssetManager:
    def __init__(self):
        self._images: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple, pygame.Surface] = {}
        self._json_cache: dict[str, object] = {}

    def load_image(self, filename: str, scale: tuple[int, int] | None = None) -> pygame.Surface:
        key = filename
        if key not in self._images:
            path = os.path.join(ASSET_DIR, filename)
            img = pygame.image.load(path).convert_alpha()
            self._images[key] = img
        img = self._images[key]
        if scale:
            cache_key = (filename, scale[0], scale[1])
            if cache_key not in self._scaled_cache:
                self._scaled_cache[cache_key] = pygame.transform.smoothscale(img, scale)
            return self._scaled_cache[cache_key]
        return img

    def get_scaled(self, filename: str, width: int, height: int) -> pygame.Surface:
        return self.load_image(filename, scale=(width, height))

    def load_json(self, filename: str):
        if filename not in self._json_cache:
            path = os.path.join(DATA_DIR, filename)
            with open(path, "r") as f:
                self._json_cache[filename] = json.load(f)
        return self._json_cache[filename]

    def precache_scales(self, filename: str, base_size: tuple[int, int],
                        scale_min: float, scale_max: float, steps: int):
        """Pre-cache scaled versions for idle animation."""
        for i in range(steps):
            t = i / max(steps - 1, 1)
            s = scale_min + t * (scale_max - scale_min)
            w = int(base_size[0] * s)
            h = int(base_size[1] * s)
            self.load_image(filename, scale=(w, h))
