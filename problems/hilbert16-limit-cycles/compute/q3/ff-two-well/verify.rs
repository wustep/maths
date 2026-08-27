//! Independent replay of the two-well cubic Hamiltonian identities.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap. This
//! program expands the same rings with a BTreeMap and evaluates the
//! cleared dH/dt residuals on the integer box {-3,...,3}. A degree-4
//! polynomial in three variables that vanishes on that box is zero.
//! rustc only.
//!
//! Imagined 14 zeros of I(h) are not produced. Kept: classification,
//! dH/dt, I(0) = 4 mu / 15, L1 = sqrt(2) mu. Not a bound on H(n).

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process;

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

    fn subst(&self, mapping: &BTreeMap<String, Poly>) -> Self {
        let mut out = Self::zero(&self.vars);
        for (exp, coeff) in &self.terms {
            let mut mon = Self::constant(&self.vars, *coeff);
            for (name, power) in self.vars.iter().zip(exp.iter()) {
                if *power == 0 {
                    continue;
                }
                let factor = mapping
                    .get(name)
                    .cloned()
                    .unwrap_or_else(|| Self::var(&self.vars, name));
                mon = mon.mul(&factor.pow(*power as u32));
            }
            out = out.add(&mon);
        }
        out
    }

    fn eval(&self, values: &BTreeMap<String, i128>) -> i128 {
        let mut total = 0i128;
        for (exp, coeff) in &self.terms {
            let mut mon = *coeff;
            for (name, power) in self.vars.iter().zip(exp.iter()) {
                if *power > 0 {
                    let base = *values.get(name).expect("missing value");
                    mon *= pow_i128(base, *power);
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
        *self.terms.get(&exp).unwrap_or(&0)
    }

    fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    fn nterms(&self) -> usize {
        self.terms.len()
    }
}

fn pow_i128(base: i128, exp: u8) -> i128 {
    let mut out = 1i128;
    for _ in 0..exp {
        out *= base;
    }
    out
}

fn names(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| s.to_string()).collect()
}

fn v(vars: &[String], name: &str) -> Poly {
    Poly::var(vars, name)
}

fn c(vars: &[String], value: i128) -> Poly {
    Poly::constant(vars, value)
}

fn require_zero(poly: &Poly, label: &str) {
    if !poly.is_zero() {
        panic!("{label} is not the zero polynomial");
    }
}

fn gcd_i128(mut a: i128, mut b: i128) -> i128 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

fn reduce_frac(num: i128, den: i128) -> (i128, i128) {
    if num == 0 {
        return (0, 1);
    }
    let mut n = num;
    let mut d = den;
    if d < 0 {
        n = -n;
        d = -d;
    }
    let g = gcd_i128(n, d);
    (n / g, d / g)
}

/// (num, den, s_power)
type JetC = (i128, i128, u8);

fn add_jet(a: JetC, b: JetC) -> JetC {
    let (n1, d1, s1) = a;
    let (n2, d2, s2) = b;
    if n1 == 0 {
        return b;
    }
    if n2 == 0 {
        return a;
    }
    if s1 != s2 {
        panic!("cannot add distinct s-powers");
    }
    let (num, den) = reduce_frac(n1 * d2 + n2 * d1, d1 * d2);
    (num, den, s1)
}

fn mul_jet(a: JetC, b: JetC) -> JetC {
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
    let (num, den) = reduce_frac(num, den);
    (num, den, sp)
}

fn sc_jet(a: JetC, k: i128) -> JetC {
    let (n, d, s) = a;
    let (num, den) = reduce_frac(n * k, d);
    if num == 0 {
        (0, 1, 0)
    } else {
        (num, den, s)
    }
}

fn reduce_s(poly: &Poly) -> Poly {
    let s_idx = poly
        .vars
        .iter()
        .position(|v| v == "s")
        .expect("s missing");
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

fn box_zero_xy(diff: &Poly) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            let mut values = BTreeMap::new();
            values.insert("x".into(), x);
            values.insert("y".into(), y);
            if diff.eval(&values) != 0 {
                panic!("residual nonzero at ({x},{y})");
            }
        }
    }
}

fn box_zero_xym(diff: &Poly) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            for mu in -3i128..=3 {
                let mut values = BTreeMap::new();
                values.insert("x".into(), x);
                values.insert("y".into(), y);
                values.insert("mu".into(), mu);
                if diff.eval(&values) != 0 {
                    panic!("residual nonzero at ({x},{y},{mu})");
                }
            }
        }
    }
}

fn box_zero_xyms(diff: &Poly) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            for mu in -3i128..=3 {
                let mut values = BTreeMap::new();
                values.insert("X".into(), x);
                values.insert("Y".into(), y);
                values.insert("mu".into(), mu);
                if diff.eval(&values) != 0 {
                    panic!("translate residual nonzero at ({x},{y},{mu})");
                }
            }
        }
    }
}

struct Counts {
    h4_terms: usize,
    dh4_unperturbed_terms: usize,
    dh4_perturbed_diff_terms: usize,
    plus_translate_diff_terms: usize,
    minus_translate_diff_terms: usize,
}

fn l1_from_jet(jet: &BTreeMap<&str, JetC>) -> (JetC, JetC, JetC) {
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
    let mut lq = mul_jet(add_jet(a20, a02), a11);
    lq = add_jet(lq, sc_jet(mul_jet(add_jet(b20, b02), b11), -1));
    lq = add_jet(lq, sc_jet(mul_jet(a20, b20), -2));
    lq = add_jet(lq, sc_jet(mul_jet(a02, b02), 2));
    let lc = add_jet(add_jet(sc_jet(a30, 3), a12), add_jet(b21, sc_jet(b03, 3)));
    let lf = add_jet(lq, lc);
    (lq, lc, lf)
}

fn jet_from_n(n_poly: &Poly) -> BTreeMap<&'static str, JetC> {
    let raw = |powers: &[(&str, u8)]| n_poly.coeff(powers);
    let mut jets: BTreeMap<&str, JetC> = BTreeMap::new();
    jets.insert("a20", (0, 1, 0));
    jets.insert("a11", (0, 1, 0));
    jets.insert("a02", (0, 1, 0));
    jets.insert("a30", (0, 1, 0));
    jets.insert("a21", (0, 1, 0));
    jets.insert("a12", (0, 1, 0));
    jets.insert("a03", (0, 1, 0));
    let (n, d) = reduce_frac(-raw(&[("u", 2)]), 2);
    jets.insert("b20", (n, d, 0));
    let (n, d) = reduce_frac(-raw(&[("v", 2)]), 2);
    jets.insert("b02", (n, d, 0));
    let (n, d) = reduce_frac(-raw(&[("u", 3)]), 2);
    jets.insert("b30", (n, d, 0));
    let (n, d) = reduce_frac(-raw(&[("u", 1), ("v", 2)]), 2);
    jets.insert("b12", (n, d, 0));
    let (n, d) = reduce_frac(-raw(&[("v", 3)]), 2);
    jets.insert("b03", (n, d, 0));

    let b11_mu_s = -raw(&[("u", 1), ("v", 1), ("mu", 1), ("s", 1)]);
    if raw(&[("u", 1), ("v", 1), ("mu", 1)]) != 0
        || raw(&[("u", 1), ("v", 1), ("s", 1)]) != 0
        || raw(&[("u", 1), ("v", 1)]) != 0
    {
        panic!("unexpected b11 constant pieces");
    }
    let (n, d) = reduce_frac(b11_mu_s, 2);
    jets.insert("b11", (n, d, 1));

    let b21_mu_s = -raw(&[("u", 2), ("v", 1), ("mu", 1), ("s", 1)]);
    if raw(&[("u", 2), ("v", 1), ("mu", 1)]) != 0
        || raw(&[("u", 2), ("v", 1), ("s", 1)]) != 0
        || raw(&[("u", 2), ("v", 1)]) != 0
    {
        panic!("unexpected b21 constant pieces");
    }
    let (n, d) = reduce_frac(b21_mu_s, 2);
    jets.insert("b21", (n, d, 1));
    jets
}

fn check_all() -> Counts {
    let xy = names(&["x", "y"]);
    let x = v(&xy, "x");
    let y = v(&xy, "y");
    let p = y.clone();
    let q = x.sub(&x.pow(3));
    let h4 = y.pow(2).scale(2).add(&x.pow(4)).sub(&x.pow(2).scale(2));
    let dh4 = h4.dvar("x").mul(&p).add(&h4.dvar("y").mul(&q));
    require_zero(&dh4, "unperturbed dH4/dt");
    box_zero_xy(&dh4);

    let well = x.pow(2).sub(&c(&xy, 1)).pow(2);
    let potential_diff = well.sub(&c(&xy, 1)).sub(&x.pow(4).sub(&x.pow(2).scale(2)));
    require_zero(&potential_diff, "potential shift");

    let q_factored = x
        .mul(&c(&xy, 1).sub(&x))
        .mul(&c(&xy, 1).add(&x));
    require_zero(&q.sub(&q_factored), "Q factorization");

    let dp_dx = p.dvar("x");
    let dp_dy = p.dvar("y");
    let dq_dx = q.dvar("x");
    let dq_dy = q.dvar("y");
    let det = dp_dx.mul(&dq_dy).sub(&dp_dy.mul(&dq_dx));
    let det_claimed = x.pow(2).scale(3).sub(&c(&xy, 1));
    require_zero(&det.sub(&det_claimed), "Jacobian det");
    let div = dp_dx.add(&dq_dy);
    require_zero(&div, "divergence");

    let mut origin = BTreeMap::new();
    origin.insert("x".into(), 0);
    origin.insert("y".into(), 0);
    if p.eval(&origin) != 0 || q.eval(&origin) != 0 {
        panic!("(0,0) is not an equilibrium");
    }
    if h4.eval(&origin) != 0 {
        panic!("H4(0,0)");
    }
    if det.eval(&origin) != -1 {
        panic!("det(0,0)");
    }
    for xv in [1i128, -1] {
        let mut vals = BTreeMap::new();
        vals.insert("x".into(), xv);
        vals.insert("y".into(), 0);
        if p.eval(&vals) != 0 || q.eval(&vals) != 0 {
            panic!("({xv},0) is not an equilibrium");
        }
        if h4.eval(&vals) != -1 {
            panic!("H4({xv},0)");
        }
        if det.eval(&vals) != 2 {
            panic!("det({xv},0)");
        }
    }

    let xym = names(&["x", "y", "mu"]);
    let xp = v(&xym, "x");
    let yp = v(&xym, "y");
    let mu = v(&xym, "mu");
    let pp = yp.clone();
    let qp = xp
        .sub(&xp.pow(3))
        .add(&mu.mul(&c(&xym, 1).sub(&xp.pow(2))).mul(&yp));
    let h4p = yp.pow(2).scale(2).add(&xp.pow(4)).sub(&xp.pow(2).scale(2));
    let dh4p = h4p.dvar("x").mul(&pp).add(&h4p.dvar("y").mul(&qp));
    let claimed4 = mu.mul(&yp.pow(2)).mul(&c(&xym, 1).sub(&xp.pow(2))).scale(4);
    let dh4_diff = dh4p.sub(&claimed4);
    require_zero(&dh4_diff, "perturbed dH4/dt");
    box_zero_xym(&dh4_diff);

    let dqp_dx = qp.dvar("x");
    let dqp_dy = qp.dvar("y");
    let dpp_dx = pp.dvar("x");
    let dpp_dy = pp.dvar("y");
    let trace = dpp_dx.add(&dqp_dy);
    let trace_claimed = mu.mul(&c(&xym, 1).sub(&xp.pow(2)));
    require_zero(&trace.sub(&trace_claimed), "perturbed trace");
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
                if detp.eval(&vals) != -1 {
                    panic!("perturbed det(0,0)");
                }
                if trace.eval(&vals) != muv {
                    panic!("perturbed trace(0,0)");
                }
            } else {
                if detp.eval(&vals) != 2 {
                    panic!("perturbed det well");
                }
                if trace.eval(&vals) != 0 {
                    panic!("perturbed trace well");
                }
            }
        }
    }
    let mut sample = BTreeMap::new();
    sample.insert("x".into(), 0);
    sample.insert("y".into(), 1);
    sample.insert("mu".into(), 1);
    if dh4p.eval(&sample) != 4 {
        panic!("dH4 sample (0,1)");
    }
    sample.insert("x".into(), 2);
    if dh4p.eval(&sample) != -12 {
        panic!("dH4 sample (2,1)");
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
    let plus_diff = q_plus.sub(&claimed_plus);
    require_zero(&plus_diff, "+1 translation");
    box_zero_xyms(&plus_diff);

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
    let minus_diff = q_minus.sub(&claimed_minus);
    require_zero(&minus_diff, "-1 translation");
    box_zero_xyms(&minus_diff);

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
    if jet_p["b20"] != (3, 2, 0) || jet_p["b11"] != (-1, 1, 1) || jet_p["b30"] != (1, 2, 0) || jet_p["b21"] != (-1, 2, 1)
    {
        panic!("plus jet {:?}", jet_p);
    }
    if jet_m["b20"] != (-3, 2, 0) || jet_m["b11"] != (1, 1, 1) || jet_m["b30"] != (1, 2, 0) || jet_m["b21"] != (-1, 2, 1)
    {
        panic!("minus jet {:?}", jet_m);
    }
    let (lq_p, lc_p, lf_p) = l1_from_jet(&jet_p);
    let (lq_m, lc_m, lf_m) = l1_from_jet(&jet_m);
    if lq_p != (3, 2, 1) || lc_p != (-1, 2, 1) || lf_p != (1, 1, 1) {
        panic!("L1 plus {lq_p:?} {lc_p:?} {lf_p:?}");
    }
    if lq_m != (3, 2, 1) || lc_m != (-1, 2, 1) || lf_m != (1, 1, 1) {
        panic!("L1 minus {lq_m:?} {lc_m:?} {lf_m:?}");
    }

    let tv = names(&["t"]);
    let t = v(&tv, "t");
    let integrand = t.pow(4).scale(4).sub(&t.pow(2).scale(2));
    let anti15 = t.pow(5).scale(12).sub(&t.pow(3).scale(10));
    require_zero(&anti15.dvar("t").sub(&integrand.scale(15)), "15*antideriv");
    let mut t1 = BTreeMap::new();
    t1.insert("t".into(), 1);
    if anti15.eval(&t1) != 2 {
        panic!("15*antideriv(1)");
    }
    let xe = names(&["x"]);
    let xe_v = v(&xe, "x");
    let one_minus = c(&xe, 1).sub(&xe_v.pow(2));
    let rad = xe_v.pow(2).scale(2).sub(&xe_v.pow(4));
    let mut map = BTreeMap::new();
    map.insert("x".into(), xe_v.neg());
    require_zero(&one_minus.subst(&map).sub(&one_minus), "1-x^2 even");
    require_zero(&rad.subst(&map).sub(&rad), "radicand even");
    if 4 * 3 - 2 * 5 != 2 || 5 * 3 != 15 {
        panic!("4/5 - 2/3");
    }

    let bad_h = y.pow(2).scale(2).sub(&x.pow(2).scale(2));
    let bad_dh = bad_h.dvar("x").mul(&p).add(&bad_h.dvar("y").mul(&q));
    if bad_dh.is_zero() {
        panic!("dropped-x^4 energy unexpectedly conserved");
    }

    Counts {
        h4_terms: h4.nterms(),
        dh4_unperturbed_terms: dh4.nterms(),
        dh4_perturbed_diff_terms: dh4_diff.nterms(),
        plus_translate_diff_terms: plus_diff.nterms(),
        minus_translate_diff_terms: minus_diff.nterms(),
    }
}

fn dump_lines(counts: &Counts) -> String {
    let mut lines = Vec::new();
    lines.push("imagined_fourteen_zeros DROP".into());
    lines.push("H3_ge_14 DROP".into());
    lines.push("unperturbed_classification KEEP".into());
    lines.push("dHdt_identities KEEP".into());
    lines.push("I_h_formula KEEP".into());
    lines.push("I0_figure_eight KEEP".into());
    lines.push("L1_both_wells KEEP".into());
    lines.push("hn_moved 0".into());
    lines.push("fourteen_zeros_produced 0".into());
    lines.push("regular_I_zeros_exhibited 0".into());
    lines.push("cycles_proved 0".into());
    lines.push("degree 3".into());
    lines.push("eq 0 0 kind=saddle det=-1 trace=0 H=0".into());
    lines.push("eq 1 0 kind=center det=2 trace=0 H=-1/4".into());
    lines.push("eq -1 0 kind=center det=2 trace=0 H=-1/4".into());
    lines.push(format!("H4_terms {}", counts.h4_terms));
    lines.push(format!(
        "dH4_unperturbed_terms {}",
        counts.dh4_unperturbed_terms
    ));
    lines.push(format!(
        "dH4_perturbed_diff_terms {}",
        counts.dh4_perturbed_diff_terms
    ));
    lines.push("div_unperturbed 0".into());
    lines.push("perturbed_eq 0 0 kind=saddle det=-1 trace=mu".into());
    lines.push("perturbed_eq 1 0 kind=center det=2 trace=0".into());
    lines.push("perturbed_eq -1 0 kind=center det=2 trace=0".into());
    lines.push("saddle_stays_saddle 1".into());
    lines.push("trace_at_wells 0".into());
    lines.push(format!(
        "plus_translate_diff_terms {}",
        counts.plus_translate_diff_terms
    ));
    lines.push(format!(
        "minus_translate_diff_terms {}",
        counts.minus_translate_diff_terms
    ));
    lines.push("plus_jet b20=3/2 b11=-sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2".into());
    lines.push("minus_jet b20=-3/2 b11=sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2".into());
    lines.push(
        "L1_formula_quad (a20+a02)*a11-(b20+b02)*b11-2*a20*b20+2*a02*b02".into(),
    );
    lines.push("L1_formula_cubic 3*a30+a12+b21+3*b03".into());
    lines.push("L1_quad_plus 3*sqrt(2)*mu/2".into());
    lines.push("L1_cubic_plus -sqrt(2)*mu/2".into());
    lines.push("L1_plus sqrt(2)*mu".into());
    lines.push("L1_quad_minus 3*sqrt(2)*mu/2".into());
    lines.push("L1_cubic_minus -sqrt(2)*mu/2".into());
    lines.push("L1_minus sqrt(2)*mu".into());
    lines.push("L1_squared_coeff 2".into());
    lines.push("V1_plus sqrt(2)*mu/8".into());
    lines.push("weak_focus_order 1".into());
    lines.push("I0_antideriv_at_1 2/15".into());
    lines.push("I0_J 4/15".into());
    lines.push("I0_right 4/15*mu".into());
    lines.push("I0_left 4/15*mu".into());
    lines.push("I_at_well_bottom 0".into());
    lines.push("I_not_identically_zero 1".into());
    lines.push("potential_shift 1/4".into());
    lines.push(String::new());
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

    let counts = check_all();
    let text = dump_lines(&counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID ff-two-well replay");
}
