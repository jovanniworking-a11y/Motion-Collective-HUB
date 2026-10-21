# BUILD BRIEF — Live-ops software (E001) → Cursor
**From:** Pip (coordination desk) · **Date:** 21 Oct 2026 · **Charter:** acting orchestrator + builder (Claude out until next week)
**Read first:** `~/workspace/motion-system/LIVE_OPS_ARCHITECTURE_E001.md` (the locked architecture) and `LIVE_OPS_RESEARCH_BRIEF.md` (verified sources, red flags).

## What to build (3 pieces, $0, this order)
1. **Counter service (Python, runs on ENGINE = 3070 Ti laptop).** `ultralytics` YOLOv8s + ByteTrack/Supervision `LineCounter` on the Wyze bridge RTSP stream; virtual trip-line at the entry doorway; serves a static dashboard page + WebSocket pushing `{occupancy, ins, outs, peak, health}` on the local LAN. No internet dependency. Include a `--test-video` mode so Pip can bench-test without the camera.
2. **Dashboard page (static HTML, dark mode).** HQ view: giant OCCUPANCY n/70 traffic-light (green <55, amber 55–64, red ≥65) + SPACE LEFT + ins/outs/peak + health tiles (bridge, counter FPS, DJM audio, projector, recorder). Door view (same page, `?view=door`): giant occupancy + SPACE LEFT + one CHECK-IN button. ≥44 pt touch targets, ≤2 taps/action, no text entry, MOTION palette (void #0A0810 / bone #EDE6DA). Auto-refresh via WebSocket.
3. **TouchDesigner template (.toe).** Audio Device In CHOP ← DJM USB-A → Audio Spectrum/Analyze CHOP (kick/bass) → 3–4 simple reactive scenes (pulse, strobe-on-kick, spectrum bars) → CornerPin TOP → fullscreen Perform Mode. Design for 1280×1280 free-license cap (chunky, no fine text). OSC in/out stubs for future growth (master fader, DMX).

## Red flags from research (do not work around — design for them)
- docker-wyze-bridge is BROKEN on current Wyze v4 firmware; last verified combo is fw 4.52.9.4188 + bridge 2.10.3. The counter must tolerate stream loss gracefully (health tile goes red, keeps last count, never crashes).
- DJM twin-USB simultaneous *capture* is unverified — build the audio input so it also accepts a plain line-in/mic fallback without code changes.
- TouchDesigner can't be bench-run headless — keep the .toe structural and documented; live test is crew hands-on 29 Oct.

## Gist back to Pip (typed, ≤150 tokens)
LANE/build, DONE or BLOCKED+what, files changed (paths), bench-test result if any, open questions for the 29 Oct hands-on test. One writer per file. No SoT edits beyond the change-log gist per your charter.
