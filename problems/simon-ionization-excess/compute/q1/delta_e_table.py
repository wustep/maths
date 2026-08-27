#!/usr/bin/env python3
"""Tabulate heuristic ΔE(N, Z) = E(N-1, Z) - E(N, Z).

Simon 1984 10(a) asks whether ionization energies decrease in N:

    ΔE(N-1, Z) >= ΔE(N, Z)

This script checks that inequality on the HF table in
certs/hf_table.json. A clean check on a finite computed range is not a
proof of monotonicity. Every number is HEURISTIC.

    python3 rhf_atoms.py
    python3 delta_e_table.py
"""

from __future__ import annotations

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_DIR = os.path.join(HERE, "certs")
LABEL = "HEURISTIC"


def pairs_from_rows(rows: list[dict]) -> list[dict]:
    by = {}
    for r in rows:
        if not r.get("ok"):
            continue
        if r.get("scf_converged") is False:
            continue
        if "E" not in r:
            continue
        by.setdefault(int(r["Z"]), {})[int(r["N"])] = r

    out = []
    for z in sorted(by):
        byn = by[z]
        ns = sorted(byn)
        deltas = {}
        for n in ns:
            if n <= 0:
                continue
            if (n - 1) not in byn:
                continue
            e_n = byn[n]["E"]
            e_nm = byn[n - 1]["E"]
            de = e_nm - e_n
            deltas[n] = de
            out.append(
                {
                    "label": LABEL,
                    "Z": z,
                    "N": n,
                    "E_N": e_n,
                    "E_N-1": e_nm,
                    "delta_E": de,
                    "heuristic_binds": bool(e_n < e_nm),
                    "note": (
                        "ΔE(N,Z)=E(N-1,Z)-E(N,Z). HEURISTIC. "
                        "Positive means the table energy dropped when the "
                        "N-th electron was added."
                    ),
                }
            )
        # 10(a) on consecutive computed N that both have ΔE
        n_with = sorted(deltas)
        for i in range(1, len(n_with)):
            n = n_with[i]
            nprev = n_with[i - 1]
            if nprev != n - 1:
                continue
            de_prev = deltas[nprev]
            de = deltas[n]
            holds = de_prev >= de
            # attach onto the ΔE(N) row
            for row in out:
                if row["Z"] == z and row["N"] == n:
                    row["ten_a_compared_to"] = nprev
                    row["delta_E_N-1"] = de_prev
                    row["ten_a_holds_on_table"] = bool(holds)
                    row["ten_a_note"] = (
                        "HEURISTIC check of ΔE(N-1,Z) >= ΔE(N,Z) on this "
                        "pair. Does not prove 1984 10(a)."
                    )
    return out


def summarize(pairs: list[dict], method: str) -> dict:
    checked = [p for p in pairs if "ten_a_holds_on_table" in p]
    holds = [p for p in checked if p["ten_a_holds_on_table"]]
    fails = [p for p in checked if not p["ten_a_holds_on_table"]]
    binds = [p for p in pairs if p.get("heuristic_binds")]
    return {
        "label": LABEL,
        "method": method,
        "n_delta_values": len(pairs),
        "n_ten_a_pairs": len(checked),
        "n_ten_a_holds": len(holds),
        "n_ten_a_fails": len(fails),
        "monotone_on_computed_range": len(fails) == 0 and len(checked) > 0,
        "ten_a_failures": [
            {
                "Z": p["Z"],
                "N": p["N"],
                "delta_E": p["delta_E"],
                "delta_E_N-1": p["delta_E_N-1"],
            }
            for p in fails
        ],
        "heuristic_binding_pairs": [
            {"Z": p["Z"], "N": p["N"], "delta_E": p["delta_E"]} for p in binds
        ],
        "disclaimer": (
            "HEURISTIC. A clean table is not a proof of monotonicity. "
            "A failed pair is not a counterexample to 10(a): the energies "
            "are approximate HF numbers, not E(N,Z)."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Heuristic ΔE table from HF JSON")
    p.add_argument(
        "--hf",
        default=os.path.join(CERT_DIR, "hf_table.json"),
    )
    p.add_argument(
        "--out",
        default=os.path.join(CERT_DIR, "delta_e.json"),
    )
    args = p.parse_args(argv)

    with open(args.hf, encoding="utf-8") as fh:
        hf = json.load(fh)

    blocks = {}
    for key in (
        "helium_like_slater",
        "uhf_sp",
        "uhf_s_n12",
        "uhf_sto3g",
        "uhf_s_even_tempered",
    ):
        if key not in hf:
            continue
        rows = hf[key]["rows"]
        pairs = pairs_from_rows(rows)
        blocks[key] = {
            "label": LABEL,
            "method": hf[key].get("method", key),
            "summary": summarize(pairs, hf[key].get("method", key)),
            "rows": pairs,
        }

    doc = {
        "label": LABEL,
        "status": "residue",
        "disclaimer": (
            "HEURISTIC. ΔE is built from the HF table, not from the "
            "true Schrödinger energies. Checking 1984 10(a) on this range "
            "does not prove monotonicity. Nothing here is a bound on N0."
        ),
        "inequality": "ΔE(N-1,Z) >= ΔE(N,Z)  (Simon 1984 10(a))",
        "definition": "ΔE(N,Z) = E(N-1,Z) - E(N,Z)",
        "source": os.path.relpath(args.hf, HERE),
        "blocks": blocks,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")

    print(f"wrote {args.out}  label={LABEL}")
    for key, block in blocks.items():
        s = block["summary"]
        print(
            f"{key}: {s['n_ten_a_holds']}/{s['n_ten_a_pairs']} "
            f"10(a) pairs hold; monotone_on_range="
            f"{s['monotone_on_computed_range']}"
        )
        for f in s["ten_a_failures"]:
            print(
                f"  FAIL Z={f['Z']} N={f['N']}  "
                f"ΔE(N-1)={f['delta_E_N-1']:.6f}  ΔE(N)={f['delta_E']:.6f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
