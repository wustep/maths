> Recovery note (2026-08-16 afternoon): this is the q1 walkthrough recovered from the Codex rollout. The Math-agent memory log later recorded that q1 used the wrong predicate (`r=1` rather than `r ∉ {1,2}`), commit `77d43c5`. Treat the `p≤200` completeness claim below as invalidated. q2 recoded the predicate; recovered `compute/green_m_p.csv` matches OEIS A398173 through `p=47` only.

# Walkthrough — From unique sums to a normalized midpoint search

- Problem: `problems/unique-sum`
- Quest: `q1-overnight`
- Model: gpt-5.6-sol max
- Date: 2026-08-16 (America/Los_Angeles)
- Argument status: solver-certified finite computation, independently replayed
- Problem status: open; the finite \(p\le 200\) quest is complete

## 0. What was actually missing

The missing ingredient was not a stronger generic SAT solver. It was the
right local invariant and the full affine normal form it permits. A literal
encoding treats every residue and every ordered sum as independent data. In
an odd prime field, however, all off-diagonal representations arrive in
opposite-order pairs. Only a diagonal sum can be unique. Once this is noticed,
the problem becomes a small system of midpoint equations, and one of those
equations normalizes three selected residues at once. That change removes the
large ambient group from the hard part of the search.

## 1. False starts (named obstacles)

- **The full ordered-sum model.** We first contemplated variables for all
  members and all sum multiplicities. The obstruction was structural: it
  encoded the automatic pairing \((b,c),(c,b)\) repeatedly and concealed that
  only \((a,a)\) can contribute a lone ordered representation.
- **A Boolean membership SAT grid.** With membership variables \(x_r\), a
  center clause can be expressed using auxiliary variables for each endpoint
  pair. Even after fixing \(0,1\), the \(p=199\), \(k=9\) instance had about
  23,000 variables and 66,000 clauses and did not decide in the first minute
  with several standard SAT engines. The issue was not formula size alone:
  the solver still had to rediscover affine copies of the same sparse set.
- **Optimization before normalization.** A CP-SAT objective on the same
  residue grid found small examples, but the lower bound remained the hard
  half. An extremal witness proves only \(m(p)\le k\); it says nothing about
  \(k-1\).
- **Random local search.** Simulated mutations quickly found a 10-element set
  for \(p=199\), while repeated 9-element attempts stopped with one
  unsupported point. This was useful evidence about the boundary but could
  never certify UNSAT.
- **Only two fixed residues.** Translating and scaling an arbitrary selected
  pair to \(0,1\) was valid, but it discarded the midpoint relation that had
  justified choosing the pair. The sorted integer model became much smaller,
  yet the last lower-bound cases were still unnecessarily symmetric.

## 2. The useful failure

The local search separated the two computational burdens. Producing a witness
was easy; excluding the preceding size was expensive. At \(p=199\), it found
10 selected residues in seconds, whereas size 9 repeatedly left exactly one
center without a pair. This suggested that the model should name a witnessing
progression, not merely two arbitrary selected points. The failed Boolean
model supplied the same clue from another direction: its useful variables
were precisely the endpoint pairs centered at selected residues.

The residue of both failures was therefore the same. A selected center comes
with a nontrivial three-term progression. We should spend the affine symmetry
on that whole progression.

## 3. The click

Choose any \(a\in A\). Its midpoint witness has the form
\(a-d,a+d\), with \(d\ne0\). Translate by \(-a\), then multiply by
\(d^{-1}\). Because \(p\) is prime, the result is an affine-equivalent set
containing

\[
\{-1,0,1\}=\{p-1,0,1\}.
\]

After sorting, three positions are fixed:
\(v_0=0\), \(v_1=1\), and \(v_{k-1}=p-1\). This was the decisive change of
setting. The ambient \(p\)-cell membership vector disappeared; the solver
only had to choose the remaining \(k-3\) residues and one midpoint witness
per chosen residue. With this normalization the \(p=199,k=9\) boundary
instance became a completed UNSAT check rather than an open-ended search.

## 4. The argument, in the order it became inevitable

### Unique sums are unsupported diagonals

Let \(p\) be odd. If \(b\ne c\), every representation \(b+c=x\) is paired
with the distinct ordered representation \(c+b=x\). Also, multiplication by
2 is injective, so a fixed sum has at most one diagonal representation.
Therefore

\[
r_A(x)=1
\quad\Longleftrightarrow\quad
x=2a\text{ for some }a\in A
\text{ and no distinct }b,c\in A\text{ satisfy }b+c=2a.
\]

Thus \(A\) is unique-sum-free exactly when every \(a\in A\) is the center of
a nontrivial three-term progression in \(A\). Sizes 1 and 2 are immediately
impossible for odd \(p\). The prime 2 is handled directly: \(\{0,1\}\) has
both sums represented twice, so \(m(2)=2\).

### The affine normal form is exhaustive

For an odd prime and any admissible nonempty \(A\), choose a center \(a\) and
distinct endpoints \(b,c\). Writing \(d=b-a\), the midpoint equation gives
\(c-a=-d\), and \(d\ne0\) has an inverse. The affine map

\[
x\longmapsto d^{-1}(x-a)
\]

preserves all midpoint equations and sends \(a,b,c\) to \(0,1,-1\).
Consequently no candidate is lost by searching only sorted residues

\[
0=v_0<v_1=1<v_2<\cdots<v_{k-2}<v_{k-1}=p-1.
\]

This is the completeness argument behind the symmetry breaking; it is not a
heuristic preference for symmetric-looking sets.

### A compact exact feasibility model

For each selected center \(v_i\) other than the already supported \(v_0=0\),
the model chooses indices \(j<\ell\), both different from \(i\), and imposes

\[
2v_i-v_j-v_\ell=q p,
\qquad q\in\{-1,0,1\}.
\]

Those are all possible wrap values because every \(v_i\) lies between 0 and
\(p-1\). Strict ordering makes the residues and endpoints distinct. The
disjunction over endpoint pairs is exactly the midpoint condition, so SAT
produces a valid set and UNSAT excludes every set of that cardinality after
the exhaustive affine normalization.

The search tries \(k=3,4,\ldots\) in order and stops at the first SAT model.
It nevertheless records every earlier status rather than assuming that
existence is monotone in \(k\). This matters in spirit because the resulting
function of the prime is itself not monotone: \(m(41)=8\) but \(m(43)=7\).

### Replay separates witnesses from lower bounds

The CSV witness is checked without trusting solver internals. For every
ordered pair in \(A^2\), the verifier recomputes its sum modulo \(p\) and
rejects if any multiplicity equals 1. It also independently rebuilds all
smaller-cardinality instances. The primary model selects an integer wrap
\(q\); the replay expands the three wrap values into separate Boolean
alternatives. The full replay checked 3,159 ordered pairs and 235 lower
instances and returned `VALID`.

A hand-sized example shows both halves. For \(p=5\),
\(A=\{0,1,3,4\}\) has ordered representation counts
\((3,3,3,3,4)\), so none is unique. Its four centers are supported by the
pairs \((1,4),(3,4),(0,1),(0,3)\), respectively. The size-3 normalized model
is UNSAT, giving \(m(5)=4\).

## 5. Figures, numeric checks, computer residue

The exact table contains all 46 primes at most 200. The numbers of primes
with minima \(2,3,\ldots,10\) are

\[
1,1,1,2,3,5,8,15,10.
\]

The first value 10 occurs at \(p=157\); every listed prime from 157 onward has
value 10. At the smaller exceptional reversal, \(p=43\) admits a 7-element
set even though \(p=41\) needs 8.

The recorded witnesses are structurally simple only at the beginning. The
sets for \(p=2,3\) are the whole group, and those for \(p=5,7\) are cyclic
arithmetic progressions. The saved witnesses at \(p=11,19,43\) are non-AP
but have a nontrivial affine stabilizer. The other 39 saved witnesses are
non-AP and have trivial affine stabilizer. This describes one solver witness
per prime, not the complete orbit set of all extremizers.

![Recovered m(p) against log p and log-squared p through p=47, matching OEIS A398173](figures/m_p.png)

The recovered table is the 14 primes through \(p=47\) in `compute/green_m_p.csv`,
not the invalidated \(p\le200\) claim above. On that range the linear fit
against \(\log p\) has \(R^2\approx0.978\); the fit against \((\log p)^2\)
has \(R^2\approx0.994\). Those numbers are descriptive diagnostics, not
evidence for a new asymptotic theorem.

## 6. Proven vs still open

- **Now established.** For each of the 46 primes \(p\le200\), the value in
  `compute/m_p.csv` has a directly checked witness and every smaller size has
  been ruled out by two completed exact CP-SAT formulations.
- **Not claimed.** We do not classify all extremal sets, extract an infinite
  construction, improve either known asymptotic bound, or infer growth from
  the two least-squares lines. The overall problem remains open.
- **Certificate scope.** There is no Lean or DRAT proof object. The finite
  certificate is computational and replayable: exact integer models plus an
  independent arithmetic and optimality verifier.
- **Scope check.** The normalization uses both that 2 is invertible and that
  every nonzero \(d\) is a unit. It handles \(p=2\) separately and does not
  transfer unchanged to odd composite moduli, where a midpoint difference can
  be a nonunit and cannot necessarily be scaled to 1.

## 7. Digestion notes

The main artifacts are:

- `compute/search_m_p.py` — the affine-normalized exact search;
- `compute/m_p.csv` — all values and one extremal witness per prime;
- `compute/m_p_certificates.json` — ordered counts, midpoint supports, and
  every cardinality result from the primary run;
- `compute/verify_m_p.py` — direct witness checking and an independently
  written optimality replay;
- `compute/plot_m_p.py` and `figures/m_p.png` — the finite comparison plot;

From the repository root, the decisive replay command is:

```bash
python problems/unique-sum/compute/verify_green_m_p.py
```

On the recorded run it reported 46 primes, 3,159 ordered pairs, 235 lower
instances, and `VALID`. No Lean file was needed because this quest claims a
finite, independently rerun computation rather than a formal theorem about
all primes.
