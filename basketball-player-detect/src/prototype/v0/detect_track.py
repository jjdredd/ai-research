"""v0 prototype — detect & track players on one clip.

Implements docs/04-v0-prototype.md: stock YOLO11 (COCO `person` only) +
ByteTrack (or BoT-SORT) -> overlay mp4 + tracks.csv + fps.json.

Kept deliberately modular for reuse by v0.1/v1 (docs/08, docs/09): the frame
loop, row schema and artifacts are stable; later prototypes import the ideas,
never this package's internals.

Usage:
    python detect_track.py --clip ../../clips/foo.webm --out ../../out/foo/bytetrack
    python detect_track.py --clip ... --tracker botsort        # one-line A/B
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO

CSV_COLUMNS = ["frame", "time_s", "track_id", "x1", "y1", "x2", "y2", "conf"]

# docs/04: conf 0.3, COCO class 0 ("person") only.
DEFAULT_CONF = 0.3
COCO_PERSON = [0]

TRACKERS = {
    "bytetrack": "bytetrack.yaml",
    "botsort": "botsort.yaml",
}


@dataclass
class RunConfig:
    clip: Path
    out_dir: Path
    model: str
    tracker: str
    conf: float
    max_frames: int | None
    device: str

    def to_json(self) -> dict:
        d = self.__dict__.copy()
        d["clip"] = str(self.clip)
        d["out_dir"] = str(self.out_dir)
        return d


def parse_args() -> RunConfig:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--clip", type=Path, required=True, help="input video file")
    p.add_argument("--out", dest="out_dir", type=Path, required=True, help="output directory")
    p.add_argument("--model", default="yolo11m.pt", help="ultralytics checkpoint")
    p.add_argument("--tracker", choices=sorted(TRACKERS), default="bytetrack")
    p.add_argument("--conf", type=float, default=DEFAULT_CONF)
    p.add_argument("--max-frames", type=int, default=None,
                   help="stop after N frames (smoke tests)")
    p.add_argument("--device", default=None,
                   help="ultralytics device (cuda:0 / cpu); auto by default")
    a = p.parse_args()
    if not a.clip.is_file():
        p.error(f"clip not found: {a.clip}")
    if a.tracker not in TRACKERS:  # argparse already gates; belt for callers
        p.error(f"unknown tracker {a.tracker}")
    return RunConfig(**vars(a))


def init_writers(out_dir: Path, frame_size: tuple[int, int], fps: float):
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "tracked.mp4"
    csv_path = out_dir / "tracks.csv"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, frame_size)
    csv_file = open(csv_path, "w", newline="")
    writer_rows = csv.writer(csv_file)
    writer_rows.writerow(CSV_COLUMNS)
    return writer, csv_file, writer_rows, video_path, csv_path


def detections_to_rows(
    detections: sv.Detections, frame_i: int, time_s: float
) -> list[list]:
    """One row per tracked box. Untracked detections (no assigned id yet) are
    skipped: tracks.csv is a *tracks* ledger, matching docs/04's schema."""
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


def run(cfg: RunConfig) -> dict:
    model = YOLO(cfg.model)
    annotators = (sv.BoxAnnotator(), sv.LabelAnnotator())

    cap = cv2.VideoCapture(str(cfg.clip))
    if not cap.isOpened():
        raise SystemExit(f"cannot open clip: {cfg.clip}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer, csv_file, row_writer, video_path, csv_path = init_writers(
        cfg.out_dir, (w, h), fps)

    t0 = time.time()
    frame_i = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            result = model.track(
                frame,
                classes=COCO_PERSON,
                tracker=TRACKERS[cfg.tracker],
                persist=True,
                conf=cfg.conf,
                verbose=False,
                device=cfg.device,
            )[0]
            detections = sv.Detections.from_ultralytics(result)
            time_s = frame_i / fps
            for row in detections_to_rows(detections, frame_i, time_s):
                row_writer.writerow(row)

            labels = [
                f"{tid}" for tid in (detections.tracker_id.tolist() if detections.tracker_id is not None else [])
            ]
            annotated = annotators[0].annotate(frame, detections)
            annotated = annotators[1].annotate(annotated, detections, labels=labels)
            writer.write(annotated)

            frame_i += 1
            if cfg.max_frames and frame_i >= cfg.max_frames:
                break
    finally:
        cap.release()
        writer.release()
        csv_file.close()

    wall = time.time() - t0
    fps_stats = {
        "clip": str(cfg.clip),
        "frames_processed": frame_i,
        "video_fps": fps,
        "wall_time_s": round(wall, 2),
        "processing_fps": round(frame_i / wall, 2) if wall > 0 else None,
        "meets_10fps": bool(frame_i / wall >= 10) if wall > 0 else False,
        "under_3x_realtime": bool(wall < 3 * frame_i / fps) if fps else None,
        "model": cfg.model,
        "tracker": cfg.tracker,
        "conf": cfg.conf,
        "python": platform.python_version(),
        "torch_device": str(getattr(model.predictor, "device", "unknown"))
        if hasattr(model, "predictor") else None,
    }
    (cfg.out_dir / "fps.json").write_text(json.dumps(fps_stats, indent=2))
    (cfg.out_dir / "run_config.json").write_text(json.dumps(cfg.to_json(), indent=2, default=str))
    return fps_stats


if __name__ == "__main__":
    stats = run(parse_args())
    print(json.dumps(stats, indent=2))
