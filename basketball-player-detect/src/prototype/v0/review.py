"""v0 review pass — eyeball metrics from tracks.csv (no notebook).

Implements the review panels of docs/04-v0-prototype.md § Procedure step 5
as a plain script: writes a text summary + PNG panels next to the run.

Panels:
  1. player-count over time histogram (expected ~10 + refs; dips=misses,
     spikes=ghosts)
  2. ID longevity strips (per-track lifespan bars)
  3. ID churn per minute (track starts/ends)

Checks the v0 acceptance criteria that are computable from tracks.csv
automatically (docs/10 § 3 v0 table, ">=6/10 hold ID >5s" proxy row).

Usage:
    python review.py ../../../../out/act_state_team/bytetrack/tracks.csv \
        [--clip-fps 25]   # fps from fps.json if present, else default
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load(fps_override: float | None, tracks_path: Path) -> tuple[pd.DataFrame, float]:
    df = pd.read_csv(tracks_path)
    required = {"frame", "time_s", "track_id", "x1", "y1", "x2", "y2", "conf"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"tracks.csv missing columns: {missing}")
    fps = fps_override
    if fps is None:
        fps_json = tracks_path.parent / "fps.json"
        if fps_json.is_file():
            fps = json.loads(fps_json.read_text())["video_fps"]
    return df, fps or 30.0


def track_stats(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("track_id")
    stats = g.agg(first_f=("frame", "min"), last_f=("frame", "max"),
                  boxes=("frame", "size"), t_first=("time_s", "min"),
                  t_last=("time_s", "max"))
    stats["lifetime_s"] = stats["t_last"] - stats["t_first"]
    return stats


def per_minute_counts(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["minute"] = (d["time_s"] // 60).astype(int)
    per_frame = d.groupby(["minute", "frame"]).size().rename("count")
    return per_frame.groupby("minute").agg(
        mean="mean", p10=lambda s: s.quantile(0.1), p90=lambda s: s.quantile(0.9))


def panels(df: pd.DataFrame, stats: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    counts = df.groupby("frame").size()
    ax.plot(counts["time_s"] if "time_s" in counts else counts.index, counts.values, lw=0.8)
    ax.set(xlabel="time (s)", ylabel="tracked boxes per frame",
           title="panel 1: player-count over time (dips=misses, spikes=ghosts)")
    ax.axhline(10, ls="--", lw=0.6, color="gray")
    fig.savefig(out_dir / "review_panel1_counts.png", dpi=110, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    keep = stats[stats["boxes"] >= 5]  # drop single-frame flicker for readability
    ax.eventplot([keep["t_first"].tolist(), keep["t_last"].tolist()],
                 lineoffsets=[1, 1.4], linewidths=1.5)
    for _, r in keep.iterrows():
        ax.plot([r["t_first"], r["t_last"]], [1.2, 1.2], lw=1.0)
    ax.set(yticks=[], xlabel="time (s)", ylabel="tracks",
           title="panel 2: ID longevity strips")
    fig.savefig(out_dir / "review_panel2_longevity.png", dpi=110, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 4))
    starts = stats.groupby(stats["t_first"] // 1).size()
    ends = stats.groupby(stats["t_last"] // 1).size()
    idx = range(int(max(starts.index.max(), ends.index.max())) + 1)
    ax.bar([i - 0.2 for i in idx], [starts.get(i, 0) for i in idx], width=0.4, label="starts")
    ax.bar([i + 0.2 for i in idx], [ends.get(i, 0) for i in idx], width=0.4, label="ends")
    ax.set(xlabel="minute", ylabel="track id changes", title="panel 3: ID churn per minute")
    ax.legend()
    fig.savefig(out_dir / "review_panel3_churn.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tracks", type=Path, help="path to tracks.csv")
    p.add_argument("--clip-fps", type=float, default=None)
    a = p.parse_args()

    df, fps = load(a.clip_fps, a.tracks)
    stats = track_stats(df)
    out_dir = a.tracks.parent

    n_long = int((stats["lifetime_s"] > 5).sum())
    median_minute = (df["time_s"] // 60).median()
    per_min = per_minute_counts(df)

    lines = [
        f"tracks.csv: {a.tracks}",
        f"frames span: {df['frame'].max() - df['frame'].min() + 1}   duration: {df['time_s'].max():.1f} s",
        f"distinct track ids: {len(stats)}   boxes: {len(df)}",
        f"tracks alive >5 s: {n_long}   (v0 proxy bar: >=6)",
        f"tracks with exactly 1 box (flicker/ghosts): {int((stats['boxes'] == 1).sum())}",
        "",
        "boxes-per-frame by minute (mean / p10 / p90; expect ~10+refs):",
        per_min.round(2).to_string(),
        "",
        "coordinate sanity: " + (
            "OK (all within frame-ish bounds)"
            if (df[["x1", "x2"]].min().min() >= 0 and df["x2"].max() > df["x1"].max())
            else "SUSPECT — inspect!"),
    ]
    summary = "\n".join(lines)
    (out_dir / "review_summary.txt").write_text(summary + "\n")
    print(summary)
    panels(df, stats, out_dir)
    print(f"\nwrote review_panel*.png + review_summary.txt to {out_dir}")


if __name__ == "__main__":
    main()
