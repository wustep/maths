#!/usr/bin/env python3
"""Replay published constructions and the Halkiewicz matching-conjecture claim."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seymour import (
    all_margins,
    cycle_power,
    directed_cycle,
    empty_graph,
    graph_signature,
    is_matching_missing,
    is_pisa,
    is_seymour_tight,
    lex_product,
    missing_degree_sequence,
    regular_tournament,
)


def report(name: str, out) -> dict:
    sig = graph_signature(out)
    print(
        f"{name}: n={sig['n']} tight={sig['tight']} pisa={sig['pisa']} "
        f"delta={sig['delta']} out={sig['outdegrees']} "
        f"miss_deg={sig['missing_deg']} matching_miss={sig['matching_missing']}"
    )
    return {"name": name, **{k: sig[k] for k in (
        "n", "tight", "pisa", "delta", "outdegrees", "missing_deg",
        "underlying_deg", "matching_missing", "strong", "margins", "missing",
    )}}


def main() -> None:
    rows = []
    # Guo–Kang–Zwaneveld Lemma 2.1
    for n in range(3, 13):
        for k in range(1, n):
            out = cycle_power(n, k)
            tight = is_seymour_tight(out)
            expect = 2 * k < n
            if tight != expect:
                raise SystemExit(f"FAIL cycle_power({n},{k}): tight={tight} expect={expect}")
            if expect and not is_pisa(out):
                raise SystemExit(f"FAIL cycle_power({n},{k}) not Pisa")
    rows.append(report("C7^2", cycle_power(7, 2)))
    rows.append(report("C8^2", cycle_power(8, 2)))
    rows.append(report("C8^3", cycle_power(8, 3)))
    rows.append(report("C9^2", cycle_power(9, 2)))
    rows.append(report("C9^3", cycle_power(9, 3)))
    rows.append(report("C7", directed_cycle(7)))
    rows.append(report("RT7", regular_tournament(7)))
    rows.append(report("C3[E2]", lex_product(directed_cycle(3), empty_graph(2))))
    rows.append(report("C4[E2]", lex_product(directed_cycle(4), empty_graph(2))))
    rows.append(report("C3[E3]", lex_product(directed_cycle(3), empty_graph(3))))

    # Halkiewicz Conjecture 5.1 is already false at n=7: C7^2 has 2-regular missing graph.
    c72 = cycle_power(7, 2)
    assert is_pisa(c72)
    assert missing_degree_sequence(c72) == (2, 2, 2, 2, 2, 2, 2)
    assert not is_matching_missing(c72)
    rows.append({
        "claim": "Halkiewicz Conjecture 5.1 (Pisa => Cn or Kn-matching) fails at n=7",
        "witness": "directed C7^2",
        "missing_deg": list(missing_degree_sequence(c72)),
        "margins": all_margins(c72),
    })

    # C8^2 is a Pisa graph on the first order they did not enumerate.
    c82 = cycle_power(8, 2)
    assert is_pisa(c82)
    assert not is_matching_missing(c82)
    print("C8^2 is a certified Pisa graph outside Cn / Kn-matching.")

    out_path = Path(__file__).resolve().parent / "certs" / "known_constructions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
