# Line SS — cubic-jet L2 of the two-well van der Pol

Status: imagined H(3)≥14 from L2 dropped. Fork kept. Not a dent
of H(3).

Imagined certificate. The second Lyapunov quantity L2 of the
cubic jet at a focus, evaluated on the two-well van der Pol
perturbation of line FF,

$$\dot x=y,\qquad \dot y=x-x^3+\mu(1-x^2)y,$$

is zero while L1 ≠ 0, or else that L2 supplies extra small
cycles and therefore H(3) ≥ 14.

Drop immediately. Each well is already an order-1 weak focus:
after the q1 focal scaling, L1 = √2 μ, and this is nonzero for
μ ≠ 0. The first nonzero quantity uses the cyclicity budget at
that point. L2 is not the first nonzero quantity, so it does
not create a second small cycle there. The Poincaré V2 of this
3-jet is in fact not zero: it is the exact multiple

$$V_2=-\frac{\sqrt{2}\,\mu}{96}(23\mu^2+18)$$

of μ (and of μ³). That is a finite identity, not a 14th cycle,
and not a beat of Li–Liu–Yang H(3) ≥ 13. Two Hopf cycles from
a trace unfolding are not claimed; FF already recorded that
this family does not unfold the trace at (±1, 0).

Fork kept. Replay of L1 = √2 μ at both wells; the cubic-jet
correction L1 = L1_E + 3 a30 + a12 + b21 + 3 b03 already in
FF and GG; V2 in the same Poincaré gauge as q1 line E; and
the μ = 0 Hamiltonian first integrals that force every
Lyapunov quantity to vanish. Symbolic only. Fractions as
strings. Not a bound on H(n).

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/ss-cubic-l2/run.sh
```

Python re-derives Poincaré V1 on a general 3-jet and V1, V2
on this family with sympy. Rust extracts the same jets with a
sparse map, evaluates L1 over Q(√2), and solves the Poincaré
linear systems again by Gaussian elimination over Q(√2) at
integer μ. The two dumps are `diff`ed. Exit 0. Certs:
`certs/core.json`, `certs/jets.json`.

## Dropped — H(3) at least 14 from L2

A second small cycle at the same well would need the first
nonzero Lyapunov quantity to have order at least 2, so that
the displacement

$$d(r)=\tfrac{\pi}{4}L_1 r^3+c\,V_2 r^5+\cdots
=r^3\Bigl(\tfrac{\pi}{4}L_1+c\,V_2 r^2+\cdots\Bigr)$$

could vanish at a positive radius after an unfolding of L1.
Here L1 ≠ 0 already. For small r the bracket is a nonzero
constant plus O(r²). The only small zero is r = 0. V2, zero
or not, does not add a cycle at this point. Fourteen cycles
are not produced, and H(3) ≥ 13 is not beaten.

The other half of the fiction, L2 = 0 while L1 ≠ 0, is false
for this jet: V2 vanishes only at μ = 0, where L1 vanishes
too.

## Kept — L1 replay at both wells

The named field is degree 3. At (±1, 0) the trace
μ(1 − x²) is zero and the determinant is 2, for every μ.
Translate x = ±1 + X, y = Y, then scale

$$u=X,\qquad v=-Y/\sqrt{2},\qquad \tau=\sqrt{2}\,t$$

to the q1 normal form ẋ = −v + ⋯, ẏ = u + ⋯. Every a_ij
vanishes. The surviving 3-jet is

| well | b20 | b11 | b30 | b21 |
| --- | --- | --- | --- | --- |
| +1 | 3/2 | −√2 μ | 1/2 | −√2 μ / 2 |
| −1 | −3/2 | √2 μ | 1/2 | −√2 μ / 2 |

The q1 primitive on the quadratic jet is

$$L_1^{E}=(a_{20}+a_{02})a_{11}-(b_{20}+b_{02})b_{11}-2a_{20}b_{20}+2a_{02}b_{02}.$$

The same Poincaré function that produced V1 = L1_E / 8 on a
quadratic, carried through the cubic terms, adds the unique
correction that keeps V1 = L1 / 8:

$$L_1=L_1^{E}+3a_{30}+a_{12}+b_{21}+3b_{03}.$$

At x = 1 this splits as L1_E = 3√2 μ / 2 and
3 a30 + a12 + b21 + 3 b03 = −√2 μ / 2, hence
L1 = √2 μ and V1 = √2 μ / 8. At x = −1 the quadratic jet
flips sign and the same two pieces reassemble to the same
L1 = √2 μ. Both languages recompute this; it matches FF.

Evaluating only L1_E would report 3√2 μ / 2, which is not
the first Lyapunov quantity of the 3-jet.

## Kept — V2 of this 3-jet

The Poincaré–Lyapunov function F = r²/2 + F3 + F4 + F5 + F6
is built in the q1 gauge (the coefficient of y^n on each even
F_n is set to zero; that is what `l1_focal.py` solves). Then

$$\frac{dF}{dt}=V_1 r^4+V_2 r^6+O(7).$$

On this family both wells give

$$V_1=\frac{\sqrt{2}\,\mu}{8},\qquad
V_2=-\frac{\sqrt{2}\,\mu}{96}(23\mu^2+18).$$

Rust does not trust the closed form: it solves the same
linear systems over Q(√2) at μ ∈ {−2, −1, 0, 1, 2} and
interpolates the odd cubic in μ. The samples are
V2(1) = −41 √2 / 96 and V2(2) = −55 √2 / 24.

This V2 is L2 as a concrete polynomial in the q1 gauge. It is
not a primitive Bautin generator, and it is not a second
small cycle.

## Kept — at μ = 0 every Lyapunov vanishes

When μ = 0 the named field is the FF Hamiltonian
ẋ = y, ẏ = x − x³. After the same scaling, each well has a
polynomial first integral

$$H_{+}=v^2+u^2+u^3+\frac{u^4}{4},\qquad
H_{-}=v^2+u^2-u^3+\frac{u^4}{4}.$$

Formal differentiation along the μ = 0 3-jet is the zero
polynomial (cleared: 4H). The equilibria are centers, so
every Lyapunov quantity vanishes. The Poincaré computation
agrees through order 6: V1(0) = V2(0) = 0.

## What this is not

Not a bound on H(n). Not a dent. Not fourteen cycles. Not a
proved pair of Hopf cycles. Not a claim that L2 is the first
nonzero quantity. The identities are reusable: a stranger can
run `run.sh` and read L1 = √2 μ and
V2 = −√2 μ (23 μ² + 18) / 96 off the JSON.
