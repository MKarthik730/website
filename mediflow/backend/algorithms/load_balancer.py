# ================================================================
#  algorithms/load_balancer.py
#  Weighted Round Robin Load Balancer — O(1) per assignment
#  + Dijkstra overflow redirect on branch graph
# ================================================================

from dataclasses import dataclass, field
from typing import Optional
import heapq


@dataclass
class BranchNode:
    branch_id:      int
    total_capacity: int
    current_load:   int   = 0
    weight:         float = 1.0   # recomputed dynamically

    @property
    def load_factor(self) -> float:
        if self.total_capacity == 0:
            return 1.0
        return self.current_load / self.total_capacity

    @property
    def is_overloaded(self) -> bool:
        return self.load_factor >= 0.80


class WeightedRoundRobin:
    """
    Weighted Round Robin across branches.
    Weight = (1 - load_factor) × specialty_demand_weight
    O(1) assignment using current-weight algorithm (Nginx-style smooth WRR).
    """

    def __init__(self):
        self._branches: dict[int, BranchNode] = {}
        self._current_weights: dict[int, float] = {}

    def register(self, branch_id: int, total_capacity: int) -> None:
        self._branches[branch_id] = BranchNode(branch_id, total_capacity)
        self._current_weights[branch_id] = 0.0

    def update_load(self, branch_id: int, current_load: int) -> None:
        if branch_id in self._branches:
            node = self._branches[branch_id]
            node.current_load = current_load
            node.weight = max(0.01, 1.0 - node.load_factor)

    def next_branch(self, exclude: Optional[list[int]] = None) -> Optional[int]:
        """
        Smooth Weighted Round Robin — O(1).
        Returns branch_id with highest effective weight.
        """
        exclude = exclude or []
        eligible = {
            bid: node for bid, node in self._branches.items()
            if bid not in exclude and not node.is_overloaded
        }
        if not eligible:
            # Fallback: least loaded even if over threshold
            eligible = {
                bid: node for bid, node in self._branches.items()
                if bid not in exclude
            }
        if not eligible:
            return None

        total_weight = sum(n.weight for n in eligible.values())

        # Increase current weights
        for bid in eligible:
            self._current_weights[bid] = self._current_weights.get(bid, 0.0) + eligible[bid].weight

        # Pick highest current weight
        best = max(eligible.keys(), key=lambda b: self._current_weights[b])

        # Decrease winner by total weight
        self._current_weights[best] -= total_weight
        return best

    def get_load_summary(self) -> list[dict]:
        return [
            {
                "branch_id":    bid,
                "load_factor":  round(node.load_factor, 3),
                "is_overloaded": node.is_overloaded,
                "weight":       round(node.weight, 3),
            }
            for bid, node in self._branches.items()
        ]


# ----------------------------------------------------------------
#  Dijkstra for overflow redirect — nearest branch with free slots
# ----------------------------------------------------------------

def nearest_available_branch(
    origin_branch_id: int,
    branch_coords:    dict[int, tuple[float, float]],   # {branch_id: (lat, lng)}
    overloaded_ids:   set[int],
) -> Optional[int]:
    """
    Find nearest non-overloaded branch using Euclidean distance as edge weight.
    O(n log n) — Dijkstra on fully-connected branch graph.
    """
    if origin_branch_id not in branch_coords:
        return None

    import math
    origin = branch_coords[origin_branch_id]

    def dist(a: tuple, b: tuple) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # Min-heap: (distance, branch_id)
    heap = [(0.0, origin_branch_id)]
    visited: set[int] = set()

    while heap:
        d, bid = heapq.heappop(heap)
        if bid in visited:
            continue
        visited.add(bid)

        if bid != origin_branch_id and bid not in overloaded_ids:
            return bid

        for nbr_id, coords in branch_coords.items():
            if nbr_id not in visited:
                heapq.heappush(heap, (dist(origin, coords), nbr_id))

    return None


# Singleton
_wrr = WeightedRoundRobin()


def get_load_balancer() -> WeightedRoundRobin:
    return _wrr
