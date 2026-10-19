# Post plan: iamariology b2b raymixes montage (DRAFT, needs Jovanni's OK)

- **File:** `MOTION_montage_iamariology_b2b_raymixes_IG.mp4`, 29.2 s, 9:16. It replaces the iamariology-only montage as the main b2b piece.
- **Austin open:** a dusk skyline pan, then the night skyline photo, captioned "AUSTIN, TEXAS". It sets the city only; the venue has no skyline view, so captions must never imply one.
- **The b2b, made visual:** the first drop trades the two DJs on the beat. iamariology gets the neon room, the masked set and the point; raymixes gets the big festival stage and the fan reaching up. Then both names stack on the bar line, and the finale card carries both.
- **Black and white:** a red filter for the daylight stage and the skyline (darker skies, stronger towers), a blue filter for the neon rooms.
- **Post as a Collab with both artists**; their followers see it from both sides.

## Caption options
1. `Austin. iamariology b2b raymixes open Devil's Night. 10.30.2026. RSVP in bio.`
2. `Two DJs, one opening set. iamariology b2b raymixes, AFTERIMAGE 001. Link in bio.`
3. `Back to back, from the first song. iamariology b2b raymixes. 10.30.2026.`

## Still needed
- Both Instagram handles, for the tags and Collab invites.
- Your OK to post. Guests' faces show briefly in the crowd beat of the masked-set run.

## v7 · On 2nite (18 Oct)
- Cut to Silva Bumpa "On 2nite" (90.6 bpm, measured). The edit uses the song from **0:16.5 to 0:47.0**: the breakdown carries the open, the drop at 0:25.75 starts the cuts, and the chorus hit at 0:43.3 is the finale.
- Repo copy is **silent** (`..._v7_on2nite_SILENT_IG.mp4`); the song is licensed to Jovanni and never goes in git.
- **To post on Instagram:** upload the silent file, tap Music, pick "On 2nite", and drag the start to **0:16**. The drop then lands on the first fast cut.

## FINAL · v8 (19 Oct)
- Two equal stars: same name size in the intros, stacks and end card; one featured moment each (iamariology's freeze, raymixes' punch-in).
- Arielogy's note: the from-behind club shot is out; the jacket close-up on the mixer plays 2 beats in its place.
- Song: On 2nite from **0:16** (same as v7). Repo copy is silent.

## FINAL · v9 (19 Oct) — replaces v8
- Arielogy: both behind-the-booth shots are out (the from-behind club shot and the jacket close-up at ~0:08). The neon eye sign tilting down to him plays there now.
- Rendered with the fast engine (`src/montage9_engine.py`): per-shot cached pieces, 4 cores, `--draft` for previews.
  - First draft ~3 min (builds the clip cache once); a re-run with one changed shot re-draws only that shot and its neighbour; no change = 2 s.
  - Full-quality final ~6 min on this 4-core cloud machine.

## FINAL · v10 (19 Oct) — the one to post. Replaces v9.
Finishing pass so nothing reads as generated:
- Real step-printed slow motion on the point-to-camera (no optical-flow in-between frames).
- Phone clip: compression blocks removed (deblock), no waxy denoise, real grain, no blended motion blur.
- Exposure flicker steadied (phone strobes, club strobes kept a little), sparklers rolled off like film (0 blown frames).
- Less ghosting and lens warp, steadier type, softer zoom hits, AFTERIMAGE clears before the logo.
- Bugs fixed: black edge strips (crop now stays inside every clip), the 0:16 black corner.
- Ariology: the club "hands under the beams" shot at ~0:16 is out; the eye triptych runs 3 beats.
- New: the last cut flows the room in through the 3x eyes (eyes as a matte).
- Export: H.264 High, CRF 14, up to 20 Mbps. Audit: `src/qc.py` (blown frames, flashes, exposure dips, black edges).

## FINAL · v11 · "Believe" (19 Oct) — the one to post
- Same edit and finishing as v10, re-timed to "Believe" (142 bpm): AFTERIMAGE on the song's real silence, cuts start on the drop (0:09.3 in the reel), a bar-line music edit into the pre-chorus for the eyes, the eyes matte opens on the hit (0:27.9). 32.3 s.
- **Instagram:** IG's music sticker plays one continuous stretch, so it can't reproduce the music edit. Either post `..._WITH_SONG.mp4` with its own audio (IG may mute it if the label claims it), or post the silent file with "Believe" from IG Music starting at **1:12** — the drop then lands at 0:09.3, and the second half will be off the edit.
