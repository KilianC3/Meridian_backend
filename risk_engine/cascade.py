"""Shock propagation utilities."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, Iterable, List, Mapping


class Edge(Mapping[str, Any]):
    src_factor: int
    dst_factor: int
    beta: float
    lag_days: int | None
    confidence: float | None

    def __init__(self, data: Mapping[str, Any]):
        self.src_factor = int(data["src_factor"])
        self.dst_factor = int(data["dst_factor"])
        self.beta = float(data.get("beta", 0.0) or 0.0)
        self.lag_days = int(data.get("lag_days", 0) or 0)
        self.confidence = float(data.get("confidence", 1.0) or 1.0)
        self._data = {
            "src_factor": self.src_factor,
            "dst_factor": self.dst_factor,
            "beta": self.beta,
            "lag_days": self.lag_days,
            "confidence": self.confidence,
        }

    def __getitem__(self, key: str):  # type: ignore[override]
        return self._data[key]

    def __iter__(self):  # type: ignore[override]
        return iter(self._data)

    def __len__(self) -> int:  # type: ignore[override]
        return len(self._data)


def propagate_shock(
    edges: Iterable[Mapping[str, float | int | None]],
    start_factor: int,
    shock: float,
    horizon: int = 3,
    decay: float = 0.7,
) -> Dict[int, float]:
    """Propagate a shock through a factor graph.

    The algorithm performs a breadth-first traversal up to ``horizon`` hops,
    attenuating the shock by ``decay`` at each hop and by edge beta and
    confidence.
    """
    adj: Dict[int, List[Edge]] = defaultdict(list)
    for e in edges:
        edge = Edge(e)
        adj[edge.src_factor].append(edge)

    impacts: Dict[int, float] = defaultdict(float)
    queue: deque[tuple[int, float, int]] = deque([(start_factor, shock, 0)])

    while queue:
        node, val, depth = queue.popleft()
        impacts[node] += val
        if depth >= horizon:
            continue
        for edge in adj.get(node, []):
            next_val = (
                val * edge.beta * (edge.confidence or 1.0) * (decay ** (depth + 1))
            )
            queue.append((edge.dst_factor, next_val, depth + 1))
    return dict(impacts)
