# q12 — leftover mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q11. The published record is still v1 only. q11
(`#136` / `9d99070`) certified printed leading 1.1010 at
aspect 10, \(n=36\), target \(\varphi=0.9117\). That cert stays
frozen. Those faces were not re-enumerated. q10 \(n=35\) stays
frozen too.

This folder hunts the next compact thicken: \(n=37\) at the
same split, with a target \(\varphi\) that can print below
1.1010 if faces certify copositive with \(\min m^\top Mm>0\).
The \(n=37\) printed dent is a hypothesis until a stored faces
dump says so.

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat 1.1010. Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover. The withdrawn \(1.1168\) stays withdrawn.

## Replay

```bash
problems/simon-ionization-excess/compute/q12/run_all.sh
```

Exit 0 with `certs/lift.json` is a leading-coefficient lift of
q11's 1.1010. Exit 0 without a certified `raise_*.json` is
residue.

Fast path after a stored raise:

```bash
python3 verify_lift.py && python3 lift_cert.py
```

`verify_lift.py` and `verify_rebuild.py` are stdlib.
`verify_aspect.c` / `.rs` replay the mass-opt identities.
`tighten_leading.py` is the interval §7 printer (`ceil_dec`).
`verify_beta3.c` has `NMAX 40` so \(n=37\) loads.

## Layout

Same as q11: `raise_*.json`, faces dump, `lift.json`.
Part files (`certs/*.part*`) and compiled verifiers are
gitignored.
