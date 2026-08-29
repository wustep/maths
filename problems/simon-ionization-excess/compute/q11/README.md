# q11 — mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q10. The published record is still v1 only. q10
(`#128` / `fd14170`) certified printed leading 1.1013 at
aspect 10, \(n=35\), target \(\varphi=0.9115\). That cert stays
frozen. Those faces were not re-enumerated.

This folder certifies printed leading **1.1010** at the same
split with \(n=36\), target \(\varphi=0.9117\): compact
\(\gamma=0.9083146735963096\), \(1/\gamma=1.1009400476166247\),
cut \(10/11>\gamma\). Faces
\(68{,}719{,}476{,}735\), copositive, \(16296\) residual skips,
\(\min m^\top Mm>6\cdot 10^{-4}\).

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat 1.1013. Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover. The withdrawn \(1.1168\) stays withdrawn.

## Replay

```bash
problems/simon-ionization-excess/compute/q11/run_all.sh
```

Exit 0 is the leading-coefficient lift of q10's 1.1013.
Certificate: `certs/lift.json`.

Fast path:

```bash
python3 verify_lift.py && python3 lift_cert.py
```

`verify_lift.py` and `verify_rebuild.py` are stdlib.
`verify_aspect.c` / `.rs` replay the mass-opt identities.
`tighten_leading.py` is the interval §7 printer (`ceil_dec`).

## Layout

Same as q10: `raise_*.json`, faces dump, `lift.json`.
Part files (`certs/*.part*`) and compiled verifiers are
gitignored.
