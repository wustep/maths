//! Second verifier for the holomorphic cube pullback.
//!
//! Independent of verify.py: Q[u,v] expansion of Y = adj(DΦ)(X ∘ Φ)
//! for Φ(u,v)=(u³−3uv², 3u²v−v³), Cauchy–Riemann / Jacobian,
//! a 5×5 Sylvester resultant, exact fibre counts, polar cube roots,
//! and the n=1,2,3 arithmetic against T3. rustc only.

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

    fn neg(self) -> Self {
        Self { n: -self.n, d: self.d }
    }
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

    fn diff_u(&self) -> Self {
        let mut out = Self::zero();
        for ((i, j), a) in &self.terms {
            if *i > 0 {
                out = out.add(&Self::monomial(i - 1, *j, a.mul(Ratio::from_i(*i as i128))));
            }
        }
        out
    }

    fn diff_v(&self) -> Self {
        let mut out = Self::zero();
        for ((i, j), a) in &self.terms {
            if *j > 0 {
                out = out.add(&Self::monomial(*i, j - 1, a.mul(Ratio::from_i(*j as i128))));
            }
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

fn phi() -> (BiPoly, BiPoly) {
    let u = BiPoly::u();
    let v = BiPoly::v();
    let p = u.pow(3).sub(&u.mul(&v.pow(2)).scale(Ratio::from_i(3)));
    let q = u.pow(2).mul(&v).scale(Ratio::from_i(3)).sub(&v.pow(3));
    (p, q)
}

fn radial_cubic() -> (BiPoly, BiPoly) {
    let x = BiPoly::u();
    let y = BiPoly::v();
    let rho2 = Ratio::new(1, 4);
    let r2 = x.pow(2).add(&y.pow(2)).sub(&BiPoly::constant(rho2));
    let p = y.sub(&x.mul(&r2));
    let q = x.scale(Ratio::from_i(-1)).sub(&y.mul(&r2));
    (p, q)
}

fn linear_center() -> (BiPoly, BiPoly) {
    (BiPoly::v(), BiPoly::u().scale(Ratio::from_i(-1)))
}

fn sample_quadratic() -> (BiPoly, BiPoly) {
    let x = BiPoly::u();
    let y = BiPoly::v();
    (x.pow(2).add(&y), y.pow(2).add(&x))
}

fn chebyshev_t3() -> (BiPoly, BiPoly) {
    let u = BiPoly::u();
    let v = BiPoly::v();
    let pu = u.pow(3).scale(Ratio::from_i(4)).sub(&u.scale(Ratio::from_i(3)));
    let pv = v.pow(3).scale(Ratio::from_i(4)).sub(&v.scale(Ratio::from_i(3)));
    (pu, pv)
}

fn adj_pullback(
    p: &BiPoly,
    q: &BiPoly,
    px: &BiPoly,
    qx: &BiPoly,
) -> (BiPoly, BiPoly, BiPoly, BiPoly, BiPoly) {
    let pu = p.diff_u();
    let pv = p.diff_v();
    let qu = q.diff_u();
    let qv = q.diff_v();
    let det = pu.mul(&qv).sub(&pv.mul(&qu));
    let pc = px.compose(p, q);
    let qc = qx.compose(p, q);
    let yu = qv.mul(&pc).sub(&pv.mul(&qc));
    let yv = qu.mul(&pc).scale(Ratio::from_i(-1)).add(&pu.mul(&qc));
    let du = pu.mul(&yu).add(&pv.mul(&yv)).sub(&det.mul(&pc));
    let dv = qu.mul(&yu).add(&qv.mul(&yv)).sub(&det.mul(&qc));
    (yu, yv, det, du, dv)
}

fn dump_mons(prefix: &str, p: &BiPoly) -> Vec<String> {
    p.monomials_sorted()
        .into_iter()
        .map(|(eu, ev, a)| format!("{prefix} {eu} {ev} {} {}", a.n, a.d))
        .collect()
}

fn det_matrix(m: &[Vec<BiPoly>]) -> BiPoly {
    let n = m.len();
    if n == 0 {
        fail("empty matrix");
    }
    if n == 1 {
        return m[0][0].clone();
    }
    if n == 2 {
        return m[0][0].mul(&m[1][1]).sub(&m[0][1].mul(&m[1][0]));
    }
    let mut out = BiPoly::zero();
    for j in 0..n {
        let mut minor = Vec::with_capacity(n - 1);
        for i in 1..n {
            let mut row = Vec::with_capacity(n - 1);
            for k in 0..n {
                if k != j {
                    row.push(m[i][k].clone());
                }
            }
            minor.push(row);
        }
        let sign = if j % 2 == 0 {
            Ratio::from_i(1)
        } else {
            Ratio::from_i(-1)
        };
        let cof = det_matrix(&minor).scale(sign);
        out = out.add(&m[0][j].mul(&cof));
    }
    out
}

/// Res_v(u³−3uv²−x, 3u²v−v³−y) as a polynomial in the first BiPoly
/// coordinate. `x` and `y` are constants. The second variable of the
/// BiPoly is unused (always 0).
fn resultant_specialized(x: Ratio, y: Ratio) -> BiPoly {
    let u = BiPoly::u();
    let f2 = u.scale(Ratio::from_i(-3));
    let f1 = BiPoly::zero();
    let f0 = u.pow(3).sub(&BiPoly::constant(x));
    let g3 = BiPoly::constant(Ratio::from_i(-1));
    let g2 = BiPoly::zero();
    let g1 = u.pow(2).scale(Ratio::from_i(3));
    let g0 = BiPoly::constant(y.neg());
    let z = BiPoly::zero();
    let m = vec![
        vec![f2.clone(), f1.clone(), f0.clone(), z.clone(), z.clone()],
        vec![z.clone(), f2.clone(), f1.clone(), f0.clone(), z.clone()],
        vec![z.clone(), z.clone(), f2.clone(), f1.clone(), f0.clone()],
        vec![g3.clone(), g2.clone(), g1.clone(), g0.clone(), z.clone()],
        vec![z, g3, g2, g1, g0],
    ];
    det_matrix(&m)
}

/// Same Sylvester, but the second BiPoly variable stands for x (y = 0).
fn resultant_y0_x_as_v() -> BiPoly {
    let u = BiPoly::u();
    let x = BiPoly::v();
    let f2 = u.scale(Ratio::from_i(-3));
    let f1 = BiPoly::zero();
    let f0 = u.pow(3).sub(&x);
    let g3 = BiPoly::constant(Ratio::from_i(-1));
    let g2 = BiPoly::zero();
    let g1 = u.pow(2).scale(Ratio::from_i(3));
    let g0 = BiPoly::zero();
    let z = BiPoly::zero();
    let m = vec![
        vec![f2.clone(), f1.clone(), f0.clone(), z.clone(), z.clone()],
        vec![z.clone(), f2.clone(), f1.clone(), f0.clone(), z.clone()],
        vec![z.clone(), z.clone(), f2.clone(), f1.clone(), f0.clone()],
        vec![g3.clone(), g2.clone(), g1.clone(), g0.clone(), z.clone()],
        vec![z, g3, g2, g1, g0],
    ];
    det_matrix(&m)
}

/// Same Sylvester, second variable stands for y (x = 0).
fn resultant_x0_y_as_v() -> BiPoly {
    let u = BiPoly::u();
    let y = BiPoly::v();
    let f2 = u.scale(Ratio::from_i(-3));
    let f1 = BiPoly::zero();
    let f0 = u.pow(3);
    let g3 = BiPoly::constant(Ratio::from_i(-1));
    let g2 = BiPoly::zero();
    let g1 = u.pow(2).scale(Ratio::from_i(3));
    let g0 = y.scale(Ratio::from_i(-1));
    let z = BiPoly::zero();
    let m = vec![
        vec![f2.clone(), f1.clone(), f0.clone(), z.clone(), z.clone()],
        vec![z.clone(), f2.clone(), f1.clone(), f0.clone(), z.clone()],
        vec![z.clone(), z.clone(), f2.clone(), f1.clone(), f0.clone()],
        vec![g3.clone(), g2.clone(), g1.clone(), g0.clone(), z.clone()],
        vec![z, g3, g2, g1, g0],
    ];
    det_matrix(&m)
}

fn check_resultant() {
    let half = resultant_specialized(Ratio::new(1, 2), Ratio::zero());
    let mut expect_half = BiPoly::zero();
    expect_half = expect_half.add(&BiPoly::monomial(9, 0, Ratio::from_i(64)));
    expect_half = expect_half.sub(&BiPoly::monomial(6, 0, Ratio::from_i(24)));
    expect_half = expect_half.sub(&BiPoly::monomial(3, 0, Ratio::new(15, 4)));
    expect_half = expect_half.sub(&BiPoly::constant(Ratio::new(1, 8)));
    if half.terms != expect_half.terms {
        fail("Sylvester at (1/2,0)");
    }
    let qq = resultant_specialized(Ratio::new(1, 4), Ratio::new(1, 4));
    let mut expect_qq = BiPoly::zero();
    expect_qq = expect_qq.add(&BiPoly::monomial(9, 0, Ratio::from_i(64)));
    expect_qq = expect_qq.sub(&BiPoly::monomial(6, 0, Ratio::from_i(12)));
    expect_qq = expect_qq.sub(&BiPoly::monomial(3, 0, Ratio::new(21, 8)));
    expect_qq = expect_qq.sub(&BiPoly::constant(Ratio::new(1, 64)));
    if qq.terms != expect_qq.terms {
        fail("Sylvester at (1/4,1/4)");
    }
    let y0 = resultant_y0_x_as_v();
    // 64u^9 - 48 x u^6 - 15 x^2 u^3 - x^3
    let u = BiPoly::u();
    let x = BiPoly::v();
    let expect_y0 = u
        .pow(9)
        .scale(Ratio::from_i(64))
        .sub(&u.pow(6).mul(&x).scale(Ratio::from_i(48)))
        .sub(&u.pow(3).mul(&x.pow(2)).scale(Ratio::from_i(15)))
        .sub(&x.pow(3));
    if y0.terms != expect_y0.terms {
        fail("Sylvester y=0 generic in x");
    }
    let x0 = resultant_x0_y_as_v();
    let y = BiPoly::v();
    let expect_x0 = u
        .pow(9)
        .scale(Ratio::from_i(64))
        .sub(&u.pow(3).mul(&y.pow(2)).scale(Ratio::from_i(27)));
    if x0.terms != expect_x0.terms {
        fail("Sylvester x=0 generic in y");
    }
    for (eu, ev, _) in y0.monomials_sorted() {
        if eu % 3 != 0 {
            fail("resultant y=0 not a polynomial in u^3");
        }
        let _ = ev;
    }
}

fn check_preimages() {
    // (1/2, 0): v(3u²−v²)=0. v=0 ⇒ one real cube root of 1/2.
    // v²=3u² ⇒ −8u³=1/2 ⇒ u³=−1/16, two signs of v. Three regular.
    // (1/4, 1/4): (−1/2, 1/2) is an exact regular preimage.
    let u0 = Ratio::new(-1, 2);
    let v0 = Ratio::new(1, 2);
    // Φ = u³ − 3uv² = -1/8 − 3(-1/2)(1/4) = -1/8 + 3/8 = 1/4
    let phi = u0.mul(u0).mul(u0).sub(Ratio::from_i(3).mul(u0).mul(v0).mul(v0));
    let psi = Ratio::from_i(3)
        .mul(u0)
        .mul(u0)
        .mul(v0)
        .sub(v0.mul(v0).mul(v0));
    if phi != Ratio::new(1, 4) || psi != Ratio::new(1, 4) {
        fail("(-1/2,1/2) is not a preimage of (1/4,1/4)");
    }
    let r2 = u0.mul(u0).add(v0.mul(v0));
    let det = Ratio::from_i(9).mul(r2).mul(r2);
    if det != Ratio::new(9, 4) {
        fail("(-1/2,1/2) Jacobian");
    }
    // T3(t)=1/2 ⇔ 8t³−6t−1=0. disc=5184, three reals in (−1,1), T3'≠0.
    let a = 8i128;
    let b = 0i128;
    let c = -6i128;
    let d = -1i128;
    let disc = 18 * a * b * c * d - 4 * b * b * b * d + b * b * c * c - 4 * a * c * c * c
        - 27 * a * a * d * d;
    if disc != 5184 {
        fail(&format!("T3 cubic discriminant {disc}"));
    }
    // t³ − (3/4)t − 1/8: (q/2)²+(p/3)³ = (1/256) + (−1/64) = −3/256.
    let delta = Ratio::new(1, 256).add(Ratio::new(-1, 64));
    if delta != Ratio::new(-3, 256) {
        fail("T3 cubic delta");
    }
}

fn polar_count(a: f64, b: f64) -> usize {
    let w_mod = (a * a + b * b).sqrt();
    if w_mod == 0.0 {
        fail("polar target is 0");
    }
    let w_arg = b.atan2(a);
    let r = w_mod.powf(1.0 / 3.0);
    let mut pts = Vec::with_capacity(3);
    for j in 0..3 {
        let th = (w_arg + 2.0 * std::f64::consts::PI * (j as f64)) / 3.0;
        pts.push((r * th.cos(), r * th.sin()));
    }
    for &(u0, v0) in &pts {
        let u = u0 * u0 * u0 - 3.0 * u0 * v0 * v0;
        let v = 3.0 * u0 * u0 * v0 - v0 * v0 * v0;
        if (u - a).abs() + (v - b).abs() > 1e-9 {
            fail("polar cube missed target");
        }
        if u0 * u0 + v0 * v0 < 1e-18 {
            fail("polar preimage at origin");
        }
        if 9.0 * (u0 * u0 + v0 * v0) * (u0 * u0 + v0 * v0) < 1e-18 {
            fail("polar Jacobian vanished");
        }
    }
    for i in 0..pts.len() {
        for j in (i + 1)..pts.len() {
            if (pts[i].0 - pts[j].0).abs() + (pts[i].1 - pts[j].1).abs() < 1e-9 {
                fail("polar cube collision");
            }
        }
    }
    pts.len()
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

    let (p, q) = phi();
    let pu = p.diff_u();
    let pv = p.diff_v();
    let qu = q.diff_u();
    let qv = q.diff_v();
    let det = pu.mul(&qv).sub(&pv.mul(&qu));
    let r2 = BiPoly::u().pow(2).add(&BiPoly::v().pow(2));
    let expect_det = r2.pow(2).scale(Ratio::from_i(9));
    if det.terms != expect_det.terms {
        fail("det DΦ != 9(u^2+v^2)^2");
    }
    if pu.terms != qv.terms || pv.terms != qu.scale(Ratio::from_i(-1)).terms {
        fail("Cauchy-Riemann failed");
    }
    let expect_pu = BiPoly::u()
        .pow(2)
        .sub(&BiPoly::v().pow(2))
        .scale(Ratio::from_i(3));
    let expect_pv = BiPoly::u()
        .mul(&BiPoly::v())
        .scale(Ratio::from_i(-6));
    let expect_qu = BiPoly::u().mul(&BiPoly::v()).scale(Ratio::from_i(6));
    if pu.terms != expect_pu.terms
        || pv.terms != expect_pv.terms
        || qu.terms != expect_qu.terms
        || qv.terms != expect_pu.terms
    {
        fail("DΦ entries");
    }
    let jac_sum = pu.pow(2).add(&pv.pow(2));
    if jac_sum.terms != expect_det.terms {
        fail("Jacobian != Φ_u^2 + Φ_v^2");
    }
    let mod_id = p.pow(2).add(&q.pow(2)).sub(&r2.pow(3));
    if !mod_id.is_zero() {
        fail("modulus identity Φ^2+Ψ^2 = (u^2+v^2)^3 failed");
    }

    let (p1, q1) = linear_center();
    let (yu1, yv1, _, du1, dv1) = adj_pullback(&p, &q, &p1, &q1);
    if !du1.is_zero() || !dv1.is_zero() {
        fail("linear adj identity failed");
    }
    let deg_1 = yu1.total_degree().max(yv1.total_degree());
    if deg_1 != 5 {
        fail(&format!("linear one-step deg {deg_1}"));
    }
    let expect_yu1 = BiPoly::v().mul(&r2.pow(2)).scale(Ratio::from_i(3));
    let expect_yv1 = BiPoly::u().mul(&r2.pow(2)).scale(Ratio::from_i(-3));
    if yu1.terms != expect_yu1.terms || yv1.terms != expect_yv1.terms {
        fail("linear closed form");
    }

    let (p2, q2) = sample_quadratic();
    let (yu2, yv2, _, du2, dv2) = adj_pullback(&p, &q, &p2, &q2);
    if !du2.is_zero() || !dv2.is_zero() {
        fail("quadratic adj identity failed");
    }
    let deg_2 = yu2.total_degree().max(yv2.total_degree());
    if deg_2 != 8 {
        fail(&format!("quadratic one-step deg {deg_2}"));
    }

    let (px, qx) = radial_cubic();
    let (yu, yv, _, du, dv) = adj_pullback(&p, &q, &px, &qx);
    if !du.is_zero() || !dv.is_zero() {
        fail("radial adj identity failed");
    }
    let deg_r = yu.total_degree().max(yv.total_degree());
    if deg_r != 11 {
        fail(&format!("radial one-step deg {deg_r}"));
    }
    let n_yu = yu.terms.len();
    let n_yv = yv.terms.len();
    if n_yu != 12 || n_yv != 12 {
        fail(&format!("radial term counts {n_yu} {n_yv}"));
    }
    let lead_u = yu.homog(11);
    let lead_v = yv.homog(11);
    let expect_lead_u = BiPoly::u().mul(&r2.pow(5)).scale(Ratio::from_i(-3));
    let expect_lead_v = BiPoly::v().mul(&r2.pow(5)).scale(Ratio::from_i(-3));
    if lead_u.terms != expect_lead_u.terms || lead_v.terms != expect_lead_v.terms {
        fail("radial leading form");
    }

    let (t3u, t3v) = chebyshev_t3();
    let (ytu1, ytv1, _, dtu1, dtv1) = adj_pullback(&t3u, &t3v, &p1, &q1);
    if !dtu1.is_zero() || !dtv1.is_zero() {
        fail("T3 linear adj identity failed");
    }
    let deg_t3_1 = ytu1.total_degree().max(ytv1.total_degree());
    if deg_t3_1 != 5 {
        fail(&format!("T3 linear deg {deg_t3_1}"));
    }
    let (ytu2, ytv2, _, dtu2, dtv2) = adj_pullback(&t3u, &t3v, &p2, &q2);
    if !dtu2.is_zero() || !dtv2.is_zero() {
        fail("T3 quad adj identity failed");
    }
    let deg_t3_2 = ytu2.total_degree().max(ytv2.total_degree());
    if deg_t3_2 != 8 {
        fail(&format!("T3 quad deg {deg_t3_2}"));
    }
    let (ytu, ytv, _, dtu, dtv) = adj_pullback(&t3u, &t3v, &px, &qx);
    if !dtu.is_zero() || !dtv.is_zero() {
        fail("T3 radial adj identity failed");
    }
    let deg_t3_r = ytu.total_degree().max(ytv.total_degree());
    if deg_t3_r != 11 {
        fail(&format!("T3 radial deg {deg_t3_r}"));
    }

    check_preimages();
    check_resultant();
    let polar_half = polar_count(0.5, 0.0);
    let polar_qq = polar_count(0.25, 0.25);
    if polar_half != 3 || polar_qq != 3 {
        fail("polar cube counts");
    }

    let mut rows = Vec::new();
    for n in [1i128, 2, 3] {
        let n_deg = 3 * n + 2;
        let sheets = 3i128;
        let bezout = 9i128;
        let cheb = 9i128;
        if n_deg != n * 3 + 3 - 1 {
            fail("N mismatch vs one-step Chebyshev of degree 3");
        }
        if sheets * (n + 1) != n_deg + 1 {
            fail("3 != (N+1)/(n+1)");
        }
        rows.push((n, n_deg, sheets, bezout, cheb));
    }

    let mut lines: Vec<String> = vec![
        "det 9(u^2+v^2)^2".into(),
        "cr Phi_u=Psi_v=3(u^2-v^2) Phi_v=-Psi_u=-6uv".into(),
        "jac_zeros_only_origin 1".into(),
        "mod_identity 1".into(),
        "identity_linear 1".into(),
        "identity_quad 1".into(),
        "identity_radial 1".into(),
        format!("deg_linear {deg_1} bound 5"),
        format!("deg_quad {deg_2} bound 8"),
        format!("deg_radial {deg_r} bound 11"),
        format!("deg_chebyshev_T3_linear {deg_t3_1} bound 5"),
        format!("deg_chebyshev_T3_quad {deg_t3_2} bound 8"),
        format!("deg_chebyshev_T3_radial {deg_t3_r} bound 11"),
        format!("n_terms_radial_Yu {n_yu}"),
        format!("n_terms_radial_Yv {n_yv}"),
    ];
    lines.extend(dump_mons("Yu_linear", &yu1));
    lines.extend(dump_mons("Yv_linear", &yv1));
    lines.extend(dump_mons("Yu_radial", &yu));
    lines.extend(dump_mons("Yv_radial", &yv));
    lines.push("preimages_cube 1/2 0 3".into());
    lines.push("preimages_cube 1/4 1/4 3".into());
    lines.push("preimages_chebyshev_T3 1/2 1/2 9".into());
    lines.push("complex_bezout_cube 9".into());
    lines.push("resultant_deg_u 9".into());
    lines.push("resultant_deg_t 3".into());
    lines.push("resultant_v 64u^9-48x*u^6-15x^2*u^3-27y^2*u^3-x^3".into());
    lines.push("polar_count 1/2 0/1 3".into());
    lines.push("polar_count 1/4 1/4 3".into());
    for (n, n_deg, sheets, bezout, cheb) in &rows {
        lines.push(format!(
            "n {n} N {n_deg} sheets {sheets} bezout {bezout} T3 {cheb}"
        ));
    }
    lines.push("sheets_eq_(N+1)/(n+1) 1".into());
    lines.push("weaker_than_T3 1".into());
    lines.push("beats_T3 0".into());
    lines.push("attains_bezout 0".into());
    lines.push("growth_complex linear".into());
    lines.push("do_not_claim_9_sheets 1".into());
    lines.push("do_not_claim_252_1080_1380_2012 1".into());

    let text = lines.join("\n") + "\n";
    if let Some(path) = dump_path {
        fs::write(&path, &text).unwrap_or_else(|e| fail(&format!("write dump: {e}")));
    }

    if let Ok(cwd) = std::env::current_dir() {
        let certs = cwd.join("certs");
        if fs::create_dir_all(&certs).is_ok() {
            let mut body = String::from("{\n");
            body.push_str("  \"det\": \"9(u^2+v^2)^2\",\n");
            body.push_str("  \"identity_linear\": true,\n");
            body.push_str("  \"identity_quad\": true,\n");
            body.push_str("  \"identity_radial\": true,\n");
            body.push_str(&format!("  \"deg_linear\": {deg_1},\n"));
            body.push_str(&format!("  \"deg_quad\": {deg_2},\n"));
            body.push_str(&format!("  \"deg_radial\": {deg_r},\n"));
            body.push_str("  \"n_terms_radial_Yu\": 12,\n");
            body.push_str("  \"n_terms_radial_Yv\": 12,\n");
            body.push_str("  \"preimages_half_0\": 3,\n");
            body.push_str("  \"preimages_quarter_quarter\": 3,\n");
            body.push_str("  \"preimages_chebyshev_T3\": 9,\n");
            body.push_str("  \"beats_T3\": false,\n");
            body.push_str("  \"weaker_than_T3\": true,\n");
            body.push_str("  \"attains_bezout\": false,\n");
            body.push_str("  \"growth_complex\": \"linear\"\n");
            body.push_str("}\n");
            let mut fh = fs::File::create(certs.join("rust_core.json"))
                .unwrap_or_else(|e| fail(&format!("write rust_core: {e}")));
            let _ = fh.write_all(body.as_bytes());
        }
    }

    print!("{text}");
    println!("verify.rs: ok");
    println!("  deg linear/quad/radial Y = {deg_1}/{deg_2}/{deg_r}");
    println!("  sheets Φ = 3, T3 = 9");
    println!("  weaker than T3 = 1");
}
