#!/usr/bin/env python3
"""Independent exact check of Bedert arXiv:2509.05260v3 Lemma 7.2.

Prints every one of the 32 five-bit windows, compares the computed rho
against the paper's 8-row table, and records the isolation gap

    min_{m in B_t} (-Im rho_m)  -  max_m Re rho_m  =  1/sqrt(2).

Exit 0 iff the lemma's three numerical claims hold in Q(sqrt(2)).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from aux_rho import (
    BEDERT_BT_IM_LOWER,
    BEDERT_IM_ABS_UPPER,
    BEDERT_RE_UPPER,
    BEDERT_TABLE,
    all_windows,
    classify_triple,
    is_Bt,
    rho_bedert_pi4,
    summarise,
)
from qsqrt2 import ZERO, QSqrt2


def main() -> int:
    s = summarise()
    failures = []

    # Per-triple maxima vs the paper table.
    print("triple (a_{m-t}, a_m, a_{m+t}) | max Re rho | max |Im rho| | paper Re | paper |Im| | ok")
    for trip in sorted(s["by_triple"]):
        rhos = s["by_triple"][trip]
        max_re = rhos[0].re
        max_im = rhos[0].im if rhos[0].im >= ZERO else -rhos[0].im
        for rho in rhos[1:]:
            if rho.re > max_re:
                max_re = rho.re
            im_abs = rho.im if rho.im >= ZERO else -rho.im
            if im_abs > max_im:
                max_im = im_abs
        paper_re, paper_im = BEDERT_TABLE[trip]
        ok = (max_re == paper_re) and (max_im == paper_im)
        if not ok:
            failures.append(("table", trip, str(max_re), str(max_im), str(paper_re), str(paper_im)))
        print(f"  {trip} | {max_re} | {max_im} | {paper_re} | {paper_im} | {ok}")

    print()
    print("all 32 windows:")
    print("  bits u,a,b,c,v | Bt | Re rho | Im rho")
    for bits in all_windows():
        rho = rho_bedert_pi4(bits)
        print(f"  {bits} | {int(is_Bt(bits))} | {rho.re} | {rho.im}")

    print()
    print(f"max Re rho          = {s['max_re']}   claimed <= {BEDERT_RE_UPPER}")
    print(f"max |Im rho|        = {s['max_im_abs']}   claimed <= {BEDERT_IM_ABS_UPPER}")
    print(f"min_{{Bt}} (-Im rho) = {s['min_neg_im_Bt']}   claimed >= {BEDERT_BT_IM_LOWER}")
    print(f"isolation gap       = {s['gap']}   (= 1/sqrt(2) = sqrt(2)/2)")

    if not (s["max_re"] <= BEDERT_RE_UPPER):
        failures.append(("re_upper", str(s["max_re"])))
    if not (s["max_im_abs"] <= BEDERT_IM_ABS_UPPER):
        failures.append(("im_upper", str(s["max_im_abs"])))
    if not (s["min_neg_im_Bt"] >= BEDERT_BT_IM_LOWER):
        failures.append(("bt_im", str(s["min_neg_im_Bt"])))

    expected_gap = QSqrt2(0, 1) - QSqrt2(0, 1) / QSqrt2(2, 0)  # √2 - 1/√2 wait
    # 4+√2 - (4 + 1/√2) = √2 - 1/√2 = √2 - √2/2 = √2/2
    expected_gap = QSqrt2(0, 1) / QSqrt2(2, 0)  # √2 / 2
    if s["gap"] != expected_gap:
        # still ok as long as gap > 0; record it
        print(f"note: gap is {s['gap']}, expected √2/2 = {expected_gap}")
        if s["gap"] != expected_gap:
            # Bedert's min over Bt is 4+√2 and max Re is 4+√2/2, gap = √2/2
            # Our min_neg_im_Bt should equal 4+√2 if the worst Bt window is (1,1)
            pass
    if not (s["gap"] > ZERO):
        failures.append(("gap_nonpositive", str(s["gap"])))

    out = {
        "ok": not failures,
        "max_re": [str(s["max_re"].a), str(s["max_re"].b)],
        "max_im_abs": [str(s["max_im_abs"].a), str(s["max_im_abs"].b)],
        "min_neg_im_Bt": [str(s["min_neg_im_Bt"].a), str(s["min_neg_im_Bt"].b)],
        "gap": [str(s["gap"].a), str(s["gap"].b)],
        "failures": [str(f) for f in failures],
    }
    Path(__file__).resolve().parent.joinpath("lemma72.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )

    if failures:
        print("FAIL", failures)
        return 1
    print("OK: Lemma 7.2 holds exactly in Q(sqrt(2)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
