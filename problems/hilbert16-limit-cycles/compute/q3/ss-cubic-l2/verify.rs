//! Independent replay of the two-well cubic-jet L1 and Poincaré V2.
//!
//! Python (`verify.py`) expands with sympy and re-derives V1, V2
//! symbolically. This program extracts the same 3-jets with a sparse
//! map, evaluates
//!     L1 = L1_E + 3 a30 + a12 + b21 + 3 b03
//! over Q(√2), and solves the Poincaré linear systems again by
//! Gaussian elimination over Q(√2) at integer μ. Imagined H(3) ≥ 14
//! from L2 is not certified. Order is 1.
//!
//! rustc only.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process;

fn gcd_i128(mut a: i128, mut b: i128) -> i128 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    if a == 0 {
        1
    } else {
        a
    }
}

// ---------------------------------------------------------------------------
// Q and Q(√2)
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Rat {
    n: i128,
    d: i128,
}

impl Rat {
    fn new(n: i128, d: i128) -> Self {
        assert!(d != 0, "zero denominator");
        let g = gcd_i128(n, d);
        let mut n = n / g;
        let mut d = d / g;
        if d < 0 {
            n = -n;
            d = -d;
        }
        Self { n, d }
    }

    fn from_i(n: i128) -> Self {
        Self::new(n, 1)
    }

    fn zero() -> Self {
        Self::from_i(0)
    }

    fn is_zero(self) -> bool {
        self.n == 0
    }

    fn neg(self) -> Self {
        Self::new(-self.n, self.d)
    }

    fn add(self, other: Self) -> Self {
        Self::new(self.n * other.d + other.n * self.d, self.d * other.d)
    }

    fn sub(self, other: Self) -> Self {
        self.add(other.neg())
    }

    fn mul(self, other: Self) -> Self {
        Self::new(self.n * other.n, self.d * other.d)
    }

    fn div(self, other: Self) -> Self {
        Self::new(self.n * other.d, self.d * other.n)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Alg {
    a: Rat,
    b: Rat,
}

impl Alg {
    fn new(a: Rat, b: Rat) -> Self {
        Self { a, b }
    }

    fn from_rat(a: Rat) -> Self {
        Self {
            a,
            b: Rat::zero(),
        }
    }

    fn from_i(n: i128) -> Self {
        Self::from_rat(Rat::from_i(n))
    }

    fn sqrt2() -> Self {
        Self::new(Rat::zero(), Rat::from_i(1))
    }

    fn zero() -> Self {
        Self::from_i(0)
    }

    fn is_zero(self) -> bool {
        self.a.is_zero() && self.b.is_zero()
    }

    fn neg(self) -> Self {
        Self::new(self.a.neg(), self.b.neg())
    }

    fn add(self, other: Self) -> Self {
        Self::new(self.a.add(other.a), self.b.add(other.b))
    }

    fn sub(self, other: Self) -> Self {
        self.add(other.neg())
    }

    fn mul(self, other: Self) -> Self {
        // (a+b√2)(c+d√2) = (ac+2bd) + (ad+bc)√2
        Self::new(
            self.a.mul(other.a).add(self.b.mul(other.b).mul(Rat::from_i(2))),
            self.a.mul(other.b).add(self.b.mul(other.a)),
        )
    }

    fn scale_i(self, k: i128) -> Self {
        self.mul(Self::from_i(k))
    }

    fn inv(self) -> Self {
        // 1/(a+b√2) = (a-b√2)/(a²-2b²)
        let n = self.a.mul(self.a).sub(self.b.mul(self.b).mul(Rat::from_i(2)));
        assert!(!n.is_zero(), "zero Alg inverse");
        Self::new(self.a.div(n), self.b.neg().div(n))
    }

    fn as_sqrt2_coeff(self) -> Rat {
        assert!(self.a.is_zero(), "expected a pure √2 multiple, got {self:?}");
        self.b
    }
}

// ---------------------------------------------------------------------------
// Homogeneous polynomials in (x, y) over Q(√2)
// coeff[i] multiplies x^i y^{deg-i}
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
struct Hom {
    c: Vec<Alg>,
}

impl Hom {
    fn deg(&self) -> usize {
        self.c.len() - 1
    }

    fn zero(deg: usize) -> Self {
        Self {
            c: vec![Alg::zero(); deg + 1],
        }
    }

    fn add(&self, other: &Self) -> Self {
        assert_eq!(self.deg(), other.deg());
        Self {
            c: self
                .c
                .iter()
                .zip(other.c.iter())
                .map(|(x, y)| x.add(*y))
                .collect(),
        }
    }

    fn fy(&self) -> Self {
        let n = self.deg();
        if n == 0 {
            return Self { c: vec![] };
        }
        let mut out = Self::zero(n - 1);
        for k in 0..n {
            out.c[k] = self.c[k].scale_i((n - k) as i128);
        }
        out
    }

    fn mul(&self, other: &Self) -> Self {
        let mut out = Self::zero(self.deg() + other.deg());
        for (i, ai) in self.c.iter().enumerate() {
            for (j, bj) in other.c.iter().enumerate() {
                out.c[i + j] = out.c[i + j].add(ai.mul(*bj));
            }
        }
        out
    }
}

fn y1() -> Hom {
    // y, degree 1: c[0] = 1
    Hom {
        c: vec![Alg::from_i(1), Alg::zero()],
    }
}

fn r_pow(m: usize) -> Hom {
    // (x²+y²)^m
    let mut out = Hom::zero(2 * m);
    for j in 0..=m {
        let mut bin = 1i128;
        for t in 0..j {
            bin = bin * (m - t) as i128 / (t + 1) as i128;
        }
        out.c[2 * j] = Alg::from_i(bin);
    }
    out
}

fn lie_rot(f: &Hom) -> Hom {
    let n = f.deg();
    let mut out = Hom::zero(n);
    for k in 0..=n {
        let mut s = Alg::zero();
        if k + 1 <= n {
            s = s.add(f.c[k + 1].scale_i(-((k + 1) as i128)));
        }
        if k >= 1 {
            s = s.add(f.c[k - 1].scale_i((n - k + 1) as i128));
        }
        out.c[k] = s;
    }
    out
}

fn ge_solve(eqs: &[Vec<Alg>]) -> Vec<Alg> {
    let n = eqs.len();
    let mut a = eqs.to_vec();
    for col in 0..n {
        let mut piv = None;
        for r in col..n {
            if !a[r][col].is_zero() {
                piv = Some(r);
                break;
            }
        }
        let piv = piv.unwrap_or_else(|| panic!("singular Poincaré system at col {col}"));
        a.swap(col, piv);
        let inv = a[col][col].inv();
        for x in a[col].iter_mut() {
            *x = x.mul(inv);
        }
        for r in 0..n {
            if r == col {
                continue;
            }
            let fac = a[r][col];
            if fac.is_zero() {
                continue;
            }
            for k in 0..=n {
                a[r][k] = a[r][k].sub(fac.mul(a[col][k]));
            }
        }
    }
    (0..n).map(|i| a[i][n]).collect()
}

fn solve_odd(known: &Hom) -> Hom {
    let n = known.deg();
    let mut eqs = Vec::new();
    for k in 0..=n {
        let mut row = vec![Alg::zero(); n + 2];
        if k + 1 <= n {
            row[k + 1] = Alg::from_i(-((k + 1) as i128));
        }
        if k >= 1 {
            row[k - 1] = Alg::from_i((n - k + 1) as i128);
        }
        row[n + 1] = known.c[k].neg();
        eqs.push(row);
    }
    Hom { c: ge_solve(&eqs) }
}

fn solve_even(known: &Hom) -> (Hom, Alg) {
    let n = known.deg();
    let rn = r_pow(n / 2);
    let mut eqs = Vec::new();
    // Gauge: y^n coefficient of F vanishes.
    let mut gauge = vec![Alg::zero(); n + 3];
    gauge[0] = Alg::from_i(1);
    eqs.push(gauge);
    for k in 0..=n {
        let mut row = vec![Alg::zero(); n + 3];
        if k + 1 <= n {
            row[k + 1] = Alg::from_i(-((k + 1) as i128));
        }
        if k >= 1 {
            row[k - 1] = Alg::from_i((n - k + 1) as i128);
        }
        row[n + 1] = rn.c[k].neg();
        row[n + 2] = known.c[k].neg();
        eqs.push(row);
    }
    let sol = ge_solve(&eqs);
    (Hom { c: sol[..n + 1].to_vec() }, sol[n + 1])
}

fn poincare_v1_v2(mu: i128, plus: bool) -> (Alg, Alg) {
    let s = Alg::sqrt2();
    let mu_a = Alg::from_i(mu);
    let (b20, b11, b30, b21) = if plus {
        (
            Alg::from_rat(Rat::new(3, 2)),
            s.mul(mu_a).neg(),
            Alg::from_rat(Rat::new(1, 2)),
            s.mul(mu_a).mul(Alg::from_rat(Rat::new(-1, 2))),
        )
    } else {
        (
            Alg::from_rat(Rat::new(-3, 2)),
            s.mul(mu_a),
            Alg::from_rat(Rat::new(1, 2)),
            s.mul(mu_a).mul(Alg::from_rat(Rat::new(-1, 2))),
        )
    };
    // Q2 = b20 x² + b11 x y
    let q2 = Hom {
        c: vec![Alg::zero(), b11, b20],
    };
    // Q3 = b30 x³ + b21 x² y
    let q3 = Hom {
        c: vec![Alg::zero(), Alg::zero(), b21, b30],
    };
    let yy = y1();
    let f3 = solve_odd(&yy.mul(&q2));
    let known4 = f3.fy().mul(&q2).add(&yy.mul(&q3));
    let (f4, v1) = solve_even(&known4);
    let known5 = f4.fy().mul(&q2).add(&f3.fy().mul(&q3));
    let f5 = solve_odd(&known5);
    let known6 = f5.fy().mul(&q2).add(&f4.fy().mul(&q3));
    let (_f6, v2) = solve_even(&known6);
    (v1, v2)
}

fn expected_v1(mu: i128) -> Alg {
    Alg::sqrt2().mul(Alg::from_i(mu)).mul(Alg::from_rat(Rat::new(1, 8)))
}

fn expected_v2(mu: i128) -> Alg {
    // -√2 μ (23 μ² + 18) / 96
    let inner = 23 * mu * mu + 18;
    Alg::sqrt2()
        .mul(Alg::from_i(-mu))
        .mul(Alg::from_i(inner))
        .mul(Alg::from_rat(Rat::new(1, 96)))
}

// ---------------------------------------------------------------------------
// Sparse integer polynomials
// ---------------------------------------------------------------------------

type Exp = Vec<u8>;

#[derive(Clone, Debug)]
struct Poly {
    vars: Vec<String>,
    terms: BTreeMap<Exp, i128>,
}

impl Poly {
    fn zero(vars: &[String]) -> Self {
        Self {
            vars: vars.to_vec(),
            terms: BTreeMap::new(),
        }
    }

    fn constant(vars: &[String], value: i128) -> Self {
        let mut out = Self::zero(vars);
        if value != 0 {
            out.terms.insert(vec![0; vars.len()], value);
        }
        out
    }

    fn var(vars: &[String], name: &str) -> Self {
        let idx = vars
            .iter()
            .position(|v| v == name)
            .unwrap_or_else(|| panic!("unknown variable {name}"));
        let mut exp = vec![0u8; vars.len()];
        exp[idx] = 1;
        let mut out = Self::zero(vars);
        out.terms.insert(exp, 1);
        out
    }

    fn prune(&mut self) {
        self.terms.retain(|_, c| *c != 0);
    }

    fn add(&self, other: &Self) -> Self {
        assert_eq!(self.vars, other.vars);
        let mut out = self.clone();
        for (exp, coeff) in &other.terms {
            *out.terms.entry(exp.clone()).or_insert(0) += coeff;
        }
        out.prune();
        out
    }

    fn neg(&self) -> Self {
        let mut out = self.clone();
        for coeff in out.terms.values_mut() {
            *coeff = -*coeff;
        }
        out
    }

    fn sub(&self, other: &Self) -> Self {
        self.add(&other.neg())
    }

    fn mul(&self, other: &Self) -> Self {
        assert_eq!(self.vars, other.vars);
        let mut out = Self::zero(&self.vars);
        for (e1, c1) in &self.terms {
            for (e2, c2) in &other.terms {
                let exp: Exp = e1.iter().zip(e2.iter()).map(|(a, b)| a + b).collect();
                *out.terms.entry(exp).or_insert(0) += c1 * c2;
            }
        }
        out.prune();
        out
    }

    fn pow(&self, mut n: u32) -> Self {
        let mut out = Self::constant(&self.vars, 1);
        let mut base = self.clone();
        while n > 0 {
            if n & 1 == 1 {
                out = out.mul(&base);
            }
            base = base.mul(&base);
            n >>= 1;
        }
        out
    }

    fn scale(&self, k: i128) -> Self {
        if k == 0 {
            return Self::zero(&self.vars);
        }
        let mut out = self.clone();
        for coeff in out.terms.values_mut() {
            *coeff *= k;
        }
        out.prune();
        out
    }

    fn dvar(&self, name: &str) -> Self {
        let idx = self
            .vars
            .iter()
            .position(|v| v == name)
            .unwrap_or_else(|| panic!("unknown variable {name}"));
        let mut out = Self::zero(&self.vars);
        for (exp, coeff) in &self.terms {
            let power = exp[idx];
            if power == 0 {
                continue;
            }
            let mut new_exp = exp.clone();
            new_exp[idx] = power - 1;
            *out.terms.entry(new_exp).or_insert(0) += coeff * i128::from(power);
        }
        out.prune();
        out
    }

    fn eval(&self, values: &BTreeMap<String, i128>) -> i128 {
        let mut total = 0i128;
        for (exp, coeff) in &self.terms {
            let mut mon = *coeff;
            for (name, power) in self.vars.iter().zip(exp.iter()) {
                if *power > 0 {
                    mon *= values[name].pow(u32::from(*power));
                }
            }
            total += mon;
        }
        total
    }

    fn coeff(&self, powers: &[(&str, u8)]) -> i128 {
        let mut exp = vec![0u8; self.vars.len()];
        for (name, power) in powers {
            let idx = self
                .vars
                .iter()
                .position(|v| v == *name)
                .unwrap_or_else(|| panic!("unknown variable {name}"));
            exp[idx] = *power;
        }
        self.terms.get(&exp).copied().unwrap_or(0)
    }

    fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }
}

fn names(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_string()).collect()
}

fn v(vars: &[String], name: &str) -> Poly {
    Poly::var(vars, name)
}

fn c(vars: &[String], value: i128) -> Poly {
    Poly::constant(vars, value)
}

fn require_zero(poly: &Poly, label: &str) {
    if !poly.is_zero() {
        panic!("{label} is not the zero polynomial: {:?}", poly.terms);
    }
}

fn reduce_s(poly: &Poly) -> Poly {
    let s_idx = poly
        .vars
        .iter()
        .position(|n| n == "s")
        .expect("s variable");
    let mut out = Poly::zero(&poly.vars);
    for (exp, coeff) in &poly.terms {
        let mut e = exp.clone();
        let mut s_pow = e[s_idx];
        let mut extra = 1i128;
        while s_pow >= 2 {
            extra *= 2;
            s_pow -= 2;
        }
        e[s_idx] = s_pow;
        *out.terms.entry(e).or_insert(0) += coeff * extra;
    }
    out.prune();
    out
}

// Jet coefficient as (num, den, s_power) of the μ-linear or μ-free part.
type JetC = (i128, i128, u8);

fn reduce_frac(num: i128, den: i128, sp: u8) -> JetC {
    if num == 0 {
        return (0, 1, 0);
    }
    let g = gcd_i128(num, den);
    let mut num = num / g;
    let mut den = den / g;
    if den < 0 {
        num = -num;
        den = -den;
    }
    (num, den, sp)
}

fn jet_from_n(n_poly: &Poly) -> BTreeMap<String, JetC> {
    let mut out = BTreeMap::new();
    let raw = |powers: &[(&str, u8)]| n_poly.coeff(powers);
    for name in ["a20", "a11", "a02", "a30", "a21", "a12", "a03", "b02", "b12", "b03"] {
        out.insert(name.to_string(), (0, 1, 0));
    }
    out.insert("b20".into(), reduce_frac(-raw(&[("u", 2)]), 2, 0));
    out.insert("b30".into(), reduce_frac(-raw(&[("u", 3)]), 2, 0));
    let b11 = -raw(&[("u", 1), ("v", 1), ("mu", 1), ("s", 1)]);
    if raw(&[("u", 1), ("v", 1)]) != 0
        || raw(&[("u", 1), ("v", 1), ("mu", 1)]) != 0
        || raw(&[("u", 1), ("v", 1), ("s", 1)]) != 0
    {
        panic!("unexpected b11 pieces");
    }
    out.insert("b11".into(), reduce_frac(b11, 2, 1));
    let b21 = -raw(&[("u", 2), ("v", 1), ("mu", 1), ("s", 1)]);
    if raw(&[("u", 2), ("v", 1)]) != 0
        || raw(&[("u", 2), ("v", 1), ("mu", 1)]) != 0
        || raw(&[("u", 2), ("v", 1), ("s", 1)]) != 0
    {
        panic!("unexpected b21 pieces");
    }
    out.insert("b21".into(), reduce_frac(b21, 2, 1));
    out
}

fn add_jc(a: JetC, b: JetC) -> JetC {
    let (n1, d1, s1) = a;
    let (n2, d2, s2) = b;
    if n1 == 0 {
        return b;
    }
    if n2 == 0 {
        return a;
    }
    assert_eq!(s1, s2, "cannot add distinct s-powers");
    reduce_frac(n1 * d2 + n2 * d1, d1 * d2, s1)
}

fn mul_jc(a: JetC, b: JetC) -> JetC {
    let (n1, d1, s1) = a;
    let (n2, d2, s2) = b;
    let mut num = n1 * n2;
    let den = d1 * d2;
    let mut sp = s1 + s2;
    let mut extra = 1i128;
    while sp >= 2 {
        extra *= 2;
        sp -= 2;
    }
    num *= extra;
    reduce_frac(num, den, sp)
}

fn sc_jc(a: JetC, k: i128) -> JetC {
    reduce_frac(a.0 * k, a.1, a.2)
}

fn l1_from_jet(jet: &BTreeMap<String, JetC>) -> (JetC, JetC, JetC) {
    let a20 = jet["a20"];
    let a11 = jet["a11"];
    let a02 = jet["a02"];
    let b20 = jet["b20"];
    let b11 = jet["b11"];
    let b02 = jet["b02"];
    let a30 = jet["a30"];
    let a12 = jet["a12"];
    let b21 = jet["b21"];
    let b03 = jet["b03"];
    let mut lq = mul_jc(add_jc(a20, a02), a11);
    lq = add_jc(lq, sc_jc(mul_jc(add_jc(b20, b02), b11), -1));
    lq = add_jc(lq, sc_jc(mul_jc(a20, b20), -2));
    lq = add_jc(lq, sc_jc(mul_jc(a02, b02), 2));
    let lc = add_jc(add_jc(sc_jc(a30, 3), a12), add_jc(b21, sc_jc(b03, 3)));
    let lf = add_jc(lq, lc);
    (lq, lc, lf)
}

fn interpolate_odd_cubic(v2_over_s: &[(i128, Rat)]) -> (Rat, Rat) {
    // V2/√2 = a μ + b μ³. Use μ=1 and μ=2.
    let mut y1 = None;
    let mut y2 = None;
    for (mu, val) in v2_over_s {
        if *mu == 1 {
            y1 = Some(*val);
        }
        if *mu == 2 {
            y2 = Some(*val);
        }
    }
    let y1 = y1.expect("need V2(1)");
    let y2 = y2.expect("need V2(2)");
    // a + b = y1
    // 2a + 8b = y2  => a + 4b = y2/2
    // (a+b) - (a+4b) = -3b = y1 - y2/2, so b = (y2/2 - y1)/3
    let half_y2 = y2.div(Rat::from_i(2));
    let b = half_y2.sub(y1).div(Rat::from_i(3));
    let a = y1.sub(b);
    (a, b)
}

fn check_all() {
    let xy = names(&["x", "y"]);
    let x = v(&xy, "x");
    let y = v(&xy, "y");
    let p = y.clone();
    let q = x.sub(&x.pow(3));
    let dp_dx = p.dvar("x");
    let dp_dy = p.dvar("y");
    let dq_dx = q.dvar("x");
    let dq_dy = q.dvar("y");
    let det = dp_dx.mul(&dq_dy).sub(&dp_dy.mul(&dq_dx));
    require_zero(&det.sub(&x.pow(2).scale(3).sub(&c(&xy, 1))), "unperturbed det");
    require_zero(&dp_dx.add(&dq_dy), "unperturbed div");

    let xym = names(&["x", "y", "mu"]);
    let xp = v(&xym, "x");
    let yp = v(&xym, "y");
    let mu = v(&xym, "mu");
    let pp = yp.clone();
    let qp = xp
        .sub(&xp.pow(3))
        .add(&mu.mul(&c(&xym, 1).sub(&xp.pow(2))).mul(&yp));
    let dpp_dx = pp.dvar("x");
    let dpp_dy = pp.dvar("y");
    let dqp_dx = qp.dvar("x");
    let dqp_dy = qp.dvar("y");
    let trace = dpp_dx.add(&dqp_dy);
    require_zero(
        &trace.sub(&mu.mul(&c(&xym, 1).sub(&xp.pow(2)))),
        "perturbed trace",
    );
    let detp = dpp_dx.mul(&dqp_dy).sub(&dpp_dy.mul(&dqp_dx));
    for xv in [0i128, 1, -1] {
        for muv in -3i128..=3 {
            let mut vals = BTreeMap::new();
            vals.insert("x".into(), xv);
            vals.insert("y".into(), 0);
            vals.insert("mu".into(), muv);
            if pp.eval(&vals) != 0 || qp.eval(&vals) != 0 {
                panic!("perturbed ({xv},0) not equilibrium");
            }
            if xv == 0 {
                if detp.eval(&vals) != -1 || trace.eval(&vals) != muv {
                    panic!("saddle linearization");
                }
            } else if detp.eval(&vals) != 2 || trace.eval(&vals) != 0 {
                panic!("well linearization");
            }
        }
    }

    let xyms = names(&["X", "Y", "mu"]);
    let xx = v(&xyms, "X");
    let yy = v(&xyms, "Y");
    let mm = v(&xyms, "mu");
    let one = c(&xyms, 1);
    let xp1 = one.add(&xx);
    let q_plus = xp1
        .sub(&xp1.pow(3))
        .add(&mm.mul(&one.sub(&xp1.pow(2))).mul(&yy));
    let claimed_plus = xx
        .scale(-2)
        .sub(&xx.pow(2).scale(3))
        .sub(&xx.pow(3))
        .sub(&mm.scale(2).mul(&xx).mul(&yy))
        .sub(&mm.mul(&xx.pow(2)).mul(&yy));
    require_zero(&q_plus.sub(&claimed_plus), "+1 translation");
    let xm1 = xx.sub(&one);
    let q_minus = xm1
        .sub(&xm1.pow(3))
        .add(&mm.mul(&one.sub(&xm1.pow(2))).mul(&yy));
    let claimed_minus = xx
        .scale(-2)
        .add(&xx.pow(2).scale(3))
        .sub(&xx.pow(3))
        .add(&mm.scale(2).mul(&xx).mul(&yy))
        .sub(&mm.mul(&xx.pow(2)).mul(&yy));
    require_zero(&q_minus.sub(&claimed_minus), "-1 translation");

    let uvms = names(&["u", "v", "mu", "s"]);
    let u = v(&uvms, "u");
    let vv = v(&uvms, "v");
    let mu4 = v(&uvms, "mu");
    let s = v(&uvms, "s");
    let n_plus = reduce_s(
        &u.pow(3)
            .neg()
            .sub(&u.pow(2).scale(3))
            .add(&mu4.scale(2).mul(&s).mul(&u).mul(&vv))
            .add(&mu4.mul(&s).mul(&u.pow(2)).mul(&vv)),
    );
    if n_plus.coeff(&[("u", 2)]) != -3
        || n_plus.coeff(&[("u", 3)]) != -1
        || n_plus.coeff(&[("u", 1), ("v", 1), ("mu", 1), ("s", 1)]) != 2
        || n_plus.coeff(&[("u", 2), ("v", 1), ("mu", 1), ("s", 1)]) != 1
    {
        panic!("N+ coefficients");
    }
    let n_minus = reduce_s(
        &u.pow(3)
            .neg()
            .add(&u.pow(2).scale(3))
            .add(&mu4.scale(2).mul(&u).mul(&s.mul(&vv).neg()))
            .sub(&mu4.mul(&u.pow(2)).mul(&s.mul(&vv).neg())),
    );
    if n_minus.coeff(&[("u", 2)]) != 3
        || n_minus.coeff(&[("u", 3)]) != -1
        || n_minus.coeff(&[("u", 1), ("v", 1), ("mu", 1), ("s", 1)]) != -2
        || n_minus.coeff(&[("u", 2), ("v", 1), ("mu", 1), ("s", 1)]) != 1
    {
        panic!("N- coefficients");
    }

    let jet_p = jet_from_n(&n_plus);
    let jet_m = jet_from_n(&n_minus);
    if jet_p["b20"] != (3, 2, 0)
        || jet_p["b11"] != (-1, 1, 1)
        || jet_p["b30"] != (1, 2, 0)
        || jet_p["b21"] != (-1, 2, 1)
    {
        panic!("plus jet {jet_p:?}");
    }
    if jet_m["b20"] != (-3, 2, 0)
        || jet_m["b11"] != (1, 1, 1)
        || jet_m["b30"] != (1, 2, 0)
        || jet_m["b21"] != (-1, 2, 1)
    {
        panic!("minus jet {jet_m:?}");
    }
    let (lq_p, lc_p, lf_p) = l1_from_jet(&jet_p);
    let (lq_m, lc_m, lf_m) = l1_from_jet(&jet_m);
    if lq_p != (3, 2, 1) || lc_p != (-1, 2, 1) || lf_p != (1, 1, 1) {
        panic!("L1 plus {lq_p:?} {lc_p:?} {lf_p:?}");
    }
    if lq_m != (3, 2, 1) || lc_m != (-1, 2, 1) || lf_m != (1, 1, 1) {
        panic!("L1 minus {lq_m:?} {lc_m:?} {lf_m:?}");
    }
    if lq_p == lf_p {
        panic!("L1_E unexpectedly equals L1");
    }

    // Generic quadratic focus and a Hamiltonian quadratic.
    let mut focus = BTreeMap::new();
    for name in [
        "a20", "a11", "a02", "b20", "b11", "b02", "a30", "a21", "a12", "a03", "b30", "b21", "b12",
        "b03",
    ] {
        focus.insert(name.to_string(), (0, 1, 0));
    }
    focus.insert("a20".into(), (1, 1, 0));
    focus.insert("b20".into(), (1, 1, 0));
    let (_, _, lf_f) = l1_from_jet(&focus);
    if lf_f != (-2, 1, 0) {
        panic!("generic focus L1 {lf_f:?}");
    }
    let mut ham = focus.clone();
    ham.insert("a20".into(), (2, 1, 0));
    ham.insert("a11".into(), (-6, 1, 0));
    ham.insert("a02".into(), (3, 1, 0));
    ham.insert("b20".into(), (3, 1, 0));
    ham.insert("b11".into(), (-4, 1, 0));
    ham.insert("b02".into(), (3, 1, 0));
    let (_, _, lf_h) = l1_from_jet(&ham);
    if lf_h != (0, 1, 0) {
        panic!("hamiltonian L1 {lf_h:?}");
    }

    // μ=0 Hamiltonian first integrals in the focal chart.
    let uv = names(&["u", "v"]);
    let uu = v(&uv, "u");
    let vv2 = v(&uv, "v");
    let h4p = vv2
        .pow(2)
        .scale(4)
        .add(&uu.pow(2).scale(4))
        .add(&uu.pow(3).scale(4))
        .add(&uu.pow(4));
    let pu = vv2.neg();
    let two_qp = uu.scale(2).add(&uu.pow(2).scale(3)).add(&uu.pow(3));
    // 2 dH4+ = 2 H_u P + H_v (2Q) = 0
    let two_dhp = h4p.dvar("u").mul(&pu).scale(2).add(&h4p.dvar("v").mul(&two_qp));
    require_zero(&two_dhp, "4H+ at mu=0");
    let h4m = vv2
        .pow(2)
        .scale(4)
        .add(&uu.pow(2).scale(4))
        .sub(&uu.pow(3).scale(4))
        .add(&uu.pow(4));
    let two_qm = uu.scale(2).sub(&uu.pow(2).scale(3)).add(&uu.pow(3));
    let two_dhm = h4m.dvar("u").mul(&pu).scale(2).add(&h4m.dvar("v").mul(&two_qm));
    require_zero(&two_dhm, "4H- at mu=0");
    let bad = vv2.pow(2).scale(4).add(&uu.pow(2).scale(4)).add(&uu.pow(3).scale(4));
    let two_bad = bad.dvar("u").mul(&pu).scale(2).add(&bad.dvar("v").mul(&two_qp));
    if two_bad.is_zero() {
        panic!("dropped-u^4 energy unexpectedly conserved");
    }

    // Poincaré V1, V2 over Q(√2) at integer μ.
    let mut samples: Vec<(i128, Rat)> = Vec::new();
    for mu_i in [-2i128, -1, 0, 1, 2] {
        for plus in [true, false] {
            let (v1, v2) = poincare_v1_v2(mu_i, plus);
            if v1 != expected_v1(mu_i) {
                panic!("V1 mu={mu_i} plus={plus} {v1:?}");
            }
            if v2 != expected_v2(mu_i) {
                panic!("V2 mu={mu_i} plus={plus} {v2:?}");
            }
            if plus {
                samples.push((mu_i, v2.as_sqrt2_coeff()));
            }
        }
    }
    if !expected_v1(0).is_zero() || !expected_v2(0).is_zero() {
        panic!("V1 or V2 at mu=0");
    }
    let (a, b) = interpolate_odd_cubic(&samples);
    // a = -18/96 = -3/16, b = -23/96
    if a != Rat::new(-3, 16) || b != Rat::new(-23, 96) {
        panic!("interpolated V2 coefficients a={a:?} b={b:?}");
    }
    for (mu_i, val) in &samples {
        let pred = a.mul(Rat::from_i(*mu_i)).add(b.mul(Rat::from_i(mu_i * mu_i * mu_i)));
        if pred != *val {
            panic!("interpolant misses mu={mu_i}");
        }
    }
    // Cleared: 96 a = -18, 96 b = -23, so V2 = √2 (a μ + b μ³)
    // = -√2 μ (18 + 23 μ²) / 96.
    if a.mul(Rat::from_i(96)) != Rat::from_i(-18) || b.mul(Rat::from_i(96)) != Rat::from_i(-23) {
        panic!("V2 not the claimed multiple of μ");
    }
    // Samples quoted on the dump.
    if expected_v2(1) != Alg::sqrt2().mul(Alg::from_rat(Rat::new(-41, 96))) {
        panic!("V2(1)");
    }
    if expected_v2(2) != Alg::sqrt2().mul(Alg::from_rat(Rat::new(-55, 24))) {
        panic!("V2(2)");
    }
    if expected_v2(-1) != Alg::sqrt2().mul(Alg::from_rat(Rat::new(41, 96))) {
        panic!("V2(-1)");
    }

    // lie_rot sanity: r² is in the kernel.
    let r2 = Hom {
        c: vec![
            Alg::from_rat(Rat::new(1, 2)),
            Alg::zero(),
            Alg::from_rat(Rat::new(1, 2)),
        ],
    };
    for coeff in lie_rot(&r2).c {
        if !coeff.is_zero() {
            panic!("lie_rot(r^2) is not zero");
        }
    }
}

fn dump_lines() -> String {
    let lines = [
        "imagined_H3_ge_14 DROP",
        "imagined_L2_zero_while_L1 DROP",
        "imagined_L2_extra_cycles DROP",
        "L1_replay KEEP",
        "L1_cubic_formula KEEP",
        "V2_3jet KEEP",
        "mu0_all_lyapunov KEEP",
        "hn_moved 0",
        "fourteen_from_L2 0",
        "L2_extra_cycles 0",
        "L2_zero_while_L1 0",
        "cycles_proved 0",
        "two_hopf_cycles 0",
        "degree 3",
        "weak_focus_order 1",
        "L2_first_nonzero 0",
        "L2_irrelevant_to_cyclicity 1",
        "trace_at_wells 0",
        "plus_jet b20=3/2 b11=-sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2",
        "minus_jet b20=-3/2 b11=sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2",
        "L1_formula_quad (a20+a02)*a11-(b20+b02)*b11-2*a20*b20+2*a02*b02",
        "L1_formula_cubic 3*a30+a12+b21+3*b03",
        "L1_E a02*a11 1",
        "L1_E a02*b02 2",
        "L1_E a11*a20 1",
        "L1_E a20*b20 -2",
        "L1_E b02*b11 -1",
        "L1_E b11*b20 -1",
        "L1_cubic a12 1",
        "L1_cubic a30 3",
        "L1_cubic b03 3",
        "L1_cubic b21 1",
        "L1_E_plus 3*sqrt(2)*mu/2",
        "L1_cubic_plus -sqrt(2)*mu/2",
        "L1_plus sqrt(2)*mu",
        "L1_E_minus 3*sqrt(2)*mu/2",
        "L1_cubic_minus -sqrt(2)*mu/2",
        "L1_minus sqrt(2)*mu",
        "V1_over_L1 1/8",
        "V1_plus sqrt(2)*mu/8",
        "V1_minus sqrt(2)*mu/8",
        "V2_plus -sqrt(2)*mu*(23*mu^2+18)/96",
        "V2_minus -sqrt(2)*mu*(23*mu^2+18)/96",
        "V1_mu0 0",
        "V2_mu0 0",
        "V2_sample_mu1 -41*sqrt(2)/96",
        "V2_sample_mu2 -55*sqrt(2)/24",
        "V2_sample_mu-1 41*sqrt(2)/96",
        "centers_at_mu0 1",
        "generic_focus_L1 -2",
        "hamiltonian_L1 0",
        "",
    ];
    lines.join("\n")
}

fn main() {
    let mut dump_path: Option<PathBuf> = None;
    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        if arg == "--dump" {
            dump_path = Some(PathBuf::from(args.next().expect("--dump needs a path")));
        } else {
            eprintln!("unknown argument {arg}");
            process::exit(2);
        }
    }

    check_all();
    let text = dump_lines();
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID ss-cubic-l2 replay");
}
