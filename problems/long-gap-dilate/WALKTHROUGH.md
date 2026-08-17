# Walkthrough — a long gap in a dilate modulo a prime

Discovery notes, not a paper. Empty sections would mean not done.

- Problem: `problems/long-gap-dilate`
- Quest: Green 100 #32, improve Shakan’s universal 2
- Model: SuperGrok CLI `grok-4.6`
- Date: 2026-08-17
- Argument status: no certified \(C>2\). Residue is a verified SAT table,
  a degree-wall for the published method, and failed lifts
- Problem status: open

## 0. What was actually missing

The missing degree of freedom was not a SAT solver and not a larger
small-prime table. Shakan’s published argument already gives

\[
  \sup_d g(d\cdot A)\;\ge\; 2p/|A|-2
\]

for every \(A\subset\mathbb F_p\) with \(|A|>1\). The 2 is the sum of
two degree bounds on a Rédei slice \(\chi^m=t^pg+h\). At the scale
\(m\sim Cp/|A|\) with \(C>2\) that slice has **no middle coefficients
forced to vanish**. The interval that defines a gap is discarded when
the product \(\prod_{j=1}^m(t+j+da)\) is replaced by its top
homogeneous part \((t+da)^m\). Whatever beats 2 has to keep that
interval, or leave Rédei entirely.

Isolated \(G(p,\sqrt p)\) for \(p\le 71\) cannot be that argument.

## 1. False starts (named obstacles)

**The list citation.** The proposed-50 source
`arXiv:2205.14038`, “On higher moments of Fourier coefficients”, is a
quant-ph paper. The result Green cites is Shakan,
[arXiv:2004.14828](https://arxiv.org/abs/2004.14828), SIDMA 34 (2020).
Fetched first.

**Tweaking the Wronskian.** Cancelled leading terms give
\(\deg W\le 2k-2\) instead of \(2k-1\). Discrete derivatives of rising
factorials do the same comparison. Both rearrange \(O(1)\). Not a
leading constant.

**Assuming \(0\in A\).** Legal by translation. Then
\(\deg_d w=1+(n-1)m\). At \(C=2\) this is still larger than \(p\), so
the \(d^p-d\) half of Alon does not drop.

**Dirichlet clustering.** Any fixed-size \(n\)-set has a dilate of
diameter \(O(p^{1-1/(n-1)})\), so \(G(p,n)/(p/n)\to n\). This is
Green’s Bohr-set remark. At \(n\sim\sqrt p\) the box principle needs
more than \(p\) boxes. No dent.

**Energy / Freiman.** \(|A-A|\le 3n\) makes some dilate an interval
and the gap is \(p-O(n)\), enormous. Random / Sidon / small
multiplicative subgroups have \(\max g\sim(p/n)\log n\), also
enormous. The sets that could keep the leading constant near 2 are
exactly the ones the polynomial method already treats. Rank-2 Bohr
sets collapse to diameter \(p^{3/4}\).

**Cauchy–Schwarz on occupancies.** \(\sum N\) and \(\sum N^2\) over
pairs \((d,t)\) recover only the pigeonhole \(C\ge 1\). Pairwise
inclusion-exclusion with a matching of \(A\) is the same.

**Singer as a \(C\to 2\) family.** For \(q=3,5\) the Singer set in
\(\mathbb Z/(q^2+q+1)\) matches the SAT value of \(G\). At \(q=17\),
\(p=307\), \(n=18\) it has gap 90 against Shakan 32 (ratio \(5.28\)).
Not a near-extremal family.

**Calling the SAT table a dent.** For \(17\le p\le 71\) one has
\(G(p,\mathrm{round}\sqrt p)/\sqrt p\in[2.18,3.09]\). House rule:
isolated small-\(p\) tables are not a universal \(C>2\). Extra above
Shakan is order \(n\) on this range; that could be a hidden \(+n\)
(which would be leading 3 at \(n\sim\sqrt p\)) or slack that dies.

## 2. The useful failure

The homogeneous Rédei slice is a wall, not a knob. Once
\(m\ge 2p/n\), \(\chi^m=t^pg+h\) is an identity that a general degree-
\(n\) polynomial can satisfy for dimension reasons. There is nothing
left to contradict. The calculation that looks like it might give
\(2+\varepsilon\) is the same calculation with no hypotheses left.

That failure is useful because it names the discarded information:
\(B\) is an interval, \(w(d,t)=d\prod_a(t+da+1)_m\) is a product of
rising factorials, and the lower Stirling terms are exactly what the
top-degree slice throws away. A Python expansion of the full \(w\)
vanishes on \(\mathbb F_p^2\) at the same \(m\) the gap definition
requires. The extra terms do not automatically vanish earlier.

## 3. The click

Two translations, then a stop.

First: \(\max_d g(dA)\) is the length of the longest arithmetic
progression in the complement. Green #32 is the hitting-set statement
“every \(\sqrt p\)-set misses some \(100\sqrt p\)-AP”. Shakan is
\(H(p,T)>2p/(T+2)\). A dent is \(H(p,C\sqrt p)>\sqrt p\) for some
fixed \(C>2\).

Second: the only published proof of the 2 uses a homogeneous slice
that is information-theoretically unable to see \(C>2\). Beating 2
is a different argument, or a use of the rising factorials that this
session did not find.

There is no third click that produces a \(C>2\) proof.

## 4. The argument, in the order it was found

1. Fetch Green #32 and Shakan (the real arXiv id). Record the published
   constant 2.
2. Re-derive the Wronskian. Confirm that \(\alpha=2\) in
   \(\deg g+\deg h\le\alpha k\) is forced by the slice, and that
   \(C>2\) makes the middle-coefficient list empty.
3. Write the Dirichlet bound and check it against exact \(G(p,3)\) and
   \(G(p,4)\): the ratios climb toward 3 and 4, as they should, and
   this does not speak to \(n\sim\sqrt p\).
4. Encode “exists an \(n\)-set hitting every \(T\)-AP” in SAT, binary-
   search \(T\), get exact \(G(p,\mathrm{round}\sqrt p)\) through
   \(p=71\). Independently recompute every witness. Enumerate all
   affine-normalised \(n\)-sets through \(p=41\); they match SAT.
5. Hunt a \(C=2+o(1)\) family (grids, squares, subgroups, Singer,
   jitter, greedy hitting sets, local search). None approaches 2 at
   \(n\sim\sqrt p\). Local-search upper bounds live at ratio \(3\)–\(3.5\).
6. Stop before calling the finite table a universal constant.

## 5. Computer residue

- `compute/certs/sat_G.jsonl` — exact \(G\), witnesses, Glucose logs
  of the binary search.
- `compute/certs/sat_G_verified.json` — independent recomputation of
  every witness gap.
- `compute/certs/enum_diagonal.json` — brute-force \(G\) through
  \(p=41\).
- `compute/certs/G_n3.json`, `G_n4.jsonl`, `G_n5.jsonl` — fixed-\(n\)
  exact values.
- `compute/certs/local_upper.jsonl`, `constructions.jsonl`,
  `singer.json`, `greedy_hit.json` — upper bounds / families.
- `figures/sat_ratios.png` — \(G/(p/n)\) and \(G/\sqrt p\) against
  Shakan’s 2.
- `compute/verify.py` — Shakan on every proper nonempty subset for
  \(p\le 13\), and on the listed constructions.

Replay:

```bash
cd problems/long-gap-dilate
sh compute/run_all.sh
```

## 6. What is proved vs still open

**Proved, published, not improved.** Shakan: every \(A\) of size
\(n>1\) has a dilate missing \(2p/n-2\) consecutive residues. For
\(n=\lfloor\sqrt p\rfloor\) this is a gap of \(2\sqrt p-2\). The
leading constant 2 is the record.

**Proved, elementary, already in Green’s comments.** For each fixed
\(n\), Dirichlet gives \(G(p,n)=p-o(p)\), so the Shakan constant \(2\)
is not sharp at bounded size. This is the regime \(|A|\le c\log p\).

**Certified computation, not a bound.** For every prime
\(17\le p\le 71\) and \(n=\mathrm{round}\sqrt p\),
\(G(p,n)\ge 2.1\sqrt p\), with an independently checked witness of
size \(n\) and (for \(p\le 41\)) an exhaustive proof that nothing
smaller-gap exists. This is a finite list.

**Still open.** Green #32: is there a universal \(C=100\), or even a
universal \(C=2.01\), such that every \(A\) of size \(\sim\sqrt p\)
has a dilate missing \(C\sqrt p\)? No such \(C>2\) is proved here.
No construction shows that \(2\) is sharp either.
