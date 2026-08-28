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
    if not Q3_OUT.exists():
        return have
    for path in sorted(Q3_OUT.glob("*.jsonl")):
        if path.name.endswith("_novel.jsonl"):
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("kind") != "tri_done":
                continue
            if rec.get("nshards", 1) != 1:
                continue
            exp = 46 * (1 << rec["rank"])
            if rec.get("complete") and rec.get("evals") == exp:
                have.add(rec["cert"])
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


def running_q3_only(lines):
    certs = set()
    workers = set()
    for ln in lines:
        if "q3/thick_drive.py" not in ln:
            continue
        parts = ln.split()
        if "--only" in parts:
            i = parts.index("--only")
            if i + 1 < len(parts):
                certs.add(parts[i + 1])
        try:
            idx = parts.index("q3/thick_drive.py")
            workers.add(int(parts[idx + 1]))
        except (ValueError, IndexError):
            pass
    return certs, workers


def q2_reserved(lines, done):
    reserved = set()
    tasks = [t for t in json.loads(SPAN.read_text())
             if 21 <= t["rank"] <= 22]
    tasks.sort(key=lambda d: (d["rank"], d["cert"]))
    for ln in lines:
        if "q2/thick_drive.py" not in ln:
            continue
        parts = ln.split()
        try:
            idx = parts.index("q2/thick_drive.py")
            w = int(parts[idx + 1])
            nw = int(parts[idx + 2])
            lo = int(parts[idx + 3])
            hi = int(parts[idx + 4])
        except (ValueError, IndexError):
            continue
        mine = [d for i, d in enumerate(tasks)
                if lo <= d["rank"] <= hi and i % nw == w]
        for d in mine:
            if d["rank"] >= 22 and d["cert"] not in done:
                reserved.add(d["cert"])
    return reserved


def import_q2():
    subprocess.run([sys.executable, str(IMPORT), str(Q2_OUT)], check=False)


def launch(cert, rank, worker):
    Q3_OUT.mkdir(exist_ok=True)
    log = Q3_OUT / f"h{worker}.console.log"
    cmd = [sys.executable, str(DRIVE), str(worker), "1",
           str(rank), str(rank), "q3/thick_out", "1", "--only", cert]
    logf = open(log, "a")
    subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT,
                     start_new_session=True)
    print(f"launch w{worker} rank={rank} {cert}", flush=True)


def step(max_workers):
    import_q2()
    done = complete_certs()
    lines = ps_args()
    inflight, used_w = running_q3_only(lines)
    reserved = q2_reserved(lines, done)
    n_c = running_thicken_count(lines)
    leftover = leftover_tasks()
    leftover.sort(key=lambda d: (d["rank"], d["cert"]))
    print(f"complete {len(done)}/{len(leftover)} thicken={n_c} "
          f"inflight={len(inflight)} reserved={len(reserved)}",
          flush=True)
    if n_c >= max_workers:
        return len(done) == len(leftover)
    blocked = done | inflight | reserved
    nxt = next((t for t in leftover if t["cert"] not in blocked), None)
    if nxt is None:
        return len(done) == len(leftover)
    worker = next(i for i in range(16) if i not in used_w)
    launch(nxt["cert"], nxt["rank"], worker)
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
