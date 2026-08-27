# q1 — five lines backwards

Imagined end-states, then work backwards. No published H(n) moved.

| Line | Imagined claim | Outcome |
| --- | --- | --- |
| `a-quadratic-five/` | quadratic with 5 cycles | dropped; fork: Shi origin is a weak focus of order 3, V3 = 35625/8 |
| `b-cubic-fourteen/` | cubic with 14 cycles | dropped; fork: van der Pol satisfies Liénard uniqueness (exactly 1 cycle) |
| `c-chebyshev/` | Chebyshev lift beats 2604.12883 Table 1 | kept as replay; table matches; no missed factorization; §6 degree-11 field with 9 ovals |
| `d-restricted-upper/` | exact upper bound for a family | kept: radial cubic has exactly 1 cycle; quadratic Hamiltonians have 0; Lotka–Volterra has 0 in the open first quadrant |
| `e-bezout-bautin/` | Bézout ceiling / Bautin L1 | kept: one-step degree-m pullback ≤ m² sheets; L1 primitive polynomial. Full Bautin ideal dropped |

Replay:

```
./run_all.sh
```

or from the problem compute folder, `./run_all.sh`.

Certificates: `a-quadratic-five/cert.json`, `b-cubic-fourteen/certificate.json`,
`c-chebyshev/certs/`, `d-restricted-upper/certs/identities.json`,
`e-bezout-bautin/*.json`. Second languages: C (A), rustc (B–E), Lean 4.32.0
(`e-bezout-bautin/AdjBezout.lean`).
