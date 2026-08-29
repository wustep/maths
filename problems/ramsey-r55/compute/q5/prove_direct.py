#!/usr/bin/env python3
"""Build one leftover orbit instance and attempt a kissat DRAT certificate."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from cases import all_cases


ROOT = Path(__file__).resolve().parent
Q2 = ROOT.parent / "q2"
ENCODER = Q2 / "orbit_sat.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


GITHUB_BLOB_LIMIT = 100 * 1024 * 1024


def store_compressed_proof(src: Path, stem: Path) -> Path:
    """gzip -9, or xz -9 when gzip would exceed GitHub's 100MB blob limit."""
    gz = Path(str(stem) + ".drat.gz")
    xz = Path(str(stem) + ".drat.xz")
    with src.open("rb") as incoming, gz.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as out:
            shutil.copyfileobj(incoming, out)
    if gz.stat().st_size < GITHUB_BLOB_LIMIT:
        if xz.exists():
            xz.unlink()
        return gz
    gz.unlink()
    result = subprocess.run(
        ["xz", "-9", "-T", "1", "-c", str(src)],
        check=True,
        capture_output=True,
    )
    xz.write_bytes(result.stdout)
    return xz


def case_by_name(name: str) -> dict:
    for row in all_cases():
        if row["name"] == name:
            return row
    raise SystemExit(f"unknown case {name}")


def build_cnf(case: dict, cnf: Path, cert: Path) -> dict:
    cmd = [
        sys.executable,
        str(ENCODER),
        "--n",
        "43",
        "--p",
        str(case["p"]),
        "--cycles",
        str(case["cycles"]),
        "--fixed-cycle-count",
        str(case["fixed_cycle_count"]),
        "--cnf",
        str(cnf),
        "--cert",
        str(cert),
    ]
    if case["p5_symbreak"]:
        cmd.append("--p5-symbreak")
    else:
        cmd.append("--anchor-symbreak")
    subprocess.run(cmd, check=True)
    build = json.loads(cert.read_text())
    expected = case.get("expected_cnf_sha256")
    if expected and build["cnf_sha256"] != expected:
        raise RuntimeError(
            f"CNF hash mismatch for {case['name']}: "
            f"{build['cnf_sha256']} != {expected}"
        )
    return build


def run_kissat(
    kissat: Path,
    cnf: Path,
    proof: Path,
    log: Path,
    time_limit: int,
    extra: list[str],
) -> tuple[str, int]:
    cmd = [str(kissat), f"--time={time_limit}", *extra, str(cnf), str(proof)]
    started = time.monotonic()
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    log.write_text(result.stdout + result.stderr)
    if result.returncode == 20 and "s UNSATISFIABLE" in result.stdout:
        status = "UNSAT"
    elif result.returncode == 10 and "s SATISFIABLE" in result.stdout:
        status = "SAT"
    else:
        status = "UNKNOWN"
    return status, round(time.monotonic() - started)


def check_drat(
    drat_trim: Path,
    cnf: Path,
    proof: Path,
    log: Path,
    timeout: int,
    extra: list[str] | None = None,
) -> bool:
    cmd = [str(drat_trim), str(cnf), str(proof)]
    if extra:
        cmd.extend(extra)
    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        log.write_text(f"drat-trim timed out after {timeout}s\n")
        return False
    log.write_text(result.stdout + result.stderr)
    return result.returncode == 0 and "s VERIFIED" in result.stdout


def decode_model(case: dict, model_path: Path) -> dict:
    sys.path.insert(0, str(Q2))
    sys.path.insert(0, str(Q2.parent))
    from orbit_sat import OrbitEncoding
    from r55lib import fingerprint, is_ramsey, to_graph6

    obj = OrbitEncoding(43, case["p"], case["cycles"])
    obj.build(
        True,
        case["fixed_cycle_count"],
        False,
        case["p5_symbreak"],
        case["anchor_symbreak"],
    )
    model = [int(tok) for tok in model_path.read_text().split() if tok not in {"0", ""}]
    nbr = obj.decode(model)
    rec = {
        "fingerprint": fingerprint(nbr),
        "graph6": to_graph6(nbr),
        "verified_55": is_ramsey(nbr),
    }
    if not rec["verified_55"]:
        raise RuntimeError(f"{case['name']}: SAT model is not a (5,5,43)-graph")
    return rec


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--kissat", type=Path, default=Q2 / "work" / "kissat-bin")
    parser.add_argument("--drat-trim", type=Path, default=Q2 / "work" / "drat-trim-bin")
    parser.add_argument("--time", type=int, default=180)
    parser.add_argument("--unsat", action="store_true")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--import-proof",
        type=Path,
        help="Skip kissat and check this DRAT against a freshly built CNF",
    )
    args = parser.parse_args()

    case = case_by_name(args.name)
    work = ROOT / "work" / case["name"]
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (ROOT / "certs").mkdir(exist_ok=True)
    (ROOT / "certs" / "proofs").mkdir(exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)

    cnf = work / f"{case['name']}.cnf"
    build_cert = ROOT / "certs" / f"{case['name']}_build.json"
    build = build_cnf(case, cnf, build_cert)

    extra = ["--unsat", f"--seed={args.seed}"] if args.unsat else ["--plain"]
    raw_proof = work / "raw.drat"
    kissat_log = ROOT / "logs" / f"{case['name']}_kissat.txt"
    imported = None
    if args.import_proof:
        imported = args.import_proof.resolve()
        if not imported.is_file():
            raise SystemExit(f"missing import-proof {imported}")
        shutil.copy2(imported, raw_proof)
        status, solve_sec = "UNSAT", 0
        extra = ["--import-proof", str(imported)]
        kissat_log.write_text(f"imported {imported}\n")
    else:
        status, solve_sec = run_kissat(
            args.kissat, cnf, raw_proof, kissat_log, args.time, extra
        )

    record = {
        **case,
        "build": {key: build[key] for key in (
            "cnf_sha256", "nvars", "nclauses", "edge_orbit_vars",
            "five_subset_orbits", "anchor_symbreak", "p5_symbreak",
        ) if key in build},
        "kissat": " ".join([f"--time={args.time}", *extra]),
        "solve_sec": solve_sec,
        "status": status,
    }

    if status == "UNSAT":
        skip_raw_bytes = 200 * 1024 * 1024
        raw_size = raw_proof.stat().st_size if raw_proof.exists() else 0
        check_timeout = max(args.time * 3, 3600)
        trimmed = work / "trimmed.drat"
        if imported is not None:
            stored_src = raw_proof
        else:
            if raw_size >= skip_raw_bytes:
                print(
                    f"{case['name']}: raw DRAT {raw_size} bytes; skip full-DRAT check, trim first",
                    flush=True,
                )
            elif not check_drat(
                args.drat_trim,
                cnf,
                raw_proof,
                ROOT / "logs" / f"{case['name']}_drat.txt",
                timeout=check_timeout,
            ):
                raise RuntimeError(f"{case['name']}: raw DRAT failed to verify")
            try:
                subprocess.run(
                    [str(args.drat_trim), str(cnf), str(raw_proof), "-l", str(trimmed)],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=max(args.time * 3, 7200),
                )
            except subprocess.TimeoutExpired:
                print(
                    f"{case['name']}: trim timed out; store raw if it already verified",
                    flush=True,
                )
            stored_src = trimmed if trimmed.exists() and trimmed.stat().st_size else raw_proof
        if not check_drat(
            args.drat_trim,
            cnf,
            stored_src,
            ROOT / "logs" / f"{case['name']}_drat.txt",
            timeout=check_timeout,
        ):
            raise RuntimeError(f"{case['name']}: stored DRAT failed to verify")
        stored = store_compressed_proof(stored_src, ROOT / "certs" / "proofs" / case["name"])
        record["proof"] = {
            "bytes": stored.stat().st_size,
            "path": str(stored.relative_to(ROOT)),
            "sha256": sha256(stored),
            "verified": True,
        }
        record["proof_verified"] = True
        if imported is not None:
            record["imported_proof"] = str(imported)
    elif status == "SAT":
        # kissat writes a witness into stdout; recover assignment from the proof file
        # if present, otherwise re-solve without a time cap for the model.
        model = work / "model.txt"
        solved = subprocess.run(
            [str(args.kissat), str(cnf)],
            check=False,
            capture_output=True,
            text=True,
        )
        values = []
        for line in solved.stdout.splitlines():
            if line.startswith("v "):
                values.extend(line.split()[1:])
        model.write_text(" ".join(values) + "\n")
        record["model"] = decode_model(case, model)
        record["found_43_graph"] = True

    out = ROOT / "certs" / f"{case['name']}.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "name": case["name"],
        "status": status,
        "solve_sec": solve_sec,
        "nvars": build.get("nvars"),
        "nclauses": build.get("nclauses"),
    }, sort_keys=True), flush=True)
    return 0 if status != "SAT" or record.get("model", {}).get("verified_55") else 2


if __name__ == "__main__":
    raise SystemExit(main())
