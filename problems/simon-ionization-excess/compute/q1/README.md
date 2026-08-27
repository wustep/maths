# q1 — Simon ionization excess

Replay of the published non-asymptotic bounds on $N_c(Z)$, and a
tightening of the Hundertmark–Pattakos–Schulz remainders. Same
Section 7 chain as arXiv:2504.18487v1. The leading coefficient
$1.1185$ is not moved.

## Certified

`certs/hps_tight.json` (interval arithmetic) and
`verify_remainder.py` (independent stdlib path) give

    N_c < b(2) Z + 2.953 Z^{1/3}                         (Z ≥ 2)
    N   < b(3) Z + 3.892 Z^{1/3}
          + 0.0134 + 0.184 Z^{-1/3} + 0.0196 Z^{-2/3}    (Z ≥ 4)
    N_c < 1.1185 Z + 3.9781 Z^{1/3}                      (Z ≥ 4)

Printed HPS: 2.96, 3.90, and 4. The LT factor stays 1.456
(Frank–Hundertmark–Jex–Nam, arXiv:1808.09017).

`certs/hminus.json` is a rational Hylleraas certificate that H^−
binds ($E=-815/1602$, gap $7/801$). With Lieb $N_c<3$ this recovers
$N_0(1)=2$, already in Lieb 1984. Not a new bound.

A floating DFT energy is not a bound. The UHF table is heuristic.

## Replay

```bash
./run_all.sh
```

That runs the HPS/Nam Python replays, `verify_remainder.py`, the
Hylleraas check, `gcc`/`rustc` verifiers of $b(2)$ and $b(3)$, and
the published-envelope table. Heuristic HF steps are non-fatal.

Lean algebraic enclosures (optional):

```bash
cd ../../lean
export PATH="$HOME/.elan/bin:$PATH"
lake build
# or, no mathlib:
lean B3NatWitness.lean
```
