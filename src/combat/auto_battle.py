"""Auto-battle engine — runs combat automatically, emitting action events."""

import random
from dataclasses import dataclass, field
from src.combat.unit import CombatUnit
from src.combat.ability import AbilityRegistry, AbilityDef
from src.combat.targeting import get_targets
from config import DAMAGE_ARMOR_FACTOR


@dataclass
class BattleAction:
    """An event emitted by the battle engine for the UI to consume."""
    type: str  # "attack", "ability", "burn_tick", "dodge", "stun_skip", "defeat", "victory"
    source: str = ""  # unit name
    target: str = ""  # unit name
    ability_name: str = ""
    damage: int = 0
    heal: int = 0
    message: str = ""


class AutoBattle:
    def __init__(self, player_units: list[CombatUnit],
                 enemy_units: list[CombatUnit],
                 ability_registry: AbilityRegistry):
        self.player_units = player_units
        self.enemy_units = enemy_units
        self.ability_registry = ability_registry
        self.turn = 0
        self.result: str | None = None  # "win", "lose", or None
        self.pending_actions: list[BattleAction] = []
        self._turn_order: list[CombatUnit] = []
        self._current_index = 0
        self._waiting = True  # True = waiting to start next round

    @property
    def all_units(self) -> list[CombatUnit]:
        return self.player_units + self.enemy_units

    def _build_turn_order(self):
        alive = [u for u in self.all_units if u.alive]
        self._turn_order = sorted(alive, key=lambda u: u.speed, reverse=True)
        self._current_index = 0

    def step(self) -> list[BattleAction]:
        """Execute one unit's turn. Returns actions generated."""
        if self.result is not None:
            return []

        actions = []

        # Start new round if needed
        if self._waiting or self._current_index >= len(self._turn_order):
            self.turn += 1
            self._build_turn_order()
            self._waiting = False
            if not self._turn_order:
                return []

        # Get current unit
        unit = self._turn_order[self._current_index]
        self._current_index += 1

        if not unit.alive:
            return self.step()  # Skip dead units

        # Tick cooldowns at start of unit's turn
        unit.tick_cooldowns()
        unit.turns_alive += 1

        # Tick buffs (burn damage, etc.)
        burn_damage = unit.tick_buffs()
        if burn_damage > 0:
            unit.take_damage(burn_damage)
            actions.append(BattleAction(
                type="burn_tick",
                target=unit.name,
                damage=burn_damage,
                message=f"{unit.name} takes {burn_damage} burn damage!",
            ))
            if not unit.alive:
                actions.append(BattleAction(
                    type="defeat",
                    target=unit.name,
                    message=f"{unit.name} has been defeated!",
                ))
                result = self._check_result()
                if result:
                    actions.append(BattleAction(type=result, message=f"{'Victory!' if result == 'victory' else 'Defeat...'}"))
                return actions

        # Check stun
        if unit.is_stunned:
            actions.append(BattleAction(
                type="stun_skip",
                source=unit.name,
                message=f"{unit.name} is stunned and cannot act!",
            ))
            return actions

        # Determine allies and enemies for this unit
        if unit.team == "player":
            allies = self.player_units
            enemies = self.enemy_units
        else:
            allies = self.enemy_units
            enemies = self.player_units

        # Try to use ability if off cooldown
        used_ability = False
        for ability_id in unit.ability_ids:
            ability = self.ability_registry.get(ability_id)
            if ability and unit.can_use_ability(ability_id):
                targets = get_targets(ability.targeting, unit, allies, enemies)
                if targets:
                    ability_actions = self._execute_ability(unit, ability, targets)
                    actions.extend(ability_actions)
                    unit.put_on_cooldown(ability_id, ability.cooldown)
                    used_ability = True
                    break

        # Auto-attack if no ability used
        if not used_ability:
            alive_enemies = [u for u in enemies if u.alive]
            if alive_enemies:
                target = random.choice(alive_enemies)
                actions.extend(self._execute_auto_attack(unit, target))

        # Check for end of round
        if self._current_index >= len(self._turn_order):
            self._waiting = True

        # Check win/lose
        result = self._check_result()
        if result:
            actions.append(BattleAction(type=result, message=f"{'Victory!' if result == 'victory' else 'Defeat...'}"))

        return actions

    def _calculate_damage(self, base_value: int, strength: int, scaling: float,
                          target_armor: int, ability_mods: list[str] | None = None) -> int:
        raw = base_value + int(strength * scaling)
        effective_armor = target_armor
        if ability_mods and "piercing" in ability_mods:
            effective_armor = int(effective_armor * 0.5)
        final = max(1, raw - int(effective_armor * DAMAGE_ARMOR_FACTOR))
        return final

    def _execute_ability(self, source: CombatUnit, ability: AbilityDef,
                         targets: list[CombatUnit]) -> list[BattleAction]:
        actions = []
        # Mana surge passive: +10% damage per turn
        damage_mult = 1.0
        if source.passive == "mana_surge":
            damage_mult = 1.0 + 0.1 * (source.turns_alive - 1)
        # Rage passive: +25% damage when below 50% HP
        if source.passive == "rage" and source.hp < source.max_hp * 0.5:
            damage_mult *= 1.25

        for target in targets:
            # Skip damage for 0-damage self-targeting abilities (e.g. summon)
            if ability.base_damage == 0 and ability.targeting == "self":
                # Still process effects (summon, buffs, etc.)
                for effect in ability.effects:
                    if effect.type == "stun":
                        target.add_buff("stun", effect.duration + 1)
                    elif effect.type == "summon":
                        actions.append(BattleAction(
                            type="summon",
                            source=source.name,
                            target=effect.enemy_id,
                            damage=effect.value,
                            message=f"{source.name} summons reinforcements!",
                        ))
                actions.append(BattleAction(
                    type="ability",
                    source=source.name,
                    target=source.name,
                    ability_name=ability.name,
                    damage=0,
                    message=f"{source.name} uses {ability.name}!",
                ))
                continue

            damage = self._calculate_damage(
                ability.base_damage, source.strength, ability.scaling,
                target.armor, source.ability_mods,
            )
            damage = int(damage * damage_mult)

            # Phase passive: 25% dodge
            if target.passive == "phase" and random.random() < 0.25:
                actions.append(BattleAction(
                    type="dodge",
                    source=source.name,
                    target=target.name,
                    ability_name=ability.name,
                    message=f"{target.name} phases through {ability.name}!",
                ))
                continue

            actual = target.take_damage(damage)

            # Flame aura passive: reflect 20%
            reflect_damage = 0
            if target.passive == "flame_aura" and actual > 0:
                reflect_damage = max(1, int(actual * 0.2))
                source.take_damage(reflect_damage)

            # Vampiric mod
            heal = 0
            if source.ability_mods and "vampiric" in source.ability_mods and actual > 0:
                heal = max(1, int(actual * 0.2))
                source.hp = min(source.max_hp, source.hp + heal)

            actions.append(BattleAction(
                type="ability",
                source=source.name,
                target=target.name,
                ability_name=ability.name,
                damage=actual,
                heal=heal,
                message=f"{source.name} uses {ability.name} on {target.name} for {actual} damage!",
            ))

            if reflect_damage > 0:
                actions.append(BattleAction(
                    type="reflect",
                    source=target.name,
                    target=source.name,
                    damage=reflect_damage,
                    message=f"{target.name}'s Flame Aura reflects {reflect_damage} damage!",
                ))

            # Apply ability effects
            for effect in ability.effects:
                if effect.type == "stun":
                    target.add_buff("stun", effect.duration + 1)
                    actions.append(BattleAction(
                        type="stun_applied",
                        source=source.name,
                        target=target.name,
                        message=f"{target.name} is stunned for {effect.duration} turn(s)!",
                    ))
                elif effect.type == "summon":
                    actions.append(BattleAction(
                        type="summon",
                        source=source.name,
                        target=effect.enemy_id,
                        damage=effect.value,
                        message=f"{source.name} summons {effect.value} {effect.enemy_id}!",
                    ))

            # Burning mod
            if source.ability_mods and "burning" in source.ability_mods:
                target.add_buff("burn", 2, value=3)
                actions.append(BattleAction(
                    type="burn_applied",
                    source=source.name,
                    target=target.name,
                    message=f"{target.name} is burning!",
                ))

            if not target.alive:
                actions.append(BattleAction(
                    type="defeat",
                    target=target.name,
                    message=f"{target.name} has been defeated!",
                ))

            if not source.alive:
                actions.append(BattleAction(
                    type="defeat",
                    target=source.name,
                    message=f"{source.name} has been defeated!",
                ))

        return actions

    def _execute_auto_attack(self, source: CombatUnit,
                             target: CombatUnit) -> list[BattleAction]:
        actions = []
        damage = self._calculate_damage(
            0, source.strength, 1.0, target.armor, source.ability_mods,
        )

        # Rage passive: +25% damage when below 50% HP
        if source.passive == "rage" and source.hp < source.max_hp * 0.5:
            damage = int(damage * 1.25)

        # Phase passive dodge
        if target.passive == "phase" and random.random() < 0.25:
            actions.append(BattleAction(
                type="dodge",
                source=source.name,
                target=target.name,
                message=f"{target.name} dodges {source.name}'s attack!",
            ))
            return actions

        actual = target.take_damage(damage)

        # Flame aura reflect
        reflect_damage = 0
        if target.passive == "flame_aura" and actual > 0:
            reflect_damage = max(1, int(actual * 0.2))
            source.take_damage(reflect_damage)

        # Vampiric
        heal = 0
        if source.ability_mods and "vampiric" in source.ability_mods and actual > 0:
            heal = max(1, int(actual * 0.2))
            source.hp = min(source.max_hp, source.hp + heal)

        actions.append(BattleAction(
            type="attack",
            source=source.name,
            target=target.name,
            damage=actual,
            heal=heal,
            message=f"{source.name} attacks {target.name} for {actual} damage!",
        ))

        if reflect_damage > 0:
            actions.append(BattleAction(
                type="reflect",
                source=target.name,
                target=source.name,
                damage=reflect_damage,
                message=f"{target.name}'s Flame Aura reflects {reflect_damage} damage!",
            ))

        # Burning mod on auto-attacks too
        if source.ability_mods and "burning" in source.ability_mods:
            target.add_buff("burn", 2, value=3)

        if not target.alive:
            actions.append(BattleAction(
                type="defeat",
                target=target.name,
                message=f"{target.name} has been defeated!",
            ))

        if not source.alive:
            actions.append(BattleAction(
                type="defeat",
                target=source.name,
                message=f"{source.name} has been defeated!",
            ))

        return actions

    def _check_result(self) -> str | None:
        players_alive = any(u.alive for u in self.player_units)
        enemies_alive = any(u.alive for u in self.enemy_units)

        if not enemies_alive:
            self.result = "victory"
            return "victory"
        if not players_alive:
            self.result = "lose"
            return "lose"
        return None
