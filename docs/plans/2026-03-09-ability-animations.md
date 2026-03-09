# Ability Animations, Tooltips & Asset Reorganization — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add sprite-based ability animations to combat, fix the team select info panel overflow, add hoverable ability tooltips with descriptions, and organize assets from Potential assets/ into permanent directories.

**Architecture:** A new `AbilityAnimator` class manages frame-based spell animations and melee slash animations, sitting alongside the existing `ParticleEmitter`. Abilities gain `icon` and `animation` config in `abilities.json`. A generic `Tooltip` widget handles hover-to-reveal info across the game. Assets are copied from `Potential assets/` into `Animations/` and `UI/` subdirectories.

**Tech Stack:** Python 3.13, pygame-ce 2.5.7, JSON data files

---

### Task 1: Reorganize Assets into Permanent Directories

Copy actively-used assets from `Potential assets/` staging area into proper permanent directories under `character assets/`.

**Step 1: Create directory structure and copy files**

Run:
```bash
# Create permanent directories
mkdir -p "character assets/Animations/abilities/Fire Ball"
mkdir -p "character assets/Animations/abilities/Fire Spell"
mkdir -p "character assets/Animations/abilities/Fire Arrow"
mkdir -p "character assets/Animations/abilities/Water Ball"
mkdir -p "character assets/Animations/abilities/Water Arrow"
mkdir -p "character assets/Animations/abilities/Water Spell"
mkdir -p "character assets/UI/ability_icons"
mkdir -p "character assets/UI/weapon_icons"

# Copy spell animation frames (PNG only)
cp "character assets/Potential assets/abilities/Fire Ball/PNG/"*.png "character assets/Animations/abilities/Fire Ball/"
cp "character assets/Potential assets/abilities/Fire Spell/PNG/"*.png "character assets/Animations/abilities/Fire Spell/"
cp "character assets/Potential assets/abilities/Fire Arrow/PNG/"*.png "character assets/Animations/abilities/Fire Arrow/"
cp "character assets/Potential assets/abilities/Water Ball/PNG/"*.png "character assets/Animations/abilities/Water Ball/"
cp "character assets/Potential assets/abilities/Water Arrow/PNG/"*.png "character assets/Animations/abilities/Water Arrow/"
cp "character assets/Potential assets/abilities/Water Spell/PNG/"*.png "character assets/Animations/abilities/Water Spell/"

# Copy generic ability icons
cp "character assets/Potential assets/abilities/PNG/"Icon*.png "character assets/UI/ability_icons/"

# Copy named spell icons
cp "character assets/Potential assets/abilities/Icons/PNG/"Icons_*.png "character assets/UI/ability_icons/"

# Copy weapon icons
cp "character assets/Potential assets/abilities/weapons/1 Icons/"Icon28_*.png "character assets/UI/weapon_icons/"
```

**Step 2: Verify files copied correctly**

Run: `ls "character assets/Animations/abilities/Fire Ball/" && ls "character assets/UI/ability_icons/" | head -5 && ls "character assets/UI/weapon_icons/" | head -5`
Expected: Frame PNGs in animations dir, Icon*.png in ability_icons, Icon28_*.png in weapon_icons.

**Step 3: Commit**

```bash
git add "character assets/Animations/" "character assets/UI/ability_icons/" "character assets/UI/weapon_icons/"
git commit -m "chore: organize ability assets into permanent directories

Copy spell animation frames, ability icons, and weapon icons from
Potential assets/ staging area into Animations/ and UI/ subdirectories."
```

---

### Task 2: Update CLAUDE.md with Asset Convention

**Files:**
- Modify: `CLAUDE.md` (project root, create if not exists)

**Step 1: Add asset organization convention**

Add to CLAUDE.md (or create it):
```markdown
## Asset Conventions
- All game-ready assets live under `character assets/` in organized subdirectories:
  - `Characters/` — playable character sprites
  - `Enemies/` — enemy sprites
  - `Animations/abilities/` — multi-frame ability animation sequences
  - `UI/icons/` — stat and map node icons (24x24, 32x32)
  - `UI/ability_icons/` — ability effect icons (32x32)
  - `UI/weapon_icons/` — weapon sprites (32x32)
  - `UI/fonts/` — TTF font files
- `Potential assets/` is a staging area for unintegrated free assets. When using an asset from there, copy it into the appropriate permanent subdirectory first.
- Only PNG format is used in-game. Aseprite/PSD/AI/EPS files are editor source files — do not reference them in code.
- Sprite paths in JSON data files are relative to ASSET_DIR (`character assets/`).
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add asset organization conventions to CLAUDE.md"
```

---

### Task 3: Add Animation Config to abilities.json

**Files:**
- Modify: `data/abilities.json`

**Step 1: Update abilities.json with icon, animation, and richer descriptions**

Each ability gets:
- `description`: Human-readable tooltip text
- `icon`: path to icon PNG (relative to ASSET_DIR)
- `animation`: object with `type`, frame info, optional `tint`, `scale`, `duration`

```json
[
    {
        "id": "shadow_bolt",
        "name": "Shadow Bolt",
        "description": "Hurls a bolt of dark energy at a single enemy.",
        "targeting": "single_enemy",
        "base_damage": 15,
        "scaling": 1.0,
        "cooldown": 2,
        "effects": [],
        "icon": "UI/ability_icons/Icon19.png",
        "animation": {
            "type": "spell",
            "frames_dir": "Animations/abilities/Water Ball",
            "tint": [150, 80, 255],
            "scale": 80,
            "duration": 0.6
        }
    },
    {
        "id": "shield_bash",
        "name": "Shield Bash",
        "description": "Smashes the target with a holy shield, stunning them for 1 turn.",
        "targeting": "single_enemy",
        "base_damage": 10,
        "scaling": 1.0,
        "cooldown": 3,
        "effects": [{"type": "stun", "duration": 1}],
        "icon": "UI/ability_icons/Icon16.png",
        "animation": {
            "type": "spell",
            "frames_dir": "Animations/abilities/Fire Spell",
            "tint": null,
            "scale": 80,
            "duration": 0.5
        }
    },
    {
        "id": "arcane_blast",
        "name": "Arcane Blast",
        "description": "Unleashes arcane energy that strikes all enemies.",
        "targeting": "all_enemies",
        "base_damage": 12,
        "scaling": 1.0,
        "cooldown": 3,
        "effects": [],
        "icon": "UI/ability_icons/Icon7.png",
        "animation": {
            "type": "spell",
            "frames_dir": "Animations/abilities/Fire Ball",
            "tint": null,
            "scale": 80,
            "duration": 0.6
        }
    },
    {
        "id": "savage_rend",
        "name": "Savage Rend",
        "description": "A vicious slash that rends the target with brutal force.",
        "targeting": "single_enemy",
        "base_damage": 18,
        "scaling": 1.2,
        "cooldown": 2,
        "effects": [],
        "icon": "UI/weapon_icons/Icon28_09.png",
        "animation": {
            "type": "melee_slash",
            "sprite": "UI/weapon_icons/Icon28_09.png",
            "tint": [100, 255, 80],
            "scale": 64,
            "duration": 0.3
        }
    },
    {
        "id": "twin_shot",
        "name": "Twin Shot",
        "description": "Fires two rapid arrows at a single target.",
        "targeting": "single_enemy",
        "base_damage": 7,
        "scaling": 0.8,
        "cooldown": 1,
        "effects": [],
        "icon": "UI/ability_icons/Icon5.png",
        "animation": {
            "type": "spell",
            "frames_dir": "Animations/abilities/Water Arrow",
            "tint": [120, 255, 100],
            "scale": 80,
            "duration": 0.5
        }
    },
    {
        "id": "summon_cultist",
        "name": "Summon Cultist",
        "description": "Calls forth cultist minions to fight alongside the warlock.",
        "targeting": "self",
        "base_damage": 0,
        "scaling": 0.0,
        "cooldown": 4,
        "effects": [{"type": "summon", "value": 1, "duration": 0, "enemy_id": "cultist_minion"}],
        "icon": "UI/ability_icons/Icon18.png",
        "animation": {
            "type": "spell",
            "frames_dir": "Animations/abilities/Fire Spell",
            "tint": [200, 80, 255],
            "scale": 80,
            "duration": 0.6
        }
    }
]
```

**Step 2: Verify JSON is valid**

Run: `python -c "import json; json.load(open('data/abilities.json')); print('OK')"`
Expected: `OK`

**Step 3: Update AbilityDef to parse new fields**

Modify: `src/combat/ability.py:24-46`

Add `icon` and `animation` fields to `AbilityDef`:

```python
@dataclass
class AbilityDef:
    id: str
    name: str
    description: str
    targeting: str
    base_damage: int
    scaling: float
    cooldown: int
    effects: list[AbilityEffect] = field(default_factory=list)
    icon: str = ""
    animation: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "AbilityDef":
        effects = [AbilityEffect.from_dict(e) for e in data.get("effects", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            targeting=data["targeting"],
            base_damage=data["base_damage"],
            scaling=data.get("scaling", 1.0),
            cooldown=data["cooldown"],
            effects=effects,
            icon=data.get("icon", ""),
            animation=data.get("animation", {}),
        )
```

**Step 4: Verify import still works**

Run: `python -c "from src.combat.ability import AbilityDef; print('OK')"`
Expected: `OK`

**Step 5: Commit**

```bash
git add data/abilities.json src/combat/ability.py
git commit -m "feat: add animation config and icons to ability definitions"
```

---

### Task 4: Create AbilityAnimator

**Files:**
- Create: `src/animation/ability_animator.py`

This is the core animation engine. Two animation types:
- `SpellAnimation`: Cycles through pre-loaded sprite frames at a target position, with optional color tint
- `MeleeSlashAnimation`: Moves a weapon sprite diagonally across target with rotation

**Step 1: Write the AbilityAnimator module**

```python
"""Sprite-based ability animations for combat."""

import os
import math
import pygame
from dataclasses import dataclass, field
from config import ASSET_DIR


def _tint_surface(surface: pygame.Surface, tint: tuple[int, int, int]) -> pygame.Surface:
    """Apply RGB tint to a surface using multiplicative blend."""
    tinted = surface.copy()
    tint_layer = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    # Normalize tint values to 0-255 range for BLEND_RGB_MULT
    tint_layer.fill((*tint, 255))
    tinted.blit(tint_layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return tinted


def load_animation_frames(frames_dir: str, scale: int,
                          tint: tuple[int, int, int] | None = None) -> list[pygame.Surface]:
    """Load all PNG frames from a directory, sorted by name, scaled and optionally tinted."""
    full_dir = os.path.join(ASSET_DIR, frames_dir)
    if not os.path.isdir(full_dir):
        return []
    files = sorted(f for f in os.listdir(full_dir) if f.lower().endswith(".png"))
    frames = []
    for fname in files:
        path = os.path.join(full_dir, fname)
        img = pygame.image.load(path).convert_alpha()
        # Scale preserving aspect ratio, fitting within scale x scale box
        w, h = img.get_size()
        aspect = w / h
        if aspect >= 1:
            new_w = scale
            new_h = int(scale / aspect)
        else:
            new_h = scale
            new_w = int(scale * aspect)
        img = pygame.transform.smoothscale(img, (new_w, new_h))
        if tint:
            img = _tint_surface(img, tint)
        frames.append(img)
    return frames


@dataclass
class SpellAnimation:
    """Multi-frame spell effect playing at a fixed position."""
    frames: list[pygame.Surface]
    x: float
    y: float
    duration: float
    age: float = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.duration

    @property
    def current_frame(self) -> pygame.Surface:
        if not self.frames:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        progress = self.age / self.duration
        idx = min(int(progress * len(self.frames)), len(self.frames) - 1)
        return self.frames[idx]


@dataclass
class MeleeSlashAnimation:
    """Weapon icon that slashes diagonally across the target."""
    sprite: pygame.Surface
    x: float
    y: float
    duration: float
    age: float = 0.0
    slash_distance: float = 60.0

    @property
    def alive(self) -> bool:
        return self.age < self.duration


class AbilityAnimator:
    """Manages active ability animations during combat."""

    def __init__(self):
        self.spell_anims: list[SpellAnimation] = []
        self.melee_anims: list[MeleeSlashAnimation] = []
        self._frame_cache: dict[str, list[pygame.Surface]] = {}

    def _get_frames(self, frames_dir: str, scale: int,
                    tint: tuple[int, int, int] | None) -> list[pygame.Surface]:
        """Load and cache animation frames."""
        cache_key = f"{frames_dir}|{scale}|{tint}"
        if cache_key not in self._frame_cache:
            self._frame_cache[cache_key] = load_animation_frames(frames_dir, scale, tint)
        return self._frame_cache[cache_key]

    def spawn_spell(self, x: float, y: float, frames_dir: str,
                    scale: int = 80, duration: float = 0.6,
                    tint: tuple[int, int, int] | None = None):
        """Spawn a multi-frame spell animation at (x, y)."""
        frames = self._get_frames(frames_dir, scale, tint)
        if frames:
            self.spell_anims.append(SpellAnimation(
                frames=frames, x=x, y=y, duration=duration,
            ))

    def spawn_melee(self, x: float, y: float, sprite_path: str,
                    scale: int = 64, duration: float = 0.3,
                    tint: tuple[int, int, int] | None = None):
        """Spawn a melee slash animation at (x, y)."""
        full_path = os.path.join(ASSET_DIR, sprite_path)
        if not os.path.exists(full_path):
            return
        img = pygame.image.load(full_path).convert_alpha()
        img = pygame.transform.smoothscale(img, (scale, scale))
        if tint:
            img = _tint_surface(img, tint)
        self.melee_anims.append(MeleeSlashAnimation(
            sprite=img, x=x, y=y, duration=duration,
        ))

    def spawn_from_config(self, x: float, y: float, animation_config: dict):
        """Spawn animation from an ability's animation config dict."""
        if not animation_config:
            return
        anim_type = animation_config.get("type", "")
        tint = animation_config.get("tint")
        if tint:
            tint = tuple(tint)
        scale = animation_config.get("scale", 80)
        duration = animation_config.get("duration", 0.6)

        if anim_type == "spell":
            frames_dir = animation_config.get("frames_dir", "")
            self.spawn_spell(x, y, frames_dir, scale, duration, tint)
        elif anim_type == "melee_slash":
            sprite = animation_config.get("sprite", "")
            self.spawn_melee(x, y, sprite, scale, duration, tint)

    def update(self, dt: float):
        for anim in self.spell_anims:
            anim.age += dt
        self.spell_anims = [a for a in self.spell_anims if a.alive]

        for anim in self.melee_anims:
            anim.age += dt
        self.melee_anims = [a for a in self.melee_anims if a.alive]

    def draw(self, surface: pygame.Surface):
        # Draw spell animations
        for anim in self.spell_anims:
            frame = anim.current_frame
            # Fade out in last 30% of lifetime
            progress = anim.age / anim.duration
            if progress > 0.7:
                fade = 1.0 - (progress - 0.7) / 0.3
                alpha = max(0, int(255 * fade))
                frame = frame.copy()
                frame.set_alpha(alpha)
            surface.blit(frame, (
                int(anim.x - frame.get_width() // 2),
                int(anim.y - frame.get_height() // 2),
            ))

        # Draw melee slash animations
        for anim in self.melee_anims:
            progress = anim.age / anim.duration
            # Diagonal slash: top-right to bottom-left
            offset_x = anim.slash_distance * (0.5 - progress)
            offset_y = -anim.slash_distance * (0.5 - progress)
            # Rotate weapon during slash
            angle = -135 * progress
            rotated = pygame.transform.rotate(anim.sprite, angle)
            # Fade out in last 40%
            if progress > 0.6:
                fade = 1.0 - (progress - 0.6) / 0.4
                alpha = max(0, int(255 * fade))
                rotated.set_alpha(alpha)
            surface.blit(rotated, (
                int(anim.x + offset_x - rotated.get_width() // 2),
                int(anim.y + offset_y - rotated.get_height() // 2),
            ))
```

**Step 2: Verify import works**

Run: `python -c "from src.animation.ability_animator import AbilityAnimator; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/animation/ability_animator.py
git commit -m "feat: add AbilityAnimator for sprite-based combat animations

Supports multi-frame spell animations and melee weapon slash effects,
with color tinting and frame caching."
```

---

### Task 5: Integrate AbilityAnimator into Combat State

**Files:**
- Modify: `src/states/combat_state.py:1-26` (imports)
- Modify: `src/states/combat_state.py:28-50` (enter method — add ability_animator init)
- Modify: `src/states/combat_state.py:260-295` (_process_action — spawn animations)
- Modify: `src/states/combat_state.py:313-325` (draw — render animations)
- Modify: `src/states/combat_state.py` (update — tick ability_animator)

**Step 1: Add import**

At `src/states/combat_state.py:12`, after the `CombatAnimator` import, add:
```python
from src.animation.ability_animator import AbilityAnimator
```

**Step 2: Initialize AbilityAnimator in enter()**

After the line that creates `self.particle_emitter` (search for `ParticleEmitter()`), add:
```python
        self.ability_animator = AbilityAnimator()
```

**Step 3: Spawn animations in _process_action()**

In `_process_action()`, inside the `if action.type in ("attack", "ability") and action.damage > 0:` block, after the particle spawn section (around line 273), add ability animation spawning:

```python
                # Spawn sprite-based ability animation
                if action.type == "ability" and action.ability_name:
                    ability_def = self.ability_registry.get_by_name(action.ability_name)
                    if ability_def and ability_def.animation:
                        self.ability_animator.spawn_from_config(tx, ty, ability_def.animation)
```

Also handle the summon case — in the `if action.type == "summon":` block, after the existing summon handling, spawn the summon animation at the source's position:
```python
            # Spawn summon animation at source position
            source_pos = self.unit_positions.get(action.source)
            if source_pos:
                summon_ability = self.ability_registry.get("summon_cultist")
                if summon_ability and summon_ability.animation:
                    self.ability_animator.spawn_from_config(
                        source_pos[0], source_pos[1], summon_ability.animation)
```

**Step 4: Add get_by_name to AbilityRegistry**

Modify: `src/combat/ability.py:49-59`

Add a lookup-by-display-name method after the existing `get()`:
```python
    def get_by_name(self, name: str) -> AbilityDef | None:
        """Look up ability by display name (e.g. 'Shadow Bolt')."""
        for ability in self._abilities.values():
            if ability.name == name:
                return ability
        return None
```

**Step 5: Update ability_animator in update()**

In the `update()` method of `CombatScreenState`, add after `self.particle_emitter.update(dt)`:
```python
        self.ability_animator.update(dt)
```

**Step 6: Draw ability animations**

In `draw()`, after `self.particle_emitter.draw(surface)` (line 323), add:
```python
        self.ability_animator.draw(surface)
```

**Step 7: Verify the game still starts**

Run: `python -c "from src.states.combat_state import CombatScreenState; print('OK')"`
Expected: `OK`

**Step 8: Commit**

```bash
git add src/states/combat_state.py src/combat/ability.py
git commit -m "feat: integrate ability animations into combat screen

Ability actions now trigger sprite-based animations (spell or melee slash)
alongside existing particle effects."
```

---

### Task 6: Fix Team Select Info Panel Overflow

**Files:**
- Modify: `src/states/team_select_state.py:51-54` (panel position)
- Modify: `src/states/team_select_state.py:263-264` (panel draw call)
- Modify: `src/ui/panel.py:35-97` (CharacterPanel layout)

The info panel currently sits at `SCREEN_WIDTH - 300` which overlaps with the rightmost character card. Reposition it as a wider bottom panel that appears below the character cards.

**Step 1: Change panel position and size in team_select_state.py**

Change the panel initialization (around line 54) from:
```python
        self.info_panel = CharacterPanel(SCREEN_WIDTH - 300, 140, 260, 400)
```
to:
```python
        self.info_panel = CharacterPanel(40, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 80, 140)
```

This puts it as a wide bar across the bottom, outside the character card area.

**Step 2: Update CharacterPanel to support horizontal layout**

Modify `src/ui/panel.py` — rewrite the `draw` method for `CharacterPanel` to use a horizontal layout when width > height:

```python
class CharacterPanel(Panel):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.char_data = None
        self.ability_rects: list[tuple[pygame.Rect, str]] = []

    def set_character(self, char_data):
        self.char_data = char_data

    def draw(self, surface: pygame.Surface):
        if self.char_data is None:
            return

        super().draw(surface)
        cd = self.char_data
        self.ability_rects.clear()

        # Horizontal layout: Name+Role | Stats | Abilities | Description
        px = self.rect.x + 15
        py = self.rect.y + 15

        # Column 1: Name and role
        draw_text(surface, cd.name, px, py, size=FONT_SIZE_MEDIUM, color=GOLD)
        py += 28
        role_color = CLASS_COLORS.get(cd.role, GREEN)
        draw_text(surface, cd.role.capitalize(), px, py, size=FONT_SIZE_SMALL, color=role_color)

        # Column 2: Stats (offset right)
        stat_x = self.rect.x + 200
        stat_y = self.rect.y + 15
        stats = [
            ("HP", cd.max_hp, "heart"),
            ("STR", cd.strength, "sword"),
            ("ARM", cd.armor, "shield"),
            ("SPD", cd.speed, "boot"),
        ]
        for stat_name, stat_val, icon_name in stats:
            icon = get_icon(icon_name)
            if icon:
                surface.blit(icon, (stat_x, stat_y - 4))
                draw_text(surface, f"{stat_name}: {stat_val}", stat_x + 30, stat_y,
                          size=FONT_SIZE_SMALL, color=WHITE)
            else:
                draw_text(surface, f"{stat_name}: {stat_val}", stat_x, stat_y,
                          size=FONT_SIZE_SMALL, color=WHITE)
            stat_y += 24

        # Column 3: Abilities
        ability_x = self.rect.x + 400
        ability_y = self.rect.y + 15
        draw_text(surface, "Abilities:", ability_x, ability_y, size=FONT_SIZE_SMALL, color=GOLD)
        ability_y += 22
        for ability_id in cd.abilities:
            display_name = ability_id.replace('_', ' ').title()
            draw_text(surface, display_name, ability_x + 10, ability_y,
                      size=FONT_SIZE_SMALL, color=WHITE)
            # Store rect for tooltip hit detection
            text_w = len(display_name) * 9
            self.ability_rects.append((
                pygame.Rect(ability_x + 10, ability_y - 2, text_w, 20),
                ability_id,
            ))
            ability_y += 22

        # Column 4: Description
        desc_x = self.rect.x + 650
        desc_y = self.rect.y + 15
        draw_text(surface, "Info:", desc_x, desc_y, size=FONT_SIZE_SMALL, color=GOLD)
        desc_y += 22
        # Word wrap description to remaining width
        max_w = self.rect.right - desc_x - 15
        words = cd.description.split()
        line = ""
        for word in words:
            test = f"{line} {word}".strip()
            if len(test) * 8 > max_w:
                draw_text(surface, line, desc_x, desc_y, size=FONT_SIZE_SMALL, color=GRAY)
                desc_y += 20
                line = word
            else:
                line = test
        if line:
            draw_text(surface, line, desc_x, desc_y, size=FONT_SIZE_SMALL, color=GRAY)
```

**Step 3: Verify the game starts and team select renders**

Run: `python -c "from src.states.team_select_state import TeamSelectState; print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add src/states/team_select_state.py src/ui/panel.py
git commit -m "fix: reposition team select info panel as bottom bar

Moves CharacterPanel from overlapping right side to a wide bottom bar
with horizontal layout: Name/Role | Stats | Abilities | Description."
```

---

### Task 7: Add Tooltip System

**Files:**
- Create: `src/ui/tooltip.py`
- Modify: `src/states/team_select_state.py` (integrate tooltips)

**Step 1: Create the Tooltip widget**

```python
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
        self.lines: list[tuple[str, tuple]] = []  # (text, color) pairs
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
        self._width = max(
            font.size(title)[0],
            *(font.size(text)[0] for text, _ in lines),
        ) + 30
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
```

**Step 2: Integrate tooltip into team_select_state.py**

Add import at top:
```python
from src.ui.tooltip import Tooltip
```

In `enter()`, after `self.info_panel` init, add:
```python
        self.tooltip = Tooltip()
        # Load ability registry for tooltip data
        self.ability_registry = AbilityRegistry()
        self.ability_registry.load(am.load_json("abilities.json"))
```

Also add the AbilityRegistry import at the top of the file:
```python
from src.combat.ability import AbilityRegistry
```

In `handle_event()`, in the `MOUSEMOTION` handler, after the info_panel update, add tooltip logic:
```python
            # Check ability hover for tooltip
            mx, my = event.pos
            tooltip_shown = False
            for arect, ability_id in self.info_panel.ability_rects:
                if arect.collidepoint(mx, my):
                    ability = self.ability_registry.get(ability_id)
                    if ability:
                        lines = [
                            (ability.description, GRAY),
                            (f"Damage: {ability.base_damage}  CD: {ability.cooldown}  Target: {ability.targeting.replace('_', ' ')}", WHITE),
                        ]
                        for eff in ability.effects:
                            if eff.type == "stun":
                                lines.append((f"Effect: Stun ({eff.duration} turn)", (100, 200, 255)))
                            elif eff.type == "summon":
                                lines.append((f"Effect: Summon {eff.enemy_id.replace('_', ' ').title()}", (200, 100, 255)))
                        # Load icon
                        icon = None
                        if ability.icon:
                            try:
                                icon = self.game.asset_manager.load_image(ability.icon)
                            except Exception:
                                pass
                        self.tooltip.show(mx, my, ability.name, lines, icon)
                        tooltip_shown = True
                    break
            if not tooltip_shown:
                self.tooltip.hide()
```

In `draw()`, at the very end (after buttons), add:
```python
        self.tooltip.draw(surface)
```

**Step 3: Add GRAY and WHITE imports if not present**

Check the existing imports in `team_select_state.py` — `GRAY` and `WHITE` are already imported.

**Step 4: Verify imports**

Run: `python -c "from src.ui.tooltip import Tooltip; from src.states.team_select_state import TeamSelectState; print('OK')"`
Expected: `OK`

**Step 5: Commit**

```bash
git add src/ui/tooltip.py src/states/team_select_state.py
git commit -m "feat: add ability tooltip system on team select hover

Hovering over ability names in the info panel shows a tooltip with
description, damage, cooldown, targeting, and effects. Includes
ability icon when available."
```

---

### Task 8: Visual Verification and Polish

**Step 1: Run the game and verify all features**

Run: `python main.py`

Verification checklist:
1. Title screen loads with bg2 background
2. Team Select shows 5 characters, bottom info panel appears on hover
3. Hovering ability names in info panel shows tooltip with icon, description, stats
4. Begin combat — ability animations play at target positions:
   - Shadow Bolt: purple-tinted water ball animation
   - Shield Bash: fire spell sweep
   - Arcane Blast: fire ball on each enemy
   - Savage Rend: green-tinted blade slash
   - Twin Shot: green-tinted water arrow
5. Particles still fire alongside sprite animations
6. Floating damage numbers still work
7. Melee slash has diagonal motion + rotation + fade
8. Boss summon plays purple fire spell at warlock's position

**Step 2: Fix any visual issues found during testing**

Adjust scale, duration, tint values in `data/abilities.json` as needed. These are data-driven and require no code changes.

**Step 3: Final commit**

```bash
git add -A
git commit -m "polish: tune ability animation timing and visual parameters"
```

---

## File Change Summary

| File | Action | Task |
|------|--------|------|
| `character assets/Animations/abilities/` | Create (6 dirs, ~50 PNGs) | 1 |
| `character assets/UI/ability_icons/` | Create (~54 PNGs) | 1 |
| `character assets/UI/weapon_icons/` | Create (~40 PNGs) | 1 |
| `CLAUDE.md` | Create/Modify | 2 |
| `data/abilities.json` | Modify | 3 |
| `src/combat/ability.py` | Modify (add icon, animation fields + get_by_name) | 3, 5 |
| `src/animation/ability_animator.py` | **Create** | 4 |
| `src/states/combat_state.py` | Modify (integrate AbilityAnimator) | 5 |
| `src/ui/panel.py` | Modify (horizontal CharacterPanel layout) | 6 |
| `src/states/team_select_state.py` | Modify (panel position + tooltip) | 6, 7 |
| `src/ui/tooltip.py` | **Create** | 7 |
