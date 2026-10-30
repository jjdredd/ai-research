# Recommended Architecture (v1 proposal)

Target: a single **game recording** (assumed one mostly-static wide camera;
broadcast handling described as a variant) → per-player tracks with team
labels and persistent identities, optionally in court coordinates.

## Pipeline

```
video ──► frame sampler
              │
              ▼
      [1] Player detector           YOLO11/RT-DETR fine-tuned (players, refs, ball)
              │  boxes + conf
              ▼
      [2] Tracker                   BoT-SORT (camera motion) or OC-SORT/ByteTrack (static cam)
              │  tracklets (stable IDs, mostly)
              ▼
      [3] Team assignment           per-tracklet HSV/mask color histogram → k-means k=2
              │                     (+ ref class filter); re-vote over tracklet lifetime
              ▼
      [4] Identity layer            ReID embedding bank per tracklet (OSNet/CLIP-ReID,
              │                     sports-finetuned if available) + agg clustering
              ▼                     → game-long player IDs
      [5] (Optional) Jersey-number  Koshkina&Elder pipeline / CRNN-PaddleOCR fine-tune;
              │                     number+team+embedding vote → named player
              ▼
      [6] (Optional) Court mapping  static homography (fixed cam) or line-based
                                    per-frame calibration (broadcast)
              ▼
      outputs: per-player trajectories (px + court coords), speed/distance,
               team possession aggregates; JSON/CSV + overlay video
```

## Stage-by-stage choices & rationale

**1. Detection.** Start with off-the-shelf YOLO11 person model; fine-tune on a
basketball set (Roboflow Universe / E-BARD / SportsMOT train split) adding
`referee` and `ball` classes. Confidence-threshold **low** (e.g. 0.3):
ByteTrack-style association benefits from weak detections; filter later by
track length.

**2. Tracking.** All candidates available in Ultralytics / Roboflow Trackers /
MMTracking, so A/B them on our footage with TrackEval:
- Static camera → **OC-SORT** or **ByteTrack** first (fast, strong on SportsMOT).
- Any camera motion → **BoT-SORT** (built-in global-motion compensation).
- If identity switches dominate → add ReID appearance to tracker, and try
  **Basketball-SORT** ideas (trajectory-projected matching, BGR/RLLI rules) —
  it beat generic trackers on fixed-camera basketball (HOTA 63.48).
- Basketball priors worth adding regardless: inbounds constraint (post-
  homography), max speed gate, 10-on-10 count prior, referee exclusion.

**3. Team assignment.** Sample mask/dominant colors from each tracklet's
visible frames; illuminate-normalized histograms; k-means k=2; assign Home/Away
by majority vote; flag ambiguous kits (both dark) for the learned-classifier
fallback (SoccerNet-style team-affiliation net).

**4. Identity (distinguish individuals).** Two tiers:
- *Within a track:* tracker handles it; merge split tracklets by
  embedding-distance + spatio-temporal plausibility (gap < N frames, position
  continuity).
- *Across the game:* maintain a per-player embedding gallery (mean of top-k
  clean crops); cluster with threshold; this yields "Player A #7 Home" style
  persistent IDs even after long occlusions.

**5. Jersey numbers (optional but highest-value for naming players).** Use
`mkoshkina/jersey-number-pipeline` or a CRNN/PaddleOCR fine-tune; run only on
high-priority crops (unoccluded, >96 px tall, front-facing by pose heuristic);
majority-vote number per track; resolve conflicts with embeddings. This is the
piece that turns tracks into named players and matches what TrackBox/Roboflow
products sell.

**6. Court mapping (optional).** For fixed cameras: manual 6–8 landmark click
once + homography; validate against court line detector. For broadcast:
restrict outputs to per-shot trajectories or invest in line-based calibration
(NVIDIA blog / KaliCalib) — biggest scope risk, do last.

## Adjacent techniques to keep on the radar

- **Pose estimation** (top-down RTMP/HMR on crops): pose features improve
  ReID under occlusion and unlock downstream action recognition (repo's 3D-CNN
  literature plugs in here — detection/tracking feeds crop sequences to a
  temporal classifier).
- **SAM2 / Track-Anything** for annotating ground truth fast (bootstrapping
  our own fine-tunes).
- **Multi-camera / LPS** (wearables): out of scope for a recording, but the
  quality bar from SportVU/Second Spectrum (§7 of landscape doc).

## Evaluation plan

1. Label ~5–10 min of our target footage (SportsMOT-format annotations;
   SAM2-assisted).
2. Run TrackEval: **HOTA / DetA / AssA / IDF1 / IDsw** per tracker variant;
   plus team-assignment accuracy and (later) IDpurity of the identity layer.
3. Compare against SportsMOT published baselines for calibration (expect
   IDF1 ≪ DetA; association is the bottleneck).
4. Regression-gate the pipeline on this mini-benchmark.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Heavy mutual occlusion → ID switches | Trajectory-based association (Basketball-SORT), ReID gallery merging, count priors |
| Identical jerseys break appearance ReID | Lean on team color + trajectory + jersey number, not generic pedestrian ReID |
| Broadcast cuts/zooms | Shot-boundary detection (PySceneDetect) → reset trackers per shot; per-shot calibration |
| Refs/bench crowd misdetected as players | Explicit ref class + court-region mask post-homography |
| Dark kits both teams | Learned team-affiliation fallback; manual team color override |
| No basketball JNR dataset | Synthetic jersey-number rendering (proven in football) + fine-tune |

## Suggested build order

> **Update (Oct 2026):** the v1 scope below was later **expanded** — steps 2
> and 3 merged into a single v1 that already delivers individual player
> identification (number + team). Authoritative v1 spec:
> [08-v1-prototype-plan.md](08-v1-prototype-plan.md).

1. v0: Ultralytics YOLO11-person + ByteTrack + supervision overlay — same day,
   qualitative sanity on our footage. Specified in detail in
   [04-v0-prototype.md](04-v0-prototype.md).
2. v1: fine-tuned detector, OC-SORT/BoT-SORT A/B, color team assignment,
   TrackEval mini-benchmark.
3. v2: identity gallery (ReID) + jersey numbers.
4. v3: court homography + stats (distance/speed/possession proxies).
