"""AI controller for non-player units in ATB lane combat."""

import random
from src.combat.unit import CombatUnit
from src.combat.ability import AbilityRegistry
from src.combat.realtime_battle import RealtimeBattle


class AIController:
    """Controls AI-driven units: auto-ability usage (no positioning needed)."""

    def __init__(self, battle: RealtimeBattle, ability_registry: AbilityRegistry):
        self.battle = battle
        self.ability_registry = ability_registry

    def update(self, dt: float, player_unit: CombatUnit | None = None):
        """Update all AI-controlled units (ability usage only)."""
        for unit in self.battle.player_units:
            if not unit.alive:
                continue
            if unit.id == self.battle.player_controlled_id:
                continue
            self._try_use_ability(unit)

        for unit in self.battle.enemy_units:
            if not unit.alive:
                continue
            self._try_use_ability(unit)

    def _should_use_ability(self, unit: CombatUnit, ability_id: str) -> bool:
        """Specific conditional checks for certain abilities."""
        if ability_id == "dark_sacrifice":
            # Cultist Minion only sacrifices if HP is below 50%
            return unit.hp < (unit.max_hp * 0.5)
            
        if ability_id == "defensive_stance":
            # Goblin Sentinel only uses stance if in front ranks
            return unit.rank <= 2
            
        if ability_id == "eldritch_command":
            # Goblin Warlock only commands if there is a Cultist Minion alive
            has_minion = any(u.alive and u.id == "cultist_minion" for u in self.battle.enemy_units)
            return has_minion

        return True

    def _try_use_ability(self, unit: CombatUnit):
        """Try to fire an ability if off cooldown (random chance per frame)."""
        if unit.is_stunned:
            return
        # Small chance per frame to check abilities (~3 checks/sec at 60fps)
        if random.random() > 0.05:
            return

        # Shuffle ability order so AI doesn't always prefer the first ability
        ability_ids = list(unit.ability_ids)
        random.shuffle(ability_ids)
        for ability_id in ability_ids:
            if unit.can_use_ability(ability_id):
                if self._should_use_ability(unit, ability_id):
                    self.battle.fire_ability(unit, ability_id)
                    break
