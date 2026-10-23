# Zone people-counter (MVP), FORGE lane

Counts **how many people are in each zone** of one camera view, every 5 s, and writes
`{timestamp, zone, headcount, confidence}` rows (the `occupancy_samples` shape) to a CSV, plus
JSON lines on stdout. It is separate from the door line-counter in `../` and shares only its venv
and `yolov8s.pt`.

```
video file / webcam / rtsp ─► sample 2 frames/s ─► YOLOv8s (person only) ─► foot point
   (bottom-centre of box) ─► point-in-polygon ─► per-frame count per zone
   ─► every 5 s: p75 of the per-frame counts + confidence ─► stdout JSONL + CSV
```

**Privacy:** counts only. There is no tracking and no IDs (not even in memory across frames), no
faces and no identity. **No image is written** unless you ask for the one `--draw-zones` preview
PNG (a test checks this). Logs go to stderr.
**Offline:** sets `YOLO_OFFLINE=1`, `YOLO_AUTOINSTALL=False` and ultralytics `sync=False` before
import. Weights load only from a local file. A missing file is an error and is never downloaded
(a test checks this too).

## Files
| file | what |
|---|---|
| `zone_counter.py` | the whole tool (CLI) |
| `zones.example.json` | example polygons (perspective-style) for the 5 zones |
| `zones.kitchen_cam.json` | high kitchen camera: living_room (+ dance_floor inside it) plus the living-room entrance line. Placeholder coordinates |
| `requirements.txt` | deps (same venv as the line counter) |
| `occupancy_bridge.py` | counts.jsonl → `POST /api/data/occupancy` every 5 s, with an on-disk retry queue (stdlib only). See **Bridge** |
| `mock_occupancy_api.py` | stand-in endpoint for testing the bridge (stdlib `http.server`). Not the real API |
| `tests/` | pytest with a fake detector: zone assignment, window stats, null-on-no-frames, CSV schema, EOF/loop, errors, entrance counting, `--zones-file` |

## Install
### Dev box / any CPU machine
```
python -m venv .venv && . .venv/bin/activate      # or reuse live-ops/counter's venv
pip install -r requirements.txt
python ../prefetch_weights.py                      # ONLINE, once: downloads ../yolov8s.pt (22.6 MB) and test-loads it
# optional, more accurate in crowds (see 'yolov8s vs yolov8m'), ONLINE, once, run inside zone_counter/:
python -c "from ultralytics import YOLO; YOLO('yolov8m.pt')"   # -> ./yolov8m.pt, 52.1 MB, sha256 5d4a90cd...e4fe5
python -m pytest tests -q                          # 18 passed, no weights needed
```
### ENGINE (Windows, RTX 3070 Ti, PowerShell). Do this while ONLINE, before 29 Oct
```powershell
cd live-ops\counter
py -3.12 -m venv .venv ; .\.venv\Scripts\Activate.ps1
# CUDA torch FIRST (check pytorch.org for the command matching the installed NVIDIA driver):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt -r zone_counter\requirements.txt
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"   # expect True + 3070 Ti
python prefetch_weights.py            # downloads yolov8s.pt next to the line counter
python prefetch_weights.py --check    # offline load check
cd zone_counter ; python -m pytest tests -q
```
`--device auto` (the default) uses `cuda:0` with FP16 when torch sees the GPU, otherwise CPU.
**GPU speed on the 3070 Ti: UNKNOWN, HANDS-ON 29 OCT.**

## Run
```
# primary: a video file
python zone_counter.py --video party_cam.mp4 --zones zones_livingroom.json --csv occupancy.csv

# webcam as primary
python zone_counter.py --webcam 0 --zones zones.json --csv occupancy.csv

# file, falling back to webcam 0 if the file won't open (otherwise: null rows + exit code 2)
python zone_counter.py --video party_cam.mp4 --webcam 0 --webcam-fallback --csv occupancy.csv

# a camera stream (e.g. docker-wyze-bridge) works too
python zone_counter.py --video rtsp://user:pass@127.0.0.1:8554/living-cam --zones zones.json --csv occupancy.csv

# loop a file forever (bench / demo)
python zone_counter.py --video sample.mp4 --loop
```
At end-of-file without `--loop` it emits the last (partial) window with `status: "partial_window"`
and exits 0. For files, timestamps are `--start-time` (default: now) plus the video time, so
results don't depend on CPU speed. For webcams and streams, timestamps are wall-clock time at the
end of each window. Both are ISO 8601 with offset, e.g. `2026-10-30T22:15:05-05:00`.

### Zones: draw them per camera on 29 Oct
Polygons are **normalised 0–1** (x right, y down) in JSON. A person belongs to a zone when the
**bottom-centre of their box (their feet)** is inside it. If polygons overlap, the **first listed
zone wins**. People whose feet are in no zone aren't counted; the JSON reports
`outside_zones_frames_sum` so a gap in the polygons shows up.
Without `--zones` a **test-only default split** is used: three columns on the top half
(living_room, dance_floor, kitchen_bar) and two on the bottom half (hallway, balcony).
**The real polygons are drawn per camera on 29 Oct.** To do that:
```
python zone_counter.py --video rtsp://...  --zones zones.json --draw-zones preview.png --draw-only
```
`preview.png` shows the first frame with the polygons, names and vertex coordinates overlaid.
Edit the JSON and repeat until the floor areas are right.

**The dance floor is inside the living room.** `living_room` always INCLUDES `dance_floor`, in
every output (CSV, JSONL, `--zones-file`). This is the default `"parents": {"dance_floor":
"living_room"}`; set `"parents": {}` in the JSON to turn it off. A person whose feet are on the
dance floor counts once in `dance_floor` and once in `living_room`. A house total must
therefore add only the top-level zones (living_room + kitchen_bar + hallway + balcony), never
dance_floor. Two ways to draw it, and both give the same counts (tested):
- **recommended:** draw `living_room` around the whole room including the dance floor, and
  `dance_floor` inside it (overlapping).
- or draw `living_room` up to the dance floor's edge (adjacent). The dance floor's area is
  added to it automatically.

**Question for the occupancy_samples table owner:** with this rule, summing all five rows of one
timestamp double-counts the dance floor. Sum only the top-level zones, or treat dance_floor as a
sub-zone. Draw polygons on the **floor**, where
feet are, not around furniture tops. Leave out areas where feet can't be seen (behind the bar
counter, sofas), or accept that seated people's boxes end at the table or sofa edge.

## Output
**CSV** (`--csv PATH`, appended; the header must match or it refuses): exactly
`timestamp,zone,headcount,confidence`, one row per zone per interval. A null headcount is an
**empty cell** with confidence `0.000`. `--csv-extra` adds `status,frames_used` (off by default
so the file matches `occupancy_samples`).
**stdout JSONL** (same rows plus diagnostics):
```json
{"timestamp":"2026-10-21T15:53:56-05:00","zone":"balcony","headcount":30,"confidence":0.63,"status":"ok",
 "frames_used":10,"frames_failed":0,"count_min":24,"count_max":32,"count_median":28.0,
 "mean_score":0.802,"low_score_frac":0.057,"window_s":5.0}
```
`status`:
- `ok`
- `partial` (fewer than half the planned frames were analysed)
- `partial_window` (end of file)
- `no_frames`
- `all_frames_failed`
- `source_down` (stream lost, reconnecting)
- `source_unavailable` (could not open anything)
- `detector_unavailable` (weights missing)

**Every null has a status, and nothing is carried forward:** each window starts empty.

### Headcount = p75 of the per-frame counts (not a tally)
2 frames/s × 5 s = 10 frames per window. Each frame gives a count per zone, and the window
reports their **75th percentile** (`--stat median|p75|p90|max|mean`). Why p75:
- In packed rooms the error is **one-sided**. People hidden behind others go missing in some
  frames, and the audit below found far more misses than false boxes. So per-frame counts are
  biased **low** and dip whenever someone is occluded. The median would follow those dips; p75
  leans toward the more complete frames.
- p75 still ignores the top 25 %, so a one-frame spike (a duplicate box, a poster detected as a
  person) doesn't move the number. `max` and `p90` would.
- A tally or sum would count the same person 10 times. Tracking IDs to de-duplicate is
  deliberately not done (privacy, and it is fragile in crowds).
- The cost: someone who walks through a zone for about 2 of the 5 s can still count. For room
  occupancy that is acceptable. Use `--stat median` if transit areas such as the hallway
  over-count.

On the one audited crowded frame, the window value against the hand count gave a zone MAE of 1.6
with p75 and 2.0 with the median. That is one window, so it is weak evidence.

### Confidence (0–1): what it means
It is a **heuristic trust score, not a calibrated probability**. It is the product of:
- **detection quality**: the mean box score in the zone, reduced by up to half according to the
  share of low-score (< 0.4) boxes. A zone with **no boxes at all** gets a fixed **0.4**
  (`--empty-confidence`; it was 0.6 before 21 Oct evening). "0 people" can't be cross-checked:
  a blocked lens, a dark corner and a really empty room all read as 0. So a steady 0 sits
  exactly on the "check manually" line instead of looking trustworthy.
- **stability**: `1 / (1 + (p90 − p10) / max(1, headcount))`. Counts that jump around score low.
- **coverage**: `sqrt(frames analysed / frames planned)`. A slow CPU, a stalled stream or failed
  frames all score lower.

No frames gives headcount null, confidence 0, and a status. In testing, the confidence ranked the
cases sensibly:

| case | confidence |
|---|---|
| the classroom (exact counts) | ~0.9 |
| the plaza (±1–4 per zone) | 0.26–0.63 |
| the packed subway platform (undercounting by ~35–90 %) | 0.15–0.37 |

**It can't see people the detector never finds,** so a packed zone that is consistently
undercounted can still show a middling score. Treat any confidence under 0.4 as "rough".

## Kitchen camera: living-room occupancy + people coming in
Planned setup: one camera mounted **high in a kitchen corner**, looking across and down into the
living room and its doorway (`zones.kitchen_cam.json`, placeholder coordinates):
- **People inside:** the `living_room` headcount (dance floor included), as above.
- **People coming in and going out:** an entrance **line** on the floor across the doorway:
  ```json
  "entrances": {"living_room": {"line": [[x1, y1], [x2, y2]]}}
  ```
  IN means crossing towards the living_room polygon (automatic). Add `"in_direction":
  "up|down|left|right"` to override.
  - A crossing is counted with **ByteTrack** (in memory only) plus supervision's `LineZone`, on
    the feet point.
  - A person must stay on the new side for 2 analysed frames (`--min-crossing-frames`), which
    stops a box that jitters on the line from counting in, out, in.
  - **Track IDs never leave the process:** they aren't logged, written or output (a test checks
    this). They exist for a few seconds per person.
  - With an entrance configured, the counter analyses **10 frames/s** (instead of 2), because a
    walking person can jump over the line between frames at 2 fps.
- **Output: a separate `--entries-csv`** with `timestamp,zone,ins,outs,confidence`, one row per
  entrance per 5 s window. The JSONL zone row also gets `ins`, `outs`, `entries_confidence`,
  `ins_total` and `outs_total`. Why a separate file: entries are a *flow* (people per 5 s),
  occupancy is a *stock* (people now). Mixing them into `{timestamp, zone, headcount,
  confidence}` would either break that schema or overload `headcount`.
  **Question for the occupancy_samples table owner:** add an `entries_samples` table with these
  columns, or keep entries as a JSONL extra?
- **Entries confidence** = (mean score of the boxes that crossed, or 0.6 if nobody crossed) ×
  min(1, analysed fps / 8) × sqrt(coverage). It falls when the tracker gets too few frames, for
  example yolov8m at 1280 on CPU (about 5 fps) scores about 0.6× lower. No frames gives null
  and 0.
- **Limits:**
  - It counts only the doorway that has a line. People leaving through another exit lower the
    headcount but not `outs`. Use the headcount for "how many are inside" and `ins` for "how many
    came in".
  - Crowds bunching in the doorway will be undercounted (tracking needs people visible as
    separate boxes).
  - **Draw the line where every person must cross it**, on the floor, a step inside the room. A
    line too far into the room is missed by people who turn off early (seen in testing, below).

Run:
```
python zone_counter.py --video rtsp://.../kitchen-cam --zones zones.kitchen_cam.json \
    --csv occupancy.csv --entries-csv entries.csv --zones-file counts.jsonl
```

## Dashboard heartbeat file (`--zones-file counts.jsonl`)
For the HQ dashboard (`../dashboard/hq-local.html`, Chaka's), one JSON line per window,
appended every ≤ 5 s even when nothing changed (`--interval` above 5 is clamped to 5 when this
is set):
```json
{"ts": 1792617594.719, "zones": {"living_room": 33, "dance_floor": 15, "kitchen_bar": 7, "hallway": 4, "balcony": 2},
 "total": 46, "status": "ok", "zone_status": {"living_room": "ok", ...}, "confidence": {"living_room": 0.61, ...}}
```
- **`ts`:** Unix seconds (float) at the end of the window. For live sources that is the wall
  clock. For files it is `--start-time` plus video time, so a file replayed faster than real
  time has `ts` values ahead of the wall clock.
- **Zone ids:** canonical ids (whatever the zone JSON names them). `living_room` includes
  `dance_floor`.
- **`total`** = the top-level zones only (33 + 7 + 4 + 2 = 46).
- **Unknown is null, never a carried-forward number:**
  - source down or every frame failed: every zone is `null`, `total: null`, `status: "unknown"`
  - some zones unknown (e.g. when two cameras are merged later): those zones are `null`,
    `total: null`, `status: "partial"`
  - zones this camera doesn't cover (the kitchen cam config) are simply absent
- **Writing:** each line is a single `os.write` of a complete line on an `O_APPEND` handle
  (binary mode on Windows), then fsync, with the file reopened each time. So rotation, deletion
  and truncation are fine. The file never contains half a line, but a reader racing a write can
  catch the newest line mid-copy, so **readers must skip a last line that has no trailing
  newline**. Write errors are logged to stderr (rate-limited) and counting carries on.

**How the dashboard handles it (tested live, see below):**
- normal lines display correctly
- a zone value of `null` and an omitted key behave identically: "No data" in grey
- top-level extras (`status`, `zone_status`, `confidence`) are ignored safely
- `{"count": n}` objects are also accepted
- **Two things to fix on the dashboard side (questions for Chaka):**
  1. An **all-null** heartbeat (camera down) is counted as a "bad line". The page falls back to
     the previous line and keeps showing the last real numbers as **Live** for about 15 s, then
     "Stale, check the counter", still with the old TOTAL. It should show "No data / camera down"
     straight away (the line carries `status: "unknown"`).
  2. With **one zone null**, TOTAL shows the sum of the known zones (e.g. 42 instead of "?") in
     normal colours, with only a small "No data: Hallway" note. It ignores our `"total": null`.
     It should show the total as "≥ 42" or greyed, since capacity decisions rely on it.

## Bridge: counts.jsonl → `POST /api/data/occupancy` (`occupancy_bridge.py`)
A separate process from `zone_counter.py`. The counter only appends to the file, so a slow or
dead API can never stall counting. Stdlib only (urllib + threading): no new dependencies.

```bash
# show night (offline): local endpoint on this machine
python zone_counter.py --video rtsp://... --zones zones.json --zones-file counts.jsonl
MOTION_DB_LOCAL=1 python occupancy_bridge.py --counts counts.jsonl --preflight   # one POST, must say 201
MOTION_DB_LOCAL=1 python occupancy_bridge.py --counts counts.jsonl            # bash
$env:MOTION_DB_LOCAL="1"; python occupancy_bridge.py --counts counts.jsonl    # PowerShell
# remote (Vercel). NEEDS INTERNET, so it's not for show night
MOTION_API_URL=https://<app>.vercel.app/api/data/occupancy MOTION_API_TOKEN=... python occupancy_bridge.py
# test without the real API
python mock_occupancy_api.py --port 3000 [--fail-rate 0.3] [--delay 5] [--status 422]
```

| env / flag | meaning |
|---|---|
| `MOTION_DB_LOCAL=1` | local mode, which **wins over everything else**. POSTs to `http://localhost:3000/api/data/occupancy` |
| `MOTION_LOCAL_URL` | overrides the local URL (e.g. when port 3000 is busy) |
| `MOTION_API_URL` / `--url` | remote URL when not in local mode (`--url` beats the env). Neither set → exit code 2 with a clear error |
| `MOTION_API_TOKEN` | optional; sent as `Authorization: Bearer …` |
| `--counts` | file to tail (default `counts.jsonl`) |
| `--interval` | seconds between POSTs (default 5) |
| `--stale-after` | newest line older than this → all-null payload (default 15 s) |
| `--timeout` | per-POST HTTP timeout (default 3 s) |
| `--spool` / `--max-spool` | on-disk queue of unsent payloads (default **`bridge_buffer.jsonl` next to the script**; bound 2000 ≈ 2.8 h, oldest dropped beyond that) |
| `--dead-letter` | JSONL of payloads the endpoint rejected (default **`bridge_dead_letter.jsonl` next to the script**) |
| `--preflight` | send ONE POST of the newest counts line, print request, status and response; exit 0 on 2xx, 1 if rejected (dead-lettered), 3 if unreachable or transient. Never buffers |
| `--include-source-ts` | add `source_ts` (the counts line's `ts`). Off by default because the endpoint's field allowlist is unconfirmed |
| `--duration` | stop after N s (tests); 0 = run forever |

**Payload** (one per tick, `ts` = wall clock when the tick happened, in Unix seconds):
```json
{"ts":1792676830.021,"zones":{"living_room":1,"dance_floor":0,"kitchen_bar":0,"hallway":0,"balcony":0},"total":1}
```
- **Zones:** always the 5 canonical keys. A value that is null, missing (a zone this camera
  doesn't cover) or not a non-negative integer is sent as **null**. Unknown zone ids are
  dropped. `status`, `confidence` and the other counts-file extras are not forwarded.
- **total:** the line's `total` when the key is present (null stays null). When it's absent,
  total = `living_room + kitchen_bar + hallway + balcony`. **dance_floor is never added**
  because it is inside living_room. Total is **null unless all four are known**: a partial sum
  would look like a real headcount and understate the house (the same rule as
  `zone_counter.py`). With the kitchen-cam config, total is therefore always null.
- **Stale:** if the newest line is older than `--stale-after`, or no line has been read yet, the
  bridge **still POSTs** (it's the heartbeat) but with **every zone null and total null**, so
  nothing downstream can show old numbers as live. A file replayed faster than real time has
  future `ts` values, which count as fresh.
- **Reading:** incremental tail by (inode, offset). The first open reads only the last 64 KB.
  It handles a file that doesn't exist yet, deletion, truncation (size < offset) and rotation
  (new inode). A last line with no trailing newline waits for the next tick. Malformed lines are
  skipped with a rate-limited warning. The newest valid line wins. (One case it cannot see: a
  file rewritten in place to a size ≥ the old offset. zone_counter only appends, so this
  doesn't happen.)

**Failure handling (sender thread).** The behaviour follows
`PATCH_bridge-retry_2026-10-22.md`, but the waiting happens in the sender thread, never in the
tick loop:
| result | action |
|---|---|
| 2xx | done. The next queued payload goes immediately (backlog drains oldest-first and **stops at the first failure**, so order is preserved) |
| network error, timeout, 5xx, 408, 429 | stays at the head of the buffer (written to `--spool`) and is retried. Backoff: **2, 4, 8, 16, 32, then 32 s forever**, each × random **0.5–1.5** (jitter), never above `BACKOFF_MAX` = 60 s. **Never gives up** on a buffered payload |
| 400, other 4xx, 3xx (wrong URL or redirect) | **not retried and not silently dropped.** Appended to `--dead-letter` as `{"at", "payload", "status", "detail"}` (detail = first 500 chars of the response body), with loud stderr lines `[BRIDGE] 400 rejected, dead-lettered: <detail>` and `[BRIDGE] OPERATOR ACTION: fix payload shape, see <file>`. Repeated once in the exit summary |
| buffer > `--max-spool` | the oldest is dropped, with a warning (`dropped_overflow`) |

**Night-of preflight (before doors):**
```bash
cd live-ops/counter/zone_counter
rm -f bridge_buffer.jsonl bridge_dead_letter.jsonl      # PowerShell: Remove-Item bridge_buffer.jsonl, bridge_dead_letter.jsonl -ErrorAction SilentlyContinue
MOTION_DB_LOCAL=1 python occupancy_bridge.py --counts counts.jsonl --preflight
# expect: STATUS 201 ... PREFLIGHT OK (exit 0). A warning that the newest line is old means zone_counter.py isn't running.
```
`rm` the buffer only when you don't want earlier test payloads replayed into the night's data.

**`post_frame(url, payload, timeout)`** is for code that uses the patch's integration snippet.
It keeps the same return contract but **never sleeps or retries in your thread**: at most one
HTTP attempt, bounded by `timeout`.
- 2xx → `{"ok": True, "status", "body"}`
- 400 or any other 4xx/3xx → dead-lettered → `{"ok": False, "reason": "rejected_400", "status", "detail"}`. `rejected_400` is used for every rejection; check `status` for the exact code.
- Transient failure, or a backlog already queued → handed to a background sender (default buffer file, same backoff) → `{"ok": False, "reason": "buffered", "status", "detail"}`

- **Logging:** one stderr line per POST attempt: `POST 201 2ms q=0 ts=… total=…`.
- **Shutdown:** Ctrl-C or SIGTERM stops the ticks. The sender gets up to `timeout+0.5` s to
  send the last tick, then the queue is saved to the spool, and stats are printed. On the next
  start the spool is loaded and flushed first.
- **Recovery delay:** after a long outage the next retry can be up to 48 s away (32 s × 1.5
  jitter), so the flush can happen up to ~48 s after the API comes back. In the 22 Oct test it
  was 13 s.
- **For the endpoint owner (Cursor):**
  - (1) Order and dedupe by the payload `ts`, not the arrival time. A flush delivers old
    samples in a burst.
  - (2) A timeout can hit after the server has already stored the row, so a retry can deliver
    the same `ts` twice. Upsert on `ts` (or ignore duplicates).

**Tested, retry patch (22 Oct 2026, ~09:05–09:12 CDT, dev box, mock only):**
- **pytest:** 45 bridge tests, 80 in the folder, all passing.
- **`--preflight`:** got 201 and exit 0. Against `--status 400` it exited 1, wrote to the dead
  letter and printed both `[BRIDGE]` lines.
- **400 run:** for 10 s with the mock on `--status 400`, 3 ticks gave 3 dead-letter records
  with payload and detail, 0 retries and no buffer file.
- **Outage:** the mock was down for 28 s. The retry delays were 2.2, 4.0, 4.2, 13.5 and
  16.6 s, all inside the jitter bounds. 8 payloads were buffered and flushed in order 13 s after
  the mock came back. 15 of 15 ticks were received, unique and in order.

**Tested, first version (22 Oct 2026, ~08:44–08:48 CDT, dev box, mock endpoint only):**
- **pytest:** 34 bridge tests, 69 in the folder, all passing.
- **End-to-end:** sample clip → mediamtx RTSP → `zone_counter.py` → counts.jsonl → bridge →
  mock, running in local mode via `MOTION_LOCAL_URL` on port 3100 (another agent's Next.js dev
  server was holding 3000).
  - **Outage:** the mock was killed for 19 s. 6 payloads were queued; when it returned, all 6
    were flushed in order. In total 14 arrived: 13 ticks plus 1 left in the spool from the
    previous run. None were lost or duplicated, and `ts` was strictly increasing.
  - **Stale:** with the counter stopped, the payloads switched to all-null 16 s after the last
    line.
  - **Slow API:** with `--delay 5` against a 3 s timeout, ticks stayed exactly 5 s apart. The
    timeouts were retried and the payloads were kept in the spool on exit.
- **Real endpoint: NOT tested** (Cursor hasn't confirmed it's live). **Vercel mode needs
  internet**, which breaks the offline show-night rule, so use `MOTION_DB_LOCAL=1` on the
  night.
- **HANDS-ON 29 OCT:** run the bridge against the real local endpoint on the ENGINE PC.

## yolov8s vs yolov8m (21 Oct, same frames and hand counts as below)
| | yolov8s 640 | yolov8s 1280 | yolov8m 640 | yolov8m 1280 | v8s tiled | v8m tiled |
|---|---|---|---|---|---|---|
| easy frames (16 people), zone MAE | 0 | 0 | 0 | 0 | 0 | 0 |
| **plaza** (high angle, ~109 people), zone MAE / found | 16.8 / 25 | 3.2 / 97 | 12.6 / 46 | **2.4 / 97** | 1.2 / 105 | **0.8 / 105** |
| subway near zones (4 people), MAE | 0 | 0 | 0 | 0.3 | 0 | 0 |
| subway packed (~36), found | 9 (−75 %) | 16 (−56 %) | 9 (−75 %) | **23 (−36 %)** | 23 (−36 %) | 24 (−33 %) |
| boarding crush (~50–70), found | 5 | 8 | 7 | 15 | 22 | 28 |
| **CPU speed** (8 vCPU, any input size) | 39 fps | 13–14 fps | 18–19 fps | **5 fps** | 0.44 fps (4K) | ~0.2 fps (4K) |

- **Does v8m help?** In the plaza, the frame closest to a high kitchen mount, only a little: zone
  MAE 3.2 → 2.4 at 1280, with the same total found. In the packed subway it finds about 40 %
  more people (16 → 23 of ~36) and doubles the crush count (8 → 15), but is still far under.
- **Cost:** about 2.7× slower. On CPU, v8m at 1280 is about 5 fps. That is enough for occupancy
  (2 fps) but **not enough for entrance tracking**, which wants 10 fps, so entries confidence is
  scaled down.
- The "found" counts are not matched person by person. In the packed scenes some of v8m's
  extra boxes could be false. The plaza audit found very few false boxes.
- **Entrance counting:** v8s and v8m both got 7/7 (below).
- **Confidence vs error:** no better with v8m. Its box scores are a bit higher, so its
  confidence is about 0.05–0.1 higher in the same windows, including the packed subway windows
  where it is still about 60 % under. The ranking (exact > plaza > packed) holds for both.
- **GPU estimate for the RTX 3070 Ti (an ESTIMATE, not measured; HANDS-ON 29 OCT):**
  - Public figures: Ultralytics-style tables list v8m at about 2.3 ms (RTX 3080, TensorRT,
    640). A PyTorch CUDA test on an RTX 3070 ran a 682-frame 1080p video with v8m in 24.9 s
    (about 27 fps end-to-end, limited by video input/output, since v8n took about the same).
  - Raw v8m inference in PyTorch FP16 on a 3070 Ti is likely around 5–10 ms at 640 and 20–40 ms
    at 1280, i.e. **about 25–50 fps at 1280**. That would cover occupancy plus entrance
    tracking (10 fps) for one camera, and probably tiled v8s at roughly 5–10 fps on a 1440p
    Wyze frame.
  - **Recommendation:** v8m at 1280 on ENGINE's GPU if 29 Oct confirms 10 fps or more;
    otherwise v8s at 1280.

## Confidence guidance for the party (70 guests, living room from a high kitchen camera)
**Plain answer: the heuristic is good enough to tell you when *not* to trust a number. It is not
good enough to make the zone count the safety number.** Use it like this:
- **The capacity number is the door count** (line counter or clickers). Zone counts show where
  people are; never use them for capacity.
- **Above 0.6: good** (seen with separated, clearly visible people: exact or ±1). **0.4–0.6:
  rough**, expect ±10–20 %. **Below 0.4: check manually** (glance at the room, or compare with
  the door count).
- **Treat a busy living room as a minimum.** Once roughly 25 or more people are in view and
  packed, the count runs low by 10–40 % even when the confidence looks middling. The detector
  can't see people hidden behind others, and the score only partly notices that.
- **Cross-check with the door every 15 min:** the living_room count should not exceed door
  occupancy, and living_room = 0 while the door says 40 or more is a camera problem.
- **Empty-zone 0.6 → changed to 0.4.** At a 70-guest party an empty living room is unusual, and a
  blocked or knocked camera also reads as a confident 0. At 0.4 it lands on "check manually".
- Entries: trust `ins` when entries confidence is 0.6 or more and the counter is analysing 8 fps
  or more. Compare `ins_total` with the door's IN count at the end of the night.

## Occlusion and packed rooms: knobs and tradeoffs
| knob | default | effect | cost |
|---|---|---|---|
| `--conf` | **0.2** (ultralytics' default is 0.25) | more partly-hidden people kept | more false boxes. These are rare at 0.2 in testing; the duplicates came from tiling |
| `--iou` (NMS) | **0.6** | two people overlapping by less than 60 % stay two boxes. Lower values (0.45) merge people standing close together | higher values keep more duplicate boxes on one person |
| `--imgsz` | **1280** | small and far people become detectable. In the plaza test, 640 found only 25 of ~109 people and 1280 found 97 | about 2× slower than 640 (still 6–10 fps on this CPU) |
| `--tile 640` | off | SAHI-style: a full-frame pass plus overlapping 640 px tiles at native resolution, merged with NMS and intersection-over-smaller to drop half-person duplicates. Best on 4K and far people (plaza: 105/109) | ~15× slower. **0.44 fps on CPU** for a 4K frame, so only ~2 frames per window; GPU UNKNOWN. Pure numpy, no SAHI dependency |
| `--sample-fps` | 2 | more frames per window give a steadier statistic | linear in compute |
| `--weights` | yolov8s | `yolov8m.pt`: about 40 % more people found in packed scenes, a small gain in the plaza (table above) | ~2.7× slower (CPU 1280: 5 fps) |

What none of these fix: **people fully hidden behind others**. In the packed subway frame,
roughly 35–90 % of the dense crowd was missed whatever the settings. A camera mounted **high and
looking down** is the biggest win. Feet-in-polygon also needs the floor area of each zone in view.

## Tested (21 Oct 2026, dev box: 8 vCPU, no GPU, offline weights)
- **pytest: 35 passed (about 2 s), pyflakes clean.** (21 Oct evening; 18 earlier in the day) Covers foot-point assignment, the five default
  zones, overlap order, outside-all-zones, config validation, p75/median window statistics,
  confidence falling with jitter, low scores and missing frames, null on no frames, all frames
  failed, source down, no carry-forward between windows, CSV header and row shape (null = empty
  cell), refusing a mismatched CSV, ISO timestamps with offset, end-to-end file run with EOF, loop
  plus `--max-windows`, detector exceptions giving nulls with no crash, a missing file with no
  fallback, missing weights never downloaded, `--draw-zones`, no images written by default, and
  the tiling helpers.
- **Real runs (YOLOv8s, CPU):** all exit 0.
  - people-detection.mp4
  - classroom.mp4
  - market-square.mp4 (4K)
  - subway.mp4 (4K)
  - a live RTSP stream (mediamtx) whose publisher was killed and restarted: windows went
    `partial` → `source_down` (null) → `ok`.
  - webcam fallback with no camera present: `source_down` nulls, no crash.

### CPU speed (detector only, this box)
| clip | imgsz 640 | imgsz 1280 | tile 640 |
|---|---|---|---|
| 768×432 | 21.8 fps | 10.1 fps | – |
| 1920×1080 | – | 8.3 fps | – |
| 2160×3840 (subway) | 14.2 fps | 7.0 fps | – |
| 2160×3840 (plaza) | – | 5.9 fps | 0.44 fps |

The default needs 2 frames/s, so every untiled setting keeps up in real time on CPU.
**RTX 3070 Ti: UNKNOWN (HANDS-ON 29 OCT).**

### Accuracy: hand count against the detector, per zone, single frames
Method: frames were sampled at fixed times. For the uncrowded clips I counted people per zone by
eye first. For the crowded frames I audited the detector's overlay: I checked every box (real
person, duplicate, false) and searched each tile for missed people. Truth = real boxes + misses,
assigned by foot position.

| frames | people (truth) | 640 | 1280 (default) | tile 640 |
|---|---|---|---|---|
| 3× people-detection + 2× classroom (25 zone-frames) | 16 | MAE 0, exact | MAE 0, exact | MAE 0, exact |
| plaza frame (4K, 5 zones) | ~109 (±3 at the café tables) | 25 found, zone MAE 16.8, −77 % | 97 found, MAE 3.2, −11 % | 105 found, MAE 1.2, −4 % |
| subway frame, near zones (3) | 4 | exact | exact | exact |
| subway frame, packed zones (2) | ~36 (range 29–43) | 9, −75 % | 16, −56 % | 23, −36 % |
| subway boarding crush, packed zones | ~50–70 (can't be counted by hand) | 5 | 8 | 22 |

Honest summary: separated people are counted exactly. A busy room with people visible gets
within about 10 % at the default 1280, and within about 4 % with tiling. **A packed crush
undercounts badly** (35–90 %) because hidden people are invisible to any detector, and the
confidence score drops (0.15–0.37), but only partly. The hand counts in the packed areas are
estimates with wide ranges.

### Entrance counting (21 Oct evening)
- **people-detection.mp4** (7 people walk in from the camera side): line across the floor at
  y = 0.72 → **7 in / 0 out with yolov8s and with yolov8m**, in the right 5 s windows (1, 2, 3, 1).
  Entries confidence 0.85–0.92.
- **The same clip reversed** (people walk out): **0 in / 7 out**.
- **Failure seen and fixed:**
  - With the line at y = 0.6, only 5 of 7 were counted. Two people turned off to the side doors
    before reaching the line (the tracker followed them correctly; they never crossed). Lesson:
    draw the line where every person must cross.
  - Box jitter at a crossing gave in, out, in for one person. Requiring 2 frames on the new side
    (`--min-crossing-frames 2`, now the default) removed it.

### Dashboard live check (21 Oct ~16:20 CDT, read-only use of Chaka's page)
- **Setup:**
  - zone_counter read a live RTSP stream (mediamtx) with `--zones-file`.
  - Chaka's `jsonl_to_countsjs.py` bridge was pointed at an `--out` in /tmp.
  - `hq-local.html?counts=…` ran in headless Chrome (mode B).
- **Results:**
  - Live numbers showed within one poll.
  - When the publisher was killed, the counter wrote `null` heartbeats every 5 s. The page counted
    them as bad lines, kept the last real numbers as "Live" for about 15 s, then went "Stale".
  - A one-zone-null line showed TOTAL 42 plus "No data: Hallway".
  - 0 non-file requests.
