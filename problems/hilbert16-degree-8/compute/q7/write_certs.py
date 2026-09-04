#!/usr/bin/env python3
"""Write nest certificates from q7 jsonl summaries.

Does not write new_schemes.json. A collection-space HIT is not a
T-curve until verify_new.py accepts a stored certificate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = HERE / "certs"


def last_summary(path: Path):
    last = None
    schemes = []
    hits = 0
    news = 0
    if not path.exists():
        return None, [], 0, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("kind") == "summary":
            last = rec
        if rec.get("kind") in ("scheme", "NEW", "HIT", "pn193", "WITNESS"):
            if rec.get("scheme"):
                schemes.append(rec["scheme"])
        if rec.get("kind") == "HIT":
            hits += 1
        if rec.get("kind") == "NEW" or rec.get("new_scheme"):
            news += 1
    return last, sorted(set(schemes)), hits, news


def write(name, payload):
    CERT.mkdir(exist_ok=True)
    dest = CERT / name
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", dest.relative_to(HERE.parent))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("odd_skel5", "all"):
        path = HERE / "certs" / "odd_skel5.json"
        if path.exists():
            print("odd_skel5 already at", path.relative_to(HERE.parent))
    if which in ("even", "all"):
        for path in sorted((HERE / "certs").glob("even_component_*.json")):
            print("even component cert", path.relative_to(HERE.parent))


if __name__ == "__main__":
    main()
