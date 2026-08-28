#!/usr/bin/env python3
"""Keep leftover ranks 22–26 thicken cores busy.

Imports complete leftover rows from q2/thick_out, then starts the
next unfinished census triangulation on a free q3 worker. Does not
write new_schemes.json. An incomplete prefix is residue, not a lower
bound.

usage:
  python3 q3/leftover_watch.py
  python3 q3/leftover_watch.py --once
  python3 q3/leftover_watch.py --max-workers 4
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from common import HERE, ROOT, boot
from write_thick_cert import collect_rows, expected_evals, merge_rows

boot()

SPAN = Path(ROOT) / "span_tasks.json"
Q2_OUT = Path(ROOT) / "q2" / "thick_out"
Q3_OUT = Path(HERE) / "thick_out"
DRIVE = Path(HERE) / "thick_drive.py"
IMPORT = Path(HERE) / "import_finished.py"


def leftover_tasks():
    return [t for t in json.loads(SPAN.read_text())
            if 22 <= t["rank"] <= 26]


def complete_certs():
    have = set()
    grouped = {}
    for rec in collect_rows():
        if rec.get("rank", 0) < 22:
            continue
        grouped.setdefault(rec["cert"], []).append(rec)
    for cert, recs in grouped.items():
        merged = merge_rows(recs, expected_evals(recs[-1]["rank"]))
        if merged and merged["complete"]:
            have.add(cert)
    return have


def finished_shards(cert):
    """Shards already written with complete=true. Do not relaunch them."""
    have = set()
    for rec in collect_rows():
        if rec.get("cert") != cert:
            continue
        if rec.get("nshards", 1) <= 1:
            continue
        if rec.get("complete") and rec.get("evals"):
            have.add(rec.get("shard", 0))
    return have


def ps_args():
    out = subprocess.check_output(["ps", "-eo", "args"], text=True)
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def running_thicken_count(lines):
    n = 0
    for ln in lines:
        if "/q2/thicken " in ln or "/q3/thicken " in ln or ln.startswith(
                str(Path(HERE) / "thicken")):
            n += 1
        elif ln.endswith("/thicken") or " thicken /tmp/" in ln:
            if "hilbert16" in ln or "/tmp/q2_thick" in ln or "/tmp/q3_thick" in ln:
                n += 1
    return n


def running_drive_count(lines):
    """A live thick_drive still owns a core: it will start the next C walker."""
    n = 0
    for ln in lines:
        if "leftover_watch" in ln:
            continue
        if "q2/thick_drive.py" in ln or "q3/thick_drive.py" in ln:
            n += 1
    return n


def _drive_argv(line, which):
    """Return argv after thick_drive.py for a q2 or q3 driver.

    Popen launches the absolute script path, so a literal
    ``q3/thick_drive.py`` token is not always present.
    """
    if "leftover_watch" in line:
        return None
    needle = f"{which}/thick_drive.py"
    if needle not in line:
        return None
    parts = line.split()
    for i, part in enumerate(parts):
        if part.endswith(needle):
            return parts[i + 1:]
    return None


def running_q3_only(lines):
    certs = set()
    workers = set()
    shards = {}
    for ln in lines:
        argv = _drive_argv(ln, "q3")
        if argv is None:
            continue
        cert = None
        if "--only" in argv:
            i = argv.index("--only")
            if i + 1 < len(argv):
                cert = argv[i + 1]
                certs.add(cert)
        try:
            workers.add(int(argv[0]))
        except (ValueError, IndexError):
            pass
        nsh = 1
        shard = 0
        if "--nshards" in argv:
            nsh = int(argv[argv.index("--nshards") + 1])
        if "--shard" in argv:
            shard = int(argv[argv.index("--shard") + 1])
        if cert and nsh > 1:
            shards.setdefault(cert, (nsh, set()))[1].add(shard)
    return certs, workers, shards


def q2_reserved(lines, done):
    reserved = set()
    tasks = [t for t in json.loads(SPAN.read_text())
             if 21 <= t["rank"] <= 22]
    tasks.sort(key=lambda d: (d["rank"], d["cert"]))
    for ln in lines:
        argv = _drive_argv(ln, "q2")
        if argv is None or len(argv) < 4:
            continue
        try:
            w, nw, lo, hi = (int(argv[0]), int(argv[1]),
                             int(argv[2]), int(argv[3]))
        except ValueError:
            continue
        mine = [d for i, d in enumerate(tasks)
                if lo <= d["rank"] <= hi and i % nw == w]
        for d in mine:
            if d["rank"] >= 22 and d["cert"] not in done:
                reserved.add(d["cert"])
    return reserved


def import_q2():
    subprocess.run([sys.executable, str(IMPORT), str(Q2_OUT)], check=False)


def launch(cert, rank, worker, shard=0, nshards=1):
    Q3_OUT.mkdir(exist_ok=True)
    log = Q3_OUT / f"h{worker}.console.log"
    cmd = [sys.executable, str(DRIVE), str(worker), "1",
           str(rank), str(rank), "q3/thick_out", "1", "--only", cert]
    if nshards > 1:
        cmd.extend(["--shard", str(shard), "--nshards", str(nshards)])
    logf = open(log, "a")
    subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT,
                     start_new_session=True)
    extra = f" shard {shard}/{nshards}" if nshards > 1 else ""
    print(f"launch w{worker} rank={rank}{extra} {cert}", flush=True)


def _free_worker(used_w):
    return next(i for i in range(16) if i not in used_w)


def step(max_workers):
    import_q2()
    done = complete_certs()
    lines = ps_args()
    inflight, used_w, shards = running_q3_only(lines)
    reserved = q2_reserved(lines, done)
    n_c = running_thicken_count(lines)
    n_d = running_drive_count(lines)
    leftover = leftover_tasks()
    leftover.sort(key=lambda d: (d["rank"], d["cert"]))
    busy = max(n_c, n_d)
    print(f"complete {len(done)}/{len(leftover)} thicken={n_c} "
          f"drives={n_d} inflight={len(inflight)} reserved={len(reserved)}",
          flush=True)
    if busy >= max_workers:
        return len(done) == len(leftover)
    for cert, (nsh, have) in shards.items():
        if cert in done or busy >= max_workers:
            continue
        have = set(have) | finished_shards(cert)
        rank = next(t["rank"] for t in leftover if t["cert"] == cert)
        for s in range(nsh):
            if s in have or busy >= max_workers:
                continue
            w = _free_worker(used_w)
            launch(cert, rank, w, shard=s, nshards=nsh)
            used_w.add(w)
            busy += 1
    blocked = done | inflight | reserved
    nxt = next((t for t in leftover if t["cert"] not in blocked), None)
    if nxt is None:
        return len(done) == len(leftover)
    if busy >= max_workers:
        return False
    if nxt["rank"] >= 26:
        nsh = 4
        for s in range(nsh):
            if busy >= max_workers:
                break
            w = _free_worker(used_w)
            launch(nxt["cert"], nxt["rank"], w, shard=s, nshards=nsh)
            used_w.add(w)
            busy += 1
        return False
    w = _free_worker(used_w)
    launch(nxt["cert"], nxt["rank"], w)
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true")
    p.add_argument("--max-workers", type=int, default=4)
    p.add_argument("--sleep", type=int, default=30)
    args = p.parse_args()
    os.chdir(ROOT)
    while True:
        done_all = step(args.max_workers)
        if args.once or done_all:
            break
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
