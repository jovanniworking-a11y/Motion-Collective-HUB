# py04 · The beat grid
Every MOTION edit cuts on the music. "Believe" is 142 bpm and its drop lands at 82.204 s.

Fill in `exercise.py`:
1. `beat_length(bpm)`: seconds per beat (60 / bpm).
2. `beat_time(drop, bpm, k)`: the time of beat `k` (0 = the drop, negative = before it).
3. `nearest_beat(drop, bpm, t)`: the beat number closest to time `t` (an int).
4. `snap(drop, bpm, t)`: move a cut at time `t` onto the nearest beat (return the new time).

Always compute from the drop (`drop + k * beat`), never by adding beats one at a time: adding rounds and drifts a frame every few beats. That's a rule in our director's bible.
