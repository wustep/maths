#!/usr/bin/env python3
"""Replay the claimed finite facts.  Does not re-enumerate 4e9 words.

Checks:
  1. Independent Ulam prefix matches OEIS A002858 (10 000 terms).
  2. Winning L=16/21/22 words are admissible and have the claimed F2.
  3. Those F2 beat 1.454 (and the tighter rationals) by integer comparison.
  4. Reported nwords equal the closed admissible-language count.
  5. Independent Python enumeration at L=16 recovers the same (word, F2).
  6. a_n ≤ (1443/1000)^n on the first 200 terms (the only possible small-n risk).
  7. Steinerberger cosine sign pattern on the first 5 000 terms.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from certify_bound import certify
from cs_matrices import count_admissible
from search_F_python import enumerate_F
from ulam import ulam_first
from verify_prefix import load_bfile, BFILE

HERE = Path(__file__).resolve().parent


def check_target(seq, num: int, den: int = 1000):
    pn = pd = 1
    fails = []
    for n, a in enumerate(seq, 1):
        pn *= num
        pd *= den
        if a * pd > pn:
            fails.append(n)
    return fails


def main() -> None:
    report = {"ok": True, "checks": []}

    def record(name, ok, detail=None):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok:
            report["ok"] = False
        print(("OK  " if ok else "FAIL"), name, detail or "")

    published = load_bfile(BFILE)
    got = ulam_first(len(published))
    record("oeis_bfile", published == got, {"terms": len(published), "last": got[-1]})

    cases = [
        ("2313131131311313", 10379520, "1.452"),
        ("231313113113131311313", 1579869184, "1.443"),
        ("2313131131313131311313", 4316282880, "1.442"),
    ]
    for word, nwords, tag in cases:
        rec = certify([int(c) for c in word], nwords)
        record(
            f"certify_L{rec['L']}",
            rec["nwords_match"] and rec["beats_1.454_exact"],
            {
                "F2": rec["F2"],
                "CF": rec["CF_float"],
                "beats_1.454": rec["beats_1.454_exact"],
                "beats_" + tag: rec[f"beats_{tag}_exact"],
                "nwords": nwords,
                "count": count_admissible(rec["L"]),
            },
        )

    py16 = enumerate_F(16)
    record(
        "python_enum_L16",
        py16["max_F2"] == 150408 and py16["wordF"] == "2313131131311313",
        py16,
    )

    seq200 = ulam_first(200)
    f443 = check_target(seq200, 1443)
    f442 = check_target(seq200, 1442)
    record("prefix_1.443_n200", f443 == [], {"fails": f443})
    record("prefix_1.442_n200_only3", f442 == [3], {"fails": f442})

    # Spectral replay on a shorter prefix.
    seq5k = ulam_first(5000)
    alpha = 2.5714474995
    pos = [a for a in seq5k if math.cos(alpha * a) >= 0]
    record(
        "steinerberger_cos_sign_5k",
        set(pos) <= {2, 3, 47, 69} and {2, 3, 47, 69} <= set(seq5k),
        {"positive": pos, "mean_cos": sum(math.cos(alpha * a) for a in seq5k) / len(seq5k)},
    )

    out = HERE / "verify_all.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out)
    if not report["ok"]:
        raise SystemExit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
