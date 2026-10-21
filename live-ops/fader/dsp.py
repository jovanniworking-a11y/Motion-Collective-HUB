"""Software gain + tanh limiter. The laptop is in the PA path. Keep this boring."""
from __future__ import annotations

import numpy as np


def process(block: np.ndarray, gain: float, mute: bool, drive: float = 1.2) -> tuple[np.ndarray, bool]:
    """Returns (audio, limiter_active). gain is 0..1 linear. mute wins."""
    x = np.asarray(block, dtype=np.float32)
    if mute or gain <= 0:
        return np.zeros_like(x), False
    y = np.tanh(x * gain * drive) / np.tanh(drive)
    limited = bool(np.max(np.abs(x * gain)) > 0.9)
    return y.astype(np.float32), limited
