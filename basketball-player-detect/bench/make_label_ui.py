#!/usr/bin/env python3
"""bench/make_label_ui.py — generate labels/label.html, a manual labeling UI.

Scans bench/mini-2026-10/ for sequences + their labels/review/<seq>/<tid>_*.jpg
crops, and writes one self-contained HTML page (images via relative paths —
open directly in a browser from the labels/ directory).

Per track row: crops + team input (T1/T2/... , datalist per sequence),
number input, non-player checkbox, note. Progress persists in localStorage.
"Export CSV" downloads track_attrs_all.csv (all sequences, one row per track)
for bench/ingest_labels.py.

Usage:
    .venv/bin/python bench/make_label_ui.py
    xdg-open bench/mini-2026-10/labels/label.html
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BENCH = REPO / "bench" / "mini-2026-10"
LABELS = BENCH / "labels"

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>mini-2026-10 attribute labeling</title>
<style>
body{font-family:system-ui;margin:1em;background:#181818;color:#ddd}
h1{font-size:1.2em} .seq{margin:1.5em 0;padding:1em;background:#222;border-radius:8px}
.row{display:flex;align-items:center;gap:8px;margin:.6em 0;flex-wrap:wrap;border-bottom:1px solid #333;padding-bottom:.4em}
.row img{height:150px;border:2px solid transparent;border-radius:4px}
.row.done img{border-color:#2a7}
input.t{width:70px} input.n{width:60px} input.note{width:220px}
input{background:#111;color:#eee;border:1px solid #555;border-radius:4px;padding:3px}
.done{opacity:.55} .bar{position:sticky;top:0;background:#181818;padding:.5em 0;z-index:9;border-bottom:1px solid #444}
button{background:#357;color:#fff;border:0;border-radius:6px;padding:6px 12px;cursor:pointer;margin-right:8px}
.help{background:#202030;border:1px solid #446;border-radius:8px;padding:.6em 1em;margin:.8em 0;font-size:.92em}
.help li{margin:.45em 0} code{background:#111;padding:1px 4px;border-radius:3px}
.tip{color:#999;font-size:.85em;margin:.3em 0}
</style></head><body>
<div class="bar"><button onclick="exportCsv()">Export CSV</button>
<button onclick="jumpNext()">Next incomplete</button>
<span id="stat"></span></div>
<details class="help" open><summary><b>How to label — read once, then collapse</b></summary>
<ol>
<li><b>Work one sequence at a time.</b> Each dark panel is one video sequence (~10 rows).
    Every row shows the <i>same tracked player</i> in up to 5 crops, taken at different
    frames (largest / most visible first). All crops in a row are guaranteed to be the
    same person — that is what the ground-truth track IDs tell us.</li>
<li><b>Team (required).</b> Look at the jersey colour across the row's crops. Players on
    the same team share the same jersey colour. Assign a short label per colour:
    <code>T1</code>, <code>T2</code>, and so on. The labels only need to be
    <i>consistent inside one sequence</i> (all white-jersey players → T1, all dark → T2,
    in that sequence). It does not matter which team is T1 vs T2. If a third kind of
    person appears (officials in stripes, coaches in suits), give them their own label
    (e.g. <code>T9</code>) and also tick Non-player.</li>
<li><b>Number.</b> Look at all crops; type the jersey number if readable in at least one.
    Two digits are normal (0–55). <u>If you cannot read it confidently, leave it
    blank</u> — blank is useful data (the OCR metric then ignores this track). Don't
    guess. If two crops seem to show different digits, the track's identity may be wrong:
    write <code>idswitch?</code> in the note field.</li>
<li><b>Non-player checkbox.</b> Tick it if this track is <i>not</i> an active player
    (referee, coach, seated bench player who wandered into frame, mascot, camera person).
    Referee stripes are usually obvious: vertical black/white.</li>
<li><b>Note field.</b> Free text for anything odd: partial occlusion, ball boy, jersey
    number on front not back, motion blur, suspected tracker id-switch, etc.</li>
<li><b>Progress is automatic.</b> Every edit is saved in this browser immediately
    (localStorage). You can close the tab and re-open the same label.html to continue —
    labeled rows dim and <i>Next incomplete</i> scrolls you onward. Keep using the same
    browser and file location, or your progress is lost. (If you must switch machines,
    Export CSV before leaving and ask the assistant to pre-load it.)</li>
<li><b>When all 30 sequences are done</b> (or any time to checkpoint): press
    <b>Export CSV</b>. It downloads <code>track_attrs_all.csv</code>. Move that file to
    <code>basketball-player-detect/bench/mini-2026-10/labels/track_attrs_all.csv</code>
    and tell the assistant &quot;labels exported&quot; — it will run
    <code>bench/ingest_labels.py</code> to validate and split them into per-sequence
    files, then continue the pipeline work.</li>
<li><b>Quality bar:</b> a wrong team label is worse than an honest blank+note. If a
    player's jersey is ambiguous (light grey between teams), label it and note
    <code>ambiguous</code>.</li>
</ol>
<div class="tip">Estimated time: 3–5 min per sequence × 30 ≈ 1.5–2.5 h total. Taking breaks is fine — state persists.</div>
</details>
<div id="content"></div>
<script>
const DATA = __DATA__;
const KEY = "mini202610-labels-v1";
let state = JSON.parse(localStorage.getItem(KEY) || "{}");
function save(){ localStorage.setItem(KEY, JSON.stringify(state)); render_stat(); }
function tidKey(seq, tid){ return seq + ":" + tid; }
function build(){
  const c = document.getElementById("content");
  let h = "";
  for (const [seq, tracks] of Object.entries(DATA)) {
    h += `<div class="seq" id="seq-${seq}"><b>${seq}</b> (${tracks.length} tracks)`;
    for (const [tid, crops] of tracks) {
      const k = tidKey(seq, tid); const s = state[k] || {};
      const imgs = crops.map(p => `<img src="${p}" loading="lazy">`).join("");
      h += `<div class="row ${s.team?"done":""}" id="r-${k}">${imgs}` +
        `<input class="t" list="teams-${seq}" placeholder="team" value="${s.team||""}" onchange="upd('${k}','team',this)">` +
        `<input class="n" placeholder="num" value="${s.number||""}" onchange="upd('${k}','number',this)">` +
        `<label><input type="checkbox" ${s.nonplayer?"checked":""} onchange="upd('${k}','nonplayer',this)"></label>` +
        `<input class="note" placeholder="note" value="${s.note||""}" onchange="upd('${k}','note',this)">` +
        `</div>`;
    }
    h += `</div>`;
  }
  c.innerHTML = h;
  render_stat();
}
function upd(k, f, el){
  const s = state[k] || (state[k]={});
  s[f] = (el.type==="checkbox") ? el.checked : el.value.trim();
  const row = document.getElementById("r-"+k);
  if (s.team) row.classList.add("done"); else row.classList.remove("done");
  save();
}
function render_stat(){
  let total=0, done=0; const seqs={};
  for (const [seq, tracks] of Object.entries(DATA)){
    let d=0; for (const [tid] of tracks){ total++; const s=state[tidKey(seq,tid)]; if(s&&s.team){done++;d++;} }
    seqs[seq]=d+"/"+tracks.length;
  }
  document.getElementById("stat").textContent = `tracks labeled: ${done}/${total}`;
}
function jumpNext(){
  for (const [seq, tracks] of Object.entries(DATA))
    for (const [tid] of tracks){ const s=state[tidKey(seq,tid)]; if(!(s&&s.team)){ document.getElementById("r-"+CSS.escape(tidKey(seq,tid)))?.scrollIntoView({behavior:"smooth",block:"center"}); return; } }
}
function exportCsv(){
  let rows = ["seq,track_id,team,number,non_player,note"];
  for (const [seq, tracks] of Object.entries(DATA))
    for (const [tid] of tracks){ const s=state[tidKey(seq,tid)]||{};
      if(!s.team) continue;
      rows.push(`${seq},${tid},${(s.team||"").replace(/,/g,";")},${s.number||""},${s.nonplayer?1:0},"${(s.note||"").replace(/"/g,"'")}"`);
    }
  const blob=new Blob([rows.join("\\n")],{type:"text/csv"});
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download="track_attrs_all.csv"; a.click();
}
build();
</script></body></html>
"""


def main() -> None:
    data: dict[str, list] = {}
    review = LABELS / "review"
    for seq_dir in sorted(p for p in BENCH.iterdir() if (p / "gt" / "gt.txt").exists()):
        seq = seq_dir.name
        crops: dict[str, list[str]] = {}
        for p in sorted((review / seq).glob("*.jpg")):
            tid = p.stem.split("_")[0].lstrip("0") or "0"
            crops.setdefault(tid, []).append(f"review/{seq}/{p.name}")
        data[seq] = list(crops.items())
    html = TEMPLATE.replace("__DATA__", json.dumps(data))
    out = LABELS / "label.html"
    out.write_text(html)
    n_tracks = sum(len(t) for t in data.values())
    print(f"wrote {out}\n{len(data)} sequences, {n_tracks} tracks — open in a browser, then Export CSV into bench/mini-2026-10/labels/")


if __name__ == "__main__":
    main()
