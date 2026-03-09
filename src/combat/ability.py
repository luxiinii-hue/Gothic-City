"""Ability definitions and registry."""

from dataclasses import dataclass, field


@dataclass
class AbilityEffect:
    type: str  # "stun", "burn", "summon", etc.
    duration: int = 0
    value: int = 0
    enemy_id: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "AbilityEffect":
        return cls(
            type=data["type"],
            duration=data.get("duration", 0),
            value=data.get("value", 0),
            enemy_id=data.get("enemy_id", ""),
        )


@dataclass
class AbilityDef:
    id: str
    name: str
    description: str
    targeting: str  # "single_enemy", "all_enemies", "single_ally", "all_allies", "self"
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


class AbilityRegistry:
    def __init__(self):
        self._abilities: dict[str, AbilityDef] = {}

    def load(self, abilities_data: list[dict]):
        for data in abilities_data:
            ability = AbilityDef.from_dict(data)
            self._abilities[ability.id] = ability

    def get(self, ability_id: str) -> AbilityDef | None:
        return self._abilities.get(ability_id)

    def get_by_name(self, name: str) -> AbilityDef | None:
        """Look up ability by display name (e.g. 'Shadow Bolt')."""
        for ability in self._abilities.values():
            if ability.name == name:
                return ability
        return None
