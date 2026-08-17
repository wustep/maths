# Attack log — Density of the Ulam sequence

## 2026-08-17 — start

House: write only under `problems/ulam-sequence`. Target is a certified finite advance
(exact prefix, covering/automaton certificate, or a spectral fact with a verifier).
Plots without a theorem are residue. Do not claim the density exists unless proved.

Fetched the three required sources.

### Green 100 #7 (December 2025 update)

Define Ulam’s sequence \(1,2,3,4,6,8,11,13,16,18,26,28,36,\ldots\) by \(u_1=1\),
\(u_2=2\), and \(u_{n+1}\) the smallest number uniquely of the form \(u_i+u_j\) with
\(i<j\le n\). Does this sequence have positive density? Can one explain the curious
Fourier properties?

Comments point at Ulam and at Steinerberger’s \(\alpha\approx 2.5714474995\). A
related open question (Dickson / Queneau variants): are consecutive differences
eventually periodic? Also Erdős #341 and #342.

### OEIS A002858 (accessed 2026-08-17)

Classical Ulam numbers. Ulam conjectured density 0; McCranie’s computations to
\(6.759\cdot 10^8\) hover near density \(0.074\). Later records:

- \(a(5\cdot 10^7)=675904508\)
- \(a(10^8)=1351856726\)
- \(a(10^9)=13517664323\)
- \(a(2.8\cdot 10^{10})=378485625853\) (Gibbs–McCranie)

Only consecutive pair \(x,x+1\) below that range: \(1,2\) and \(47,48\).
Only consecutive-sum Ulam numbers in the first 28 billion terms: \(3=1+2\) and
\(131=62+69\). First differences and large-gap companions: A072832, A080287, A080288.

We will not beat a 28-billion-term prefix. An exact-prefix dent is closed.

### Steinerberger, *A hidden signal in the Ulam sequence*, Exp. Math. 26 (2017);
arXiv:1507.00267

Empirical \(\alpha\sim 2.5714474995\) with
\(\{\alpha a_n\bmod 2\pi\}\) absolutely continuous and non-uniform.
For the first \(10^7\) terms, \(\cos(2.5714474995\,a_n)<0\) except
\(\{2,3,47,69\}\). McCranie later gave
\(2.57144749846<\alpha<2.57144749850\). No closed form. Other “erratic”
initial data \((1,3)\), \((1,4)\), \((2,3)\) have analogous (different) frequencies.

### Current published theorems (not density)

- Sequence infinite; \(a_{n+1}\le a_n+a_{n-1}\) (trivial unique-sum of last two).
- Eggleton (in Recamán, AMM 1973): \(a_{n+1}\le a_n+a_{n-2}\), hence
  \(a_n\le\rho_E^n\) with \(\rho_E\) the real root of \(x^3-x^2-1=0\)
  (\(\rho_E\approx 1.46557\)).
- Clément–Steinerberger, *Small gaps in the Ulam sequence*, CR Math. 363 (2025),
  arXiv:2501.16285: Eggleton cannot hold twice in a row. Majorize by products of
  three \(4\times 4\) matrices \(T_1,T_2,T_3\) (Type I / Type II / Eggleton) with
  no two consecutive \(T_3\). Submultiplicative estimate at word length \(L=15\)
  gives \(a_n\le 1.454^n\) for large \(n\). Same argument cannot beat
  \(\rho(T_3 T_1^2)^{1/3}\approx 1.4146\). Also: some small gaps must exist,
  \(\min_{k\le n}a_{k+1}/a_k\le 1+c(\log n)/n\).
- Regular (eventually periodic difference) theory: Finch; Schmerl–Spiegel
  (\(U(2,2n+1)\) has exactly two evens); Cassaigne–Finch (\(U(4,4k+1)\) has
  exactly three evens). Does **not** apply to \(U(1,2)\).
- Hinman–Kuca–Schlesinger–Sheydvasser: rigidity for families \(U(a,b)\) as \(b\)
  grows; density of \(U(1,n)\) at most \((n+1)/(3n)\) (for \(n=2\) this is \(1/2\),
  useless for the classical sequence); several new regular pairs via a finite
  even-free certificate.
- Kravitz–Steinerberger: Ulam sets in \(\mathbb{Z}^d\).
- Erdős #342 (Bloom, last edit 2025-09-30; forum accessed 2026-08-17): still
  **open**, “cannot be resolved with a finite computation”. Zero claimed proofs.
  Forum note (Jan 2026) explicitly suggests optimizing the CS constant \(1.454\).

### Agama arXiv:2007.02697v12 (dated 2026)

Claims density zero via “circles of partition” and addition chains. Not cited by
Green (Dec 2025) or by Erdős #342 (2026-08-17). We treat it as unaccepted and do
not use it. A density claim is not a finite certificate in any case.

### Judge (Codex, 2026-08-16)

`dentable_tonight: 2`, reject `no-finite-handle`. The specified tonight quest
is none. The house prompt nevertheless asks for a certified finite advance.
The only published finite-handle with a number we can beat is the CS growth
constant \(1.454\), obtained by a finite word-max of an operator norm.

## Quest

1. Independently generate a verified Ulam prefix (match OEIS A002858 b-file /
   listed terms). Replay Steinerberger’s cosine inequality on that prefix with a
   verifier. This is documentation, not a dent.
2. Independently recompute the CS \(L=15\) quantity. If it matches \(1.4539\ldots\),
   the published \(1.454\) is reproduced.
3. Compute the same quantity at larger \(L\), and/or under extra combinatorially
   proved forbidden words, and/or under a conjugated / extremal norm. If the
   resulting \(C\) is strictly less than \(1.454\), that is a certified improvement
   of the published growth bound.
4. Do not claim the natural density exists.

Search residue (plots, empirical density \(\approx 0.074\), unproved automata)
is not a bound.

## 2026-08-17 — sources finished, first computations

Independent Ulam generator matches OEIS A002858 b-file: 10 000 terms, last
term \(a(10000)=132788\). Two generators (value-sieve and first-\(k\)) agree.

Steinerberger cosine test on the first 20 000 terms, at both the 2015 working
value \(2.5714474995\) and the McCranie bracket
\((2.57144749846, 2.57144749850)\): \(\cos(\alpha a_n)<0\) except exactly
\(\{2,3,47,69\}\). Mean cosine \(\approx -0.7934\), matching Steinerberger's
\(c_1\approx -0.794\). Harmonic packet \(c_\ell\) for \(\ell\le 8\) matches
his Table 1 to two digits. This is a documented finite spectral fact with a
verifier. It is not a proof that a limiting measure exists.

## 2026-08-17 — false start: extra forbidden CS words

Classified every step of the first 20 000 Ulam numbers as Eggleton / Type I /
Type II / other. After the opening
\(4=3+1\) (E), \(6=4+2\) (E), \(8=6+2\) (I), \(11=8+3\) (I), every later
step is “other”. Largest true gap in this range is 315 (Knuth). Typical gap
over the Eggleton scale \(a_{n-2}\) is \(10^{-4}\).

So the CS recurrences almost never fire on the actual sequence. That does
**not** let us drop \(T_1,T_2,T_3\) from the majorant: the majorant is a
worst-case envelope over every sequence obeying the CS lemmas, and the
adversary may still take Type I / II / Eggleton whenever those lemmas allow.
Proving they never fire again is essentially the linear-growth problem.
Extra smaller matrices (Type IV etc.) also do not help the worst-case max.
The only finite handle is a longer word-max, or a new lemma forbidding a
positive-density set of words.

Agama arXiv:2007.02697v12 claims density zero via “circles of partition”.
Not cited by Green (Dec 2025) or by Erdős #342 (accessed 2026-08-17, zero
claimed proofs). We do not use it.

## 2026-08-17 — click: recompute CS \(L=15\), then extend

Implemented the three \(4\times 4\) matrices exactly as in CS §2.
Admissible language: \(\{1,2,3\}^*\) with no consecutive \(3\)s.
Word count matches the recurrence \(t_n=2t_{n-1}+2t_{n-2}\)
(\(t_1=3,t_2=8\)): \(t_{15}=3799168\), \(t_{16}=10379520\),
\(t_{22}=4316282880\).

Independent \(L=15\) 2-norm max: \(C_2=1.453902202043493\), extremal word
`231313113131313`. This reproduces CS’s \(1.4539\ldots\), which they rounded
to \(1.454\). Their printed “extremal word \((T_3T_1)^3(T_1T_3)^3T_2\)” has
length 13 and is *not* the maximizer (its \(C_2\approx 1.439\)); the
surrounding \(1.4539\) figure is the one that matches a full enumeration.

Eggleton root \(1.4655712318767682\). Method barrier
\(\rho(T_3T_1^2)^{1/3}=1.4146717609798722\).

## 2026-08-17 — exact Frobenius certificate, record beaten

Frobenius norm is submultiplicative and \(\|W\|_2\le\|W\|_F=\sqrt{\sum W_{ij}^2}\)
with an integer sum of squares. Exhaustive max of that integer, over the
whole admissible language, is a fully exact growth bound.

| \(L\) | \(\#\) words | \(\max\|W\|_F^2\) | \(C_F=(\max F_2)^{1/(2L)}\) | beats \(1.454\) |
| ---: | ---: | ---: | ---: | :---: |
| 15 | 3 799 168 | 75 172 | 1.453902232781 | yes (CS) |
| 16 | 10 379 520 | 150 408 | 1.451408682527 | yes |
| 20 | 578 272 256 | 2 417 294 | 1.444053344939 | yes |
| 21 | 1 579 869 184 | 4 845 788 | 1.442697712198 | yes |
| 22 | 4 316 282 880 | 9 690 750 | 1.441387826311 | yes |

\(L=16\) already beats the published \(1.454\) by an integer comparison
\(150408\cdot 1000^{32}<1452^{32}\). Independently re-enumerated in Python
with the same word and the same \(F_2\).

Best run: \(L=22\), word `2313131131313131311313`, \(F_2=9690750\),
\(9690750\cdot 1000^{44}<1442^{44}\). Word-count matches \(t_{22}\).
Python recomputes the integer matrix of the winning word and the sum of
squares; it does not re-enumerate \(4.3\cdot 10^9\) words (the \(L\le 16\)
Python/C agreement audits the enumerator).

Unfolding the CS majorant from \(v_5=(6,4,3,2)\), \(\|v_5\|_2^2=65\):

- \(a_n\le(1443/1000)^n\) for every \(n\ge 1\)
  (direct integer check on a generated prefix through \(n=3304\), plus the
  \(L=21\) majorant for \(n\ge 3304\)).
- \(a_n\le(1442/1000)^n\) for every \(n\ge 1\) except \(n=3\)
  (only failure in \(1..1634\) is \(a_3=3>(1442/1000)^3\); \(L=22\) majorant
  from \(n=1635\)).

Published record beaten: Clément–Steinerberger, CR Math. 363 (2025),
Theorem 1, \(a_n\le 1.454^n\) for large \(n\).
We do **not** claim that the natural density exists.

Replay: `python3 compute/verify_all.py`.
Certificates: `compute/certificate_L16.json`, `certificate_L21.json`,
`certificate_L22.json`, `compute/bounds_table.json`.
Figure: `figures/cs_growth_constants.png`.
