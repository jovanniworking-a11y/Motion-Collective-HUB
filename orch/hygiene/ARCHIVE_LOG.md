# ARCHIVE LOG

Git history is the copy. These paths were removed from the working tree because they were not runnable or they would regenerate a canceled lineup.

| Date | Path | Why |
|---|---|---|
| 2026-10-21 | `orch/context/studio/_chk.py` `_chk2.py` `_chk3.py` `_chk4.py` `_chk5.py` `_chk6.py` | Scratch. Each exec'd a `_t2.py` that is not in the repo. |
| 2026-10-21 | `orch/context/studio/_err.py` `_night2.py` `_all2.py` | Same scratch set. `test_studio.py` stays. |
| 2026-10-21 | `orch/context/studio/_report_b1.json` `_report_b2.json` | One-off sim dumps, not inputs. |
| 2026-10-21 | `orch/context/assets/flyer_v4_glamz/FINAL4_src.py` | Renderer for a canceled act. README left in the folder. |
| 2026-10-21 | `orch/context/assets/flyer_v4_glamz/FINAL4_no_genres_src.py` | Same. |

Not removed: `legacy/ch31-planner/` (already quarantined, not imported by the ops panel or the API), Room Studio `index.html`, budget builders, the Source of Truth body (header lock added; history kept for the T-002 rebuild).

The rows above were written before the files left the tree. They were still present at `1707126` and are removed in the hygiene fix that follows.
