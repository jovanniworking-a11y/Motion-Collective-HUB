"""Studio / Muse bridge — layout JSON read/write + postMessage contract."""

from __future__ import annotations

import json
import time
from copy import deepcopy
from typing import Any

from .config import LAYOUT_STORE, STUDIO_DIR

DEFAULT_LAYOUT: dict[str, Any] = {
    "version": 1,
    "source": "motion-control-plane",
    "note": "Draft layout bridge — no venue address, no guest data.",
    "scen": {"baths": 2, "arr": "spread", "drinks": "medium", "smoke": 0.5, "label_baths": "estimate"},
    "items": [
        {"type": "dj", "x": -4.0, "z": 2.0, "rot": 0, "locked": True},
        {"type": "dispenser", "x": 1.5, "z": 0.5, "rot": 0, "locked": True, "serves": "lemonade"},
        {"type": "dispenser", "x": 2.0, "z": 0.5, "rot": 0, "locked": True, "serves": "paloma"},
        {"type": "cooler", "x": 5.0, "z": -3.0, "rot": 0, "locked": True},
        {"type": "trash", "x": 1.0, "z": 1.2, "rot": 0, "locked": False},
        {"type": "recycle", "x": 1.4, "z": 1.2, "rot": 0, "locked": False},
        {"type": "ball", "x": -4.0, "z": 2.5, "rot": 0, "locked": False},
    ],
    "sim_params": {"guests": 50, "guests_label": "estimate", "seed": 1234, "mode": "night"},
}


def studio_paths() -> dict[str, Any]:
    index = STUDIO_DIR / "index.html"
    return {
        "studio_dir": str(STUDIO_DIR),
        "index_html": str(index) if index.exists() else None,
        "index_exists": index.exists(),
        "embed_hint": "/studio/embed",
        "postmessage_contract": {
            "to_studio": [
                {"type": "motion:setLayout", "payload": "layout object"},
                {"type": "motion:setScen", "payload": "scen partial"},
                {"type": "motion:runSim", "payload": "{kind, params}"},
            ],
            "from_studio": [
                {"type": "motion:layoutChanged", "payload": "layout object"},
                {"type": "motion:simProgress", "payload": "{pct, text}"},
                {"type": "motion:ready", "payload": "{version}"},
            ],
        },
    }


def load_layout() -> dict[str, Any]:
    if LAYOUT_STORE.exists():
        try:
            data = json.loads(LAYOUT_STORE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "items" in data:
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return deepcopy(DEFAULT_LAYOUT)


def save_layout(layout: dict[str, Any]) -> dict[str, Any]:
    cleaned = deepcopy(layout)
    for ban in ("address", "venue_address", "guest", "guests_named", "phone", "email"):
        cleaned.pop(ban, None)
    cleaned["updated_at"] = time.time()
    cleaned.setdefault("version", 1)
    cleaned["source"] = "motion-control-plane"
    LAYOUT_STORE.parent.mkdir(parents=True, exist_ok=True)
    LAYOUT_STORE.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
    return cleaned


def patch_layout(partial: dict[str, Any]) -> dict[str, Any]:
    current = load_layout()
    if "scen" in partial and isinstance(partial["scen"], dict):
        current.setdefault("scen", {}).update(partial["scen"])
    if "sim_params" in partial and isinstance(partial["sim_params"], dict):
        current.setdefault("sim_params", {}).update(partial["sim_params"])
    if "items" in partial and isinstance(partial["items"], list):
        current["items"] = partial["items"]
    for k, v in partial.items():
        if k in {"scen", "sim_params", "items"}:
            continue
        if k in {"address", "venue_address", "guest", "guests_named", "phone", "email"}:
            continue
        current[k] = v
    return save_layout(current)
