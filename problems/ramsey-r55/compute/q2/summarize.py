#!/usr/bin/env python3
"""Collect q2's checked finite results into one certificate."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CERTS = ROOT / "certs"
LOGS = ROOT / "logs"


def load(name: str) -> dict:
    return json.loads((CERTS / name).read_text())


def sha_size(path: Path) -> dict:
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def parse_done(name: str) -> dict:
    text = (LOGS / name).read_text()
    line = next(line for line in reversed(text.splitlines()) if line.startswith("DONE "))
    values: dict[str, object] = {"done": line}
    for key, value in re.findall(r"(\w+)=([^ ]+)", line):
        try:
            values[key] = int(value)
        except ValueError:
            try:
                values[key] = float(value)
            except ValueError:
                values[key] = value
    return values


def proof_ok(log: Path) -> bool:
    return log.exists() and "s VERIFIED" in log.read_text()


def orbit_record(p: int, cycles: int, cert_name: str) -> dict:
    name = f"orbit_n43_p{p}_c{cycles}"
    rec = load(cert_name)
    proof = CERTS / "proofs" / f"{name}.drat.gz"
    log_candidates = [
        LOGS / f"drat_trim_p{p}_c{cycles}.txt",
        LOGS / f"drat_trim_p{p}.txt",
        LOGS / f"replay_drat_p{p}_c{cycles}.txt",
    ]
    rec = {
        "p": p,
        "cycles": cycles,
        "fixed": 43 - p * cycles,
        "status": rec.get("status"),
        "nvars": rec["nvars"],
        "nclauses": rec["nclauses"],
        "cnf_sha256": rec.get("cnf_sha256"),
        "proof_verified": any(proof_ok(path) for path in log_candidates),
        "proof": sha_size(proof),
    }
    return rec


def timeout_record(name: str) -> dict:
    path = LOGS / name
    if not path.exists():
        return {"log": name, "status": "NOT_RUN"}
    text = path.read_text(errors="replace")
    status = "UNKNOWN"
    if "s UNSATISFIABLE" in text:
        status = "UNSAT"
    elif "s SATISFIABLE" in text:
        status = "SAT"
    return {"log": name, "status": status, "tail": text.splitlines()[-8:]}


def main() -> int:
    orbit_specs = [
        (11, 1, "orbit_n43_p11_c1.json"),
        (11, 2, "orbit_n43_p11_c2.json"),
        (11, 3, "orbit_n43_p11.json"),
        (13, 1, "orbit_n43_p13_c1.json"),
        (13, 2, "orbit_n43_p13_c2.json"),
        (17, 1, "orbit_n43_p17_c1.json"),
        (17, 2, "orbit_n43_p17.json"),
        (19, 1, "orbit_n43_p19_c1.json"),
        (19, 2, "orbit_n43_p19.json"),
        (23, 1, "orbit_n43_p23.json"),
    ]
    orbit = [orbit_record(*spec) for spec in orbit_specs]
    repair = load("repair_r6.json")
    repair_proof = CERTS / "proofs" / "repair_r6.drat.gz"
    rec = {
        "published_interval": [43, 46],
        "interval_moved": False,
        "any_43_graph": False,
        "encoder_selftest": load("encoder_selftest.json"),
        "degree_obstructions": load("degree_obstructions.json"),
        "two_edit": {
            "classification": parse_done("two_edit_classify.txt"),
            "extension": parse_done("two_edit_extend.txt"),
        },
        "prime_automorphism_cycle_types": orbit,
        "repair": {
            "radius": repair["radius"],
            "source_objective": repair["source_objective"],
            "status": repair["status"],
            "nvars": repair["nvars"],
            "nclauses": repair["nclauses"],
            "cnf_sha256": repair["cnf_sha256"],
            "proof_verified": proof_ok(LOGS / "drat_trim_repair_r6.txt")
            or proof_ok(LOGS / "replay_drat_repair_r6.txt"),
            "proof": sha_size(repair_proof),
        },
        "small_prime_runs": [
            timeout_record("kissat_p7_sb.txt"),
            timeout_record("kissat_p5_sb.txt"),
            timeout_record("kissat_p3_k6_sb.txt"),
            timeout_record("kissat_p3_k7_sb.txt"),
            timeout_record("kissat_p2_k9_sb.txt"),
            timeout_record("kissat_p2_k10_sb.txt"),
        ],
        "note": (
            "No endpoint moved. DRAT-verified UNSAT claims cover the listed "
            "cycle types and the radius-6 ball only. Degree obstructions cover "
            "additional listed cycle types. Small-prime timeouts remain UNKNOWN."
        ),
    }
    if not rec["encoder_selftest"]["all_ok"]:
        raise SystemExit("encoder self-test failed")
    if not all(row["proof_verified"] and row["status"] == "UNSAT" for row in orbit):
        raise SystemExit("an orbit proof is missing or unverified")
    if not rec["repair"]["proof_verified"] or rec["repair"]["status"] != "UNSAT":
        raise SystemExit("repair proof is missing or unverified")
    out = CERTS / "q2_summary.json"
    out.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, sort_keys=True))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
