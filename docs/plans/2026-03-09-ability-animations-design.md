# Ability Animations, Tooltips & Asset Reorganization — Design

## Problem Statement

1. **Team select info panel overflow**: The CharacterPanel stat block renders above the character card, overflowing to the right side of the screen.
2. **No ability descriptions**: Abilities are listed by name only — no way to see what they do.
3. **Combat animations are particles-only**: Abilities trigger particle bursts but lack sprite-based visual effects.
4. **Asset disorganization**: Usable assets live in "Potential assets/" — they should be promoted to proper directories.

## Design

### 1. Team Select Panel Fix

The CharacterPanel (260x400 at x=SCREEN_WIDTH-300) overflows when 5 character cards take up most of the width. Fix by repositioning the panel as a bottom overlay that appears on hover, rather than a side panel. This avoids overlap with character cards entirely.

### 2. Tooltip System

Add a `Tooltip` component that renders a floating box near the mouse cursor when hovering over keywords (ability names, status effects, etc.). Tooltips show:
- Ability name + icon
- Description text (new field in abilities.json)
- Stats: damage, cooldown, targeting
- Effects (stun, burn, summon)

In team select, ability names in the info panel become hoverable. The tooltip follows the mouse with smart edge clamping so it never goes off-screen.

### 3. Asset Reorganization

Move used assets from `Potential assets/` into permanent directories:

| Source | Destination | Content |
|--------|------------|---------|
| `Potential assets/abilities/PNG/Icon*.png` | `UI/ability_icons/` | 48 generic ability icons |
| `Potential assets/abilities/Icons/PNG/Icons_*.png` | `UI/ability_icons/` | 6 named spell icons |
| `Potential assets/abilities/weapons/1 Icons/Icon28_*.png` | `UI/weapon_icons/` | 40 weapon icons |
| `Potential assets/abilities/{spell}/PNG/*.png` | `Animations/abilities/{spell}/` | Frame sequences |
| `Potential assets/backgrounds/` | Stays (already used via full path) | Background images |

The `Potential assets/` directory stays as a staging area for unused/future assets. Only actively-used assets get promoted.

CLAUDE.md convention: "When integrating assets from `Potential assets/`, copy them into the appropriate `character assets/` subdirectory (UI/icons, Animations, etc.) rather than referencing Potential assets paths directly in code."

### 4. Ability Animation System

#### Animation Types

Two distinct visual styles:

**Spell animations** (ranged/magic abilities): Play a multi-frame sprite sequence at the target position. Frames cycle over ~0.6s, scaled to ~80x80px, then fade out.
- Shadow Bolt: Water Ball frames, tinted purple at load time
- Shield Bash: Fire Spell frames (fire sweep)
- Arcane Blast: Fire Ball frames (plays on each target)
- Twin Shot: Water Arrow frames, two staggered instances

**Melee animations** (physical abilities): The weapon icon scales up, slashes diagonally across the target (translate + rotate over ~0.3s), then fades. Combined with existing particle sparks.
- Savage Rend: Icon28_09 (curved blade), green tint

#### Color Tinting

At load time, apply a color tint to sprite frames using `pygame.Surface.fill()` with `BLEND_RGB_MULT`. This shifts the hue without losing detail. Tint map:
- Shadow Bolt: purple (0.6, 0.3, 1.0)
- Twin Shot: green (0.5, 1.0, 0.4)
- Others: use as-is

#### Ability-to-Animation Mapping

Stored in `data/abilities.json` as new fields per ability:
```json
{
  "icon": "ability_icons/Icon19.png",
  "animation": {
    "type": "spell",
    "frames_dir": "Animations/abilities/Water Ball",
    "tint": [150, 80, 255],
    "scale": 80,
    "duration": 0.6
  }
}
```

For melee:
```json
{
  "icon": "weapon_icons/Icon28_09.png",
  "animation": {
    "type": "melee_slash",
    "sprite": "weapon_icons/Icon28_09.png",
    "tint": [100, 255, 80],
    "scale": 64,
    "duration": 0.3
  }
}
```

#### New Class: `AbilityAnimator`

In `src/animation/ability_animator.py`:
- `SpellAnimation`: holds frame list, current frame index, position, scale, tint, lifetime
- `MeleeSlashAnimation`: holds weapon sprite, start/end position, rotation, lifetime
- `AbilityAnimator`: manages active animations, `update(dt)`, `draw(surface)`
- Integrates with existing `ParticleEmitter` — particles still fire alongside sprite animations

#### Integration with combat_state.py

In `_process_action()`: when an ability action fires, look up the ability's animation config, spawn the appropriate animation at the target's screen position. The `AbilityAnimator` renders after units but before the UI overlay, same layer as particles.

### 5. Ability Descriptions in abilities.json

Add `description` field to each ability:
- shadow_bolt: "Hurls a bolt of dark energy at a single enemy."
- shield_bash: "Smashes the target with a holy shield, stunning them for 1 turn."
- arcane_blast: "Unleashes arcane energy that strikes all enemies."
- savage_rend: "A vicious slash that rends the target with brutal force."
- twin_shot: "Fires two rapid arrows at a single target."
- summon_cultist: "Calls forth cultist minions to fight alongside the warlock."
