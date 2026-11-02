# v0 Prototype — Detect & Track Players on One Clip

Spec: [`../../../docs/04-v0-prototype.md`](../../../docs/04-v0-prototype.md).
Testing procedure: [`../../../docs/10-testing-guide.md`](../../../docs/10-testing-guide.md) § 3 (v0 table).

Requires the system `ffmpeg`/`ffprobe` on PATH (frame decode/encode goes
through ffmpeg pipes — OpenCV's bundled ffmpeg fails on AV1/VP9 webm).

Stock YOLO11 (`person` only, zero training) + ByteTrack/BoT-SORT →
overlay video + `tracks.csv` + `fps.json`. This folder is **self-contained**
by design: v0.1/v1 get their own folders and reuse the ideas/artifact
schemas, not this code.

## Setup (one time)

```bash
# from repo root (basketball-player-detect/)
python3.13 -m venv .venv
.venv/bin/pip install -r src/prototype/v0/requirements.txt
```

(`.venv` lives at repo root, shared across prototypes; per-prototype
`requirements.txt` files keep versions reproducible.)

## Run — smoke test (light, ~1 min, safe on a busy GPU)

All commands below run **from the repo root**:

```bash
.venv/bin/python src/prototype/v0/detect_track.py \
  --clip clips/act_state_team_720p.ogv \
  --out  out/smoke/bytetrack \
  --max-frames 120
```

Checks: exit 0, `tracked.mp4` playable, `tracks.csv` pandas-loadable with
sane coordinates, `fps.json` written. (docs/10 § 2, layer L0.)

## Run — FULL passes (⚠️ HEAVY: ask before running on a busy machine)

Full-clip runs are long GPU jobs (order: minutes of wall time per minute of
1080p footage). Run these when the GPU is free:

```bash
PY=.venv/bin/python
D=src/prototype/v0/detect_track.py
# 1. fixed-cam primary clips, ByteTrack (docs/04 procedure step 3)
$PY $D --clip clips/act_state_team_720p.ogv --out out/act_state_team/bytetrack
$PY $D --clip clips/sasebo_youth_1080p.webm --out out/sasebo_youth/bytetrack

# 2. broadcast-style stress clip: BOTH trackers (A/B)
$PY $D --clip clips/hawaii_highlights_1080p.webm --out out/hawaii_highlights/bytetrack --tracker bytetrack
$PY $D --clip clips/hawaii_highlights_1080p.webm --out out/hawaii_highlights/botsort --tracker botsort
```

Tuning knobs (defaults sized for 30 threads / 80 GB RAM / ≤14 GB VRAM):
`--batch-size` (GPU throughput, default 16), `--imgsz` (default 640),
`--threads` (torch CPU threads, default 30), `--device cuda:0|cpu`.
fp16 auto-enables on CUDA. Measured on a *contended* GPU: 1080p broadcast
clip ≈ 41 fps with batch 16 (was ~22 fps unbatched). If the GPU is fully
occupied, force `--device cpu` and raise `--threads`.

## Outputs & reruns

Each run **first deletes** the previous run's artifacts in `--out`
(`tracked.mp4`, `tracks.csv`, `fps.json`, `run_config.json`, `run.log`,
review panels), so an interrupted run never leaves stale mixtures.
Progress + config are logged to `out/<clip>/<tracker>/run.log`, and every
run upserts its summary row into `out/RESULTS.md` (the run ledger).

## Track-level stats (after full runs)

```
.venv/bin/python src/prototype/v0/track_stats.py out/act_state_team/bytetrack
```

Prints the numeric summary used in `docs/notes/v0-findings.md`: churn
(ids/min), track lifetime percentiles, >5 s track counts (incl. the
median-minute acceptance proxy), ghost tracks, id-start bursts.
Accepts multiple run dirs or a glob.

## Review pass (after full runs)

```bash
.venv/bin/python src/prototype/v0/review.py out/act_state_team/bytetrack/tracks.csv
```

Writes `review_summary.txt` + three PNG panels next to the run: player-count
histogram over time, ID longevity strips, ID churn per minute — the eyeball
metrics for the acceptance criteria (docs/04 § Acceptance). Plain script, no
notebook.

## Outputs (per run)

```
out/<clip>/<tracker>/
  tracked.mp4        # overlay: boxes + track ids (h264, ffmpeg-encoded)
  tracks.csv         # frame,time_s,track_id,x1,y1,x2,y2,conf
  fps.json           # processing fps + acceptance flags (>=10fps, <3x realtime)
  run_config.json    # exact settings of the run
  run.log            # full run log (fresh each run)
out/RESULTS.md       # ledger: one row per run, replaced on rerun
```

## Findings note

After reviewing: fill `docs/notes/v0-findings.md` (docs/04 § Procedure step 6)
— detection good enough without fine-tune? camera motion force BoT-SORT?
label budget for the TrackEval mini-benchmark?
