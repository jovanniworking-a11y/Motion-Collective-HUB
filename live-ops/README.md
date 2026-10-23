# MOTION live-ops

Two cameras. They are not interchangeable.

- Door counter: Tapo, Reolink, or `--camera 0` on the booth PC. This process.
- Overview footage: your camera, on its own card. It never connects here. Guests do not touch the laptop.

```bash
python counter/server.py --test-video synthetic
python counter/server.py --rtsp "rtsp://USER:PASS@CAMERA_IP:554/stream"
python counter/server.py --camera 0
python fader/server.py --test-tone
```

Dashboard `http://<pc>:8765`. Door iPad `?view=door`. Fader `:8775`.
CHECK IN only counts after the camera tile is red.
No Wyze account. No paid API. Guest video stays off git.
