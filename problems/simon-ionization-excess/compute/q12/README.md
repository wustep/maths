# q12 — leftover mid-radius bins at the proven aspect-10 split

Same HPS §7 / [arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487)
chain as q1–q11. The published record is still v1 only. q11
(`#136` / `9d99070`) certified printed leading 1.1010 at
aspect 10, \(n=36\), target \(\varphi=0.9117\). That cert stays
frozen. Those faces were not re-enumerated. q10 \(n=35\) stays
frozen too.

This folder copied the q11 stack and raised `NMAX` to 40 so
\(n=37\) loads. SLSQP at target \(\varphi=0.9119\) predicts
printed \(1.1006\) if faces certify. The \(2^{37}-1\) dump was
stopped incomplete: slowest shard about \(29.6\%\). Scanned
faces stay copositive with \(\min\varphi=0.912085>0.9119\).
That is not a certificate. Predicted \(1.1006\) is uncertified.
Printed leading stays \(1.1010\).

\(R\le 9\) with \(Q>R/(R+1)\) cannot beat \(1.1010\). Finite-\(Z\)
integers (Lieb), \(N_0(Z)-Z\) bounded, and \(s>3\) along
Lemma 4.3 stay leftover. The withdrawn \(1.1168\) stays withdrawn.

## Replay

```bash
problems/simon-ionization-excess/compute/q12/run_all.sh
```

Exit 0 without `certs/lift.json` is residue.
Checkpoint: `certs/leftover_n37.json` and the four `*.part*` dumps.
