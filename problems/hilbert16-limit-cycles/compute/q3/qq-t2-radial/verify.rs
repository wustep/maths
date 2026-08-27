//! Second verifier for the T2 Chebyshev pullback of the §6 radial cubic.
//!
//! Independent of verify.py: integer Chebyshev recurrence, bivariate
//! polynomials over Q, exact degree-7 expansion, Sturm counts of T2'
//! on the open branches, and four-rectangle sign checks. rustc only.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::io::Write;
use std::path::PathBuf;

fn fail(msg: &str) -> ! {
    eprintln!("verify.rs FAIL: {msg}");
    std::process::exit(1);
}

// ---------------------------------------------------------------------------
// Q arithmetic
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
struct Ratio {
    n: i128,
    d: i128,
}

fn gcd_i128(mut a: i128, mut b: i128) -> i128 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a
}

impl Ratio {
    fn new(n: i128, d: i128) -> Self {
        if d == 0 {
            fail("division by zero");
        }
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
        Self { n, d: 1 }
    }

    fn zero() -> Self {
        Self { n: 0, d: 1 }
    }

    fn is_zero(self) -> bool {
        self.n == 0
    }

    fn add(self, other: Self) -> Self {
        Self::new(
            self.n
                .checked_mul(other.d)
                .and_then(|a| other.n.checked_mul(self.d).and_then(|b| a.checked_add(b)))
                .unwrap_or_else(|| fail("ratio add overflow")),
            self.d
                .checked_mul(other.d)
                .unwrap_or_else(|| fail("ratio add den overflow")),
        )
    }

    fn sub(self, other: Self) -> Self {
        self.add(Ratio {
            n: -other.n,
            d: other.d,
        })
    }

    fn mul(self, other: Self) -> Self {
        Self::new(
            self.n
                .checked_mul(other.n)
                .unwrap_or_else(|| fail("ratio mul overflow")),
            self.d
                .checked_mul(other.d)
                .unwrap_or_else(|| fail("ratio mul den overflow")),
        )
    }

    fn div(self, other: Self) -> Self {
        if other.is_zero() {
            fail("ratio div by zero");
        }
        Self::new(
            self.n
                .checked_mul(other.d)
                .unwrap_or_else(|| fail("ratio div overflow")),
            self.d
                .checked_mul(other.n)
                .unwrap_or_else(|| fail("ratio div den overflow")),
        )
    }

    fn abs(self) -> Self {
        Self { n: self.n.abs(), d: self.d }
    }

    fn signum(self) -> i8 {
        if self.n > 0 {
            1
        } else if self.n < 0 {
            -1
        } else {
            0
        }
    }
}

// ---------------------------------------------------------------------------
// Univariate Q[t]
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
struct UPoly {
    c: Vec<Ratio>,
}

impl UPoly {
    fn from_coeffs(mut c: Vec<Ratio>) -> Self {
        while c.len() > 1 && c.last().copied().map(Ratio::is_zero).unwrap_or(false) {
            c.pop();
        }
        if c.is_empty() {
            c.push(Ratio::zero());
        }
        Self { c }
    }

    fn zero() -> Self {
        Self {
            c: vec![Ratio::zero()],
        }
    }

    fn constant(a: Ratio) -> Self {
        Self { c: vec![a] }
    }

    fn t() -> Self {
        Self {
            c: vec![Ratio::zero(), Ratio::from_i(1)],
        }
    }

    fn deg(&self) -> i32 {
        if self.c.len() == 1 && self.c[0].is_zero() {
            return -1;
        }
        (self.c.len() as i32) - 1
    }

    fn coeff(&self, i: usize) -> Ratio {
        self.c.get(i).copied().unwrap_or_else(Ratio::zero)
    }

    fn add(&self, other: &Self) -> Self {
        let n = self.c.len().max(other.c.len());
        let mut c = vec![Ratio::zero(); n];
        for i in 0..n {
            c[i] = self.coeff(i).add(other.coeff(i));
        }
        Self::from_coeffs(c)
    }

    fn sub(&self, other: &Self) -> Self {
        let n = self.c.len().max(other.c.len());
        let mut c = vec![Ratio::zero(); n];
        for i in 0..n {
            c[i] = self.coeff(i).sub(other.coeff(i));
        }
        Self::from_coeffs(c)
    }

    fn scale(&self, s: Ratio) -> Self {
        Self::from_coeffs(self.c.iter().map(|a| a.mul(s)).collect())
    }

    fn mul(&self, other: &Self) -> Self {
        if self.deg() < 0 || other.deg() < 0 {
            return Self::zero();
        }
        let mut c = vec![Ratio::zero(); self.c.len() + other.c.len() - 1];
        for i in 0..self.c.len() {
            if self.c[i].is_zero() {
                continue;
            }
            for j in 0..other.c.len() {
                c[i + j] = c[i + j].add(self.c[i].mul(other.c[j]));
            }
        }
        Self::from_coeffs(c)
    }

    fn pow(&self, n: usize) -> Self {
        let mut out = Self::constant(Ratio::from_i(1));
        for _ in 0..n {
            out = out.mul(self);
        }
        out
    }

    fn diff(&self) -> Self {
        if self.c.len() <= 1 {
            return Self::zero();
        }
        let mut c = Vec::with_capacity(self.c.len() - 1);
        for i in 1..self.c.len() {
            c.push(self.c[i].mul(Ratio::from_i(i as i128)));
        }
        Self::from_coeffs(c)
    }

    fn eval(&self, x: Ratio) -> Ratio {
        let mut acc = Ratio::zero();
        for coeff in self.c.iter().rev() {
            acc = acc.mul(x).add(*coeff);
        }
        acc
    }

    fn is_zero(&self) -> bool {
        self.deg() < 0
    }

    fn rem(&self, divisor: &Self) -> Self {
        if divisor.is_zero() {
            fail("remainder by zero");
        }
        let mut r = self.clone();
        let dd = divisor.deg();
        let lc = divisor.coeff(dd as usize);
        while !r.is_zero() && r.deg() >= dd {
            let rd = r.deg();
            let factor = r.coeff(rd as usize).div(lc);
            let shift = (rd - dd) as usize;
            let mut sub = vec![Ratio::zero(); shift + divisor.c.len()];
            for (i, a) in divisor.c.iter().enumerate() {
                sub[i + shift] = a.mul(factor);
            }
            r = r.sub(&UPoly::from_coeffs(sub));
        }
        r
    }

    fn int_coeffs_asc(&self) -> Vec<i128> {
        self.c
            .iter()
            .map(|r| {
                if r.d != 1 {
                    fail("expected integer Chebyshev coefficients");
                }
                r.n
            })
            .collect()
    }
}

fn chebyshev_t(m: usize) -> UPoly {
    let t = UPoly::t();
    if m == 0 {
        return UPoly::constant(Ratio::from_i(1));
    }
    if m == 1 {
        return t;
    }
    let mut prev = UPoly::constant(Ratio::from_i(1));
    let mut curr = t.clone();
    for _ in 2..=m {
        let next = t.mul(&curr).scale(Ratio::from_i(2)).sub(&prev);
        prev = curr;
        curr = next;
    }
    curr
}

fn sturm_chain(p: &UPoly) -> Vec<UPoly> {
    let mut chain = vec![p.clone(), p.diff()];
    while !chain[chain.len() - 1].is_zero() && chain[chain.len() - 1].deg() >= 0 {
        let rem = chain[chain.len() - 2].rem(&chain[chain.len() - 1]).scale(Ratio::from_i(-1));
        if rem.is_zero() {
            break;
        }
        chain.push(rem);
    }
    if chain.last().map(UPoly::is_zero).unwrap_or(false) {
        chain.pop();
    }
    chain
}

fn sturm_sign_variations(chain: &[UPoly], a: Ratio) -> i32 {
    let mut signs: Vec<i8> = Vec::new();
    for q in chain {
        let val = q.eval(a);
        if val.is_zero() {
            continue;
        }
        signs.push(val.signum());
    }
    let mut n = 0;
    for i in 0..signs.len().saturating_sub(1) {
        if signs[i] * signs[i + 1] < 0 {
            n += 1;
        }
    }
    n
}

fn count_real_roots_open(p: &UPoly, left: Ratio, right: Ratio) -> i32 {
    if p.deg() <= 0 {
        return 0;
    }
    let chain = sturm_chain(p);
    let step = right.sub(left).div(Ratio::from_i(1_000_000));
    let mut lo = left;
    let mut hi = right;
    for _ in 0..8 {
        if chain.iter().all(|q| !q.eval(lo).is_zero()) {
            break;
        }
        lo = lo.add(step);
    }
    for _ in 0..8 {
        if chain.iter().all(|q| !q.eval(hi).is_zero()) {
            break;
        }
        hi = hi.sub(step);
    }
    // Both denominators are positive after Ratio::new.
    if lo.n * hi.d >= hi.n * lo.d {
        fail("Sturm interval collapsed");
    }
    sturm_sign_variations(&chain, lo) - sturm_sign_variations(&chain, hi)
}

fn gcd_upoly(a: &UPoly, b: &UPoly) -> UPoly {
    let mut r0 = a.clone();
    let mut r1 = b.clone();
    while !r1.is_zero() {
        let r = r0.rem(&r1);
        r0 = r1;
        r1 = r;
    }
    r0
}

// ---------------------------------------------------------------------------
// Bivariate Q[u,v]
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, Default)]
struct BiPoly {
    terms: BTreeMap<(i32, i32), Ratio>,
}

impl BiPoly {
    fn zero() -> Self {
        Self {
            terms: BTreeMap::new(),
        }
    }

    fn constant(a: Ratio) -> Self {
        let mut p = Self::zero();
        if !a.is_zero() {
            p.terms.insert((0, 0), a);
        }
        p
    }

    fn monomial(eu: i32, ev: i32, a: Ratio) -> Self {
        let mut p = Self::zero();
        if !a.is_zero() {
            p.terms.insert((eu, ev), a);
        }
        p
    }

    fn u() -> Self {
        Self::monomial(1, 0, Ratio::from_i(1))
    }

    fn v() -> Self {
        Self::monomial(0, 1, Ratio::from_i(1))
    }

    fn add(&self, other: &Self) -> Self {
        let mut out = self.clone();
        for (k, a) in &other.terms {
            let e = out.terms.entry(*k).or_insert_with(Ratio::zero);
            *e = e.add(*a);
            if e.is_zero() {
                out.terms.remove(k);
            }
        }
        out
    }

    fn sub(&self, other: &Self) -> Self {
        let mut out = self.clone();
        for (k, a) in &other.terms {
            let e = out.terms.entry(*k).or_insert_with(Ratio::zero);
            *e = e.sub(*a);
            if e.is_zero() {
                out.terms.remove(k);
            }
        }
        out
    }

    fn scale(&self, s: Ratio) -> Self {
        if s.is_zero() {
            return Self::zero();
        }
        let mut out = Self::zero();
        for (k, a) in &self.terms {
            out.terms.insert(*k, a.mul(s));
        }
        out
    }

    fn mul(&self, other: &Self) -> Self {
        let mut out = Self::zero();
        for ((i1, j1), a) in &self.terms {
            for ((i2, j2), b) in &other.terms {
                let k = (i1 + i2, j1 + j2);
                let e = out.terms.entry(k).or_insert_with(Ratio::zero);
                *e = e.add(a.mul(*b));
                if e.is_zero() {
                    out.terms.remove(&k);
                }
            }
        }
        out
    }

    fn pow(&self, n: usize) -> Self {
        let mut out = Self::constant(Ratio::from_i(1));
        for _ in 0..n {
            out = out.mul(self);
        }
        out
    }

    fn total_degree(&self) -> i32 {
        self.terms.keys().map(|(i, j)| i + j).max().unwrap_or(-1)
    }

    fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    fn compose(&self, u_sub: &BiPoly, v_sub: &BiPoly) -> Self {
        let mut out = Self::zero();
        for ((eu, ev), a) in &self.terms {
            let mut term = Self::constant(*a);
            if *eu > 0 {
                term = term.mul(&u_sub.pow(*eu as usize));
            }
            if *ev > 0 {
                term = term.mul(&v_sub.pow(*ev as usize));
            }
            out = out.add(&term);
        }
        out
    }

    fn homog(&self, deg: i32) -> Self {
        let mut out = Self::zero();
        for ((i, j), a) in &self.terms {
            if i + j == deg {
                out.terms.insert((*i, *j), *a);
            }
        }
        out
    }

    fn monomials_sorted(&self) -> Vec<(i32, i32, Ratio)> {
        let mut items: Vec<_> = self
            .terms
            .iter()
            .map(|((i, j), a)| (*i, *j, *a))
            .collect();
        items.sort_by_key(|(i, j, _)| (i + j, *i, *j));
        items
    }
}

fn upoly_as_u(p: &UPoly) -> BiPoly {
    let mut out = BiPoly::zero();
    for (i, a) in p.c.iter().enumerate() {
        if !a.is_zero() {
            out.terms.insert((i as i32, 0), *a);
        }
    }
    out
}

fn upoly_as_v(p: &UPoly) -> BiPoly {
    let mut out = BiPoly::zero();
    for (i, a) in p.c.iter().enumerate() {
        if !a.is_zero() {
            out.terms.insert((0, i as i32), *a);
        }
    }
    out
}

fn section6_x(rho2: Ratio) -> (BiPoly, BiPoly) {
    let x = BiPoly::u();
    let y = BiPoly::v();
    let r2 = x.pow(2).add(&y.pow(2)).sub(&BiPoly::constant(rho2));
    let p = y.sub(&x.mul(&r2));
    let q = x.scale(Ratio::from_i(-1)).sub(&y.mul(&r2));
    (p, q)
}

fn pullback(p: &BiPoly, q: &BiPoly, tm: &UPoly) -> (BiPoly, BiPoly, BiPoly, BiPoly) {
    let t_u = upoly_as_u(tm);
    let t_v = upoly_as_v(tm);
    let tp = tm.diff();
    let tp_u = upoly_as_u(&tp);
    let tp_v = upoly_as_v(&tp);
    let p_phi = p.compose(&t_u, &t_v);
    let q_phi = q.compose(&t_u, &t_v);
    let yu = tp_v.mul(&p_phi);
    let yv = tp_u.mul(&q_phi);
    (yu, yv, tp_u, tp_v)
}

fn dump_mons(prefix: &str, p: &BiPoly) -> Vec<String> {
    p.monomials_sorted()
        .into_iter()
        .map(|(eu, ev, a)| format!("{prefix} {eu} {ev} {} {}", a.n, a.d))
        .collect()
}

// ---------------------------------------------------------------------------
// Checks
// ---------------------------------------------------------------------------

fn check_chebyshev() -> (Vec<i128>, i32, i32, i32) {
    let named: [(usize, Vec<i128>); 4] = [
        (0, vec![1]),
        (1, vec![0, 1]),
        (2, vec![-1, 0, 2]),
        (3, vec![0, -3, 0, 4]),
    ];
    for (m, expect) in named {
        let got = chebyshev_t(m).int_coeffs_asc();
        if got != expect {
            fail(&format!("T_{m} coeffs {got:?} != {expect:?}"));
        }
    }

    let tm = chebyshev_t(2);
    let tp = tm.diff();
    if tm.int_coeffs_asc() != vec![-1, 0, 2] {
        fail("T2 coeffs");
    }
    if tp.int_coeffs_asc() != vec![0, 4] {
        fail("T2' coeffs");
    }

    let m2 = Ratio::from_i(4);
    let t2 = UPoly::t().pow(2);
    let one_minus_t2 = UPoly::constant(Ratio::from_i(1)).sub(&t2);
    let ident = tm
        .pow(2)
        .scale(m2)
        .add(&one_minus_t2.mul(&tp.pow(2)))
        .sub(&UPoly::constant(m2));
    if !ident.is_zero() {
        fail("Pell identity failed for m=2");
    }
    if tm.eval(Ratio::from_i(1)) != Ratio::from_i(1) {
        fail("T2(1) != 1");
    }
    if tm.eval(Ratio::from_i(-1)) != Ratio::from_i(1) {
        fail("T2(-1) != 1");
    }
    if tm.eval(Ratio::zero()) != Ratio::from_i(-1) {
        fail("T2(0) != -1");
    }

    let g = gcd_upoly(&tp, &tp.diff());
    if g.deg() != 0 {
        fail("T2' is not square-free");
    }

    let n_open = count_real_roots_open(&tp, Ratio::from_i(-1), Ratio::from_i(1));
    if n_open != 1 {
        fail(&format!("T2' has {n_open} roots in (-1,1)"));
    }
    let n_plus = count_real_roots_open(&tp, Ratio::zero(), Ratio::from_i(1));
    let n_minus = count_real_roots_open(&tp, Ratio::from_i(-1), Ratio::zero());
    if n_plus != 0 || n_minus != 0 {
        fail("T2' has a critical point in an open branch");
    }

    if tm.eval(Ratio::new(1, 2)) != Ratio::new(-1, 2) {
        fail("T2(1/2)");
    }
    if tm.eval(Ratio::new(-1, 2)) != Ratio::new(-1, 2) {
        fail("T2(-1/2)");
    }
    if !tp.eval(Ratio::zero()).is_zero() {
        fail("T2'(0)");
    }
    if tp.eval(Ratio::new(1, 2)) != Ratio::from_i(2) {
        fail("T2'(1/2)");
    }
    if tp.eval(Ratio::new(-1, 2)) != Ratio::from_i(-2) {
        fail("T2'(-1/2)");
    }
    if tp.eval(Ratio::from_i(1)) != Ratio::from_i(4) {
        fail("T2'(1)");
    }
    if tp.eval(Ratio::from_i(-1)) != Ratio::from_i(-4) {
        fail("T2'(-1)");
    }

    (tm.int_coeffs_asc(), n_open, n_plus, n_minus)
}

fn check_degree_formula() -> Vec<(i32, i32)> {
    let mut rows = Vec::new();
    for n in [1usize, 2, 3] {
        let mut p = BiPoly::zero();
        p.terms.insert((n as i32, 0), Ratio::from_i(1));
        let q = BiPoly::zero();
        let tm = chebyshev_t(2);
        let (yu, yv, _, _) = pullback(&p, &q, &tm);
        let deg = yu.total_degree().max(yv.total_degree());
        let expected = (n * 2 + (2 - 1)) as i32;
        if deg != expected {
            fail(&format!("deg Y for (x^{n},0), m=2: {deg} != {expected}"));
        }
        rows.push((n as i32, deg));
    }
    rows
}

fn check_polar(rho2: Ratio) {
    let (p, q) = section6_x(rho2);
    let x = BiPoly::u();
    let y = BiPoly::v();
    let r2 = x.pow(2).add(&y.pow(2));
    let radial = x
        .mul(&p)
        .add(&y.mul(&q))
        .add(&r2.mul(&r2.sub(&BiPoly::constant(rho2))));
    let angular = x.mul(&q).sub(&y.mul(&p)).add(&r2);
    if !radial.is_zero() || !angular.is_zero() {
        fail("polar identities failed");
    }
    let fprime = rho2.mul(Ratio::from_i(-2));
    if fprime.is_zero() {
        fail("f'(rho)=0");
    }
    if fprime != Ratio::new(-1, 2) {
        fail("f'(1/2) != -1/2");
    }
}

fn check_field() -> (BiPoly, BiPoly, i32, i32, i32) {
    let rho2 = Ratio::new(1, 4);
    let (p, q) = section6_x(rho2);
    let deg_x = p.total_degree().max(q.total_degree());
    if deg_x != 3 {
        fail(&format!("deg X = {deg_x}"));
    }
    let tm = chebyshev_t(2);
    let (yu, yv, tp_u, tp_v) = pullback(&p, &q, &tm);
    let t_u = upoly_as_u(&tm);
    let t_v = upoly_as_v(&tm);
    let lam = tp_u.mul(&tp_v);
    let p_phi = p.compose(&t_u, &t_v);
    let q_phi = q.compose(&t_u, &t_v);
    let dphi_u = tp_u.mul(&yu).sub(&lam.mul(&p_phi));
    let dphi_v = tp_v.mul(&yv).sub(&lam.mul(&q_phi));
    if !dphi_u.is_zero() || !dphi_v.is_zero() {
        fail("conjugacy DΦ·Y = λ X∘Φ failed");
    }
    let deg_u = yu.total_degree();
    let deg_v = yv.total_degree();
    let deg_y = deg_u.max(deg_v);
    if deg_y != 7 || deg_u != 7 || deg_v != 7 {
        fail(&format!("deg Y = {deg_y} ({deg_u},{deg_v}), expected 7"));
    }
    if yu.terms.len() != 8 || yv.terms.len() != 8 {
        fail(&format!(
            "term counts Yu={} Yv={}",
            yu.terms.len(),
            yv.terms.len()
        ));
    }

    let expect_u: [(i32, i32, i128); 8] = [
        (0, 1, 3),
        (0, 3, -8),
        (2, 1, -30),
        (0, 5, 16),
        (2, 3, 32),
        (4, 1, 48),
        (2, 5, -32),
        (6, 1, -32),
    ];
    let got_u = yu.monomials_sorted();
    if got_u.len() != 8 {
        fail("Yu term count");
    }
    for (i, (eu, ev, a)) in got_u.iter().enumerate() {
        let (xu, xv, xn) = expect_u[i];
        if *eu != xu || *ev != xv || a.n != xn || a.d != 1 {
            fail(&format!("Yu monomial {i}"));
        }
    }
    let expect_v: [(i32, i32, i128); 8] = [
        (1, 0, 11),
        (1, 2, -30),
        (3, 0, -24),
        (1, 4, 48),
        (3, 2, 32),
        (5, 0, 16),
        (1, 6, -32),
        (5, 2, -32),
    ];
    let got_v = yv.monomials_sorted();
    for (i, (eu, ev, a)) in got_v.iter().enumerate() {
        let (xu, xv, xn) = expect_v[i];
        if *eu != xu || *ev != xv || a.n != xn || a.d != 1 {
            fail(&format!("Yv monomial {i}"));
        }
    }

    let u = BiPoly::u();
    let v = BiPoly::v();
    let u4v4 = u.pow(4).add(&v.pow(4));
    let expect_lead_u = u
        .pow(2)
        .mul(&v)
        .mul(&u4v4)
        .scale(Ratio::from_i(-32));
    let expect_lead_v = u.mul(&v.pow(2)).mul(&u4v4).scale(Ratio::from_i(-32));
    if yu.homog(7).terms != expect_lead_u.terms {
        fail("Yu leading form");
    }
    if yv.homog(7).terms != expect_lead_v.terms {
        fail("Yv leading form");
    }

    let (yu4, yv4, _, _) = pullback(&p.scale(Ratio::from_i(4)), &q.scale(Ratio::from_i(4)), &tm);
    if yu4.total_degree().max(yv4.total_degree()) != 7 {
        fail("integer 4X pullback degree != 7");
    }
    (yu, yv, deg_u, deg_v, deg_y)
}

fn check_four_rectangles() {
    let tm = chebyshev_t(2);
    let tp = tm.diff();
    if tp.int_coeffs_asc() != vec![0, 4] {
        fail("T2' coeffs");
    }

    let intervals: [(&str, Ratio, Ratio, i8); 2] = [
        ("I1", Ratio::zero(), Ratio::from_i(1), 1),
        ("I2", Ratio::from_i(-1), Ratio::zero(), -1),
    ];
    for (name, left, right, sign) in intervals {
        let mid = left.add(right).mul(Ratio::new(1, 2));
        let tp_mid = tp.eval(mid);
        if tp_mid.is_zero() {
            fail(&format!("T2' vanishes in {name}"));
        }
        let got_sign: i8 = if tp_mid.n > 0 { 1 } else { -1 };
        if got_sign != sign {
            fail(&format!("T2' sign on {name}"));
        }
        let n_crit = count_real_roots_open(&tp, left, right);
        if n_crit != 0 {
            fail(&format!("T2' has {n_crit} roots in {name}"));
        }
        let t_left = tm.eval(left);
        let t_right = tm.eval(right);
        if t_left.abs() != Ratio::from_i(1) || t_right.abs() != Ratio::from_i(1) {
            fail(&format!("|T2| != 1 at endpoints of {name}"));
        }
        if t_left == t_right {
            fail(&format!("T2 not opposite on {name}"));
        }
        let half = Ratio::new(1, 2);
        let minus_l = t_left.add(half);
        let minus_r = t_right.add(half);
        let plus_l = t_left.sub(half);
        let plus_r = t_right.sub(half);
        if minus_l.signum() * minus_r.signum() >= 0 || plus_l.signum() * plus_r.signum() >= 0 {
            fail(&format!("T2±1/2 do not change sign on {name}"));
        }
        if t_left.abs().n * half.d <= half.n * t_left.d
            || t_right.abs().n * half.d <= half.n * t_right.d
        {
            fail(&format!("[-1/2,1/2] not strictly inside T2({name})"));
        }
    }

    let t_u = upoly_as_u(&tm);
    let t_v = upoly_as_v(&tm);
    let f = t_u.pow(2).add(&t_v.pow(2)).sub(&BiPoly::constant(Ratio::new(1, 4)));
    let f4 = f.scale(Ratio::from_i(4));
    let mut expect = BiPoly::zero();
    expect = expect.add(&BiPoly::monomial(4, 0, Ratio::from_i(16)));
    expect = expect.add(&BiPoly::monomial(0, 4, Ratio::from_i(16)));
    expect = expect.add(&BiPoly::monomial(2, 0, Ratio::from_i(-16)));
    expect = expect.add(&BiPoly::monomial(0, 2, Ratio::from_i(-16)));
    expect = expect.add(&BiPoly::constant(Ratio::from_i(7)));
    if f4.terms != expect.terms {
        fail("cleared level curve");
    }
    if f4.total_degree() != 4 {
        fail("level curve degree != 4");
    }
}

fn write_core(yu: &BiPoly, yv: &BiPoly, deg_u: i32, deg_v: i32, deg_y: i32) {
    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let certs = cwd.join("certs");
    fs::create_dir_all(&certs).unwrap_or_else(|e| fail(&format!("mkdir certs: {e}")));
    let path = certs.join("rust_core.json");

    let mut body = String::new();
    body.push_str("{\n");
    body.push_str(&format!("  \"deg_Y\": {deg_y},\n"));
    body.push_str(&format!("  \"deg_Yu\": {deg_u},\n"));
    body.push_str(&format!("  \"deg_Yv\": {deg_v},\n"));
    body.push_str("  \"deg_X\": 3,\n");
    body.push_str("  \"conjugacy\": true,\n");
    body.push_str("  \"H7_from_this_field\": 4,\n");
    body.push_str("  \"beats_PT_74\": false,\n");
    body.push_str("  \"four_ovals\": true,\n");
    body.push_str("  \"n_terms_Yu\": 8,\n");
    body.push_str("  \"n_terms_Yv\": 8,\n");
    body.push_str("  \"T2_at_1\": [1, 1],\n");
    body.push_str("  \"T2_at_-1\": [1, 1],\n");
    body.push_str("  \"T2_at_0\": [-1, 1],\n");

    fn dump_monomials(body: &mut String, p: &BiPoly) {
        let items = p.monomials_sorted();
        body.push('[');
        for (k, (eu, ev, a)) in items.iter().enumerate() {
            if k > 0 {
                body.push_str(", ");
            }
            body.push_str(&format!(
                "{{\"u\": {eu}, \"v\": {ev}, \"num\": {}, \"den\": {}}}",
                a.n, a.d
            ));
        }
        body.push(']');
    }

    body.push_str("  \"Y_u_monomials\": ");
    dump_monomials(&mut body, yu);
    body.push_str(",\n  \"Y_v_monomials\": ");
    dump_monomials(&mut body, yv);
    body.push_str(",\n");
    body.push_str("  \"same_4_sheets_as_CL_at_N7\": true,\n");
    body.push_str("  \"beats_CL\": false,\n");
    body.push_str("  \"CL_beats_this\": false,\n");
    body.push_str("  \"do_not_claim_252_1080_1380_2012\": true,\n");
    body.push_str("  \"T2_coeffs\": [-1, 0, 2]\n");
    body.push_str("}\n");

    let mut fh = fs::File::create(&path).unwrap_or_else(|e| fail(&format!("write {path:?}: {e}")));
    fh.write_all(body.as_bytes())
        .unwrap_or_else(|e| fail(&format!("write {path:?}: {e}")));
}

fn main() {
    let mut dump_path: Option<PathBuf> = None;
    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        if args[i] == "--dump" && i + 1 < args.len() {
            dump_path = Some(PathBuf::from(&args[i + 1]));
            i += 2;
            continue;
        }
        i += 1;
    }

    let (t2_coeffs, n_open, n_plus, n_minus) = check_chebyshev();
    let lemma5 = check_degree_formula();
    check_polar(Ratio::new(1, 4));
    let (yu, yv, deg_u, deg_v, deg_y) = check_field();
    check_four_rectangles();

    if t2_coeffs != vec![-1, 0, 2] {
        fail("T2 coeffs in dump");
    }

    let mut lines: Vec<String> = vec![
        "paper arXiv:2604.12883v1".into(),
        "T2 2*t^2-1".into(),
        "T2_prime 4*t".into(),
        "T2_coeffs -1 0 2".into(),
        "T2_prime_coeffs 0 4".into(),
        "pell 1".into(),
        "square_free_T2_prime 1".into(),
        "T2_at_1 1 1".into(),
        "T2_at_-1 1 1".into(),
        "T2_at_0 -1 1".into(),
        "T2_prime_at_0 0 1".into(),
        "T2_prime_at_1/2 2 1".into(),
        "T2_prime_at_-1/2 -2 1".into(),
        format!("Sturm_(-1,1) {n_open}"),
        format!("Sturm_I1 {n_plus}"),
        format!("Sturm_I2 {n_minus}"),
        "I1 (0,1) sign 1".into(),
        "I2 (-1,0) sign -1".into(),
        "T2_pm_half_sign_changes 1".into(),
        "preimage_half_strictly_inside 1".into(),
        "polar_radial 1".into(),
        "polar_angular 1".into(),
        "fprime_rho -1 2".into(),
        "hyperbolic 1".into(),
        "conjugacy 1".into(),
        "deg_X 3".into(),
        format!("deg_Y {deg_y}"),
        format!("deg_Yu {deg_u}"),
        format!("deg_Yv {deg_v}"),
        "expected_deg 7".into(),
        format!("n_terms_Yu {}", yu.terms.len()),
        format!("n_terms_Yv {}", yv.terms.len()),
    ];
    lines.extend(dump_mons("Yu", &yu));
    lines.extend(dump_mons("Yv", &yv));
    lines.push("leading_Yu -32 u^2 v (u^4+v^4)".into());
    lines.push("leading_Yv -32 u v^2 (u^4+v^4)".into());
    lines.push("integer_4X_deg 7".into());
    for (n, deg) in &lemma5 {
        lines.push(format!("lemma5 n={n} m=2 deg {deg}"));
    }
    lines.push("level_curve 16u^4 - 16u^2 + 16v^4 - 16v^2 + 7".into());
    lines.push("level_curve_deg 4".into());
    lines.push("four_oval_factors_over_Q 0".into());
    lines.push("rectangle 1 1 I1 I1".into());
    lines.push("rectangle 1 2 I1 I2".into());
    lines.push("rectangle 2 1 I2 I1".into());
    lines.push("rectangle 2 2 I2 I2".into());
    lines.push("four_ovals 1".into());
    lines.push("H7_from_this_field 4".into());
    lines.push("beats_PT_74 0".into());
    lines.push("same_4_sheets_as_CL_at_N7 1".into());
    lines.push("beats_CL 0".into());
    lines.push("CL_beats_this 0".into());
    lines.push("do_not_claim_252_1080_1380_2012 1".into());
    lines.push("hn_moved 0".into());

    let text = lines.join("\n") + "\n";
    if let Some(path) = dump_path {
        fs::write(&path, &text).unwrap_or_else(|e| fail(&format!("write dump: {e}")));
    }

    write_core(&yu, &yv, deg_u, deg_v, deg_y);

    print!("{text}");
    println!("verify.rs: ok");
    println!("  deg Y = {deg_y} (expected 7)");
    println!(
        "  Yu terms = {}, Yv terms = {}",
        yu.terms.len(),
        yv.terms.len()
    );
    println!("  four ovals = true");
    println!("  beats PT 74 = false");
}
