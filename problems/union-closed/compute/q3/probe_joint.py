"""Failed q3 handle: joint entropy of two unions sharing one sample.

For X,Y,Z iid Bern(b), set U=X OR Y and V=X OR Z.  The four output
probabilities are explicit.  The interior solution of

    H(U,V) = 2 h(b)

is below the current ray constant, so this independent shared-union
inequality cannot improve q1.  This is a recorded failure, not a bound.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import findroot, log, mp, mpf, nstr

mp.dps = 80
LN2 = log(2)
HERE = Path(__file__).resolve().parent
CLAIMED = mpf("0.38305")


def entropy(probs):
    return -sum(p * log(p) / LN2 for p in probs if p > 0)


def h(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return entropy((p, 1 - p))


def joint_entropy(b):
    b = mpf(b)
    q00 = (1 - b) ** 3
    q10 = b * (1 - b) ** 2
    q01 = q10
    q11 = 1 - q00 - q10 - q01
    return entropy((q00, q10, q01, q11))


def gap(b):
    b = mpf(b)
    return joint_entropy(b) - 2 * h(b)


def main():
    root = findroot(gap, mpf("0.3437"))
    eps = mpf("1e-6")
    report = {
        "protocol": "(X OR Y, X OR Z) for iid Bernoulli inputs",
        "interior_equality_b": nstr(root, 40),
        "residual": nstr(gap(root), 12),
        "gap_1e_6_below": nstr(gap(root - eps), 20),
        "gap_1e_6_above": nstr(gap(root + eps), 20),
        "claimed_c": float(CLAIMED),
        "equality_below_claimed": bool(root < CLAIMED),
        "note": (
            "failed handle: the independent shared-union joint-entropy "
            "inequality reaches equality below the q1/q3 ray constant"
        ),
    }
    report["all_ok"] = bool(
        abs(gap(root)) < mpf("1e-60")
        and gap(root - eps) > 0
        and gap(root + eps) < 0
        and root < CLAIMED
    )
    path = HERE / "certs" / "joint_star.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
