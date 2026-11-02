#!/usr/bin/env python3
"""bench/score.py — score tracker outputs against bench/mini-2026-10 GT.

Uses vendored TrackEval (third_party/trackeval, MIT, pinned — see
third_party/TRACKEVAL.lock) unmodified via its library API
(`trackeval.eval.Evaluator`) with the MOT-Challenge 2D box dataset adapter,
which is exactly the SportsMOT layout the bench uses:

    bench/mini-2026-10/<seq>/img1/frame000001.jpg   (optional here; not read)
    bench/mini-2026-10/<seq>/gt/gt.txt              frame,id,x,y,w,h,conf,cls,vis
    bench/mini-2026-10/<seq>/gt/seqinfo.ini

Tracker results are converted into the same tree shape TrackEval wants:

    bench/_eval/trackers/SportsMOT-bench/<tracker>/data/<seq>.txt

GT is materialised under bench/_eval/gt/<seq>/gt/ (symlinks not used:
TrackEval resolves relative paths).

Attributes (team/number) scoring lives in score_attributes.py — this script
only runs DetA / AssA / HOTA / MOTA / IDF1 / IDsw via TrackEval.

Usage:
    .venv/bin/python bench/score.py --trackers out-stems... --bench bench/mini-2026-10
A tracker "stem" is a directory containing per-sequence results files named
<seq>.txt (MOT-challenge row format). See convert_v0_tracks.py for making one
from v0 tracks.csv.
"""
from __future__ import annotations

import argparse
import configparser
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "third_party" / "trackeval"))

import pandas as pd  # noqa: E402
import trackeval  # noqa: E402

BENCH_DEFAULT = REPO / "bench" / "mini-2026-10"


def seq_names(bench: Path) -> list[str]:
    return sorted(p.name for p in bench.iterdir() if (p / "gt" / "gt.txt").exists())


def materialize_gt(bench: Path, eval_root: Path, seqs: list[str]) -> None:
    gt_root = eval_root / "gt" / "SportsMOT-bench"  # TrackEval joins BENCHMARK-SPLIT with a hyphen
    gt_root.mkdir(parents=True, exist_ok=True)
    for s in seqs:
        dst = gt_root / s / "gt"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bench / s / "gt" / "gt.txt", dst / "gt.txt")
        ini_src = bench / s / "gt" / "seqinfo.ini"
        if ini_src.exists():
            shutil.copyfile(ini_src, gt_root / s / "seqinfo.ini")
        else:
            raise SystemExit(f"missing {ini_src} (TrackEval requires seqinfo.ini)")
    seqmaps = eval_root / "gt" / "seqmaps"
    seqmaps.mkdir(parents=True, exist_ok=True)
    (seqmaps / "SportsMOT-bench.txt").write_text("\n".join(seqs) + "\n")


def eval_tracker(tracker_dir: Path, eval_root: Path, seqs: list[str], metrics: list[str]) -> dict:
    tr_name = tracker_dir.name
    tr_root = eval_root / "trackers" / "SportsMOT-bench" / tr_name
    for s in seqs:
        src = tracker_dir / f"{s}.txt"
        if not src.exists():
            raise SystemExit(f"tracker {tr_name}: missing {src}")
        dst = tr_root / "data"  # TrackEval layout: TRACKERS/bench-split/<tracker>/data/<seq>.txt
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst / f"{s}.txt")

    eval_cfg = {
        "USE_PARALLEL": True,
        "NUM_PARALLEL_CORES": min(8, len(seqs)),
        "BREAK_ON_ERROR": True,
        "PRINT_RESULTS": False,
        "PRINT_ONLY_COMBINED": True,
        "TIME_PROGRESS": False,
        "OUTPUT_SUMMARY": True,
        "OUTPUT_DETAILED": True,
        "PLOT_CURVES": False,
        "DISPLAY_LESS_PROGRESS": True,
    }
    ds_cfg = {
        "GT_FOLDER": str(eval_root / "gt"),
        "TRACKERS_FOLDER": str(eval_root / "trackers"),
        "OUTPUT_FOLDER": str(eval_root / "out"),
        "TRACKERS_TO_EVAL": [tr_name],
        "BENCHMARK": "SportsMOT",
        "SPLIT_TO_EVAL": "bench",
        "CLASSES_TO_EVAL": ["pedestrian"],  # MOT-adapter maps pedestrian -> class id 1 (= player in SportsMOT gt)
        "TRACKER_SUB_FOLDER": "data",
        "OUTPUT_SUB_FOLDER": "",
        "DO_PREPROC": True,
        "SEQ_INFO": {s: None for s in seqs},  # lengths from each seqinfo.ini
    }
    metric_cls = {"HOTA": trackeval.metrics.HOTA, "CLEAR": trackeval.metrics.CLEAR, "Identity": trackeval.metrics.Identity}
    metrics_list = [metric_cls[m]({}) for m in metrics]
    summary, _detailed = trackeval.Evaluator(eval_cfg).evaluate(
        [trackeval.datasets.MotChallenge2DBox(ds_cfg)], metrics_list
    )
    # summary -> {dataset: {tracker: {seq|COMBINED_SEQ: {class: {metric: {key: value}}}}}}
    ds_key = next(iter(summary))
    combined = summary[ds_key][tr_name]["COMBINED_SEQ"]["pedestrian"]

    def scalar(metric: str, key: str):
        v = combined.get(metric, {}).get(key)
        import numpy as np

        return None if v is None else float(np.mean(v))

    # HOTA DetA/AssA are alpha-sweep arrays; the official summary reports their mean.
    return {
        "HOTA": scalar("HOTA", "HOTA(0)"),
        "DetA": scalar("HOTA", "DetA"),
        "AssA": scalar("HOTA", "AssA"),
        "MOTA": scalar("CLEAR", "MOTA"),
        "MOTP": scalar("CLEAR", "MOTP"),
        "IDSW": scalar("CLEAR", "IDSW"),
        "IDF1": scalar("Identity", "IDF1"),
        "IDP": scalar("Identity", "IDP"),
        "IDR": scalar("Identity", "IDR"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bench", type=Path, default=BENCH_DEFAULT)
    ap.add_argument(
        "--trackers",
        nargs="+",
        type=Path,
        required=True,
        help="dirs of per-seq <seq>.txt MOT-challenge results",
    )
    ap.add_argument("--metrics", nargs="+", default=["HOTA", "CLEAR", "Identity"])
    ap.add_argument("--seqs", nargs="*", default=None, help="restrict to these sequence names (subset runs)")
    ap.add_argument("--out", type=Path, default=REPO / "bench" / "_eval")
    args = ap.parse_args()

    seqs = seq_names(args.bench)
    if args.seqs:
        unknown = set(args.seqs) - set(seqs)
        if unknown:
            raise SystemExit(f"unknown sequences: {sorted(unknown)}")
        seqs = [s for s in seqs if s in set(args.seqs)]
    if not seqs:
        raise SystemExit(f"no sequences with gt/gt.txt under {args.bench}")
    print(f"bench: {len(seqs)} sequences")
    materialize_gt(args.bench, args.out, seqs)

    rows = {}
    for t in args.trackers:
        t = t.resolve()
        print(f"evaluating {t.name} ...")
        rows[t.name] = eval_tracker(t, args.out, seqs, args.metrics)

    out_df = pd.DataFrame(rows).T.sort_index()
    pd.set_option("display.width", 200)
    print(out_df.round(3).to_string())
    args.out.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out / "scores.csv")
    print(f"\nwrote {args.out / 'scores.csv'}")


if __name__ == "__main__":
    main()
