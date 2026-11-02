# Datasets Catalog
## Data for basketball player detection, tracking, team assignment, and identification

Companion to `05-literature-review.md` (methods) and `06-licenses-and-patents.md`
(code/model licensing). Every entry lists what it contains, which sub-problem
it serves, how to get it, and — where the owner states one — its **data
license**. Where no license is stated, that is called out explicitly, because
"no license" legally means *all rights reserved*.

**License legend:** 🟢 permissive (commercial-usable) · 🟡 attribution/conditions ·
🔴 research/non-commercial only · ⛔ no stated license (verify before use) ·
🏢 proprietary (not publicly available) · ❓ existence/availability itself
could not be confirmed — entry kept for completeness, do **not** rely on it
without resolving it first.

---

## A. Sports multi-object tracking benchmarks (the core evaluation data)

### SportsMOT — the basketball benchmark
Cui et al., ICCV 2023. 240 clips (~150k annotated frames) across five sports
incl. **basketball** — the only mainstream MOT benchmark with substantial
broadcast-style basketball footage. Train/test split with hosted evaluation.
Empirically: basketball is its hardest sport (3+ way contact occlusions;
detection is easy, association is not). Serves: detection fine-tuning, tracker
evaluation (HOTA/MOTA via TrackEval), baseline comparisons (MixSORT etc.).
- Access: https://github.com/MCG-NJU/SportsMOT — **official Hugging Face
  mirror: `huggingface.co/datasets/MCG-NJU/SportsMOT`** (verified 2026-11-02:
  `dataset/{train,val,test}.tar` = 6.4/6.3/22.1 GB; `splits_txt/basketball.txt`
  lists 80 basketball sequences, 15 in train + 15 in val carry GT, 35 test-only;
  basketball clips avg ~845 fr @25 fps, ~10 tracks, ~9 boxes/frame)
- **Data license: CC BY-NC 4.0** 🟠 (**corrected 2026-11-02** — the official
  README carries the BY-NC mark and competition terms incl. *no redistribution
  without written permission*; earlier notes here said CC BY 4.0, that was
  wrong). Consequences: fine for our internal eval; raw frames/GT must never be
  committed to this repo or redistributed; NC labels must never leak into any
  future training set (v0.1 trains nothing, so this is a docs-only constraint)
- Code license: **none stated** in the repo ⛔ (use TrackEval — MIT — instead)

### TeamTrack — full-pitch, no cuts
Scott et al., CVPR 2024. High-resolution (4K–8K) **full-pitch** videos of
basketball, soccer and handball games with **over 4M annotated boxes**; drone
and fisheye views; deliberately avoids broadcast cuts so trajectories stay
continuous across a whole game — closest public match to a plain "game
recording". Serves: long-term tracking, ID-retention tests, full-game analytics.
- Access: https://atomscott.github.io/TeamTrack/ · code: https://github.com/AtomScott/TeamTrack
- **Data license: not stated on the repo** ⛔ — the repo is MIT but the video
  data itself carries no explicit terms; contact authors before any product use.
- Code license: MIT 🟢

### SoccerNet (Tracking / ReID / Game-State-Reconstruction)
Somers et al. — the most mature sports-CV ecosystem: 10+ hours of broadcast
soccer with MOT annotations (sn-tracking), a 340k-crop player-ReID benchmark
(sn-ReID, 400 games/6 leagues incl. team-affiliation labels), and the GSR
task (tracking + ReID + role + calibration, GS-HOTA metric). Soccer, not
basketball — but team-assignment/ReID designs transfer almost 1:1, and it is
the only sports dataset with large-scale *identity* labels.
- Access: https://www.soccer-net.org/ · https://github.com/SoccerNet/sn-tracking ·
  https://github.com/SoccerNet/sn-reid
- **Data license: research use only, strictly non-commercial** 🔴 — broadcast
  footage remains copyright of the original holders; you must accept their
  terms (see https://www.soccer-net.org/faq).
- Code licenses: MIT 🟢 / custom per repo

### DanceTrack — same-appearance stress test
Jiang et al., CVPR 2022. 62 clips (100+ dancers per frame), extreme
same-appearance/different-motion — the canonical proxy for "everyone wears the
same kit". No basketball, but the right generalization test for team-sports
trackers when basketball data is thin.
- Access: https://dancetrack.github.io/
- **Data license: annotations CC BY-NC 4.0** 🔴 (per project terms); frames
  from broadcast sources
- Devkit code: MIT 🟢

### MOT17 / MOTChallenge (context only)
The general-purpose pedestrian benchmarks (MOT17: 7 train + 7 test seqs, ~66k
frames). Not sports; people walk, players sprint. Useful only as pretraining
sanity-check and metric infrastructure (its devkits spawned TrackEval).
- Access: https://motchallenge.net/ (site shows "currently offline" banners periodically, Oct 2025)
- **Data license: CC BY-NC-SA 3.0** 🔴 — non-commercial, share-alike

---

## B. Basketball-specific & identification data

### NBA SportVU tracking data (historical league trajectories)
The 2010s NBA optical-tracking streams (players + ball xy at 25 Hz, ~10 full
games per night for several seasons). Official stats endpoints have been
discontinued; cleaned dumps circulate on GitHub (e.g. searches for
"SportVU tracking data"). No images — trajectory data only — so it can't train
detectors, but it is the **only public ground truth of what real player
trajectories look like** (spacing, speed profiles, possession dynamics) for
validating a tracking pipeline's outputs.
- **Data license: NBA media terms — personal/research use only** 🔴; the
  underlying game footage rights were never released with the numbers.

### Roboflow Universe basketball datasets
Dozens of community-annotated sets: "basketball players" detection sets
(thousands of images, fixed cameras and broadcasts), referee/ball classes, and
**jersey-number crops** used in the Roboflow basketball pipeline (`05` §Part 6).
Pragmatic fuel for v0/v1 fine-tuning when SportsMOT's official splits are not
enough. Quality varies per set — inspect before trusting.
- Access: https://universe.roboflow.com/ (search "basketball players",
  "jersey number")
- **Data license: per-dataset** — many are CC BY 4.0 🟡 but some inherit
  broadcast footage with unclear rights; check the license widget on each set.

### Koshkina & Elder jersey-number pipeline data
The CVPRW 2024 JNR framework (`05` §5c) trains on sports video with jersey
number annotations; released code expects that data format. Data itself is
sports-clip based — check the repo README for what is provided vs referenced.
- Access: https://github.com/mkoshkina/jersey-number-pipeline
- **Code: no LICENSE file** ⛔ · data: research context 🔴

### Unverified candidates (kept on record, marked ❓)

Earlier research notes referenced datasets I could not trace through any
channel tried (GitHub search, Hugging Face datasets API, web search, arXiv
API). They are **listed rather than dropped**, with the honest status:

| Candidate | Claimed contents | Status |
|---|---|---|
| **TeamSportAI** | purported sports collective-behaviour dataset (NeurIPS-style D&B track) | ❓ **not found** — name may be misremembered; re-derive the citation before use |
| **JPSD** / "J" jersey-number dataset (Japanese pro soccer?) | purported jersey-number recognition set | ❓ **not found** — the arXiv ID recorded earlier (2203.00779) is a biology paper ⇒ the note was wrong at source |

If these resurface, verify existence *and* license before adding them to any
build plan; until then treat SportsMOT + SoccerNet-ReID + RF Universe as the
complete public option set.

### Basketball-51 & the action-recognition datasets (adjacent)
From the seed repo (`01-repo-review.md`): Basketball-51 (51-action basketball
video clips), used by the Informatica 2024 3D-CNN study and ACA-Net/EITNet
follow-ups. Downstream consumers of our tracking output, not training data for
it — listed for completeness.
- Access: via the org-file links in the parent directory (`../basketball.materials.org`), `../other.org`
- License: mixed ⛔ (dataset terms rarely stated; treat research-only 🔴)

---

## C. Auxiliary pre-training data (not players, but everyone starts here)

Generic person data compensates for thin sports datasets — with the caveat that
pedestrian models must be fine-tuned for kits/occlusion (the `02` landscape doc
covers the domain-gap evidence).

| Dataset | Contents / serves | Access | License |
|---|---|---|---|
| **CrowdHuman** | 15k densely-annotated pedestrian images (full-body + head + visible-box); best pretraining for crowded, heavily occluded player detection | http://www.crowdhuman.org/ | research/non-commercial 🔴 |
| **CUHK-SYSU** | person search (detection + ReID per identity), 80 ids | via `deep-person-reid`/fair repos | no formal license; research convention 🔴⛔ |
| **PRW** | person search in the wild, 93 ids, multimodal | via person-search toolboxes | no formal license; research convention 🔴⛔ |
| **Market-1501** | the classic person-ReID set (1,501 ids, 32k boxes); default pretrain for OSNet/FastReID checkpoints you'll download | via `JDAI-CV/fast-reid`, `KaiyangZhou/deep-person-reid` | no formal license; research convention 🔴⛔ |
| **COCO person** | generic detection pretraining; every YOLO/DETR checkpoint starts here | https://cocodataset.org/ | images CC BY 4.0 / annotations CC BY 4.0 🟡 |

Note: pretrained **weights** shipped in MIT/Apache repos (FastReID,
deep-person-reid, BoT-SORT ReID heads) were trained on these research-only
datasets — the weights inherit the data question even where the code is 🟢
(see `06` master table).

## D. Ball tracking (the tiny-fast-object sibling problem)

### TrackNet / TrackNetV2 / TrackNetV3 dataset family
The racquet-sports ball-tracking line (`05` Part 8): TrackNet's original
table-tennis dataset, TrackNetV2's badminton corpus (~100k+ frames from
broadcast clips; follow-ups publish shuttlecock trajectory datasets), now
extended to tennis/pickleball transfer studies. Not basketball, but the
recipe (stacked-frame CNNs for tiny moving objects) is what anyone tracking a
basketball on broadcast footage ends up adapting; the datasets are open and
can be re-annotated for basketball experiments.
- Access: TrackNet arXiv https://arxiv.org/abs/1907.03698 · TrackNetV2 via
  https://www.semanticscholar.org/paper/TrackNetV2%3A-Efficient-Shuttlecock-Tracking-Network-Sun-Lin/223c287d516284fec9bd9792ca2805aa0f551fc9
  · badminton dataset notes: https://hackmd.io/@TUIK/rJkRW54cU
- License: research use; mixed/unstated per release ⛔🔴

## E. Closed / proprietary systems (not available — calibration targets)

| System | What it produces | Why it matters here |
|---|---|---|
| 🏢 **Hawk-Eye (Sony)** | multi-camera ball/player trajectories (tennis, football) | the reference accuracy bar; patented family (`06`) |
| 🏢 **Second Spectrum / Genius (NBA)** | league-wide player+ball tracking, analytics feeds | the quality bar & patent zone for basketball (`06`) |
| 🏢 **PlaySight SmartCourt** | multi-camera facility tracking (tennis/padel/basketball) | single-venue fixed-rig product pattern |
| 🏢 **TRACAB / Sportec (football)** | broadcast-rig optical tracking | shows what ~10-camera rigs achieve vs single-camera research |

No public data; included so accuracy expectations ("HOTA ≈ ? is good enough")
are anchored to products, not papers.

## Quick comparison

| Dataset | Task(s) | Basketball? | Identity labels? | Size | Data license |
|---|---|---|---|---|---|
| SportsMOT | MOT eval/finetune | ✅ | no | 240 cl / ~150k fr | 🟠 CC BY-NC 4.0 (corrected) |
| TeamTrack | full-game MOT | ✅ | no | 4M+ boxes, 4K–8K | ⛔ unstated |
| SoccerNet Track/ReID/GSR | MOT + ReID + team | ❌ (soccer) | ✅ ✅✅ | 10h+ / 340k crops | 🔴 research-only |
| DanceTrack | same-appearance MOT | ❌ | no | 62 clips | 🔴 CC BY-NC |
| MOT17 | pretrain/metrics | ❌ | no | 14 seqs | 🔴 CC BY-NC-SA 3.0 |
| SportVU dumps | trajectory validation | ✅ | ✅ (jersey ids) | seasons of games | 🔴 NBA terms |
| RF Universe sets | detector finetune, JNR | ✅ | partial | varies | 🟡/⛔ per set |
| CrowdHuman | occlusion pretrain | ❌ | no | 15k imgs | 🔴 research |
| Market-1501 etc. | ReID pretrain | ❌ | ✅ | 32k boxes | 🔴⛔ convention |
| TrackNet family | ball tracking | ❌ (racquet) | no | ~100k+ fr | ⛔ mixed |

## Practical takeaways for this project

1. **v0/v1 fine-tune + eval combo:** SportsMOT (CC BY-NC 4.0 as of the 2026-11
   re-check — eval-only, not redistributable; no longer "cleanest terms") + a vetted RF Universe basketball set for detector
   fine-tuning; evaluate with TrackEval (MIT).
2. **Identity stages can only be validated on SoccerNet-ReID** (research-only)
   → keep identity experiments research-phase, or build your own small labeled
   set on rights-cleared footage (high-school/own games).
3. **⛔ entries need an email before product use** — TeamTrack's data,
   jersey-number-pipeline code, SportsMOT's own baseline code.
4. Broadcast footage you don't own is a rights problem no dataset license
   fixes (see `06` §Patents & the wider IP picture).
