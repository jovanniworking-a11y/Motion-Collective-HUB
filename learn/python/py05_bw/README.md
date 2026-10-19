# py05 · Black and white with a colour filter
Our reels are B&W made like a photographer: a "blue filter" mix darkens yellow neon so it pops; a "red filter" darkens skies.
A filter is just a weighted sum of the red, green and blue channels.

Fill in `exercise.py` (NumPy arrays, values 0–255):
1. `to_bw(rgb, weights)`: `rgb` is an (H, W, 3) array; return an (H, W) uint8 array = `R*w0 + G*w1 + B*w2`, clipped to 0–255.
2. `BLUE = (...)` and `RED = (...)`: the weights we use: blue filter (0.08, 0.22, 0.70), red filter (0.70, 0.22, 0.08).
3. `bw_file(src, dst, weights)`: open an image with Pillow, convert, save. (Try it on any photo of yours.)
