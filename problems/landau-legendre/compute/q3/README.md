# Landau 3 / Legendre, third computation

## Outcome

Assume RH. For every real $x\geq1$ and every

$$
\delta\geq\frac{4504880398387}{20000000000000}
=0.22524401991935,
$$

the interval $[x^{2+\delta},(x+1)^{2+\delta}]$ contains a prime. This
tightens q1's certified threshold $0.22525$. It does not prove Legendre's
conjecture and does not extend the finite Oppermann record.

## Replay

From any directory, run

```bash
problems/landau-legendre/compute/q3/run_all.sh
```

The replay uses Python 3 and a standard C compiler, needs no network, and
writes only to a temporary directory. It first rechecks q1's exact certificate
for the previous threshold, regenerates the q3 certificate, byte-compares it
with the committed copy, reconstructs every rational enclosure independently,
and runs a separate `long double` calculation.

## Why the extra digits are real

Put

$$
N=70{,}500{,}000{,}000{,}000,\qquad
d=0.22524401991935,\qquad
\alpha=2+d,\qquad X=N^{2/\alpha}.
$$

For $2<\alpha<3$, Taylor's theorem gives, for $x>0$,

$$
(x+1)^\alpha-x^\alpha
>\alpha x^{\alpha-1}
+\frac{\alpha(\alpha-1)}2x^{\alpha-2}.
$$

Consequently, Chamberland--Straub inequality (6) follows if

$$
S(x)=x^{d/2}+\frac{\alpha-1}{2}x^{d/2-1}
-\frac1\alpha x^{-\alpha/2}-\frac{22}{25}\log x>0.
$$

Their simpler condition (5) drops the last two power terms. At the splice
$x=X$, its certified logarithmic margin is negative: its exact upper bound is
less than $-2.03\cdot10^{-13}$. Thus q1's one-term test does not certify this
new value.

Write $A=X^{d/2}=N^{d/\alpha}$ and $b=(\alpha-1)/2$. At $X$, the ratio of
the retained correction to $A$ is

$$
t=\frac bX-\frac1{\alpha N A}.
$$

The rational certificate proves $2\cdot10^{12}<X<2.8\cdot10^{12}$ and
$25<A<26$, then obtains an exact lower bound for $t$. Using
$\log(1+t)\geq t/(1+t)$ gives a positive strengthened overlap margin greater
than $1.51\cdot10^{-14}$.

For $x\geq X$, differentiation gives

$$
xS'(x)=\frac d2x^{d/2}-\frac{22}{25}
-b\left(1-\frac d2\right)x^{d/2-1}
+\frac12x^{-\alpha/2}.
$$

The same coarse bounds prove this is greater than $1.93$. Hence $S$ is
increasing after the splice. The analytic argument covers $x\geq X$, while
the published finite Oppermann result and Chamberland--Straub Proposition 3.4
cover $x<X$. The exponent-transfer argument from q1 covers every larger
$\delta$.

## Certificate

`certs/rh_delta_taylor.json` contains normalized rational enclosures for all
logarithms and every sign used above. No decimal approximation is trusted by
the authoritative verifier.
