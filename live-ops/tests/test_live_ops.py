"""No camera, no DJM, no projector. These are the table tests."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tripwire = _load("motion_tripwire", ROOT / "counter" / "tripwire.py")
synthetic = _load("motion_synthetic", ROOT / "counter" / "synthetic.py")
dspmod = _load("motion_dsp", ROOT / "fader" / "dsp.py")
sys.path.insert(0, str(ROOT / "counter"))
counter = _load("motion_counter_server", ROOT / "counter" / "server.py")

TripWire = tripwire.TripWire
script = synthetic.script
process = dspmod.process


def test_two_in_one_out():
    w = TripWire(320)
    for frame in script():
        if frame:
            w.update(frame)
    assert w.ins == 2
    assert w.outs == 1
    assert w.occupancy == 1
    assert w.peak == 2


def test_occupancy_never_negative():
    w = TripWire(100)
    w.update([(1, 200)])
    w.update([(1, 10)])
    w.update([(1, 200)])
    w.update([(1, 10)])
    assert w.occupancy == 0
    assert w.outs == 2
    assert w.ins == 1


def test_limiter_and_mute():
    hot = np.ones(64, dtype=np.float32)
    y, limited = process(hot, gain=1.0, mute=False)
    assert limited
    assert np.max(np.abs(y)) <= 1.0
    z, _ = process(hot, gain=1.0, mute=True)
    assert np.all(z == 0)


def test_dashboard_thresholds_and_palette():
    html = (ROOT / "dashboard" / "index.html").read_text()
    assert "#0A0810" in html and "#EDE6DA" in html
    assert ">= 65" in html
    assert ">= 55" in html
    assert "Hold the door" in html
    assert 'view") === "door"' in html
    assert "CHECK IN" in html


def test_dropout_still_counts_the_cross():
    w = TripWire(100)
    w.update([(7, 40)])
    for _ in range(5):
        w.update([])
    w.update([(7, 180)])
    assert w.ins == 1
    assert w.occupancy == 1


def test_check_in_only_when_camera_red():
    counter.STATE = counter.Counter()
    counter.STATE.observe([(1, 10)])
    assert counter.STATE.check_in() is False
    counter.STATE.last_frame -= 5
    assert counter.STATE.check_in() is True
    assert counter.STATE.payload()["occupancy"] == 1
