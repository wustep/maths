#!/usr/bin/env python3
"""Replay Gasull–Santana Harnack arithmetic, arXiv:2510.11705v2 Cor. 2.

Independent check of
    H(n+m) >= H(n) + Har(m),
    Har(m) = (m-1)(m-2)/2 + [1+(-1)^m]/2,
on the same published seeds q1/c-chebyshev uses, plus the Chebyshev
table numbers already on arXiv:2604.12883v1.

This is a replay, not a new H(n) bound. The imagined claim that the
recurrence beats a published table entry for some N=n+m<=50 is
dropped. Do not cite 252/1080/1380/2012, or H_K(5)>=28, as found here.
"""

from __future__ import annotations

import json
import os
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, "certs")

# ---------------------------------------------------------------------------
# Published seeds. Cited, not reconstructed. Same dicts as
# q1/c-chebyshev/verify.py. We do not replay the Prohens–Torregrosa
# or Han–Li centres.
# ---------------------------------------------------------------------------

# Prohens–Torregrosa, Nonlinearity 32 (2019), Theorem 1.
PT_THM1: dict[int, int] = {
    4: 28,
    5: 37,
    6: 53,
    7: 74,
    8: 96,
    9: 120,
    10: 142,
}

# Han–Li, J. Differ. Equations 252 (2012), Theorem 1.2(i),
# as quoted by 2604.12883v1 Appendix A (not extracted from the paywall).
HAN_LI_APP_A: dict[int, int] = {
    11: 153,
    12: 157,
    14: 194,
    15: 345,
    16: 351,
    18: 372,
    19: 503,
    20: 509,
}

# Prohens–Torregrosa 2019, Corollary 2(a), the m=2 lifts they record.
PT_COR2: dict[int, int] = {
    13: 212,
    17: 384,
    21: 568,
    31: 1184,
    35: 1536,
    39: 1920,
    43: 2272,
}

# Table 1 L_pub column, including Han–Li rows that Appendix A does not
# list as seeds.
HAN_LI_TABLE1_ONLY: dict[int, int] = {
    23: 833,
    24: 843,
    25: 870,
    26: 880,
    27: 1023,
    29: 1060,
}

# Published small-n bounds, not used as Appendix A seeds.
SMALL_PUB: dict[int, int] = {1: 0, 2: 4, 3: 13}

# 2604.12883v1 Table 1 / Table 2, as printed. Already on that arXiv.
# Included here as published lower bounds when comparing; say so.
PAPER_L_CH: dict[int, int] = {
    11: 148,
    13: 212,
    14: 252,
    15: 296,
    17: 384,
    19: 480,
    20: 477,
    21: 568,
    23: 666,
    24: 700,
    25: 628,
    26: 864,
    27: 848,
    29: 1080,
    31: 1380,
    35: 1536,
    39: 2012,
    43: 2272,
}

PAPER_FOUR_NEW: dict[int, int] = {14: 252, 29: 1080, 31: 1380, 39: 2012}

N_MAX = 50

SOURCES: dict[str, dict[int, int]] = {
    "SMALL_PUB": SMALL_PUB,
    "PT_THM1": PT_THM1,
    "HAN_LI_APP_A": HAN_LI_APP_A,
    "PT_COR2": PT_COR2,
    "HAN_LI_TABLE1_ONLY": HAN_LI_TABLE1_ONLY,
    "PAPER_L_CH": PAPER_L_CH,
}


def fail(msg: str) -> None:
    raise SystemExit(f"verify.py FAIL: {msg}")


def har(m: int) -> int:
    """Harnack number. Integer form of (m-1)(m-2)/2 + [1+(-1)^m]/2."""
    if m < 1:
        fail(f"Har index {m} < 1")
    ovals = (m - 1) * (m - 2) // 2
    parity = (1 + (-1) ** m) // 2
    alt = 1 if m % 2 == 0 else 0
    if parity != alt:
        fail(f"Har parity formulas disagree at m={m}: {parity} vs {alt}")
    return ovals + parity


def combine_l_pub(sources: dict[str, dict[int, int]]) -> dict[int, int]:
    out: dict[int, int] = {}
    for table in sources.values():
        for n, val in table.items():
            if n in out:
                out[n] = max(out[n], val)
            else:
                out[n] = val
    return out


def increment_closed_recorded(n: int, l_pub: dict[int, int]) -> int:
    """Best published lower bound at n after H(k+1) >= H(k)+1.

    Gasull–Santana arXiv:2407.13465v2. Applied only to recorded seeds:
    H(n) >= L_pub(k) + (n-k) for each recorded k < n, and L_pub(n)
    itself when present.
    """
    best = l_pub.get(n, 0)
    for k, val in l_pub.items():
        if k < n:
            best = max(best, val + (n - k))
    return best


def enumerate_harnack(l_pub: dict[int, int], n_max: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n in range(1, n_max):
        for m in range(1, n_max - n + 1):
            n_tot = n + m
            seed = l_pub.get(n, 0)
            lift = seed + har(m)
            recorded = n_tot in l_pub
            l_at = l_pub.get(n_tot)
            closed = increment_closed_recorded(n_tot, l_pub) if recorded else None
            exceeds_quoted = bool(recorded and lift > l_at)
            exceeds_closed = bool(recorded and closed is not None and lift > closed)
            rows.append(
                {
                    "n": n,
                    "m": m,
                    "N": n_tot,
                    "L_pub_n": seed,
                    "seed_recorded": n in l_pub,
                    "Har_m": har(m),
                    "lift": lift,
                    "N_recorded": recorded,
                    "L_pub_N": l_at,
                    "L_closed_N": closed,
                    "exceeds_quoted": exceeds_quoted,
                    "exceeds_closed": exceeds_closed,
                }
            )
    return rows


def best_per_n(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    best: dict[int, dict[str, Any]] = {}
    for row in rows:
        n_tot = row["N"]
        cur = best.get(n_tot)
        key = (row["lift"], row["n"], row["m"])
        if cur is None or key > (cur["lift"], cur["n"], cur["m"]):
            best[n_tot] = {
                "N": n_tot,
                "lift": row["lift"],
                "n": row["n"],
                "m": row["m"],
                "L_pub_n": row["L_pub_n"],
                "Har_m": row["Har_m"],
                "seed_recorded": row["seed_recorded"],
                "N_recorded": row["N_recorded"],
                "L_pub_N": row["L_pub_N"],
                "L_closed_N": row["L_closed_N"],
                "slack_quoted": (
                    None if row["L_pub_N"] is None else row["L_pub_N"] - row["lift"]
                ),
                "slack_closed": (
                    None if row["L_closed_N"] is None else row["L_closed_N"] - row["lift"]
                ),
            }
    return best


def chebyshev_one_step(seeds: dict[int, int], n_max: int) -> dict[int, int]:
    """One-step L_Ch: N+1 = m(n+1), m>=2, n>=1, lift = m^2 L(n)."""
    out: dict[int, int] = {}
    for n_tot in range(1, n_max + 1):
        np = n_tot + 1
        best = None
        for m in range(2, np + 1):
            if np % m != 0:
                continue
            n = np // m - 1
            if n < 1 or n not in seeds:
                continue
            lift = m * m * seeds[n]
            if best is None or lift > best:
                best = lift
        if best is not None:
            out[n_tot] = best
    return out


def check_har_named() -> list[int]:
    expected = [0, 1, 1, 4, 6, 11]
    got = [har(m) for m in range(1, 7)]
    if got != expected:
        fail(f"named Har(1..6) = {got} != {expected}")
    if har(1) != 0:
        fail("Har(1) != 0")
    # Closed form vs the even/odd rule, through N_MAX.
    for m in range(1, N_MAX + 1):
        har(m)
    return got


def check_table() -> dict[str, Any]:
    named = check_har_named()
    l_pub = combine_l_pub(SOURCES)
    if l_pub.get(4) != 28:
        fail(f"L_pub[4] = {l_pub.get(4)} != 28")
    if l_pub.get(5) != 37:
        fail(f"L_pub[5] = {l_pub.get(5)} != 37")
    if l_pub.get(14) != 252:
        fail("L_pub[14] must include Chebyshev 252")
    if l_pub.get(18) != 372:
        fail("L_pub[18] must be the Han–Li quoted 372 before increment-closure")

    rows = enumerate_harnack(l_pub, N_MAX)
    if len(rows) != N_MAX * (N_MAX - 1) // 2:
        fail(f"pair count {len(rows)} != {N_MAX * (N_MAX - 1) // 2}")

    quoted_beats = [r for r in rows if r["exceeds_quoted"]]
    closed_beats = [r for r in rows if r["exceeds_closed"]]
    quoted_m_ge_2 = [r for r in quoted_beats if r["m"] >= 2]
    if quoted_m_ge_2:
        fail(f"m>=2 pair exceeds quoted L_pub: {quoted_m_ge_2}")
    if closed_beats:
        fail(f"pair exceeds increment-closed published bound: {closed_beats}")

    # The only quoted-table exceedance is Har(1)=0 at N=18.
    expected_m1 = {
        "n": 17,
        "m": 1,
        "N": 18,
        "lift": 384,
        "L_pub_N": 372,
        "L_pub_n": 384,
        "Har_m": 0,
        "increment_would_give": 385,
        "is_dent": False,
    }
    m1 = [r for r in quoted_beats if r["m"] == 1]
    if len(m1) != 1:
        fail(f"expected exactly one m=1 quoted exceedance, got {m1}")
    r0 = m1[0]
    if (
        r0["n"] != 17
        or r0["N"] != 18
        or r0["lift"] != 384
        or r0["L_pub_N"] != 372
        or r0["Har_m"] != 0
    ):
        fail(f"unexpected m=1 exceedance {r0}")
    if increment_closed_recorded(18, l_pub) != 385:
        fail("increment-closed L(18) != 385")

    best = best_per_n(rows)

    # Chebyshev one-step from the Appendix A seeds, as in q1.
    seeds_app_a = dict(PT_THM1)
    seeds_app_a.update(HAN_LI_APP_A)
    seeds_app_a.update(PT_COR2)
    l_ch = chebyshev_one_step(seeds_app_a, N_MAX)
    for n_tot, paper_val in PAPER_L_CH.items():
        if l_ch.get(n_tot) != paper_val:
            fail(f"L_Ch({n_tot}) = {l_ch.get(n_tot)} != paper {paper_val}")

    four_harnack = {}
    for n_tot, paper_val in PAPER_FOUR_NEW.items():
        h = best[n_tot]["lift"]
        four_harnack[str(n_tot)] = {
            "chebyshev_already_on_2604_12883": paper_val,
            "harnack_best": h,
            "argmax": {"n": best[n_tot]["n"], "m": best[n_tot]["m"]},
            "beats_chebyshev": h > paper_val,
        }
        if h > paper_val:
            fail(f"Harnack lift at {n_tot} beats Chebyshev {paper_val}")

    # Kolmogorov: H_K(n) >= H(n-1). Printed H_K(5)>=28 from H(4)>=28.
    hk5 = l_pub[4]
    if hk5 != 28:
        fail("H_K(5) replay is not 28")
    if hk5 == 9:
        fail("H_K(5) is not the Section-6 nine-oval field")
    if hk5 >= l_pub[5]:
        fail("H_K(5)>=28 must not beat planar H(5)>=37")

    recorded_rows = []
    for n_tot in sorted(l_pub):
        if n_tot < 2:
            continue
        b = best[n_tot]
        recorded_rows.append(
            {
                "N": n_tot,
                "L_pub": l_pub[n_tot],
                "L_closed": increment_closed_recorded(n_tot, l_pub),
                "L_Ch": l_ch.get(n_tot),
                "harnack_best": b["lift"],
                "argmax": {"n": b["n"], "m": b["m"], "L_pub_n": b["L_pub_n"], "Har_m": b["Har_m"]},
                "slack_quoted": l_pub[n_tot] - b["lift"],
                "slack_closed": increment_closed_recorded(n_tot, l_pub) - b["lift"],
            }
        )

    holes = []
    for n_tot in range(2, N_MAX + 1):
        if n_tot in l_pub:
            continue
        b = best[n_tot]
        holes.append(
            {
                "N": n_tot,
                "harnack_best": b["lift"],
                "argmax": {"n": b["n"], "m": b["m"], "L_pub_n": b["L_pub_n"], "Har_m": b["Har_m"]},
                "note": (
                    "no recorded L_pub at this N in the six seed tables; "
                    "lift is Cor. 2 arithmetic, not a new H(N)"
                ),
            }
        )

    return {
        "papers": {
            "harnack": "arXiv:2510.11705v2 Corollary 2",
            "increment": "arXiv:2407.13465v2",
            "chebyshev_table": "arXiv:2604.12883v1 Table 1 / Appendix A",
        },
        "seed_citations": {
            "small_n H(1)=0, H(2)>=4, H(3)>=13": SMALL_PUB,
            "Prohens–Torregrosa 2019 Thm 1": PT_THM1,
            "Han–Li 2012 Thm 1.2(i) as quoted in 2604.12883v1 App A": HAN_LI_APP_A,
            "Prohens–Torregrosa 2019 Cor 2(a)": {str(k): v for k, v in PT_COR2.items()},
            "Han–Li Table 1 rows not in App A seeds": HAN_LI_TABLE1_ONLY,
            "Chebyshev L_Ch already on 2604.12883v1": {str(k): v for k, v in PAPER_L_CH.items()},
        },
        "PAPER_L_CH_included_as_published": True,
        "N_max": N_MAX,
        "n_pairs": len(rows),
        "Har_1_to_6": named,
        "Har": {str(m): har(m) for m in range(1, N_MAX + 1)},
        "L_pub": {str(k): l_pub[k] for k in sorted(l_pub)},
        "recorded_N": recorded_rows,
        "unrecorded_N_le_50": holes,
        "m1_quoted_exceedances": [expected_m1],
        "n_beats_quoted_m_ge_2": 0,
        "n_beats_closed_recorded": 0,
        "n_beats_claimed": 0,
        "four_chebyshev": {str(k): v for k, v in PAPER_FOUR_NEW.items()},
        "harnack_vs_four": four_harnack,
        "H_K_5": 28,
        "L_pub_4": 28,
        "L_pub_5": 37,
        "H_K_5_equals_L_pub_4": True,
        "H_K_5_equals_9": False,
        "H_K_5_beats_H_5": False,
        "Har_1": 0,
        "weaker_than_increment": True,
        "do_not_claim_252_1080_1380_2012_as_ours": True,
        "do_not_claim_HK5_28_as_ours": True,
        "example_H6_from_H2": {
            "n": 2,
            "m": 4,
            "lift": l_pub[2] + har(4),
            "L_pub_6": l_pub[6],
        },
    }


def canonical_core(table: dict[str, Any]) -> dict[str, Any]:
    """Numeric core that the Rust verifier must match exactly."""
    return {
        "N_max": table["N_max"],
        "n_pairs": table["n_pairs"],
        "Har_1_to_6": table["Har_1_to_6"],
        "Har": table["Har"],
        "L_pub": table["L_pub"],
        "n_beats_quoted_m_ge_2": table["n_beats_quoted_m_ge_2"],
        "n_beats_closed_recorded": table["n_beats_closed_recorded"],
        "n_beats_claimed": table["n_beats_claimed"],
        "m1_quoted_exceedances": table["m1_quoted_exceedances"],
        "H_K_5": table["H_K_5"],
        "L_pub_4": table["L_pub_4"],
        "L_pub_5": table["L_pub_5"],
        "H_K_5_equals_L_pub_4": table["H_K_5_equals_L_pub_4"],
        "H_K_5_equals_9": table["H_K_5_equals_9"],
        "H_K_5_beats_H_5": table["H_K_5_beats_H_5"],
        "Har_1": table["Har_1"],
        "weaker_than_increment": table["weaker_than_increment"],
        "four_chebyshev": table["four_chebyshev"],
        "harnack_vs_four": {
            k: v["harnack_best"] for k, v in table["harnack_vs_four"].items()
        },
        "do_not_claim_252_1080_1380_2012_as_ours": True,
        "do_not_claim_HK5_28_as_ours": True,
        "best_harnack": {
            str(row["N"]): {"lift": row["harnack_best"], "n": row["argmax"]["n"], "m": row["argmax"]["m"]}
            for row in table["recorded_N"]
        },
        "example_H6_from_H2": table["example_H6_from_H2"]["lift"],
        "L_pub_6": table["example_H6_from_H2"]["L_pub_6"],
        "L_closed_18": 385,
    }


def write_json(name: str, payload: dict[str, Any]) -> str:
    os.makedirs(CERTS, exist_ok=True)
    path = os.path.join(CERTS, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")
    return path


def emit_tables() -> dict[str, Any]:
    """Integer tables for the Rust verifier. String keys, pair lists."""
    def pairs(d: dict[int, int]) -> list[list[int]]:
        return [[k, d[k]] for k in sorted(d)]

    return {
        "N_max": N_MAX,
        "SMALL_PUB": pairs(SMALL_PUB),
        "PT_THM1": pairs(PT_THM1),
        "HAN_LI_APP_A": pairs(HAN_LI_APP_A),
        "PT_COR2": pairs(PT_COR2),
        "HAN_LI_TABLE1_ONLY": pairs(HAN_LI_TABLE1_ONLY),
        "PAPER_L_CH": pairs(PAPER_L_CH),
        "PAPER_FOUR_NEW": pairs(PAPER_FOUR_NEW),
        "SEEDS_APP_A": pairs({**PT_THM1, **HAN_LI_APP_A, **PT_COR2}),
    }


def main() -> None:
    table = check_table()
    core = canonical_core(table)
    write_json("tables.json", emit_tables())
    write_json("table_replay.json", table)
    write_json("core.json", core)

    print("verify.py: ok")
    print(f"  pairs N=n+m<=50 = {table['n_pairs']}")
    print(f"  Har(1..6) = {table['Har_1_to_6']}")
    print(f"  quoted m>=2 beats = {table['n_beats_quoted_m_ge_2']}")
    print(f"  closed recorded beats = {table['n_beats_closed_recorded']}")
    print(f"  claimed beats = {table['n_beats_claimed']}")
    print(f"  m=1 quoted exceedance N=18: 384 vs 372 (not a dent; increment 385)")
    print(f"  H_K(5)>=28 == L_pub[4] = {table['H_K_5_equals_L_pub_4']}; ==9? {table['H_K_5_equals_9']}")
    print(f"  H(2)+Har(4) = {table['example_H6_from_H2']['lift']} vs L_pub[6]={table['example_H6_from_H2']['L_pub_6']}")


if __name__ == "__main__":
    main()
