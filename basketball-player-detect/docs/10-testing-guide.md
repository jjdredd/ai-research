# Testing Guide: Verifying Each Prototype After Implementation

Companion to `04-v0-prototype.md` (v0), `09-v0.1-prototype-plan.md` (v0.1),
`08-v1-prototype-plan.md` (v1). Explains **how a developer tests each
proposal once built**: what to run, which artifact proves which acceptance
criterion, and what "pass" means. Every acceptance bar in `04`/`09`/`08`
maps to exactly one row below — no criterion is checked by vibes alone,
except the ones explicitly labeled qualitative (and those have a written
procedure too).

## 0. Shared test assets (built once, used by all three)

| Asset | Location | Used by | Notes |
|---|---|---|---|
| Clip set | `clips/` | v0, v0.1, v1 | ≥2 fixed-cam 2–5 min; 1 broadcast stress clip; 1 quarter-length clip. **Freeze clip hashes** (`clips/MANIFEST.sha256`) — a "pass" on different footage than last time is not a pass |
| Labeled mini-benchmark | `bench/mini-2026-10/` | v0.1, v1 (v0 optional) | SportsMOT-format boxes+IDs+team+number (`08` § Data & benchmark plan); eval-only, frozen; version-tagged |
| Golden fixtures | `bench/fixtures/` | all | ~20 hand-picked frames + expected-stage outputs (see § 2 L1/L2); tiny, checked into git |
| Metrics schema | `bench/schemas/metrics.schema.json` | all | every prototype emits `metrics.json` in one schema so CI can compare any run to any bar |
| Review script | `src/prototype/<p>/review.py` | v0 (mandatory), v0.1/v1 (same pattern, more panels) | plain Python, no notebooks (user preference); text summary + PNG panels; panels defined in § 4 |

**Harness commands** (uniform across prototypes; scripts differ, interfaces
don't):

```bash
make smoke        # L0: pipeline runs on a 300-frame stub, outputs parse
make unit         # L1: pure-logic tests, no models, <60 s, runs in CI on every commit
make stage        # L2: per-stage scoring vs fixtures, small GPU ok
make bench        # L3: full TrackEval + custom scorers on bench/mini-2026-10
make e2e          # L4: quarter-length run -> players.json + overlay + metrics.json
make review       # runs the prototype's review.py against the latest out/ run
```

## 1. What TrackEval covers — and what it doesn't

| Metric | Tool | Covers which acceptance bar |
|---|---|---|
| HOTA / DetA / AssA / IDF1 / IDsw | **TrackEval** (MIT, `05` P3) — unmodified, fed SportsMOT-format GT | tracker bars in all three docs |
| mAP@0.5, recall per slice (normal / occluded / edge-bench) | custom `bench/scorers/det_map.py` (COCO-style eval on detection-only dump) | v1 "beats stock on all 3 slices"; v0.1 ≥70%/≥45% |
| Team accuracy | custom `bench/scorers/team_acc.py` (per-track GT team vs shipped label) | v1 ≥95% / v0.1 ≥85% |
| JNR top-1 / top-3 on readable crops | custom `bench/scorers/jnr.py` (GT number vs cluster vote, restricted to crops meeting the gate) | v1 ≥85% / v0.1 ≥45% |
| IDpurity, named-player coverage, failure-reason completeness | custom `bench/scorers/identity.py` (operates on `players.json` alone) | v1 IDpurity ≥0.9, ≥8/10 named / v0.1 ≥0.6, ≥3/10 |

The three custom identity/team/JNR scorers are **part of the v1/v0.1
deliverables** (`bench/` in both docs); this guide is their acceptance spec.

## 2. The test layers, per prototype

### L0 — smoke (all three)

Goal: the pipeline *runs*. No numbers checked.

1. Trim any fixed-cam clip to 300 frames; run the prototype CLI end-to-end.
2. Assert: exit code 0; overlay mp4 exists and is playable; CSV/JSON outputs
   parse (`pd.read_csv` / `json.load`); coordinates within frame bounds;
   track IDs are integers (not nan/None).

v0 criterion "tracks.csv round-trips" ⇒ this layer. v1/v0.1
"quarter-length input without restart" ⇒ L4, but L0 must pass first.

### L1 — unit tests (pure logic, no models)

Everything downstream of boxes is deterministic logic and gets real unit
tests with synthetic inputs:

| Unit under test | Tested with | Prototypes |
|---|---|---|
| Fusion rule (`08`: name only when team-vote ∧ number-vote ∧ conf ≥ τ) | table-driven: agree/disagree/low-conf inputs ⇒ expect `<Team> #<n>` vs `#?`/`unknown-k` **with failure reason attached** | v0.1, v1 |
| Team k-means + re-vote | synthetic HSV histograms (light kit / dark kit / both-dark) | v0.1, v1 |
| Tracklet merge (gap < N frames ∧ position continuity ∧ embedding distance) | synthetic tracklets + embeddings; assert no merge below thresholds | v0.1, v1 |
| Number majority vote | synthetic per-frame number reads incl. ties and 0-reads | v0.1, v1 |
| Shot-boundary reset logic | synthetic cut list; tracker state reset, gallery persists | v1, v0.1 |
| Heuristic referee class (`09` [3']) | synthetic palettes: dark-vs-dark game ⇒ heuristic disabled flag set | v0.1 only |
| Count/speed/inbounds priors | synthetic positions | v0.1, v1 |

### L2 — stage-level scoring (small clips or fixed frames)

Per-stage numbers *before* integration, to answer "which stage broke":

- **Detector:** score detection dumps on benchmark frames (mAP/recall per
  slice). v1 additionally runs stock-vs-finetune side-by-side — the
  "beats stock on all three slices" bar is decided here, not at E2E.
- **Tracker:** feed **GT detections** to the tracker only (isolates
  association from detection). HOTA/IDF1/IDsw on GT-detections is the
  tracker's honest number; compare A/B configs here.
- **Team/JNR/embeddings:** run on **GT tracks** (isolates upstream error).
- v0 has no L2 by design (single stage pair, measured qualitatively).

### L3 — benchmark run (`make bench`)

TrackEval + the four custom scorers over `bench/mini-2026-10/`; emits one
`metrics.json`. This is the layer every quantitative bar lives at. Output is
committed (`bench/results/<prototype>-<sha>.json`) — **the numbers go in the
commit message** (`08` § Data & benchmark plan, rule 3).

### L4 — end-to-end (quarter-length)

Full pipeline on the quarter clip → `players.json` + overlay + metrics.
Checks functional bars (no manual restart, per-shot resets, schema frozen)
plus the named-player counts.

## 3. Acceptance tables: criterion → test → pass rule

### v0 (`04`) — qualitative bar

| Acceptance criterion (04) | Layer | Procedure | Pass rule |
|---|---|---|---|
| ≥90% visible players detected (fixed cam) | L4 + review script | sample 6×10 s windows; eyeball counts per window against overlay | ≥90% in each window |
| ≥6/10 players hold ID >5 s during continuous play | L4 + review script | ID-longevity panel: per-minute, count tracks alive >5 s | ≥6 in the median minute of play |
| Watchable overlay, ≥10 FPS or <3× realtime | L0/L4 | wall-clock recorded to `fps.json` | either/or |
| tracks.csv round-trips | L0 | `pd.read_csv` + bounds/NaN asserts | no errors, sane coords |
| **Expose** expected failures (pile-up ID swaps, refs-as-players, cut fragmentation, bench flicker) | review checklist § 4 | each failure mode observed and noted in `v0-findings.md` | all four observed *or* explanation why the footage didn't exercise it |

The last row inverts the usual polarity: for v0, **finding** each failure
mode is a pass condition (`04` § Known expected failures).

### v0.1 (`09`) — relaxed quantitative bar

| Acceptance criterion (09) | Layer | Command | Pass rule (from 09's table) |
|---|---|---|---|
| Quarter-length end-to-end, no restart | L4 | `make e2e` | exit 0, one continuous run |
| Detection recall ≥70% normal / ≥45% occluded | L3 | `make bench` → `det_map` | both slices ≥ their bar; edge/bench recorded only |
| IDpurity ≥0.6 | L3 | `identity` scorer | ≥0.6 |
| IDsw/min within ±20% of v0 ByteTrack baseline | L3 | TrackEval, baseline row pinned in `bench/` | ±20% of the frozen v0 number |
| Team accuracy ≥85% | L3 | `team_acc` | ≥85% |
| JNR top-1 ≥45% on readable crops | L3 | `jnr` | ≥45%; readable fraction recorded, not gated |
| ≥3/10 starters named, failure reasons on every miss | L4 | `identity` scorer on `players.json` | ≥3 correct ∧ **0 outputs with a name and no agreement trace ∧ 0 unnamed outputs without a reason string** |
| **No-training invariant** | CI check | `bench/checks/no_training.py`: every checkpoint matches a pinned SHA256 (`models.lock.json` downloaded from public sources); grep suite forbids `optim`/`trainer.fit`/`epochs>` in `src/prototype/v0.1/`; no file in `bench/mini-2026-10/` opened outside scorer code | all three green |
| No runtime gate | — | speed recorded only | cannot fail |
| Optional optimizations don't move metrics <2% | L3 re-run | after any optimization patch | `‖Δmetrics‖ < 2%` or patch is reverted |

### v1 (`08`) — full quantitative bar

| Acceptance criterion (08) | Layer | Command | Pass rule |
|---|---|---|---|
| Quarter-length without restart | L4 | `make e2e` | exit 0 |
| IDpurity ≥0.9 | L3 | `identity` | ≥0.9 |
| Published IDF1/IDsw not worse than M2 baseline run | L3 | compare vs pinned `bench/results/v1-m2.json` | ≥ baseline − ε (ε declared at M2) |
| Fine-tuned detector beats stock on all 3 slices | L2 | stock-vs-finetune `det_map` | margin > 0 on each slice, margins recorded |
| Team acc ≥95% | L3 | `team_acc` | ≥95% |
| JNR top-1 ≥85% on readable crops | L3 | `jnr` | ≥85% ∧ readable ≥60% |
| ≥8/10 starters named correctly | L4 | `identity` | ≥8 correct by quarter end |
| Never a silent wrong name | L4 | `identity` failure-reason audit (same as v0.1) | 0 violations |
| Runtime ≥5× realtime, recorded | L4 | wall-clock | recorded; fails only if <5× |
| Regression gate | L3 in CI | `make bench` vs `bench/results/best.json` | any metric regression > declared ε blocks merge |

## 4. Qualitative review checklist (`make review`)

One review script per prototype (plain Python + PNG panels, no notebooks),
four panels, used at every prototype (v0 mandatory; v0.1/v1 as triage when
metrics don't explain a failure):

1. **Count-over-time histogram** — expected ~10 + refs; dips = misses,
   spikes = ghosts.
2. **ID longevity strips** — per-track lifespan bars; churn per minute.
3. **Cluster view** (v0.1/v1) — per player cluster: team color, top-3
   number votes, gallery crops (last 8 crops a cluster saw — contamination
   is visible in the gallery).
4. **Failure-reason ledger** — every unnamed/`#?` output with its attached
   reason, grouped by cause type.

Plus the v0-specific checklist: were pile-up switches, ref-as-player tracks,
cut fragmentation, and bench flicker all observed?

## 5. Determinism & reproducibility rules

- `pip` lockfile per prototype; model weights pinned by URL+SHA256
  (`models.lock.json`) — stock weights are downloaded, never rebuilt, and the
  v0.1 no-training check audits exactly this.
- Fixed random seeds for k-means, clustering thresholds, tracker init;
  detector inference at `half=False` on CPU for benchmark runs (GPU
  nondeterminism recorded as run variance, ± reported, not hidden).
- A benchmark pass is only valid if clip hashes and `models.lock.json` match
  the pinned manifest.
- Every `make bench` writes `bench/results/…-<git-sha>.json`; merges to main
  require the JSON to update in the same PR (CI-enforced for v1, per `08`'s
  "numbers in commit messages" rule).

## 6. Suggested build order for the harness itself

The harness is small and shared — build it **during v0/v0.1 M1**, not after:

1. `metrics.json` schema + TrackEval wrapper (needed for v0.1 M1 baseline rows anyway).
2. L0 smoke + clips MANIFEST (during v0).
3. Custom scorers as each signal ships: `team_acc` with M3, `jnr` with M3, `identity` with M4.
4. `no_training.py` invariant check lands with v0.1 M2 — it guards the one
   claim (`09`: "no training or fine-tuning whatsoever") that would
   otherwise be unfalsifiable.

## Cross-references

- `04` § Acceptance criteria / § Known expected failures → § 3 v0 table + § 4
- `09` § Acceptance / § Speed / § Components → § 3 v0.1 table (incl. the no-training invariant)
- `08` § Data & benchmark plan / § Acceptance criteria → § 3 v1 table + § 5 CI rule
- `06` — TrackEval MIT (unmodified use), weight-license pins in `models.lock.json`
- `07` — SportsMOT-format GT is the benchmark's annotation format
