# LIVE OPS RESEARCH BRIEF — Devil's Night · AFTERIMAGE 001
**Date:** 21 Oct 2026 · **Status:** research only — nothing purchased, installed, or signed up for
**Design rule (Jovanni):** Apple-like — complex behind the scenes, UI clean/simple/touch-friendly. Dashboard runs on the MacBook in a dark green room; door view on the iPad; crew operates mid-party, possibly with drinks in hand.

## Gear snapshot (all crew-owned or rented; $0 software budget)
- Visual/counting engine: gaming laptop, RTX 3070 Ti
- HQ dashboard: Jovanni's MacBook (hot spare: Haven's laptop)
- Door: iPad (mirrors dashboard)
- Booth recording: venue PC at the booth
- Cameras: Wyze Cam v4 (overhead; IR night vision; **no official RTSP**), Alex's GoPro (booth POV), Ben Schuler's action cam (2nd wide), iPhone 17 Pro (roving), old camcorder (static wide), sister's Canon 4K (stills)
- Audio: Pioneer DJM-900NXS2 (rented CDJs + mixer, Rock n Roll Rentals); USB audio to laptop
- Projector: rented from Rock n Roll Rentals (model TBD — assume 1080p HDMI)
- Venue: Rio 3BD/2BA apartment, living room 253 sq ft (confirmed), ~70 guests, residential power

---

## Lane 1 — People counting from the overhead camera
**Industry standard:** YOLOv8 person detection + a multi-object tracker (ByteTrack/SORT/DeepSORT) + a virtual trip-line; each tracked ID crossing the line increments in/out. Pretrained model, no training needed, counts/zones only (no faces). On an NVIDIA GPU this runs 30–60+ FPS (DeepWiki). Overhead/high-angle mounting is the recommended camera position because it minimizes occlusion (DeepWiki config guide).
**$0 adaptation for THIS gear:** Python on the 3070 Ti laptop: `ultralytics` YOLOv8s (~20–25 MB weights, confirmed) + ByteTrack/Supervision `LineCounter` (Roboflow's open tutorial covers exactly this pipeline). Virtual line drawn across the entry doorway. Counts pushed over a local WebSocket to the dashboard page. Wyze v4 has no official RTSP, so the stream comes via **docker-wyze-bridge** on the same laptop.
**Fiddliest part + de-risk:** the bridge, not the counting. Verified from Wyze forums (Oct 2026): Wyze changed camera authentication in newer firmware and **all known docker-wyze-bridge forks broke on current v4 firmware**; last user-verified working combo is v4 firmware **4.52.9.4188** with bridge 2.10.3; the original repo looks abandoned. De-risk: (1) the moment the cam arrives, **disable auto-update** and pin firmware; (2) build + test the full bridge→counter chain **the night before the 30th**, not day-of; (3) run the bridge host on **wired ethernet**, not Wi-Fi (forum users report lag/dropouts trace to Wi-Fi, not the bridge); (4) keep the door clicker as the human fallback regardless.
**Backup plan:** hand tally counter in/out at the door (already in the plan); TinyCam Pro in server mode on a spare Android device as an alternate Wyze→RTSP converter (forum-verified alternative); if the bridge dies mid-party, the iPad check-in count becomes the source of truth.

## Lane 2 — Projection mapping + audio-reactive visuals
**Industry standard:** Resolume Arena = the live-VJ standard; MadMapper = accessible manual mapping; **TouchDesigner = the pick for interactive/generative/audio-reactive work**, free for non-commercial use (multiple 2026 comparisons converge on this split).
**$0 adaptation for THIS gear:** TouchDesigner (free non-commercial) on the 3070 Ti laptop. Chain: DJM USB → **Audio Device In CHOP** → **Audio Spectrum CHOP** (kick/bass bands) or Derivative's built-in audio-analysis component (has kick/snare detection) → Analyze/Filter CHOPs → drive visual parameters → **CornerPin TOP** → fullscreen → projector. (Derivative's own docs + community tutorials document this exact operator chain.)
**Fiddliest part + de-risk:** two things. (1) **Free-license resolution cap: 1280×1280** (confirmed in Derivative's licensing docs). On a 1080p rental projector the content gets upscaled — acceptable for a house party, but design visuals chunky/high-contrast, not fine text. (2) Audio latency/glitch on first connect — test the DJM→TD handshake at the pickup, not at doors-open. De-risk: pre-build 3–4 dead-simple reactive scenes (pulse, strobe-on-kick, spectrum bars) that work even if mapping alignment is rough; mapping alignment (corner-pin) happens at the venue during setup.
**Backup plan:** static branded loop (eye art + AFTERIMAGE 001 lockup) on a USB stick straight into the projector — visuals continue with zero software if TD fails; TV-corner fallback if the projector fails outright.

## Lane 3 — DJM-900NXS2 USB audio into a laptop
**Industry standard:** install Pioneer's driver + Settings Utility first, then route. The mixer is a 24-bit/96 kHz USB soundcard (confirmed across B&H, Sweetwater, Pioneer specs). The Settings Utility's **MIXER OUTPUT tab** chooses what the computer receives (channel post-fader, master, REC OUT, etc.). The mixer has **twin USB ports = twin independent sound cards**, designed for two laptops simultaneously (Digital DJ Tips, Sweetwater).
**$0 adaptation for THIS gear:** split the jobs across the two USB ports and two machines — **USB-A → 3070 Ti laptop** (TouchDesigner Audio Device In for reactive visuals), **USB-B → venue booth PC** (set recording in Audacity/OBS, free). This dodges the classic Windows ASIO trap (one app can grab an ASIO device exclusively) by giving each app its own device. Set MIXER OUTPUT to REC OUT or MASTER in the utility.
**Fiddliest part + de-risk:** driver handshake. Verified failure modes: on macOS, Apple's kext security blocks the driver until manually allowed in Security & Privacy (Pioneer forums document the uninstall → reboot → reinstall → allow dance); on Windows, install as admin **before** first connecting the mixer. Apple-Silicon compatibility of the NXS2 driver is **unverified** — do the booth recording on the Windows venue PC to sidestep this entirely. Also **unverified**: whether both USB ports can stream mixer→computer audio *simultaneously* (twin ports are documented for B2B/DVS input, not dual capture) — confirm on test night; fallback is one USB for TD + analog **REC OUT (RCA)** into the recording laptop's line-in.
**Backup plan:** REC OUT analog → any recorder (even a phone with a TRS adapter) keeps the set archive alive if USB fails; a 5-minute pre-doors recording test is the cheapest insurance in this whole brief.

## Lane 4 — Small-room sound for 70 people + the "master fader" concept
**Industry standard:** for rooms ≤200 people, 500–1000 W of PA (two full-range tops + one sub) is the standard bracket (eventtechnology.org). Sub placement wisdom from live-sound forums: corner-load a single sub, then walk the room — small rooms have modal nulls no formula fixes (Gearspace). Keep stage volume sane; the room is 253 sq ft, not a club.
**$0 adaptation for THIS gear:** PA itself comes via Rapid Ric (Haven's liaison — contents TBD). The "master fader" concept = a **tablet-controlled digital mixer** (Behringer X-Air series with the free X AIR app, or Mackie DL with Master Fader) that lets one person mix from anywhere in the venue over Wi-Fi — i.e., **run sound from the green room on the iPad**. The X-Air pattern is exactly this: free app, mixer in AP mode, mix from the floor, the balcony, or HQ (Behringer/B&H docs). Ask Rapid Ric specifically for a mixer with tablet remote; if his rig is analog-only, the iPad becomes a level/talkback display instead.
**Fiddliest part + de-risk:** Wi-Fi. The mixer's control Wi-Fi must be a dedicated AP (not the apartment's congested router) or the faders lag when 70 phones join the network. Also: agree on a **master volume ceiling with the DJ** before doors — in an apartment, the limiter is the neighbor, not the amp.
**Backup plan:** DJM Booth Out → powered speaker direct (bypasses any mixer entirely); a printed "if sound dies" card at the booth: check mixer → check amp power → go direct. Neighbor-noise plan: sub low-passed and pulled back after midnight (estimate: bass carries through floors/walls far more than mids — keep the sub modest; this is the #1 apartment-party killer).

## Lane 5 — Residential power
**Industry standard:** US apartment circuits are typically 15 A = 1800 W max, **1440 W safe for continuous load** (80% NEC rule); 20 A = 2400/1920 W (engineerfix, acelectricohio). The pro move in any venue is the **breaker map**: plug a lamp into each outlet, flip breakers, write down which outlets share a circuit (dvinfo forum method) — 10 minutes at the venue visit.
**$0 adaptation for THIS gear (all estimates):** gaming laptop ~250 W under load + projector ~250 W + two powered tops ~300 W avg each + MacBook ~60 W + DJM/CDJs ~100 W + odds/ends ~100 W ≈ **~1.4 kW worst case if everything lands on one circuit** — right at the 1440 W safe line. So: split the rig across **at least two circuits** (e.g., PA + lighting on one, laptops + projector + booth on another). No space heaters on party circuits (a 1500 W heater alone eats a whole 15 A circuit — acelectricohio).
**Fiddliest part + de-risk:** not knowing which outlets share a breaker — that's what trips breakers mid-set (uking-online: "most breaker trips at gigs come from skipping the math, or not knowing which outlets share a breaker"). Do the breaker map on 23 Oct; tape-label the two "show circuits."
**Backup plan:** a written outlet map taped inside the breaker box door; one crew member (Haven, production floor) knows where the box is; keep phone flashlights handy — if a breaker trips mid-set, music continues on the DJM (it holds power briefly? no — it dies too; the real backup is simply restoring power in <60 s because someone knows exactly which breaker).

## Lane 6 — Backup plans the pros use
**Industry standard:** "If it's mission-critical, it needs a backup. Period." (pynxpro). The recurring pro pattern (stagerightinc, prosoundweb, ftsmusic): **map every piece of gear → decide what happens when each fails → write it down**; keep spares physically present (cables, laptop, power); tiered fallback (full show → reduced show → keep-the-room-alive); rehearse the handoff, don't improvise it. The most common single point of failure at small shows is **one laptop doing everything** (huview).
**$0 adaptation for THIS gear — the failure board:**
| Fails | Fallback (all $0) |
|---|---|
| Wyze bridge / counter | Door clicker + iPad check-in count (human truth) |
| TouchDesigner / visuals | USB stick with branded loop straight to projector |
| Projector | TV-corner fallback; party continues — visuals are garnish |
| DJM USB audio | REC OUT analog → phone/laptop line-in for the archive |
| Booth recording PC | Second laptop records; worst case the set isn't archived — party unaffected |
| PA / mixer | DJM Booth Out direct to a powered speaker |
| Breaker trip | Breaker map + designated person restores in <60 s |
| Internet/Wi-Fi | Everything runs on local LAN — **nothing in this stack needs the internet night-of** (verify this in testing: no cloud logins, no phoning home) |
**Fiddliest part + de-risk:** the handoff nobody rehearsed. Run a 15-minute "kill drill" at setup: unplug the projector, kill the bridge, trip-test the plan — so the first failure isn't at midnight.
**Backup plan for the backup plans:** the door clicker, the USB stick, and the breaker map are all analog — they work when every screen is dark.

## Lane 7 — UI/UX: Apple-like live-ops dashboard (Jovanni's design rule)
**What the best show-control UIs do (verified patterns):**
- **Glanceable by default, detailed on demand** — operators shouldn't study the screen; critical info visible at a glance (crowd-safety UX research, Medium 2026).
- **Never one modality:** critical states use color AND icon AND text (and optional sound) — never color alone.
- **Action-oriented language:** not "High density detected" but "Hold the door — at cap" (same source).
- **Context over raw data:** show the number against its limit (47/70), not a bare number.
- **One-button show control:** Bitfocus Buttons' whole philosophy — each button says what it does in plain words ("play video", "dim house lights"); complex cascades hide behind one foolproof tap.
- **Touch-first control surfaces:** TouchOSC + TouchDesigner over OSC is the industry-standard iPad-remote pattern (Derivative's own BasicTouch auto-generates TouchOSC layouts; club-tested in dark rooms).
- **UI off the render machine:** host the control UI on a different computer than the one doing heavy visuals, so the UI never taxes the show (interactiveimmersive.io).
- **Perform Mode:** TouchDesigner's live mode renders only the output window — the operator never sees the node network (Derivative forum).

**UI spec for OUR build:**
- **Green-room dashboard (MacBook, dark room):** one screen, dark mode, huge type. Top: **OCCUPANCY 47/70** with traffic-light state (green <55, amber 55–64, red ≥65) + "SPACE LEFT: 23". Below: ins tonight / outs tonight / peak. Bottom row: subsystem health tiles — Wyze bridge, counter FPS, DJM audio, projector, recorder — each a green/amber/red dot with one word. Auto-refresh; zero interaction required to read it.
- **Door view (iPad):** even simpler — giant occupancy number, "SPACE LEFT", one big CHECK-IN button. That's the whole screen.
- **Principles:** touch targets ≥44 pt (finger-sized, drink-in-hand-proof); max 1–2 taps for any action; no text entry mid-party; destructive actions (reset counts) behind a confirm; dark background (#0A0810 void, bone text — the MOTION palette); settings lockable so a stray tap can't reconfigure the show.
- **Architecture (matches the verified guidance):** 3070 Ti runs TD in Perform Mode (visuals only); the dashboard is a **separate lightweight local web page** served to the MacBook (Node-RED or static page — both free), fed counts via WebSocket from the Python counter; iPad views the same page. No internet needed night-of. OSC/MIDI stays the control bus so master-fader, DMX lighting, and future upgrades slot in later without rewiring ("room for growth").

---

## Could NOT verify / open items
- Wyze v4 official RTSP status today (forum threads are Mar 2026; may have shipped since) — check at purchase.
- docker-wyze-bridge vs. the exact firmware the new cam ships with — test night-before, non-negotiable.
- Pioneer DJM-900NXS2 driver on Apple Silicon Macs — unverified; booth recording stays on the Windows venue PC.
- Simultaneous mixer→computer audio on BOTH DJM USB ports — documented for B2B/DVS, dual *capture* needs test-night confirmation.
- Projector model/lumens/throw (rental TBD) — affects whether 1280×1280 TD output is visibly soft.
- PA contents via Rapid Ric (mixer model decides whether tablet remote mixing is possible).
- Venue breaker map — do it 23 Oct.
- Whether the apartment's Wi-Fi can be avoided entirely for show control (preferred: dedicated AP or wired).

## Sources (what each verified)
- YOLO counting pipeline: https://blog.roboflow.com/yolov8-tracking-and-counting/ (ByteTrack + Supervision LineCounter tutorial); https://deepwiki.com/xkien2k4/counting-people-using-YOLO/2-getting-started (30–60+ FPS on NVIDIA GPU; overhead camera guidance; crossed_ids logic)
- docker-wyze-bridge status: https://forums.wyze.com/t/wyze-v4-docker-wyze-bridge-iotc-er-timeout-401-client-error/342218?page=2 (auth change broke v4; last working fw 4.52.9.4188); https://forums.wyze.com/t/wyze-cam-v4-rtsp-removed-5-cameras-now-useless-for-their-intended-purpose/341508 (TinyCam Pro server-mode alternative; Wyze RTSP beta status); https://community.home-assistant.io/t/picked-up-docker-wyze-bridge-project-updates/873251 (fork status)
- Projection mapping tools: https://visualalchemist.in/2026/07/09/best-software-for-projection-mapping/ (Resolume=live VJ, MadMapper=accessible, TD=interactive); https://tseentertainment.com/bringing-big-visuals-to-small-stages-projection-mapping/ (tool table)
- TouchDesigner free limits: https://docs.derivative.ca/TouchDesigner_Non-Commercial and https://docs.derivative.ca/Licensing (1280×1280 cap, confirmed; NDI available on free tier, confirmed)
- Audio-reactive chain: https://lab.arts.ac.uk/books/touchdesigner/page/audio-in-touchdesigner-receiving-data-from-arduino/revisions/3690 and https://interactiveimmersive.io/touchdesigner-operators-sops-and-mats/ (Audio Device In → Analyze → Trail CHOP pattern); https://docs.derivative.ca (audio-analysis component with kick/snare detection)
- DJM-900NXS2: https://www.bhphotovideo.com/c/product/1590134-REG/pioneer_dj_djm_900nxs2_w_uxj4_djm900nxs2_white.html (24-bit/96 kHz USB soundcard); https://www.digitaldjtips.com/reviews/pioneer-dj-djm-900nxs2/ (twin USB = twin sound cards, two laptops); https://www.savemygig.com/knowledge/pioneer-dj/djm-900nxs2 (I/O levels, failure guide); https://forums.pioneerdj.com/hc/en-us/community/posts/207480166-DJM900-NXS2-Return-from-Ableton (Settings Utility routing); https://forums.pioneerdj.com/hc/fr/community/posts/360042836312-Djm-Nexus2-Driver-for-Mojave (macOS kext approval dance); https://www.manualowl.com/m/Pioneer/DJM-900NXS2/Manual/475036?page=9 (driver install procedure)
- Small-room PA: https://eventtechnology.org/solutions/choosing-the-right-pa-system-for-large-and-small-venues/ (500–1000 W for ≤200 people); https://gearspace.com/board/live-sound/1345689-subwoofer-placement.html and https://gearspace.com/threads/elevated-subwoofer.469888/ (sub placement, room modes)
- Tablet mixing: https://www.bhphotovideo.com/c/product/1821770-REG/behringer_xr12_12_input_digital_mixer_for.html/overview (X-Air free app, AP mode, mix-from-anywhere)
- Power: https://engineerfix.com/why-are-my-christmas-lights-tripping-the-breaker/ (15 A = 1800 W, 1440 W safe); https://www.acelectricohio.com/lighting-overloads/ (80% NEC rule); https://www.dvinfo.net/forum/photon-management/90425-household-power-how-much-can-i-use-whats-good-alternative.html (breaker-mapping method); https://www.uking-online.com/blogs/stage-lighting-dmx-knowledge-hub/how-to-calculate-total-lighting-load (watts÷volts=amps)
- Backup philosophy: https://www.prosoundweb.com/preparing-for-failure-are-your-systems-and-components-adequately-backed-up/4/ (map every failure, written plan, backup mixer); https://www.stagerightinc.com/recurring-av-issues/ (spares physically present); https://ftsmusic.com/articles/live-playback-rig-backup-plan (tiered fallback); https://huview.com/common-av-mistakes-and-how-to-avoid-them/ (single-laptop = top failure); https://pynxpro.ca/news/confident-events-reliable-corporate-av-avoid-technical-glitches (redundancy rule)
- UI/UX: https://medium.com/@brilu699/designing-a-crowd-safety-system-understanding-the-problem-through-ux-e28a1a7a94fc (glanceable-by-default, multi-modality, action language); https://bitfocus.io/buttons/application/installed-av-spaces (one-button foolproof show control); https://www.livedesignonline.com/news/visual-productions-introduces-kiosctouch2-seamless-touch-interface-smarter-lighting-control (touch control surface pattern); https://interactiveimmersive.io/blog/touchdesigner-lessons/basic-setup-for-touchosc-and-touchdesigner/ (TouchOSC+TD; UI off the render machine); https://derivative.ca/community-post/asset/basictouch-automatic-playable-osc-controller/73386 (OSC remote pattern); https://forum.derivative.ca/t/how-to-open-designer-layout-while-keeping-the-perform-mode/234418 (Perform Mode renders only the output window)
