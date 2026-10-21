# LIVE OPS ARCHITECTURE — Devil's Night · AFTERIMAGE 001
**Date:** 21 Oct 2026 · **Status:** architecture locked for build · **Design rule (Jovanni):** Apple-like — complex behind the scenes, UI clean/simple/touch-friendly
**Extends:** `tasks-inbox/DP-04-live_BUILD_BRIEF.md` · **Research:** `LIVE_OPS_RESEARCH_BRIEF.md` (all claims source-verified there)

## The one-setup principle
One software stack, four machines, each with exactly one job. Nobody touches a node network mid-party. The crew sees two screens: the HQ dashboard (MacBook) and the door view (iPad). Everything else is plumbing.

## Machine map
| Machine | Codename | Job (one only) | Backup |
|---|---|---|---|
| 3070 Ti laptop | ENGINE | docker-wyze-bridge → Python YOLO counter → WebSocket out; TouchDesigner in Perform Mode (visuals) ← DJM USB-A audio; HDMI → projector | Counter can drop to 10 FPS or move to booth PC if TD chokes |
| Jovanni's MacBook | HQ | Dashboard web page (dark mode), zero interaction needed to read it | Haven's laptop (hot spare, same URL) |
| iPad | DOOR | Door view: giant occupancy + SPACE LEFT + one CHECK-IN button | Paper tally sheet |
| Venue booth PC | BOOTH | DJM USB-B → set recording (Audacity or OBS, free) | REC OUT analog → phone line-in |

Dashboard is a static page + WebSocket served by the counter script on ENGINE over local LAN. MacBook/iPad just open the URL. **Nothing in this stack needs the internet night-of** — verify in testing (no cloud logins, no phoning home).

## Subsystem pipelines
**1. People counting (Wyze overhead → HQ number).** Wyze v4 → docker-wyze-bridge (wired ethernet) → Python: YOLOv8s + ByteTrack + virtual trip-line across the entry doorway → counts over WebSocket → dashboard. Counts/zones only, no faces. RED FLAG (verified): Wyze broke bridge auth on current v4 firmware — **disable auto-update the moment the cam arrives, pin firmware**, full chain test the night before the 30th, never day-of. Fallback: door clicker + iPad check-in count (human truth). Alt RTSP path: TinyCam Pro server mode.

**2. Projection mapping (DJM audio → reactive visuals).** DJM USB-A → TouchDesigner Audio Device In CHOP → Audio Spectrum/Analyze CHOP (kick/bass) → reactive network → CornerPin TOP → fullscreen → projector. 3–4 dead-simple scenes pre-built (pulse, strobe-on-kick, spectrum bars) so the show works even if mapping alignment is rough; corner-pin alignment happens at venue setup. Free-license cap is 1280×1280 — design chunky, no fine text. Fallback: USB stick with branded eye-art loop straight into the projector; TV corner if the projector dies.

**3. DJM-900NXS2 USB audio.** Install Pioneer's driver + Settings Utility BEFORE first connecting (admin on Windows; macOS kext approval dance documented). MIXER OUTPUT → REC OUT or MASTER. Twin USB ports = twin sound cards: USB-A → ENGINE (visuals), USB-B → BOOTH (recording) — dodges the Windows ASIO exclusive-access trap. Booth recording stays on the Windows PC (Apple Silicon driver unverified). 5-minute pre-doors recording test is the cheapest insurance in the whole plan. Fallback: REC OUT analog → any recorder.

**4. Sound (PA via Rapid Ric).** 500–1000 W bracket for ≤200 people; corner-load the sub; walk the room. ASK RAPID RIC: a tablet-mixable digital mixer (Behringer X-Air class) so sound can be run from the green room on the iPad over a DEDICATED mixer AP (not the apartment's congested Wi-Fi). If his rig is analog-only, the iPad becomes a level display. Agree a master volume ceiling with the DJ before doors — in an apartment the limiter is the neighbor, not the amp; pull the sub back after midnight (bass is the #1 apartment killer).

**5. Power.** 15 A circuit = 1800 W max / 1440 W safe continuous. Rig worst-case ≈1.4 kW if stacked on one circuit — split across ≥2 circuits (PA on one, laptops + projector + booth on another). **10-minute breaker map at the 23 Oct venue visit** (lamp-in-every-outlet method); tape-label the two show circuits. No space heaters on party circuits. One person (Haven) knows where the breaker box is; outlet map taped inside the box door.

**6. Failure board (written down, not improvised).** Bridge→clicker · TD→USB stick loop · projector→TV corner · USB audio→REC OUT analog · booth PC→second laptop records · PA→DJM Booth Out direct to powered speaker · breaker→mapped restore <60 s · internet→not needed. **15-minute kill drill at setup:** unplug the projector, kill the bridge, rehearse the handoffs — first failure is never at midnight.

## UI spec (Apple-like, from research lane 7)
- **HQ dashboard (MacBook, dark room):** dark mode, MOTION palette (void #0A0810, bone text). Top: **OCCUPANCY 47/70** traffic-light (green <55, amber 55–64, red ≥65) + "SPACE LEFT: 23". Below: ins / outs / peak tonight. Bottom: health tiles — bridge, counter FPS, DJM audio, projector, recorder — green/amber/red dot + one word each. Auto-refresh; zero taps to read.
- **Door view (iPad):** giant occupancy, SPACE LEFT, one big CHECK-IN button. That's the whole screen.
- **Principles:** ≥44 pt touch targets; ≤2 taps per action; no text entry mid-party; destructive actions (reset counts) behind confirm; action language ("Hold the door — at cap"), never bare alerts; color AND icon AND text, never color alone; settings lockable.

## Room for growth (Jovanni's requirement)
OSC/MIDI stays the control bus from day one — master-fader remote mixing, DMX lighting, and NDI camera feeds slot in later without rewiring. The dashboard's health-tile row is built to absorb new tiles (DMX, stream status). Hardware growth path: dedicated show-control mini-PC → replaces ENGINE's double duty; managed switch → replaces ad-hoc LAN.

## Build order + who builds what
1. **Counter + dashboard page** (Cursor; Pip bench-tests with sample footage) — no hardware needed.
2. **TD template** (.toe: audio-reactive network + CornerPin + Perform Mode layout; Cursor from the operator chain in the research brief) — bench-check structure only; live test needs the DJM.
3. **Hands-on gates (crew):** 23 Oct venue visit = breaker map + projector throw check; 29 Oct = full chain test night (bridge→counter→dashboard, DJM USB A/B, TD→projector, kill drill). Nothing debuts on the 30th.
4. **Rapid Ric ask** (Haven): PA contents + tablet-mixable mixer yes/no — decides the iPad's sound role.

## Test plan: bench (Pip, now) vs hands-on (crew)
- **Bench:** counter pipeline on sample video (FPS + line-cross accuracy), dashboard page render + WebSocket flow, TD template structural review, failure-board completeness.
- **Hands-on:** Wyze bridge handshake + firmware pin, DJM USB A/B simultaneous capture, projector mapping + 1280 cap check, breaker map, kill drill, no-internet rehearsal.
