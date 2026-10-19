import os, tempfile
def run(m):
    assert m.clip_name("2026-10-30", "iamariology", 1, ".MOV") == "2026-10-30_iamariology_01.mov", "clip_name: check padding and lower-case extension"
    assert m.clip_name("2026-10-30", "raymixes", 12, ".mp4") == "2026-10-30_raymixes_12.mp4", "clip_name: 2-digit numbers"
    d = tempfile.mkdtemp()
    for n in ["IMG_2.MOV", "IMG_1.mov", "notes.txt", "IMG_3.MP4"]: open(os.path.join(d, n), "w").close()
    out = m.rename_folder(d, "2026-10-30", "glamz")
    assert out == ["2026-10-30_glamz_01.mov", "2026-10-30_glamz_02.mov", "2026-10-30_glamz_03.mp4"], f"rename_folder returned {out}"
    assert sorted(os.listdir(d)) == sorted(out + ["notes.txt"]), "files on disk don't match (did you skip notes.txt?)"
