#!/usr/bin/env python3
"""bench/label_attrs.py — build per-track review crops + attribute template CSVs.

SportsMOT GT has boxes + ids but NO team / jersey-number labels. For M3/M4
exit checks (team assignment, OCR, re-ID) we add constant per-track attributes
in bench/mini-2026-10/labels/<seq>/track_attrs.csv:

    track_id,team,number,note
    1,A,23,
    2,B,,referee? blank number = not readable

This script prepares the work:
 1. For every track in gt.txt, pick its 3 largest-area frames.
 2. Crop each with margin, save to labels/review/<seq>/<tid>_<frame>.jpg.
 3. Emit labels/<seq>/track_attrs.csv template (team/number blank; fill in).

Run crops per sequence, read them (assistant) and fill team/number.
Re-running with --skip-existing keeps manual edits (CSV never overwritten
if it exists unless --force-template).

Usage:
    .venv/bin/python bench/label_attrs.py --seqs v_2j7kLB-vEEk_c001 [--all]
"""
from __future__ import annotations

import argparse
import configparser
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
BENCH = REPO / "bench" / "mini-2026-10"


def load_seq(seq_dir: Path):
    ini = configparser.ConfigParser()
    ini.read(seq_dir / "gt" / "seqinfo.ini")
    return dict(ini["Sequence"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--seqs", nargs="*", help="sequence names")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--crops-per-track", type=int, default=3)
    ap.add_argument("--force-template", action="store_true")
    args = ap.parse_args()

    all_seqs = sorted(p.name for p in BENCH.iterdir() if (p / "gt" / "gt.txt").exists())
    seqs = all_seqs if args.all else args.seqs

    for s in seqs:
        seq_dir = BENCH / s
        info = load_seq(seq_dir)
        gt = pd.read_csv(seq_dir / "gt" / "gt.txt", header=None,
                         names=["frame", "id", "x", "y", "w", "h", "conf", "cls", "vis"])
        gt = gt[gt.cls == 1]
        review_dir = BENCH / "labels" / "review" / s
        review_dir.mkdir(parents=True, exist_ok=True)
        rows_out = []
        for tid, tr in gt.groupby("id"):
            attrs_csv = BENCH / "labels" / s / "track_attrs.csv"
            top = tr.assign(area=tr.w * tr.h).nlargest(args.crops_per_track, "area")
            n_crops = 0
            for _, r in top.iterrows():
                img_path = seq_dir / "img1" / f"{int(r.frame):06d}{info.get('imext', '.jpg')}"
                if not img_path.exists():
                    continue
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                H, W = img.shape[:2]
                m = 0.15
                x1, y1 = max(0, int(r.x - r.w * m)), max(0, int(r.y - r.h * m))
                x2, y2 = min(W, int(r.x + r.w * (1 + m))), min(H, int(r.y + r.h * (1 + m)))
                crop = img[y1:y2, x1:x2]
                out = review_dir / f"{tid:04d}_f{int(r.frame):06d}.jpg"
                if not out.exists():
                    cv2.imwrite(str(out), crop)
                n_crops += 1
            rows_out.append({"track_id": tid, "team": "", "number": "", "note": "",
                             "gt_len_frames": len(tr), "median_h": int(tr.h.median())})
        attrs_csv.parent.mkdir(parents=True, exist_ok=True)
        if args.force_template or not attrs_csv.exists():
            pd.DataFrame(rows_out).to_csv(attrs_csv, index=False)
            print(f"{s}: template ({len(rows_out)} tracks, {n_crops} crops -> labels/review/{s}/)")
        else:
            print(f"{s}: existing track_attrs.csv kept (use --force-template to regenerate)")


if __name__ == "__main__":
    main()
