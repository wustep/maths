#!/usr/bin/env python3
"""Sequential replay of the pinned finite producer; not a proof of CLAIM.

No stored row enters the producer. Every completed segment is compared with
the archived row stream afterwards. One child process, constant-memory
comparison, and an exclusive lock keep this lane RAM-light and sequential.
"""
import argparse
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import time

PIN = "a74738deb6d5e0f76887cb36901da08b68dca705"
SOURCE_SHA = "580d0b51165da58d4ca22e16d80a8c3db603dd0d9246f26dd027b5f820bf0808"
ROW = re.compile(r"N (\d+) L12 (0\.\d{12}) GT089 ([01])\n")
SEGMENTS = [
    (a, b, 6, 220, 14, "0.005") for a, b in [
        (690988,690988),(690989,690990),(690991,690995),
        (690996,691010),(691011,691050),(691051,691150),
        (691151,691500),(691501,693000),(693001,697000),
        (697001,707000),(707001,718000),(718001,728999)]
] + [
    (729000,818999,5,200,14,"0.005"),
    (819000,1027999,4,200,14,"0.005"),
    (1028000,1030000,3,240,16,"0.00025"),
    (1030001,1050000,3,240,16,"0.00025"),
    (1050001,1100000,3,220,14,"0.002"),
] + [(a,b,3,220,14,"0.01") for a,b in [
    (1100001,1300000),(1300001,1700000),(1700001,2200000),
    (2200001,2800000),(2800001,3300000),(3300001,3840000)]]

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def archived_rows(root):
    files = list((root / "certificates").glob("*.log.gz"))
    files = [p for p in files if re.fullmatch(r"p\d+_\d+_\d+\.log\.gz", p.name)]
    files.sort(key=lambda p: int(p.name.split("_")[1]))
    require(len(files) == 15, "expected exactly 15 archived shards")
    for path in files:
        with gzip.open(path, "rt") as stream:
            for line in stream:
                if line.startswith("N "):
                    require(ROW.fullmatch(line), f"malformed archived row in {path}")
                    yield line

def check_segment(path, lo, hi, expected):
    next_n = lo
    floor = 10**12
    timings = 0
    banners = []
    with path.open() as stream:
        for line in stream:
            m = ROW.fullmatch(line)
            if m:
                require(int(m[1]) == next_n, f"row coverage at {next_n}")
                require(line == next(expected), f"archived mismatch at {next_n}")
                value = int(m[2].split(".")[1])
                require(value > 0, f"nonpositive floor at {next_n}")
                floor = min(floor, value)
                next_n += 1
            elif re.fullmatch(r"TIMING [0-9.]+ [0-9]+\n", line):
                require(int(line.split()[2]) == hi-lo+1, "timing count")
                timings += 1
            elif line.startswith("TBOX ") or line == "WEIGHT TRIANGLE\n":
                banners.append(line.strip())
            else:
                raise RuntimeError(f"unrecognized output: {line!r}")
    box = "16125/100000 16125/100000" if hi < 729000 else "161250000/1000000000 161250001/1000000000"
    require(banners == [f"TBOX {box}", "WEIGHT TRIANGLE"], "parameter banners")
    require(next_n == hi+1 and timings == 1, "incomplete segment")
    return floor

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root, binary, output = (p.resolve() for p in (args.upstream,args.binary,args.output))
    require(subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip() == PIN, "upstream pin")
    require(sha(root/"src/lemma_sweep_p235711.c") == SOURCE_SHA, "producer source hash")
    output.mkdir(parents=True,exist_ok=True)
    with (output/".lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        expected = archived_rows(root)
        report = {"claim_certified":False,"pin":PIN,"source_sha256":SOURCE_SHA,
                  "binary_sha256":sha(binary),"segments":[]}
        for lo,hi,mode,prec,order,hw in SEGMENTS:
            path = output/f"N{lo}-{hi}.txt"
            t = [16125,16125,100000] if mode == 6 else [161250000,161250001,1000000000]
            command = [str(binary),str(lo),str(hi),*map(str,t),"350708","10000000",
                       str(mode),str(prec),str(order),hw,"t"]
            started = time.monotonic()
            reused = path.exists()
            if not reused:
                partial = path.with_suffix(".partial")
                print(f"RUN {lo}..{hi}",flush=True)
                with partial.open("w") as stream:
                    subprocess.run(command,stdout=stream,check=True,preexec_fn=lambda: os.nice(10))
                partial.rename(path)
            floor = check_segment(path,lo,hi,expected)
            entry = {"first_N":lo,"last_N":hi,"rows":hi-lo+1,"floor_1e12":floor,
                     "sha256":sha(path),"command":command,"reused":reused,
                     "wall_seconds":round(time.monotonic()-started,3),
                     "children_maxrss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
            report["segments"].append(entry)
            report["rows_regenerated"] = sum(s["rows"] for s in report["segments"])
            (output/"progress.json").write_text(json.dumps(report,indent=2)+"\n")
            print(f"MATCH {lo}..{hi}: {entry['rows']} rows; floor={floor}/10^12; wall={entry['wall_seconds']}s",flush=True)
        require(next(expected,None) is None,"extra archived rows")
        require(report["rows_regenerated"] == 3149013,"global row count")
        print("FULL FINITE REPLAY MATCH; independent implementation and analytic review still required",flush=True)

if __name__ == "__main__":
    main()
