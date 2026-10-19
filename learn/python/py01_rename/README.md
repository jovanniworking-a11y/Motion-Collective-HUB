# py01 · Rename clips
Phone clips come in as `IMG_4412.MOV`. Before an edit we rename them so they sort and read cleanly:
`2026-10-30_iamariology_01.mov`.

Fill in `exercise.py`:
1. `clip_name(date, artist, n, ext)`: `clip_name("2026-10-30", "iamariology", 1, ".MOV")` → `"2026-10-30_iamariology_01.mov"`. Number padded to 2 digits, extension lower-case.
2. `rename_folder(folder, date, artist)`: rename every video in the folder (`.mov`, `.mp4`, any case), in alphabetical order, starting at 01. Leave other files alone. Return the list of new names.

Hints: `f"{n:02d}"` pads a number. `os.listdir`, `os.path.splitext`, `os.rename`. Sort first: `sorted(...)`.
