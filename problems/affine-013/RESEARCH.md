# Research log — Extremal affine copies of {0,1,3}

## 2026-08-17

- [Ben Green, *100 Open Problems*, Problem 24](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025 update). SHA-256
  `e06971245914947f152550dee59bbb29fe0e798f0c51b2bc2557f824c2f9a44a`.
  Statement: maximum number of affine translates of {0,1,3} in an
  n-element integer set. Comments: Ganguly / Pemantle; conjectured
  (1/3+o(1))n²; “Aaronson’s paper [2] should be consulted.” No later
  update on this problem in the Dec 2025 file.
- Green’s bibliography [2] is James Aaronson, *Maximising the number of
  solutions to a linear equation in a set of integers*,
  [arXiv:1801.07135v4](https://arxiv.org/abs/1801.07135)
  = Bull. Lond. Math. Soc. 51 (2019), 577–594. The list entry
  `1805.01980` is a different paper (inverse scattering). SHA-256 of
  v4: `f0da178874c50f7653d87271d86fae036abb5d19e9b83b17503251424f2e2ef2`.
- Aaronson’s T(S) counts ordered triples in S³ with x+2y=3z, including
  n trivials. Affine copies of {0,1,3} are the nontrivial triples
  {y, y+d, y+3d}, d≠0. Asymptotic constant unaffected by the n trivials.
- Published record on γ_{1,2,-3} := limsup T(S)/|S|² after the fetch:
  - lower 1/3, from any interval (T = n²/3+O(1));
  - upper 3/4, from Hardy–Littlewood / Gabriel / Lev rearrangement
    (Aaronson (1.2) and Lemma 2.6). Exact γ known only for |abc|≤2.
  Aaronson conjectures γ_{1,2,-3}=1/3. No later paper found tonight
  moves this constant. Green Dec 2025 still lists the problem as open.
- [Green–Sisask, arXiv:0709.4432](https://arxiv.org/abs/0709.4432),
  Theorem 1.2: maximum number of 3APs in an n-element integer set is
  ⌈n²/2⌉, by an ordering argument on midpoints. The same sum
  ∑(1+2 min(j−1,n−j)) appears in tonight’s {0,1,3} bound; the fibre
  injection is different (scale −2 about z, not reflection about z).
- Lev, *On the number of solutions of a linear equation over finite
  sets*, J. Combin. Theory Ser. A 83 (1998), 251–267; Lev–Pinchasi,
  Acta Arith. 163 (2014), 127–140: exact maximisers for x+y+z=0 and
  a±b=2c. Not used in the 1/2 argument.
- Bukh, *Sums of dilates*, Combin. Probab. Comput. 17 (2008):
  |S+2S|≥3|S|−o(|S|). Used only as residue (too weak alone to beat 3/4).

## Bound claimed tonight

T(S) ≤ ⌈n²/2⌉ for every n-element S⊂ℤ, hence γ_{1,2,-3} ≤ 1/2.
This is strictly below the published 3/4. It does not prove the
conjecture 1/3. Independent check: `compute/verify_half.py`.
