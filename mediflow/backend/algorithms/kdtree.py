# ================================================================
#  algorithms/kdtree.py
#  K-d Tree Branch Search — O(log n) nearest neighbor
#  Finds closest available branch by GPS coordinates
# ================================================================

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class BranchPoint:
    branch_id:   int
    lat:         float
    lng:         float
    is_available: bool = True   # False if overloaded / closed


class KDNode:
    __slots__ = ("point", "left", "right")

    def __init__(self, point: BranchPoint):
        self.point: BranchPoint             = point
        self.left:  Optional["KDNode"]      = None
        self.right: Optional["KDNode"]      = None


class KDTree:
    """
    2D K-d Tree for branch nearest-neighbor search.
    Build: O(n log n)
    Query: O(log n) average
    """

    def __init__(self):
        self._root: Optional[KDNode] = None
        self._points: list[BranchPoint] = []

    def build(self, points: list[BranchPoint]) -> None:
        """Build tree from list of branch points."""
        self._points = points
        self._root = self._build(list(points), depth=0)

    def _build(self, pts: list[BranchPoint], depth: int) -> Optional[KDNode]:
        if not pts:
            return None
        axis = depth % 2   # 0=lat, 1=lng
        pts.sort(key=lambda p: p.lat if axis == 0 else p.lng)
        mid = len(pts) // 2
        node = KDNode(pts[mid])
        node.left  = self._build(pts[:mid],   depth + 1)
        node.right = self._build(pts[mid+1:], depth + 1)
        return node

    def insert(self, point: BranchPoint) -> None:
        """Insert a new branch into existing tree."""
        self._points.append(point)
        self._root = self._insert(self._root, point, depth=0)

    def _insert(self, node: Optional[KDNode], point: BranchPoint, depth: int) -> KDNode:
        if node is None:
            return KDNode(point)
        axis = depth % 2
        val_new  = point.lat if axis == 0 else point.lng
        val_node = node.point.lat if axis == 0 else node.point.lng
        if val_new < val_node:
            node.left  = self._insert(node.left,  point, depth + 1)
        else:
            node.right = self._insert(node.right, point, depth + 1)
        return node

    @staticmethod
    def _dist(a: BranchPoint, b: BranchPoint) -> float:
        return math.sqrt((a.lat - b.lat) ** 2 + (a.lng - b.lng) ** 2)

    def nearest(
        self,
        query_lat:         float,
        query_lng:         float,
        exclude_branch_ids: Optional[set[int]] = None,
        only_available:    bool = True,
    ) -> Optional[BranchPoint]:
        """
        Find nearest available branch to (query_lat, query_lng).
        O(log n) average.
        """
        query = BranchPoint(branch_id=-1, lat=query_lat, lng=query_lng)
        exclude = exclude_branch_ids or set()
        best = [None, float("inf")]

        def search(node: Optional[KDNode], depth: int) -> None:
            if node is None:
                return
            pt = node.point
            if pt.branch_id not in exclude:
                if not only_available or pt.is_available:
                    d = self._dist(query, pt)
                    if d < best[1]:
                        best[0] = pt
                        best[1] = d

            axis = depth % 2
            diff = (query.lat - pt.lat) if axis == 0 else (query.lng - pt.lng)
            close, away = (node.left, node.right) if diff < 0 else (node.right, node.left)

            search(close, depth + 1)
            if diff ** 2 < best[1]:
                search(away, depth + 1)

        search(self._root, 0)
        return best[0]

    def k_nearest(
        self,
        query_lat:          float,
        query_lng:          float,
        k:                  int = 3,
        exclude_branch_ids: Optional[set[int]] = None,
        only_available:     bool = True,
    ) -> list[BranchPoint]:
        """Return k nearest available branches sorted by distance."""
        exclude = exclude_branch_ids or set()
        query = BranchPoint(branch_id=-1, lat=query_lat, lng=query_lng)
        results = []

        for pt in self._points:
            if pt.branch_id in exclude:
                continue
            if only_available and not pt.is_available:
                continue
            results.append((self._dist(query, pt), pt))

        results.sort(key=lambda x: x[0])
        return [pt for _, pt in results[:k]]


# Singleton
_kdtree = KDTree()


def get_kdtree() -> KDTree:
    return _kdtree


def rebuild_kdtree(branches: list[dict]) -> None:
    """
    Rebuild tree from DB branch records.
    Call on startup and when branches change.
    branches = [{"branch_id": 1, "latitude": 12.9, "longitude": 80.1, "is_active": True}, ...]
    """
    points = [
        BranchPoint(
            branch_id=b["branch_id"],
            lat=b.get("latitude") or 0.0,
            lng=b.get("longitude") or 0.0,
            is_available=b.get("is_active", True),
        )
        for b in branches
        if b.get("latitude") and b.get("longitude")
    ]
    _kdtree.build(points)
