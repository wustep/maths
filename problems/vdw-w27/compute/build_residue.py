#!/usr/bin/env python3
"""Reconstruct the p=617 quadratic-residue certificate and try +1/+2.

Writes:
  cycle_617.txt          cyclic coloring of Z/617Z (01)
  coloring_3703.txt      6 copies + one extra (published length)
  coloring_3702.txt      6 copies, no extra
  extend_try.json        whether 3704 can be appended in either color
"""

from __future__ import annotations

import json
from pathlib import Path

from vdw import (
    can_color_extension,
    first_mono_ap,
    format_ab,
    max_monochrome_run,
    quadratic_residue_cycle,
    repeat_cycle,
)

HERE = Path(__file__).resolve().parent
P = 617


def choose_extra(cycle: list[int]) -> int:
    """Color that does not complete the residue-class 7-AP of difference P."""
    # Positions 1, 1+P, ..., 1+6P live in [1, 6P+1] = [1, 3703].
    # After 6 copies of the cycle (0-based [0, 3701]), index 3702 is the extra
    # and is congruent to 3702 % 617 = 3702 - 5*617 = 3702 - 3085 = 617 ≡ 0.
    # So the extra sits on the 0-class. The 7-AP of 0-class points in
    # [0, 3702] is 0,617,...,3702. Those must not be monochromatic, so the
    # extra (index 3702) must oppose cycle[0].
    return 1 - cycle[0]


def main() -> None:
    reports = []
    for zero in (0, 1):
        cycle = quadratic_residue_cycle(P, zero_color=zero)
        run = max_monochrome_run(cycle, cyclic=True)
        cyclic_hit = first_mono_ap(cycle, k=7, cyclic=True)
        reports.append(
            {
                "zero_color": zero,
                "max_cyclic_run": run,
                "cyclic_7ap": None
                if cyclic_hit is None
                else {"start": cyclic_hit[0], "diff": cyclic_hit[1]},
            }
        )

    # Prefer the zero-color that is cyclically 7-AP-free.
    cycle = None
    zero_used = None
    for zero in (0, 1):
        cand = quadratic_residue_cycle(P, zero_color=zero)
        if first_mono_ap(cand, k=7, cyclic=True) is None:
            cycle = cand
            zero_used = zero
            break
    if cycle is None:
        # Fall back to zero=0 and still emit the linear 6-fold coloring.
        cycle = quadratic_residue_cycle(P, zero_color=0)
        zero_used = 0

    linear_3702 = repeat_cycle(cycle, 6)
    extra = choose_extra(cycle)
    linear_3703 = linear_3702 + [extra]

    (HERE / "cycle_617.txt").write_text(format_ab(cycle) + "\n", encoding="ascii")
    (HERE / "coloring_3702.txt").write_text(format_ab(linear_3702) + "\n", encoding="ascii")
    (HERE / "coloring_3703.txt").write_text(format_ab(linear_3703) + "\n", encoding="ascii")

    ext_3703 = can_color_extension(linear_3702, k=7)
    ext_3704 = can_color_extension(linear_3703, k=7)

    hit_3702 = first_mono_ap(linear_3702, k=7)
    hit_3703 = first_mono_ap(linear_3703, k=7)

    payload = {
        "prime": P,
        "zero_color": zero_used,
        "cycle_reports": reports,
        "coloring_3702_ok": hit_3702 is None,
        "coloring_3703_ok": hit_3703 is None,
        "extra_color": extra,
        "append_to_3702": ext_3703,
        "append_to_3703": ext_3704,
        "files": ["cycle_617.txt", "coloring_3702.txt", "coloring_3703.txt"],
    }
    (HERE / "extend_try.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
