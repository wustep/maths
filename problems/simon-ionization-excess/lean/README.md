# Lean lemmas for the HPS coefficient and Lieb's pair inequality

The algebraic pieces of Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1,
Proposition 2.5, and the triangle inequality Lieb uses for
$N_c<2Z+1$. This folder does not formalize HVZ, the quadratic-form
remainder, or a bound on the excess charge.

Pinned toolchain: Lean 4.32.0, mathlib `v4.32.0`. The Lake
`packagesDir` is `../../../.lake/packages`, so this problem and
`problems/brocard/lean` share one mathlib checkout.

## Replay

From this directory:

```bash
export PATH="$HOME/.elan/bin:$PATH"
lake exe cache get
lake build
```

`lake build` checks four libraries: `B3NatWitness`, `HPSRational`,
`HPSCoefficient`, `LiebPair`.

If the mathlib download fails, the integer witnesses still check
without Lake:

```bash
lean B3NatWitness.lean
```

## What is proved

`HPSCoefficient.lean` defines

$$
b(3)=\frac23\frac{(1+\sqrt{2})^{1/3}}{(1+\sqrt{2})^{2/3}-1},\qquad
b(2)=\frac{\sqrt{2}+1}{2}
$$

and proves the printed enclosures
$11184/10000<b(3)<11185/10000$ and
$12071/10000<b(2)<12072/10000$. The $b(3)$ argument isolates
$\delta=t-t^{-1}$ for $t=(1+\sqrt{2})^{1/3}$, uses
$\delta^3+3\delta=2$, and compares the cubic at the two rational
endpoints.

`LiebPair.lean` proves that for $x\neq y$ in
$\mathbb{R}^3$ one has $(\|x\|+\|y\|)/\|x-y\|\ge 1$. That is the
triangle inequality. It is not the full Lieb ionization bound.

`B3NatWitness.lean` and `HPSRational.lean` record the same
comparisons after the radicals are cleared, as `Nat` inequalities
and as real inequalities that need only `Mathlib.Data.Real.Basic`.
