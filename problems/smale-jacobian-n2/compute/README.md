# compute — Smale 16 / plane Jacobian conjecture

- `q1/`: Python/Rust bridge check plus the pinned exact certificate replay that
  excludes \((72,108)\) and gives maximum counterexample degree at least 125.
- `q2/`: exact sparse verification and classification notes for every
  homogeneous plane Keller perturbation.
- `q3/`: formal-coefficient verification that a raw tangent-line sweep in the
  plane cannot have nonzero constant Jacobian.

Run all local checks with:

```bash
./problems/smale-jacobian-n2/compute/q2/run_all.sh
./problems/smale-jacobian-n2/compute/q3/run_all.sh
```

q1 also downloads and replays an 86 MB exact certificate archive; see its
README for the one-command and pre-downloaded forms.
