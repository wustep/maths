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
| [landau-n2-plus-1](problems/landau-n2-plus-1) | Landau 4. Certified 12391 primes $n^2+1$ for $n\le 200000$. Infinitude open. |

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
[refs/](refs/).
