#!/usr/bin/env python3
"""bench/ingest_labels.py — merge exported track_attrs_all.csv into per-seq label files.

Input: the CSV exported from labels/label.html (place it at
bench/mini-2026-10/labels/track_attrs_all.csv, or pass --csv).

For each sequence, writes labels/<seq>/track_attrs.csv (merging template stats
gt_len_frames/median_h) and prints a coverage summary vs the 30-seq bench.

Usage:
    .venv/bin/python bench/ingest_labels.py [--csv PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
BENCH = REPO / "bench" / "mini-2026-10"
LABELS = BENCH / "labels"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", type=Path, default=LABELS / "track_attrs_all.csv")
    args = ap.parse_args()
    if not args.csv.exists():
        raise SystemExit(f"not found: {args.csv} (export it from label.html first)")

    df = pd.read_csv(args.csv, dtype={"track_id": int})
    need = {"seq", "track_id", "team", "number"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"unexpected CSV header {sorted(missing)} — wrong file?")

    bench_seqs = {p.name for p in BENCH.iterdir() if (p / "gt" / "gt.txt").exists()}
    unknown = set(df.seq) - bench_seqs
    if unknown:
        raise SystemExit(f"CSV references unknown sequences: {sorted(unknown)[:5]}")

    total, filled = 0, {}
    for seq, g in df.groupby("seq"):
        gt = pd.read_csv(BENCH / seq / "gt" / "gt.txt", header=None,
                         names=["frame", "id", "x", "y", "w", "h", "conf", "cls", "vis"])
        gt = gt[gt.cls == 1]
        stats = (gt.groupby("id").agg(gt_len_frames=("id", "size"), median_h=("h", "median"))
                   .reset_index().rename(columns={"id": "track_id"}))
        g2 = g[["track_id", "team", "number", "non_player", "note"]].merge(stats, on="track_id", how="left")
        # sanity: labeled ids must exist in gt
        ghost = set(g2.track_id) - set(stats.track_id)
        if ghost:
            print(f"  !! {seq}: labels for ids not in GT: {sorted(ghost)}", file=sys.stderr)
        out = LABELS / seq / "track_attrs.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        g2.to_csv(out, index=False)
        filled[seq] = len(g2)
        total += int((g2.team.notna() & (g2.team != "")).sum())

    print(f"ingested labels for {len(filled)} sequences, {total} tracks")
    for seq, n in sorted(filled.items()):
        print(f"  {seq}: {n}")
    remaining = bench_seqs - set(filled)
    if remaining:
        print(f"unlabeled sequences: {len(remaining)}")


if __name__ == "__main__":
    main()
