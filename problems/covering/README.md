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
