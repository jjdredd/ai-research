#!/usr/bin/env python3
"""bench/convert_tracks.py — convert pipeline track CSVs to bench tracker-result files.

Input: a tracks CSV with header `frame,time_s,track_id,x1,y1,x2,y2,conf`
(the stable v0/v0.1 artifact schema, see src/prototype/v0/README.md).

Output: one MOT-challenge row file per sequence for bench/score.py:
    <out-dir>/<seq>.txt   rows: frame,id,x,y,w,h,conf,-1,-1

Frame indexing: TrackEval aligns predictions and GT by frame *index within the
sequence*. If the pipeline processed a subsampled stream (e.g. every Nth frame
of a 60 fps source, or a frames.csv manifest), pass --frames pointing at a
single-column file of the GT frame ids in processed order (row r = GT frame id
of processed frame r+1). Tracker CSV frames are then interpreted as 1-based
positions into that list. Without --frames, tracker frames are used verbatim.

Usage:
    .venv/bin/python bench/convert_tracks.py --tracks out/clip/oc_sort/tracks.csv \
        --seq stowe_q1 --out bench/_results/oc_sort [--frames out/clip/frames.csv]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tracks", type=Path, required=True)
    ap.add_argument("--seq", required=True)
    ap.add_argument("--out", type=Path, required=True, help="dir for <seq>.txt")
    ap.add_argument("--frames", type=Path, default=None, help="single-col GT frame ids, processed order")
    args = ap.parse_args()

    df = pd.read_csv(args.tracks)
    need = {"frame", "track_id", "x1", "y1", "x2", "y2"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"{args.tracks}: missing columns {sorted(missing)}")

    if args.frames:
        gt_ids = pd.read_csv(args.frames, header=None)[0].tolist()
        # tracker 'frame' = 1-based processed position -> GT frame id
        df["frame"] = df["frame"].map(lambda f: gt_ids[int(f) - 1])

    out = df.assign(
        x=df.x1.round(2),
        y=df.y1.round(2),
        w=(df.x2 - df.x1).round(2),
        h=(df.y2 - df.y1).round(2),
        conf=df.get("conf", pd.Series(1.0, index=df.index)).round(4),
    )[["frame", "track_id", "x", "y", "w", "h", "conf"]]
    out["cls"] = -1
    out["vis"] = -1
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{args.seq}.txt"
    out.to_csv(path, index=False, header=False)
    print(f"wrote {path} ({len(out)} rows, {df.track_id.nunique()} ids)")


if __name__ == "__main__":
    main()
