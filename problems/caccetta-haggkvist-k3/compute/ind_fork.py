#!/usr/bin/env python3
"""Independent expansions of IndT, IndV, and Fork on H0..H31.

Conventions match HKN: densities are unlabeled types, and the factor 24 = 4!
counts labeled injections.  We compare against the published identities
(4.14), (4.15) and the fork expansion after Lemma 4.7.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from flags4 import (
    H_EDGES,
    enumerate_labeled,
    has_c3,
    induced,
    type_of,
)

OUT = Path(__file__).resolve().parent / "certs"


def is_T(arcs3) -> bool:
    """Type T on (v1,v2,v3)=(0,1,2): edges 2→3, 2→1, 3→1 i.e. 1→2, 1→0, 2→0."""
    want = frozenset([(1, 2), (1, 0), (2, 0)])
    return arcs3 == want


def is_V(arcs3) -> bool:
    """Type V: edges 2→1, 3→1 i.e. 1→0, 2→0, and no 1–2 edge."""
    want = frozenset([(1, 0), (2, 0)])
    return arcs3 == want


def classify_source(arcs, roots, extra) -> str:
    """'F0', 'source', or 'other' for a type where vertex 1 has indegree |σ|-1."""
    if any((extra, r) in arcs for r in roots):
        return "other"
    if all((r, extra) in arcs for r in roots):
        return "F0"
    return "source"


def expand_ind(is_type, n_roots: int = 3):
    """Return (const_coeff[t], c_coeff[t]) so Ind_t = const + c * c_coeff.

    For each labeled 4-graph of type t, for each injection of the 3-type:
      if the type embeds:
        F0     → +c0     (relative to the -c0 unit)
        source → +1
        other  →  0
        plus the unit −c0 for every embedding of the type
    Average over labeled copies, no extra 24 (we count all injections, which
    already is the 4! convention once we divide by n_labeled and... wait).

    HKN writes 24 Ψ([[f]]).  Our average-over-labeled-graphs of (#injections
    with a given property) is exactly that 24-scaled density, because a random
    4-set of type t contributes its injection count, and Ψ_t is the type density.
    """
    n_type = [0] * 32
    # accumulators: for each t, sum over labeled G of
    #   n_embed, n_F0, n_source_not_F0
    n_emb = [0] * 32
    n_f0 = [0] * 32
    n_src = [0] * 32
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for vs in itertools.permutations(range(4), 3):
            if not is_type(induced(arcs, vs)):
                continue
            extra = ({0, 1, 2, 3} - set(vs)).pop()
            n_emb[t] += 1
            kind = classify_source(arcs, vs, extra)
            if kind == "F0":
                n_f0[t] += 1
            elif kind == "source":
                n_src[t] += 1
    # Per type, average injection counts:
    # contribution = n_src * 1 + n_f0 * c0 - n_emb * c0
    #             = n_src + (n_f0 - n_emb) * c0
    # divide by n_type so it multiplies Ψ_t.
    const = [0.0] * 32
    ccoe = [0.0] * 32
    for t in range(32):
        if n_type[t] == 0:
            continue
        const[t] = n_src[t] / n_type[t]
        ccoe[t] = (n_f0[t] - n_emb[t]) / n_type[t]
    return const, ccoe, n_type, n_emb, n_f0, n_src


def expand_fork():
    """4 Ψ(κ) coefficients: κ = induced fork (center outdeg 2, no leaf–leaf edge)."""
    n_type = [0] * 32
    n_fork = [0] * 32
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        # C(4,3)=4 triples; count induced forks.  Then 4 Ψ(κ) uses
        # 4 * (n_fork_triples / 4) = n_fork_triples, averaged.
        forks = 0
        for triple in itertools.combinations(range(4), 3):
            sub = induced(arcs, triple)
            # some vertex outdeg 2, no edge between the two leaves
            for c in range(3):
                leaves = [i for i in range(3) if i != c]
                if (c, leaves[0]) in sub and (c, leaves[1]) in sub:
                    if (leaves[0], leaves[1]) not in sub and (leaves[1], leaves[0]) not in sub:
                        if (leaves[0], c) not in sub and (leaves[1], c) not in sub:
                            forks += 1
                            break
        n_fork[t] += forks
    coeff = [n_fork[t] / n_type[t] if n_type[t] else 0.0 for t in range(32)]
    return coeff, n_type, n_fork


def main():
    print("=== IndT ===")
    ct, cq, nT, eT, fT, sT = expand_ind(is_T)
    # published (4.14):
    # (1-c) r9 - c r13 - c r14 - c r16 + (1-c) r18 + (1-c) r19 + (1-c) r20
    # - 2c r22 - 2c r24 - 2c r26 + (1-2c) r27 + (1-2c) r29
    # + (2-2c) r30 - 3c r31
    pub_T_const = [0.0] * 32
    pub_T_c = [0.0] * 32
    for k in (9, 18, 19, 20):
        pub_T_const[k] += 1
        pub_T_c[k] += -1
    for k in (13, 14, 16):
        pub_T_c[k] += -1
    for k in (22, 24, 26):
        pub_T_c[k] += -2
    for k in (27, 29):
        pub_T_const[k] += 1
        pub_T_c[k] += -2
    pub_T_const[30] += 2
    pub_T_c[30] += -2
    pub_T_c[31] += -3

    print("t  const_comp  const_pub   c_comp    c_pub")
    for t in range(32):
        if abs(ct[t]) + abs(cq[t]) + abs(pub_T_const[t]) + abs(pub_T_c[t]) > 1e-12:
            print(f"{t:2d} {ct[t]:10.4f} {pub_T_const[t]:10.4f} {cq[t]:10.4f} {pub_T_c[t]:10.4f}")

    print("\n=== IndV ===")
    vt, vq, *_ = expand_ind(is_V)
    pub_V_const = [0.0] * 32
    pub_V_c = [0.0] * 32
    # (1-c) r2 - 3c r5 + (1-c) r6 - c r11 + (1-c) r12 - 2c r13 + (1-c) r14
    # + (2-2c) r21 - c r22 - c r23 - c r24 - c r25 - c r26
    for k in (2, 6, 12, 14):
        pub_V_const[k] += 1
        pub_V_c[k] += -1
    pub_V_c[5] += -3
    pub_V_c[11] += -1
    pub_V_c[13] += -2
    pub_V_const[21] += 2
    pub_V_c[21] += -2
    for k in (22, 23, 24, 25, 26):
        pub_V_c[k] += -1
    print("t  const_comp  const_pub   c_comp    c_pub")
    for t in range(32):
        if abs(vt[t]) + abs(vq[t]) + abs(pub_V_const[t]) + abs(pub_V_c[t]) > 1e-12:
            print(f"{t:2d} {vt[t]:10.4f} {pub_V_const[t]:10.4f} {vq[t]:10.4f} {pub_V_c[t]:10.4f}")

    print("\n=== Fork 4Ψ(κ) ===")
    fk, ntype, nfork = expand_fork()
    pub_fk = [0.0] * 32
    for k, m in [(4, 1), (7, 1), (8, 3), (12, 1), (17, 1), (19, 1), (20, 2),
                 (21, 2), (23, 1), (25, 1), (26, 1), (29, 1), (30, 2)]:
        pub_fk[k] = m
    print("t  comp   pub")
    for t in range(32):
        if abs(fk[t]) + abs(pub_fk[t]) > 1e-12:
            print(f"{t:2d} {fk[t]:6.3f} {pub_fk[t]:6.3f}")

    payload = {
        "IndT_const": ct,
        "IndT_c": cq,
        "IndV_const": vt,
        "IndV_c": vq,
        "Fork_4psi": fk,
        "pub_T_const": pub_T_const,
        "pub_T_c": pub_T_c,
        "pub_V_const": pub_V_const,
        "pub_V_c": pub_V_c,
        "pub_fork": pub_fk,
    }
    path = OUT / "ind_fork.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
