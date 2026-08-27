#!/usr/bin/env python3
"""Run verify_beta3 on a stored matrix, splitting the mask space.

Usage:
  python3 run_faces_parallel.py certs/beta3_mid_R10_n28_t0p9100.txt \\
      certs/beta3_mid_faces_R10_n28_t0p9100.txt

Writes the merged faces dump. Exit 0 iff copositive.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def parse_faces(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        k, _, v = line.partition(" ")
        if k in {
            "n",
            "interior_critical",
            "singular_or_illconditioned",
            "n_faces",
            "copositive",
        }:
            out[k] = int(float(v))
        elif k in {"mask_lo", "mask_hi"}:
            out[k] = int(v)
        else:
            out[k] = float(v)
    return out


def merge(parts: list[dict]) -> dict:
    n = parts[0]["n"]
    target = parts[0]["gamma_target"]
    nfaces = (1 << n) - 1
    interior = sum(p["interior_critical"] for p in parts)
    singular = sum(p["singular_or_illconditioned"] for p in parts)
    min_m = min(p["min_mMm"] for p in parts)
    min_phi = min(p["min_phi"] for p in parts)
    margin = 1e-10
    min_m_safe = min_m - margin
    min_phi_safe = min_phi - margin
    return {
        "n": n,
        "gamma_target": target,
        "n_faces": nfaces,
        "interior_critical": interior,
        "singular_or_illconditioned": singular,
        "min_mMm": min_m,
        "min_mMm_safe": min_m_safe,
        "min_phi": min_phi,
        "min_phi_safe": min_phi_safe,
        "copositive": 1 if min_m_safe >= 0.0 else 0,
    }


def write_faces(path: Path, blob: dict) -> None:
    lines = [
        f"n {blob['n']}",
        f"gamma_target {blob['gamma_target']:.16e}",
        f"n_faces {blob['n_faces']}",
        f"interior_critical {blob['interior_critical']}",
        f"singular_or_illconditioned {blob['singular_or_illconditioned']}",
        f"min_mMm {blob['min_mMm']:.16e}",
        f"min_mMm_safe {blob['min_mMm_safe']:.16e}",
        f"min_phi {blob['min_phi']:.16e}",
        f"min_phi_safe {blob['min_phi_safe']:.16e}",
        f"copositive {blob['copositive']}",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("matrix")
    ap.add_argument("faces")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    mat = Path(args.matrix)
    fac = Path(args.faces)
    header = mat.read_text().splitlines()[0].split()
    n = int(float(header[0]))
    nfaces = (1 << n) - 1
    jobs = max(1, min(args.jobs, nfaces))

    cbin = HERE / "verify_beta3"
    src = HERE / "verify_beta3.c"
    subprocess.check_call(["gcc", "-O3", "-o", str(cbin), str(src), "-lm"])

    span = nfaces // jobs
    procs = []
    parts = []
    for j in range(jobs):
        lo = 1 + j * span
        hi = nfaces if j == jobs - 1 else (j + 1) * span
        part = fac.with_name(fac.name + f".part{j}")
        log = part.with_suffix(part.suffix + ".log")
        lf = open(log, "w")
        p = subprocess.Popen(
            [str(cbin), str(mat), str(part), str(lo), str(hi)],
            cwd=str(HERE),
            stdout=lf,
            stderr=subprocess.STDOUT,
        )
        procs.append((p, lf, part, lo, hi))
        print(f"shard {j}: masks {lo}..{hi} -> {part.name}", flush=True)

    failed = False
    for p, lf, part, lo, hi in procs:
        rc = p.wait()
        lf.close()
        print(f"shard {part.name} exit {rc} range {lo}..{hi}", flush=True)
        if rc != 0:
            # copositive failure is still a valid dump if the file exists
            if not part.exists():
                failed = True
                continue
        parts.append(parse_faces(part))

    if failed or len(parts) != jobs:
        raise SystemExit("run_faces_parallel.py FAIL (missing shard)")

    blob = merge(parts)
    write_faces(fac, blob)
    print(
        f"merged n={blob['n']} target={blob['gamma_target']:.6f} "
        f"minM={blob['min_mMm']:.4e} minφ={blob['min_phi']:.8f} "
        f"singular={blob['singular_or_illconditioned']} "
        f"copositive={blob['copositive']}"
    )
    print("wrote", fac)
    if not blob["copositive"]:
        raise SystemExit("run_faces_parallel.py FAIL (not copositive)")
    print("run_faces_parallel.py PASS")


if __name__ == "__main__":
    main()
