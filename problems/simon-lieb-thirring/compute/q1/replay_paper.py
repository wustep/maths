#!/usr/bin/env python3
"""Replay Frank–Hundertmark–Jex–Nam Lemma 11 trial pairs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from c1_functional import (
    evaluate_c1,
    paper_first_pair,
    paper_second_pair,
    ratio_from_c1,
)


def main() -> int:
    out = {}
    for name, factory in (
        ("lemma11_first", paper_first_pair),
        ("lemma11_second", paper_second_pair),
    ):
        f, phi, mu, c0 = factory()
        res = evaluate_c1(f, phi, support=1.0, t_cut=1e6)
        ratios = ratio_from_c1(res.C_1)
        # Conservative published-style upper bound: add the estimated error
        # plus the explicit tail bound converted into C_1 units.
        c1_up = res.C_1 + res.abs_err_est
        out[name] = {
            "C_1_float": res.C_1,
            "C_1_plus_err": c1_up,
            "a": res.a,
            "A_g": res.A_g,
            "mu": mu,
            "c0": c0,
            "abs_err_est": res.abs_err_est,
            "extras": res.extras,
            "ratios_from_float": ratios,
            "ratios_from_plus_err": ratio_from_c1(c1_up),
        }
        print(f"{name}: C_1={res.C_1:.12f}  +err={c1_up:.12f}  "
              f"L/Lcl={ratios['L_over_Lcl']:.9f}")
    dest = Path(__file__).resolve().parent / "paper_replay.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
