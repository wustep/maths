# Covering: $\ell_2(10,2)\le 50$

Write $\ell_2(r,R)$ for the least length of a binary linear code
with redundancy $r$ and covering radius $R$. A binary linear code
of length 50 and dimension 40 has covering radius exactly 2, so

$$
\ell_2(10,2)\le 50.
$$

The November 2025 table (Davydov–Marcugini–Pambianco,
arXiv:2511.02542, Table 5.1) had $\ell_2(10,2)\le 51$.

## The seed argument

The certificate is a $10\times 50$ parity-check matrix,
[`compute/H_r10_n50.txt`](compute/H_r10_n50.txt): every syndrome
in $\mathbb{F}_2^{10}$ is a sum of at most two of its columns
(1024/1024, two independent verifiers). The same matrix has a
$(2,0)$-partition with $p(H)=10$, so the $\mathrm{QM}_2^2$
construction of arXiv:2511.02542 lifts it to longer codes
($r=18$, $n=815$; $r=20$, $n=1631$) and to the density bound
$\bar\mu(2)\le 2601/2048\approx 1.27002$. That is the interesting
part: one finite seed moves the asymptotic constant, not just a
table entry.

## Status

Construction, an upper bound. Sphere covering gives only
$\ge 45$, and an $n=49$ search left 7 holes, so 50 is not shown
optimal.

## Replay

```bash
python compute/verify_certificate.py
cd result && ./run_all.sh
```

Standalone writeup: [`result/`](result). Explainers:
[HTML](explainer.html), [PDF](explainer.pdf).

## What was tried for 49

Still open. Sphere covering only gives $\ge 45$. Overnight work on
2026-08-21 did not produce a 49, and it did not produce a lower bound.

Three construction families, none of them a neighbour-search on the
50-set:

1. Recover the 2003 Kaikkonen–Rosendahl 51-set and ask whether 51 or 50
   is a lift of the $r=8$ record. They are not. Replacing one quotient
   block of the 50-set by a shorter block does not yield a 49 in any
   instance that was decided.
2. Prescribe an automorphism of odd prime order. No 49-set is invariant
   under an element of order 7. Combined with a short arithmetic
   argument, any 49-set has automorphism group a $\{2,3,5\}$-group.
   The known 50-set and 51-set are both 2-group symmetric.
3. A fibered construction (one column over every nonzero point of a
   quotient, plus a kernel block). It reproduces the documented lengths
   at $r=4,7,8,9$ and is completely decided for $r\le 8$. At $r=10$ it
   cannot produce any length $\le 47$; its own best is 54. The nearest
   unfinished case in the family is length 38 at $r=9$, which would
   beat $\ell_2(9,2)\le 39$ and was not decided.

Code: [`compute/q9/`](compute/q9/), [`compute/q10/`](compute/q10/),
[`compute/q11/`](compute/q11/).

