# Research log — Linear covering codes of radius two

## 2026-08-16

- [Ben Green, *100 Open Problems*, Problem 40](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) — \(1\le f(2)\le 1.4238\); unknown whether \(f(2)=1\).
- [Davydov–Marcugini–Pambianco, arXiv:2511.02542v1, Table 5.1](https://arxiv.org/abs/2511.02542) — documented \(\ell_2(10,2)\le 51\), density \(1327/1024\); also \(\ell_2(8,2)\le 26\), \(\ell_2(9,2)\le 39\). Named in the recovered `witness_r10_n50.json`.
- Kaikkonen–Rosendahl 51-column seed used by q1 search (named in WALKTHROUGH.md and witness JSON). The explicit 51-column hex listing was not recovered as a separate file.

## 2026-08-18 (q4, n=49 push — residue only)

- Counting: \(1+49+\binom{49}{2}=1226\ge 1024\), so 49 is not excluded by volume; a 49-covering would have density \(1226/1024\approx 1.19727\), well below the paper's \(\bar\mu\) values. Counting lower bound is only \(n\ge 45\).
- Invariant-covering reduction: for \(G\le GL(10,2)\), \(G\)-invariant coverings live in orbit-class space; conjugate subgroups give equivalent problems, and \(\langle M\rangle=\langle M^k\rangle\) collapses cyclic classes to cyclotomic-coset data. Order-7 elements of \(GL(10,2)\): elementary divisors from \(x^3+x+1\), \(x^3+x^2+1\), trivial part of dim 1, 4, or 7. Frobenius (order-10) and pure multiplicative order-3/5/11/31 symmetries are arithmetically impossible at n=49 (orbit sizes cannot sum to 49).
- Exhaustions (all zero witnesses): both order-7 dim-1-fixed classes; all 50 \(C_7\times C_7\) classes; 12 order-15, 10 order-21, 7 order-105 classes. Open: order-7 with fixed dim 4/7 (timeouts), order-9/-35/-45 (not reached before stop).
- The 7-hole residue at n=49 reproduces across independent anneals; two inequivalent GL-classes of 7-hole optima found, both with hole sets of rank 5 containing exactly one zero-sum quadruple, both ≥5- resp. ≥4-swap-deep (exhaustive k-swap prover with exact defer/endgame logic).
- WLOG frame reduction for SAT: a rank-10 covering can be assumed to contain the ten unit vectors (GL acts transitively on ordered bases); cuts the cardinality-49 CNF search substantially. Instance built (1.14M clauses); no verdict before the stop order.

## 2026-08-20 (leftover paper constructions)

- \(M_{OK}\) last hex word in arXiv:2511.02542 (6.10) is the invalid token `ICE`. Exhausting all 9-bit last columns against Theorem 7.1's \(P_{OK}\) leaves exactly one survivor: `1CE`.
- QM\(_2^1\) on the certified \(p(H_{18})\le 17\) partition is the unused \(p\)-preserving lift: \(n=2^m(n_0+2)-2\) is usually worse than QM\(_2^2\), but here \(m=4\) is legal and yields a shorter \(r=26\) matrix than the already-certified QM\(_3^2\) length 13309.
