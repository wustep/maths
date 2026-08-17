# maths

Notebook for a few open problems.

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
| [covering](problems/covering) | $\ell_2(10,2)\le 50$. Certified $[50,40]$ radius-2 code, $p(H)=10$, propagated to $\bar\mu(2)\le 2601/2048$. $n=49$ still 7 holes. |
| [brocard](problems/brocard) | Lean lemmas for modular / prime-power split. Conjecture open. |
| [unique-sum](problems/unique-sum) | Rematched OEIS A398173 through $p=47$. |
| [three-in-line](problems/three-in-line) | $n=71$ SAT UNKNOWN. |
| [schur](problems/schur) | No 1697-coloring found. |
| [vdw-w27](problems/vdw-w27) | Verified Paley/QR coloring of $[3703]$. Does not extend to 3704. No dent. |
| [c7-shannon](problems/c7-shannon) | Verified Polak–Schrijver 367-set in $C_7^{\boxtimes 5}$. No 368. No dent. |
| [landau-n2-plus-1](problems/landau-n2-plus-1) | Landau 4. Certified 54110 primes $n^2+1$ for $n\le 10^6$, matching Wolf $\pi_q(10^{12})$. Infinitude open. |
| [sidon-second-term](problems/sidon-second-term) | Hou–Zhao L=6: $\sqrt{ab}=0.9434925085$, $8.22\times 10^{-8}$ below $\gamma_0$. Four-decimal 0.9435 unchanged. |
| [chowla-cosine](problems/chowla-cosine) | $K(n)\ge n^{1/7}/18$ for all $n\ge 1$. Does not beat Bedert $n^{1/5-o(1)}$. |
| [unit-distance-509](problems/unit-distance-509) | Rebuilt Parts 509, 5-chromatic and vertex-critical. No smaller graph found. Record still 509. |
| [cosine-zeros](problems/cosine-zeros) | $Z(N)\ge\log\log N/(200\log\log\log N)$ when RHS $\ge 4$. Does not beat Bedert's exponent. |
| [two-squares-gap](problems/two-squares-gap) | Jameson $a=3$ on $n\le 1.024\cdot 10^{15}$ except $\{3,6,21,91\}$ (m$\le$250 cert replayed). Green's $1/10$ open. |
| [ulam-sequence](problems/ulam-sequence) | L=22 word with $C_F<1.442$, beating CS 1.454. Density open. |
| [long-gap-dilate](problems/long-gap-dilate) | SAT $G(p,\mathrm{round}\sqrt p)$ through $p=71$. No universal $C>2$. Record still Shakan 2. |
| [thin-cyclic-bases](problems/thin-cyclic-bases) | BEL $\sqrt{8/3}$ family replayed through $q=61$. No thinner liminf. $\sqrt2$ open. |
| [union-closed](problems/union-closed) | $0.38285$ on $\{b,1\}$ with iid+Example-4 at $\beta=1/5$ (mesh min ratio $1.000077$). Recovers Liu $0.382709$. Not $1/2$. |
| [cohn-elkies](problems/cohn-elkies) | Exact $R=3627599/500000=7.255198$, beats printed Table 4 $7.25520$. Not a magic function. |
| [kissing-5d](problems/kissing-5d) | Restricted Delsarte: $T_{D_5}$ bound 42, $T_{L_5}$ bound $239925/5456<44$. Unrestricted $40\le\tau_5\le 44$ unchanged. |
| [affine-013](problems/affine-013) | $T(S)\le\lceil n^2/2\rceil$ for affine copies of $\{0,1,3\}$. Beats Aaronson $3/4$. Conjecture $1/3$ open. |
| [zero-one-polynomials](problems/zero-one-polynomials) | BSKK $\theta=0.00373556$ (published $0.003736$ over-round). Census $n\le 20$. $p_n\to 1$ open. |
| [one-third-two-thirds](problems/one-third-two-thirds) | Width-3 $W_{10}$ has $\delta=6/17<14/39$, $e=187$, still $>1/3$. Did not re-run the n=10 census. Conjecture open. |
| [seymour-second-neighborhood](problems/seymour-second-neighborhood) | Explicit n=8 Pisa graphs with irregular missing degrees $3^2 2^6$, $3^4 2^4$, $3^6 2^2$. Seven stored witnesses replayed. Did not re-run the 2.5B census. Conjecture open. |
| [two-smooth-summands](problems/two-smooth-summands) | Residue. $F(131486759)=83$, not a $79$-smooth sum. $G(y)$ through $y=23$ replayed. No exponent below Balog $4/(9\sqrt{e})$. Green #59 open. |
| [tuza-triangle-packing-covering](problems/tuza-triangle-packing-covering) | 8-regular codegree-7 Puleo pair: 1044 cores independently checked (STS(9) on $K_7$). Does not prove Tuza for $\Delta\le 8$. |

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

Chronicle of the repo and the runs: [notes/log.md](notes/log.md).
Lists, picks, and process notes live under [notes/](notes/).

## Lean

`lean-toolchain` pins Lean 4.32.0. Formal files live under the problem that
owns them, not at the repo root.

## refs

OpenAI walkthroughs, the ten-proofs PDF, and the house style live in
`refs/`.
