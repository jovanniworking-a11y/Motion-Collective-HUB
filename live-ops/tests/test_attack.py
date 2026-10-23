"""What someone on the Wi-Fi can try. These must fail."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "counter"))

import lan

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

counter = _load("attack_counter", ROOT / "counter" / "server.py")
fader = _load("attack_fader", ROOT / "fader" / "server.py")


def test_wrong_token_rejected():
    lan.TOKEN = "night-token"
    assert lan.allowed("/?token=night-token")
    assert not lan.allowed("/")
    assert not lan.allowed("/?token=night-tokeN")
    assert not lan.allowed("/?token=" + "night-token" + "x")
    lan.TOKEN = "a+b"
    assert lan.allowed("/?token=a%2Bb")
    assert not lan.allowed("/?token=a b")


def test_checkin_flood_and_cap():
    counter.STATE = counter.Counter()
    counter.STATE.last_frame -= 5
    assert counter.STATE.check_in() is True
    assert counter.STATE.check_in() is False
    counter.STATE._last_check -= 2
    counter.STATE.wire.occupancy = counter.CAP
    assert counter.STATE.check_in() is False


def test_fader_rejects_nan_and_string_mute():
    g, m = fader.apply_control({"gain": float("nan"), "mute": "no"}, 0.7, False)
    assert g == 0.7 and m is False
    g, m = fader.apply_control({"gain": "9e9", "mute": True}, 0.7, False)
    assert g == 1.0 and m is True
    g, m = fader.apply_control("nope", 0.4, False)
    assert g == 0.4 and m is False
