# ================================================================
#  algorithms/interval_tree.py
#  Slot Conflict Detection — O(log n) per query
#  Uses a sorted list of intervals; binary search for overlap check
# ================================================================

import bisect
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Interval:
    start:      datetime
    end:        datetime
    slot_id:    int
    doctor_id:  int
    branch_id:  int

    def overlaps(self, other_start: datetime, other_end: datetime) -> bool:
        return self.start < other_end and other_start < self.end


class IntervalTree:
    """
    Lightweight interval tree per doctor.
    Stores sorted intervals and uses bisect for O(log n) conflict detection.
    """

    def __init__(self):
        # Sorted by start time
        self._intervals: list[Interval] = []
        self._starts:    list[datetime] = []   # parallel list for bisect

    def insert(self, interval: Interval) -> None:
        """Insert a booked slot. O(log n) bisect + O(n) list insert (acceptable for scheduling)."""
        idx = bisect.bisect_left(self._starts, interval.start)
        self._starts.insert(idx, interval.start)
        self._intervals.insert(idx, interval)

    def has_conflict(
        self,
        doctor_id: int,
        start: datetime,
        end: datetime,
        exclude_slot_id: Optional[int] = None,
    ) -> Optional[Interval]:
        """
        Check if a proposed (start, end) conflicts with any booked interval
        for the given doctor. Returns conflicting Interval or None.
        O(log n) to find start position, O(k) to scan nearby — k usually very small.
        """
        idx = bisect.bisect_left(self._starts, start)

        # Check backward (slots that start before but may end after)
        for i in range(max(0, idx - 5), min(len(self._intervals), idx + 10)):
            iv = self._intervals[i]
            if iv.doctor_id != doctor_id:
                continue
            if exclude_slot_id and iv.slot_id == exclude_slot_id:
                continue
            if iv.overlaps(start, end):
                return iv
        return None

    def remove(self, slot_id: int) -> None:
        """Remove a slot when cancelled."""
        for i, iv in enumerate(self._intervals):
            if iv.slot_id == slot_id:
                self._intervals.pop(i)
                self._starts.pop(i)
                return

    def get_free_slots(
        self,
        doctor_id: int,
        day_start: datetime,
        day_end: datetime,
        slot_duration_mins: int = 15,
    ) -> list[tuple[datetime, datetime]]:
        """
        Return list of free (start, end) windows for a doctor on a given day.
        """
        booked = sorted(
            [iv for iv in self._intervals if iv.doctor_id == doctor_id
             and iv.start >= day_start and iv.end <= day_end],
            key=lambda x: x.start,
        )
        free = []
        cursor = day_start
        from datetime import timedelta
        delta = timedelta(minutes=slot_duration_mins)

        for iv in booked:
            while cursor + delta <= iv.start:
                free.append((cursor, cursor + delta))
                cursor += delta
            cursor = max(cursor, iv.end)

        while cursor + delta <= day_end:
            free.append((cursor, cursor + delta))
            cursor += delta

        return free


# Global registry per doctor
_trees: dict[int, IntervalTree] = {}


def get_tree(doctor_id: int) -> IntervalTree:
    if doctor_id not in _trees:
        _trees[doctor_id] = IntervalTree()
    return _trees[doctor_id]
