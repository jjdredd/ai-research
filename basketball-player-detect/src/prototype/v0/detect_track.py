"""v0 prototype — detect & track players on one clip.

Implements docs/04-v0-prototype.md: stock YOLO11 (COCO `person` only) +
ByteTrack (or BoT-SORT) -> overlay mp4 + tracks.csv + fps.json.

Decoding/encoding go through ffmpeg subprocess pipes (OpenCV's bundled ffmpeg
fails on AV1/VP9 webm with "Failed to get pixel format"); inference is
batched + fp16 on GPU. Output dir is cleaned at start so re-runs never mix
with artifacts of an interrupted run. Every run logs to <out>/run.log and
upserts a row into out/RESULTS.md.

Usage (from repo root):
    .venv/bin/python src/prototype/v0/detect_track.py \
        --clip clips/foo.webm --out out/foo/bytetrack
    .venv/bin/python src/prototype/v0/detect_track.py --clip ... --tracker botsort
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
import torch
from ultralytics import YOLO

CSV_COLUMNS = ["frame", "time_s", "track_id", "x1", "y1", "x2", "y2", "conf"]

# docs/04: conf 0.3, COCO class 0 ("person") only.
DEFAULT_CONF = 0.3
COCO_PERSON = [0]

TRACKERS = {
    "bytetrack": "bytetrack.yaml",
    "botsort": "botsort.yaml",
}

# every file this script (or review.py) writes into --out; removed at start
ARTIFACT_NAMES = ["tracked.mp4", "tracks.csv", "fps.json", "run_config.json",
                  "run.log", "review_summary.txt"]

log = logging.getLogger("detect_track")


@dataclass
class RunConfig:
    clip: Path
    out_dir: Path
    model: str
    tracker: str
    conf: float
    max_frames: int | None
    device: str | None
    batch_size: int
    imgsz: int
    threads: int
    decoder: str

    def to_json(self) -> dict:
        return {k: str(v) if isinstance(v, Path) else v
                for k, v in self.__dict__.items()}


def parse_args() -> RunConfig:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--clip", type=Path, required=True, help="input video file")
    p.add_argument("--out", dest="out_dir", type=Path, required=True,
                   help="output dir (cleaned of prior artifacts on each run)")
    p.add_argument("--model", default="yolo11m.pt", help="ultralytics checkpoint")
    p.add_argument("--tracker", choices=sorted(TRACKERS), default="bytetrack")
    p.add_argument("--conf", type=float, default=DEFAULT_CONF)
    p.add_argument("--max-frames", type=int, default=None,
                   help="stop after N frames (smoke tests)")
    p.add_argument("--device", default=None,
                   help="ultralytics device (cuda:0 / cpu); auto by default")
    p.add_argument("--batch-size", type=int, default=16,
                   help="frames per inference batch (GPU throughput lever)")
    p.add_argument("--imgsz", type=int, default=640, help="inference image size")
    p.add_argument("--threads", type=int, default=30,
                   help="CPU threads for torch (default 30)")
    p.add_argument("--decoder", choices=["ffmpeg", "cv2"], default="ffmpeg",
                   help="frame source; ffmpeg handles AV1/VP9, cv2 fails on some builds")
    a = p.parse_args()
    if not a.clip.is_file():
        p.error(f"clip not found: {a.clip}")
    if a.batch_size < 1 or a.imgsz < 32 or a.threads < 1:
        p.error("--batch-size/--imgsz/--threads must be positive")
    return RunConfig(**vars(a))


def clean_out_dir(out_dir: Path) -> list[str]:
    """Delete artifacts of a previous (possibly interrupted) run."""
    out_dir.mkdir(parents=True, exist_ok=True)
    removed = []
    for f in list(out_dir.iterdir()):
        if f.is_file() and (f.name in ARTIFACT_NAMES
                            or f.name.startswith("review_panel")):
            f.unlink()
            removed.append(f.name)
    return removed


def setup_logging(out_dir: Path) -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh = logging.FileHandler(out_dir / "run.log", mode="w")  # fresh per run
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    log.handlers[:] = [fh, sh]


# ---------------------------------------------------------------- decoding

@dataclass
class VideoMeta:
    width: int
    height: int
    fps: float


def probe_meta(clip: Path) -> VideoMeta:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,avg_frame_rate,r_frame_rate",
           "-of", "json", str(clip)]
    info = json.loads(subprocess.check_output(cmd))["streams"][0]
    rate = info.get("avg_frame_rate") or info.get("r_frame_rate") or "30/1"
    num, _, den = rate.partition("/")
    fps = float(num) / float(den or 1) if den else float(num)
    return VideoMeta(int(info["width"]), int(info["height"]), fps or 30.0)


def frames_ffmpeg(clip: Path, meta: VideoMeta):
    """Yield BGR frames via ffmpeg rawvideo pipe (sw-decodes AV1/VP9/Theora)."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(clip),
           "-f", "rawvideo", "-pix_fmt", "bgr24", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=meta.width * meta.height * 3)
    frame_bytes = meta.width * meta.height * 3
    assert proc.stdout is not None
    try:
        while True:
            buf = proc.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            # copy(): np.frombuffer is read-only; annotators draw in place
            yield np.frombuffer(buf, dtype=np.uint8).reshape(meta.height, meta.width, 3).copy()
    finally:
        proc.stdout.close()
        proc.wait()


def frames_cv2(clip: Path, meta: VideoMeta):
    cap = cv2.VideoCapture(str(clip))
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            yield frame
    finally:
        cap.release()


# ---------------------------------------------------------------- encoding

def open_writer(out_dir: Path, meta: VideoMeta):
    """ffmpeg libx264 overlay writer (fast, small, playable); cv2 mp4v fallback."""
    path = out_dir / "tracked.mp4"
    if shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-v", "error", "-y",
               "-f", "rawvideo", "-pix_fmt", "bgr24",
               "-s", f"{meta.width}x{meta.height}", "-r", f"{meta.fps}",
               "-i", "pipe:0", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "23", "-pix_fmt", "yuv420p", str(path)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        return proc.stdin, proc, path
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"),
                             meta.fps, (meta.width, meta.height))
    return writer, writer, path


def write_frame(stream, frame) -> None:
    stream.write(frame if isinstance(stream, cv2.VideoWriter) else frame.tobytes())


# ---------------------------------------------------------------- rows

def detections_to_rows(detections: sv.Detections, frame_i: int, time_s: float) -> list[list]:
    rows: list[list] = []
    ids = detections.tracker_id
    if ids is None:
        return rows
    for (xyxy, tid, conf) in zip(detections.xyxy, ids, detections.confidence):
        x1, y1, x2, y2 = (round(float(v), 1) for v in xyxy)
        if not (0 <= x1 < x2 and 0 <= y1 < y2):
            continue  # sanity guard (acceptance: sane coordinates)
        rows.append([frame_i, round(time_s, 3), int(tid),
                     x1, y1, x2, y2, round(float(conf), 4)])
    return rows


# ---------------------------------------------------------------- results ledger

def update_results_md(out_dir: Path, stats: dict) -> None:
    out_root = next((p for p in out_dir.parents if p.name == "out"), out_dir.parent)
    run_name = out_dir.relative_to(out_root) if out_dir != out_root else out_dir.name
    results_path = out_root / "RESULTS.md"

    row = {
        "run": str(run_name),
        "frames": stats["frames_processed"],
        "proc_fps": stats["processing_fps"],
        "wall_s": stats["wall_time_s"],
        "ok": stats["meets_10fps"],
        "device": stats["torch_device"],
        "when": time.strftime("%Y-%m-%d %H:%M"),
    }
    header = ["run", "frames", "proc_fps", "wall_s", "ok", "device", "when"]
    rows: list[dict] = []
    if results_path.is_file():
        text = results_path.read_text()
        for line in text.splitlines():
            if line.startswith("|") and "---" not in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) == len(header) and cells[0] not in ("run", header[0]):
                    rows.append(dict(zip(header, cells)))
    rows = [r for r in rows if r["run"] != row["run"]]  # upsert
    rows.append(row)

    lines = [f"# v0 run results (auto-updated by detect_track.py; "
             f"reruns replace a run's row)\n",
             "| " + " | ".join(header) + " |",
             "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(r[h]) for h in header) + " |" for r in rows]
    results_path.write_text("\n".join(lines) + "\n")
    log.info("results ledger: %s", results_path)


# ---------------------------------------------------------------- main

def run(cfg: RunConfig) -> dict:
    stale = clean_out_dir(cfg.out_dir)
    setup_logging(cfg.out_dir)
    for name in stale:
        log.info("cleaned stale artifact from previous run: %s", name)
    log.info("config: %s", json.dumps(cfg.to_json()))

    torch.set_num_threads(cfg.threads)
    cv2.setNumThreads(max(1, cfg.threads // 2))
    use_cuda = (cfg.device is None and torch.cuda.is_available()) or \
               (cfg.device is not None and str(cfg.device).startswith("cuda"))
    half = bool(use_cuda)
    log.info("decoder=%s threads=%d batch=%d imgsz=%d half=%s",
             cfg.decoder, cfg.threads, cfg.batch_size, cfg.imgsz, half)

    meta = probe_meta(cfg.clip) if cfg.decoder == "ffmpeg" else None
    frame_src = frames_ffmpeg(cfg.clip, meta) if cfg.decoder == "ffmpeg" else None
    if frame_src is None:
        cap = cv2.VideoCapture(str(cfg.clip))
        if not cap.isOpened():
            raise SystemExit(f"cannot open clip: {cfg.clip}")
        meta = VideoMeta(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                         int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                         cap.get(cv2.CAP_PROP_FPS) or 30.0)
        cap.release()
        frame_src = frames_cv2(cfg.clip, meta)

    model = YOLO(cfg.model)
    box, label = sv.BoxAnnotator(), sv.LabelAnnotator()

    video_in, video_proc, video_path = open_writer(cfg.out_dir, meta)
    csv_path = cfg.out_dir / "tracks.csv"
    csv_file = open(csv_path, "w", newline="")
    row_writer = csv.writer(csv_file)
    row_writer.writerow(CSV_COLUMNS)

    t0 = time.time()
    next_log = t0 + 5.0
    frame_i = 0
    try:
        batch: list = []
        exhausted = False
        while not exhausted:
            batch = []
            for frame in frame_src:
                batch.append(frame)
                if len(batch) >= cfg.batch_size or \
                        (cfg.max_frames and len(batch) >= cfg.max_frames - frame_i):
                    break
            else:
                exhausted = True
            if not batch:
                break

            results = model.track(
                batch,
                classes=COCO_PERSON,
                tracker=TRACKERS[cfg.tracker],
                persist=True,
                conf=cfg.conf,
                imgsz=cfg.imgsz,
                half=half,
                verbose=False,
                device=cfg.device,
            )
            for frame, result in zip(batch, results):
                detections = sv.Detections.from_ultralytics(result)
                time_s = frame_i / meta.fps
                for row in detections_to_rows(detections, frame_i, time_s):
                    row_writer.writerow(row)

                labels = [f"{tid}" for tid in
                          (detections.tracker_id.tolist()
                           if detections.tracker_id is not None else [])]
                annotated = box.annotate(frame, detections)
                annotated = label.annotate(annotated, detections, labels=labels)
                write_frame(video_in, annotated)
                frame_i += 1

                if cfg.max_frames and frame_i >= cfg.max_frames:
                    exhausted = True
                    break

            if time.time() >= next_log:
                log.info("progress: %d frames, %.1f fps (batch=%d)",
                         frame_i, frame_i / (time.time() - t0), cfg.batch_size)
                next_log = time.time() + 5.0
    finally:
        if hasattr(frame_src, "close"):
            frame_src.close()  # stop ffmpeg decoder on early exit (max-frames)
        csv_file.close()
        if isinstance(video_proc, subprocess.Popen):
            video_in.flush()
            video_in.close()
            video_proc.wait()
        else:
            video_proc.release()

    wall = time.time() - t0
    stats = {
        "clip": str(cfg.clip),
        "frames_processed": frame_i,
        "video_fps": meta.fps,
        "wall_time_s": round(wall, 2),
        "processing_fps": round(frame_i / wall, 2) if wall > 0 else None,
        "meets_10fps": bool(frame_i / wall >= 10) if wall > 0 else False,
        "under_3x_realtime": bool(wall < 3 * frame_i / meta.fps) if meta.fps else None,
        "model": cfg.model,
        "tracker": cfg.tracker,
        "conf": cfg.conf,
        "batch_size": cfg.batch_size,
        "imgsz": cfg.imgsz,
        "half": half,
        "python": platform.python_version(),
        "torch_device": "cuda:0" if use_cuda else "cpu",
    }
    if frame_i == 0:
        stats["error"] = "no frames decoded — check clip codec / decoder flag"
        log.error("zero frames decoded from %s", cfg.clip)
    (cfg.out_dir / "fps.json").write_text(json.dumps(stats, indent=2))
    (cfg.out_dir / "run_config.json").write_text(json.dumps(cfg.to_json(), indent=2))
    log.info("done: %s -> %s (%.1fs), artifacts: %s, %s, fps.json, run_config.json",
             cfg.clip, cfg.out_dir, wall, video_path.name, csv_path.name)
    update_results_md(cfg.out_dir, stats)
    return stats


if __name__ == "__main__":
    stats = run(parse_args())
    print(json.dumps(stats, indent=2))
