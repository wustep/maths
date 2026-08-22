# Research — lonely runner, 14 runners

## Papers replayed

**Sungkawichai and Trakulthongchai, *Eleven, twelve, and thirteen lonely
runners*, arXiv:2604.23906v1 (26 Apr 2026).**
<https://arxiv.org/abs/2604.23906>. Fetch with
`python3 scripts/arxiv_fetch.py 2604.23906`; the reading copy used here was
`pdftotext -layout` into `compute/refs/st26.txt`. `compute/refs/` is local
only. Read in full on 2026-08-22. The published frontier: LRC(k) for k ≤ 12, i.e. up to 13 runners.

What was actually used, with the section numbers, because the folder had
been citing this paper loosely:

- Definition 2.1 — `(k,p,l)`-proper, *including the gcd branch*
  `gcd(l, v_1,…,v̂_i,…,v_k) > 1`. Footnote 1 replaces `lp` by `l`. This is
  the term the 2026-08-17 transcription dropped.
- Lemma 2.2, Lemma 2.4, Corollary 2.5, Proposition 2.7 — the reduction
  from LRC(k) to `J(k,p) = ∅` over a prime set with `∏ p ≥ B_k`.
- Lemma 2.6 — `B_k = (C(k+1,2)^{k-1}/k)^k`, from Malikiosis–Santos–Schymura.
  `ln B_13 = 13(12 ln 91 − ln 13) = 670.3497…`.
- Remark 3.2 — if `p > k+1` then `I(k,p,l) = ∅` only if `(k+1) | l`. At
  k=13 this forces `14 | l`, so a `×2` ladder alone can never finish.
- **§5.2, the k=11 lifting diagram** `S1 ×2 ×2 ×2 ×2 ×3 ×3 → S7`. This is
  the load-bearing observation for this folder: `k+1 = 12` is composite and
  they simply lift through its prime factors, with no polynomial method
  anywhere. Compositeness of `k+1` is a change of route, not a wall.
- Proposition 4.1 — the polynomial identity in `F_{k+1}`, odd prime `k+1`.
  It exists only to avoid the `c = k+1` lift. Its proof compares leading
  coefficients of two degree-k polynomials agreeing on k+1 points; both
  steps need a field, so `Z/14` is genuinely unavailable.
- Lemma 4.2, Lemma 4.3, Proposition 4.4, Proposition 1.4 — the chain from
  Prop 4.1 to "every `u` with `gcd(u)=1` and `u_i ≡ i (mod p)` has the LR
  property", valid when `k+1` and `p > k²+k` are both odd primes.
- §5.1 — the equivalence reduction (permute, negate, scale by `Z_p^×`),
  giving about `p^k / (2^k (k−1)!)` representatives.
- Table 1 — the prime sets and `ln ∏ p` vs `ln B_k` for k = 10, 11, 12.
- **§7** — names the k=13 bottleneck explicitly: "the primary bottleneck in
  extending our results to k = 13 is the efficient computation of
  `I(k,p,1)`". At p=191 under §5.1 that is about `1.1e17` representatives.
  Also Conjecture 7.1 (a universal denominator `D` for non-tight tuples).

**Trakulthongchai, *Nine and ten lonely runners*, arXiv:2511.22427**,
E-JC 33 (2026). <https://arxiv.org/abs/2511.22427>
(`python3 scripts/arxiv_fetch.py 2511.22427`). Source of the lifting scheme
(Definition 31, Lemma 5, Lemma 7) that ST26 generalize. Not re-derived
here beyond what ST26 restate.

## Cited through ST26, not opened

- Malikiosis, Santos, Schymura, *Linearly exponential checking is enough…*,
  Forum of Mathematics Sigma 13 (2025) — the `B_k` bound, used as quoted.
- Goddyn and Wong, *Tight instances of the lonely runner*, Integers 6
  (2006) A38 — tightness of `(1,…,k)`. Used qualitatively: `(1,…,k)` has a
  witness time only at `s/(k+1)` with `gcd(s,k+1)=1`, which is why every
  `s=0` constraint in `compute/q1/cover.c` is hit. The code asserts this at
  run time rather than relying on the citation.
- Rosenfeld, arXiv:2509.14111 (eight runners) and arXiv:2512.01912 (nine).
- Bedert, arXiv:2511.16636 — the `1/(2k) + k^{-5/3+o(1)}` gap. Different
  regime; not used.

## Companion code

- `vzsky/13-lonely-runners` (ST26) and `t-tanupat/nine-and-ten-lonely-runners`
  (Tra25). Recorded 2026-08-17: `LrcVerifier<13>`/`<14>` templates exist but
  `results/` stops at k=12, and their `sat/README.md` estimates ~1.5 machine
  years for a k=14 find-cover. Not re-fetched on 2026-08-22; nothing in this
  session depends on their numbers.

## Lookups that came back empty

- No published statement of ST26 Proposition 1.4 or 4.4 with the primality
  hypothesis on `k+1` removed. Their §7 gestures at extending "the algebraic
  method in Proposition 4.1 … to other classes of speed tuples", but the
  composite-`k+1` case is not treated.
- No OEIS lookup was useful: the object here is a covering condition on
  `(Z/14Z)^13`, not an integer sequence.
