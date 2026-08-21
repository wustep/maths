# Walkthrough — A longer word, an integer norm

- Problem: `problems/ulam-sequence` (P20 / Green 100 #7)
- Date: 2026-08-17
- Argument status: certified finite improvement of a published growth bound
- Problem status: open. Density is not shown to exist. The hidden signal is
  not explained.

## 0. What was actually missing

The density of $U(1,2)$ is not a finite question. The missing degree of
freedom on a one-night clock was already isolated by Clément–Steinerberger
in 2025, and then left on the table: their growth bound is a *maximum of
finitely many matrix norms*. They evaluated that maximum at word length
$L=15$, obtained $1.4539\ldots$, and published $1.454$. They wrote
explicitly that more cases would improve the constant, and that the method
cannot pass $\rho(T_3T_1^2)^{1/3}\approx 1.4146$.

What was missing was not a new dynamical idea. It was the rest of that
finite maximum, written so that a second machine can check the integer.

## 1. Named false starts

- **A longer exact prefix.** Gibbs–McCranie have $a(2.8\cdot 10^{10})$.
  An overnight generator will not beat that record. House rule: cite the
  record you beat, or say you did not. We did not.

- **An automaton for $U(1,2)$.** Regular Ulam sequences (eventually
  periodic differences) are completely understood when only finitely many
  evens appear. $U(1,2)$ has many evens. Hinman–Kuca–Schlesinger–Sheydvasser
  rigidity describes *families* $U(1,n)$ as $n$ grows, not a finite-state
  law for the classical sequence. No covering certificate appeared.

- **A proof that the density exists, or that it is positive.** That is
  Green #7. Agama’s arXiv:2007.02697v12 claims density zero; Green’s
  December 2025 list and Erdős #342 (accessed 2026-08-17, zero claimed
  proofs) do not accept it. We did not use it.

- **Forbidding Eggleton / Type I / Type II after the opening.** On the
  first 20 000 Ulam numbers those three CS recurrences fire only four times,
  all before $a_7=11$. That is striking and useless for the majorant.
  The majorant is an *adversary* that may take any combinatorially legal
  jump. Proving the jumps never return is the linear-growth problem in
  disguise.

- **Adding smaller matrices.** If the true step is “other”, one can bound
  it by $a_n+a_{n-4}$ and friends. The worst-case product still uses
  $T_1,T_2,T_3$ wherever the lemmas permit. Extra letters do not cut the
  maximum.

- **Conjugated / extremal norms.** A natural next tightening. SciPy was
  not in the environment; the exact Frobenius maximum already beat the
  published number, so this was left as residue.

## 2. The useful failure

The step classification was the useful failure. It showed that the CS
envelope is almost never tight on the genuine sequence, and therefore that
no amount of staring at actual gaps will, by itself, improve the published
exponent. The exponent is the joint spectral radius of a *language of
matrices*, not a statistic of $U(1,2)$.

Once that is seen, the only finite move is to compute that language more
carefully than $L=15$.

The same computation produced a second, unexpected, piece of bookkeeping.
The 2-norm maximizer at every $L$ we ran is essentially rank-one: its
Frobenius norm agrees with its 2-norm to eight digits. The exact integer
$\sum W_{ij}^2$ is therefore not a blunt majorant. It is, for these
particular winning words, the same number.

## 3. The click

Clément–Steinerberger reduce growth to three $0$-$1$ matrices

$$
T_1=\begin{pmatrix}1&0&0&1\\1&0&0&0\\0&1&0&0\\0&0&1&0\end{pmatrix},
\quad
T_2=\begin{pmatrix}0&1&1&0\\1&0&0&0\\0&1&0&0\\0&0&1&0\end{pmatrix},
\quad
T_3=\begin{pmatrix}1&0&1&0\\1&0&0&0\\0&1&0&0\\0&0&1&0\end{pmatrix},
$$

acting on $(b_n,b_{n-1},b_{n-2},b_{n-3})^\top$, with one prohibition:
Eggleton cannot be attained twice in a row, so $T_3T_3$ is illegal.
Any submultiplicative matrix norm then gives, for every admissible word
length $L$,

$$
a_n\le K_L\,C_L^n,\qquad C_L=\max\|W\|^{1/L}.
$$

They used the operator 2-norm at $L=15$. The click is that the Frobenius
norm is also submultiplicative, dominates the 2-norm, and turns the
maximum into a comparison of two integers:

$$
\Bigl(\max\sum_{i,j}W_{ij}^2\Bigr)^{1/(2L)}
<\frac{p}{1000}
\quad\Longleftrightarrow\quad
\Bigl(\max\sum W_{ij}^2\Bigr)\cdot 1000^{2L}<p^{2L}.
$$

Recompute $L=15$ to lock the published $1.4539$. Then increase $L$.

## 4. The argument, in the order it was found

Start the majorant at the same place CS do: $b_n=a_n$ for $n\le 5$, so
the first state is $v_5=(6,4,3,2)$ and $\|v_5\|_2^2=65$. After that,
every step of the majorant is left-multiplication by $T_1$, $T_2$, or
$T_3$, never $T_3$ twice. Write $n=5+Lq+r$ with $r<L$. Then

$$
a_n\le\|v_n\|_2\le\|W_q\|_F\,\|W_r\|_F\,\|v_5\|_2,
$$

and $\|W_q\|_F\le(\max\|W\|_F)^q$. The maximum on the right is a finite
search: $t_L$ words, $t_L=2t_{L-1}+2t_{L-2}$.

The $L=15$ search returns $C_2=1.453902202043493$ on the word
`231313113131313`, and $C_F=1.453902232781$ from $F_2=75172$. That is
CS’s $1.4539$, independently.

At $L=16$ the same enumerator, in C and again in Python, returns
$F_2=150408$ on `2313131131311313`. The integer comparison
$150408\cdot 1000^{32}<1452^{32}$ is then a one-line certificate that
$C_{16}<1.452<1.454$.

Pushing the Frobenius search to $L=22$ ($4\,316\,282\,880$ words,
count matching $t_{22}$) gives $F_2=9\,690\,750$ on
`2313131131313131311313`, and $C_{22}<1.442$. The $L=21$ run similarly
gives $C_{21}<1.443$.

Unfolding the majorant against $1443/1000$ first holds for every remainder
at block $q=158$, i.e. from $n=3304$. The Ulam numbers themselves
satisfy $a_n\le(1443/1000)^n$ on the whole prefix $n\le 3304$ by direct
integer comparison (the only delicate small values are $n=1,2,3,4$; after
that the exponential is already larger than $13.5n$). Glueing the two
halves:

$$
a_n\le\Bigl(\frac{1443}{1000}\Bigr)^n\qquad\text{for every }n\ge 1.
$$

Against $1442/1000$, the majorant holds from $n=1635$, and the only
prefix failure in $1..1634$ is $a_3=3>(1442/1000)^3$. So the same
argument gives $a_n\le(1442/1000)^n$ for all $n\neq 3$.

Nothing here implies that $\lim a_n/n$ exists, or that the limit is
positive. The majorant is still exponential; the sequence still looks
linear. The gulf CS complained about is smaller by $0.011$ and remains
a gulf.

## 5. Computer residue

- OEIS A002858 b-file, 10 000 terms, last entry $132788$: matched.
- Step census on 20 000 terms: Eggleton twice, Type I twice, then only
  “other”. Residue, not a lemma.
- Steinerberger cosine on 20 000 terms: four published exceptions, mean
  cosine $-0.7934$, packet $(c_\ell)_{\ell\le 8}$ as in his Table 1.
  Finite spectral fact; not a limiting measure.
- Growth table $L=1..22$: `compute/bounds_table.json`.
- Winning words and integer matrices: `compute/certificate_L{16,21,22}.json`.
- Independent Python enumeration at $L=16$: same word, same $F_2$.
- Replay of every claimed comparison except the $4.3\cdot 10^9$-word
  search: `python3 compute/verify_all.py`.
- Plot of $C_L$ against $L$: `figures/cs_growth_constants.png`.

The CS printed word $(T_3T_1)^3(T_1T_3)^3T_2$ is length 13 and is not
maximal; we treat that sentence as a slip and treat their $1.4539$ as
the actual $L=15$ figure, which we reproduced.

## 6. What is proved vs still open

**Proved (this folder).** Let $a_n$ be the classical Ulam sequence.
Following the Clément–Steinerberger majorant, with the $L=21$ (resp.
$L=22$) Frobenius maximum in place of their $L=15$ 2-norm maximum,

$$
a_n\le\Bigl(\frac{1443}{1000}\Bigr)^n
\quad\text{for all }n\ge 1,
$$

and

$$
a_n\le\Bigl(\frac{1442}{1000}\Bigr)^n
\quad\text{for all }n\neq 3.
$$

This beats Clément–Steinerberger, *Small gaps in the Ulam sequence*,
CR Math. 363 (2025), Theorem 1 ($a_n\le 1.454^n$ for large $n$).
The method still cannot beat $\approx 1.4146$ without a new forbidden
word.

**Documented, not proved.** Steinerberger’s cosine inequality on every
prefix we generated; empirical density $\approx 0.074$; the McCranie
bracket on $\alpha$; the rarity of Eggleton/Type I/II after $a_7$.

**Still open.** Existence of the natural density; positivity of the
density; a proof-level account of the frequency $\alpha$; eventual
periodicity of differences; infinitely many consecutive pairs
$a,a+2$; infinitely many even terms as a theorem rather than an
observation. Green #7 and Erdős #342 are unchanged.
