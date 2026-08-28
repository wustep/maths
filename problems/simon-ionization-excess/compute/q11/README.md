# q11 — mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q10. The published record is still v1 only. q10
(`#128` / `fd14170`) certified printed leading 1.1013 at
aspect 10, \(n=35\), target \(\varphi=0.9115\). That cert stays
frozen. Do not re-enumerate those faces.

This folder hunts a printed leading below **1.1013** at the same
split with \(n=36\) bins (\(2^{36}-1=68{,}719{,}476{,}735\) faces).
Face enumeration is the certificate, not the SLSQP prediction.
A predicted compact \(\gamma\) that sits below the \(10/11\) cut
is only a dent after the faces dump is copositive.

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat 1.1013. Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover. The withdrawn \(1.1168\) stays withdrawn.

Optional cheaper probes (full re-enum; changing \(\varphi\)
changes \(M\)) on the \(n=34\) or \(n=35\) matrix are not an
\(n=36\) dent.

## Replay

```bash
problems/simon-ionization-excess/compute/q11/run_all.sh
```

Exit 0 with a stored `certs/raise_*.json` is a leading-coefficient
lift of q10's 1.1013. Exit 0 without that file is a leftover
record. Certificate, if certified: `certs/lift.json`.

Fast path after a stored dump:

```bash
python3 verify_lift.py && python3 lift_cert.py
```

`verify_lift.py` and `verify_rebuild.py` are stdlib.
`verify_aspect.c` / `.rs` replay the mass-opt identities.
`tighten_leading.py` is the interval §7 printer (`ceil_dec`).

## Layout

Same as q10: `raise_*.json`, faces dump, `lift.json`.
Part files (`certs/*.part*`) and compiled verifiers are
gitignored. Shard from those parts; do not restart a live
shard from zero if `minM>0`.
