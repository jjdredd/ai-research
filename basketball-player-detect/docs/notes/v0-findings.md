# v0 prototype — findings note

Run date: 2026-11-02. Pipeline: `src/prototype/v0/` (commit range
`76e6220..HEAD`), spec: [`../04-v0-prototype.md`](../04-v0-prototype.md),
acceptance table: [`../10-testing-guide.md`](../10-testing-guide.md) § 3.

## 1. Tests implemented & how to reproduce

| Test | Tool | What it checks |
|---|---|---|
| Pipeline run (4 passes) | `detect_track.py` | end-to-end decode→detect→track→artifacts; wall-clock/fps gate recorded to `fps.json` |
| Review pass | `review.py` | boxes-per-frame histogram, ID-longevity strips, churn-per-minute panels + text summary per run |
| Track-level stats | `track_stats.py` | churn (ids/min), lifetime percentiles, >1s/>5s counts, median-minute long tracks, ghost (1-box) tracks, id-start bursts |
| Round-trip check | inside `review.py`/`track_stats.py` | `pd.read_csv` + coordinate-bounds asserts on every `tracks.csv` |

All four heavy passes ran on `cuda:0` (RTX 4080) with the optimized defaults:
ffmpeg pipe decoding, batch 16, fp16 (`quantize=16`), imgsz 640, conf 0.3,
30 CPU threads. Reproduce from repo root:

```bash
D=src/prototype/v0/detect_track.py
.venv/bin/python $D --clip clips/act_state_team_720p.ogv      --out out/act_state_team/bytetrack
.venv/bin/python $D --clip clips/sasebo_youth_1080p.webm      --out out/sasebo_youth/bytetrack
.venv/bin/python $D --clip clips/hawaii_highlights_1080p.webm --out out/hawaii_highlights/bytetrack --tracker bytetrack
.venv/bin/python $D --clip clips/hawaii_highlights_1080p.webm --out out/hawaii_highlights/botsort   --tracker botsort
.venv/bin/python src/prototype/v0/review.py     out/<run>/tracks.csv
.venv/bin/python src/prototype/v0/track_stats.py out/<run>
```

## 2. Raw results

From `out/RESULTS.md` + `track_stats.py`:

| run | frames | proc fps | wall s | ids | ids/min | med life s | p90 life s | >5s tracks | median-min >5s | ghosts (1 box) | conf mean |
|---|---|---|---|---|---|---|---|---|---|---|---|
| act_state_team / bytetrack | 1453 | 76.8 | 18.9 | 297 | 368 | 0.60 | 3.76 | 24 | 24 | 22 | 0.52 |
| sasebo_youth / bytetrack | 1783 | 59.2 | 30.4 | 333 | 336 | 1.27 | 4.63 | 31 | 31 | 11 | 0.71 |
| hawaii_highlights / bytetrack | 15151 | 67.9 | 224.5 | 2343 | 278 | 0.50 | 2.57 | 44 | 8 | 145 | 0.71 |
| hawaii_highlights / botsort | 15151 | 43.0 | 354.4 | 2293 | 272 | 0.60 | 2.74 | 53 | 14 | 149 | 0.69 |

Boxes/frame (mean / p10): act 8.4/5.0; sasebo 9.9/2.0; hawaii ~4.2–4.7/~1–2
(steady), 7.0 in the final segment.

## 3. Acceptance checklist (docs/10 § 3 v0 table)

| Criterion | Result | Evidence |
|---|---|---|
| ≥90% visible players detected (fixed cam) | **FAIL on act_state / PASS on sasebo** | act mean 8.4 boxes/frame vs ~10 players+refs expected; **visually confirmed** on `out/evidence/act_t10.png`: most visible players missed at t=10 s (only 4–7 boxes, frame conf tops out at 0.62; 305/1449 frames ≤6 boxes). Detector is markedly weaker on this Theora-720p clip (conf mean 0.52 vs 0.71 elsewhere) — small players + compression + motion blur. sasebo mean 9.9 meets the bar on average (dips to p10=2 on wide/bench frames). → fine-tune justified. |
| ≥6/10 players hold ID >5 s (median minute) | **PASS** | median-minute long tracks: act 24, sasebo 31, hawaii-bytetrack 8, hawaii-botsort 14 (bar ≥6). Note: long tracks exist, but they coexist with massive churn (see § 4). |
| Watchable overlay, ≥10 FPS or <3× realtime | **PASS** | 43.0–76.8 proc fps vs 25–30 fps clips → 1.4–3× realtime decode-to-output; all `fps.json` gates green (`ok=true` in `out/RESULTS.md`). |
| tracks.csv round-trips | **PASS** | all 4 load via pandas; coordinate sanity "OK (all within frame-ish bounds)"; no NaN. |
| Expose 4 expected failure modes | **PASS (3 observed, 1 partially)** | see § 4 |

## 4. Expected-failure-mode observations

1. **Cut fragmentation (broadcast)** — observed, strongest signal. Hawaii id
   starts burst ~7–19 per 30 s vs a fixed-cam baseline; median track lifetime
   collapses to 0.5 s (hawaii) vs 1.27 s (sasebo fixed cam). Every hard cut in
   the highlight reel kills all ids and mints new ones. ByteTrack vs BoT-SORT
   barely differ → re-association across cuts is a shared blind spot (matches
   expectation; motivates per-shot segmentation in v1).
2. **Bench / partial-player flicker** — observed via ghost tracks: 11–22
   single-box tracks on fixed cam, 145–149 on broadcast; sasebo boxes/frame
   dips to p10=2 when players leave the framed area.
3. **Pile-up ID swaps** — partially exercised. Continuous-contact segments show
   churn (ids/min 272–368 even on fixed cam) consistent with swap-and-recreate
   behavior; sasebo evidence frame (`out/evidence/sasebo_t30.png`) reviewed and
   judged good. Individual swap events not isolated frame-by-frame; evidence
   frames kept for manual re-check.
4. **Refs-as-players** — partially exercised. act_state clip mean 8.4 boxes/
   frame sits *above* 10-player expectation at peaks (p90=12), consistent with
   referees/spectators being tracked; no dedicated referee disambiguation
   possible with COCO-only classes. Overlay spot-check did not flag obvious ref
   boxes, but detection misses on the act clip dominate there — re-check after
   the v0.1 fine-tune.

## 5. Engineering findings (affect v0.1/v1 tooling)

- **OpenCV cannot decode AV1/VP9 webm here** (bundled ffmpeg → "Failed to get
  pixel format", 0 frames). Fixed by piping rawvideo through system ffmpeg
  (libdav1d) for both decode and encode; `--decoder ffmpeg|cv2` flag kept.
- **Throughput**: batching (16) + fp16 took the 1080p broadcast pass from
  ~21.8 fps (single-frame, fp32) to 43–68 fps on a *contended* GPU. v1 can
  afford imgsz 960–1280 within the same budget.
- ultralytics ≥8.4: `half=` deprecated → `quantize=16` (fixed).
- Reruns are idempotent: `--out` artifacts deleted at start; every run upserts
  a row in `out/RESULTS.md`; per-run `run.log` kept.

## 6. Conclusions (the three questions from 04 § Procedure 6)

1. **Is stock detection good enough for v1 without fine-tune?** **No** —
   visually confirmed misses on act_state (most players missed at t=10 s);
   sasebo passes on average but dips. Below the 90% bar overall. Fine-tuning on basketball frames (the v0.1 plan) is
   justified; class list should add `referee` and `ball`.
2. **Does camera motion force BoT-SORT?** **Not by itself.** BoT-SORT beat
   ByteTrack only slightly on the broadcast clip (53 vs 44 long tracks,
   14 vs 8 median-minute long tracks) at ~1.6× wall time. The dominant failure
   is cut/occlusion re-association, not camera-motion compensation — a
   Basketball-SORT-style per-shot pipeline + appearance re-id is the better
   investment than BoT-SORT camera motion alone.
3. **Annotation volume for the TrackEval mini-benchmark?** The churn numbers
   show raw id-counts are useless without ground truth; ~10 minutes of
   frame-level annotation (≈60 s fixed-cam + ≈60 s broadcast, sampled every
   5th frame) is enough to pin detection recall, IDpurity and IDsw/min baselines
   for v0.1's `bench/`.

**Overall verdict: v0 passes its qualitative bar except the detection-count
criterion, which fails clearly on the act_state clip** (visually confirmed
misses; see § 3/§ 4). That failure is itself the point of v0: it produces
exactly the evidence that motivates v0.1 (fine-tune on basketball frames,
add `referee`/`ball` classes, consider imgsz ↑ given the fp16/batch
throughput headroom) and v1 (per-shot cut segmentation + appearance re-id).
Proceed to v0.1 per `docs/09`.
