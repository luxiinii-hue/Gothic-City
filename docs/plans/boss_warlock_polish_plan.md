# Plan: Warlock Boss & Minion Polish

## 1. Warlock Boss Adjustments
### Minion Spawning Position
**Problem:** The Warlock boss currently summons minions, but their placement might not consistently protect him or fulfill the "tank and sacrifice" mechanical fantasy.
**Solution:**
- In src/combat/realtime_battle.py, update the _do_summon logic specifically for the Warlock's summon_cultist ability.
- Force summoned Cultist Minions to spawn at **Rank 1 (Frontline)**.
- Existing units (including the Warlock) should automatically be pushed back (Rank 2, 3, etc.) to accommodate the new frontline tank.
- Ensure the Warlock's "Dark Sacrifice" ability logic correctly targets the frontline minion when his HP triggers it.

## 2. Minion Visual Bug Fix
**Problem:** Cultist Minions currently spawn as a default round blob instead of their intended sprite.
**Solution:**
- Inspect data/enemies.json for the "Cultist Minion" entry.
- Ensure the "sprite" field points correctly to "Enemies/Cultist_Minion.png".
- Verify that combat_state.py correctly unpacks the edata.sprite during the visual summon phase, avoiding the generic fallback shape.

## 3. Visual Flair & Animations
**Objective:** Make the Warlock boss fight feel more dramatic and ominous.

### Summoning Animation (The Warlock)
- When the Warlock casts "Summon Cultist", freeze his ATB temporarily.
- Trigger a dark magical casting animation (e.g., using Animations/icons/magic/fb664.png swirling around him).

### Entrance Animation (The Minion)
- **Portal Effect:** Before the minion sprite appears, spawn a dark rift at Rank 1. (Use Dark VFX 1 or a purple circle scaling up).
- **Spawn Particle Burst:** Use the existing spawn_death_burst but tinted purple/black as the minion materializes.
- **Screen Shake:** Add a slight, low-frequency screen shake (camera.shake(intensity=3, duration=0.4)) when the minion heavily drops into the frontline to emphasize the impact.

### Sacrifice Animation
- When the Warlock sacrifices a minion, don't just despawn it.
- Play a "soul drain" particle effect: red/purple particles traveling from the minion's position to the Warlock's position.
- Flash the Warlock red/white as he absorbs the HP/Buff, followed by a fierce floating text (e.g., "+POWER!").
