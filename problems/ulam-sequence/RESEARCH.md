# Research log — Density of the Ulam sequence

## Statement (as attacked)

Green 100 #7 (December 2025 update): does the classical Ulam sequence
$U(1,2)$ have positive density? Can one explain Steinerberger’s Fourier
spike at $\alpha\approx 2.5714474995$?

Erdős #342 (Bloom, accessed 2026-08-17): still open, “cannot be resolved
with a finite computation”, zero claimed proofs. Additional questions in
Guy C4 / Erdős–Graham: infinitely many pairs $a,a+2$? Eventually
periodic differences? Density zero?

Tonight’s allowed dent, per the house prompt: a certified finite advance
(exact prefix, covering/automaton certificate, or a spectral fact with a
verifier). Density is not to be claimed unless proved.

## Sources fetched

- Ben Green, *100 Open Problems*, Problem 7, December 2025 update,
  https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf
- OEIS A002858, accessed 2026-08-17 (b-file through $n=10000$,
  $a(10000)=132788$)
- Steinerberger, *A hidden signal in the Ulam sequence*, Exp. Math. 26
  (2017); arXiv:1507.00267
- Clément–Steinerberger, *Small gaps in the Ulam sequence*, CR Math. 363
  (2025), 941–949; arXiv:2501.16285. **Published growth record.**
- Hinman–Kuca–Schlesinger–Sheydvasser, *The unreasonable rigidity of Ulam
  sets*, J. Number Theory 194 (2019); arXiv:1711.00145
- Kravitz–Steinerberger, *Ulam sequences and Ulam sets*, arXiv:1705.01883
- Erdős problem #342 and its forum (last page edit 2025-09-30; forum
  accessed 2026-08-17). A January 2026 comment already suggests optimizing
  the CS constant $1.454$.
- Agama, arXiv:2007.02697v12, “Ulam numbers have zero density”. Not
  accepted by the current Green list or by Erdős #342. Unused.

Computational records we did **not** beat: Gibbs–McCranie,
$a(2.8\cdot 10^{10})=378485625853$; McCranie
$2.57144749846<\alpha<2.57144749850$.

## Published theorems used

1. The sequence is infinite, and $a_{n+1}\le a_n+a_{n-1}$.
2. Eggleton (in Recamán, AMM 1973): $a_{n+1}\le a_n+a_{n-2}$, hence
   $a_n\le\rho_E^n$ with $\rho_E$ the real root of $x^3-x^2-1=0$
   ($\rho_E\approx 1.4655712318767682$).
3. Clément–Steinerberger 2025, Lemma 1–2 and Theorem 1: Eggleton cannot
   hold twice in a row (once there are enough previous terms); if the next
   term is not Eggleton it is at most $\max(a_n+a_{n-3},a_{n-1}+a_{n-2})$;
   the resulting majorant is a product of $T_1,T_2,T_3$ with no
   consecutive $T_3$; $L=15$ gives $a_n\le 1.454^n$ for large $n$.
   The same method cannot prove a base below
   $\rho(T_3T_1^2)^{1/3}\approx 1.4146717609798722$.
4. Regularity theorems of Finch, Schmerl–Spiegel, Cassaigne–Finch: not
   applicable to $U(1,2)$.
5. Hinman et al.: $\operatorname{dens} U(1,n)\le(n+1)/(3n)$. For $n=2$
   this is $1/2$, too weak to move Green #7.

## What this folder proves

**Theorem.** Let $a_n$ be the Ulam sequence with $a_1=1$, $a_2=2$.
Then

$$
a_n\le\Bigl(\frac{1443}{1000}\Bigr)^n
\quad\text{for every integer }n\ge 1,
$$

and

$$
a_n\le\Bigl(\frac{1442}{1000}\Bigr)^n
\quad\text{for every integer }n\neq 3.
$$

This is the Clément–Steinerberger majorant with a longer admissible word
and with the Frobenius norm in place of the operator 2-norm. The $L=15$
2-norm maximum was independently recomputed as $1.453902202043493$,
matching the published $1.4539$ that they rounded to $1.454$. The
first $L$ at which the exact Frobenius maximum beats $1.454$ is
$L=16$ ($F_2=150408$, $C_F\approx 1.451408682527$). The strongest
run is $L=22$ ($F_2=9690750$, $C_F\approx 1.441387826311$).

The all-$n$ statement at $1.443$ uses the $L=21$ majorant from
$n=3304$ and a direct integer check of $a_n\le(1443/1000)^n$ on
$1\le n\le 3304$. The almost-all statement at $1.442$ uses the $L=22$
majorant from $n=1635$; the only prefix failure is $a_3=3$.

**Record beaten.** Clément–Steinerberger, CR Math. 363 (2025), Theorem 1.
**Record not beaten.** Any published prefix length, any published digit of
$\alpha$, any statement about density.

**Not claimed.** Existence of $\lim a_n/n$; positivity of that limit;
any explanation of $\alpha$.

## Finite spectral fact (not a dent by itself)

On an independently generated prefix of $20\,000$ terms,
$\cos(2.5714474995\,a_n)<0$ except $\{2,3,47,69\}$, and the same four
exceptions persist throughout the McCranie bracket on $\alpha$. Mean
cosine $\approx -0.7934$. Replay: `compute/verify_spectral.py` and the
spectral check inside `compute/verify_all.py`. This is Steinerberger’s
observation, re-verified, not a new theorem.

## How to replay

```
cd problems/ulam-sequence/compute
python3 verify_all.py
```

That script does not re-enumerate $4.3\cdot 10^9$ words. It does:

- match OEIS A002858 (`b002858.txt`) against a fresh generator;
- recompute the integer products of the three winning words and the
  integer comparisons against $1454,1452,1445,1443,1442$;
- check that the reported word counts equal the closed recurrence
  $t_n=2t_{n-1}+2t_{n-2}$;
- re-enumerate $L=16$ in Python and match $F_2=150408$, word
  `2313131131311313`;
- check $a_n\le(1443/1000)^n$ on the first 200 terms, and that
  $n=3$ is the only $1.442$ failure in that range;
- replay the Steinerberger sign pattern on the first 5 000 terms.

To rebuild the large maxima from scratch (minutes to a few minutes per
length):

```
cc -O3 -o search_cs_F search_cs_F.c -lm
./search_cs_F 16
./search_cs_F 22
```

The full 2-norm enumerator (used to reproduce CS at $L=15$) is
`search_cs_bound.c`. Matrices are in `cs_matrices.py`.

## What is still open

Green #7 / Erdős #342, in full. The CS method, even at infinite $L$,
stops at $\approx 1.4146$ unless a new combinatorial prohibition on
words is proved. The actual sequence appears to grow linearly with slope
about $13.52$ and density about $0.074$; that remains experimental.
The hidden frequency $\alpha$ remains an experimental constant.

## Files

| path | role |
| --- | --- |
| `PROBLEM.md` | statement |
| `ATTACK.md` | chronological log |
| `WALKTHROUGH.md` | discovery narrative |
| `RESEARCH.md` | this file |
| `compute/ulam.py` | exact generator |
| `compute/cs_matrices.py` | $T_1,T_2,T_3$ |
| `compute/search_cs_bound.c` | 2-norm + Frobenius enumerator |
| `compute/search_cs_F.c` | exact Frobenius enumerator |
| `compute/search_F_python.py` | independent Python enumerator |
| `compute/certify_bound.py` | integer certificate for one word |
| `compute/bounds_table.py` | table and exact $N_0$ |
| `compute/verify_all.py` | one-command replay |
| `compute/certificate_L{16,21,22}.json` | winning words |
| `compute/bounds_table.json` | $L=1..22$ table |
| `compute/b002858.txt` | OEIS b-file |
| `figures/cs_growth_constants.png` | $C_L$ versus $L$ |
