# MOTION Ops — desktop shell

Discord-like **windowed PC app** for MOTION operations. Electron host with a system tray, single-instance lock, and close-to-tray behavior. Loads the Next ops panel when available; otherwise the Night-Of crew page in `ops/`.

**Draft / local only — do not publish.**

## One-command launch

From repo root (after a one-time install in `desktop/`):

```bash
cd desktop && npm install && npm run desktop
```

Or:

```bash
python desktop/launch.py
```

Root convenience (if root `package.json` is present):

```bash
npm run desktop
```

### Manual window open
Headless CI only verifies the main process boots (`npm run smoke`). On a real desktop, `npm run desktop` should open a native **MOTION Ops** window and a tray icon.

## What it loads

| Priority | Target | How |
|---|---|---|
| 1 | Explicit URL | `MOTION_OPS_URL=https://…` |
| 2 | Next ops panel | `apps/ops-panel` + `http://localhost:3000` when reachable |
| 3 | Night-Of ops | static serve of repo `ops/` |
| 4 | Placeholder | `desktop/shell/fallback.html` |

Hooks for the sibling Next app (do not edit that app from here):

```bash
# terminal A
cd apps/ops-panel && npm run dev

# terminal B
MOTION_OPS_FALLBACK=panel npm run desktop
# or
MOTION_OPS_URL=http://localhost:3000 npm run desktop
```

Force Night-Of even if the panel folder exists:

```bash
MOTION_OPS_FALLBACK=night-of npm run desktop
```

## Discord-like shell traits
- Native app window titled **MOTION Ops** (product name in `package.json`)
- Single-instance lock (second launch focuses the first window)
- System tray icon — click to show/hide; Quit from tray menu
- Close button hides to tray (Quit exits)
- Dark MOTION night chrome (`#060B13`); external links open in the OS browser

## Smoke test (CI / headless)

```bash
cd desktop && npm install && npm run smoke
```

Expect log lines `target=…` and `smoke OK`, exit code 0. Does not require a display.

## Optional Python / pywebview

Default `launch.py` shells out to Electron. Pure-Python window (no Electron):

```bash
pip install pywebview
MOTION_OPS_ENGINE=webview python desktop/launch.py
```

## Layout
```
desktop/
  package.json      Electron app (own deps — no fight with apps/ops-panel)
  main.js           BrowserWindow + tray + target resolver
  preload.js        small contextBridge
  launch.py         Python entry (Electron or webview)
  shell/fallback.html
  README.md
```
