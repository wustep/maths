# q10 — mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q9. The published record is still v1 only. q9
(`#119` / `b258707`) certified printed leading **1.1017** at
aspect 10, \(n=34\), target \(\varphi=0.9113\): compact
\(\gamma=0.9077156846635223\), \(1/\gamma=1.1016665426142618\),
cut \(10/11>\gamma\). Do not re-enumerate those
\(17{,}179{,}869{,}183\) faces.

This folder is the leftover: \(n=35\) mid-radius bins at the
same proven split. The mass-opt cut \(10/11\) still has slack.
A certified compact \(\gamma\) at target \(0.9115\) is predicted
to print **1.1013**. An optional cheaper probe retargets
\(\varphi=0.9114\) on the existing \(n=34\) matrix (predicted
printed **1.1016**); that is not an \(n=35\) dent.

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat 1.1017. Do not reopen
that slab unless a sharper large-aspect cut is certified.
Finite-\(Z\) integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\)
along Lemma 4.3 stay residue.

## Replay

```bash
problems/simon-ionization-excess/compute/q10/run_all.sh
```

Exit 0 is either a lift of q9's 1.1017 or a recorded residue.
If `certs/raise_*.json` is missing, leftover scripts still
pass and the wrap is residue: do not invent a leading.

Fast path after a certified raise:

```bash
python3 verify_lift.py && python3 lift_cert.py
```

`verify_lift.py` and `verify_rebuild.py` are stdlib.
`verify_aspect.c` / `.rs` replay the mass-opt identities.
`tighten_leading.py` is the interval §7 printer (`ceil_dec`).

## Layout

Same as q9: `raise_*.json`, faces dump, `lift.json`.
Part files (`certs/*.part*`) and compiled verifiers are
gitignored. Face cost is \(2^n-1\); \(n=35\) is
\(34{,}359{,}738{,}367\) faces.
