# v1 Prototype Plan: Long-Session Tracking, Stricter Detection, Player Identity

Status: **proposal** (build starts after v0 findings, `04-v0-prototype.md`
§ Procedure step 6). Supersedes the v1/v2 split in
`03-recommended-architecture.md` § "Suggested build order": v1 scope is
**expanded** to include individual player identification (jersey number +
team) because that is the feature the whole pipeline exists for — deferring
it a further phase delays the only output that distinguishes us from a
generic tracker demo. Court mapping (stage 6 of `03`) stays out of v1.

> **Sidecar variant (Oct 2026):** `09-v0.1-prototype-plan.md` specifies a
> full-functionality, **no-training** variant of this plan (stock weights,
> relaxed bars, no runtime gate) that runs on the same `bench/mini-2026-10/`
> and freezes the stock-baseline rows every fine-tune below must beat.
> Testing procedure for all prototypes: `10-testing-guide.md`.

## What v1 adds over v0

| Dimension | v0 (shipped bar) | v1 target |
|---|---|---|
| Session length | 2–5 min clips | one full quarter (~10 min game clock, 20–40 min wall time incl. stoppages) without manual restart |
| Detection | eyeballed, "≥90% visible players" | quantitative on a labeled mini-benchmark via TrackEval (see Acceptance) |
| Identity | per-clip track IDs, switches tolerated | persistent **named** IDs: `Home #7` style, stable across occlusions, stoppages, and tracklet fragmentation |
| Team | out of scope | Home/Away assignment per player |
| Eval | review notebook histograms | SportsMOT-format mini-benchmark + TrackEval regression gate |

## Objectives (measurable)

1. **Longer-time tracking.** Identity survives: ≥30 s occlusion (bench,
   referee screen, out-of-bounds walk-off), re-entry at a different frame
   position, and brief detector dropouts. ID switches per minute of play
   materially below v0's ByteTrack baseline (v0 finding sets the exact number).
2. **Higher detection requirements.** Fine-tuned multi-class detector
   (`player`, `referee`, `ball`) beats stock YOLO11-person on our labeled
   mini-benchmark on all of: mAP@0.5, recall of *occluded* players (visible
   area <50%), and precision at frame edges/benches. No more numeric gate
   guessing — we publish the bar after the first benchmark run (expected
   calibration point: SportsMOT basketball baselines, HOTA ≈ 55–65 range).
3. **Individual player identification.** Final output per player per quarter:
   team label + jersey number + a persistent ID, with per-identification
   confidence. Team assignment and number read are independent signals fused
   by vote (see Identity layer).

## Architecture (v1 = stages 1–5 of `03-recommended-architecture.md`)

```
video (quarter-length) ──► [0] shot-boundary scan (PySceneDetect)
                              per-shot tracker reset boundaries
              │
              ▼
      [1] Fine-tuned detector        YOLO11m or RF-DETR, classes: player/referee/ball
              │                      low conf (0.3), weak detections kept for assoc.
              ▼
      [2] Tracker A/B                OC-SORT/ByteTrack (static) vs BoT-SORT (motion)
              │                      + basketball priors: 10-on-10 count, speed gate,
              ▼                      inbounds ROI (manual polygon, no homography yet)
      [3] Team assignment            tracklet color histograms → k-means k=2
              │                      (+ ref class exclusion); manual kit override flag
              ▼
      [4] Tracklet-merge + gallery   embedding gallery per cluster; merge split
              │                      tracklets (gap < N frames, position continuity,
              ▼                      embedding distance) → game-long player clusters
      [5] Jersey number + vote       PaddleOCR/CRNN fine-tune on high-quality crops
              │                      (>96 px, front-facing by pose heuristic);
              ▼                      majority number per cluster
      outputs: players.json (Home #7, track spans, gallery stats) + overlay video
```

No court homography in v1: the inbounds constraint uses a **manual court
polygon per camera** instead (cheaper, sufficient for ROI filtering and
speed gates). Homography stays v2+.

## Components & decisions

| Stage | Choice | Alternatives | Decision criterion |
|---|---|---|---|
| 1 Detector | YOLO11m fine-tune (SportsMOT basketball train split + Roboflow Universe picks + our SAM2-labeled frames), classes `player/referee/ball` | RF-DETR (Apache weights — cleanest license, `06` table); RT-DETR (official Apache weights; avoid Ultralytics AGPL mirror) | whichever wins mAP/recall on our benchmark **and** clears license review for intended use |
| 2 Tracker | BoT-SORT default; OC-SORT for static cam | MixSORT ckpts (⚠️ research-only weights, `06`); Basketball-SORT association rules ported manually (paper-only, ❌ weights) | TrackEval HOTA/IDF1 on our benchmark; v0 findings on camera motion |
| 3 Team | HSV histogram k-means + re-vote per tracklet | learned team-affiliation net (SoccerNet-style) as fallback for dark-kit games | agreement ≥95% on labeled frames; manual color override input |
| 4 Identity gallery | mean-of-top-k clean-crop embeddings; cluster + merge split tracklets | OSNet/CLIP-ReID (⚠️ pedestrian weights, identical-jersey caveat per `03` risks) vs SigLIP features (✅ Apache weights) | IDpurity on our labeled tracks; A/B both embedders — pedestrian ReID is expected to underperform on identical kits |
| 5 JNR | PaddleOCR CRNN fine-tune (✅ Apache weights) on real crops + **synthetic jersey renders**; majority-vote per cluster | `mkoshkina/jersey-number-pipeline` — ❌ no weights, no license: **reference only, not a dependency** | top-1 number accuracy on labeled crops ≥85%; crop-gating must keep ≥60% of players readable per quarter |
| 0 Shot cuts | PySceneDetect thresholds tuned on our footage | — | per-shot reset; identity gallery persists *across* shots |

**Fusion rule (the actual "identification"):** a player cluster is *named* as
`<Team> #<n>` only when team vote and number vote agree and number confidence
≥ threshold; otherwise it ships as `Home #?` / `unknown-3` with the failure
reason attached. Never silently guess.

## Data & benchmark plan

1. Label **10–15 min** of target footage (SportsMOT-format boxes + track IDs
   + team + jersey number per track; SAM2-assisted, ~2 labeler-days).
2. Freeze as `bench/mini-2026-10/`; publish per-stage targets from the first
   full-pipeline run (detector: mAP/recall table; tracker: HOTA/DetA/AssA/
   IDF1/IDsw; team: accuracy; JNR: top-1/top-3 on readable crops; identity:
   IDpurity + named-player coverage).
3. Every later change runs the benchmark → numbers in commit messages.

## Deliverables

```
src/prototype/v1/
  finetune/detector/     # training configs + scripts (ultralytics or RF-DETR)
  pipeline.py            # per-frame orchestration of stages 1–5 (CLI: clip in)
  identity/              # gallery, merge logic, team vote, number vote, fusion
  bench/                 # TrackEval wrappers, mini-benchmark loader, scorers
  annotate/              # SAM2-assisted labeling helpers, synthetic number renders
out/quarter1/            # players.json + overlay mp4 + metrics.json per run
docs/notes/v1-findings.md
```

## Milestones

| # | Milestone | Exit check |
|---|---|---|
| M1 | Benchmark labeled; detector fine-tune beats stock | mAP@0.5 up vs stock on `bench/`, both license options documented |
| M2 | Long-session tracking | quarter-length clip runs end-to-end; IDsw/min < v0 baseline; per-shot resets correct |
| M3 | Team + number signals live | team acc ≥95%; JNR top-1 ≥85% on readable crops (bar from first run if M1 shows unrealistic) |
| M4 | Fusion + named players, full integration | ≥8 of 10 starters named correctly by end of quarter; `players.json` schema frozen |

## Acceptance criteria (v1 bar — quantitative)

- **Tracking:** quarter-length input without restart; IDpurity ≥0.9 on
  benchmark; published IDF1/IDsw numbers not worse than the M2 baseline run.
- **Detection:** fine-tuned detector beats stock person-model on all three
  benchmark slices (normal, occluded, edge/bench) — margins recorded.
- **Identification:** by quarter end, ≥8/10 starters correct team+number;
  every miss carries an explicit failure reason, never a silent wrong name.
- **Runtime:** offline — ≥5× realtime on one GPU is plenty; record the number.

## Risks & mitigations (v1-specific deltas on top of `03`)

| Risk | Mitigation |
|---|---|
| Number occlusion dominates (players face away) | crop-gating + per-cluster accumulation over time (numbers accrue across a quarter); accept `#?` output |
| Identical kits break embedding clustering | fuse with team color + trajectory continuity + count priors; do not trust embeddings alone |
| Gallery contamination (merged wrong people early poisons the quarter) | conservative merge thresholds + split-repair pass at quarter end + IDpurity metric in CI |
| Long-session drift in team colors (lighting changes) | re-cluster team palettes per period; manual kit override input |
| JNR fine-tune data too small | synthetic rendering of digit sets onto player crops (proven in football, `05` §; license: our own renders) |
| Scope creep back toward homography/stats | hard exclusion; `players.json` px coords only |

## Time box

Two weeks part-time: M1 ≈ 3 days (labeling parallel), M2 ≈ 3 days,
M3 ≈ 4 days, M4 ≈ 2 days. If M1 shows the label budget is insufficient,
stop and renegotiate scope before building on sand.

## Open questions

1. Which footage: one of the v0 fixed-cam clips extended to quarter length,
   or a broadcast quarter (adds shot-cut handling to M2)?
2. Do we run number reading on every frame above crop bar (accuracy) or
   sampled (compute)? Default: sampled at 2 FPS.
3. v0 findings may force BoT-SORT; confirm before M2 tracker A/B.
