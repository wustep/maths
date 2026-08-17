# Walkthrough — a smaller constant in the two-squares gap

Discovery notes, not a paper.

## 0. What was actually missing

The missing degree of freedom was not a new sieve and not the
Landau–Ramanujan counting function. Bambah–Chowla already give
\(G(n)<2\sqrt{2}\,n^{1/4}+1\). Jameson already shaved the \(+1\) to
\(-2\). Shiu isolated the next increment: \(a=3\), i.e.
\(G(n)<2\sqrt{2}\,n^{1/4}-3\), and produced an infinite family of
\(n\) on which the two obvious lattice points — the Bambah–Chowla
point and \((u+1)^2\) — both sit just on the wrong side of
\(\Phi-3\).

On that family the two obvious points give leftover exactly \(2m\),
while \(2m+2<\Phi<2m+3\). So \(a=3\) is the existence of **some other**
lattice point in \([n,n+2m)\). That is a search, not a new exponent.

Green’s \(1/10\) is a much smaller multiplicative target. It is not
the published proven constant, and a gap table does not prove it.

## 1. Named false starts

**Claiming Bloom #143.** The proposed-50 list says Erdős #143.
Fetched: #143 is primitive-set sparsity. Green’s comments say Erdős
1957 Problem 15. Bloom’s matching page is #222. Numbering error,
recorded and moved on.

**Landau–Ramanujan ⇒ \(1/10\).** Average gaps \(\asymp\sqrt{\log X}\)
would make \(1/10\,X^{1/4}\) look generous for large \(X\). House
rule: do not claim the density. Average gaps are not a max-gap bound.

**Richards / DEKKM as a dent.** \(\limsup G/\log s_n\ge 0.868\) is
real and later than Richards’s \(1/4\). The gaps live at
\(X=\exp(\Theta(k))\) and are logarithmic. They do not constrain the
\(X^{1/4}\) coefficient and they do not kill \(1/10\) at that \(X\).

**Hoping the Shiu family is empty.** If \((u^2+m^2,u^2+(m+1)^2)\) were
empty for infinitely many even \(m\) with \(2u+1=(m+1)^2\), then
\(\limsup G(n)/n^{1/4}=2\sqrt{2}\) and Bambah–Chowla would be sharp.
Checked even \(m\le 8000\): the only empty open interval is \(m=2\)
(\(n=21\)). For \(m=4\) one already has \(9^2+9^2=162=n+1\). Occupied.

**A bounded \(p=u-u'\) for every even \(m\).** Least-\(p\) search
through \(m=8000\) has max \(p=40\), attained at Shiu’s own example
\(m=2862\). Success measure for a fixed \(p\) is \(\sim 1/\sqrt{1+p}\).
Independence of \(\sqrt{1+p}\) would make the bad box nonempty for
any fixed \(P\), so bounded \(p\) is not a proof for the tail.

**Hypothesis H / any \(\alpha>0\).** Shiu’s fractional-part hypothesis
would give every positive coefficient. It is exactly the hard
equidistribution statement he left open. Not tonight.

**Empty ladders as an infinite family.** Empty interiors of
\((u^2+m^2,u^2+(m+1)^2)\) exist (the ratio champion \(1493\to 1508\),
\(m=7\), \(u=38\)). Through \(u=1500\) they only occur for \(m\le 14\).
Small-\(m\) residue, not an infinite \(X^{1/4}\) lower bound.

## 2. The useful failure

The Shiu family is **occupied**, not empty. That kills the dream of a
sharp \(2\sqrt{2}\) lower bound from this family, and it is also the
opening: \(a=3\) on the only infinite two-point obstruction is a
search for one extra lattice point in an interval of length \(2m\).

The other useful failure is two-point \(a=3\) itself. Jameson’s \(a=2\)
already holds from \(\min(h_{\mathrm{BC}},(u+1)^2-n)\) for every \(n\)
we checked (and Jameson proved it for all \(n\)). The only \(n\) that
need a third point are the ladder tops sitting in a short integer
window \(k\in[2m-2,3m+2]\). That set is enumerable in \(m\).

## 3. The click

Write the two-point failure test as
\((\min(h,h_2)+3)^4\ge 64n\). Expand. Then:

- rungs \(t\ge 1\) never fail (the left side drops by about
  \(4(2m)^3\) and the right side grows);
- \(k\le 2m-3\) and \(k\ge 3m+3\) never fail;
- so every \(a=3\) obstruction with \(n\ge 2\) is a single ladder top,
  indexed by \((m,k)\).

Also \(m\le\sqrt{2}\,n^{1/4}\), so a bound \(m\le M\) is a bound
\(n\le(M/\sqrt{2})^4\). The infinite-looking problem is a finite
\((m,k)\)-search. For each top, scan lattice points near the circle
for leftover \(< \Phi-3\).

The four exceptions \(3,6,21,91\) are the only unsaved tops. They
are small and exact.

## 4. The argument, in the order it was found

1. Fetch Green #66 and (after the #143 miss) Bloom #222. Record the
   published proven constant: \(2\sqrt{2}\), additive \(-2\) (Jameson),
   open increment \(a=3\) (Shiu).
2. Replay the elementary Bambah–Chowla leftover \(<2\sqrt{2}\,n^{1/4}+1\)
   on \(n\le 10^5\). Zero failures. Two-point \(a=2\) zero failures.
   Two-point \(a=3\) fails on a thin set.
3. Hunt a third lattice point on that thin set, first by scanning
   \(n\le 2\cdot 10^5\). Unsaved: \(3,6,21,91\).
4. Switch from scanning \(n\) to enumerating Shiu ladders
   \((u,m,t)\). Through \(u=20000\) (\(n\le 4\cdot 10^8\)) the unsaved
   set is still those four, and every saved failure has \(t=0\).
5. Prove the integer classification: only tops, only
   \(k\in[2m-2,3m+2]\). Check \(t>0\) count is zero through \(u=5000\),
   then do the expansions.
6. Enumerate danger-zone tops by \((m,k)\). Save each by a near-circle
   lattice search. \(m\le 2000\): \(1\,002\,993\) tops, **zero unsaved**,
   stored witnesses independently checked. \(m\le 8000\):
   \(16\,011\,993\) tops, **zero unsaved**.
7. Exhaustive \(G(n)\) from a two-square table on \([1,5\cdot 10^6]\):
   \(a=3\) fails exactly at \(\{1,3,6,21,91\}\); \(a=2\) fails nowhere.

The range \(m\le 8000\) is \(n\le 1.024\cdot 10^{15}\).

## 5. Computer residue

- `compute/exhaustive_a3_5e6.json` — exact exception set on
  \([1,5\cdot 10^6]\).
- `compute/a3_cert_m250.json` and `compute/a3_cert_m2000.json.gz` —
  stored \((n,a,b,s)\) witnesses, checker
  `compute/verify_a3_cert.py`.
- `compute/a3_summary_m8000.json` — \(16\,011\,993\) tops, \(0\) unsaved.
- `compute/min_p_m8000.json` — least \(p=u-u'\) on the even Shiu
  curve; max \(p=40\) at \(m=2862\).
- `compute/gap_census_2e7.json` — running-max ratio \(2.407\) at
  \(1493\to 1508\); \(1/10\) still crossed at \(X=2\cdot 10^7\).
- `figures/gap_ratios.png` — consecutive gaps over \(X^{1/4}\).

Replay commands: `compute/README.md`.

## 6. What is proved vs still open

**Proved (computer-assisted, this folder).**
\(G(n)<2\sqrt{2}\,n^{1/4}-3\) for \(2\le n\le 1.024\cdot 10^{15}\)
except \(\{3,6,21,91\}\). Classification is exact. Witnesses for
\(m\le 2000\) are independently checked. The \(m\le 8000\) search
uses the same integer lattice scan.

**Still open.**

- Green / Littlewood: \(C=1/10\) for all sufficiently large \(X\).
- Any multiplicative \(\alpha<2\sqrt{2}\) for all large \(n\).
- \(a=3\) for **all** \(n\), not just \(n\le 10^{15}\). The tail
  \(m>8000\) is the same search; we did not run it, and we did not
  find a uniform closed-form replacement.
- Whether \(\limsup G(n)/n^{1/4}\) is positive. The largest observed
  ratio through \(N=2\cdot 10^7\) is \(2.407\), attained at \(n=1508\).
  That is not a bound.

We did not beat \(1/10\). We did beat Jameson’s published additive
\(-2\), on an explicit range, with four exact exceptions and a
replayable checker.
