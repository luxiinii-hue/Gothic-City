"""Map node dataclass."""

from dataclasses import dataclass, field


@dataclass
class MapNode:
    id: int
    row: int
    col: int
    node_type: str  # "combat", "elite", "shop", "treasure", "rest", "event", "boss", "start"
    connections: list[int] = field(default_factory=list)
    screen_x: int = 0
    screen_y: int = 0
    difficulty: int = 1
    visited: bool = False
