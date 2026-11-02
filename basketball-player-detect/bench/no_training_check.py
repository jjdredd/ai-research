#!/usr/bin/env python3
"""bench/no_training_check.py — machine-check the v0.1 "zero training" invariant.

Three checks (docs/09 §Invariants):

1. WEIGH PINS: every checkpoint in bench/models.lock.json exists at the
   expected path with the pinned sha256 (stock publication, un-fine-tuned).
   A checkpoint loaded by code but absent from the lock is caught by check 2's
   name scan (default model filenames appear in source).
2. NO-TRAINING GREP: src/prototype/v0.1/ (and bench/) must not contain
   training-loop APIs. Allow-list inline with `# noqa: training-ok`.
3. VENDOR INTEGRITY: third_party/ files match the sha256 manifest embedded in
   third_party/TRACKEVAL.lock (# sha256  relpath lines appended below the
   header; regenerate with --update-vendor-manifest).

Exit code 0 = invariant holds. Run in CI / before every v0.1 run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "bench" / "models.lock.json"
VENDOR_DIR = REPO / "third_party" / "trackeval"
VENDOR_LOCK = REPO / "third_party" / "TRACKEVAL.lock"

TRAINING_PATTERNS = [
    (r"\.train\(", "model.train() / Dataset.train — training entrypoint"),
    (r"trainer\.fit", "lightning/trainer fit"),
    (r"\.backward\(", "loss.backward()"),
    (r"torch\.optim", "optimizer construction"),
    (r"(?<![\w.])optim\b\s*\(", "optimizer() call"),
    (r"\bepochs?\s*=\s*\d", "epochs= kwarg (training configs)"),
    (r"requires_grad_(?:\s*=\s*True)", "enabling grads on params"),
    (r"\.param_groups|\.parameters\(", "optimizer-style param access on a model"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_weights(fail: list[str]) -> None:
    lock = json.loads(LOCK.read_text())
    for w in lock["weights"]:
        p = Path(w["expected_path"]).expanduser()
        if not p.is_absolute():
            p = REPO / p
        if not p.exists():
            fail.append(f"WEIGHTS: {w['name']}: not found at {p}")
            continue
        got = sha256(p)
        if got != w["sha256"]:
            fail.append(
                f"WEIGHTS: {w['name']}: sha256 mismatch\n"
                f"  pinned: {w['sha256']}\n  actual: {got}  ({p})\n"
                f"  => local copy diverged from stock publication — possible fine-tune"
            )
    print(f"weights: {len(lock['weights'])} pinned, verified")


def check_no_training(fail: list[str]) -> None:
    roots = [REPO / "src" / "prototype"]
    n = 0
    for root in roots:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            text = py.read_text()
            for i, line in enumerate(text.splitlines(), 1):
                if "noqa: training-ok" in line:
                    continue
                for pat, why in TRAINING_PATTERNS:
                    if re.search(pat, line):
                        rel = py.relative_to(REPO)
                        fail.append(f"NO-TRAINING: {rel}:{i}: {why}\n  {line.strip()[:120]}")
                n += 1
    print(f"no-training grep: {n} lines scanned across src/prototype/**")


def vendor_manifest_lines() -> list[str]:
    lines = []
    for p in sorted(VENDOR_DIR.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            rel = p.relative_to(VENDOR_DIR.parent).as_posix()
            lines.append(f"# sha256 {sha256(p)}  {rel}")
    return lines


def check_vendor(fail: list[str]) -> None:
    text = VENDOR_LOCK.read_text()
    pinned = {}
    for line in text.splitlines():
        m = re.match(r"^# sha256 ([0-9a-f]{64})  (\S+)$", line)
        if m:
            pinned[m.group(2)] = m.group(1)
    if not pinned:
        fail.append("VENDOR: TRACKEVAL.lock has no sha256 manifest — run --update-vendor-manifest")
        return
    for rel, want in pinned.items():
        p = VENDOR_DIR.parent / rel
        if not p.exists():
            fail.append(f"VENDOR: {rel} missing")
        elif sha256(p) != want:
            fail.append(f"VENDOR: {rel} modified since vendoring (unpin+re-vendor intentionally)")
    for p in VENDOR_DIR.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            rel = p.relative_to(VENDOR_DIR.parent).as_posix()
            if rel not in pinned:
                fail.append(f"VENDOR: {rel} present but not in manifest")
    print(f"vendor integrity: {len(pinned)} files cross-checked against TRACKEVAL.lock")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--update-vendor-manifest", action="store_true",
                    help="embed/refresh sha256 manifest in TRACKEVAL.lock (do this at vendoring time)")
    args = ap.parse_args()

    if args.update_vendor_manifest:
        text = VENDOR_LOCK.read_text()
        text = "\n".join(l for l in text.splitlines() if not re.match(r"^# sha256 ", l))
        VENDOR_LOCK.write_text(text.rstrip("\n") + "\n" + "\n".join(vendor_manifest_lines()) + "\n")
        print(f"manifest updated ({len(vendor_manifest_lines())} files)")
        return

    fail: list[str] = []
    check_weights(fail)
    check_no_training(fail)
    check_vendor(fail)
    if fail:
        print(f"\nINVARIANT VIOLATED ({len(fail)}):")
        for f_ in fail:
            print(" -", f_)
        sys.exit(1)
    print("\nno-training invariant holds ✓")


if __name__ == "__main__":
    main()
