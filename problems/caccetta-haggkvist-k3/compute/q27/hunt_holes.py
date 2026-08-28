#!/usr/bin/env python3
"""Walk remaining exact holes after q26, high-k cubes first, store DRATs.

If a cube times out, retry with a longer budget, kissat --stable, then a
t = |N⁺(1) ∩ U| split. One timeout is not residue.
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from holes import cube_range, remaining_after_q26
from run_cubes import solve_cube

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
KEEP = CERTS / "keep"


def is_ok(row: dict) -> bool:
    return row.get("status") == "UNSAT" and row.get("drat") == "VERIFIED"


def try_t_split(n: int, d: int, k: int, secs: int) -> dict:
    """Split a stalled (n,d,k) cube on t = |N⁺(1) ∩ U|."""
    u_len = n - 1 - d - k
    # 1 needs d outs from (A\{1}) ∪ U, size (d-1)+u_len, so 1 ≤ t ≤ min(d, u_len)
    t_min = max(1, d - (d - 1))
    t_max = min(d, u_len)
    rows = []
    leftover = []
    for t in range(t_min, t_max + 1):
        slim = solve_cube(n, d, k, secs, True, False, t, False, True)
        slim["split"] = f"t={t}"
        rows.append(slim)
        print(
            f"    split t={t} {slim.get('status')} time={slim.get('time_s')} "
            f"drat={slim.get('drat')}",
            flush=True,
        )
        if not is_ok(slim):
            leftover.append(slim)
    if leftover:
        return {
            "n": n,
            "d": d,
            "indeg0": k,
            "status": "UNKNOWN",
            "drat": "split-leftover",
            "split_rows": rows,
            "leftover": leftover,
        }
    return {
        "n": n,
        "d": d,
        "indeg0": k,
        "status": "UNSAT",
        "drat": "VERIFIED",
        "split": "u_from_1",
        "split_rows": rows,
        "time_s": sum(r.get("time_s") or 0 for r in rows),
    }


def already_kept(n: int, d: int, k: int) -> bool:
    return (KEEP / f"ch-{n}-{d}-k{k}.drat").is_file()


def solve_cube_with_retry(n, d, k, secs, retries):
    if already_kept(n, d, k):
        rec = {
            "n": n,
            "d": d,
            "indeg0": k,
            "status": "UNSAT",
            "drat": "VERIFIED",
            "keep": f"ch-{n}-{d}-k{k}.drat",
            "skipped_existing": True,
        }
        print(f"  skip existing k={k}", flush=True)
        return rec
    attempts = []
    budgets = [secs]
    for extra in retries:
        budgets.append(extra)
    seen = set()
    uniq = []
    for b in budgets:
        if b not in seen:
            seen.add(b)
            uniq.append(b)

    for i, budget in enumerate(uniq):
        stable = i > 0
        print(
            f"  try k={k} time={budget}s stable={stable}",
            flush=True,
        )
        slim = solve_cube(n, d, k, budget, True, False, None, stable, True)
        slim["attempt"] = i
        slim["stable"] = stable
        attempts.append(slim)
        print(
            f"    k={k} {slim.get('status')} time={slim.get('time_s')} "
            f"conflicts={slim.get('conflicts')} drat={slim.get('drat')}",
            flush=True,
        )
        if is_ok(slim):
            slim["n_attempts"] = i + 1
            return slim
        if slim.get("status") == "SAT":
            slim["n_attempts"] = i + 1
            return slim

    print(f"  split k={k} on t=|N+(1)∩U|", flush=True)
    split = try_t_split(n, d, k, max(uniq))
    split["n_attempts"] = len(attempts)
    return split


def write_summary(closed, residue, this_run):
    prev_path = KEEP / "summary.json"
    prev_closed = []
    if prev_path.is_file():
        try:
            prev = json.loads(prev_path.read_text())
            prev_closed = list(prev.get("closed") or [])
        except json.JSONDecodeError:
            prev_closed = []
    all_closed = sorted(set(prev_closed) | set(closed))
    first_open = None
    leftover = remaining_after_q26(n_max=400)
    closed_set = set(all_closed)
    for row in leftover:
        if row["n"] not in closed_set:
            first_open = {"n": row["n"], "d": row["d"]}
            break
    n_cubes = 0
    if KEEP.is_dir():
        n_cubes = len(list(KEEP.glob("ch-*-*-k*.drat")))
    summary = {
        "closed": all_closed,
        "this_run": this_run,
        "n_cubes": n_cubes,
        "residue": [
            {"n": r["n"], "d": r["d"], "n_leftover": len(r["leftover"])} for r in residue
        ],
        "f4": 0.34640,
        "published_hkn": 0.3465,
        "prior_stored_f4": 0.34645,
        "personal_communication_3388": 0.3388,
        "next_hole": first_open,
        "note": (
            "closed = every needed cube UNSAT with stored DRAT. "
            "A leftover is residue, not a bound. F4 unchanged unless a new "
            "certificate says otherwise. Did not beat 0.3388."
        ),
    }
    path = KEEP / "summary.json"
    path.write_text(json.dumps(summary, indent=2))
    print("wrote", path, "closed", closed, "all_closed", all_closed)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--time", type=int, default=180)
    ap.add_argument("--n-max", type=int, default=145)
    ap.add_argument("--n-min", type=int, default=136)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--retry-time", type=int, default=600)
    ap.add_argument("--stop-on-unknown", action="store_true")
    args = ap.parse_args()

    holes = [
        row
        for row in remaining_after_q26(n_max=args.n_max)
        if row["n"] >= args.n_min
    ]
    print(
        f"remaining holes n={args.n_min}..{args.n_max}: {[r['n'] for r in holes]}",
        flush=True,
    )
    CERTS.mkdir(exist_ok=True)
    KEEP.mkdir(exist_ok=True)

    closed = []
    residue = []
    retries = [args.retry_time] if args.retry_time > args.time else []

    for row in holes:
        n, d = row["n"], row["d"]
        info = cube_range(n, d)
        ks = info["needed_cubes"]
        print(f"\n==== n={n} d={d} cubes {ks[0]}..{ks[-1]} ====", flush=True)
        rows = []
        leftover = []
        if args.jobs <= 1:
            for k in reversed(ks):
                slim = solve_cube_with_retry(n, d, k, args.time, retries)
                rows.append(slim)
                if slim.get("status") == "SAT" and slim.get("verified_model"):
                    leftover.append(slim)
                    print("SAT MODEL — would disprove the exact statement", flush=True)
                    (CERTS / f"n{n}_sat_model.json").write_text(
                        json.dumps(slim, indent=2)
                    )
                    break
                if not is_ok(slim):
                    leftover.append(slim)
                    if args.stop_on_unknown:
                        break
        else:
            with ThreadPoolExecutor(max_workers=args.jobs) as ex:
                futs = {
                    ex.submit(
                        solve_cube_with_retry, n, d, k, args.time, retries
                    ): k
                    for k in reversed(ks)
                }
                by_k = {}
                for fut in as_completed(futs):
                    slim = fut.result()
                    by_k[slim["indeg0"]] = slim
                    print(
                        f"  done k={slim['indeg0']} {slim.get('status')} "
                        f"time={slim.get('time_s')} drat={slim.get('drat')}",
                        flush=True,
                    )
                rows = [by_k[k] for k in sorted(by_k, reverse=True)]
                leftover = [r for r in rows if not is_ok(r)]

        rec = {
            "n": n,
            "d": d,
            "pigeonhole": info,
            "all_unsat": not leftover,
            "leftover": leftover,
            "rows": rows,
        }
        (CERTS / f"n{n}_cubes_summary.json").write_text(json.dumps(rec, indent=2))
        (KEEP / f"n{n}_cubes_summary.json").write_text(json.dumps(rec, indent=2))
        if leftover:
            residue.append({"n": n, "d": d, "leftover": leftover})
            print(f"RESIDUE n={n} leftover={len(leftover)}", flush=True)
            write_summary(closed, residue, closed)
            if args.stop_on_unknown:
                break
        else:
            closed.append(n)
            print(f"CLOSED n={n}", flush=True)
            write_summary(closed, residue, closed)

    write_summary(closed, residue, closed)
    return 0 if not residue else 1


if __name__ == "__main__":
    raise SystemExit(main())
