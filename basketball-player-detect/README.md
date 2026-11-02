# Basketball Player Detection, Tracking & Identification — Research

Goal: from a **video recording of a basketball game**, **detect** every player,
**track** them across frames with stable IDs, and **distinguish** them
(team assignment + per-player identity, e.g. jersey number / ReID embedding).

This repository captures the state of the art (papers, code, projects, products,
algorithms) as of research conducted 2025-10, starting from the reference
repository [jjdredd/ai-research](https://github.com/jjdredd/ai-research),
whose raw materials live directly in the parent directory (the `ai-research` repo root).

## Contents

| Document | What's inside |
|---|---|
| [docs/01-repo-review.md](docs/01-repo-review.md) | Review of the papers/materials in the `jjdredd/ai-research` repo (mostly basketball **action recognition** — adjacent to, but not the same as, our detection/tracking problem) |
| [docs/02-solution-landscape.md](docs/02-solution-landscape.md) | The broader solution landscape: MOT algorithms, sports-specific papers, benchmarks/datasets, ReID & jersey-number recognition, team assignment, commercial products, open-source projects |
| [docs/03-recommended-architecture.md](docs/03-recommended-architecture.md) | A concrete recommended pipeline (detect → track → assign team → identify) with candidate components, trade-offs, evaluation plan and risks |
| [docs/04-v0-prototype.md](docs/04-v0-prototype.md) | v0 prototype proposal: same-day YOLO11 + ByteTrack + supervision spike — scope, deliverables, code sketch, acceptance criteria |
| [docs/05-literature-review.md](docs/05-literature-review.md) | Annotated **literature review / reading list**: papers, benchmarks, and systems for detection, tracking, team assignment, ReID & jersey-number recognition — single-algorithm methods and full pipelines, in reading order, with a 10-paper core path |
| [docs/06-licenses-and-patents.md](docs/06-licenses-and-patents.md) | License & IP table for every method/model/dataset in the reading list (code, weights, data terms) + patent landscape (SportVU/Second Spectrum/Hawk-Eye…) and commercial-safe build combinations |
| [docs/07-datasets.md](docs/07-datasets.md) | Dataset catalog for detection/tracking/identification: SportsMOT, TeamTrack, SoccerNet, DanceTrack, SportVU dumps, Roboflow Universe, pretraining sets, ball-tracking corpora — each with contents, access and **license terms** |
| [docs/08-v1-prototype-plan.md](docs/08-v1-prototype-plan.md) | v1 prototype plan: quarter-length sessions, quantitatively gated detection (TrackEval mini-benchmark), and individual player identification fused from jersey number + team + appearance gallery |
| [docs/09-v0.1-prototype-plan.md](docs/09-v0.1-prototype-plan.md) | v0.1 variant: **all v1 functionality with zero training/fine-tuning** (stock pretrained weights only), accuracy bars at ≈v0 level (below v1), no speed requirements — doubles as the frozen stock-baseline row for v1's fine-tune claims |
| [docs/10-testing-guide.md](docs/10-testing-guide.md) | How a developer **tests each prototype** once implemented: shared harness (smoke/unit/stage/bench/e2e layers), criterion→test→pass-rule tables for v0/v0.1/v1, custom scorers, the v0.1 no-training invariant, determinism & CI rules |
| [`..`](../) | The reference repo's raw materials at the `ai-research` root (org files, PDF, mmaction2 results) |
| [notes/](notes/) | Raw parsed text of papers we read in full |

## TL;DR

- The task decomposes into four well-studied sub-problems: **person detection**
  (YOLO/DETR-family, fine-tuned on sports data), **multi-object tracking**
  (ByteTrack / BoT-SORT / OC-SORT; basketball-specific **Basketball-SORT**, 2024),
  **team assignment** (jersey-color clustering — cheap and robust), and
  **player identification** (ReID embeddings + jersey-number OCR;
  Koshkina & Elder, CVPRW 2024 gives a general framework).
- Best-matching benchmarks to prototype and evaluate against:
  **SportsMOT** (ICCV 2023, includes basketball), **TeamTrack** (full-pitch
  multi-sport, includes basketball), **SoccerNet** tracking/ReID (most mature
  ecosystem, adjacent sport).
- Industry reference points: NBA's optical tracking line
  (**SportVU → Second Spectrum**, now Genius Sports' 14-camera rig) prove
  fixed multi-camera rigs give near-perfect results; single broadcast-camera
  solutions (Roboflow pipelines, PlayerTV, TrackBox) are the realistic path for
  arbitrary game recordings.
- A practical v1 (all open-source, single fixed camera): fine-tuned YOLOv8/YOLO11
  player detector → ByteTrack/BoT-SORT tracker → HSV k-means jersey-color team
  assignment → ReID embeddings (e.g. OSNet/CLIP-ReID) for stable identity →
  optional jersey-number OCR (CRNN/PaddleOCR fine-tuned) for named-player IDs.
