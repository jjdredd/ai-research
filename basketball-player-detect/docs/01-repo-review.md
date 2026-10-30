# Review of the `jjdredd/ai-research` Repository

Repo: https://github.com/jjdredd/ai-research (its raw materials live directly
in the parent directory, `../`). Contents: two org-structured link lists
(`basketball.materials.org`, `other.org`), one PDF
(`6100-18042.pdf`), and experiment notes (`mmaction2-basketball51-results.md`).

## Headline finding

**The repo is centered on basketball *action recognition* (what play/move is
happening), not on *detection/tracking/identification of players* (our task).**
It is still valuable: it seeds the surrounding ecosystem (YOLO detectors, 3D-CNN
and Transformer recognizers, MMAction2 tooling, datasets), and several items are
directly reusable building blocks or useful context.

## Item-by-item review

### `basketball.materials.org` — curated paper list

| Item | Relevance to detect/track/identify |
|---|---|
| *Basketball Video Analysis Based on YOLO and Transformer Framework* (ACM 2025) | Medium — YOLO detection frontend + Transformer backend; confirms the detect→analyze pipeline shape we plan. |
| *ACA-Net: adaptive context-aware network for basketball action recognition* (PMC) | Low/adjacent — action recognition only. |
| *Basketball-51: a video dataset for activity recognition* | Low/adjacent — 51-class activity dataset; good for a downstream action head, not for tracking. |
| *Basketball Detection: From Images to Videos* (cs231n 2024 project) | Low — repo's own note: "simple ball detection, not very interesting". Ball, not players. |
| *AI/NN-based shooting accuracy prediction* (Wiley) | Low (repo note: not interesting). |
| *Basketball technique action recognition using 3D CNNs* (Nature Sci. Reports 2024) | Adjacent — repo notes the article lacks architecture detail; points to two deeper refs (dynamic residual attention CNN; GCN shooting-action recognition). |
| *Real-Time Basketball Shooting Action Recognition* (DiVA thesis) | Medium — worth reading for real-time engineering practice; still action recognition. |
| `informatica.si` article 6100 (see PDF below) | Medium — read in full. |
| *EITNet: IoT-enhanced real-time basketball action recognition* (arXiv 2410.09954) | Adjacent — edge-deployment architecture ideas (real-time constraints, camera/IoT setup) are transferable. |
| JNI 2025 special issue link (`bit.kuas.edu.tw/~jni/2025/vo`) | Untriaged journal issue. |

### `6100-18042.pdf` — Cui, *"3D-CNN-based Action Recognition Algorithm for
Basketball Players"*, Informatica 48 (2024) 97–110 — **read in full**
(full text: `notes/informatica-3dcnn-basketball.txt`)

- **Pipeline:** SSD (single-shot multibox detector) finds players per frame →
  crop sequences of **continuous frames** → dual-resolution **3D-CNN**
  (two 3D convolutional streams fused) classifies the technical action
  (shoot/dribble/pass etc.).
- **Results:** ~**90.3%** average recognition with 3D-CNN alone; **94.6%**
  when fusing the two resolution streams. Argues that using continuous frame
  sequences (vs single frames) is the key accuracy driver.
- **Take-away for us:** the **detection-then-crop-then-temporal-classify**
  structure is exactly the structure of our pipeline too; this paper is about
  the classify stage. Also a caution: this is 2017–2019-era tech (SSD, plain
  3D-CNN) — we'd use YOLO/DETR + TimeSformer/RiR or pose-based recognizers.

### `mmaction2-basketball51-results.md`

Repo author's own evaluation: MMAction2 baseline on **Basketball-51**
validation (24 clips, 8 classes, CPU inference, best checkpoint epoch 41).
Mixed per-video results (made-vs-missed free throws confusable, "misc" class
weakest). Signals: the author has MMAction2 experience; MMAction2/MMTracking
(OpenMMLab) is a reasonable toolbox choice on our side for the recognition
module if we ever add one.

### `other.org`

Foundation-model links: **Segment Anything (SAM)**, **Depth Anything**,
**SpaceJAM** (joint image alignment). Relevant to us as optional components:
SAM/SAM2 for mask-based tracking (Track-Anything style) and Depth Anything for
rough 3D/court geometry; not tracking solutions by themselves.

## What the repo is *missing* relative to our task

No coverage of: multi-object tracking (SORT/ByteTrack/DeepSORT lineage), sports
MOT benchmarks (SportsMOT, TeamTrack, SoccerNet-Tracking), player ReID,
team/jersey assignment, court calibration. Those gaps are filled by
`02-solution-landscape.md`.
