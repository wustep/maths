# Research log — projective plane of order 12

## Status (accessed 2026-08-17)

- [Moorhouse, *Projective Planes of Small Order*](https://ericmoorhouse.org/pub/planes/) — revised November 2017, re-fetched 2026-08-17. Catalogue of known planes of order $n<34$. **No order-12 incidence record.** Completeness claimed only through order 10 (Lam–Kolesova–Thiel 1988; Lam–Thiel–Swiercz 1988). The empty slot is a database cross-check, not an exclusion.
- [TheoremDB `projective-plane-order-12`](https://www.theoremdb.org/statements/projective-plane-order-12/) — snapshot 2026-07-25, records R592–R597. Existence still open. Strongest published symmetry: $\lvert G\rvert\in\{1,2,3\}$.
- Wikipedia *Projective plane*, fetched 2026-08-17: order 12 still listed as open.
- Bruzda, arXiv:2607.25954 (2026): $N(12)\ge5$ still the published lower bound; existence of six MOLS of order 12 remains open.

No later accepted construction or nonexistence theorem was found.

## Published record we are measuring against

| claim | source | this folder |
| --- | --- | --- |
| Bruck–Ryser silent at $n=12$ | Bruck–Ryser, Canad. J. Math. 1 (1949) | `compute/replay_identities.py`: $12\equiv0\pmod4$; $\lvert\det B\rvert=13\cdot12^{78}$ |
| $N(12)\ge5$ | Bose–Chakravarti–Knuth, Technometrics 2 (1960) | not replayed (no BCK squares ingested); MacNeish gives 2, not 5 |
| no elation of order 3 | Janko–van Trung, Stud. Sci. Math. 16 (1981) | cited, not re-proved |
| $\lvert G\rvert$ a $\{2,3\}$-group, no $V_4$, no nonabelian $S_3$ | Janko–van Trung 1980–82 | cited |
| $\lvert G\rvert$ divides 16 or 9 | Horvatić-Baldasar–Kramer–Matulić-Bedenić 1986–87 | cited |
| no $\lvert G\rvert=16$ | Suetake, JCTA 107 (2004) | cited |
| no $\lvert G\rvert=8$ | Akiyama–Suetake, JCD 16 (2008) | cited |
| no $\lvert G\rvert=9$ | Akiyama–Suetake–Tanaka, AJC 74 (2019) | local `compute/refs/akiyama-suetake-tanaka-2019-order9.pdf` |
| no $\lvert G\rvert=4$; hence $\lvert G\rvert\in\{1,2,3\}$ | Akiyama–Suetake–Tanaka, JCD 31 (2023) | DOI 10.1002/jcd.21869; paywalled tonight, abstract + TheoremDB R595 |
| OA / 11-MOLS / Hadamard reformulation | Kharaghani–Suda, EJC 30 (2023) P2.49 | local `compute/refs/kharaghani-suda-2023.pdf` |

We did **not** beat the 2023 group-order classification. A dent tonight would have been a certified exclusion of one of the three remaining orders, or a construction.

## Independent type arithmetic (this folder)

`compute/classify_types.py` (all checks pass, `certs/type_classification.json`):

- Unique order-2 Baer type: involutory elation ($n$ even, not square; the $n\equiv2\pmod4$ involution ban is silent).
- No true homology of order 3: $f=14\not\equiv1\pmod3$ and $3\nmid 11$.
- No generalized homology of order 3: axis action vs $f\equiv1\pmod3$ force incompatible conditions on the number of fixed points of the axis.
- No planar order-3 element with Fano Fix: an invariant ambient line would have 10 extra points.
- Remaining order-3 geometry: planar with $\mathrm{Fix}\cong\mathrm{PG}(2,3)$, or generalized elation with $f\in\{1,4,7,10\}$. The $f=13$ elation is the 1981 theorem.

These divisibility lemmas recover the type list already used in the 2009/2019 Akiyama–Suetake papers. They are not claimed as a new forbidden automorphism type.

## Computational residue on $\lvert G\rvert=2$

An involutory elation is equivalent to $t=11$ MOLS of order 12 with $L[r+6][c]=L[r][c]+6$. Already $t=3$ would be implied.

| instance | result | certificate |
| --- | --- | --- |
| $t=1$ involution-Latin | SAT | `certs/t1_squares.json`, independent verifier |
| $t=2$ (SAT search) | SAT | `certs/t2_squares.json` |
| $t=2$ MacNeish product | explicit | `certs/macneish_involution_2mols.json` |
| third mate of the SAT pair | UNSAT | `certs/mate_t2.drat`, drat-trim VERIFIED |
| third mate of MacNeish | UNSAT | `certs/mate_macneish.drat`, drat-trim VERIFIED |
| $t=3$ cell-symbol | UNKNOWN at 2400s | `certs/t3c.out`: 45,210,387 conflicts, 2396s |
| $t=3$ $\sigma,\delta$ | UNKNOWN at 2400s | `certs/sd3.out`: 21,232,051 conflicts, 2396s |

The two mate-UNSAT proofs show that two distinct isotopy classes of involution 2-MOLS are maximal. They do not classify all classes. Search residue is not a bound.

## Sources fetched tonight

- https://ericmoorhouse.org/pub/planes/
- https://www.theoremdb.org/statements/projective-plane-order-12/
- https://www.theoremdb.org/records/pp12-attempt-literature-and-catalogue-audit
- https://ajc.maths.uq.edu.au/pdf/74/ajc_v74_p112.pdf
- https://ajc.maths.uq.edu.au/pdf/43/ajc_v43_p133.pdf
- https://arxiv.org/pdf/2211.02410 (Kharaghani–Suda)
- https://mathoverflow.net/questions/38632/projective-plane-of-order-12
- https://doi.org/10.1002/jcd.21869 (abstract only)
