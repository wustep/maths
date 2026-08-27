# Cursor Grok 2026-08-27 — Lieb–Thirring q2

Continuation of Simon 2000 #15. Search lives in
`problems/simon-lieb-thirring/compute/q2/`. Covering stayed frozen.
Branched from the q1 branch (PR #93), not from main.

q1 replay (`compute/q1/run_all.sh`) exited 0. Family A still
certifies 1.45576. Lemma 11 second pair still does not convert below
1.456.

The later record is Carvalho Corso–Ried, arXiv:2403.04347v2:
$L/L^{\mathrm{cl}}\le 1.44655$ from $M_3=0.371185695$. The abstract
hides the number. Carvalho Corso, arXiv:2407.10117v2, writes the same
bound as a Clausen value and rounds it to 1.447. Independently, the
sine series for $\mathrm{CI}_2(2\pi/3)$ converts to
$M_3\le 0.371185695$ and $L/L^{\mathrm{cl}}\le 1.4465531$. Did not
beat 1.44655. Residue vs the later record. No new trial pair. No
priority claim.

Replay:

```
cd problems/simon-lieb-thirring/compute/q2
./run_all.sh
```

Certificate: `compute/q2/certs/m3_ccr.json`.
Sobolev $2/\sqrt{3}$ still open.
