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

**Status markers** (rows without a marker were directly verified this
session, typically via the GitHub API):
❓ = license **not found / not confirmed** — entry listed anyway; resolve
before any product decision · 🏢 = proprietary, no public license ·
⚠️ = owner-stated policy rather than a standard license file ·
⛔ = **no license file** ⇒ all rights reserved by default.

**Weights column = "are open weights available?"** (re-checked against repos /
model hubs, Oct 2026):
✅ open weights under a permissive license · ⚠️ checkpoints downloadable but
research-only terms or no weight license (weight files rarely carry their own
license — treat unlicensed weights as all-rights-reserved) · ❌ no public
checkpoints found · `—` = method ships no learned weights of its own
(detector/classical — whose weights apply is noted in the cell).

## Master table

### Trackers (association / tracking-by-detection)

| Method | Code (license) | Weights | Notes |
|---|---|---|---|
| SORT | no official code release | — | reimplementations are many and mixed-license |
| DeepSORT | no official code release | — | canonical impls: py-mot / third-party (MIT-ish) |
| **ByteTrack** | `FoundationVision/ByteTrack` — **MIT** | — none of its own (detector's license applies) | repo moved from `ifzhang/ByteTrack` |
| **OC-SORT** | `noahcao/OC_SORT` — **MIT** | — none (motion-only) | |
| **BoT-SORT** | `NirAharon/BoT-SORT` — **MIT** | — none needed; ships BoT-ReID/CABNet appearance ckpts ⚠️ research | |
| StrongSORT | `dyhBUPT/StrongSORT` — **GPL-3.0** | ⚠️ TorchReID checkpoints provided | GPL viral → affects anything you link into |
| Tracktor | no official code | — third-party detector weights | third-party only |
| FairMOT | `ifzhang/FairMOT` — **MIT** | ⚠️ official checkpoints provided — weight files unlicensed | |
| CenterTrack | `xingyizhou/CenterTrack` — **MIT** | ⚠️ official checkpoints provided — weight files unlicensed | |
| MOTR | `megvii-research/MOTR` — **custom/non-standard** (`NOASSERTION`) | ⚠️ official checkpoints via README model links | read LICENSE before use |
| TransTrack | `PeizeSun/TransTrack` — **MIT** | ⚠️ checkpoints provided (original + H-TransTrack repro) | |
| TrackFormer | `timmeinhardt/trackformer` — **Apache-2.0** | ⚠️ trained checkpoints linked from repo docs | |
| QD-TRACK | no public official code found ❓ | ❌ none located | results reproduced via SportsMOT baselines |
| **MixSORT** (ICCV 2023) | baseline code inside `MCG-NJU/SportsMOT` — **no license file** ⛔ | ⚠️ model zoo: trained checkpoints published (Drive/Baidu) | top SportsMOT baseline; same all-rights-reserved caveat as the benchmark repo |
| MOTRv2 (CVPR 2023) | ❓ code availability not confirmed this session | ❓ no checkpoints located | listed for completeness of the transformer-tracking line |
| SAM | `facebookresearch/segment-anything` — **Apache-2.0** | **Apache-2.0** (re-released; originally NC) | |
| SAM 2 | `facebookresearch/sam2` — **Apache-2.0** | **Apache-2.0** | |
| Segment-and-Track-Anything | `z-x-yang/Segment-and-Track-Anything` — **AGPL-3.0** | SAM weights Apache | AGPL wrapper — keep it out of products |

### Re-identification & appearance models

| Method | Code (license) | Weights | Notes |
|---|---|---|---|
| OSNet / deep-person-reid | `KaiyangZhou/deep-person-reid` — **MIT** | ⚠️ trained checkpoints provided — pedestrian-trained on Market-1501 (research-only data) | |
| FastReID | `JDAI-CV/fast-reid` — **Apache-2.0** | ⚠️ model-zoo checkpoints — trained on research datasets | same data caveat |
| CLIP-ReID | `Syliz517/CLIP-ReID` — **MIT** | ⚠️ checkpoints provided in repo | built on OpenCLIP (BSD-family) |
| SoccerNet-ReID models | `SoccerNet/sn-reid` — **MIT** (code) | ⚠️ trained baselines available — trained on SoccerNet data → inherits its research-only terms | |
| SportsMOT baselines | `MCG-NJU/SportsMOT` — **no license file** | ⚠️ MixSort model zoo publishes trained ckpts (research data) | default copyright: all rights reserved — ask before shipping |

### Jersey-number recognition / identification

| Method | Code (license) | Weights | Notes |
|---|---|---|---|
| Koshkina & Elder JNR framework | `mkoshkina/jersey-number-pipeline` — **no LICENSE file** | ❌ weights not released | all-rights-reserved by default; paper is freely readable, code is not licensed |
| CRNN / PaddleOCR (typical number readers) | e.g. PaddlePaddle/PaddleOCR — **Apache-2.0** | ✅ Apache-2.0 weights | PaddleOCR is the most permissive practical OCR stack |

### Detectors & tooling (the licenses that actually bite)

| Component | Code (license) | Weights | Notes |
|---|---|---|---|
| **Ultralytics YOLOv8/YOLO11** | `ultralytics/ultralytics` — **AGPL-3.0** | **AGPL-3.0** | commercial products need an Ultralytics Enterprise license; the usual first legal surprise |
| RF-DETR (Roboflow) | `roboflow/RFDETR`-family — **Apache-2.0** | **Apache-2.0** | most permissive modern detector option here |
| RT-DETR (official `lyuwenyu/RT-DETR`) | **Apache-2.0** | ✅ official pretrained weights (Objects365 model zoo); ⚠️ the same models via Ultralytics are AGPL-1.0 | mind which distribution you pull |
| YOLOX / PP-YOLOE (sports-baseline detectors) | **Apache-2.0** | ✅ model-zoo weights published | permissive YOLO-family alternative |
| roboflow/trackers | **Apache-2.0** | n/a | ByteTrack/BoT-SORT/OC-SORT reimplementations |
| supervision | **MIT** | n/a | |
| TrackEval | `JonathonLuiten/TrackEval` — **MIT** | n/a | |

### Basketball-specific methods, pipelines & community code

Everything in the reading list the tables above didn't cover — listed here
precisely *because* the license situation is thin. Several entries have **no
findable code or license at all**; that is a design input (don't plan on
depending on them), not a reason to omit them.

| Entry | What | Code availability | Code license | Open weights? | Notes |
|---|---|---|---|---|---|
| **Basketball-SORT** (arXiv:2406.19655) | basketball-tuned SORT variant | ❌ no repo located | ❓ | ❌ none | treat as paper-only until authors release |
| **GameSense** (Nature, 2025) | full basketball perception system | ❌ no public code located | ❓ | ❌ none | Nature publication ≠ open code; check the supplement |
| **PlayerTV** (arXiv:2407.16076) | player localization/tracking in TV broadcasts (soccer) | ✅ `simula/PlayerTV` | **MIT** | ❌ pipeline code only, no pretrained weights | re-check before building on it |
| **E-BARD** (VLMs for basketball) | detection + action models | ✅ `GabrieleGiudic/BARD` | CC-BY 4.0 (project) | ✅ detection models on HF `GabrieleGiudici/E-BARD-detection-models` — check model-card terms | soccer/basketball VLM line; weights open, data terms govern |
| **JT-MOT** (arXiv:2504.12731) | joint tracking-identification | ❌ not found | ❓ | ❌ none | adjacent research only |
| **SoccerNet GSR** (task + baselines) | game-state reconstruction | `SoccerNet/sn-*` repos | ⚠️ custom per-repo terms | ⚠️ baseline ckpts via sn-gsr — research-only data | soccer data, transferable task design |
| **Roboflow basketball pipeline** (blog + notebooks) | detect→track→team recipe | Roboflow example repos | ⚠️ usually Apache-2.0 per repo — confirm per notebook | ⚠️ no own weights — depends on Ultralytics (AGPL) or RF-hosted weights | depends on Ultralytics weights ⇒ AGPL in practice |
| **TrackNet / V2 / V3** (arXiv:1907.03698 →) | tiny-ball tracking CNNs (racquet sports) | ❓ official vs many reimplementations | ❓ varies per release | ⚠️ official: no weights; community TrackNetV3 ckpts published (e.g. `qaz812345/TrackNetV3`, MIT) | adapt the *recipe*; vet each implementation's terms |
| **Pose-based player detection** (arXiv:1906.02042 & follow-ups) | keypoints as detection/ID signal | varies per paper ❓ | ❓ | ❌ paper weights not located | skeleton toolkits themselves (MMPose etc.) usually Apache-2.0 |
| **CVBallTracking** (`brettfazio`) | classic HSV/blob ball tracker | public repo | ⛔ **no license file** | — classical CV, no learned weights | algorithm idea fine; code not reusable |
| **StrikerAI** (`KavinSivaharan`) | YOLO ball/player tracking | public repo | ⛔ **no license file** | ⚠️ uses stock Ultralytics weights (AGPL) | reference only |
| `cs25m116/Basketball-Player-Tracking` | student tracking project | public repo | ⛔ **no license file** | ⚠️ stock pretrained weights (YOLO/DINOv2-class) | reference only |
| `Manishmaurya89/...` (ball tracking) | community tracker | public repo | ⛔ **no license file** | — none of its own | reference only |
| **TrackBox / TRACAB-class rigs** | broadcast-rig optical tracking | closed 🏢 | 🏢 | 🏢 no weights ever published | see systems table |

### Identity embeddings, pose & court models (support stack)

| Component | Code (license) | Weights | Notes |
|---|---|---|---|
| DINOv2 (features, cs25m116-style projects) | CC-BY-NC 4.0 | ⚠️ weights CC-BY-NC 4.0 — **non-commercial** | |
| CLIP | MIT | ✅ weights published | web-scale training data (unresolved in courts) |
| SigLIP / SigLIP2 (§03 identity stage) | Apache-2.0 | ✅ Apache weights (HF) | web-scale (unresolved) |
| OpenCLIP | MIT (code) | ⚠️ checkpoints carry no explicit weight license | LAION (research) |
| RTMP / MMPose model zoo | Apache-2.0 | ✅ Apache model-zoo weights | trained on COCO/CrowdPose (research data) |
| HMR (mesh, Roboflow recipes) | research | ⚠️ research-only weights | SMPL model has its own research license |
| Court-line / rim landmark detectors (roboflow/sports, sportsapi) | MIT | ✅ hosted weights free (Roboflow cloud) | |

Adjacent trackers from `02-solution-landscape.md` without rows above:
Deep-OC-SORT (research code, ❌ no weights), TrackTrack & FastTrack
(basketball-adapted research code, ❌ no weights located), SAMTrack /
Track-Anything (MIT wrapper; consumes SAM/SAM2 Apache weights, ❌ own
trained weights not located).

### Benchmarks & datasets (code vs data — often different!)

| Benchmark | Code license | **Data license** |
|---|---|---|
| SportsMOT | repo: no license file | **CC BY 4.0** (per official mirror terms; GitHub page adds citation/challenge conditions) |
| TeamTrack | **MIT** | ⛔ **not stated on the repo/site found so far** — ask authors before any product use |
| SoccerNet (all tasks incl. ReID/GSR) | MIT | **research-only, non-commercial**; underlying broadcast footage remains copyright holder's |
| DanceTrack | devkit MIT | **CC BY-NC 4.0** (annotations); video stills from creators |
| MOT17 / MOTChallenge | MIT-ish devkits | **CC BY-NC-SA 3.0** — explicitly non-commercial |
| NBA SportVU dumps | n/a | NBA terms: personal/research only; official tracking endpoints discontinued |
| Roboflow Universe basketball sets | n/a | per-dataset, often CC BY 4.0 but **verify each** |
| CrowdHuman | research/non-commercial (owner-stated) ⚠️ | same 🔴 |
| Market-1501 / CUHK-SYSU / PRW | ❓ **no formal license** — research community convention only | ❓ same; pretrained ReID weights inherit the ambiguity |
| TrackNet-family racquet datasets | ❓ mixed/unstated per release | ❓ |
| Basketball-51 (action dataset, seed repo) | ❓ unstated | ❓ treat research-only |

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
