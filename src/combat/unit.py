"""Runtime combat unit wrapper — mutable state around static definitions."""

from dataclasses import dataclass, field


@dataclass
class Buff:
    type: str  # "burn", "stun", "mana_surge"
    duration: int
    value: float = 0


class CombatUnit:
    def __init__(self, unit_id: str, name: str, team: str,
                 max_hp: int, strength: int, armor: int, speed: int,
                 ability_ids: list[str], passive: str | None = None,
                 ability_mods: list[str] | None = None):
        self.id = unit_id
        self.name = name
        self.team = team  # "player" or "enemy"
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.armor = armor
        self.speed = speed
        self.block = 0
        self.ability_ids = list(ability_ids)
        self.passive = passive
        self.ability_mods = ability_mods or []

        # Cooldown tracking: ability_id -> turns remaining
        self.cooldowns: dict[str, int] = {}
        self.buffs: list[Buff] = []
        self.stunned = False
        self.alive = True

        # Track stats for mana surge passive
        self.turns_alive = 0

    @property
    def is_stunned(self) -> bool:
        return any(b.type == "stun" and b.duration > 0 for b in self.buffs)

    def tick_cooldowns(self):
        for ability_id in list(self.cooldowns):
            self.cooldowns[ability_id] = max(0, self.cooldowns[ability_id] - 1)

    def tick_buffs(self):
        damage = 0
        for buff in self.buffs:
            if buff.type == "burn" and buff.duration > 0:
                damage += int(buff.value)
            buff.duration -= 1
        self.buffs = [b for b in self.buffs if b.duration > 0]
        return damage

    def can_use_ability(self, ability_id: str) -> bool:
        return self.cooldowns.get(ability_id, 0) <= 0

    def put_on_cooldown(self, ability_id: str, cooldown: int):
        self.cooldowns[ability_id] = cooldown

    def add_buff(self, buff_type: str, duration: int, value: float = 0):
        self.buffs.append(Buff(type=buff_type, duration=duration, value=value))

    def take_damage(self, amount: int) -> int:
        """Apply damage after block. Returns actual HP lost."""
        remaining = amount
        if self.block > 0:
            blocked = min(self.block, remaining)
            self.block -= blocked
            remaining -= blocked
        if remaining > 0:
            self.hp = max(0, self.hp - remaining)
        if self.hp <= 0:
            self.alive = False
        return remaining

    @classmethod
    def from_character(cls, char_data, ability_mods: list[str] | None = None,
                       stat_boosts: dict | None = None) -> "CombatUnit":
        max_hp = char_data.max_hp
        strength = char_data.strength
        armor = char_data.armor
        speed = char_data.speed

        if stat_boosts:
            max_hp += stat_boosts.get("max_hp", 0)
            strength += stat_boosts.get("strength", 0)
            armor += stat_boosts.get("armor", 0)
            speed += stat_boosts.get("speed", 0)

        # Determine passive based on role
        passive = None
        if char_data.id == "acoc1":
            passive = "phase"  # 25% dodge
        elif char_data.id == "acoc2":
            passive = "flame_aura"  # reflect 20% damage
        elif char_data.id == "acoc3":
            passive = "mana_surge"  # +10% ability damage per turn
        elif char_data.id == "acoc4":
            passive = "rage"  # +25% damage when below 50% HP

        return cls(
            unit_id=char_data.id,
            name=char_data.name,
            team="player",
            max_hp=max_hp,
            strength=strength,
            armor=armor,
            speed=speed,
            ability_ids=list(char_data.abilities),
            passive=passive,
            ability_mods=ability_mods,
        )

    @classmethod
    def from_enemy(cls, enemy_data) -> "CombatUnit":
        return cls(
            unit_id=enemy_data.id,
            name=enemy_data.name,
            team="enemy",
            max_hp=enemy_data.max_hp,
            strength=enemy_data.strength,
            armor=enemy_data.armor,
            speed=enemy_data.speed,
            ability_ids=list(enemy_data.abilities),
        )
