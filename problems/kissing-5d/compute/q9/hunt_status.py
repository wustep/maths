#!/usr/bin/env python3
"""Snapshot the live leftover SAT hunts in this folder."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

CERTS = Path(__file__).resolve().parent / "certs"


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
        "interval": "40 <= tau5 <= 44",
        "k30": {
            "cnf": _sz(CERTS / "five_k30_n0_5.cnf"),
            "meta": _sz(CERTS / "five_k30_n0_5.cnf.json"),
            "cadical_log": _sz(CERTS / "five_k30_n0_5.cadical.log"),
            "kissat_log": _sz(CERTS / "five_k30_n0_5.kissat.log"),
            "drat": _sz(CERTS / "five_k30_n0_5.native.drat"),
            "sat": _sz(CERTS / "five_k30_n0_5.sat.json"),
        },
        "global": {
            "cnf": _sz(CERTS / "n1_k19_star5_no21_no13.cnf"),
            "meta": _sz(CERTS / "n1_k19_star5_no21_no13.cnf.json"),
            "cadical_log": _sz(CERTS / "n1_k19_star5_no21_no13.cadical.log"),
            "kissat_log": _sz(CERTS / "n1_k19_star5_no21_no13.kissat.log"),
            "drat": _sz(CERTS / "n1_k19_star5_no21_no13.native.drat"),
            "sat": _sz(CERTS / "n1_k19_star5_no21_no13.sat.json"),
        },
        "code41": _sz(CERTS / "code41.json"),
        "loadavg": os.getloadavg(),
    }
    out = CERTS / "hunt_status.json"
    out.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
