# Walkthrough — Thin cyclic additive bases

- Problem: `problems/thin-cyclic-bases`
- Quest: Green 100 #33, infinitely many \(q\) with
  \(|A|=(\sqrt2+o(1))\sqrt q\) and \(A+A=\mathbb Z/q\mathbb Z\)
- Model: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Date: 2026-08-17
- Argument status: published infinite family independently replayed;
  no thinner family found
- Problem status: open

## 0. What was actually missing

The counting degree of freedom is real: unordered pairs plus doubles
give at most \(\binom{m+1}{2}\) sums, so any sum cover has
\(m\ge(\sqrt2+o(1))\sqrt q\). Difference covers already meet the
companion bound \(m\sim\sqrt q\) along Singer and Bose orders
(Banakh–Gavrylkiv). The missing object is a *sum* packing that is
also a cover — a Sidon-like set of size \(\sqrt{2q}\) whose pairwise
sums hit every residue, or a structured thickening of a known Sidon
set that adds only \((\sqrt2-1)\sqrt q\) extra points.

Green’s parabola remark makes the same gap geometric: on
\(y=x^2\), slopes are pairwise sums. A subset of the parabola of
size \(\sqrt{2p}\) determines every finite direction if and only if
those sums exhaust \(\mathbb F_p\).

## 1. False starts (named obstacles)

- **Convert a Singer difference set by \(A\cup(-A)\).** A
  reversible Singer set of size \(k>5\) is impossible, because
  \(k(k+1)/2<k(k-1)+1\). The symmetric hull costs a factor 2 and
  returns the elementary constant, not \(\sqrt2\).
- **Thicken Singer or Bose by an interval or a short AP.** Both
  seeds are sum packings, so they miss about half the group. A
  translate of a Singer set always meets the existing sumset
  (\(D+D-D=G\)), and a single extra point covers only about
  \(|D|/2\) missed residues. Interval/AP repairs inside the
  \(\sqrt{8/3}\) budget never completed.
- **Three equal arithmetic progressions \(I\cup dI\cup eI\).**
  Three \(\ell\times\ell\) rectangles have just enough cells to
  cover \(n\sim3.4\ell^2\) if they tile. A 56,700-formula linear
  scan and a wider \((d,e)\) scan for \(\ell\le12\) produced no
  cover in the BEL-beating window.
- **Delete points from the elementary two-AP cover.** That cover
  is essentially a collision-free rectangle. Greedy deletion drops
  0 or 1 point for \(n\le210\). You cannot walk from constant 2
  down to \(1.63\) by local thinning.
- **Quadratic windows and geometric progressions in \(\mathbb F_p\).**
  Near-covers at ratio \(\ge2\), not thin covers.

## 2. The useful failure

Singer is the right *shape* of seed — a perfect sum packing of size
\(\sqrt q\) — and the first-order counting for a repair set \(B\) of
size \(\alpha q\) says \(\alpha\ge\sqrt2-1\approx0.414\) is enough
if \(D+B\) and \(B+B\) tile the missed half. The gain histogram
kills the fantasy. Each new point realises only \(\sim|D|/2\) missed
sums, so a hitting-set estimate wants \(\alpha\sim1\) and the
completed ratio drifts back to 2. Random \(B\) is worse: \(D+B\)
hits each missed residue with probability \(1-e^{-\alpha}\), and a
union bound forces an extra \(\sqrt{\log q}\) .

The same arithmetic explains why BEL stops at \(3/8\). A
diameter-2 generating set in
\(\mathbb Z_{r_1}\times\mathbb Z_{r_2}\times\mathbb Z_w\) needs a
4-element strict sum cover of \(\mathbb Z_w\). The largest such \(w\)
is 6. That pair \((|B|,w)=(4,6)\) maximises \(w/|B|^2\) among
Haanpää’s table. Larger \(B\) loses.

## 3. The click

There was no construction click. The organisational click was to
stop treating “small \(n\) below \(\sqrt{8/3}\)” as progress and to
name the published infinite-family constant correctly:
Bevan–Erskine–Lewis, Corollary 18,
\(\liminf \mathrm{SS}(n,2)/\sqrt n\le\sqrt{8/3}\), not Jia–Shen’s
\(\sqrt3+\varepsilon\) (which is the *all-\(n\)* bound). A dent
tonight is a family with a strictly smaller liminf, or a proof that
the liminf is \(\sqrt2\).

## 4. The argument, in the order it was found

Green #33, then Croot–Lev 5.2, then Caprace–de la Harpe’s \(n_p\),
then Bajnok’s \(\varphi(\mathbb Z_n,[0,2])\), then Jia–Shen
\(\sqrt3\) for every large \(n\), then BEL’s directed circulant
template. The last of these is the live record for infinitely many
\(n\).

The template, for \(q\ge7\) and \(q\equiv1\pmod6\):

- \(T=\mathbb Z_q\times\mathbb Z_{q-2}\times\mathbb Z_6\), cyclic of
  order \(n=6q(q-2)\);
- \(B=\{0,1,2,4\}\) is a strict sum cover of \(\mathbb Z/6\mathbb Z\);
- generators: the first axis, the second axis shifted by \(1\), the
  diagonal \((t,t,2)\) of length \(q+2\), and the slope-2 diagonal
  \((t,2t,4)\) of length \(q\);
- \(A=X\cup\{0\}\) has size \(4q\).

Lemma 6 of BEL guarantees directed diameter 2, hence \(A+A=T\).
CRT writes \(A\) as a subset of \(\mathbb Z/n\mathbb Z\). Independently,
`compute/verify.py` recomputes the cyclic sumset from the listed
residues and checks \(|A+A|=n\).

## 5. Computer residue

Replayable:

```bash
python3 compute/make_bel_certs.py
python3 compute/haanpaa_replay.py
python3 compute/verify.py
```

BEL certificates through \(q=61\) (\(n=21594\), ratio \(1.660\)) all
verify. Haanpää’s twelve cyclic table rows all verify. Search logs:
`linear_family_hits.json` (0 hits), `three_ap_wide.json` (0 hits),
`sidon_repair.json` (no interval/AP completion),
`greedy_singer.json` (unstructured extras, ratio \(\ge1.62\)),
`two_ap_prune.json` (almost nothing drops),
`algebraic_eval.json` (no thin prime-field cover).

## 6. What is proved vs still open

Proved here: the BEL family really does give cyclic sum covers of
size \((4+o(1))q\) in order \(6q(q-2)\), hence
\(\mathrm{SS}(n,2)\le(\sqrt{8/3}+o(1))\sqrt n\) along
\(n=6q(q-2)\), \(q\equiv1\pmod6\). This is the published statement,
independently checked, not a new constant.

Still open: Green’s \(\sqrt2+o(1)\) for infinitely many \(q\); any
liminf strictly below \(\sqrt{8/3}\); Jia–Shen’s challenge of a
universal constant below \(\sqrt3\). Isolated Haanpää-scale tables
do not move any of those.
