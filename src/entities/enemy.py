"""EnemyData dataclass."""

from dataclasses import dataclass, field
from src.entities.character import IdleConfig


@dataclass
class EnemyData:
    id: str
    name: str
    sprite: str | None
    max_hp: int
    strength: int
    armor: int
    speed: int
    abilities: list[str]
    tier: str
    gold_reward: int
    color: tuple = (200, 50, 50)
    idle_config: IdleConfig = field(default_factory=IdleConfig)
    on_death_ability: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "EnemyData":
        d = dict(data)
        idle_cfg = IdleConfig.from_dict(d.pop("idle_config", {}))
        return cls(
            id=d["id"],
            name=d["name"],
            sprite=d.get("sprite"),
            max_hp=d["max_hp"],
            strength=d.get("strength", 2),
            armor=d.get("armor", 0),
            speed=d.get("speed", 1),
            abilities=d.get("abilities", []),
            tier=d.get("tier", "normal"),
            gold_reward=d.get("gold_reward", 10),
            color=tuple(d.get("color", [200, 50, 50])),
            idle_config=idle_cfg,
            on_death_ability=d.get("on_death_ability", ""),
        )
