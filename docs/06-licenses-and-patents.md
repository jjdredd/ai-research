# Licenses & IP Landscape
## Code, model weights, datasets, and patents for every method in the reading list

Companion to `05-literature-review.md` and `07-datasets.md`.

Code licenses verified via the GitHub license API (Oct 2025). ⚠️ Three things
this table makes visible:

1. **Permissive code ≠ free output.** MIT tracker code fed with AGPL YOLO
   weights or non-commercial datasets can still yield a non-shippable product.
2. **The datasets are the restrictive layer.** Almost every sports benchmark
   carries non-commercial and/or broadcast-copyright constraints.
3. **Academic methods are essentially patent-free; the industry systems are
   not.** No known patents cover SORT/ByteTrack/OC-SORT-style association or
   jersey-number OCR as such. The patented territory is *deployed sports
   tracking systems* (see §Patents below).

> This is research notes, **not legal advice**. Re-check each license at the
> source before any commercial use; licenses change (ByteTrack moved orgs and
> several projects relicensed in recent years).

## Master table

### Trackers (association / tracking-by-detection)

| Method | Code (license) | Weights | Notes |
|---|---|---|---|
| SORT | no official code release | — | reimplementations are many and mixed-license |
| DeepSORT | no official code release | — | canonical impls: py-mot / third-party (MIT-ish) |
| **ByteTrack** | `FoundationVision/ByteTrack` — **MIT** | n/a (detector's license applies) | repo moved from `ifzhang/ByteTrack` |
| **OC-SORT** | `noahcao/OC_SORT` — **MIT** | n/a | |
| **BoT-SORT** | `NirAharon/BoT-SORT` — **MIT** | n/a | |
| StrongSORT | `dyhBUPT/StrongSORT` — **GPL-3.0** | TorchReID weights | GPL viral → affects anything you link into |
| Tracktor | no official code | — | third-party only |
| FairMOT | `ifzhang/FairMOT` — **MIT** | research weights, unlicensed | |
| CenterTrack | `xingyizhou/CenterTrack` — **MIT** | research weights | |
| MOTR | `megvii-research/MOTR` — **custom/non-standard** (`NOASSERTION`) | research | read LICENSE before use |
| TransTrack | `PeizeSun/TransTrack` — **MIT** | research | |
| TrackFormer | `timmeinhardt/trackformer` — **Apache-2.0** | research | |
| QD-TRACK | no public official code found | — | results reproduced via SportsMOT baselines |
| SAM | `facebookresearch/segment-anything` — **Apache-2.0** | **Apache-2.0** (re-released; originally NC) | |
| SAM 2 | `facebookresearch/sam2` — **Apache-2.0** | **Apache-2.0** | |
| Segment-and-Track-Anything | `z-x-yang/Segment-and-Track-Anything` — **AGPL-3.0** | SAM weights Apache | AGPL wrapper — keep it out of products |

### Re-identification & appearance models

| Method | Code (license) | Weights | Notes |
|---|---|---|---|
| OSNet / deep-person-reid | `KaiyangZhou/deep-person-reid` — **MIT** | research | pedestrian-trained; weights include Market-1501 (research-only data) |
| FastReID | `JDAI-CV/fast-reid` — **Apache-2.0** | research | same data caveat |
| CLIP-ReID | `Syliz517/CLIP-ReID` — **MIT** | research | built on OpenCLIP (BSD-family) |
| SoccerNet-ReID models | `SoccerNet/sn-reid` — **MIT** (code) | trained on SoccerNet data → inherits its research-only terms | |
| SportsMOT baselines | `MCG-NJU/SportsMOT` — **no license file** | — | default copyright: all rights reserved — ask before shipping |

### Jersey-number recognition / identification

| Method | Code (license) | Weights | Notes |
|---|---|---|---|
| Koshkina & Elder JNR framework | `mkoshkina/jersey-number-pipeline` — **no LICENSE file** | not released | all-rights-reserved by default; paper is freely readable, code is not licensed |
| CRNN / PaddleOCR (typical number readers) | e.g. PaddlePaddle/PaddleOCR — **Apache-2.0** | Apache-2.0 | PaddleOCR is the most permissive practical OCR stack |

### Detectors & tooling (the licenses that actually bite)

| Component | Code (license) | Weights | Notes |
|---|---|---|---|
| **Ultralytics YOLOv8/YOLO11** | `ultralytics/ultralytics` — **AGPL-3.0** | **AGPL-3.0** | commercial products need an Ultralytics Enterprise license; the usual first legal surprise |
| RF-DETR (Roboflow) | `roboflow/RFDETR`-family — **Apache-2.0** | **Apache-2.0** | most permissive modern detector option here |
| roboflow/trackers | **Apache-2.0** | n/a | ByteTrack/BoT-SORT/OC-SORT reimplementations |
| supervision | **MIT** | n/a | |
| TrackEval | `JonathonLuiten/TrackEval` — **MIT** | n/a | |

### Benchmarks & datasets (code vs data — often different!)

| Benchmark | Code license | **Data license** |
|---|---|---|
| SportsMOT | repo: no license file | **CC BY 4.0** (per official mirror terms; GitHub page adds citation/challenge conditions) |
| TeamTrack | **MIT** | research use via site (verify current terms at download) |
| SoccerNet (all tasks incl. ReID/GSR) | MIT | **research-only, non-commercial**; underlying broadcast footage remains copyright holder's |
| DanceTrack | devkit MIT | **CC BY-NC 4.0** (annotations); video stills from creators |
| MOT17 / MOTChallenge | MIT-ish devkits | **CC BY-NC-SA 3.0** — explicitly non-commercial |
| NBA SportVU dumps | n/a | NBA terms: personal/research only; official tracking endpoints discontinued |
| Roboflow Universe basketball sets | n/a | per-dataset, often CC BY 4.0 but **verify each** |

Full dataset descriptions: `07-datasets.md`.

## Patents & the wider IP picture

- **Academic MOT/ReID/JNR methods:** no known patent filings on the published
  algorithms themselves (SORT-family association, trajectory-projection
  matching in Basketball-SORT, jersey-number detection+classification). In the
  US, algorithms "as abstract ideas" are not patentable (*Alice*); in the EU,
  "computer programs as such" are excluded. Publishing a paper also creates
  prior art that blocks others from patenting the same idea — academic methods
  are effectively a patent-free commons for us.
- **The patented zone is deployed sports-tracking systems.** Relevant holders
  (illustrative, not exhaustive):
  - **STATS / SportVU** — optical raft-camera player tracking in NBA arenas
    since 2010–13; STATS marketed "AutoSTATS" (2019) as "the first **patented**
    AI-powered technology to capture sports tracking data via broadcast video"
    — i.e. patent claims exist over *broadcast-derived* tracking pipelines, our
    exact setting, at least in the US.
  - **Second Spectrum** (acquired by **Genius Sports**, 2023) — large NBA/FIFA
    tracking IP portfolio (see Genius SEC filings); NBA rights run through 2026+.
  - **Hawk-Eye (Sony)** — multi-camera trajectory tracking, tennis/football;
    foundational sports-vision patent family.
  - **PlaySight** — multi-camera "smart court" patents for tennis/padel-style
    facility tracking.
  - **NVIDIA, Sportec Solutions, Tracab/Bridge AI** — additional tracking-
    system portfolios mainly in football.
- **Practical read-across:** these patents cover *systems* (multi-camera rigs,
  calibration + fusion + league delivery), not the open-source building blocks.
  A research prototype on one broadcast clip using MIT/Apache components
  infringes nothing patent-wise that we can find; **productizing broadcast
  footage of professional games collides with league media rights long before
  it collides with anyone's patents.**
- **Copyright traps bigger than patents here:** (1) game footage rights;
  (2) non-commercial dataset terms (MOT17 CC BY-NC-SA, SoccerNet research-only);
  (3) AGPL code (Ultralytics, Track-Anything wrapper); (4) unlicensed repos
  (SportsMOT baseline code, jersey-number-pipeline) are all-rights-reserved.

## Implications for this project's build order

| Stage | Safe combination for a **commercial** path |
|---|---|
| v0 spike (research) | YOLO11 + ByteTrack + supervision on SportsMOT/TeamTrack — fine for non-commercial experimentation |
| Commercial pivot | RF-DETR (Apache) detector + OC-SORT/BoT-SORT (MIT) association + supervision (MIT) + self-collected amateur footage (rights cleared) + PaddleOCR (Apache) numbers |
| Avoid in product | Ultralytics AGPL weights, Segment-and-Track-Anything (AGPL), StrongSORT (GPL) unless you accept copyleft; anything trained on MOT17/SoccerNet data for commercial use |
