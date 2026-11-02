# v0 Prototype: Detect & Track Players on One Clip

Status: **proposal** (not yet built). Goal: same-day qualitative sanity check
of the core detect→track pipeline on our own footage, before investing in
fine-tunes, ReID, or calibration. Scope rationale: see
`03-recommended-architecture.md` § "Suggested build order". Testing
procedure once built: `10-testing-guide.md` § 3 (v0 table).

## Objectives (v0 only)

1. Every player in frame gets a bounding box with a **stable track ID**
   (occasional switches acceptable; we want to *count* them, not fix them).
2. Real-time-ish processing (≥10 FPS end-to-end on one GPU, or offline batch).
3. Overlay video output we can watch to judge failure modes (occlusion,
   referees, bench crowd, camera motion).
4. Out of scope for v0: team assignment, jersey numbers, ReID, homography,
   stats. (v1+ — deliberately deferred so v0 measures the tracker, not the
   rest.)

## Components

| Component | Choice | Notes |
|---|---|---|
| Detector | `yolo11m-pose` or `yolo11m` (COCO `person` class only) | Off-the-shelf, zero training. Pose variant is +free signal for later filtering (players vs seated spectators). |
| Tracker | ByteTrack (via `model.track(persist=True, tracker="bytetrack.yaml")`) | Static-camera default per landscape doc; swap to `botsort.yaml` if clip has camera motion — one-line change. |
| Overlay / bookkeeping | `supervision` (annotators, `ByteTrackTracker`, CSV via `sv.CSVSink` or manual dict) | |
| Input | 1–3 clips, 2–5 min each, 1080p, one fixed wide camera | Practice/analysis-style recording; grab broadcast clip separately as a known-hard case, run it but don't gate on it. |

## Deliverables

```
src/prototype/v0/
  detect_track.py      # CLI: video in -> overlay mp4 + tracks.csv + fps.json
  tracks.csv           # frame, time_s, track_id, x1,y1,x2,y2, conf
  README.md            # how to run
notebooks/v0_review.ipynb  # eyeball metrics: IDs over time, count histogram
```

## Code sketch (the whole prototype, essentially)

```python
import csv, time
import cv2
from ultralytics import YOLO
import supervision as sv

model = YOLO("yolo11m.pt")
annotator = sv.AnnotatedFrame()
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

video_in = sv.VideoCapture("clips/game1.mp4")
video_out = sv.VideoSink("out/game1_tracked.mp4", video_in)

def on_frame(frame, tracker_id, xyxy):  # aggregation to tracks.csv
    ...

with open("out/tracks.csv", "w", newline="") as f:
    writer = csv.writer(f); writer.writerow(["frame","t_s","track_id","x1","y1","x2","y2","conf"])
    t0 = time.time(); frame_i = 0
    for frame in video_in:
        det = model.track(frame, classes=[0], tracker="bytetrack.yaml",
                          persist=True, conf=0.3, verbose=False)[0]
        # write det.boxes.id / xyxy / conf rows ...
        video_out.write_frame(frame, annotations=[det])
        frame_i += 1
```

(Final form will use `model.video_cb`/generator API or `sv`'s tracking
wrappers; sketch is indicative.)

## Procedure

1. Create venv, `pip install ultralytics supervision opencv-python`.
2. Put 2–3 clips in `clips/` (fixed-cam primary; one broadcast clip as
   stress case).
3. Run ByteTrack on fixed-cam clips; run **both** ByteTrack and BoT-SORT on
   the broadcast clip.
4. Produce overlay videos + `tracks.csv`.
5. Review notebook: expected-player-count histogram over time (should sit at
   10 during play + refs; deviations = missed/ghost detections), longest-lived
   track durations, ID churn per minute.
6. Write a short findings note (`docs/notes/v0-findings.md`) deciding:
   is detection good enough for v1 without fine-tune? does camera motion
   force BoT-SORT? roughly how many annotation-labeled minutes do we need
   for the TrackEval mini-benchmark?

## Acceptance criteria (qualitative, v0 bar is low)

- ≥90% of visible players detected on the fixed-cam clip (eyeball, 10 s
  samples × 6).
- During continuous play, ≥6 of 10 players keep an ID for >5 s stretches.
- Output video watchable; processing ≥10 FPS or completes in <3× realtime.
- tracks.csv round-trips (pandas-loadable, sane coordinates).

## Known expected failures (we *want* v0 to expose these)

- ID swaps in 2–3 player pile-ups (rebounds/picks) → motivates Basketball-SORT
  style association in v1.
- Refs and warm-up crowd tracked as players → motivates `referee` class +
  court-region mask in v1.
- Broadcast zoom/pans fragment tracks → motivates shot-boundary splitting.
- Bench players at frame edge flicker → motivates region-of-interest filtering.

## Time box

Half a day to first overlay video; one day total including review notebook.
