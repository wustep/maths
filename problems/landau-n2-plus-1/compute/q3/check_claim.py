#!/usr/bin/env python3
"""run_all.sh exit 0 only if the CLAIM integers hold."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WOLF_16 = 3_954_181
P2 = 12_172_983
NMAX = 100_000_000


def main() -> None:
    data = json.loads((HERE / "n2p1.json").read_text())
    vok = json.loads((HERE / "verify_ok.json").read_text())
    if int(data["n_max"]) != NMAX:
        sys.exit(f"n_max {data['n_max']} != {NMAX}")
    if int(data["count_prime"]) != WOLF_16:
        sys.exit(f"count_prime {data['count_prime']} != Wolf π_q(10^16)={WOLF_16}")
    if int(data["unsplit"]) != 0:
        sys.exit(f"unsplit {data['unsplit']}")
    mismatches = [row for row in data["wolf_A083844"] if not row["match"]]
    if mismatches:
        sys.exit(f"Wolf mismatch {mismatches}")
    row16 = next(r for r in data["wolf_A083844"] if int(r["x"]) == 10**16)
    if int(row16["pi_q"]) != WOLF_16:
        sys.exit(f"π_q(10^16) stored {row16['pi_q']}")
    if int(vok["extra"]) or int(vok["missing"]) or int(vok["complete_miss"]) or int(vok["complete_extra"]):
        sys.exit(f"C verifier holes {vok}")
    if int(vok["primes_claimed"]) != WOLF_16 or int(vok["primes_found"]) != WOLF_16:
        sys.exit(f"C verifier prime count {vok}")
    if int(data["count_p2_omega_eq_2_composite"]) != P2:
        sys.exit(f"count_p2 {data['count_p2_omega_eq_2_composite']} != {P2}")
    if int(vok["p2_rows"]) != P2:
        sys.exit("C verifier P2 count disagrees with CLAIM")
    print(
        f"CLAIM OK: primes={WOLF_16} p2={P2} "
        f"Wolf π_q(10^16)={WOLF_16}"
    )


if __name__ == "__main__":
    main()
