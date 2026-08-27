//! Second verifier for the Chebyshev pullback replay of arXiv:2604.12883v1.
//!
//! Independent of verify.py: integer Chebyshev recurrence, bivariate
//! polynomials over Q, exact Section 6 expansion, nine-rectangle sign
//! checks, and Table 1 / Appendix A arithmetic. rustc only.

use std::collections::BTreeMap;
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

// X is a polynomial in (x, y). We reuse BiPoly with (u,v) meaning (x,y).
fn section6_x(rho2: Ratio) -> (BiPoly, BiPoly) {
    // P = y - x (x^2 + y^2 - rho2) = y - x^3 - x y^2 + rho2 x
    // Q = -x - y (x^2 + y^2 - rho2) = -x - x^2 y - y^3 + rho2 y
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

// ---------------------------------------------------------------------------
// Checks
// ---------------------------------------------------------------------------

fn check_chebyshev() -> BTreeMap<usize, Vec<i128>> {
    let named: [(usize, Vec<i128>); 6] = [
        (0, vec![1]),
        (1, vec![0, 1]),
        (2, vec![-1, 0, 2]),
        (3, vec![0, -3, 0, 4]),
        (4, vec![1, 0, -8, 0, 8]),
        (5, vec![0, 5, 0, -20, 0, 16]),
    ];
    let mut all = BTreeMap::new();
    for (m, expect) in named {
        let got = chebyshev_t(m).int_coeffs_asc();
        if got != expect {
            fail(&format!("T_{m} coeffs {got:?} != {expect:?}"));
        }
        all.insert(m, got);
    }
    for m in 6..=8 {
        all.insert(m, chebyshev_t(m).int_coeffs_asc());
    }

    for m in 1..=16 {
        let tm = chebyshev_t(m);
        let tp = tm.diff();
        // m^2 T^2 + (1-t^2) (T')^2 - m^2 = 0
        let m2 = Ratio::from_i((m as i128) * (m as i128));
        let t2 = UPoly::t().pow(2);
        let one_minus_t2 = UPoly::constant(Ratio::from_i(1)).sub(&t2);
        let ident = tm
            .pow(2)
            .scale(m2)
            .add(&one_minus_t2.mul(&tp.pow(2)))
            .sub(&UPoly::constant(m2));
        if !ident.is_zero() {
            fail(&format!("Pell identity failed for m={m}"));
        }
        if tm.eval(Ratio::from_i(1)) != Ratio::from_i(1) {
            fail(&format!("T_{m}(1) != 1"));
        }
        let expect_m1 = if m % 2 == 0 {
            Ratio::from_i(1)
        } else {
            Ratio::from_i(-1)
        };
        if tm.eval(Ratio::from_i(-1)) != expect_m1 {
            fail(&format!("T_{m}(-1) mismatch"));
        }
    }
    all
}

fn check_degree_formula() {
    let samples: [(usize, usize); 9] = [
        (1, 2),
        (2, 2),
        (3, 2),
        (3, 3),
        (4, 3),
        (5, 2),
        (1, 5),
        (6, 2),
        (2, 4),
    ];
    for (n, m) in samples {
        let mut p = BiPoly::zero();
        p.terms.insert((n as i32, 0), Ratio::from_i(1)); // x^n in (x,y)
        let q = BiPoly::zero();
        let tm = chebyshev_t(m);
        let (yu, yv, _, _) = pullback(&p, &q, &tm);
        let deg = yu.total_degree().max(yv.total_degree());
        let expected = (n * m + (m - 1)) as i32;
        if deg != expected {
            fail(&format!(
                "deg Y for (x^{n},0), m={m}: {deg} != {expected}"
            ));
        }
    }
}

fn check_polar(rho2: Ratio) {
    let (p, q) = section6_x(rho2);
    let x = BiPoly::u();
    let y = BiPoly::v();
    let r2 = x.pow(2).add(&y.pow(2));
    // xP + yQ + (x^2+y^2)((x^2+y^2)-rho2) = 0
    let radial = x
        .mul(&p)
        .add(&y.mul(&q))
        .add(&r2.mul(&r2.sub(&BiPoly::constant(rho2))));
    // xQ - yP + (x^2+y^2) = 0
    let angular = x.mul(&q).sub(&y.mul(&p)).add(&r2);
    if !radial.is_zero() || !angular.is_zero() {
        fail("polar identities failed");
    }
    let fprime = rho2.mul(Ratio::from_i(-2));
    if fprime.is_zero() {
        fail("f'(rho)=0");
    }
}

fn check_section6() -> (BiPoly, BiPoly, i32, i32, i32) {
    let rho2 = Ratio::new(1, 4);
    let (p, q) = section6_x(rho2);
    let deg_x = p.total_degree().max(q.total_degree());
    if deg_x != 3 {
        fail(&format!("deg X = {deg_x}"));
    }
    let tm = chebyshev_t(3);
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
    if deg_y != 11 {
        fail(&format!("deg Y = {deg_y}, expected 11"));
    }

    // Integer time-rescale 4X.
    let (yu4, yv4, _, _) = pullback(&p.scale(Ratio::from_i(4)), &q.scale(Ratio::from_i(4)), &tm);
    if yu4.total_degree().max(yv4.total_degree()) != 11 {
        fail("integer 4X pullback degree != 11");
    }
    (yu, yv, deg_u, deg_v, deg_y)
}

fn check_nine_rectangles() {
    let tm = chebyshev_t(3);
    let tp = tm.diff();
    // T3' = 12 t^2 - 3 = 3(2t-1)(2t+1)
    let expect_tp = UPoly::from_coeffs(vec![
        Ratio::from_i(-3),
        Ratio::zero(),
        Ratio::from_i(12),
    ]);
    if tp.c != expect_tp.c {
        fail("T3' coeffs");
    }
    let fact = UPoly::from_coeffs(vec![Ratio::from_i(3)])
        .mul(&UPoly::from_coeffs(vec![
            Ratio::from_i(-1),
            Ratio::from_i(2),
        ]))
        .mul(&UPoly::from_coeffs(vec![
            Ratio::from_i(1),
            Ratio::from_i(2),
        ]));
    if fact.c != tp.c {
        fail("T3' != 3(2t-1)(2t+1)");
    }

    let ev = |arg: Ratio| tm.eval(arg);
    let ep = |arg: Ratio| tp.eval(arg);
    if ev(Ratio::from_i(1)) != Ratio::from_i(1) {
        fail("T3(1)");
    }
    if ev(Ratio::from_i(-1)) != Ratio::from_i(-1) {
        fail("T3(-1)");
    }
    if ev(Ratio::new(1, 2)) != Ratio::from_i(-1) {
        fail("T3(1/2)");
    }
    if ev(Ratio::new(-1, 2)) != Ratio::from_i(1) {
        fail("T3(-1/2)");
    }
    if ev(Ratio::zero()) != Ratio::zero() {
        fail("T3(0)");
    }
    if !ep(Ratio::new(1, 2)).is_zero() || !ep(Ratio::new(-1, 2)).is_zero() {
        fail("T3'(±1/2) != 0");
    }
    if ep(Ratio::zero()) != Ratio::from_i(-3) {
        fail("T3'(0)");
    }
    if ep(Ratio::new(3, 4)) != Ratio::new(12 * 9 - 3 * 16, 16) {
        fail("T3'(3/4)");
    }
    if ep(Ratio::new(1, 4)) != Ratio::new(12 - 48, 16) {
        fail("T3'(1/4)");
    }

    let intervals: [(&str, Ratio, Ratio, i8); 3] = [
        ("I1", Ratio::new(1, 2), Ratio::from_i(1), 1),
        ("I2", Ratio::new(-1, 2), Ratio::new(1, 2), -1),
        ("I3", Ratio::from_i(-1), Ratio::new(-1, 2), 1),
    ];
    for (name, left, right, sign) in intervals {
        let mid = left.add(right).mul(Ratio::new(1, 2));
        let tp_mid = ep(mid);
        if tp_mid.is_zero() {
            fail(&format!("T3' vanishes in {name}"));
        }
        let got_sign: i8 = if tp_mid.n > 0 { 1 } else { -1 };
        if got_sign != sign {
            fail(&format!("T3' sign on {name}"));
        }
        let t_left = ev(left);
        let t_right = ev(right);
        if t_left.n.abs() != t_left.d || t_right.n.abs() != t_right.d {
            fail(&format!("|T3| != 1 at endpoints of {name}"));
        }
        if t_left == t_right {
            fail(&format!("T3 not opposite on {name}"));
        }
        let half = Ratio::new(1, 2);
        let minus_l = t_left.add(half);
        let minus_r = t_right.add(half);
        let plus_l = t_left.sub(half);
        let plus_r = t_right.sub(half);
        if minus_l.n.signum() * minus_r.n.signum() >= 0
            || plus_l.n.signum() * plus_r.n.signum() >= 0
        {
            fail(&format!("T3±1/2 do not change sign on {name}"));
        }
        if t_left.n.abs() * half.d <= half.n * t_left.d
            || t_right.n.abs() * half.d <= half.n * t_right.d
        {
            fail(&format!("[-1/2,1/2] not strictly inside T3({name})"));
        }
    }
}

// ---------------------------------------------------------------------------
// Table
// ---------------------------------------------------------------------------

fn seeds_app_a() -> BTreeMap<i32, i64> {
    let rows: [(i32, i64); 22] = [
        (4, 28),
        (5, 37),
        (6, 53),
        (7, 74),
        (8, 96),
        (9, 120),
        (10, 142),
        (11, 153),
        (12, 157),
        (13, 212),
        (14, 194),
        (15, 345),
        (16, 351),
        (17, 384),
        (18, 372),
        (19, 503),
        (20, 509),
        (21, 568),
        (31, 1184),
        (35, 1536),
        (39, 1920),
        (43, 2272),
    ];
    rows.into_iter().collect()
}

fn paper_l_ch() -> BTreeMap<i32, i64> {
    [
        (11, 148),
        (13, 212),
        (14, 252),
        (15, 296),
        (17, 384),
        (19, 480),
        (20, 477),
        (21, 568),
        (23, 666),
        (24, 700),
        (25, 628),
        (26, 864),
        (27, 848),
        (29, 1080),
        (31, 1380),
        (35, 1536),
        (39, 2012),
        (43, 2272),
    ]
    .into_iter()
    .collect()
}

fn paper_four() -> [(i32, i64); 4] {
    [(14, 252), (29, 1080), (31, 1380), (39, 2012)]
}

fn l_ch_for(n_target: i32, seeds: &BTreeMap<i32, i64>) -> Option<(i64, Vec<(i32, i32, i64)>)> {
    let np = n_target + 1;
    let mut known = Vec::new();
    for m in 2..=np {
        if np % m != 0 {
            continue;
        }
        let n = np / m - 1;
        if n < 1 {
            continue;
        }
        if let Some(&seed) = seeds.get(&n) {
            let lift = (m as i64) * (m as i64) * seed;
            known.push((n, m, lift));
        }
    }
    if known.is_empty() {
        return None;
    }
    let best = known.iter().map(|r| r.2).max().unwrap();
    let argmax: Vec<_> = known.into_iter().filter(|r| r.2 == best).collect();
    Some((best, argmax))
}

fn check_table() -> BTreeMap<i32, i64> {
    let seeds = seeds_app_a();
    let paper = paper_l_ch();
    let mut ours = BTreeMap::new();
    for (&n, &pval) in &paper {
        match l_ch_for(n, &seeds) {
            Some((got, _)) if got == pval => {
                ours.insert(n, got);
            }
            Some((got, argmax)) => {
                fail(&format!(
                    "L_Ch({n}) = {got} != paper {pval}; argmax {argmax:?}"
                ));
            }
            None => fail(&format!("no L_Ch({n})")),
        }
    }
    let mut beats = Vec::new();
    for (n, pval) in paper_four() {
        let (got, _) = l_ch_for(n, &seeds).unwrap();
        if got > pval {
            beats.push(n);
        }
        if got != pval {
            fail(&format!("four-new N={n}: {got} != {pval}"));
        }
    }
    if !beats.is_empty() {
        fail(&format!("unexpected beat of the four numbers: {beats:?}"));
    }

    // Exhaust N<=50; store every defined L_Ch.
    let mut all = BTreeMap::new();
    for n in 1..=50 {
        if let Some((val, _)) = l_ch_for(n, &seeds) {
            all.insert(n, val);
        }
    }
    ours.append(&mut all.clone());
    ours
}

// ---------------------------------------------------------------------------
// JSON
// ---------------------------------------------------------------------------

fn cwd_certs() -> PathBuf {
    let certs = std::env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .join("certs");
    fs::create_dir_all(&certs).unwrap_or_else(|e| fail(&format!("mkdir certs: {e}")));
    certs
}

fn write_core(
    tm_coeffs: &BTreeMap<usize, Vec<i128>>,
    yu: &BiPoly,
    yv: &BiPoly,
    deg_u: i32,
    deg_v: i32,
    deg_y: i32,
    lch: &BTreeMap<i32, i64>,
) {
    let path = cwd_certs().join("rust_core.json");

    let mut body = String::new();
    body.push_str("{\n");
    body.push_str(&format!("  \"deg_Y\": {deg_y},\n"));
    body.push_str(&format!("  \"deg_Yu\": {deg_u},\n"));
    body.push_str(&format!("  \"deg_Yv\": {deg_v},\n"));
    body.push_str("  \"deg_X\": 3,\n");
    body.push_str("  \"conjugacy\": true,\n");
    body.push_str("  \"H11_from_this_field\": 9,\n");
    body.push_str("  \"beats_HanLi_153\": false,\n");
    body.push_str("  \"nine_ovals\": true,\n");
    body.push_str("  \"T3_at_1\": [1, 1],\n");
    body.push_str("  \"T3_at_-1\": [-1, 1],\n");
    body.push_str("  \"T3_at_1/2\": [-1, 1],\n");
    body.push_str("  \"T3_at_-1/2\": [1, 1],\n");

    let paper_ns = [
        11, 13, 14, 15, 17, 19, 20, 21, 23, 24, 25, 26, 27, 29, 31, 35, 39, 43,
    ];
    body.push_str("  \"L_Ch\": {\n");
    for (i, n) in paper_ns.iter().enumerate() {
        let val = lch.get(n).copied().unwrap_or_else(|| fail("missing L_Ch"));
        let comma = if i + 1 == paper_ns.len() { "" } else { "," };
        body.push_str(&format!("    \"{n}\": {val}{comma}\n"));
    }
    body.push_str("  },\n");
    body.push_str("  \"beats_four\": [],\n");
    body.push_str("  \"table1_L_Ch_match\": true,\n");
    body.push_str("  \"four\": {\n");
    body.push_str("    \"14\": 252,\n");
    body.push_str("    \"29\": 1080,\n");
    body.push_str("    \"31\": 1380,\n");
    body.push_str("    \"39\": 2012\n");
    body.push_str("  },\n");

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
    body.push_str(",\n  \"T_m\": {\n");
    let last_m = *tm_coeffs.keys().max().unwrap();
    for (m, coeffs) in tm_coeffs {
        let comma = if *m == last_m { "" } else { "," };
        let list = coeffs
            .iter()
            .map(|c| c.to_string())
            .collect::<Vec<_>>()
            .join(", ");
        body.push_str(&format!("    \"{m}\": [{list}]{comma}\n"));
    }
    body.push_str("  }\n}\n");

    let mut fh = fs::File::create(&path).unwrap_or_else(|e| fail(&format!("write {path:?}: {e}")));
    fh.write_all(body.as_bytes())
        .unwrap_or_else(|e| fail(&format!("write {path:?}: {e}")));
}

fn write_table(lch: &BTreeMap<i32, i64>) {
    let path = cwd_certs().join("rust_table.json");
    let mut body = String::from("{\n  \"L_Ch_N_le_50\": {\n");
    let keys: Vec<_> = lch.keys().copied().collect();
    for (i, n) in keys.iter().enumerate() {
        let comma = if i + 1 == keys.len() { "" } else { "," };
        body.push_str(&format!("    \"{n}\": {}{comma}\n", lch[n]));
    }
    body.push_str("  },\n  \"beats_four\": [],\n  \"table1_L_Ch_match\": true\n}\n");
    fs::write(&path, body).unwrap_or_else(|e| fail(&format!("write table: {e}")));
}

fn main() {
    let tm_coeffs = check_chebyshev();
    check_degree_formula();
    check_polar(Ratio::new(1, 4));
    let (yu, yv, deg_u, deg_v, deg_y) = check_section6();
    check_nine_rectangles();
    let lch = check_table();
    write_core(&tm_coeffs, &yu, &yv, deg_u, deg_v, deg_y, &lch);
    write_table(&lch);
    println!("verify.rs: ok");
    println!("  deg Y = {deg_y} (expected 11)");
    println!("  nine ovals = true");
    println!("  Table 1 L_Ch match = true");
    println!("  beats 252/1080/1380/2012 = []");
}
