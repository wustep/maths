# Cursor Grok 2026-08-27 — Simon ionization excess, later search

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q2/`.

## Result

Residue. The published fermionic leading coefficient is still

$$
N_c < 1.1185\,Z + 4Z^{1/3}\qquad(Z\ge 4)
$$

(Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1). The q1 remainder
tightening is unchanged. $N_0(Z)-Z$ bounded is still open.

What was tried and did not certify a dent:

- $s>3$: two-shell dipoles make $I_s(\nu)$ negative. $b(4)\approx1.083$
  cannot be used.
- Finite $Z$: Lieb still gives the best integers at $Z=2,3,4,5$.
  Tetrahedron blocks $N=4$ at $Z=2$ by pair geometry ($54<64$).
- A claimed $\beta_3^{-1}\le1.1168$ tail lift is withdrawn
  ($h(0,1)\approx0.991$ exceeds the power-law trial $0.921$).
- Compact aspect $\le4$: certified $Q\ge0.901924$ (so $1/Q\le1.1087$
  in that class only). Not a replacement for Theorem 2.2.

Benguria–González-Brantes 2511.07582v1 is bosonic / statistics-
independent, $N<1.4811Z+3.1516Z^{1/3}$ for $Z\ge12$. Does not beat
1.1185 for fermions.

Hydrogen $N_0(1)=2$ is not claimed.

## Replay

```bash
problems/simon-ionization-excess/compute/q1/run_all.sh
problems/simon-ionization-excess/compute/q2/run_all.sh
```

Or `problems/simon-ionization-excess/compute/run_all.sh`.
