"""Replay Ellis arXiv:2211.12401: Gilmer Conjecture 1 is false.

Gilmer §5 hoped that H(A∪B)+D(A∪B||A)>H(A) whenever every
coordinate has mean < 1/2, which would have given Frankl 1/2.
Ellis gives an n=2 distribution with the functional already
negative at mean = 1/2, and a perturbation with mean < 1/2.

This is why a KL-corrected 2-sample argument is not a path to 1/2
without extra assumptions on A.  Sawin independently refuted the
same conjecture (Gilmer v2 note, 28 Nov 2022).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

LN2 = math.log(2)


def functional(x: float) -> float:
    """Ellis's closed form at the symmetric 4-atom law, mean = 1/2."""
    return (0.5 + 2 * x * x - 2 * x) * math.log(1.0 / x) / LN2 + (
        -0.5 - 2 * x * x + 2 * x
    ) * math.log(1.0 / (0.5 - x)) / LN2


def from_atoms(p_empty, p1, p2, p12):
    """Direct H(A∪B)+D(A∪B||A)-H(A) = Σ q log2(1/p) − Σ p log2(1/p)."""
    p = [p_empty, p1, p2, p12]
    # A∪B law
    q_empty = p_empty * p_empty
    q1 = p_empty * p1 + p1 * p_empty + p1 * p1
    q2 = p_empty * p2 + p2 * p_empty + p2 * p2
    q12 = 1.0 - q_empty - q1 - q2
    q = [q_empty, q1, q2, q12]
    acc = 0.0
    for qi, pi in zip(q, p):
        if pi <= 0.0:
            raise ValueError("p atom")
        acc += (qi - pi) * math.log(1.0 / pi) / LN2
    mean1 = p1 + p12
    mean2 = p2 + p12
    return acc, mean1, mean2, q


def main():
    x = 0.3
    closed = functional(x)
    direct, m1, m2, q = from_atoms(x, 0.5 - x, 0.5 - x, x)
    # perturbation with frequencies strictly below 1/2
    eps = 1e-3
    pert, pm1, pm2, pq = from_atoms(x, 0.5 + eps - x, 0.5 + eps - x, x - 2 * eps)

    report = {
        "source": "https://arxiv.org/abs/2211.12401",
        "x": x,
        "closed_form": closed,
        "direct": direct,
        "means_unperturbed": [m1, m2],
        "q_unperturbed": q,
        "matches_ellis_below_-0.04": closed < -0.04 and direct < -0.04,
        "closed_minus_direct": closed - direct,
        "perturbed": {
            "eps": eps,
            "functional": pert,
            "means": [pm1, pm2],
            "means_below_half": pm1 < 0.5 and pm2 < 0.5,
            "still_negative": pert < 0.0,
        },
        "note": (
            "Gilmer Conjecture 1 fails.  The KL+entropy 2-sample "
            "strengthening does not give Frankl 1/2."
        ),
    }
    path = Path(__file__).resolve().parent / "certs" / "ellis.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["matches_ellis_below_-0.04"]:
        raise SystemExit(1)
    if abs(closed - direct) > 1e-12:
        raise SystemExit(1)
    if not report["perturbed"]["means_below_half"] or not report["perturbed"]["still_negative"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
