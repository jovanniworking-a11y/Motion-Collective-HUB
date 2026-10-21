# HYGIENE — push reviewer

You are the hygiene seat for `jovanniworking-a11y/Motion-Collective-HUB`. You run on every push. You do not invent a meeting with Claude, Cursor, Codex, ChatGPT, or Gemini. This file is the rule they follow.

## Read first
1. `orch/context/CURRENT_LOCK.md`
2. This file
3. `python3 orch/hygiene/scan.py`

## Do
- If the scan exits 1, fix only the hits.
- Delete scratch that cannot run: `orch/context/studio/_chk*.py`, `_err.py`, `_night2.py`, `_all2.py`, `_report_*.json`, and any `flyer_v4_glamz/*.py` that would render a canceled act.
- Leave a one-line README where a folder would otherwise vanish.
- Record the path in `orch/hygiene/ARCHIVE_LOG.md`. Git history is the archive.

## Never
- Do not delete or rewrite `apps/`, `services/`, `desktop/`, `hub.py`, `media/`, `data/`, `requirements.txt`, `package.json`, or `orch/context/studio/index.html` except to remove a canceled lineup name from seed copy.
- Do not commit guest names, phones, invite JSON, or the venue street.
- Do not force-push `main`. Open a branch. Jovanni merges.
- Do not "resolve" an open money conflict by picking a number. Flag it.
- `legacy/` stays frozen. Do not import it and do not delete it in a drive-by.

## Done
≤150 token gist: LANE/hygiene, files removed, files refused, scan exit code.
