# Literature Review & Reading List
## Player Detection, Tracking and Identification in (Basketball) Video

A curated, ordered reading list covering **single-algorithm methods** (a tracker,
a ReID model, a number reader) and **multi-step / full-pipeline approaches**
(end-to-end systems). It consolidates the findings documented in this repo
(`01`–`04`) and adds further foundational and adjacent work. All links checked
Oct 2025.

**Reading tiers:** ⭐ = core (start here), ◆ = supporting/deep-dive, ▸ = adjacent.
**Method tags:** `[single]` one algorithm/model · `[pipeline]` multi-step system
· `[bench]` dataset/benchmark/metric.

---

## Part 0 — Orientation (read first, ~1 day)

⭐ **Computer Vision in Sports** — O'Shea & Keegan, 2017 ◆
The classic field survey; older (pre-deep-MOT) but frames the whole problem
space (events, tactics, tracking).
arXiv: https://arxiv.org/abs/1705.09525

⭐ **A Comprehensive Review of Computer Vision in Sports: Open Issues, Futures** — 2022
Modern survey covering player detection/classification, tracking of players and
ball, trajectory prediction, with dataset/metric tables. Best single overview of our exact subproblems.
arXiv: https://arxiv.org/pdf/2203.02281

⭐ **Player tracking (NBA) — Wikipedia** — industry context
Concise history of league-grade optical tracking (SportVU → Second Spectrum →
Genius Sports 14-camera), the quality bar any academic method is measured against.
https://en.wikipedia.org/wiki/Player_tracking_(NBA)

---

## Part 1 — The tracker lineage: single-algorithm MOT methods

Read in order; each is short and builds on the previous. All are
`[single]` — drop-in association/track-management algorithms behind a detector.

⭐ **SORT: Simple Online and Realtime Tracking** — Bewley et al., ACM ICIP 2016
Kalman filter + Hungarian assignment on IoU. The template every SORT-family
tracker still uses; IDs die quickly under occlusion.
arXiv: https://arxiv.org/abs/1602.00763

⭐ **Simple Online and Realtime Tracking with a Deep Association Metric
(DeepSORT)** — Wojke, Bewley, Paulus, ICIP 2017
Adds an appearance embedding + ReID to SORT. The canonical baseline; weak when
teammates wear identical kits (our problem).
arXiv: https://arxiv.org/abs/1703.07402

⭐ **ByteTrack: Multi-Object Tracking by Associating Every Detection Box** —
Zhang et al., ECCV 2022
Two-stage association that keeps *low-score* detections (they mark occluded
objects) instead of discarding them. Detection-centric, very fast (~30 FPS),
strong sports performer. Default v0 tracker here.
arXiv: https://arxiv.org/abs/2110.06864 · code: https://github.com/ifzhang/ByteTrack (also built into Ultralytics)

⭐ **OC-SORT: Observation-Centric SORT** — Cao et al., CVPR 2023
Re-kinematizes tracks from observations instead of trusting the Kalman
prediction; handles abrupt stops/direction changes — exactly athlete motion.
Best static-camera default in sports (MixSort-OC: 74.1 HOTA on SportsMOT).
arXiv: https://arxiv.org/abs/2203.14360 · code: https://github.com/noahcao/OC_SORT

◆ **BoT-SORT: Robust Associations Multi-Pedestrian Tracking** — Han et al., 2022
SORT + ReID + camera-motion (global motion) compensation + causal tracing.
The default when the camera moves (broadcast feeds).
arXiv: https://arxiv.org/abs/2206.14651

◆ **StrongSORT / StrongSORT++: Make DeepSORT Great Again** — Shi et al., 2022/2023
Systematic DeepSORT upgrade (modern detector, ReID, IoU+EM association, camera
motion). High accuracy, heavier; good for offline game analysis.
arXiv: https://arxiv.org/abs/2202.13514

◆ **Tracking Objects via Untrained Learner (Tracktor)** — Bergmann et al., 2019
No detector at all at run time — tracks by bounding-box IoU + appearance via
self-supervised box propagation. Interesting single-algorithm outlier; fragile
for team sports.
arXiv: https://arxiv.org/abs/1905.07180

◆ **Recent Advances in Embedding Methods for Multi-Object Tracking** — 2022
Survey of the appearance-embedding branch of MOT (JDE vs ReID-only, losses).
Background reading for choosing identity models.
arXiv: https://arxiv.org/abs/2205.10766

---

## Part 2 — One-network approaches: joint detection + tracking

`[single]` in the strongest sense: one network does detection, embedding, and
association. Research-grade accuracy claims, rarely the pragmatic pick.

◆ **FairMOT: On the Fairness of Detection and Re-Identification in MOT** — Wang et al., 2020
Single CenterNet-style encoder-decoder producing detections *and* per-instance
ReID embeddings; the canonical joint-detect-embed method when appearance matters.
arXiv: https://arxiv.org/abs/2004.01888

◆ **CenterTrack: Tracking as Keypoint Offset Estimation** — Zhou et al., CVPR 2019
Detects objects as keypoints and tracks via offset to previous frame's keypoint.
Foundational idea behind many later end-to-end trackers.
arXiv: https://arxiv.org/abs/1908.06265

◆ **MOTR: End-to-End Multiple-Object Tracking with Transformer** — Zeng et al., ECCV 2021
Tracking queries inside a DETR; tracks through occlusion via query propagation.
◆ **TransTrack** — Sun et al., ECCV 2021 — arXiv: https://arxiv.org/abs/2012.15460
◆ **TrackFormer** — Meinhardt et al., CVPR 2021 — arXiv: https://arxiv.org/abs/2101.02702
◆ **QD-TRACK: Quasi-Dense Similarity Learning** — Pang et al., CVPR 2021 — arXiv: https://arxiv.org/abs/2103.16882

◆ **Track Anything / Segment Anything (SAM)** — Kirillov et al., 2023 (+ SAM2 2024)
SAM masks + per-track propagation (Track-Anything, SAMTrack): ideal for
*given-player* top-down tracking and **fast annotation**, not dense crowds.
SAM: https://arxiv.org/abs/2304.02643 · Segment-and-Track-Anything: https://github.com/z-x-yang/Segment-and-Track-Anything (see also supervision/SAM2 examples)

---

## Part 3 — Benchmarks & evaluation (know before building)

⭐ **HOTA: A Higher Order Metric for Evaluating Multi-Object Tracking** —
Luiten et al., IJCV 2021
The metric that separates detection quality (DetA) from association quality
(AssA/IDF1). Basketball fails on association, so MOTA alone is misleading.
arXiv: https://arxiv.org/abs/2009.07736 · toolkit: https://github.com/JonathonLuiten/TrackEval

⭐ **SportsMOT: A Large Multi-Object Tracking Dataset in Multiple Sports Scenes** —
Cui et al., ICCV 2023
240 clips (~150k annotated frames) across basketball, soccer, volleyball. Key
empirical findings: basketball is the **hardest** sport to track (3+ way
contact occlusions); DetA is high but IDF1/AssA lag — association, not
detection, is the bottleneck. Baselines: Deep-EIoU, QD-DET, MixSort.
arXiv: https://arxiv.org/abs/2304.05170 · code: https://github.com/MCG-NJU/SportsMOT

⭐ **TeamTrack: A Dataset for Multi-Sport Multi-Object Tracking in Full-pitch Videos** —
Scott et al., 2024
Full-pitch (no broadcast cuts) basketball/soccer/handball MOT — the closest
public benchmark to a plain "game recording".
arXiv: https://arxiv.org/abs/2404.13868 · site: https://atomscott.github.io/TeamTrack/

◆ **SoccerNet-Tracking: Multiple Object Tracking Dataset and Benchmark in Soccer Videos** —
Somers et al., CVPR 2022
Adjacent sport, but the most mature sports-MOT benchmark + dev kit; designs
transfer directly.
arXiv: https://arxiv.org/abs/2204.06918 · code: https://github.com/SoccerNet/sn-tracking

◆ **DanceTrack: Multi-Object Tracking in Uniform Appearance and Diverse Motion** —
Jiang et al., CVPR 2022
People in similar outfits with large motion — the same-appearance stress test
team sports need; useful pretraining/eval proxy when basketball data is thin.
arXiv: https://arxiv.org/abs/2111.14690 · site: https://dancetrack.github.io/

---

## Part 4 — Basketball-specific methods (the heart of this list)

⭐ **Basketball-SORT: An Association Method for Complex Multi-object Occlusion
Problems in Basketball MOT** — Hu et al., 2024 `[single]`
Defines **CMOO** (Complex Multi-Object Occlusion: ≥3 similarly-dressed players
in contact). Replaces IoU association with trajectory-projected-position
matching + basketball game restriction (BGR) + reacquiring long-lost IDs
(RLLI). HOTA 63.48% on fixed-camera basketball, beating ByteTrack/DeepSORT/
OC-SORT on that data. The single most relevant paper in this list.
arXiv: https://arxiv.org/abs/2406.19655

◆ **Single-Camera Basketball Tracker through Pose and Semantic Features** — 2019 `[pipeline]`
Pose-based tracking with semantic (jersey) features from one broadcast camera;
early example of appearance-free (skeleton) identity cues for basketball.
arXiv: https://arxiv.org/abs/1906.02042

◆ **GameSense: Hierarchical Spatio-Temporal Transformer for Basketball Player Identity Tracking** — 2025 `[single]`
Memory-driven Transformer decoder with hierarchical short/long-term memory for
identity continuity in fast basketball play. Newest identity-tracking work.
https://www.nature.com/articles/s41598-025-29586-y

◆ **Learning to Track and Identify Players from Broadcast Sports Videos** —
Zhao & Zemel (UBC), ICPR 2014 `[pipeline]`
Classic pre-deep-MOT broadcast approach (appearance + motion learning for
identification; lineage feeding Zemel's NBA Raptor work).
PDF: https://open.library.ubc.ca/media/download/pdf/24/1.0052129/2

◆ **Robust Camera Calibration and Player Tracking in Broadcast Basketball Video** /
**Court Reconstruction for Camera Calibration in Broadcast Basketball Videos** — NTU `[pipeline]`
Quadrangle-candidate homography calibration for moving broadcast cameras;
maps CamShift tracks to real court coordinates. The court-geometry reference pair.
https://www.researchgate.net/publication/224206313 · https://www.researchgate.net/publication/279160655

◆ **Real-time MOT for sports scenarios: a lightweight approach** — 2026, Nature Sci. Rep.
Uses SportsMOT as primary corpus; documents supplementing it for indoor
basketball camera angles — useful deployment notes.
https://www.nature.com/articles/s41598-026-58180-z

---

## Part 5 — Distinguishing players: ReID, team assignment, jersey numbers

### 5a. Re-identification `[single]`

⭐ **OSNet: Orthogonal Convolution Network for Person Re-ID** — Zhou et al., ICCV 2019
Standard lightweight ReID backbone (also BoT-SORT's embedding choice lineage).
arXiv: https://arxiv.org/abs/1905.00953 · ◆ **CLIP-ReID** (LLM-style supervision for ReID): https://arxiv.org/abs/2310.00431 · toolbox: https://github.com/JDAI-CV/fast-reid (FastReID)

◆ **Reidentifying soccer players in broadcast videos using body feature
embeddings** — ACM 2023
Shows faces only work in close-ups; overview shots need body-feature embeddings.
Directly transferable finding (same-team kits break generic pedestrian ReID).
https://dl.acm.org/doi/fullHtml/10.1145/3603781.3603860

◆ **SoccerNet ReID / multi-task ReID + team affiliation + role** — Somers et al.
SoccerNet-ReID: 340,993 player crops, 400 games, 6 leagues; joint multi-task
model is SOTA for team-aware ReID.
code: https://github.com/SoccerNet/sn-reid

### 5b. Team assignment `[single]`

⭐ **PlayerTV: Advanced Player Tracking and Identification for Automatic
Commentary Generation** — 2024 `[pipeline]`
Closest published analog to our end goal: detection → ByteTrack-style tracking
→ per-track dominant jersey color, normalized, k-means k=2, cluster-center
mapped to team colors from a player DB. Reported ~92%+ team accuracy territory.
arXiv: https://arxiv.org/abs/2407.16076

◆ **Team Affiliation, Jersey Number Recognition and Player Tracking** (thesis, York)
Unsupervised team assignment study: per-channel color normalization + k-means
baseline vs learned feature clustering.
PDF: https://yorkspace.library.yorku.ca/server/api/core/bitstreams/81af2a04-35c0-4066-9d89-3fba16857e6c/content

◆ **Automatic Team Assignment and Jersey Number Recognition** — IASC 2023
Reported 92% team-assignment accuracy beating raw cluster-center + jersey-color
heuristics; documents where color clustering fails (dark vs dark kits).
https://www.techscience.com/iasc/v36n3/51888/html

### 5c. Jersey-number recognition & player identification `[single]`

⭐ **A General Framework for Jersey Number Recognition in Sports Video** —
Koshkina & Elder, CVPRW 2024
ReID-net features to filter distractor crops, then number classifier; general
across sports. Best public starting point; open code.
arXiv: https://arxiv.org/abs/2405.13896 · code: https://github.com/mkoshkina/jersey-number-pipeline

◆ **Automated player identification and indexing using two-stage deep
networks** — Nature Sci. Rep. 2023
Two-stage detection→OCR design for jersey numbers.
https://www.nature.com/articles/s41598-023-36657-5

◆ **Basketball Player Identification by Jersey and Number Recognition** —
Ephrati & Moghadam (Stanford) `[pipeline]`
Early end-to-end CNN jersey+number identification, basketball-specific.
PDF: https://stacks.stanford.edu/file/druid:yj296hj2790/Ephrati_Moghadam_Basketball_players_recognition.pdf

---

## Part 6 — Full multi-step systems (detect → track → identify → court)

⭐ **How to Detect, Track, and Identify Basketball Players** — Roboflow, 2025 `[pipeline]`
The most direct end-to-end open recipe for our task: RF-DETR fine-tunes for
players / jersey numbers / referees / ball + tracking + SigLIP/CLIP-style
identity matching; notebook + blog.
https://roboflow.com/blog/identify-basketball-players (notebook: roboflow-ai/notebooks, `basketball-ai-how-to-detect-track-and-identify-basketball-players.ipynb`)

◆ **SoccerNet Game State Reconstruction (GSR): End-to-End Athlete Tracking and
Identification** — Somers et al., CVPRW 2024 `[pipeline]`
End-to-end monocular pipeline: tracking + ReID + team affiliation + role +
calibration with the GS-HOTA metric (field-distance-aware association).
Basketball-adjacent but the blueprint for game-level identity.
PDF: https://openaccess.thecvf.com/content/CVPR2024W/CVsports/papers/Somers_SoccerNet_Game_State_Reconstruction_End-to-End_Athlete_Tracking_and_Identification_on_CVPRW_2024_paper.pdf

◆ **Creating More Engaging Sports Broadcasts with AI** — NVIDIA dev blog `[pipeline]`
Practical broadcast pipeline: segmentation → camera-pose init → homography
refinement; production-perspective engineering notes.
https://developer.nvidia.com/blog/creating-more-engaging-sports-broadcasts-with-ai/

◆ **Roboflow Trackers / supervision** — Apache-2.0 implementations of ByteTrack,
BoT-SORT, OC-SORT etc. with clean APIs; fastest path from idea to running v0.
https://github.com/roboflow/trackers · https://supervision.roboflow.com/
(overview: https://learnopencv.com/multi-object-tracking-with-roboflow-trackers-and-opencv/)

◆ **Open Source Sports Video Analysis using Machine Learning** — DEV.to post `[pipeline]`
Early open attempt: court-line detection → person detection → jersey-color team
split → tracking → homography to 2D court. Documents what breaks in practice.
https://dev.to/stephan007/open-source-sports-video-analysis-using-maching-learning-2ag4

◆ Community repos (read, don't depend):
`brettfazio/CVBallTracking`,
`Manishmaurya89/Basketball-Analytics-Estimation-Using-Object-Segmentation-`,
`cs25m116/Basketball-Player-Detection-Tracking-Identification` (DINOv2 + SAM2 + jersey numbers),
`KavinSivaharan/StrikerAI` (soccer analog: YOLO + KMeans teams + homography minimap).

---

## Part 7 — Industry systems & products (quality bar, not code)

◆ **SportVU / Second Spectrum / Genius Sports (NBA optical tracking)** —
6 raft-mounted cameras @25 Hz (SportVU, 2013) → Second Spectrum ML/CV stack
(2016–2023) → Genius 14-camera rig (2025). Proof that fixed multi-camera rigs
give league-grade trajectories; defines downstream product expectations
(possession, spacing, Raptor).
https://www.theglobeandmail.com/sports/how-sportvu-works/article18540599/ ·
https://grantland.com/features/the-toronto-raptors-sportvu-cameras-nba-analytical-revolution/ ·
https://pr.nba.com/nba-g-league-second-spectrum/

◆ **Proof of Concept for a Deep-Learning CV System for Athlete Tracking** (indoor)
Academic validation of a commercial-style single-camera gym system; documents
LPS (wearable) alternatives and their infrastructure cost.
https://www.mdpi.com/1999-4893/19/6/464

◆ **TrackBox — the vision layer for sports video** — commercial API whose task
list (detection, MOT, ReID, JNR, team assignment, calibration, ball) matches
our roadmap feature-for-feature. https://www.trackbox.be/

◆ **Hudl / Veo / Pixellot / PlaySight** — capture + semi-auto stat platforms;
UX benchmark rather than CV references. https://www.hudl.com/

---

## Part 8 — Adjacent but useful

▸ **TrackNet: A Deep Learning Network for Tracking High-speed and Tiny Objects
in Sports** — 2019 `[single]`
The standard ball-tracking approach (spatiotemporal CNN over frame stacks);
basketball ball tracking is the hardest instance of this.
arXiv: https://arxiv.org/abs/1907.03698

▸ **Camera Calibration in Sports with Keypoints** — Roboflow blog (YOLOv8
keypoint court-line detector + homography walkthrough, soccer).
https://roboflow.com/blog/camera-calibration-sports-computer-vision

▸ **Action recognition downstream context** (from the `jjdredd/ai-research`
repo; see `01-repo-review.md`): Cui, *3D-CNN-based Action Recognition for
Basketball Players*, Informatica 48 (2024) — SSD detect → crop → dual-resolution
3D-CNN (94.6% fused); *Basketball-51* activity dataset; *ACA-Net*; *EITNet*
(edge deployment). These consume our tracking output, not our problem itself.

▸ **Biomechanical Validation of Skeletal Tracking Data (NBA)** — MIT thesis 2025 —
how league transitions are validated; good cautionary engineering read.
https://dspace.mit.edu/bitstream/handle/1721.1/162729/hong-sshong-meng-eecs-2025-thesis.pdf

---

## Suggested 10-paper core path (in order)

1. Comprehensive review of CV in sports (§Part 0) — field map
2. SORT (P1) → 3. ByteTrack (P1) → 4. OC-SORT (P1) — association basics
5. HOTA/TrackEval (P3) — how to measure
6. SportsMOT (P3) — why basketball is hard, what numbers to expect
7. Basketball-SORT (P4) — the domain-specific answer
8. TeamTrack (P3) — full-pitch data setting
9. PlayerTV (P5b) — team + identity pipeline end-to-end
10. Koshkina & Elder (P5c) — naming players via jersey numbers

Then branch: §Part 2 for one-network alternatives, §Part 6 for system design,
§Part 7 for the quality bar.

## Cross-references in this repo

- `06-licenses-and-patents.md` — code/weights/data licenses & patent landscape for every entry here
- `07-datasets.md` — dataset-by-dataset catalog with license terms
- `02-solution-landscape.md` — tabloid version of this list with commentary
- `03-recommended-architecture.md` — pipeline these references inform
- `04-v0-prototype.md` — the experiment that tests them
- `01-repo-review.md` — action-recognition papers from the seed repository
