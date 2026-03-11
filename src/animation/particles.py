"""Particle system + floating damage numbers for combat effects."""

import math
import random
from dataclasses import dataclass, field

import pygame


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple
    lifetime: float
    age: float = 0.0
    size: float = 3.0
    gravity: float = 0.0
    fade: bool = True


@dataclass
class FloatingNumber:
    x: float
    y: float
    text: str
    color: tuple
    age: float = 0.0
    lifetime: float = 1.0
    speed: float = 40.0


class ParticleEmitter:
    def __init__(self):
        self.particles: list[Particle] = []
        self.floaters: list[FloatingNumber] = []
        self._circle_cache = {}
        self._text_cache = {}
        self._font = None

    def emit_burst(self, x: float, y: float, count: int, color: tuple,
                   speed_range: tuple = (30, 80), lifetime: float = 0.6,
                   size_range: tuple = (2, 5), gravity: float = 60.0,
                   spread: float = math.pi * 2):
        for _ in range(count):
            angle = random.uniform(-spread / 2, spread / 2) - math.pi / 2
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            # Slight color variation
            r = max(0, min(255, color[0] + random.randint(-20, 20)))
            g = max(0, min(255, color[1] + random.randint(-20, 20)))
            b = max(0, min(255, color[2] + random.randint(-20, 20)))
            self.particles.append(Particle(
                x=x + random.uniform(-5, 5),
                y=y + random.uniform(-5, 5),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=(r, g, b),
                lifetime=lifetime + random.uniform(-0.1, 0.1),
                size=size,
                gravity=gravity,
            ))

    def add_floating_number(self, x: float, y: float, text: str, color: tuple):
        self.floaters.append(FloatingNumber(
            x=x + random.uniform(-10, 10),
            y=y,
            text=text,
            color=color,
        ))

    def update(self, dt: float):
        # Update particles
        for p in self.particles:
            p.age += dt
            p.vx *= 0.98
            p.vy += p.gravity * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
        self.particles = [p for p in self.particles if p.age < p.lifetime]

        # Update floaters
        for f in self.floaters:
            f.age += dt
            f.y -= f.speed * dt
        self.floaters = [f for f in self.floaters if f.age < f.lifetime]

    def draw(self, surface: pygame.Surface):
        # Draw particles
        for p in self.particles:
            if p.fade:
                alpha = max(0, int(255 * (1.0 - p.age / p.lifetime)))
            else:
                alpha = 255
            size = max(1, int(p.size * (1.0 - p.age / p.lifetime * 0.5)))
            if alpha > 0 and size > 0:
                # Use cached circle surfaces to prevent huge allocations
                # Key on (color, size, alpha)
                color_key = (*p.color, alpha)
                cache_key = (color_key, size)
                if cache_key not in self._circle_cache:
                    ps = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(ps, color_key, (size, size), size)
                    self._circle_cache[cache_key] = ps
                surface.blit(self._circle_cache[cache_key], (int(p.x) - size, int(p.y) - size))

        # Draw floating numbers
        if not self.floaters:
            return
            
        if not self._font:
            from src.ui.text_renderer import get_font
            self._font = get_font(28, "body")
            
        for f in self.floaters:
            alpha = max(0, int(255 * (1.0 - f.age / f.lifetime)))
            if alpha <= 0:
                continue
                
            # Cache the rendered text surface for the duration of the floater's life
            # (or at least avoid re-rendering every frame if alpha is the same)
            # Actually, alpha changes every frame, so we still have to handle it.
            # But we can cache the base (non-alpha) surface!
            base_key = (f.text, f.color)
            if base_key not in self._text_cache:
                self._text_cache[base_key] = self._font.render(f.text, True, f.color)
            
            text_surf = self._text_cache[base_key]
            # Apply alpha efficiently
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (int(f.x) - text_surf.get_width() // 2,
                                     int(f.y) - text_surf.get_height() // 2))
        
        # Periodically clear caches if they get too large
        if len(self._circle_cache) > 2000:
            self._circle_cache.clear()
        if len(self._text_cache) > 100:
            self._text_cache.clear()


# --- Preset spawn functions ---

def spawn_hit_sparks(emitter: ParticleEmitter, x: float, y: float):
    """Generic melee hit — yellow-white sparks."""
    emitter.emit_burst(x, y, 8, (255, 230, 150), speed_range=(40, 100),
                       lifetime=0.4, size_range=(2, 4), gravity=80.0)


def spawn_shadow_bolt(emitter: ParticleEmitter, x: float, y: float):
    """Purple wisps for Shadow Bolt."""
    emitter.emit_burst(x, y, 12, (160, 60, 220), speed_range=(20, 60),
                       lifetime=0.7, size_range=(3, 6), gravity=10.0)


def spawn_shield_bash(emitter: ParticleEmitter, x: float, y: float):
    """Blue flame burst for Shield Bash."""
    emitter.emit_burst(x, y, 10, (80, 140, 255), speed_range=(30, 80),
                       lifetime=0.5, size_range=(3, 5), gravity=40.0)


def spawn_arcane_blast(emitter: ParticleEmitter, x: float, y: float):
    """Pink/magenta sparkles for Arcane Blast — wider spread."""
    emitter.emit_burst(x, y, 15, (220, 100, 200), speed_range=(30, 90),
                       lifetime=0.6, size_range=(2, 5), gravity=20.0,
                       spread=math.pi * 2)


def spawn_savage_rend(emitter: ParticleEmitter, x: float, y: float):
    """Green slashing particles for Savage Rend."""
    emitter.emit_burst(x, y, 10, (100, 220, 60), speed_range=(50, 110),
                       lifetime=0.5, size_range=(2, 5), gravity=60.0,
                       spread=math.pi * 0.8)


def spawn_twin_shot(emitter: ParticleEmitter, x: float, y: float):
    """Yellow-green impact puffs for Twin Shot."""
    emitter.emit_burst(x, y, 6, (200, 220, 80), speed_range=(20, 50),
                       lifetime=0.4, size_range=(2, 4), gravity=30.0)


def spawn_death_burst(emitter: ParticleEmitter, x: float, y: float,
                      color: tuple = (200, 50, 50)):
    """Large burst on unit death."""
    # Blood burst
    emitter.emit_burst(x, y, 25, color, speed_range=(40, 150),
                       lifetime=0.8, size_range=(3, 7), gravity=80.0)
    # Bone fragment burst (white/grey chunks)
    emitter.emit_burst(x, y, 15, (230, 230, 220), speed_range=(60, 200),
                       lifetime=1.0, size_range=(3, 6), gravity=150.0)


def spawn_projectile_trail(emitter: ParticleEmitter, x: float, y: float, color: tuple):
    """Small particle left behind a flying projectile."""
    emitter.emit_burst(x, y, 1, color, speed_range=(0, 10),
                       lifetime=0.3, size_range=(1, 3), gravity=5.0)

def spawn_void_step(emitter: ParticleEmitter, x: float, y: float):
    """Purple/black teleportation swirl."""
    emitter.emit_burst(x, y, 20, (120, 40, 180), speed_range=(20, 50),
                       lifetime=0.6, size_range=(2, 4), gravity=-10.0)

def spawn_holy_provocation(emitter: ParticleEmitter, x: float, y: float):
    """Golden outward flash."""
    emitter.emit_burst(x, y, 25, (255, 200, 80), speed_range=(60, 120),
                       lifetime=0.5, size_range=(3, 5), gravity=0.0)

def spawn_ignite(emitter: ParticleEmitter, x: float, y: float):
    """Fiery embers."""
    emitter.emit_burst(x, y, 15, (255, 80, 40), speed_range=(40, 90),
                       lifetime=0.5, size_range=(2, 4), gravity=-30.0)

def spawn_bloodlust_charge(emitter: ParticleEmitter, x: float, y: float):
    """Red bloody slash trails."""
    emitter.emit_burst(x, y, 20, (200, 40, 40), speed_range=(80, 150),
                       lifetime=0.4, size_range=(3, 6), gravity=20.0)

def spawn_caltrops(emitter: ParticleEmitter, x: float, y: float):
    """Grey spikes dropping."""
    emitter.emit_burst(x, y, 15, (150, 150, 150), speed_range=(30, 60),
                       lifetime=0.8, size_range=(2, 3), gravity=80.0)

# Map ability names to spawn functions
ABILITY_PARTICLES = {
    "Shadow Bolt": spawn_shadow_bolt,
    "Shield Bash": spawn_shield_bash,
    "Arcane Blast": spawn_arcane_blast,
    "Savage Rend": spawn_savage_rend,
    "Twin Shot": spawn_twin_shot,
    "Void Step": spawn_void_step,
    "Holy Provocation": spawn_holy_provocation,
    "Ignite": spawn_ignite,
    "Bloodlust Charge": spawn_bloodlust_charge,
    "Caltrops": spawn_caltrops,
}
