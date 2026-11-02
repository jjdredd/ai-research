# Clips Manifest (v0 test footage)

All clips sourced from Wikimedia Commons (open licenses) on 2026-11-02.
Replace/augment with our own practice/analysis recordings when available —
docs/04 envisioned 2–5 min fixed-cam clips; the fixed-cam items here are
shorter (48–60 s) but sufficient for the v0 spike. A longer fixed-cam option
is on record below without being downloaded.

| File | Source (Commons) | License | Resolution | Duration | Role |
|---|---|---|---|---|---|
| `act_state_team_720p.ogv` | [ID Basketball ACT State Team](https://commons.wikimedia.org/wiki/File:ID_Basketball_ACT_State_Team.ogv) | CC BY-SA 3.0 | 1280×720 @30 | 48 s | fixed-cam primary |
| `sasebo_youth_1080p.webm` | [Sasebo Bo Boys Youth Basketball Game](https://commons.wikimedia.org/wiki/File:Sasebo_Bo_Boys_Youth_Basketball_Game_(999422).webm) | Public domain (US Navy) | 1920×1080 @29.97 | 60 s | fixed-cam secondary |
| `hawaii_highlights_1080p.webm` | [Hawaii Basketball — Highlights From Northern Arizona Game](https://commons.wikimedia.org/wiki/File:Hawaii_Basketball_-_Highlights_From_Northern_Arizona_Game.webm) | CC BY 3.0 | 1920×1080 @29.97 | 8 min 28 s | broadcast-style stress case (cuts/zooms; run both trackers, don't gate on it per docs/04) |
| `stowe_full_1080p.webm` | [Boys Varsity Basketball v. Stowe — Feb. 10, 2025](https://commons.wikimedia.org/wiki/File:Boys_Varsity_Basketball_v._Stowe_-_Feb._10,_2025.webm) | CC BY 4.0 | 1920×1080 **AV1 @60** | 89 min (full game) | **v0.1 quarter-length source** (docs/09). Fixed school-broadcast cam (Hardwick Community TV). AV1: decode via system ffmpeg (libdav1d), not OpenCV bundled ffmpeg. `f7cfa0eb97aa100f9835ceb102cbe82b853bee2731834b3f4ddff8594cf4c2f4` |

Not downloaded (recorded for later, esp. v0.1/v1 quarter-length sessions):

- [Boys Varsity Basketball v. Stowe — Feb. 10, 2025](https://commons.wikimedia.org/wiki/File:Boys_Varsity_Basketball_v._Stowe_-_Feb._10,_2025.webm) — CC BY 4.0, 1920×1080, full game, 3.3 GB. Best available long fixed-cam source.

## Attribution

- CC BY-SA 3.0 / CC BY 3.0 clips: attribute per license if ever redistributed
  (originals linked above; Commons pages carry author strings).
- US Navy imagery (Sasebo, Diego Garcia): public domain, no attribution required.

## Checksums

See `MANIFEST.sha256` (docs/10 § 0: clip hashes must match for a benchmark-
valid run). Regenerate with: `sha256sum *.ogv *.webm > MANIFEST.sha256`
