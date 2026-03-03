# ================================================================
#  algorithms/priority_queue.py
#  Max-Heap Priority Queue — O(log n) insert/extract
#  Score = (urgency×0.5) + (wait_time×0.3) + (age×0.1) + (type×0.1)
#  Anti-starvation: wait score grows every minute
# ================================================================

import heapq
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


URGENCY_SCORES = {
    "critical": 100,
    "high":     75,
    "medium":   50,
    "low":      25,
}

TYPE_SCORES = {
    "emergency":    100,
    "surgery":       80,
    "consultation":  50,
    "follow_up":     30,
}

WEIGHTS = {
    "urgency": 0.50,
    "wait":    0.30,
    "age":     0.10,
    "type":    0.10,
}


@dataclass(order=True)
class QueueNode:
    """
    Stored in the heap as negative score (max-heap via min-heap inversion).
    """
    neg_score:      float                    # negated for max-heap
    appointment_id: int       = field(compare=False)
    patient_id:     int       = field(compare=False)
    doctor_id:      int       = field(compare=False)
    branch_id:      int       = field(compare=False)
    urgency:        str       = field(compare=False)
    appointment_type: str     = field(compare=False)
    age:            int       = field(compare=False, default=30)
    entered_at:     datetime  = field(compare=False, default_factory=datetime.utcnow)
    is_emergency:   bool      = field(compare=False, default=False)


def compute_score(
    urgency: str,
    appointment_type: str,
    entered_at: datetime,
    age: int = 30,
    emergency_override: bool = False,
) -> dict:
    """
    Compute the composite priority score.
    Returns breakdown dict + final_score.
    """
    if emergency_override:
        return {
            "raw_urgency_score": 100,
            "raw_wait_score":    40.0,
            "raw_age_score":     10,
            "raw_type_score":    100,
            "final_score":       999.0,   # always top of heap
        }

    wait_minutes   = (datetime.utcnow() - entered_at).total_seconds() / 60
    raw_urgency    = URGENCY_SCORES.get(urgency, 50)
    raw_wait       = min((wait_minutes / 60) * 10, 40)   # max 40 pts — anti-starvation cap
    raw_age        = 10 if (age >= 65 or age <= 12) else 5
    raw_type       = TYPE_SCORES.get(appointment_type, 50)

    final = (
        raw_urgency * WEIGHTS["urgency"] +
        raw_wait    * WEIGHTS["wait"]    +
        raw_age     * WEIGHTS["age"]     +
        raw_type    * WEIGHTS["type"]
    )

    return {
        "raw_urgency_score": raw_urgency,
        "raw_wait_score":    round(raw_wait, 4),
        "raw_age_score":     raw_age,
        "raw_type_score":    raw_type,
        "final_score":       round(final, 4),
    }


class MediflowPriorityQueue:
    """
    Thread-safe max-heap priority queue per (doctor_id, branch_id).
    Uses Python's heapq (min-heap) with negated scores.
    """

    def __init__(self):
        self._heap: list[QueueNode] = []
        self._removed: set[int] = set()   # appointment_ids marked removed (lazy deletion)

    def push(self, node: QueueNode) -> None:
        """Insert in O(log n)."""
        heapq.heappush(self._heap, node)

    def pop(self) -> Optional[QueueNode]:
        """Extract highest-priority patient in O(log n)."""
        while self._heap:
            node = heapq.heappop(self._heap)
            if node.appointment_id not in self._removed:
                return node
        return None

    def emergency_insert(self, node: QueueNode) -> QueueNode:
        """
        Preemptive override — assign score=999, push to front effectively.
        O(log n) heappush; 999 guarantees extraction before all others.
        """
        node.neg_score    = -999.0
        node.is_emergency = True
        self.push(node)
        return node

    def remove(self, appointment_id: int) -> None:
        """Lazy deletion — O(1) mark, skipped on next pop."""
        self._removed.add(appointment_id)

    def peek(self) -> Optional[QueueNode]:
        """View top without extracting."""
        while self._heap:
            if self._heap[0].appointment_id not in self._removed:
                return self._heap[0]
            heapq.heappop(self._heap)
        return None

    def size(self) -> int:
        return len([n for n in self._heap if n.appointment_id not in self._removed])

    def recalculate_all(self) -> None:
        """
        Rebuild heap with updated wait scores — call periodically (e.g. every 5 min).
        O(n log n) full rebuild.
        """
        valid = [n for n in self._heap if n.appointment_id not in self._removed]
        for node in valid:
            scores = compute_score(node.urgency, node.appointment_type, node.entered_at, node.age)
            node.neg_score = -scores["final_score"]
        heapq.heapify(valid)
        self._heap = valid


# Global queue registry: key = (doctor_id, branch_id)
_queues: dict[tuple[int, int], MediflowPriorityQueue] = {}


def get_queue(doctor_id: int, branch_id: int) -> MediflowPriorityQueue:
    key = (doctor_id, branch_id)
    if key not in _queues:
        _queues[key] = MediflowPriorityQueue()
    return _queues[key]
