# ml02 · Sharp or blurry? (picking the freeze frame)
For the freeze in the b2b reel we picked the sharpest frame by measuring it, not by eye. A sharp image has strong
pixel-to-pixel changes; a blurry one doesn't.

Fill in `exercise.py`:
1. `sharpness(img)`: the variance of the image's Laplacian (second difference). Use
   `lap = img[1:-1, :-2] + img[1:-1, 2:] + img[:-2, 1:-1] + img[2:, 1:-1] - 4 * img[1:-1, 1:-1]` on a float array, return `lap.var()`.
2. `learn_threshold(sharp_scores, blurry_scores)`: the number halfway between the two groups' average scores.
3. `classify(img, threshold)`: `"sharp"` or `"blurry"`.

The check makes 40 synthetic frames (half blurred) and wants at least 90% right.
