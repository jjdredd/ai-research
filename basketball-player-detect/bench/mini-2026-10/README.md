# bench/mini-2026-10

30 basketball sequences from **SportsMOT** (MCG-NJU/SportsMOT on HuggingFace,
`dataset/train.tar` + `val.tar`), being exactly the sequences that appear in
both `splits_txt/basketball.txt` and a public-GT split (15 train + 15 val).
Named 2026-10 by acquisition date.

## Layout (MOT-challenge 2D box format, as consumed by `bench/score.py`)

```
mini-2026-10/
  <seq>/                    e.g. v_2j7kLB-vEEk_c001
    img1/                   source frames (000001.jpg …)
    gt/gt.txt               frame,id,x,y,w,h,conf,class,visible  (class 1 = player)
    gt/seqinfo.ini          seqLength, frameRate=25, imWidth, imHeight, imExt
  labels/                   per-track attribute CSVs (team / jersey number) — see below
```

## LICENSE — READ BEFORE SHARING

SportsMOT is **CC BY-NC 4.0** with competition no-redistribution terms
(see docs/07-datasets.md). Therefore:

- This directory's contents (images + gt.txt + seqinfo.ini) are **NOT** to be
  committed or redistributed. The repo `.gitignore` excludes everything here
  except this README.
- Labels added under `labels/` inherit the NC restriction and must **never**
  enter a future training set (v0.1 trains nothing — enforced by
  `bench/no_training_check.py`).
- Re-acquire via: `huggingface.co/datasets/MCG-NJU/SportsMOT`
  (`dataset/train.tar` sha-verified; extraction recipe in
  `docs/notes/v01-acquisition-notes.md`).

## Scoring

```
.venv/bin/python bench/score.py --trackers <dir-with-seq-txt-files> [--seqs …]
```

Identity-tracker smoke (gt.txt copied as predictions) scores HOTA/MOTA/IDF1 =
1.0 on all 30 sequences — verified 2026-11-02.

## labels/ — manual attribute labeling (human task, ~1.5–2.5 h)

Team colors & jersey numbers are **not** in SportsMOT GT. They are added by
hand, per track, for all 30 sequences. Required for M3/M4 exit checks (team
assignment accuracy, jersey-number OCR, referee detection, gallery re-ID).

Workflow (regenerate any step; all outputs are gitignored):

1. `.venv/bin/python bench/label_attrs.py --all --crops-per-track 5`
   → per-track review crops in `labels/review/<seq>/` (up to 5 best frames
   per track, cropped from GT boxes — crops are guaranteed same-person per row).
2. `.venv/bin/python bench/make_label_ui.py`
   → writes `labels/label.html` — open it in a browser. It contains the full
   labeling instructions (team T1/T2 by jersey colour, number rules, non-player
   checkbox, notes), shows all 1500 crops, auto-saves progress per browser.
3. Press **Export CSV** when done (or to checkpoint) →
   drop the downloaded `track_attrs_all.csv` into `labels/`, then run
   `.venv/bin/python bench/ingest_labels.py` — validates track ids against GT
   and splits into `labels/<seq>/track_attrs.csv`
   (`track_id,team,number,non_player,note,gt_len_frames,median_h`).

Label quality bar: consistent team labels within a sequence; never guess a
number (blank = unreadable = excluded from OCR metric); flag officials as
non-player; note suspected GT id-switches.
