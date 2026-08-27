# q3 — the raw tangent sweep cannot be Keller in the plane

Recent higher-dimensional preprints use tangent sweeps as part of their
claimed counterexample mechanism. This check asks only whether the unmodified
geometric sweep can already work in two dimensions.

For any polynomial parametrized curve \(K(w)=(p(w),q(w))\), sweep its tangent
lines by

$$
S(w,\gamma)=K(w)+\gamma K'(w).
$$

The two columns of its Jacobian matrix are \(K'+\gamma K''\) and \(K'\).
Therefore

$$
\det JS
=\gamma\det(K'',K')
=\gamma\bigl(p''q'-p'q''\bigr).
$$

The determinant is divisible by \(\gamma\). It is either zero or nonconstant,
so a raw tangent-line sweep cannot have a nonzero constant Jacobian in the
plane.

`verify_tangent_sweep.py` represents every coefficient of \(p\) and \(q\) by
a separate formal symbol and expands both sides exactly for generic degrees 1
through 12. The displayed two-column calculation proves the same identity for
arbitrary degree; the finite runs guard the implementation and sign convention.

```bash
./problems/smale-jacobian-n2/compute/q3/run_all.sh
```

Final marker: `Q3_TANGENT_SWEEP_OBSTRUCTION_PASS`.

This obstruction is deliberately narrow. It does not exclude a construction
with extra twists, different parameters, or additional coordinates, and it
does not change the finite degree bound.
