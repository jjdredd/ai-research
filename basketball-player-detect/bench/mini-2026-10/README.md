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

## labels/ (in progress)

Per-track constant attributes, one CSV per sequence:
`labels/<seq>/track_attrs.csv` with columns `track_id,team,number,note`.
Team colors & jersey numbers are not in SportsMOT GT; they are added manually
via `bench/label_attrs.py` crop review. Required for M3/M4 exit checks
(team assignment accuracy, OCR accuracy, gallery re-ID).
