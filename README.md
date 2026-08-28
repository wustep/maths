# maths

A public notebook of attacks on open problems.

Stephen orchestrates the agents via Grok Bot. Each run hands Codex,
Claude, Grok, or another model an open math problem and asks it to
make some progress. Agents log their attempts, findings, and compute
scripts in the repo. Models are named in the ledger below.

This README and the explainers are for human readers. The other files
in a problem folder (ATTACK.md, WALKTHROUGH.md, the PROBLEM.md status
line, the skills) are working notes and may use two agent terms. A
dent is a verified finite improvement of a published record. A residue
is an incomplete search.

## Interesting results

So far there is one.

### Covering: $\ell_2(10,2)\le 50$

A binary linear code of length 50 and dimension 40 has covering radius
exactly 2. Equivalently, the $10\times 50$ parity-check matrix
`problems/covering/compute/H_r10_n50.txt` hits every syndrome in
$\mathbb{F}_2^{10}$ as a sum of at most two columns (1024/1024,
two independent verifiers). That is

$$
\ell_2(10,2)\le 50.
$$

The November 2025 table (Davydov–Marcugini–Pambianco, arXiv:2511.02542,
Table 5.1) had $\ell_2(10,2)\le 51$. This is a construction, an upper
bound, not a conjecture. Sphere covering still only gives $\ge 45$,
and an $n=49$ search left 7 holes, so 50 is not shown optimal.

The same matrix has a $(2,0)$-partition with $p(H)=10$. The
$\mathrm{QM}_2^2$ construction then produces longer codes
($r=18$, $n=815$; $r=20$, $n=1631$) and the density bound
$\bar\mu(2)\le 2601/2048\approx 1.27002$. That is the interesting
part: a finite seed that moves the asymptotic constant, not just a
table entry.

The same seed, via

$$
\mathrm{QM}_3^2,\ \mathrm{QM}_5^2
$$

(arXiv:2511.02542 Thm 5.1), gives independently replayed lengths

$$
\ell_2(22,2)\le 3325,\ \ell_2(24,2)\le 6653,\ \ell_2(26,2)\le 13070,\ \ell_2(28,2)\le 26111
$$

(paper 3389, 6781, 13565, 26623). Full $2^r$ sweeps, including
$2^{28}$.

The $r=26$ matrix has a verified 19-block partition, so
$\mathrm{QM}_2^2$ gives a theorem-only lift.

That length is $\ell_2(36,2)\le 418271$.

The $r=28$ matrix has a verified 28-block partition, so
$\mathrm{QM}_2^2$ propagates theorem-only to

$$
\ell_2(40,2)\le 1671167,\ \ell_2(42,2)\le 3342335,\ \ell_2(44,2)\le 6684671
$$

(not enumerated). Same seed plus Golay gives
$\ell_2(26,3)\le 817$ (paper 818).

$\mathrm{QM}_4^4$ with the same 50-set gives a blockwise
certificate for $2^{31}$.

The bound is $\ell_2(31,4)\le 689$ (paper 690).

The $r=18$ and $r=20$ lifts have verified partitions

$$
p(H_{18})\le 17,\ p(H_{20})\le 14
$$

so $\mathrm{QM}_5^3$ gives theorem-only

$$
\ell_2(38,3)\le 13102,\ \ell_2(41,3)\le 26206
$$

(paper 13118, 26238; not enumerated). Replay:
`problems/covering/compute/run_qm3_checks.sh`,
`run_qm5_checks.sh`, `run_qm35_checks.sh`,
`run_p64_checks.sh`, `run_p28_checks.sh`, `run_qm44_checks.sh`,
`run_q7c_checks.sh`, `run_qm21_checks.sh`, and
`run_qm43_checks.sh`.

Replay:

```bash
python problems/covering/compute/verify_certificate.py
cd problems/covering/result && ./run_all.sh
```

Standalone writeup in [problems/covering/result](problems/covering/result).
Explainers: [HTML](problems/covering/explainer.html),
[PDF](problems/covering/explainer.pdf).

## Problems

| Folder | Status |
| --- | --- |
| [erdos-szekeres-seven](problems/erdos-szekeres-seven) | The published record is $33 \leq ES(7) \leq 113$. The classical 32-point witness is independently replayed in Python and C. A compact signotope encoding has a checked small DRAT proof; its full 33-vertex run returned `UNKNOWN` after 300 seconds, so no bound changed. |
| [covering](problems/covering) | $$\ell_2(10,2)\le 50,\ \ell_2(21,3)\le 303,\ \ell_2(26,2)\le 13070,\ \ell_2(26,3)\le 817,\ \ell_2(31,4)\le 689,\ \ell_2(36,2)\le 418271,\ \ell_2(38,3)\le 13102,\ \ell_2(41,3)\le 26206$$; $\mathrm{QM}\ 22/24/28$ and $$p(H_{18})\le 17,\ p(H_{20})\le 14,\ p(H_{26})\le 19,\ p(H_{28})\le 28$$. $n=49$ still 7 holes; q9 recovers the 2003 Kaikkonen–Rosendahl 51-set, shows 51 and 50 are not lifts of the $r=8$ record in any of the 174251 quotients, and exhaustively rules out 271127 of the 279034 single-block shrinks of the 50-set with block width $\le 12$. q10 prescribes an automorphism instead of perturbing the 50: order 7 is settled at $r=10$ for every fixed-space dimension, and with orders 11, 17, 31, 73, 127 also excluded, any 49-set has a $\{2,3,5\}$-group of automorphisms. At $r=11$ no invariant set below the record 79 exists for orders 11, 17 or 23. q11 adds a fibered "graph plus kernel" family — one column over every nonzero point of a quotient, plus a kernel block — whose radius-2 condition is a line colouring of $\mathrm{PG}$; it contains the documented lengths at $r=4,7,8,9$, is exactly decided for $r\le 8$ (so it reproduces $\ell_2(8,2)\le 26$ and cannot beat it), and provably cannot produce any $n\le 47$ at $r=10$, where its own best is 54. The nearest miss is at $r=9$: $n=38$ would beat $\ell_2(9,2)\le 39$ and reduces inside the family to exactly 17 kernel-block classes, all 17 of which anneal to the same floor of 14 missing incidences and none of which the exact solver decides. |
| [brocard](problems/brocard) | Four infinite prime-offset families excluded by Wilson's theorem: $n=p-2$ or $p-3$ for primes $p\equiv3,5\pmod 8$ (with $p>3$ in the second form). Conjecture open. |
| [unique-sum](problems/unique-sum) | Independently replayed OEIS A398173 through $p=53$. At $p=59$, a checked 15-set gives $m(59)\le15$; size at most 14 remains undecided after a 100-million-node exact search. |
| [three-in-line](problems/three-in-line) | Replayed Heule's rct4 142-set at $n=71$: $D(71)=142$. At the first current hole, $n=75$, an audited rct4 portfolio ended without a 150-set. |
| [schur](problems/schur) | No 1697-coloring found. |
| [vdw-w27](problems/vdw-w27) | Verified Paley/QR coloring of $[3703]$. Does not extend to 3704. No improvement. |
| [c7-shannon](problems/c7-shannon) | Verified Polak–Schrijver 367-set in $C_7^{\boxtimes 5}$. No 368. Missing a letter in any coordinate caps the set at 345. Hamming distance 11 from the published set is empty. No improvement. |
| [landau-legendre](problems/landau-legendre) | Landau 3. Assuming RH, primes occur between consecutive $(2+\delta)$-powers for every real $x\geq1$ when $\delta\geq0.22525$, tightening the printed $0.2253$. Both Oppermann halves were independently replayed for the last 100,000 square intervals below $2^{64}$. The published finite record remains $n=7.05\cdot10^{13}$, and Legendre's conjecture remains open. |
| [landau-n2-plus-1](problems/landau-n2-plus-1) | Landau 4. Certified 54110 primes $n^2+1$ for $n\le 10^6$, matching Wolf $\pi_q(10^{12})$. Infinitude open. |
| [sidon-second-term](problems/sidon-second-term) | Independent 11-kernel certificate: $$F(N)\le N^{1/2}+0.94301\,N^{1/4}+O(1)$$. Beats Hou–Zhao arXiv:2607.01169v2 (0.9435). |
| [chowla-cosine](problems/chowla-cosine) | $K(n)\ge n^{1/7}/18$ for all $n\ge 1$. Does not beat Bedert $n^{1/5-o(1)}$. |
| [unit-distance-509](problems/unit-distance-509) | Rebuilt Parts 509, 5-chromatic and vertex-critical. No smaller graph found. Record still 509. |
| [hadwiger-nelson-plane](problems/hadwiger-nelson-plane) | Published interval $5\le\chi(\mathbb R^2)\le7$. A 2,434-vertex exact Parts spawn combining a 677-point reserve and four rotation layers is five-colorable; its model also covers arbitrary base-vertex deletion within this fixed family. No new lower bound. |
| [cosine-zeros](problems/cosine-zeros) | $Z(N)\ge\log\log N/(200\log\log\log N)$ when RHS $\ge 4$. Does not beat Bedert's exponent. |
| [two-squares-gap](problems/two-squares-gap) | Jameson $a=3$ on $n\le 1.024\cdot 10^{15}$ except $\{3,6,21,91\}$ (m $\le 250$ cert replayed). Green's $1/10$ open. |
| [ulam-sequence](problems/ulam-sequence) | L=22 word with $C_F<1.442$, beating CS 1.454. Density open. |
| [long-gap-dilate](problems/long-gap-dilate) | SAT $G(p,\mathrm{round}\sqrt p)$ through $p=73$. No universal $C>2$. Record still Shakan 2. |
| [thin-cyclic-bases](problems/thin-cyclic-bases) | BEL $\sqrt{8/3}$ family replayed through $q=61$. No thinner liminf. $\sqrt2$ open. |
| [union-closed](problems/union-closed) | Certified frequency $0.38305$ on the two-point family {b,1} under Liu Example 4. Analytic first-crossing $0.3830513565\ldots$; a 9,000 by 7,000 Python/C mesh has minimum ratio $1.0000049143$. This improves the prior printed $0.38304$ and Liu's $0.382709$. Frankl's one-half target remains open. |
| [cohn-elkies](problems/cohn-elkies) | Exact $R=3627599/500000=7.255198$, beats printed Table 4 $7.25520$. Not a magic function. |
| [kissing-5d](problems/kissing-5d) | All four 40-point codes (D5, L5, Q5, R5) are polar-maximal (polar max $$5/4$$). Integer Delsarte on the Q5 angles excludes size 44. Exact 3-point matrices over the rationals; no unrestricted dual below 44. The leftover (1/4)Z^5 graph has no 41-set using 22 or more D5-type points, no leftover 41-set hosted by four D5 coordinate-stars, and no leftover 41-set hosted by a type-(2,1) or type-(1,3) five-star (native CaDiCaL DRAT verified). The 355-point T^5 remainder has no 36-clique (native CaDiCaL DRAT verified). Range still $$40\le\tau_5\le 44$$. |
| [affine-013](problems/affine-013) | $T(S)\le\lceil n^2/2\rceil$ for affine copies of $\{0,1,3\}$. Beats Aaronson $3/4$. Conjecture $1/3$ open. |
| [zero-one-polynomials](problems/zero-one-polynomials) | BSKK $\theta=0.00373556$ (published $0.003736$ over-round). Census $n\le 20$. $p_n\to 1$ open. |
| [one-third-two-thirds](problems/one-third-two-thirds) | Gupta v2 is a full order-14 balance census (least above $1/3$ is $37/106$). Width-3 $W_{10}$ at $6/17$ is the width-3 minimum through 14. Broken-rung ladder minima independently replayed through 14 and computed through 22. Three-rail minima through 15 stay above $6/17$. Interval orders through 10 stay at or above $1/3$. Conjecture open. |
| [seymour-second-neighborhood](problems/seymour-second-neighborhood) | Explicit n=8 Pisa graphs with irregular missing degrees $3^2 2^6$, $3^4 2^4$, $3^6 2^2$. Seven stored witnesses replayed. Did not re-run the 2.5B census. Conjecture open. |
| [two-smooth-summands](problems/two-smooth-summands) | Incomplete search. $F(131486759)=83$, not a $79$-smooth sum. $G(y)$ through $y=79$ replayed. No exponent below Balog $4/(9\sqrt{e})$. Green #59 open. |
| [tuza-triangle-packing-covering](problems/tuza-triangle-packing-covering) | 8-regular codegree-7 Puleo pair: 1044 cores independently checked (STS(9) on $K_7$). Does not prove Tuza for $\Delta\le 8$. |
| [caccetta-haggkvist-k3](problems/caccetta-haggkvist-k3) | Exact CH-triangle at n=18, 21, 24, 26, 27, 29, 30, 32, 33, 35, 36 and every leftover order through n=130 (534 stored DRATs through n=72, 1026 through n=108, 213 through n=114, 36 through n=115, 37 through n=116, 38 through n=117, 37 through n=118, 38 through n=119, 39 through n=120, 38 through n=121, 39 through n=122, 40 through n=123, 39 through n=124, 40 through n=125, 41 through n=126, 40 through n=127, 41 through n=128, 42 through n=129, then 41 through n=130, then 42 through n=131, then 43 through n=132, then 42 through n=133, then 43 through n=134, then 44 through n=135, then 43 through n=136, then 44 through n=137, then 45 through n=138). First remaining hole n=139. $$F_4\text{ certificate }c=0.34640\text{ (CKLS 2015 fork), below HKN }0.3465\text{ and the prior stored }0.34645.$$ Did not beat 0.3388. Conjecture 1/3 open. |
| [projective-plane-order-twelve](problems/projective-plane-order-twelve) | Two involution 2-MOLS replayed (intercalates $108+108$ vs $90+78$). $t=3$ timeout. Published Aut still $\lvert G\rvert\in\{1,2,3\}$. Plane open. |
| [ramsey-r55](problems/ramsey-r55) | McKay 328+328 $(5,5,42)$ graphs replayed; circulant 42/43 empty. Interval still $43\le R(5,5)\le 46$. |
| [graph-reconstruction-next-order](problems/graph-reconstruction-next-order) | Full independent degseq census: all 8,571,837 n=14 graphs are $4^{11}6^{3}$; 17,143 `labelg` samples matched. Uniqueness (hence reconstructibility) not independently re-sorted. McKay n=13 unchanged. |
| [lonely-runner-fourteen](problems/lonely-runner-fourteen) | Every 13-tuple of coprime speeds with $$u_i \equiv i \pmod{p}$$ has the lonely runner property, for each of the ten primes 191 through 239, checked exhaustively in about four minutes apiece. So the tight tuple $(1,2,\dots,13)$ — which the published work reports as the sole survivor of its doubling ladder — is eliminated at all ten, with no lift by 7 or 14. The check fails for primes up to 41, so the modulus is doing real work. Sungkawichai–Trakulthongchai (arXiv:2604.23906) prove the analogue only when the number of runners is prime, and 14 is not. Cross-checked against brute force at 6 and 8 runners. Not a bound on the number of runners: the 14-runner case is open, and the published bottleneck is untouched. |
| [fekete-s2](problems/fekete-s2) | Replayed Ridgway–Cheviakov 2018 Table 3 for $N=2$–$65$. No improvement. Smale 7 open. |
| [smale-jacobian-n2](problems/smale-jacobian-n2) | Smale 16 / plane Jacobian conjecture. Guccione–Guccione–Horruitiner–Valqui left only $(72,108)$, up to transposition, below maximum degree 125. A pinned exact unit-ideal certificate replay, with an independent Python/Rust check of the published polygon bridge, excludes that pair. Thus every hypothetical plane counterexample has $$\max\{\deg P,\deg Q\}\ge125.$$ The conjecture remains open; the 2026 three-variable announcement is not treated as community consensus. |
| [hilbert16-degree-8](problems/hilbert16-degree-8) | Seventeen real schemes realized as T-curves sit outside the 2,367 of arXiv:2602.06888v3, so that census lower bound is $\ge 2{,}384$. All 2,367 published certificates replayed. Haas zone decompositions checked against all 38 published M-certificates. Every census triangulation swept exhaustively (230.5 million sign distributions) realizes exactly their 38 M-schemes and no others; 4,609 further triangulations add none. A later radius-1 thicken of the sign-vector stratum finished all 164 leftover census triangulations of twist-rank at most 20, then all five of twist-rank 21, and found only schemes already among the seventeen. Fifteen leftover triangulations of ranks 22 through 26 are still open, as are the two undecided deep nests. Hilbert 16(a) degree 8 open. |
| [hilbert16-limit-cycles](problems/hilbert16-limit-cycles) | Hilbert 16(b): the Hilbert number H(n), maximum isolated periodic orbits of a planar polynomial vector field of degree n. Published lower bounds still stand: H(2) at least 4 (Shi; Chen–Wang), H(3) at least 13 (Li–Liu–Yang), H(4) at least 28 (Prohens–Torregrosa), and the Han–Li / Chebyshev lifts. A quadratic with 5 cycles, a cubic with 14, a homogeneous nest, a Liénard beat of B(n), iterated squaring past the quadratic ceiling, a Harnack-recurrence table beat, a 29th cycle on the Prohens–Torregrosa quartic, a two-well 14, a four-zero quasi-homogeneous Melnikov, a 9-sheet holomorphic cube, a beat of Z(2,n), a constructive +1 with two cycles, a cubic with an invariant line and three cycles, five Abelian zeros, a four-fold or T2 beat of H(7) at least 74, a cubic Kolmogorov with 7 cycles, an L2 extra nest, and a degree-5 radial product with two cycles were not constructed. Replayed: Shi’s order-3 jet, van der Pol uniqueness, the Chebyshev pullback identity and its 2026 table arithmetic, uniqueness for one radial cubic, the first Lyapunov quantity of a quadratic focus, homogeneous scaling, the odd-cubic Liénard energy identity, iterated-squaring sheet counts, the Harnack-recurrence arithmetic, the explicit degree-4 Darboux seed with three centers, the two-well energy and figure-eight integral, vanishing of L1 at those three centers, first-order cyclicity at most 1 for one cubic perturbation of the quasi-homogeneous center, the holomorphic-cube sheet count, the radial family attaining Z(2,n), a degree-4 line product with one circle, a named cubic with an invariant line and no cycles, an explicit Christopher–Lloyd degree-7 four-oval field, an explicit T2 degree-7 four-oval field, a cubic Kolmogorov Dulac in the first quadrant, the second Poincaré quantity at the two-well, and the degree-5 radial product with one circle. No published H(n) moved. Different problem from the degree-8 folder above. |
| [simon-lieb-thirring](problems/simon-lieb-thirring) | Later record is Carvalho Corso–Ried (arXiv:2403.04347v2) $$L_{1,1,1}/L_{1,1,1}^{\mathrm{cl}}\le 1.44655\quad(M_3=0.371185695).$$ Independently the Clausen form of that value is at most 1.4465531. Did not beat 1.44655. The 2018 FHJN trial pair was 1.456; a certified pair on this notebook still gives 1.45576 and does not beat CCR. Conjecture open. |
| [simon-ionization-excess](problems/simon-ionization-excess) | Simon 2000 #9. Replayed Lieb $2Z+1$, Nam $1.22$, and Hundertmark–Pattakos–Schulz. Remainders $2.953$, $3.892$, $3.9781$ from the $Z\ge 4$ ratio. Leading coefficient moved from printed $1.1185$ through $1.1118$, $1.1057$, $1.1035$, $1.1026$, $1.1021$, $1.1020$, and $1.1017$ to $1.1013$ by tightening the compact mid-radius bound and lifting it at aspect 10. Hydrogen N0(1)=2 replayed. Bounded excess open. |
| [simon-ids-continuity](problems/simon-ids-continuity) | Simon 2000 #14. Bourgain–Klein proves log-Hölder continuity for arbitrary bounded continuum potentials in dimensions 1–3 and for discrete operators in every dimension. An exact Python/Rust replay locates their continuum frontier at $d=4$, where the modulus exponent $(4-d)/8$ becomes zero. Frank–Ivanisvili's 2026 real bounded Landis examples make the underlying $4/3$ power sharp for this route. Adding a free Euclidean direction gives an absolutely continuous DOS by the standard separable convolution identity. General bounded ergodic continuum potentials in dimensions at least 4 remain open. |

Each problem folder:

```
PROBLEM.md        statement and what would count as a new bound
ATTACK.md         chronological attempts
WALKTHROUGH.md    discovery notes, not a cleaned proof
RESEARCH.md       papers, OEIS, failed lookups
compute/          scripts, certificates, tables
lean/             only if there is a lemma
```

## Notes

Lists, dated picks, the SuperGrok 2026-08-17 run, and a Grok Bot
transcript recreation live under [notes/](notes/). Agent runbook:
[AGENTS.md](AGENTS.md).

## Which model ran what

| Problem | Folder | Models | When |
| --- | --- | --- | --- |
| Erdős–Szekeres ES(7) | `problems/erdos-szekeres-seven` | GPT-5.6 Sol | 2026-08-23 |
| covering / $\ell_2(10,2)$ | `problems/covering` | Sol 5.6, Opus 5, Fable 5, Grok 4.6 | 2026-08-16–21 |
| covering / 24 August search section | `problems/covering/compute` | Grok 4.6 | 2026-08-24 |
| covering / prescribed automorphisms ($r=10,11$) | `problems/covering/compute/q10` | Claude Opus 5 | 2026-08-21 |
| covering / fibered graph family ($r=4\text{–}11$) | `problems/covering/compute/q11` | Claude Opus 5 | 2026-08-21 |
| Brocard–Ramanujan | `problems/brocard` | Sol 5.6 | 2026-08-16 |
| Brocard–Ramanujan prime-offset modular families | `problems/brocard/compute/q3` | GPT-5.6 Sol | 2026-08-23 |
| unique-sum mod p | `problems/unique-sum` | Sol 5.6 | 2026-08-16 |
| unique-sum published-prefix replay / p=59 boundary | `problems/unique-sum/compute/q3` | GPT-5.6 Sol | 2026-08-23 |
| no-three-in-line n=71 | `problems/three-in-line` | Sol 5.6 | 2026-08-16 |
| no-three-in-line n=71 certificate replay | `problems/three-in-line/compute/q3` | GPT-5.6 Sol | 2026-08-23 |
| no-three-in-line n=75 search | `problems/three-in-line/compute/q4` | GPT-5.6 Sol | 2026-08-23 |
| Schur S(7) | `problems/schur` | Sol 5.6 | 2026-08-16 |
| Schur S(7), q3 source recovery / 1697 search | `problems/schur/compute/q3` | GPT-5.6 Sol | 2026-08-23 |
| Schur S(7), q4 bounded repair | `problems/schur/compute/q4` | GPT-5.6 Sol | 2026-08-23 |
| van der Waerden W(2,7) | `problems/vdw-w27` | Grok 4.6 | 2026-08-16 |
| Shannon $C_7$ 5th power | `problems/c7-shannon` | Grok 4.6 | 2026-08-16 |
| Shannon $C_7$ 5th power / six-shape 368 search | `problems/c7-shannon/compute/q1` | Grok 4.6 | 2026-08-23 |
| Shannon $C_7$ 5th power / support bound and Hamming 11 | `problems/c7-shannon/compute/q2` | Grok 4.6 | 2026-08-27 |
| Shannon $C_7$ 5th power / 8-coset leftover | `problems/c7-shannon/compute/q3` | Grok 4.6 | 2026-08-27 |
| Shannon $C_7$ 5th power / new-shape 368 search | `problems/c7-shannon/compute/q4` | Grok 4.6 | 2026-08-27 |
| Landau 3 (Legendre), conditional exponent and edge replay | `problems/landau-legendre/compute/q1` | Codex 5.6 Sol | 2026-08-27 |
| Landau 4 ($n^2+1$ primes) | `problems/landau-n2-plus-1` | SuperGrok 4.6 | 2026-08-17 |
| unit-distance 509 | `problems/unit-distance-509` | SuperGrok 4.6 | 2026-08-17 |
| Sidon second term | `problems/sidon-second-term` | SuperGrok 4.6 | 2026-08-17 |
| Sidon second term, free-histogram certificate | `problems/sidon-second-term/compute/q1` | SuperGrok 4.6 | 2026-08-27 |
| Sidon second term, m=48 free-histogram certificate | `problems/sidon-second-term/compute/q2` | Grok 4.6 | 2026-08-27 |
| Chowla cosine | `problems/chowla-cosine` | SuperGrok 4.6 | 2026-08-17 |
| two-squares gap | `problems/two-squares-gap` | SuperGrok 4.6 | 2026-08-17 |
| cosine zeros | `problems/cosine-zeros` | SuperGrok 4.6 | 2026-08-17 |
| Ulam sequence | `problems/ulam-sequence` | SuperGrok 4.6 | 2026-08-17 |
| long-gap dilate | `problems/long-gap-dilate` | SuperGrok 4.6 | 2026-08-17 |
| long-gap dilate / SAT past 71 and rising factorials | `problems/long-gap-dilate/compute/q1` | Grok 4.6 | 2026-08-27 |
| thin cyclic bases | `problems/thin-cyclic-bases` | SuperGrok 4.6 | 2026-08-17 |
| union-closed | `problems/union-closed` | SuperGrok 4.6 | 2026-08-17 |
| union-closed / Example 4 on {b,1} | `problems/union-closed/compute/q1` | Grok 4.6 | 2026-08-27 |
| union-closed / 2-sample ceiling on {b,1} | `problems/union-closed/compute/q2` | Grok 4.6 | 2026-08-27 |
| union-closed / fifth-decimal ray certificate | `problems/union-closed/compute/q3` | Codex (GPT-5) | 2026-08-27 |
| 0/1 polynomials | `problems/zero-one-polynomials` | SuperGrok 4.6 | 2026-08-17 |
| Cohn–Elkies planar | `problems/cohn-elkies` | SuperGrok 4.6 | 2026-08-17 |
| kissing number 5d | `problems/kissing-5d` | SuperGrok 4.6 | 2026-08-17 |
| kissing number 5d / polar maximality and Q5 integer 44 | `problems/kissing-5d/compute/q1` | SuperGrok 4.6 | 2026-08-27 |
| kissing number 5d / leftover graphs and unrestricted dual | `problems/kissing-5d/compute/q2` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / leftover (1/4)Z^5 and T^5 36-clique | `problems/kissing-5d/compute/q3` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / exact unrestricted 3-point dual | `problems/kissing-5d/compute/q4` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / D5 stars and T5 share 28 | `problems/kissing-5d/compute/q4` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / leftover n1>=24 and T5 share 27 | `problems/kissing-5d/compute/q4` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / leftover n1>=22 and T5 share 24 | `problems/kissing-5d/compute/q4` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / leftover n1<=21 and T5 36 | `problems/kissing-5d/compute/q5` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / leftover n1<=21 star-cover 4 | `problems/kissing-5d/compute/q6` | Grok 4.6 | 2026-08-27 |
| kissing number 5d / leftover n1<=21 star-cover 5 | `problems/kissing-5d/compute/q7` | Cursor Grok 4.6 | 2026-08-27 |
| affine {0,1,3} copies | `problems/affine-013` | SuperGrok 4.6 | 2026-08-17 |
| 1/3–2/3 posets | `problems/one-third-two-thirds` | SuperGrok 4.6 | 2026-08-17 |
| 1/3–2/3 posets / Gupta v2 replay and ladder table | `problems/one-third-two-thirds/compute/q1` | Grok 4.6 | 2026-08-27 |
| 1/3–2/3 posets / ladder 22, three-rail 15, interval 10 | `problems/one-third-two-thirds/compute/q2` | Grok 4.6 | 2026-08-27 |
| Seymour second neighborhood | `problems/seymour-second-neighborhood` | SuperGrok 4.6 | 2026-08-17 |
| two smooth summands | `problems/two-smooth-summands` | SuperGrok 4.6 | 2026-08-17 |
| Tuza triangles | `problems/tuza-triangle-packing-covering` | SuperGrok 4.6 | 2026-08-17 |
| Caccetta–Häggkvist | `problems/caccetta-haggkvist-k3` | SuperGrok 4.6 | 2026-08-17 |
| Caccetta–Häggkvist n=18 cubes | `problems/caccetta-haggkvist-k3/compute/q1` | Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist exact orders through n=36 | `problems/caccetta-haggkvist-k3/compute/q2` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=72 | `problems/caccetta-haggkvist-k3/compute/q3` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover-cube covering count | `problems/caccetta-haggkvist-k3/compute/q4` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist F₄ F-coordinate dump at 0.3464 | `problems/caccetta-haggkvist-k3/compute/q4` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=108 | `problems/caccetta-haggkvist-k3/compute/q4` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist F₄ CKLS-fork certificate 0.34640 | `problems/caccetta-haggkvist-k3/compute/q4` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=114 | `problems/caccetta-haggkvist-k3/compute/q5` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=115 | `problems/caccetta-haggkvist-k3/compute/q6` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=116 | `problems/caccetta-haggkvist-k3/compute/q7` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=117 | `problems/caccetta-haggkvist-k3/compute/q8` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=118 | `problems/caccetta-haggkvist-k3/compute/q9` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=119 | `problems/caccetta-haggkvist-k3/compute/q10` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=120 | `problems/caccetta-haggkvist-k3/compute/q11` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=121 | `problems/caccetta-haggkvist-k3/compute/q12` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=122 | `problems/caccetta-haggkvist-k3/compute/q13` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=123 | `problems/caccetta-haggkvist-k3/compute/q14` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=124 | `problems/caccetta-haggkvist-k3/compute/q15` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=125 | `problems/caccetta-haggkvist-k3/compute/q16` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=126 | `problems/caccetta-haggkvist-k3/compute/q17` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=127 | `problems/caccetta-haggkvist-k3/compute/q18` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=128 | `problems/caccetta-haggkvist-k3/compute/q19` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=129 | `problems/caccetta-haggkvist-k3/compute/q20` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=130 | `problems/caccetta-haggkvist-k3/compute/q21` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=131 | `problems/caccetta-haggkvist-k3/compute/q22` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=132 | `problems/caccetta-haggkvist-k3/compute/q23` | Cursor Grok 4.6 | 2026-08-27 |
| Caccetta–Häggkvist leftover holes through n=133 | `problems/caccetta-haggkvist-k3/compute/q24` | Cursor Grok 4.6 | 2026-08-28 |
| Caccetta–Häggkvist leftover holes through n=134 | `problems/caccetta-haggkvist-k3/compute/q25` | Cursor Grok 4.6 | 2026-08-28 |
| Caccetta–Häggkvist leftover holes through n=135 | `problems/caccetta-haggkvist-k3/compute/q26` | Cursor Grok 4.6 | 2026-08-28 |
| Caccetta–Häggkvist leftover holes through n=136 | `problems/caccetta-haggkvist-k3/compute/q27` | Cursor Grok 4.6 | 2026-08-28 |
| Caccetta–Häggkvist leftover holes through n=137 | `problems/caccetta-haggkvist-k3/compute/q28` | Cursor Grok 4.6 | 2026-08-28 |
| Caccetta–Häggkvist leftover holes through n=138 | `problems/caccetta-haggkvist-k3/compute/q29` | Cursor Grok 4.6 | 2026-08-28 |
| projective plane 12 | `problems/projective-plane-order-twelve` | SuperGrok 4.6 | 2026-08-17 |
| Ramsey R(5,5) | `problems/ramsey-r55` | SuperGrok 4.6 | 2026-08-17 |
| graph reconstruction n=14 | `problems/graph-reconstruction-next-order` | SuperGrok 4.6 | 2026-08-17 |
| lonely runner 14 | `problems/lonely-runner-fourteen` | SuperGrok 4.6 | 2026-08-17 (incomplete) |
| lonely runner 14 | `problems/lonely-runner-fourteen` | Opus 5 | 2026-08-22 |
| elliptic Fekete $S^2$ | `problems/fekete-s2` | Grok 4.6 | 2026-08-19 |
| Grok Bot transcript page | `notes/chat` | Grok 4.6 | 2026-08-21 |
| Hilbert 16(a) degree 8 | `problems/hilbert16-degree-8` | Fable 5, Opus 5 | 2026-08-21, 2026-08-23 |
| Hilbert 16(a) degree 8 / leftover thicken and (19,3) row | `problems/hilbert16-degree-8/compute/q1` | Grok 4.6 | 2026-08-27 |
| Hilbert 16(a) degree 8 / leftover ranks 21–26 | `problems/hilbert16-degree-8/compute/q2` | Grok 4.6 | 2026-08-27 |
| Hilbert 16(b) Hilbert number H(n) | `problems/hilbert16-limit-cycles` | Grok 4.6 | 2026-08-27 |
| Hilbert 16(b) five-line campaign | `problems/hilbert16-limit-cycles/compute/q1` | Grok 4.6 | 2026-08-27 |
| Hilbert 16(b) twenty-five ideas, five lines | `problems/hilbert16-limit-cycles/compute/q2` | Grok 4.6 | 2026-08-27 |
| Hilbert 16(b) ten ideas, leftover menu, extras | `problems/hilbert16-limit-cycles/compute/q3` | Grok 4.6 | 2026-08-27 |
| Hadwiger–Nelson plane | `problems/hadwiger-nelson-plane` | GPT-5.6 Sol | 2026-08-23 |
| Hadwiger–Nelson fourth rotation layer | `problems/hadwiger-nelson-plane/compute/q4` | GPT-5.6 Sol | 2026-08-23 |
| Lieb–Thirring (Simon 2000 #15) | `problems/simon-lieb-thirring` | Grok 4.6 | 2026-08-27 |
| Lieb–Thirring $\mathcal{C}_1$ trial pair | `problems/simon-lieb-thirring/compute/q1` | Grok 4.6 | 2026-08-27 |
| Lieb–Thirring CCR $M_3$ / Clausen envelope | `problems/simon-lieb-thirring/compute/q2` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess | `problems/simon-ionization-excess` | Grok 4.6 | 2026-08-27 |
| Simon ionization excess / HPS remainder | `problems/simon-ionization-excess/compute/q1` | Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading coefficient | `problems/simon-ionization-excess/compute/q2` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading lift | `problems/simon-ionization-excess/compute/q3` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1057 | `problems/simon-ionization-excess/compute/q4` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1035 | `problems/simon-ionization-excess/compute/q5` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1026 | `problems/simon-ionization-excess/compute/q6` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1021 | `problems/simon-ionization-excess/compute/q7` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1020 | `problems/simon-ionization-excess/compute/q8` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1017 | `problems/simon-ionization-excess/compute/q9` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / n=35 at aspect 10 | `problems/simon-ionization-excess/compute/q10` | Cursor Grok 4.6 | 2026-08-27 |
| Simon ionization excess / leading 1.1013 | `problems/simon-ionization-excess/compute/q10` | Cursor Grok 4.6 | 2026-08-28 |
| Simon IDS continuity / dimension frontier and free-direction replay | `problems/simon-ids-continuity` | GPT-5.6 Sol | 2026-08-27 |
| Smale 16 / plane Jacobian degree-125 frontier and controls | `problems/smale-jacobian-n2/compute` | Codex 5.6 Sol | 2026-08-27 |

## Lean

`lean-toolchain` pins Lean 4.32.0. Formal files live under the problem that
owns them, not at the repo root.

## refs

OpenAI walkthroughs, the ten-proofs PDF, and the house style live in
`refs/`.
