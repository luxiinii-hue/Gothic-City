# ATB Lane Combat & Project Backlog

> **Coordination file for AI assistants (Claude / Gemini).**
> Check this file before starting any task. Update status when you start and finish.

---

## Active Plans & Pending Tasks

### 1. UI & UX Polish
- [ ] **Reward Screen Interactions:** During the "choose reward" screen, clicking outside of the character selection area should revert back to the buff selection. This prevents wrong clicks and allows changing decisions smoothly.
- [ ] **Character Selection Logic:** Clicking on another character should automatically deselect the current side-character and set the newly clicked one as the side-character.

### 2. Abilities & Content Progression
- [ ] **Ability Cards System:** 
  - Introduce Ability Cards in events that are specific to class types (e.g., Magic wielders find Fireball, fighting classes find Sweep).
  - Characters can maintain a roster of abilities.
  - Implement a max active ability limit of 3 per character.
  - Add a UI mechanism to select and rearrange active abilities from the roster for both the player character and allies.
  - Make some Ability Cards character-specific (e.g., move Nightfang's specific unlockables to this system).

### 3. Scaling & Game Loop
- [ ] **Infinite Scaling:** Design and implement a scaling formula (stats, enemy HP/damage, rewards) to allow the game to continue on indefinitely. (May require a dedicated sub-plan).
- [ ] **Audio Integration:** Add complete sound effects (attack, hit, ability usage, death, speed bar "ding" when full).
- [ ] **Multiplayer (Co-op):** Add support for a second player to control a different party member during combat.

### 4. Environment & Map
- [ ] **Map Perspective Redesign:** Tilt the map so that it moves horizontally to the right instead of the current top-down vertical view.

### 5. Boss Fights & Balance Polish
- [ ] **Warlock Boss Adjustments:** 
  - Minions summoned by the Warlock should specifically spawn in the frontline to "tank" player damage and be sacrificed later.
  - **Visual Bug Fix:** Minions currently load as a round blob instead of their intended sprite. Assign the correct sprite (`Cultist_Minion.png`) to them.

---

## Completed Milestones (Archived)
- **Sprint 1-3 (ATB Pivot):** Complete transition to Lane-based ATB combat. Includes all rank positioning, pushing/pulling, AI adaptations, ATB speed bars, and new character abilities.
- **Summon Refactoring:** Moved summon creation logic into the battle engine (`realtime_battle.py`) to prevent sync issues and enforce max ranks.
- **Visual Overhauls:** 
  - Dynamic Ability Animators with tweening.
  - Redesigned map paths using Pygame-drawn procedural glowing bezier curves.
  - Removed clunky frame backgrounds from map HP portraits for a cleaner look.