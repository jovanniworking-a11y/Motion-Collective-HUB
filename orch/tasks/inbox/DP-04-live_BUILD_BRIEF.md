# DP-04 LIVE BUILD BRIEF — unified night-of ops stack (door count + music-reactive visuals, one control point)

Owner: Jovanni. Builder: Cursor (Claude Code seat dark until next week). Event: Fri 30 Oct 2026 (9 days).
Staff consults behind this brief: Groq gpt-oss-120b (unified stack design) + Gemini 3.5-flash-lite (audio→visuals chain). Existing spec: "MOTION Collective Projection Mapping MVP Spec" (Drive, 16 Oct) — read it first; this brief is the build order, not a replacement.

## Goal
One software setup, run from the crew's existing hardware, linking:
1. LIVE people-counting from the Wyze Cam v4 (overhead) → green-room dashboard (current occupancy vs 70 cap).
2. Music-reactive projection-mapped visuals for the DJ sets, driven by the DJM-900NXS2 audio.
3. All $0 software. No faces tracked anywhere — bodies/counts/zones only (data-platform privacy rule).

## Hardware assignment (do not reshuffle without Jovanni)
- Gaming laptop (RTX 3070 Ti): visual engine + counting. Runs docker-wyze-bridge, the Python counter, TouchDesigner, OBS. HDMI out → projector (RENT from Rock n Roll Rentals with the CDJ pickup run 27–29 Oct — Jovanni, 21 Oct; price open).
- Jovanni's MacBook (HQ/green room): dashboard (Node-RED or static page), mirrors to iPad at door via Sidecar.
- Venue PC at booth: DJ software + DJM-900NXS2 USB; audio forwarded to the gaming laptop (USB splitter preferred over NDI — simpler, lower latency).
- Haven's laptop/PC: hot backup for the visual engine.

## Data flow
Wyze v4 → docker-wyze-bridge → Python (YOLO person detect, virtual line at entry, in/out/occupancy) → WebSocket → dashboard page (big number, vs cap 70, peak).
DJM-900NXS2 USB → gaming laptop → TouchDesigner Audio Device In CHOP → Audio Spectrum/Analyze CHOP (kick/bass triggers) → reactive visual network → CornerPin TOP (wall align) → fullscreen → projector.
Fallbacks (build these FIRST, not last): door hand-counter stays night-of truth; static HTML dashboard if Node-RED dies; blackout hotkey if visuals fail.

## Build order (9→0)
0. Projector: borrow 1080p HDMI (campus AV) or rent mini (~$30/day). No projector = no mapping; visuals can still run on the TV corner.
1. docker-wyze-bridge on gaming laptop, verify stream.
2. Python counter: YOLO detect → line cross → JSON over WebSocket. Acceptance: `curl` returns `{"count": N}` matching a hand count ±2 on a test video.
3. Dashboard page: big occupancy number, green <60 / red ≥65, peak. Acceptance: loads on the MacBook + iPad.
4. DJM USB → TouchDesigner audio in, verify meters move with music. (Fiddliest part per Gemini: USB audio driver handshake/sample rate.)
5. Reactive visual: kick → pulse, spectrum → motion. Keep it dark/monochrome + red accent (brand rule: red ≤10%, never tints).
6. CornerPin align to the wall; test pattern first.
7. Full rehearsal: all four running, kill each one, verify fallback.

## Privacy / house rules
- Counts and zones only. No face recognition, no identity, no stored face crops. Pass numbers never names in any log.
- Event is announced as recorded; phones fine.
- Nothing published, no spend, without Jovanni's OK. Draft only.

## Open items for Jovanni (only he can answer)
- Projector: borrow, rent, or skip (TV corner fallback)?
- New DJ addition (b2b with Rohan Rali): name, fee, set time — lineup lock.
- Who operates visuals night-of (watchdog)?
