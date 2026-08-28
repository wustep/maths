# q10 — mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q9. The published record is still v1 only. q9
(`#119` / `b258707`) certified printed leading 1.1017 at
aspect 10, \(n=34\), target \(\varphi=0.9113\).

This folder certifies printed leading **1.1013** at the same
split with \(n=35\), target \(\varphi=0.9115\): compact
\(\gamma=0.908018018752533\), \(1/\gamma=1.1012997312254167\),
cut \(10/11>\gamma\). Faces
\(34{,}359{,}738{,}367\), copositive, \(8362\) residual skips,
\(\min m^\top Mm>5\cdot 10^{-4}\).

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat 1.1017. Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover.

## Replay

```bash
problems/simon-ionization-excess/compute/q10/run_all.sh
```

Exit 0 is the leading-coefficient lift of q9's 1.1017.
Certificate: `certs/lift.json`.

Fast path:

```bash
python3 verify_lift.py && python3 lift_cert.py
```

`verify_lift.py` and `verify_rebuild.py` are stdlib.
`verify_aspect.c` / `.rs` replay the mass-opt identities.
`tighten_leading.py` is the interval §7 printer (`ceil_dec`).

## Layout

Same as q9: `raise_*.json`, faces dump, `lift.json`.
Part files (`certs/*.part*`) and compiled verifiers are
gitignored.
