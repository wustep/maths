# maths

Notebook for a few open problems.

This is a public notebook of agent-run attacks on open problems.
Agents (Codex, Claude, Grok, and the like) get a finite handle (a
table bound, a constant, a small case) and try to move it. What
stays in git is the attack log and, when the number is real, a
verifier plus a certificate. Stephen Wu is the human author;
models are named in the ledger below.

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
| [covering](problems/covering) | $$\ell_2(10,2)\le 50,\ \ell_2(21,3)\le 303,\ \ell_2(26,2)\le 13070,\ \ell_2(26,3)\le 817,\ \ell_2(31,4)\le 689,\ \ell_2(36,2)\le 418271,\ \ell_2(38,3)\le 13102,\ \ell_2(41,3)\le 26206$$; $\mathrm{QM}\ 22/24/28$ and $$p(H_{18})\le 17,\ p(H_{20})\le 14,\ p(H_{26})\le 19,\ p(H_{28})\le 28$$. $n=49$ still 7 holes; q9 recovers the 2003 Kaikkonen–Rosendahl 51-set, shows 51 and 50 are not lifts of the $r=8$ record in any of the 174251 quotients, and exhaustively rules out 271127 of the 279034 single-block shrinks of the 50-set with block width $\le 12$. |
| [brocard](problems/brocard) | Lean lemmas for modular / prime-power split. Conjecture open. |
| [unique-sum](problems/unique-sum) | Rematched OEIS A398173 through $p=47$. |
| [three-in-line](problems/three-in-line) | $n=71$ SAT UNKNOWN. |
| [schur](problems/schur) | No 1697-coloring found. |
| [vdw-w27](problems/vdw-w27) | Verified Paley/QR coloring of $[3703]$. Does not extend to 3704. No dent. |
| [c7-shannon](problems/c7-shannon) | Verified Polak–Schrijver 367-set in $C_7^{\boxtimes 5}$. No 368. No dent. |
| [landau-n2-plus-1](problems/landau-n2-plus-1) | Landau 4. Certified 54110 primes $n^2+1$ for $n\le 10^6$, matching Wolf $\pi_q(10^{12})$. Infinitude open. |
| [sidon-second-term](problems/sidon-second-term) | Hou–Zhao L=6: $\sqrt{ab}=0.9434925085$, $$8.22\times 10^{-8}$$ below $\gamma_0$. Four-decimal 0.9435 unchanged. |
| [chowla-cosine](problems/chowla-cosine) | $K(n)\ge n^{1/7}/18$ for all $n\ge 1$. Does not beat Bedert $n^{1/5-o(1)}$. |
| [unit-distance-509](problems/unit-distance-509) | Rebuilt Parts 509, 5-chromatic and vertex-critical. No smaller graph found. Record still 509. |
| [cosine-zeros](problems/cosine-zeros) | $Z(N)\ge\log\log N/(200\log\log\log N)$ when RHS $\ge 4$. Does not beat Bedert's exponent. |
| [two-squares-gap](problems/two-squares-gap) | Jameson $a=3$ on $n\le 1.024\cdot 10^{15}$ except $\{3,6,21,91\}$ (m $\le 250$ cert replayed). Green's $1/10$ open. |
| [ulam-sequence](problems/ulam-sequence) | L=22 word with $C_F<1.442$, beating CS 1.454. Density open. |
| [long-gap-dilate](problems/long-gap-dilate) | SAT $G(p,\mathrm{round}\sqrt p)$ through $p=71$. No universal $C>2$. Record still Shakan 2. |
| [thin-cyclic-bases](problems/thin-cyclic-bases) | BEL $\sqrt{8/3}$ family replayed through $q=61$. No thinner liminf. $\sqrt2$ open. |
| [union-closed](problems/union-closed) | $0.38285$ on $\{b,1\}$ with iid+Example-4 at $\beta=1/5$ (mesh min ratio $1.000077$). Recovers Liu $0.382709$. Not $1/2$. |
| [cohn-elkies](problems/cohn-elkies) | Exact $R=3627599/500000=7.255198$, beats printed Table 4 $7.25520$. Not a magic function. |
| [kissing-5d](problems/kissing-5d) | Restricted Delsarte: $$T_{D_5}$$ bound 42, $$T_{L_5}$$ bound $239925/5456<44$. Unrestricted $40\le\tau_5\le 44$ unchanged. |
| [affine-013](problems/affine-013) | $T(S)\le\lceil n^2/2\rceil$ for affine copies of $\{0,1,3\}$. Beats Aaronson $3/4$. Conjecture $1/3$ open. |
| [zero-one-polynomials](problems/zero-one-polynomials) | BSKK $\theta=0.00373556$ (published $0.003736$ over-round). Census $n\le 20$. $p_n\to 1$ open. |
| [one-third-two-thirds](problems/one-third-two-thirds) | Width-3 $W_{10}$ has $\delta=6/17<14/39$, $e=187$, still $>1/3$. Did not re-run the n=10 census. Conjecture open. |
| [seymour-second-neighborhood](problems/seymour-second-neighborhood) | Explicit n=8 Pisa graphs with irregular missing degrees $3^2 2^6$, $3^4 2^4$, $3^6 2^2$. Seven stored witnesses replayed. Did not re-run the 2.5B census. Conjecture open. |
| [two-smooth-summands](problems/two-smooth-summands) | Residue. $F(131486759)=83$, not a $79$-smooth sum. $G(y)$ through $y=23$ replayed. No exponent below Balog $4/(9\sqrt{e})$. Green #59 open. |
| [tuza-triangle-packing-covering](problems/tuza-triangle-packing-covering) | 8-regular codegree-7 Puleo pair: 1044 cores independently checked (STS(9) on $K_7$). Does not prove Tuza for $\Delta\le 8$. |
| [caccetta-haggkvist-k3](problems/caccetta-haggkvist-k3) | $F_4$ certificate $c=0.34645$, $5\cdot 10^{-5}$ below HKN $0.3465$. Did not replay DRAT. $n=18$ residue. Conjecture $1/3$ open. |
| [projective-plane-order-twelve](problems/projective-plane-order-twelve) | Two involution 2-MOLS replayed (intercalates $108+108$ vs $90+78$). $t=3$ timeout. Published Aut still $\lvert G\rvert\in\{1,2,3\}$. Plane open. |
| [ramsey-r55](problems/ramsey-r55) | McKay 328+328 $(5,5,42)$ graphs replayed; circulant 42/43 empty. Interval still $43\le R(5,5)\le 46$. |
| [graph-reconstruction-next-order](problems/graph-reconstruction-next-order) | Full independent degseq census: all 8,571,837 n=14 graphs are $4^{11}6^{3}$; 17,143 `labelg` samples matched. Uniqueness (hence reconstructibility) not independently re-sorted. McKay n=13 unchanged. |
| [lonely-runner-fourteen](problems/lonely-runner-fourteen) | Incomplete. Inclusion $$r_{13}(1/14\mathbb Z)\subseteq r_{13}(1/p\mathbb Z)$$ replayed; two p=191 witnesses. LRC(13) open. |
| [fekete-s2](problems/fekete-s2) | Replayed Ridgway–Cheviakov 2018 Table 3 for $N=2$–$65$. No dent. Smale 7 open. |

Each problem folder:

```
PROBLEM.md        statement and what would count as a dent
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
| covering / $\ell_2(10,2)$ | `problems/covering` | Sol 5.6, Opus 5, Fable 5, Grok 4.6 | 2026-08-16–21 |
| Brocard–Ramanujan | `problems/brocard` | Sol 5.6 | 2026-08-16 |
| unique-sum mod p | `problems/unique-sum` | Sol 5.6 | 2026-08-16 |
| no-three-in-line n=71 | `problems/three-in-line` | Sol 5.6 | 2026-08-16 |
| Schur S(7) | `problems/schur` | Sol 5.6 | 2026-08-16 |
| van der Waerden W(2,7) | `problems/vdw-w27` | Grok 4.6 | 2026-08-16 |
| Shannon $C_7$ 5th power | `problems/c7-shannon` | Grok 4.6 | 2026-08-16 |
| Landau 4 ($n^2+1$ primes) | `problems/landau-n2-plus-1` | SuperGrok 4.6 | 2026-08-17 |
| unit-distance 509 | `problems/unit-distance-509` | SuperGrok 4.6 | 2026-08-17 |
| Sidon second term | `problems/sidon-second-term` | SuperGrok 4.6 | 2026-08-17 |
| Chowla cosine | `problems/chowla-cosine` | SuperGrok 4.6 | 2026-08-17 |
| two-squares gap | `problems/two-squares-gap` | SuperGrok 4.6 | 2026-08-17 |
| cosine zeros | `problems/cosine-zeros` | SuperGrok 4.6 | 2026-08-17 |
| Ulam sequence | `problems/ulam-sequence` | SuperGrok 4.6 | 2026-08-17 |
| long-gap dilate | `problems/long-gap-dilate` | SuperGrok 4.6 | 2026-08-17 |
| thin cyclic bases | `problems/thin-cyclic-bases` | SuperGrok 4.6 | 2026-08-17 |
| union-closed | `problems/union-closed` | SuperGrok 4.6 | 2026-08-17 |
| 0/1 polynomials | `problems/zero-one-polynomials` | SuperGrok 4.6 | 2026-08-17 |
| Cohn–Elkies planar | `problems/cohn-elkies` | SuperGrok 4.6 | 2026-08-17 |
| kissing number 5d | `problems/kissing-5d` | SuperGrok 4.6 | 2026-08-17 |
| affine {0,1,3} copies | `problems/affine-013` | SuperGrok 4.6 | 2026-08-17 |
| 1/3–2/3 posets | `problems/one-third-two-thirds` | SuperGrok 4.6 | 2026-08-17 |
| Seymour second neighborhood | `problems/seymour-second-neighborhood` | SuperGrok 4.6 | 2026-08-17 |
| two smooth summands | `problems/two-smooth-summands` | SuperGrok 4.6 | 2026-08-17 |
| Tuza triangles | `problems/tuza-triangle-packing-covering` | SuperGrok 4.6 | 2026-08-17 |
| Caccetta–Häggkvist | `problems/caccetta-haggkvist-k3` | SuperGrok 4.6 | 2026-08-17 |
| projective plane 12 | `problems/projective-plane-order-twelve` | SuperGrok 4.6 | 2026-08-17 |
| Ramsey R(5,5) | `problems/ramsey-r55` | SuperGrok 4.6 | 2026-08-17 |
| graph reconstruction n=14 | `problems/graph-reconstruction-next-order` | SuperGrok 4.6 | 2026-08-17 |
| lonely runner 14 | `problems/lonely-runner-fourteen` | SuperGrok 4.6 | 2026-08-17 (incomplete) |
| elliptic Fekete $S^2$ | `problems/fekete-s2` | Grok 4.6 | 2026-08-19 |

## Lean

`lean-toolchain` pins Lean 4.32.0. Formal files live under the problem that
owns them, not at the repo root.

## refs

OpenAI walkthroughs, the ten-proofs PDF, and the house style live in
`refs/`.
