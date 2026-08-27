# q2 — homogeneous plane Keller maps

This route started from the imagined end-state “classify every homogeneous
plane perturbation.” It closes, but only by recovering a classical shear
family, so it does not improve the degree record.

Let \(H=(R,S)\) be homogeneous of degree \(d\ge2\), and suppose
\(F=I+H\) has Jacobian determinant 1. In

$$
\det JF=1+(R_x+S_y)+(R_xS_y-R_yS_x),
$$

the two nonconstant terms have distinct degrees. Thus the divergence and
\(\det JH\) vanish separately. The divergence identity gives

$$
R=h_y,\qquad S=-h_x
$$

for a binary homogeneous form \(h\) of degree \(d+1\), while the second
identity says that the Hessian determinant of \(h\) is zero.

For completeness, dehomogenize as \(h=x^m f(y/x)\). Its Hessian determinant,
apart from the nonzero factor \((m-1)x^{2m-4}\), is

$$
mff''-(m-1)(f')^2.
$$

At a root of multiplicity \(r\), vanishing forces \(r=m\). Hence \(f\) is
constant or has one root of multiplicity \(m\), so \(h\) is a power of a
linear form. After absorbing constants, every map in the class has the form

$$
F(x,y)=\bigl(x+cb(ax+by)^d,\ y-ca(ax+by)^d\bigr).
$$

The linear form \(ax+by\) is invariant, so changing the two nonlinear signs
gives the polynomial inverse. `verify_family.py` checks the Jacobian, invariant,
and both compositions in exact sparse integer arithmetic, including degree
125.

```bash
./problems/smale-jacobian-n2/compute/q2/run_all.sh
```

Final marker: `Q2_HOMOGENEOUS_CLASS_PASS`.
