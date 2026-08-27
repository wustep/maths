#!/usr/bin/env python3
"""Replace a kissat DRAT with a smaller core-lemma DRAT if it still verifies.

GitHub rejects files over 100 MB and warns above 50 MB. Raw kissat proofs
at n≈84+ can hit that. ``drat-trim -l`` writes the used lemmas; those
must still replay against a CNF regenerated from encode.py.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from encode import encode, write_cnf
from solve import find_bin

HERE = Path(__file__).resolve().parent
KEEP = HERE / "certs" / "keep"


def write_cube_cnf(n: int, d: int, k: int, dest: Path) -> tuple[int, int]:
    clauses, nvars = encode(n, d, exact=True, sb=True, indeg0=k)
    with dest.open("w") as f:
        write_cnf(clauses, nvars, f)
    return nvars, len(clauses)


def verified(drat_bin: Path, cnf: Path, proof: Path) -> bool:
    chk = subprocess.run(
        [str(drat_bin), str(cnf), str(proof)],
        capture_output=True,
        text=True,
    )
    return "s VERIFIED" in (chk.stdout + chk.stderr)


def trim_proof(
    cnf: Path,
    raw: Path,
    dest: Path,
    *,
    binary: bool = False,
) -> dict:
    drat_bin = find_bin("drat-trim")
    cmd = [str(drat_bin), str(cnf), str(raw)]
    if binary:
        cmd.append("-C")
    cmd += ["-l", str(dest)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    text = proc.stdout + proc.stderr
    ok_trim = "s VERIFIED" in text and dest.is_file() and dest.stat().st_size > 0
    ok_replay = ok_trim and verified(drat_bin, cnf, dest)
    return {
        "trim_verified": ok_trim,
        "replay_verified": ok_replay,
        "raw_bytes": raw.stat().st_size,
        "core_bytes": dest.stat().st_size if dest.is_file() else 0,
        "binary": binary,
        "log_tail": text[-400:],
    }


def trim_keep_file(
    n: int,
    d: int,
    k: int,
    *,
    min_bytes: int = 8 * 1024 * 1024,
    try_binary: bool = True,
) -> dict:
    raw = KEEP / f"ch-{n}-{d}-k{k}.drat"
    if not raw.is_file():
        return {"n": n, "d": d, "k": k, "ok": False, "error": "missing-drat"}
    raw_bytes = raw.stat().st_size
    rec = {
        "n": n,
        "d": d,
        "k": k,
        "raw_bytes": raw_bytes,
        "replaced": False,
        "ok": True,
    }
    if raw_bytes < min_bytes:
        rec["skipped"] = "below-min"
        return rec
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cnf = tmp / "cube.cnf"
        write_cube_cnf(n, d, k, cnf)
        candidates = []
        text_core = tmp / "core.drat"
        candidates.append(trim_proof(cnf, raw, text_core, binary=False))
        if try_binary:
            bin_core = tmp / "core.bin.drat"
            candidates.append(trim_proof(cnf, raw, bin_core, binary=True))
        good = [
            c
            for c in candidates
            if c["replay_verified"] and 0 < c["core_bytes"] < raw_bytes
        ]
        rec["attempts"] = [
            {
                "binary": c["binary"],
                "core_bytes": c["core_bytes"],
                "replay_verified": c["replay_verified"],
            }
            for c in candidates
        ]
        if not good:
            rec["ok"] = any(c["replay_verified"] for c in candidates)
            rec["error"] = "no-smaller-verified-core"
            return rec
        best = min(good, key=lambda c: c["core_bytes"])
        src = text_core if not best["binary"] else (tmp / "core.bin.drat")
        dest = raw
        dest.write_bytes(src.read_bytes())
        rec["replaced"] = True
        rec["core_bytes"] = dest.stat().st_size
        rec["binary"] = best["binary"]
        rec["ok"] = verified(find_bin("drat-trim"), cnf, dest)
    return rec


def parse_stem(path: Path) -> tuple[int, int, int] | None:
    parts = path.stem.split("-")
    if len(parts) < 4 or not parts[3].startswith("k"):
        return None
    return int(parts[1]), int(parts[2]), int(parts[3][1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-mb", type=float, default=8.0)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--keep-dir", type=Path, default=KEEP)
    args = ap.parse_args()
    min_bytes = int(args.min_mb * 1024 * 1024)
    rows = []
    paths = sorted(args.keep_dir.glob("ch-*-*-k*.drat"))
    for path in paths:
        parsed = parse_stem(path)
        if parsed is None:
            continue
        n, d, k = parsed
        if args.n is not None and n != args.n:
            continue
        if path.stat().st_size < min_bytes:
            continue
        print(
            f"trim n={n} d={d} k={k} raw={path.stat().st_size}",
            flush=True,
        )
        rec = trim_keep_file(n, d, k, min_bytes=min_bytes)
        print(
            f"  ok={rec.get('ok')} replaced={rec.get('replaced')} "
            f"core={rec.get('core_bytes')} err={rec.get('error')}",
            flush=True,
        )
        rows.append(rec)
    print("trimmed", len(rows), "files")
    if any(not r.get("ok") for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
