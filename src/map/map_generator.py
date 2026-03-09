"""Procedural branching map generator."""

import random
from src.map.map_node import MapNode
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_ROWS, MAP_COLS_MIDDLE


# Node type weights for middle rows
NODE_WEIGHTS = {
    "combat": 40,
    "elite": 15,
    "shop": 10,
    "treasure": 10,
    "rest": 15,
    "event": 10,
}


def generate_map() -> list[MapNode]:
    """Generate a branching map with MAP_ROWS rows."""
    nodes: list[MapNode] = []
    node_id = 0

    # Row 0: single start/combat node
    start_node = MapNode(id=node_id, row=0, col=1, node_type="combat", difficulty=1)
    nodes.append(start_node)
    node_id += 1

    # Row indices for each row
    row_indices: list[list[int]] = [[0]]  # row 0 node indices

    # Middle rows (1 to MAP_ROWS - 2)
    for row in range(1, MAP_ROWS - 1):
        row_node_ids = []
        for col in range(MAP_COLS_MIDDLE):
            ntype = _random_node_type(row)
            node = MapNode(id=node_id, row=row, col=col, node_type=ntype,
                           difficulty=row + 1)
            nodes.append(node)
            row_node_ids.append(node_id)
            node_id += 1
        row_indices.append(row_node_ids)

    # Last row: boss node
    boss_node = MapNode(id=node_id, row=MAP_ROWS - 1, col=1, node_type="boss",
                        difficulty=MAP_ROWS)
    nodes.append(boss_node)
    row_indices.append([node_id])
    node_id += 1

    # Generate connections between rows
    for row_idx in range(len(row_indices) - 1):
        current_row = row_indices[row_idx]
        next_row = row_indices[row_idx + 1]
        _connect_rows(nodes, current_row, next_row)

    # Ensure at least one rest node before the boss
    _ensure_rest_before_boss(nodes, row_indices)

    # Calculate screen positions
    _calculate_positions(nodes)

    return nodes


def _random_node_type(row: int) -> str:
    """Pick a random node type with weighted distribution."""
    weights = dict(NODE_WEIGHTS)
    # No elites in row 1
    if row == 1:
        weights.pop("elite", None)

    types = list(weights.keys())
    weight_values = [weights[t] for t in types]
    return random.choices(types, weights=weight_values, k=1)[0]


def _connect_rows(nodes: list[MapNode], current_ids: list[int],
                  next_ids: list[int]):
    """Connect nodes between two rows, ensuring no orphans."""
    # Each node in current row connects to 1-2 nodes in next row
    connected_next: set[int] = set()

    for cid in current_ids:
        # Connect to 1-2 nodes in next row
        num_connections = random.randint(1, min(2, len(next_ids)))
        targets = random.sample(next_ids, num_connections)
        for tid in targets:
            if tid not in nodes[cid].connections:
                nodes[cid].connections.append(tid)
            connected_next.add(tid)

    # Ensure no orphan nodes in next row
    for nid in next_ids:
        if nid not in connected_next:
            # Connect from random node in current row
            source = random.choice(current_ids)
            if nid not in nodes[source].connections:
                nodes[source].connections.append(nid)


def _ensure_rest_before_boss(nodes: list[MapNode],
                             row_indices: list[list[int]]):
    """Make sure at least one node in the row before boss is a rest node."""
    if len(row_indices) < 3:
        return
    pre_boss_row = row_indices[-2]
    has_rest = any(nodes[nid].node_type == "rest" for nid in pre_boss_row)
    if not has_rest:
        # Convert one random node to rest
        convert_id = random.choice(pre_boss_row)
        nodes[convert_id].node_type = "rest"


def _calculate_positions(nodes: list[MapNode]):
    """Set screen_x, screen_y for each node."""
    # Vertical layout: top to bottom
    y_start = 100
    y_end = SCREEN_HEIGHT - 80
    x_center = SCREEN_WIDTH // 2 - 100  # offset left for sidebar

    # Collect rows
    rows: dict[int, list[MapNode]] = {}
    for node in nodes:
        rows.setdefault(node.row, []).append(node)

    max_row = max(rows.keys()) if rows else 0
    row_spacing = (y_end - y_start) / max(max_row, 1)

    for row_num, row_nodes in rows.items():
        y = int(y_start + row_num * row_spacing)
        count = len(row_nodes)
        col_spacing = 180
        x_start = x_center - (count - 1) * col_spacing // 2

        for i, node in enumerate(row_nodes):
            node.screen_x = x_start + i * col_spacing
            node.screen_y = y
