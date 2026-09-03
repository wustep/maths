# q13 — mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q12. The published record is still v1 only. q11
(`#136` / `9d99070`) certified printed leading 1.1010 at
aspect 10, \(n=36\), target \(\varphi=0.9117\). That cert stays
frozen. q12 started \(n=37\) with the naive mask dump and
stopped incomplete. Those four shards stay leftover, not a bound.

This folder certifies printed leading **1.1006** at the same
split with \(n=37\), target \(\varphi=0.9119\): compact
\(\gamma=0.9086061090539742\), \(1/\gamma=1.1005869210379662\),
cut \(10/11>\gamma\). Faces
\(137{,}438{,}953{,}471\), copositive, \(0\) residual skips,
\(\min m^\top Mm>6\cdot 10^{-4}\), \(\min\varphi=0.912085\).
The dump is a Gray-code walk of \(M_S\) (`verify_gray.c`), one
thread, about 2 MB RSS, not a four-shard Gauss-Jordan dump.

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat 1.1010. Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover. The withdrawn \(1.1168\) stays withdrawn.

## Replay

```bash
problems/simon-ionization-excess/compute/q13/run_all.sh
```

Exit 0 is the leading-coefficient lift of q11's 1.1010.
Certificate: `certs/lift.json`.

Fast path, once the Gray dump is stored:

```bash
python3 write_raise.py && python3 verify_lift.py && python3 lift_cert.py
```

`write_raise.py`, `verify_lift.py`, and `verify_rebuild.py` are
stdlib. `verify_aspect.c` / `.rs` replay the mass-opt identities.
`tighten_leading.py` is the interval §7 printer (`ceil_dec`).
Set `PYTHON` to a venv with mpmath if the system Python lacks it.
