#!/usr/bin/env python3
"""SAT search for an almost complement-symmetric seven-coloring.

For a target interval [1, N], ordinary complement symmetry identifies x with
N+1-x.  When 3 divides N+1, the orbit {(N+1)/3, 2(N+1)/3} must be split,
since the smaller point added to itself is the larger one.  This script encodes
exactly that Fredricksen--Sweet notion of symmetry and uses a bundled PySAT
solver.  The published 1680 coloring can be supplied as phase guidance; it is
never asserted as a constraint unless --freeze-prefix is requested.
"""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver

from search_shifted_sat import verify


OLD_1680_HALF: tuple[tuple[int, ...], ...] = (
    (
        1, 15, 17, 38, 52, 56, 80, 82, 85, 87, 89, 96, 98, 109, 129,
        133, 135, 140, 142, 149, 151, 153, 158, 182, 184, 186, 190, 200,
        206, 208, 230, 237, 239, 241, 250, 253, 255, 261, 274, 283, 308,
        318, 320, 334, 336, 352, 371, 373, 389, 391, 415, 424, 428, 444,
        446, 470, 477, 479, 486, 488, 493, 499, 512, 521, 523, 525, 532,
        541, 543, 546, 565, 567, 572, 574, 576, 583, 590, 596, 627, 629,
        643, 664, 666, 682, 684, 708, 717, 737, 750, 759, 761, 768, 770,
        779, 781, 800, 803, 810, 812, 814, 816, 821, 834,
    ),
    (
        2, 29, 36, 42, 53, 67, 73, 86, 91, 100, 117, 124, 138, 147, 155,
        171, 188, 202, 209, 235, 240, 268, 280, 290, 291, 299, 306, 311,
        317, 324, 337, 350, 355, 361, 362, 383, 388, 393, 394, 421, 426,
        432, 443, 459, 473, 476, 481, 490, 506, 514, 528, 537, 544, 555,
        561, 575, 588, 594, 599, 621, 626, 658, 659, 665, 670, 681, 696,
        697, 703, 714, 728, 740, 747, 752, 778, 785, 799, 832,
    ),
    (
        3, 8, 10, 12, 21, 23, 28, 30, 32, 50, 61, 63, 68, 70, 72, 79,
        81, 83, 99, 101, 103, 105, 110, 112, 114, 121, 123, 130, 132,
        134, 141, 143, 150, 152, 154, 156, 161, 163, 165, 174, 176, 183,
        185, 194, 196, 201, 203, 205, 214, 221, 223, 232, 236, 238, 243,
        245, 252, 254, 256, 258, 265, 267, 272, 276, 278, 285, 287, 294,
        296, 303, 305, 307, 314, 323, 325, 327, 329, 338, 345, 347, 356,
        358, 367, 374, 376, 380, 385, 387, 396, 398, 405, 407, 409, 420,
        427, 431, 438, 440, 447, 449, 456, 458, 460, 465, 467, 469, 471,
        478, 480, 487, 489, 491, 498, 507, 509, 511, 513, 518, 520, 522,
        529, 531, 540, 542, 547, 551, 558, 560, 562, 569, 573, 578, 580,
        582, 591, 593, 600, 602, 609, 611, 613, 620, 622, 624, 631, 633,
        640, 644, 649, 662, 671, 673, 680, 691, 693, 695, 700, 706, 711,
        713, 715, 726, 731, 733, 735, 744, 746, 753, 757, 762, 773, 775,
        777, 782, 784, 793, 795, 797, 802, 806, 808, 813, 815, 817, 822,
        824, 826, 828, 835, 837,
    ),
    (
        4, 11, 18, 20, 33, 34, 35, 62, 64, 65, 71, 88, 115, 118, 120,
        167, 168, 170, 173, 217, 218, 220, 227, 242, 249, 270, 271, 273,
        295, 297, 300, 302, 309, 312, 326, 339, 348, 353, 370, 379, 406,
        408, 411, 423, 425, 452, 455, 461, 503, 505, 508, 533, 550, 564,
        577, 605, 608, 617, 632, 646, 647, 661, 663, 690, 699, 729, 741,
        743, 780, 788, 789, 796, 811,
    ),
    (
        5, 14, 39, 46, 47, 49, 102, 104, 106, 136, 139, 189, 191, 192,
        199, 224, 233, 259, 262, 277, 284, 288, 315, 321, 340, 341, 342,
        343, 344, 359, 377, 403, 412, 429, 430, 437, 439, 441, 462, 474,
        494, 496, 497, 515, 526, 527, 538, 549, 556, 559, 579, 581, 597,
        612, 614, 615, 623, 641, 650, 667, 668, 675, 676, 678, 679, 694,
        709, 712, 732, 734, 749, 764, 765, 767, 776, 794, 819, 820, 829,
        831,
    ),
    (
        6, 9, 24, 25, 26, 27, 41, 43, 44, 45, 55, 57, 58, 59, 74, 76,
        77, 92, 94, 95, 97, 108, 111, 126, 127, 144, 145, 146, 159, 162,
        164, 177, 178, 179, 180, 193, 195, 197, 211, 212, 213, 215, 226,
        229, 244, 246, 247, 263, 264, 279, 282, 293, 330, 332, 333, 335,
        346, 349, 364, 365, 366, 368, 382, 384, 397, 399, 400, 402, 414,
        416, 417, 418, 433, 434, 435, 448, 450, 451, 453, 464, 466, 468,
        482, 483, 484, 485, 500, 501, 502, 517, 534, 535, 536, 552, 553,
        568, 570, 571, 584, 585, 587, 603, 606, 618, 619, 634, 635, 637,
        638, 652, 653, 655, 656, 672, 685, 687, 688, 702, 704, 705, 718,
        720, 721, 722, 723, 725, 738, 755, 756, 758, 771, 772, 774, 787,
        790, 791, 805, 809, 823, 825, 838, 840,
    ),
    (
        7, 13, 16, 19, 22, 31, 37, 40, 48, 51, 54, 60, 66, 69, 75, 78,
        84, 90, 93, 107, 113, 116, 119, 122, 125, 128, 131, 137, 148,
        157, 160, 166, 169, 172, 175, 181, 187, 198, 204, 207, 210, 216,
        219, 222, 225, 228, 231, 234, 248, 251, 257, 260, 266, 269, 275,
        281, 286, 289, 292, 298, 301, 304, 310, 313, 316, 319, 322, 328,
        331, 351, 354, 357, 360, 363, 369, 372, 375, 378, 381, 386, 390,
        392, 395, 401, 404, 410, 413, 419, 422, 436, 442, 445, 454, 457,
        463, 472, 475, 492, 495, 504, 510, 516, 519, 524, 530, 539, 545,
        548, 554, 557, 563, 566, 586, 589, 592, 595, 598, 601, 604, 607,
        610, 616, 625, 628, 630, 636, 639, 642, 645, 648, 651, 654, 657,
        660, 669, 674, 677, 683, 686, 689, 692, 698, 701, 707, 710, 716,
        719, 724, 727, 730, 736, 739, 742, 745, 748, 751, 754, 760, 763,
        766, 769, 783, 786, 792, 798, 801, 804, 807, 818, 827, 830, 833,
        836, 839,
    ),
)


def old_coloring() -> list[int]:
    colors = [-1] * 1681
    for color, entries in enumerate(OLD_1680_HALF):
        for x in entries:
            if colors[x] != -1:
                raise ValueError(f"duplicate old-coloring entry {x}")
            colors[x] = color
    for x in range(1, 1681):
        if colors[x] == -1:
            colors[x] = colors[1681 - x]
        if colors[x] == -1:
            raise ValueError(f"uncovered old-coloring entry {x}")
    verify(colors)
    return colors


def search(
    target: int,
    solver_name: str,
    timeout_seconds: float,
    freeze_prefix: int,
) -> tuple[list[int], dict[str, int | float | str]]:
    center = target + 1
    exceptional = (center // 3, 2 * center // 3) if center % 3 == 0 else None

    def key(x: int) -> int:
        if exceptional is not None and x in exceptional:
            return x
        return min(x, center - x)

    keys = sorted({key(x) for x in range(1, target + 1)})
    key_index = {value: index for index, value in enumerate(keys)}

    def variable(key_value: int, color: int) -> int:
        return 7 * key_index[key_value] + color + 1

    clauses: list[list[int]] = []
    for key_value in keys:
        clauses.append([variable(key_value, color) for color in range(7)])
        for left in range(7):
            for right in range(left + 1, 7):
                clauses.append([-variable(key_value, left), -variable(key_value, right)])

    # Color labels are interchangeable.  Fixing c(1)=0 removes a factor of 7.
    clauses.append([variable(key(1), 0)])

    old = old_coloring()
    if freeze_prefix:
        if freeze_prefix > min(target, 1680):
            raise ValueError("freeze prefix exceeds the published 1680 seed")
        for x in range(1, freeze_prefix + 1):
            clauses.append([variable(key(x), old[x])])

    orbit_triples: set[tuple[int, ...]] = set()
    for x in range(1, target + 1):
        for y in range(x, target - x + 1):
            orbit_triples.add(tuple(sorted({key_index[key(x)], key_index[key(y)], key_index[key(x + y)]})))
    for orbit_triple in orbit_triples:
        for color in range(7):
            clauses.append([-(7 * index + color + 1) for index in orbit_triple])

    phase_literals: list[int] = []
    for key_value in keys:
        preferred = old[key_value] if key_value <= 1680 else 6
        phase_literals.append(variable(key_value, preferred))

    started = monotonic()
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        solver.set_phases(phase_literals)
        timer = None
        if timeout_seconds:
            timer = threading.Timer(timeout_seconds, solver.interrupt)
            timer.start()
        try:
            result = solver.solve_limited(expect_interrupt=bool(timeout_seconds))
        finally:
            if timer is not None:
                timer.cancel()
        elapsed = monotonic() - started
        stats: dict[str, int | float | str] = {
            "target": target,
            "center": center,
            "exceptional_split": "none" if exceptional is None else f"{exceptional[0]},{exceptional[1]}",
            "orbit_variables": len(keys),
            "boolean_variables": 7 * len(keys),
            "orbit_triples": len(orbit_triples),
            "cnf_clauses": len(clauses),
            "freeze_prefix": freeze_prefix,
            "solver": solver_name,
            "elapsed_seconds": round(elapsed, 6),
            "solver_result": "sat" if result is True else "unsat" if result is False else "interrupted",
        }
        if result is not True:
            raise RuntimeError(json.dumps(stats, sort_keys=True))
        model = set(solver.get_model())

    key_colors: dict[int, int] = {}
    for key_value in keys:
        chosen = [color for color in range(7) if variable(key_value, color) in model]
        if len(chosen) != 1:
            raise RuntimeError(f"model assigns orbit {key_value} colors {chosen}")
        key_colors[key_value] = chosen[0]
    colors = [-1] + [key_colors[key(x)] for x in range(1, target + 1)]
    verify(colors)
    return colors, stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1697)
    parser.add_argument("--solver", default="kissat404")
    parser.add_argument("--timeout-seconds", type=float, default=0.0)
    parser.add_argument("--freeze-prefix", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    colors, stats = search(args.target, args.solver, args.timeout_seconds, args.freeze_prefix)
    print(json.dumps(stats, sort_keys=True))
    if args.output:
        args.output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        print(f"wrote {args.output} ({len(colors) - 1} colors)")


if __name__ == "__main__":
    main()
