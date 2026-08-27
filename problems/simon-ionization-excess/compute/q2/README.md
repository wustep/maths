# q2 — leading coefficient and small Z

Search for a leading coefficient below $1.1185$, a bound on
$N_0(Z)-Z$ for a concrete $Z$-range, or an $s>3$ path. Nothing
here replaces Hundertmark–Pattakos–Schulz Theorem 2.2
(arXiv:2504.18487v1). Hydrogen uniqueness is not claimed.

```bash
./run_all.sh
```

That replays the small-$Z$ envelopes, the $s>3$ two-shell
counterexamples, the withdrawn $1.1168$ notice, the compact
aspect-$\le 4$ face enumeration, and the independent Rust
rebuild. Exit $0$ is residue.

Certificates: `certs/smallz.json`, `certs/s_gt_3.json`,
`certs/beta3_compact.json`, `certs/beta3_rad.json` (withdrawn),
`certs/aspect_try.json`. Notes in `work/`.
