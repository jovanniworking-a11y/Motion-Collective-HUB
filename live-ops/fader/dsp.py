"""Software gain + tanh limiter. The laptop is in the PA path. Keep this boring."""
from __future__ import annotations

import numpy as np


def process(block: np.ndarray, gain: float, mute: bool, drive: float = 1.2) -> tuple[np.ndarray, bool]:
    """Returns (audio, limiter_active). gain is 0..1 linear. mute wins."""
    x = np.asarray(block, dtype=np.float32)
    if mute or gain <= 0:
        return np.zeros_like(x), False
    # Same dtype on both tanhs, then a hard clip. Float32 tanh(1.2)/tanh(1.2)
    # can land at 1.0000001, which is already over full scale on the PA.
    drive_f = np.float32(drive)
    y = np.tanh(x * np.float32(gain) * drive_f) / np.tanh(drive_f)
    y = np.clip(y, -1.0, 1.0)
    limited = bool(np.max(np.abs(x * gain)) > 0.9)
    return y.astype(np.float32), limited
