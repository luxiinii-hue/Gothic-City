"""Procedural idle animation: subtle bob, breathe, glow, shadow from static PNGs.

The PNG sprite is always the dominant visual. Animations are barely perceptible —
just enough to feel alive. No distortion, no flashy effects.
"""

import pygame
from src.animation.tween import sine_wave, pulse
from src.entities.character import IdleConfig
from config import IDLE_SCALE_STEPS, SHADOW_ALPHA


class IdleAnimator:
    def __init__(self, base_surface: pygame.Surface, config: IdleConfig, flip_x: bool = False):
        self._shadow_surf_cache = {}
        self._glow_surf_cache = {}
        self.config = config
        self.time = 0.0
        
        self.num_frames = getattr(config, "num_frames", 1)
        self.frame_rate = getattr(config, "frame_rate", 0.15)
        
        self.frames = []
        if self.num_frames > 1:
            fw = base_surface.get_width() // self.num_frames
            fh = base_surface.get_height()
            for i in range(self.num_frames):
                frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
                frame.blit(base_surface, (0, 0), (i * fw, 0, fw, fh))
                if flip_x:
                    frame = pygame.transform.flip(frame, True, False)
                self.frames.append(frame)
        else:
            frame = base_surface
            if flip_x:
                frame = pygame.transform.flip(frame, True, False)
            self.frames.append(frame)

        self.base = self.frames[0]
        self.base_w = self.base.get_width()
        self.base_h = self.base.get_height()

        # Pre-cache the few scaled frames needed for the tiny breathe range
        # Note: With multiple frames, pre-caching every frame and scale combination is memory intensive.
        # So if it's animated (num_frames > 1), we disable breathe caching and scale dynamically.
        self._scale_cache: dict[tuple[int, int], pygame.Surface] = {}
        if self.num_frames == 1:
            self._precache_scales()

    def _precache_scales(self):
        steps = IDLE_SCALE_STEPS
        smin = self.config.breathe_min
        smax = self.config.breathe_max
        for i in range(steps):
            t = i / max(steps - 1, 1)
            s = smin + t * (smax - smin)
            w = max(1, int(self.base_w * s))
            h = max(1, int(self.base_h * s))
            key = (w, h)
            if key not in self._scale_cache:
                self._scale_cache[key] = pygame.transform.smoothscale(self.base, key)

    def _get_scaled(self, scale: float) -> pygame.Surface:
        w = max(1, int(self.base_w * scale))
        h = max(1, int(self.base_h * scale))
        
        frame_idx = 0
        if self.num_frames > 1:
            frame_idx = int(self.time / self.frame_rate) % self.num_frames
            
        current_frame = self.frames[frame_idx]
        
        if self.num_frames == 1:
            key = (w, h)
            if key not in self._scale_cache:
                self._scale_cache[key] = pygame.transform.smoothscale(current_frame, key)
            return self._scale_cache[key]
        else:
            # If animated, scale dynamically to save memory
            return pygame.transform.smoothscale(current_frame, (w, h))

    def update(self, dt: float):
        self.time += dt

    def draw(self, surface: pygame.Surface, center_x: int, foot_y: int):
        """Draw the animated sprite anchored at foot position."""
        cfg = self.config

        # Breathing: very subtle scale oscillation (< 1% variation)
        breathe_freq = cfg.bob_frequency * 0.67
        breathe_scale = pulse(self.time, breathe_freq,
                              cfg.breathe_min, cfg.breathe_max)
        scaled = self._get_scaled(breathe_scale)
        sw, sh = scaled.get_size()

        # Bobbing: gentle vertical float (1-2 pixels typically)
        bob_y = sine_wave(self.time, cfg.bob_frequency, cfg.bob_amplitude)

        # Position anchored at feet
        x = center_x - sw // 2
        y = foot_y - sh + bob_y

        # Shadow: small dark ellipse at feet, shrinks slightly when sprite bobs up
        shadow_w = int(sw * 0.5)
        shadow_h = max(2, int(shadow_w * 0.2))
        if cfg.bob_amplitude > 0:
            shadow_intensity = 1.0 - (bob_y / cfg.bob_amplitude) * 0.05
            shadow_w = max(4, int(shadow_w * shadow_intensity))
            shadow_h = max(2, int(shadow_h * shadow_intensity))
        # Cache shadow surface by dimensions to prevent frame-by-frame allocation
        if (shadow_w, shadow_h) not in self._shadow_surf_cache:
            shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, SHADOW_ALPHA),
                                (0, 0, shadow_w, shadow_h))
            self._shadow_surf_cache[(shadow_w, shadow_h)] = shadow_surf
            
        surface.blit(self._shadow_surf_cache[(shadow_w, shadow_h)], (center_x - shadow_w // 2,
                                   foot_y - shadow_h // 2))

        # Glow: very faint colored halo behind sprite center
        if cfg.glow_enabled:
            glow_alpha = int(pulse(self.time, 0.9,
                                   cfg.glow_alpha_min, cfg.glow_alpha_max))
            glow_r = max(4, int(sw * cfg.glow_radius_factor))
            # Cache glow surface by radius to avoid per-frame circle drawing
            if glow_r not in self._glow_surf_cache:
                gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                # Draw with full alpha once, then set_alpha during blit for faster fading
                pygame.draw.circle(gs, (*cfg.glow_color, 255), (glow_r, glow_r), glow_r)
                self._glow_surf_cache[glow_r] = gs
            
            glow_surf = self._glow_surf_cache[glow_r]
            glow_surf.set_alpha(glow_alpha)
            gx = center_x - glow_r
            gy = foot_y - sh * 0.55 - glow_r + bob_y
            surface.blit(glow_surf, (gx, gy))

        # Sprite: the PNG itself, always drawn last so it's on top
        surface.blit(scaled, (x, y))
