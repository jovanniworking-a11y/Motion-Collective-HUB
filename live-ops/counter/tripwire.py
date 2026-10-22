"""Virtual trip-line. Tracks cross a vertical line; direction sets in vs out.

Coordinates are pixels, x increasing to the right. Default line is mid-frame.
Left-to-right is IN (toward the room). Right-to-left is OUT.
A track counts once per direction change across the line, not on every frame.
"""
from __future__ import annotations


class TripWire:
    def __init__(self, line_x: float, margin: float = 8.0):
        self.line_x = float(line_x)
        self.margin = float(margin)
        self._side: dict[int, str] = {}
        self._miss: dict[int, int] = {}
        self.grace = 8
        self.ins = 0
        self.outs = 0
        self.occupancy = 0
        self.peak = 0

    def _band(self, x: float) -> str | None:
        if x < self.line_x - self.margin:
            return "left"
        if x > self.line_x + self.margin:
            return "right"
        return None

    def update(self, tracks: list[tuple[int, float]]) -> None:
        """tracks: (track_id, center_x) for this frame."""
        seen = set()
        for tid, x in tracks:
            seen.add(tid)
            self._miss[tid] = 0
            side = self._band(x)
            if side is None:
                continue
            prev = self._side.get(tid)
            self._side[tid] = side
            if prev is None or prev == side:
                continue
            if prev == "left" and side == "right":
                self.ins += 1
                self.occupancy += 1
            elif prev == "right" and side == "left":
                self.outs += 1
                self.occupancy = max(0, self.occupancy - 1)
            self.peak = max(self.peak, self.occupancy)
        for tid in list(self._side):
            if tid in seen:
                continue
            self._miss[tid] = self._miss.get(tid, 0) + 1
            if self._miss[tid] > self.grace:
                del self._side[tid]
                del self._miss[tid]

    def snapshot(self) -> dict:
        return {
            "occupancy": self.occupancy,
            "ins": self.ins,
            "outs": self.outs,
            "peak": self.peak,
        }
