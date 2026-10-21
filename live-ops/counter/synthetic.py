"""Scripted crossings for --test-video synthetic. No camera, no model weights."""
from __future__ import annotations


def script(width: int = 640) -> list[list[tuple[int, float]]]:
    """Frames of (id, x). Two people in, one out, then a stall (stream loss drill)."""
    line = width / 2
    frames: list[list[tuple[int, float]]] = []

    def walk(tid: int, start: float, end: float, steps: int) -> None:
        for i in range(steps):
            x = start + (end - start) * (i / (steps - 1))
            frames.append([(tid, x)])

    walk(1, line - 80, line + 80, 8)
    walk(2, line - 80, line + 80, 8)
    walk(1, line + 80, line - 80, 8)
    frames.extend([] for _ in range(5))
    return frames
