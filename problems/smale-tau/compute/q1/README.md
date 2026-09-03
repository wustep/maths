# q1 — exhaustive search for short straight-line programs

Decides whether an integer \(N\) has a straight-line program of length
\(L\) (OEIS A173419 / A217032; Smale 1998, Problem 4, integer form).

## Files

| file | role |
| --- | --- |
| `slp_search.c` | the search (C, OpenMP): count mode, decide mode, endgame test mode |
| `check.rs` | independent Rust re-implementation: count mode and a brute-force endgame sampler |
| `targets.txt`, `targets_core.txt`, `targets13.txt` | targets: \(n!\) for \(13\le n\le 34\) and primorials to \(47\#\); the core list for the 11- and 12-step runs; the 13-step list (20!, 21!, 22!, 37#) |
| `brute_check.py` | Python brute-force cross-check of the three-step endgame at prefix depths 3–6 |
| `compare_endgame.py` | Rust brute-force sampler versus the C endgame at prefix depths 7–10 (`compare_*.txt`) |
| `verify_slp.py` | exact replay of every witness program (stdlib) |
| `make_tau_table.py`, `tau_table_10266.txt` | \(\tau(n)\) for \(n\le 10266\), C and Rust tables compared, OEIS b-file format |
| `b173419.txt` | OEIS A173419 b-file (n ≤ 1800) used as a control |
| `run_all.sh`, `launch13.sh` | replay driver; launcher for the 13-step decision |
| `count9.json`, `count9_10266.json`, `check_count9_10266.json` | count mode to 9 steps (C twice, Rust once) |
| `decide11_core.json`, `decide12.json`, `decide13.json` | decisions at 11, 12, 13 steps |
| `make_certificate.py`, `certificate.json` | summary of every decision |

## Definitions

A program is \(x_0=1\), \(x_k=x_i\circ x_j\) with \(i,j<k\) and
\(\circ\in\{+,-,\times\}\); \(\tau(N)\) is the least \(k\) with
\(x_k=N\). Subtraction is allowed in either order and \(i=j\) is
allowed. This is the convention of OEIS A173419, of the 2013 contest,
and of Markström; Shub–Smale and Smale use the same one.

## Normalisation

If \(N>0\) has a program of length \(k\), it has one of length at most
\(k\) whose values are pairwise distinct and strictly positive. Replace
every value by its absolute value: \(|x_i x_j|=|x_i||x_j|\), and
\(|x_i\pm x_j|\) is either \(|x_i|+|x_j|\) or the positive difference
of \(|x_i|\) and \(|x_j|\), so the new sequence is again a program. A
zero can only arise as a difference of equal values; a repeated value
can be dropped after redirecting later references to its first copy.
(Markström, arXiv:1306.3091, Appendix A, states the same.)

## Canonical order

Let \(S_d=\{1,v_1,\dots,v_d\}\) be the values of a normalised program
prefix. The queue \(Q(S_d)\) lists every positive integer derivable in
one step from \(S_d\) and not in \(S_d\), in blocks: block 0 holds the
values derivable from \(\{1\}\), block \(i\) the values first derivable
once \(v_i\) is present, each block in a fixed generation order and
without repetition. Positions in the queue depend only on the prefix.

Rule: the next value \(v_{d+1}\) must sit in \(Q(S_d)\) at a position
strictly larger than the position of \(v_d\) in \(Q(S_{d-1})\).

Every normalised program has exactly one valid order that satisfies the
rule. Among all orderings of its value set that are programs (each value
derivable from the earlier ones), take the one whose sequence of queue
positions is lexicographically least. If two consecutive values had
non-increasing positions, the later one would lie in an earlier block,
hence be derivable without the former; swapping the two gives a program
with a smaller position sequence. For an optimal program the target is
the only value not used later, so it is last in every ordering. This is
the "pending queue" order described by Rokicki in the OEIS A217032
digest; the count mode reproduces Markström's reached-set sizes exactly,
which is the empirical check of exhaustiveness.

## Endgame

For length \(L\) the search enumerates prefixes of \(L-3\) steps and
asks whether \(N\) is derivable in at most three more steps. Write
\(S\) for the prefix set, \(Q\) for its queue, and \(y_1,y_2\) for the
new values (each new, positive, and used later).

- 0 or 1 step: \(N\in S\) or \(N\in Q\).
- 2 steps: \(N=y_1\circ b\) with \(b\in S\) or \(b=y_1\), so \(y_1\in\{N-b,\,N+b,\,b-N,\,N/b\}\cup\{N/2,\sqrt N\}\) and \(y_1\in Q\).
- 3 steps, last step uses \(y_1\): \(N=y_2\circ y_1\) with \(y_1\in Q\); either \(y_2\in Q\), or \(y_2=y_1\circ c\) with \(c\in S\cup\{y_1\}\), which is solved for \(c\) (for instance \(N=(y_1+c)+y_1\) gives \(c=N-2y_1\)).
- 3 steps, last step does not use \(y_1\): \(N=y_2\circ z\) with \(z\in S\cup\{y_2\}\), so \(y_2\) is one of at most \(4|S|+2\) candidates, and \(y_2=y_1\circ c\) with \(c\in S\cup\{y_1\}\), \(y_1\in Q\). Divisibility \(c\mid y_2\) is decided from residues \(N\bmod c\) and \(b\bmod c\) without division.

Any hit is turned into an explicit program and re-verified in Python.
`brute_check.py` compares the endgame with a direct three-step
expansion on random prefixes.

## Filters

- Markström's bound: with \(r\) steps left, values stay below
  \(M^{2^r}\) where \(M\) is the current maximum.
- Leaf bound: in three steps the only ways to exceed \(M^5\) are
  \(N=y_2^2\) and \(N=y_1^3\). Factorials and primorials are never
  perfect powers, so a leaf with \(M^5<N\) is skipped for that target.
- Range checks before every lookup: a value must lie between the
  minimum and maximum of the set it is claimed to belong to.

Arithmetic is exact: values below \(2^{128}\) are native, larger ones
use limbs; the arena is asserted, never truncated.

## Replay

```bash
./run_all.sh            # build, controls, decisions at 11 and 12 steps, verify
./run_all.sh --full     # also the 13-step decision (hours on 8 threads)
```
