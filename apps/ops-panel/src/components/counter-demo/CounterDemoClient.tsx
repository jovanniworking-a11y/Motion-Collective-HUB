"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ObjectDetection } from "@tensorflow-models/coco-ssd";
import {
  VENUE_CAP,
  cameraErrorMessage,
  capacity,
  duration,
  people,
  timecode,
} from "@/lib/counter";
import s from "./counter-demo.module.css";

type Status = "idle" | "starting" | "live" | "error";

type Stats = {
  count: number;
  peak: number;
  avg: number;
  frames: number;
  fps: number;
  elapsedMs: number;
};

const EMPTY: Stats = { count: 0, peak: 0, avg: 0, frames: 0, fps: 0, elapsedMs: 0 };

/** Load tfjs + COCO-SSD on demand, in the browser only. Weights come from the public TF CDN. */
async function loadModel(): Promise<ObjectDetection> {
  const tf = await import("@tensorflow/tfjs");
  await tf.ready();
  const cocoSsd = await import("@tensorflow-models/coco-ssd");
  return cocoSsd.load({ base: "lite_mobilenet_v2" });
}

export function CounterDemoClient() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const tcRef = useRef<HTMLSpanElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const modelRef = useRef<ObjectDetection | null>(null);
  const runningRef = useRef(false);
  const detectRaf = useRef<number | null>(null);
  const clockRaf = useRef<number | null>(null);
  const session = useRef({ start: 0, frames: 0, sum: 0, peak: 0, stamps: [] as number[] });

  const [status, setStatus] = useState<Status>("idle");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [stats, setStats] = useState<Stats>(EMPTY);
  const [aspect, setAspect] = useState({ w: 16, h: 9 });

  const halt = useCallback(() => {
    runningRef.current = false;
    if (detectRaf.current !== null) cancelAnimationFrame(detectRaf.current);
    if (clockRaf.current !== null) cancelAnimationFrame(clockRaf.current);
    detectRaf.current = null;
    clockRaf.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    const v = videoRef.current;
    if (v) {
      v.pause();
      v.srcObject = null;
    }
    const c = canvasRef.current;
    c?.getContext("2d")?.clearRect(0, 0, c.width, c.height);
  }, []);

  const stop = useCallback(() => {
    halt();
    setStatus("idle");
    setNote("");
    setStats((prev) => ({ ...prev, count: 0, fps: 0 }));
  }, [halt]);

  // Release camera + model on unmount.
  useEffect(() => {
    return () => {
      halt();
      modelRef.current?.dispose();
      modelRef.current = null;
    };
  }, [halt]);

  const draw = useCallback((boxes: ReturnType<typeof people>) => {
    const c = canvasRef.current;
    const v = videoRef.current;
    if (!c || !v) return;
    const w = v.videoWidth;
    const h = v.videoHeight;
    if (c.width !== w || c.height !== h) {
      c.width = w;
      c.height = h;
    }
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, w, h);
    const unit = Math.max(1, w / 640);
    ctx.lineWidth = 1.5 * unit;
    ctx.font = `500 ${11 * unit}px ui-monospace, Menlo, monospace`;
    ctx.textBaseline = "top";
    for (const p of boxes) {
      const [x, y, bw, bh] = p.bbox;
      // Video is mirrored with CSS; mirror x here so boxes line up but labels stay readable.
      const mx = w - x - bw;
      ctx.strokeStyle = "rgba(237, 230, 218, 0.85)";
      ctx.strokeRect(mx, y, bw, bh);
      const label = `PERSON ${Math.round(p.score * 100)}%`;
      const pad = 4 * unit;
      const tw = ctx.measureText(label).width + pad * 2;
      const th = 11 * unit + pad * 2;
      const ly = y - th >= 0 ? y - th : y;
      ctx.fillStyle = "rgba(10, 8, 16, 0.78)";
      ctx.fillRect(mx, ly, tw, th);
      ctx.fillStyle = "#EDE6DA";
      ctx.fillText(label, mx + pad, ly + pad);
    }
  }, []);

  const detectLoop = useCallback(async () => {
    if (!runningRef.current) return;
    const v = videoRef.current;
    const model = modelRef.current;
    if (v && model && v.readyState >= 2 && v.videoWidth > 0) {
      try {
        const preds = await model.detect(v, 30, 0.3);
        if (!runningRef.current) return;
        const found = people(preds);
        draw(found);
        const now = performance.now();
        const sess = session.current;
        sess.frames += 1;
        sess.sum += found.length;
        sess.peak = Math.max(sess.peak, found.length);
        sess.stamps.push(now);
        while (sess.stamps.length && now - sess.stamps[0] > 1000) sess.stamps.shift();
        setStats({
          count: found.length,
          peak: sess.peak,
          avg: sess.sum / sess.frames,
          frames: sess.frames,
          fps: sess.stamps.length,
          elapsedMs: now - sess.start,
        });
      } catch (err) {
        console.error("[counter-demo] detect failed", err);
      }
    }
    if (runningRef.current) detectRaf.current = requestAnimationFrame(() => void detectLoop());
  }, [draw]);

  const clock = useCallback(() => {
    if (!runningRef.current) return;
    if (tcRef.current) tcRef.current.textContent = timecode(performance.now() - session.current.start);
    clockRaf.current = requestAnimationFrame(clock);
  }, []);

  const start = useCallback(async () => {
    setError("");
    if (typeof window === "undefined") return;
    if (!window.isSecureContext) {
      setStatus("error");
      setError("The camera needs a secure (HTTPS) connection. Open this page on the live https:// site.");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("error");
      setError("This browser can't access a camera. Try the latest Chrome, Safari or Edge.");
      return;
    }
    setStatus("starting");
    setNote("Requesting camera");

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      });
    } catch (err) {
      setStatus("error");
      setError(cameraErrorMessage(err));
      return;
    }
    streamRef.current = stream;
    stream.getVideoTracks()[0]?.addEventListener("ended", () => {
      halt();
      setStatus("error");
      setError("The camera disconnected. Reconnect it and press Start again.");
    });

    const v = videoRef.current;
    if (!v) return;
    v.srcObject = stream;
    try {
      await v.play();
    } catch {
      /* autoplay is allowed for muted inline video after a gesture; ignore */
    }
    if (v.videoWidth && v.videoHeight) setAspect({ w: v.videoWidth, h: v.videoHeight });

    if (!modelRef.current) {
      setNote("Loading detection model");
      try {
        modelRef.current = await loadModel();
      } catch (err) {
        console.error("[counter-demo] model load failed", err);
        halt();
        setStatus("error");
        setError("Couldn't load the detection model. Check the connection and try again.");
        return;
      }
    }
    if (!streamRef.current) return; // stopped while loading

    session.current = { start: performance.now(), frames: 0, sum: 0, peak: 0, stamps: [] };
    setStats(EMPTY);
    runningRef.current = true;
    setStatus("live");
    setNote("");
    clockRaf.current = requestAnimationFrame(clock);
    detectRaf.current = requestAnimationFrame(() => void detectLoop());
  }, [clock, detectLoop, halt]);

  const cap = capacity(stats.count, VENUE_CAP);
  const live = status === "live";
  const busy = status === "starting";

  return (
    <section className={s.page} aria-labelledby="counter-title">
      <header className={s.head}>
        <p className={s.kicker}>MOTION · AFTERIMAGE 001</p>
        <h1 id="counter-title" className={s.title}>
          People counter
        </h1>
      </header>

      <div
        className={s.frame}
        style={{
          aspectRatio: `${aspect.w} / ${aspect.h}`,
          maxWidth: `min(720px, calc(62dvh * ${aspect.w} / ${aspect.h}))`,
        }}
      >
        <video
          ref={videoRef}
          className={s.video}
          playsInline
          muted
          aria-label="Camera preview"
          onLoadedMetadata={(e) => {
            const v = e.currentTarget;
            if (v.videoWidth && v.videoHeight) setAspect({ w: v.videoWidth, h: v.videoHeight });
          }}
        />
        <canvas ref={canvasRef} className={s.canvas} aria-hidden="true" />
        <span className={`${s.corner} ${s.tl}`} aria-hidden="true" />
        <span className={`${s.corner} ${s.tr}`} aria-hidden="true" />
        <span className={`${s.corner} ${s.bl}`} aria-hidden="true" />
        <span className={`${s.corner} ${s.br}`} aria-hidden="true" />

        <div className={`${s.hud} ${s.hudTop}`}>
          <span className={s.rec} data-live={live}>
            <i aria-hidden="true" />
            REC
          </span>
          <span>CAM A</span>
        </div>
        <div className={`${s.hud} ${s.hudBottom}`}>
          <span ref={tcRef} className={s.mono}>
            00:00:00:00
          </span>
          <span>{live ? `${stats.fps} FPS` : "STANDBY"}</span>
        </div>

        {!live && (
          <div className={s.idle}>
            <p>{busy ? note : "Camera off"}</p>
          </div>
        )}
      </div>

      <div className={s.controls}>
        {live || busy ? (
          <button type="button" className={`${s.btn} ${s.stop}`} onClick={stop}>
            Stop
          </button>
        ) : (
          <button type="button" className={s.btn} onClick={() => void start()}>
            Start camera
          </button>
        )}
      </div>

      {error && (
        <p className={s.error} role="alert">
          {error}
        </p>
      )}

      <div className={s.count} aria-live="polite">
        <span className={s.countNum} data-level={cap.level}>
          {stats.count}
        </span>
        <span className={s.label}>People in frame</span>
      </div>

      <div className={s.capacity}>
        <div className={s.capRow}>
          <span className={s.label}>Capacity</span>
          <span className={`${s.label} ${s.mono}`}>
            {stats.count} / {VENUE_CAP} · {cap.pct}%
          </span>
        </div>
        <div
          className={s.bar}
          role="meter"
          aria-label="Capacity"
          aria-valuemin={0}
          aria-valuemax={VENUE_CAP}
          aria-valuenow={stats.count}
        >
          <i data-level={cap.level} style={{ width: `${cap.fill * 100}%` }} />
        </div>
        {cap.level === "over" && <p className={s.over}>Over cap</p>}
      </div>

      <dl className={s.stats}>
        <div>
          <dt>Peak</dt>
          <dd>{stats.peak}</dd>
        </div>
        <div>
          <dt>Average</dt>
          <dd>{stats.avg.toFixed(1)}</dd>
        </div>
        <div>
          <dt>Session</dt>
          <dd>{duration(stats.elapsedMs)}</dd>
        </div>
        <div>
          <dt>Frames</dt>
          <dd>{stats.frames}</dd>
        </div>
        <div>
          <dt>Detect FPS</dt>
          <dd>{stats.fps}</dd>
        </div>
        <div>
          <dt>Cap</dt>
          <dd>{VENUE_CAP}</dd>
        </div>
      </dl>

      <p className={s.foot}>Detection runs on this device. No video leaves the browser.</p>
    </section>
  );
}
