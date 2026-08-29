"""Snapshot the live SAT hunts (q8 kissat + leftover q7 cadical)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

CERTS = Path(__file__).resolve().parent / "certs"
Q7 = Path(__file__).resolve().parent.parent / "q7" / "certs"


def _sz(p: Path) -> dict:
    if not p.is_file():
        return {"exists": False, "path": str(p)}
    st = p.stat()
    return {
        "exists": True,
        "path": str(p),
        "bytes": st.st_size,
        "mtime": st.st_mtime,
    }


def main() -> None:
    rec = {
        "t": time.time(),
        "q8": {
            "k30_cnf": _sz(CERTS / "five_k30_n0_5.cnf"),
            "k30_kissat": _sz(CERTS / "five_k30_n0_5.kissat.sat.json"),
            "k30_native": _sz(CERTS / "five_k30_n0_5.sat.json"),
            "k30_drat": _sz(CERTS / "five_k30_n0_5.native.drat"),
            "global_cnf": _sz(CERTS / "n1_k19_star5_no21_no13.cnf"),
            "global_kissat": _sz(CERTS / "n1_k19_star5_no21_no13.kissat.sat.json"),
            "global_native": _sz(CERTS / "n1_k19_star5_no21_no13.sat.json"),
            "global_drat": _sz(CERTS / "n1_k19_star5_no21_no13.native.drat"),
            "code41": _sz(CERTS / "code41.json"),
        },
        "q7_leftover": {
            "k30_drat": _sz(Q7 / "five_k30_n0_5.native.drat"),
            "k30_sat": _sz(Q7 / "five_k30_n0_5.sat.json"),
            "global_drat": _sz(Q7 / "n1_k19_star5.native.drat"),
            "global_sat": _sz(Q7 / "n1_k19_star5.sat.json"),
        },
        "loadavg": os.getloadavg(),
    }
    out = CERTS / "hunt_status.json"
    out.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
