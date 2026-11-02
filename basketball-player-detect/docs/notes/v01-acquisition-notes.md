# v0.1 acquisition & model notes (running log, starts pre-M1)

Dates: 2026-11-02. Author: assistant. Companion to `docs/09-v0.1-prototype-plan.md`.

## RF-DETR (rfdetr 1.11.2, RFDETRLarge + Medium) — resolved gotchas

1. **`predict()` returns a single `supervision.Detections`, not a list.**
   Indexing `[0]` selects one *row* → earlier "model detects only 1 object"
   panic was my bug, not the model's. Never index; use the object directly.
2. Same sasebo frame @ t=17 s where YOLO11m found 14 persons: RF-DETR-Large
   (threshold 0.3) finds **13 person + 2 sports ball + 1 bench + 2 backpack**
   (18 boxes). The bench-box is a useful warning: RF-DETR sees COCO classes
   like `bench` courtside → v0.1 must filter to `person` (and optionally use
   `sports ball` for the ball channel). Extra backpack/bench detections sit
   where crowd/objects are → another argument for the stage-2 inbounds/ROI
   prior in docs/09.
3. Weights are fine: `~/.roboflow/models/rf-detr-large-2026.pth` (136 MB
   looks small but downloads from the package's own pinned GCS URL; MD5
   verified by the loader).
4. Speed: **~4 fps single-frame fp16** at default shape on the RTX 4080
   (`m.inference(dtype=torch.float16)` after load; default load warns
   "not optimized for inference"). No speed gate in v0.1 (docs/09), but
   batched `predict([frame1, frame2, ...])` is the lever if needed.
5. `shape` must be divisible by 32 (patch 16 × windows 2). `padding` is not
   a predict kwarg; valid params: `images, threshold, shape, patch_size,
   include_source_image`.
6. COCO ids: person=0, sports ball=32. `detections['class_name']` available.

## SportsMOT — acquisition (official sources verified)

- Paper: **Cui et al., ICCV 2023** (arXiv:2304.05170), repo
  `MCG-NJU/SportsMOT`. (An earlier subagent report claiming "Sun et al., ICCV
  2021, SenseTime" was wrong — corrected; the HF page matches Cui.)
- **License: CC BY-NC 4.0** + competition terms (no redistribution w/o
  permission). docs/07 previously said CC BY 4.0 — **corrected** in commit
  `4c0f374`. Consequences: eval-only; raw frames/GT never committed; NC
  annotations must never enter a future training set.
- **Official HF mirror** `huggingface.co/datasets/MCG-NJU/SportsMOT`:
  `dataset/train.tar` 6.39 GB, `val.tar` 6.29 GB, `test.tar` 22.1 GB
  (test has no GT). `splits_txt/`: 80 basketball sequences total;
  **15 in train + 15 in val carry GT** (35 test-only).
- Basketball clip stats (README): avg 845 frames @25 fps (~34 s), ~10
  tracks/clip, ~9 boxes/frame, avg track length 768 fr (long IDs — good for
  IDF1), track gap 69 fr.
- → bench plan: use the 30 GT basketball sequences ≈ 17 min of footage at
  25 fps. Selective extraction from the tars using the basketball∩(train|val)
  list in `bench/_staging/` (gitignored).
- MOT-challenge gt.txt rows are 9 cols: `frame,id,x,y,w,h,conf,class,visible`
  (class=1 → player; only on-court players annotated — referees/audience
  excluded by annotators, which conveniently matches our target set).

## Stowe quarter-length clip (v0.1 primary footage)

- `clips/stowe_full_1080p.webm` — Commons *Boys Varsity Basketball v. Stowe —
  Feb. 10, 2025*, **CC BY 4.0**, Hardwick Community TV. 3.31 GB,
  **AV1 1920×1080 @60 fps, 5350 s (89 min, full game)**, opus audio.
  SHA256 `f7cfa0eb…c4c2f4` (full in `clips/MANIFEST.md`).
- Decode: OpenCV's bundled ffmpeg fails AV1 → use system ffmpeg (libdav1d)
  pipe like v0 already does. 60 fps source: v0.1 pipeline should read with
  frame-step 2 (→ ~30 fps effective) to halve GPU time.
- Quarter extraction for runs: ffmpeg `-ss/-t` cuts from the full file into
  `clips/quarters/` (derived cuts share the same license; record cut ranges
  + hashes in MANIFEST when cut).

## venv state (shared `.venv`, py3.13)

Added for v0.1: scenedetect 0.7.2, rfdetr 1.11.2, trackers 2.6.1
(roboflow: `OCSORTTracker`, `ByteTrackTracker`, `BoTSORTTracker`,
`CMCConfig`, `load_mot_file`, `eval`). Still missing (M3/M4): paddleocr,
transformers/SigLIP (torch already present), possibly `timm`.

## 2026-11-02b — bench/mini-2026-10 built (M1 data complete)

- SportsMOT train.tar (6.70 GB) + val.tar (6.59 GB) downloaded to `bench/_staging/`
  (gitignored). Both tar-valid (exit 0, only AppleDouble xattr warnings; tar contains
  macOS `._*` junk — deleted 25k+ files after extraction).
- basketball ∩ (train|val) = exactly **30 sequences** (`_staging/basketball_gt.txt`);
  extracted via `tar --wildcards -T extract_patterns.txt` (patterns `train/<seq>/*` etc;
  exit 2 = harmless "pattern didn't match both tars"). Extracted = 6.0 GB, all have
  img1/ + gt/gt.txt + seqinfo.ini (25 fps, 720p, ~845 fr avg).
- Public GT is players-only: gt.txt cls column = 1 for all 227,673 rows (no referee rows).
- Final layout = score.py's bench contract: `bench/mini-2026-10/<seq>/{img1/,gt/gt.txt,gt/seqinfo.ini}`
  (seqinfo.ini moved into gt/; configparser lowercases keys → use info.get('imext')).
- Identity-tracker smoke: HOTA/MOTA/IDF1 = 1.0 on 30/30 (`bench/score.py --trackers <gt-copies>`).
- TrackEval vendored + numpy-alias patched; sha256 manifest embedded in third_party/TRACKEVAL.lock
  (`bench/no_training_check.py --update-vendor-manifest` regenerates; all green).
- Git repo root is the **parent** `ai-research/` (paths prefixed `basketball-player-detect/`).
- Labeling: no vision in any assistant model → manual human labeling chosen (all 30 seqs).
  Tooling: `bench/label_attrs.py` (5 crops/track → labels/review/), `bench/make_label_ui.py`
  (self-contained labels/label.html with instructions + localStorage autosave + CSV export),
  `bench/ingest_labels.py` (validate + split into labels/<seq>/track_attrs.csv).
  Commit 30e0e17 = bench foundation; labeling UI follow-up commit.
