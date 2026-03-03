# ================================================================
#  algorithms/bipartite_matching.py
#  Doctor-Patient Matching — Hopcroft-Karp Bipartite
#  O(E √V) — matches patients to doctor-slot pairs optimally
# ================================================================

from collections import deque
from typing import Optional


class HopcroftKarp:
    """
    Hopcroft-Karp maximum bipartite matching.
    Left nodes  = patients (0..n_patients-1)
    Right nodes = doctor-slot pairs (0..n_slots-1)
    """

    INF = float("inf")

    def __init__(self, n_patients: int, n_slots: int):
        self.n   = n_patients
        self.m   = n_slots
        # adj[patient] = list of compatible slot indices
        self.adj: list[list[int]] = [[] for _ in range(n_patients)]

        self.match_patient = [-1] * n_patients   # match_patient[p] = slot
        self.match_slot    = [-1] * n_slots       # match_slot[s]    = patient
        self.dist          = [0.0] * n_patients

    def add_edge(self, patient: int, slot: int) -> None:
        """Add compatibility edge between patient and slot."""
        self.adj[patient].append(slot)

    def _bfs(self) -> bool:
        queue = deque()
        for p in range(self.n):
            if self.match_patient[p] == -1:
                self.dist[p] = 0
                queue.append(p)
            else:
                self.dist[p] = self.INF

        found = False
        while queue:
            p = queue.popleft()
            for s in self.adj[p]:
                np = self.match_slot[s]
                if np == -1:
                    found = True
                elif self.dist[np] == self.INF:
                    self.dist[np] = self.dist[p] + 1
                    queue.append(np)
        return found

    def _dfs(self, p: int) -> bool:
        for s in self.adj[p]:
            np = self.match_slot[s]
            if np == -1 or (self.dist[np] == self.dist[p] + 1 and self._dfs(np)):
                self.match_patient[p] = s
                self.match_slot[s]    = p
                return True
        self.dist[p] = self.INF
        return False

    def max_matching(self) -> int:
        """Run Hopcroft-Karp. Returns number of matched pairs."""
        matching = 0
        while self._bfs():
            for p in range(self.n):
                if self.match_patient[p] == -1:
                    if self._dfs(p):
                        matching += 1
        return matching

    def get_matches(self) -> dict[int, int]:
        """Return {patient_index: slot_index} for all matched pairs."""
        return {p: s for p, s in enumerate(self.match_patient) if s != -1}


def match_patients_to_slots(
    patient_ids:        list[int],
    slot_ids:           list[int],
    compatibility:      dict[int, list[int]],   # {patient_id: [compatible slot_ids]}
) -> dict[int, int]:
    """
    High-level wrapper.
    Returns {patient_id: slot_id} optimal matching.
    """
    if not patient_ids or not slot_ids:
        return {}

    p_index = {pid: i for i, pid in enumerate(patient_ids)}
    s_index = {sid: i for i, sid in enumerate(slot_ids)}

    hk = HopcroftKarp(len(patient_ids), len(slot_ids))

    for pid, compatible_slots in compatibility.items():
        if pid not in p_index:
            continue
        for sid in compatible_slots:
            if sid in s_index:
                hk.add_edge(p_index[pid], s_index[sid])

    hk.max_matching()
    raw = hk.get_matches()

    p_rev = {i: pid for pid, i in p_index.items()}
    s_rev = {i: sid for sid, i in s_index.items()}

    return {p_rev[pi]: s_rev[si] for pi, si in raw.items()}
