# Research log — second term for Sidon subsets of [N]

## Status (accessed 2026-08-27)

Opened this session:

- [arXiv:2607.01169 abs](https://arxiv.org/abs/2607.01169) — still v2 (5 Jul 2026).
  Theorem $F(N)\le N^{1/2}+0.9435 N^{1/4}+O(1)$. No v3.
- [arXiv HTML v2](https://arxiv.org/html/2607.01169v2) — Lemma 2.1 requires
  symmetric kernels; $L$ is free; Table 1 saturates near $R=8$. §5 asks for
  more kernels / a systematic outer search, and mentions cross-kernel
  correlations with a positivity constraint (not implemented here).
- [Green, *100 Open Problems*](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  — Problem 31, Dec 2025 update: still $N^{1/2}+O(1)\le F(N)\le N^{1/2}+N^{1/4}+O(1)$;
  comments record BFR $0.998$ and CHO $0.98183$. Does not cite Hou–Zhao.
- [Tao et al. $C_{5a}$](https://teorth.github.io/optimizationproblems/constants/5a.html)
  — published upper bounds still stop at CHO25 $0.98183$; $0.97633$ still
  unpublished. Does not list $0.9435$.
- [Hou–Zhao GitHub](https://github.com/HbZhao1/sidon-vector-smoothing) —
  landing page only; local snapshot in `compute/refs/` already matches
  Claim 4.1. Did not clone.
- [Erdős #30](https://www.erdosproblems.com/30) — Cloudflare interstitial;
  page body not readable this session. Last successful access in this
  folder was 2026-08-17 (OPEN, edited 2026-04-06).

Published record to beat is still Hou–Zhao $0.9435$. Anything in
$(0.9435,0.98183]$ is a weaker constant.

## Status (accessed 2026-08-17)

- [Erdős Problem #30](https://www.erdosproblems.com/30) — **OPEN**. Page last
  edited 2026-04-06. $1000 form: $h(N)=N^{1/2}+O_\varepsilon(N^\varepsilon)$.
  Zero claimed proofs. Do not claim Erdős–Turán.
- [Green, *100 Open Problems*, Problem 31](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025 update): improve, for infinitely many $N$,
  $N^{1/2}+O(1)\le F(N)\le N^{1/2}+N^{1/4}+O(1)$. Comments record BFR 0.998
  and CHO 0.98183.
- [Tao et al., constant $C_{5a}$](https://teorth.github.io/optimizationproblems/constants/5a.html)
  — published upper bounds stop at CHO25 0.98183; 0.97633 listed as unpublished
  AlphaEvolve (Carter–Georgiev–Gómez-Serrano–Hunter–O’Bryant–Tao–Wagner, 2025).
  Forum note (Tao, 17 Feb 2026) mentions a tentative ~0.947 argument “subject
  to confirmation”.

## Published upper bounds on the $N^{1/4}$ coefficient

| C | Reference |
| --- | --- |
| 1 | Erdős–Turán 1941; Lindström 1969 |
| 0.998 | Balogh–Füredi–Roy, arXiv:2103.15850 / AMM 2023 |
| 0.99703 | O’Bryant, arXiv:2207.07800 |
| 0.98183 | Carter–Hunter–O’Bryant, arXiv:2310.20032, Acta Math. Hungar. 175 (2025) |
| 0.9435 | **Hou–Zhao, [arXiv:2607.01169v2](https://arxiv.org/abs/2607.01169)** (5 Jul 2026) |

Hou–Zhao is later than the Erdős #30 page edit and later than PROBLEM.md’s
“best general upper bound 0.98183”. It is the current arXiv record. Code:
<https://github.com/HbZhao1/sidon-vector-smoothing>. The 8-kernel verifier
hashes to `957a5afadd849ac4f97c2b71252abb5c796c2db3c91a608ab35097e3c49292a8`,
matching Claim 4.1.

## Independent checks (this folder)

- `compute/verify_houzhao.py` — PASS. Rebuilt λ, p, w from the integer tables.
  √(ab) = 0.943492590713545 < 0.9435. a, b match Claim 4.1.
- `compute/search_kernels.py --phase replay` — Table 1 floats match.
- `compute/cho_two_windows.py` — CHO Thm 2.1 parameters give b_∞ ≤ 1.990578
  (C ≤ 0.99529) on a 400² sample of (w1,w2). Weaker than Hou–Zhao.
- `compute/construct_singer.py` — Singer unfolds for primes p≤31: size p+1,
  second term → ½, **0 extra points** in [p²+p+1].
- `compute/construct_bose.py` — Bose–Chowla for primes 3≤p≤79 is Sidon of
  size p in [p²-1]; greedy extras inside the interval are 0 for all p≥7.

## What we certified

Same eight kernels and mixing weights as Hou–Zhao, boundary length L=6
instead of L=4 (a valid instance of their Lemma 2.1). Exact certificate
`compute/certs/hz_kernels_L6.json`:

- a is the Claim 4.1 fraction (kernels unchanged)
- √(ab) = 0.9434925085033526
- so $F(N)\le N^{1/2}+0.94349251\,N^{1/4}+O(1)$
- this is 8.22×10^{-8} below Hou–Zhao’s γ0, and below (0.94349251)²

Verifiers (do not import each other):

```bash
python3 compute/verify_certificate.py compute/certs/hz_kernels_L6.json --beat 0.94349259
python3 compute/verify_beat_hz.py
```

This is a microscopic tightening of the published certificate, not a new
argument and not an improvement of the four-decimal statement 0.9435.

## OEIS / tables (residue only)

- [A003022](https://oeis.org/A003022), [A143824](https://oeis.org/A143824),
  [A227590](https://oeis.org/A227590) — finite Sidon / Golomb-ruler values.
  Isolated F(N) tables are not a dent.

## Did not beat

- Erdős–Turán / the $1000 form.
- $F(N)\ge\sqrt{N}+\omega(1)$ for infinitely many N. Singer gives +½+o(1);
  Shakan’s gap 2√p unwraps to another O(1). Greedy extras stay bounded.
- A constant at the 0.9434 level or below. L-lifts saturate by L=6;
  1-kernel search stays ~0.946; m-refinement of the same histograms is
  inert; multi-scale / coordinate-descent searches had not beaten the L=6
  plateau when this log was written.
