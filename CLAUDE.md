# Dungeon of the Acoc

## Asset Conventions
- All game-ready assets live under `character assets/` in organized subdirectories:
  - `Characters/` — playable character sprites
  - `Enemies/` — enemy sprites
  - `Animations/abilities/` — multi-frame ability animation sequences (PNG frames)
  - `UI/icons/` — stat and map node icons (24x24, 32x32)
  - `UI/ability_icons/` — ability effect icons (32x32)
  - `UI/weapon_icons/` — weapon sprites (32x32)
  - `UI/fonts/` — TTF font files
- `Potential assets/` is a staging area for unintegrated free assets. When using an asset from there, copy it into the appropriate permanent subdirectory first — do not reference `Potential assets/` paths in code for new integrations.
- Only PNG format is used in-game. Aseprite/PSD/AI/EPS files are editor source files — do not reference them in code.
- Sprite paths in JSON data files are relative to `ASSET_DIR` (`character assets/`).
