#!/usr/bin/env python3
"""Track-level statistics over one or more tracks.csv runs (post-processing).

Complements review.py (which draws panels) with the numeric summary used for
the v0 acceptance analysis in docs/notes/v0-findings.md:

  ids/min            churn: new track ids per minute of clip
  median/p90 life    per-track lifetime (last_seen - first_seen), seconds
  >1s / >5s          tracks alive longer than the threshold
  median-minute      tracks alive >5 s overlapping the clip's median minute
                     (the ">=6/10 hold ID >5s" acceptance proxy)
  boxes/track        mean boxes per track id (ghosts drag this down)
  id-starts/30s      distribution of id starts; broadcast cuts show as
                     repeated short bursts (cut-fragmentation proxy)

Usage (repo root):
    python src/prototype/v0/track_stats.py out/act_state_team/bytetrack ...
    python src/prototype/v0/track_stats.py out/*/*/    # every run dir
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def stats(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    g = df.groupby("track_id").agg(t0=("time_s", "min"), t1=("time_s", "max"),
                                   n=("frame", "size"))
    g["life"] = g["t1"] - g["t0"]
    dur = float(df["time_s"].max())

    # long tracks (>5 s) overlapping the median minute of the clip
    m0 = int(dur / 2) // 60 * 60
    long = g[g["life"] > 5]
    med_ov = int(((long["t1"] >= m0) & (long["t0"] < m0 + 60)).sum())

    # id-start bursts per 30 s of clip (cut fragmentation proxy)
    starts = df.groupby("track_id")["time_s"].min()
    bursts = starts.groupby(starts.index.map(lambda i: int(i // 30))).size()

    return {
        "run": str(csv_path.parent),
        "frames": int(df["frame"].max() + 1),
        "duration_s": round(dur, 1),
        "ids": len(g),
        "ids_per_min": round(len(g) / (dur / 60), 0),
        "median_life_s": round(g["life"].median(), 2),
        "p90_life_s": round(g["life"].quantile(0.9), 2),
        "tracks_gt1s": int((g["life"] > 1).sum()),
        "tracks_gt5s": int((g["life"] > 5).sum()),
        "median_min_long_tracks": med_ov,
        "mean_boxes_per_track": round(g["n"].mean(), 1),
        "ghost_tracks_1box": int((g["n"] == 1).sum()),
        "conf_mean": round(float(df["conf"].mean()), 2),
        "burst_max_30s": int(bursts.max()),
        "burst_median_30s": round(float(bursts.median()), 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dirs", nargs="+", type=Path,
                    help="run output dir(s) containing tracks.csv")
    args = ap.parse_args()

    rows = []
    for d in args.run_dirs:
        csv = d / "tracks.csv" if d.is_dir() else d
        if not csv.exists():
            print(f"skip {d}: no tracks.csv")
            continue
        rows.append(stats(csv))

    if not rows:
        print("no runs found")
        return 1
    table = pd.DataFrame(rows).set_index("run")
    print(table.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
