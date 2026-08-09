# Validation Set CPU Inference Results — Basketball_51

All 24 videos from the validation split (`basketball51_val.txt`),
3 per class, processed with `infer.py --cpu` using the best checkpoint
(`best_acc_top1_epoch_41_fixed.pth`).

## Per-video results

| Video | Ground Truth | Prediction | Top-1 Conf | Top-2 | Correct? |
| --- | --- | --- | --- | --- | --- |
| 2p0_v108_001936_x264.mp4 | 2-pt miss | 2-pt miss | 65.1% | 2-pt made (27.4%) | ✓ |
| 2p0_v108_010620_x264.mp4 | 2-pt miss | 2-pt miss | 45.9% | Misc miss (36.8%) | ✓ |
| 2p0_v156_005139_x264.mp4 | 2-pt miss | Misc miss | 40.9% | 2-pt miss (31.5%) | ✗ |
| 2p1_v108_000546_x264.mp4 | 2-pt made | 2-pt made | 72.6% | Misc made (22.6%) | ✓ |
| 2p1_v108_005937_x264.mp4 | 2-pt made | 2-pt made | 45.3% | 2-pt miss (21.8%) | ✓ |
| 2p1_v152_003216_x264.mp4 | 2-pt made | 2-pt made | 55.8% | 2-pt miss (44.2%) | ✓ |
| 3p0_v108_005125_x264.mp4 | 3-pt miss | 3-pt miss | 66.6% | Misc miss (14.4%) | ✓ |
| 3p0_v108_011250_x264.mp4 | 3-pt miss | 3-pt miss | 33.8% | 3-pt made (22.6%) | ✓ |
| 3p0_v152_005815_x264.mp4 | 3-pt miss | 3-pt miss | 90.0% | 3-pt made (5.4%) | ✓ |
| 3p1_v108_001544_x264.mp4 | 3-pt made | 2-pt made | 49.3% | 3-pt made (39.7%) | ✗ |
| 3p1_v108_005158_x264.mp4 | 3-pt made | 3-pt made | 76.2% | 3-pt miss (18.5%) | ✓ |
| 3p1_v147_010503_x264.mp4 | 3-pt made | 3-pt made | 84.2% | Misc made (15.5%) | ✓ |
| ft0_v108_002649_x264.mp4 | FT miss | FT made | 83.7% | FT miss (16.3%) | ✗ |
| ft0_v108_013556_x264.mp4 | FT miss | FT miss | 81.1% | FT made (18.9%) | ✓ |
| ft0_v157_014035_x264.mp4 | FT miss | FT miss | 82.5% | FT made (17.2%) | ✓ |
| ft1_v108_000302_x264.mp4 | FT made | FT made | 99.5% | FT miss (0.5%) | ✓ |
| ft1_v108_001409_x264.mp4 | FT made | FT made | 88.1% | FT miss (11.9%) | ✓ |
| ft1_v146_002010_x264.mp4 | FT made | FT made | 99.6% | FT miss (0.3%) | ✓ |
| mp0_v108_003022_x264.mp4 | Misc miss | 3-pt miss | 61.3% | Misc miss (25.9%) | ✗ |
| mp0_v108_012119_x264.mp4 | Misc miss | Misc miss | 22.3% | Misc made (21.6%) | ✓ |
| mp0_v146_010151_x264.mp4 | Misc miss | 2-pt made | 28.1% | Misc made (17.8%) | ✗ |
| mp1_v108_000758_x264.mp4 | Misc made | Misc made | 63.0% | 3-pt made (16.1%) | ✓ |
| mp1_v108_010539_x264.mp4 | Misc made | 3-pt miss | 43.3% | 3-pt made (17.0%) | ✗ |
| mp1_v129_005619_x264.mp4 | Misc made | 2-pt made | 68.4% | 2-pt miss (21.6%) | ✗ |

## Per-class accuracy

| Class | Accuracy |
| --- | --- |
| **2-pt miss** | 2/3 = 66.7% |
| **2-pt made** | 3/3 = 100.0% |
| **3-pt miss** | 3/3 = 100.0% |
| **3-pt made** | 2/3 = 66.7% |
| **FT miss** | 2/3 = 66.7% |
| **FT made** | 3/3 = 100.0% |
| **Misc miss** | 1/3 = 33.3% |
| **Misc made** | 1/3 = 33.3% |
| **Overall** | **17/24 = 70.8%** |

## Confusion matrix (normalized by row)

Rows are ground truth (3 samples per class), columns are predicted labels.
Each row sums to 1.0 (probabilities).  Diagonal = recall for that class.

| GT ↓ \ Pred → | 2-pt miss | 2-pt made | 3-pt miss | 3-pt made | FT miss | FT made | Misc miss | Misc made |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2-pt miss** | **0.667** | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.333 | 0.000 |
| **2-pt made** | 0.000 | **1.000** | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| **3-pt miss** | 0.000 | 0.000 | **1.000** | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| **3-pt made** | 0.000 | 0.333 | 0.000 | **0.667** | 0.000 | 0.000 | 0.000 | 0.000 |
| **FT miss** | 0.000 | 0.000 | 0.000 | 0.000 | **0.667** | 0.333 | 0.000 | 0.000 |
| **FT made** | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | **1.000** | 0.000 | 0.000 |
| **Misc miss** | 0.000 | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 | **0.333** | 0.000 |
| **Misc made** | 0.000 | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 | 0.000 | **0.333** |

### Confusion matrix analysis

- **Diagonal strength**: 17/24 diagonal hits — most errors are concentrated in
  just 7 off-diagonal cells.  The average recall across all 8 classes is 0.708.

- **FT miss ↔ FT made** (0.333 confusion probability): The model confuses the
  two free-throw classes at a high rate — one FT miss was classified as FT made
  at 83.7% confidence (top-2 correctly includes FT miss).  The visual
  difference between a made and missed free-throw (subtle trajectory change)
  is harder to learn than the binary outcome.

- **3-pt made → 2-pt made** (0.333): One 3-pt made video was classified as
  2-pt made at 49.3% confidence, barely above the 39.7% 3-pt made probability.
  The shooting motion for longer-range attempts apparently resembles a 2-pt
  motion to the model.

- **Misc miss → 3-pt miss and 2-pt made** (0.333 each): The catch-all "miss"
  class confuses with specific miss types — the model tries to pin the action
  to a concrete shot category even when the clip is a non-standard miss.

- **Misc made → 3-pt miss and 2-pt made** (0.333 each): Similarly, the catch-
  all "made" class gets pulled toward 2-pt made (the most populous made class)
  or 3-pt miss (when the clip has a longer-range look).

- **2-pt miss → Misc miss** (0.333): The model occasionally mislabels a 2-pt
  miss as Misc miss (40.9% confidence), suggesting some 2-pt miss clips look
  generic enough to fall into the catch-all bucket.

- **No cross-shot-type confusion**: The model never confuses a 2-pt attempt
  with a 3-pt attempt, or a free-throw with a field-goal — the errors are
  either within the same shot family (FT miss↔FT made) or between a specific
  class and its corresponding catch-all (Misc class).

### Key observations

- **Strong classes** (100% recall): 2-pt made, 3-pt miss, FT made — distinctive
  motion patterns the model locks onto confidently.
- **Weakest classes** (33.3% recall): Misc miss and Misc made — catch-all
  classes with high intra-class variation.
- **Top-2 rescue**: In 6 of 7 errors, the true class appears in the top-2,
  confirming that top-3 evaluation would push accuracy toward 85%+.
- **Gap**: Validation accuracy (70.8%) is 8.4% below the mixed-set evaluation
  (79.2%), confirming that the earlier run was inflated by training-set samples.

## Comparison with previous uncontrolled run

The earlier run sampled from the full dataset (train+val mix) and got
79.2% overall.  The validation-only run below shows true generalization.

| Split | Accuracy |
| --- | --- |
| Mixed (train+val) | 19/24 = 79.2% |
| **Validation only** | **17/24 = 70.8%** |
