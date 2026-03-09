"""Target selection logic for abilities and auto-attacks."""

import random
from src.combat.unit import CombatUnit


def get_targets(targeting: str, source: CombatUnit,
                allies: list[CombatUnit],
                enemies: list[CombatUnit]) -> list[CombatUnit]:
    """Return list of valid targets based on targeting type."""
    alive_enemies = [u for u in enemies if u.alive]
    alive_allies = [u for u in allies if u.alive]

    if targeting == "single_enemy":
        if alive_enemies:
            return [random.choice(alive_enemies)]
        return []

    elif targeting == "all_enemies":
        return alive_enemies

    elif targeting == "single_ally":
        if alive_allies:
            return [random.choice(alive_allies)]
        return []

    elif targeting == "all_allies":
        return alive_allies

    elif targeting == "self":
        return [source]

    # Default: single enemy
    if alive_enemies:
        return [random.choice(alive_enemies)]
    return []
