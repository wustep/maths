#!/usr/bin/env python3
"""Assemble certs/smallz.json from the q2 dumps. Residue, not a dent."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def load(name: str) -> dict:
    return json.loads((CERTS / name).read_text())


def main() -> None:
    env = load("envelopes.json")
    alpha = load("alpha_n.json")
    weights = load("lieb_weights.json")
    nam = load("nam_smallz.json")
    temple = load("temple.json")
    geom = load("geometric_alpha.json")
    tetra = load("tetra.json")

    best = {row["Z"]: row["best_published"] for row in env["at"]}
    unsettled = {row["Z"]: row["unsettled_integers"] for row in env["at"]}

    a4 = [r for r in alpha["rows"] if r["N"] == 4 and abs(r["s"] - 2.0) < 1e-12]
    a4s2 = a4[0]["search_min"] if a4 else None
    any_weight_excludes = any(
        r["excludes_Z2_if_this_were_a_lower_bound"] and not r["already_cannot_exclude_Z2"]
        for r in weights["rows"]
    )
    # The flag "excludes if this were a lower bound" on an *upper* is not a proof.
    # What matters: did every family produce a config with R <= 2?
    families_blocked = {}
    for r in weights["rows"]:
        key = (r["N"], r["family"])
        families_blocked[str(key)] = families_blocked.get(str(key), False) or r[
            "already_cannot_exclude_Z2"
        ]

    nam_any = any(a["contradiction_from_published_alpha_lower"] for a in nam["nam_lemma1"])
    hps_any = any(a["contradiction"] for a in nam["hps_710"])

    blob = {
        "is_new_bound": False,
        "status": "residue",
        "certified_finite_Z_dent": None,
        "hydrogen_uniqueness_not_claimed": True,
        "best_published_integer_bound": {
            "Z=2": {
                "Nc_le": best[2]["max_integer_Nc"],
                "source": "Lieb Nc < 2Z+1",
                "unsettled_N": unsettled[2],
                "N0_ge": 2,
                "comment": "Zhislin binds N=2; Lieb excludes N>=5; N=3,4 open",
            },
            "Z=3": {
                "Nc_le": best[3]["max_integer_Nc"],
                "source": "Lieb Nc < 2Z+1",
                "unsettled_N": unsettled[3],
                "N0_ge": 3,
            },
            "Z=4": {
                "Nc_le": best[4]["max_integer_Nc"],
                "source": "Lieb Nc < 2Z+1",
                "unsettled_N": unsettled[4],
                "N0_ge": 4,
            },
            "Z=5": {
                "Nc_le": best[5]["max_integer_Nc"],
                "source": "Lieb Nc < 2Z+1",
                "unsettled_N": unsettled[5],
                "N0_ge": 5,
            },
        },
        "tried": {
            "published_envelopes": (
                "Lieb, Nam, HPS s=2 printed and q1, HPS s=3 printed and q1. "
                "At Z=2,3,4,5 Lieb is strictly best. Nam/HPS exclude no extra integer."
            ),
            "lieb_weights": (
                "φ = |x|^s, |x|/(1+λ|x|), 1-e^{-α|x|}, |x|e^{-μ|x|}, min(|x|,ρ), "
                "compact C^1 cutoff. Search upper on inf R_N(φ) is ≤ 2 for every "
                "family at N=3 and N=4, so none of these weights can exclude "
                "those N at Z=2."
            ),
            "nam_hps_plug_in": (
                "Nam Lemma 1 + Prop. 1 and HPS (7.10) at N=3,4 and Z=2..5: "
                "no contradiction from published alpha lowers. Prop. 1 remainder "
                "destroys the bound at N=4."
            ),
            "alpha_search": (
                f"Numerical upper on alpha_4,2 ≈ {a4s2}. The regular tetrahedron "
                "gives the exact upper sqrt(6)/4, so alpha_4,2 * 3 < 2 by 54<64. "
                "Need > 2/3 if kinetic is dropped. Pair geometry cannot exclude "
                "N=4 at Z=2."
            ),
            "tetrahedron": tetra["statement"],
            "temple_IH": (
                "3e Slater trials have μ above the helium Hylleraas upper, so "
                "Temple vs E_1 ≥ E(2,2) does not apply. IH minorants 1/|x-y|≥0 "
                "and 1/(|x|+|y|) sit well below E(2,2)."
            ),
            "not_used": "HF/DFT tables are not bounds and were not used.",
        },
        "flags": {
            "any_nam_lemma1_contradiction": nam_any,
            "any_hps710_contradiction": hps_any,
            "any_weight_certified_R_gt_2": False,
            "temple_applies": temple["temple"]["applies_if_E1_is_published_He"],
            "families_have_R_leq_2_config": families_blocked,
        },
        "replay": "problems/simon-ionization-excess/compute/q2/run_all.sh",
        "note": (
            "Residue: nothing here certifies Nc(2)<4 or Nc(2)<3, nor any "
            "unique N0(Z) for Z>1. Best published integer bounds remain "
            "Lieb: Nc(2)≤4, Nc(3)≤6, Nc(4)≤8."
        ),
    }
    path = CERTS / "smallz.json"
    path.write_text(json.dumps(blob, indent=2) + "\n")
    print("wrote", path)
    print(blob["note"])
    if blob["is_new_bound"] or blob["certified_finite_Z_dent"]:
        raise SystemExit("assemble_cert must not claim a dent")


if __name__ == "__main__":
    main()
