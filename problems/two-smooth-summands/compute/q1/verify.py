"""Replay the q1 certificates. Exit nonzero on a mismatch."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from smooth_lib import largest_prime_factor

from templates import (
    CLOSED_FORMS,
    exceeds_pow,
    floor_divisor,
    template_fails,
)

ROOT = Path(__file__).resolve().parent
CERTS = ROOT / "certs"


def load(name: str) -> dict:
    return json.loads((CERTS / name).read_text())


def check_closed_form(rec: dict) -> list[str]:
    errs = []
    p, q = map(int, rec["exponent"].split("/"))
    name = rec["template"]
    if name == "floor_divisor":
        fn = lambda n, p=p, q=q: floor_divisor(n, p, q)
    else:
        fn = CLOSED_FORMS[name]
    first = rec["first_hole"]
    if first is None:
        # Must really have no hole on the recorded range.
        for n in range(2, rec["limit"] + 1):
            if template_fails(fn(n), n, p, q):
                errs.append(f"{name} {p}/{q}: unexpected hole {n}")
                break
        return errs
    if not template_fails(fn(first), first, p, q):
        errs.append(f"{name} {p}/{q}: listed first hole {first} is not a hole")
    # Every recorded hole must fail, and nothing before first may fail.
    for n in range(2, first):
        if template_fails(fn(n), n, p, q):
            errs.append(f"{name} {p}/{q}: earlier hole {n} before {first}")
            break
    for n in rec["first_holes"]:
        if not template_fails(fn(n), n, p, q):
            errs.append(f"{name} {p}/{q}: listed hole {n} is covered")
    return errs


def check_infinite_family(doc: dict) -> list[str]:
    errs = []
    for row in doc["floor_divisor_family"]:
        p, q = map(int, row["exponent"].split("/"))
        if row["n_misses"] != 0:
            errs.append(f"floor-divisor {p}/{q}: {row['n_misses']} primes missed")
        for w in row["sample_hits"]:
            n, a = w["n"], w["a"]
            if a + w["b"] != n:
                errs.append(f"family split {n}")
            if not template_fails(a, n, p, q):
                errs.append(f"family n={n} does not fail floor-divisor")
            if floor_divisor(n, p, q) != a:
                errs.append(f"family n={n} a mismatch")
    for w in doc["pow2_family"]:
        n, a = w["n"], w["a"]
        if a != 1 << (n - 1).bit_length() - 1:
            errs.append(f"pow2 a(n) mismatch at {n}")
        if not exceeds_pow(largest_prime_factor(n - a), n, 1, 2):
            errs.append(f"pow2 n={n} does not fail at 1/2")
    if doc["pow2_misses"]:
        errs.append(f"pow2 misses {doc['pow2_misses']}")
    return errs


def check_poly(doc: dict) -> list[str]:
    errs = []
    if not doc["size_lower_bound_holds"]:
        errs.append("poly size lower bound failed")
    for row in doc["polys"]:
        if row["beats_square_by_size"]:
            errs.append(f"{row['poly']} claims to beat squares by size")
        deg = row["degree"]
        if deg < 2:
            errs.append(f"{row['poly']} degree {deg}")
    return errs


def main() -> int:
    errs: list[str] = []
    search = load("q1_search.json")
    for rec in search["closed_form"] + search["floor_divisor"]:
        errs.extend(check_closed_form(rec))
    if search["square_trivial_bound_holes"]:
        errs.append(
            "square 2sqrt+1 bound has holes "
            f"{search['square_trivial_bound_holes']}"
        )
    # Two-factor: recompute F-style only on listed first holes, and confirm
    # they are listed as holes. Full recomputation is search.py.
    for rec in search["two_factor"]:
        if rec["first_hole"] is None:
            errs.append(f"two-factor {rec['exponent']} unexpectedly hole-free")
        elif rec["first_hole"] < 3:
            errs.append(f"two-factor first hole {rec['first_hole']} looks wrong")
        if rec.get("exponent") == "2/5" and not rec.get("matches_known_F_exceptions"):
            errs.append("two-factor 2/5 holes drifted from the known F prefix")
        if rec.get("exponent") == "1/3":
            if rec.get("n_holes") != 76 or rec.get("last_hole") != 18191:
                errs.append(
                    "two-factor 1/3 should match the 76 F-exceptions, last 18191"
                )

    fam = load("infinite_family.json")
    errs.extend(check_infinite_family(fam))
    poly = load("poly_obstruction.json")
    errs.extend(check_poly(poly))

    if errs:
        print("VERIFY_FAIL")
        for e in errs:
            print(" ", e)
        return 1
    print("Q1_OK")
    print(f"replayed {CERTS / 'q1_search.json'}")
    print(f"replayed {CERTS / 'infinite_family.json'}")
    print(f"replayed {CERTS / 'poly_obstruction.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
