import numpy as np, os, tempfile
from PIL import Image
def run(m):
    assert tuple(m.BLUE) == (0.08, 0.22, 0.70) and tuple(m.RED) == (0.70, 0.22, 0.08), "BLUE / RED weights"
    yellow = np.zeros((2, 2, 3), np.uint8); yellow[..., 0] = 255; yellow[..., 1] = 220
    a = m.to_bw(yellow, m.BLUE); b = m.to_bw(yellow, m.RED)
    assert a.shape == (2, 2) and a.dtype == np.uint8, "to_bw must return (H, W) uint8"
    assert a[0, 0] < b[0, 0], "yellow light should come out darker through the blue filter than the red one"
    assert int(b[0, 0]) == int(np.clip(255 * .7 + 220 * .22, 0, 255)), "to_bw maths"
    d = tempfile.mkdtemp(); src = os.path.join(d, "in.png"); dst = os.path.join(d, "out.png")
    Image.fromarray(yellow).save(src); m.bw_file(src, dst, m.RED)
    assert Image.open(dst).mode in ("L", "RGB"), "bw_file should save an image"
