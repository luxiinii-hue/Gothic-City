"""Combat animations: attack lunge, damage flash, card play."""

import pygame


class CombatAnimator:
    def __init__(self):
        self._anims: list[dict] = []

    def add_flash(self, target: str, color: tuple = (255, 255, 255),
                  duration: float = 0.15):
        self._anims.append({
            "type": "flash",
            "target": target,
            "color": color,
            "duration": duration,
            "elapsed": 0.0,
        })

    def add_shake(self, target: str, intensity: float = 4.0,
                  duration: float = 0.2):
        self._anims.append({
            "type": "shake",
            "target": target,
            "intensity": intensity,
            "duration": duration,
            "elapsed": 0.0,
        })

    def update(self, dt: float):
        for anim in self._anims:
            anim["elapsed"] += dt
        self._anims = [a for a in self._anims if a["elapsed"] < a["duration"]]

    def get_offset(self, target: str) -> tuple[float, float]:
        """Get x,y offset for a target from active shake animations."""
        import math
        ox, oy = 0.0, 0.0
        for anim in self._anims:
            if anim["type"] == "shake" and anim["target"] == target:
                t = anim["elapsed"] / anim["duration"]
                fade = 1.0 - t
                intensity = anim["intensity"] * fade
                ox += math.sin(anim["elapsed"] * 50) * intensity
                oy += math.cos(anim["elapsed"] * 37) * intensity * 0.5
        return ox, oy

    def get_flash(self, target: str) -> tuple | None:
        """Get flash color for target if active, else None."""
        for anim in self._anims:
            if anim["type"] == "flash" and anim["target"] == target:
                t = anim["elapsed"] / anim["duration"]
                alpha = int(255 * (1.0 - t))
                return (*anim["color"][:3], alpha)
        return None

    @property
    def is_animating(self) -> bool:
        return len(self._anims) > 0
