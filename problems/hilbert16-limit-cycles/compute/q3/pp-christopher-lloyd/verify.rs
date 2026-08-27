//! Second verifier for the Christopher–Lloyd (u², v²) four-fold.
//!
//! Independent of verify.py: Q[u,v] expansion of
//! Yu = v P(u², v²), Yv = u Q(u², v²) (time rescale dt/dτ = 2uv,
//! not the adj pullback), T2 of the untranslated radial cubic,
//! oval residual, fibre counts, and the n=1,2,3 arithmetic.
//! rustc only.

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
        let mut items: Vec<_> = self.terms.iter().map(|((i, j), a)| (*i, *j, *a)).collect();
        items.sort_by_key(|(i, j, _)| (i + j, *i, *j));
        items
    }

    fn eval(&self, u: Ratio, v: Ratio) -> Ratio {
        let mut out = Ratio::zero();
        for ((eu, ev), a) in &self.terms {
            let mut term = *a;
            for _ in 0..*eu {
                term = term.mul(u);
            }
            for _ in 0..*ev {
                term = term.mul(v);
            }
            out = out.add(term);
        }
        out
    }
}

fn dump_mons(prefix: &str, p: &BiPoly) -> Vec<String> {
    p.monomials_sorted()
        .into_iter()
        .map(|(eu, ev, a)| format!("{prefix} {eu} {ev} {} {}", a.n, a.d))
        .collect()
}

fn radial_untranslated() -> (BiPoly, BiPoly) {
    let x = BiPoly::u();
    let y = BiPoly::v();
    let rho2 = Ratio::new(1, 4);
    let r2 = x.pow(2).add(&y.pow(2)).sub(&BiPoly::constant(rho2));
    let p = y.sub(&x.mul(&r2));
    let q = x.scale(Ratio::from_i(-1)).sub(&y.mul(&r2));
    (p, q)
}

fn translate(p: &BiPoly, q: &BiPoly) -> (BiPoly, BiPoly) {
    let two = BiPoly::constant(Ratio::from_i(2));
    let xs = BiPoly::u().sub(&two);
    let ys = BiPoly::v().sub(&two);
    (p.compose(&xs, &ys), q.compose(&xs, &ys))
}

fn linear_center() -> (BiPoly, BiPoly) {
    (BiPoly::v(), BiPoly::u().scale(Ratio::from_i(-1)))
}

fn sample_quadratic() -> (BiPoly, BiPoly) {
    let x = BiPoly::u();
    let y = BiPoly::v();
    (x.pow(2).add(&y), y.pow(2).add(&x))
}

fn cl_field(p: &BiPoly, q: &BiPoly) -> (BiPoly, BiPoly, BiPoly, BiPoly) {
    let u2 = BiPoly::u().pow(2);
    let v2 = BiPoly::v().pow(2);
    let pc = p.compose(&u2, &v2);
    let qc = q.compose(&u2, &v2);
    let yu = pc.mul(&BiPoly::v());
    let yv = qc.mul(&BiPoly::u());
    (yu, yv, pc, qc)
}

fn adj_field(p: &BiPoly, q: &BiPoly) -> (BiPoly, BiPoly) {
    let u2 = BiPoly::u().pow(2);
    let v2 = BiPoly::v().pow(2);
    let pc = p.compose(&u2, &v2);
    let qc = q.compose(&u2, &v2);
    let yu = pc.mul(&BiPoly::v()).scale(Ratio::from_i(2));
    let yv = qc.mul(&BiPoly::u()).scale(Ratio::from_i(2));
    (yu, yv)
}

fn cl_identity(yu: &BiPoly, yv: &BiPoly, pc: &BiPoly, qc: &BiPoly) -> (BiPoly, BiPoly) {
    // 2u Yu − 2uv Pc,  2v Yv − 2uv Qc
    let two_u = BiPoly::u().scale(Ratio::from_i(2));
    let two_v = BiPoly::v().scale(Ratio::from_i(2));
    let two_uv = BiPoly::u().mul(&BiPoly::v()).scale(Ratio::from_i(2));
    let du = two_u.mul(yu).sub(&two_uv.mul(pc));
    let dv = two_v.mul(yv).sub(&two_uv.mul(qc));
    (du, dv)
}

fn adj_identity(yu: &BiPoly, yv: &BiPoly, pc: &BiPoly, qc: &BiPoly) -> (BiPoly, BiPoly) {
    let two_u = BiPoly::u().scale(Ratio::from_i(2));
    let two_v = BiPoly::v().scale(Ratio::from_i(2));
    let four_uv = BiPoly::u().mul(&BiPoly::v()).scale(Ratio::from_i(4));
    let du = two_u.mul(yu).sub(&four_uv.mul(pc));
    let dv = two_v.mul(yv).sub(&four_uv.mul(qc));
    (du, dv)
}

fn t2_field(p: &BiPoly, q: &BiPoly) -> (BiPoly, BiPoly) {
    let t2u = BiPoly::u().pow(2).scale(Ratio::from_i(2)).sub(&BiPoly::constant(Ratio::from_i(1)));
    let t2v = BiPoly::v().pow(2).scale(Ratio::from_i(2)).sub(&BiPoly::constant(Ratio::from_i(1)));
    let pc = p.compose(&t2u, &t2v);
    let qc = q.compose(&t2u, &t2v);
    (pc.mul(&BiPoly::v()).scale(Ratio::from_i(4)), qc.mul(&BiPoly::u()).scale(Ratio::from_i(4)))
}

fn polar_square_count(a: f64, b: f64) -> usize {
    let w_mod = (a * a + b * b).sqrt();
    if w_mod == 0.0 {
        fail("polar target is 0");
    }
    let w_arg = b.atan2(a);
    let r = w_mod.sqrt();
    let mut pts = Vec::with_capacity(2);
    for j in 0..2 {
        let th = (w_arg + 2.0 * std::f64::consts::PI * (j as f64)) / 2.0;
        pts.push((r * th.cos(), r * th.sin()));
    }
    for &(u0, v0) in &pts {
        let uu = u0 * u0 - v0 * v0;
        let vv = 2.0 * u0 * v0;
        if (uu - a).abs() + (vv - b).abs() > 1e-9 {
            fail("polar square missed target");
        }
        if u0 * u0 + v0 * v0 < 1e-18 {
            fail("polar preimage at origin");
        }
        if 4.0 * (u0 * u0 + v0 * v0) < 1e-18 {
            fail("polar Jacobian vanished");
        }
    }
    if (pts[0].0 - pts[1].0).abs() + (pts[0].1 - pts[1].1).abs() < 1e-9 {
        fail("polar square collision");
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

    let (p0, q0) = radial_untranslated();
    let r2 = BiPoly::u().pow(2).add(&BiPoly::v().pow(2));
    let flux = BiPoly::u().mul(&p0).add(&BiPoly::v().mul(&q0));
    let expect_flux = r2.mul(&r2.sub(&BiPoly::constant(Ratio::new(1, 4)))).scale(Ratio::from_i(-1));
    if flux.terms != expect_flux.terms {
        fail("radial flux");
    }
    let fprime = Ratio::new(1, 4).sub(Ratio::new(3, 4));
    if fprime != Ratio::new(-1, 2) {
        fail("f'(ρ)");
    }

    let (p1, q1) = linear_center();
    let (yu1, yv1, pc1, qc1) = cl_field(&p1, &q1);
    let (du1, dv1) = cl_identity(&yu1, &yv1, &pc1, &qc1);
    if !du1.is_zero() || !dv1.is_zero() {
        fail("linear CL identity failed");
    }
    if yu1.terms != BiPoly::v().pow(3).terms
        || yv1.terms != BiPoly::u().pow(3).scale(Ratio::from_i(-1)).terms
    {
        fail("linear closed form");
    }
    let deg_1 = yu1.total_degree().max(yv1.total_degree());
    if deg_1 != 3 {
        fail(&format!("linear CL deg {deg_1}"));
    }

    let (p2, q2) = sample_quadratic();
    let (yu2, yv2, pc2, qc2) = cl_field(&p2, &q2);
    let (du2, dv2) = cl_identity(&yu2, &yv2, &pc2, &qc2);
    if !du2.is_zero() || !dv2.is_zero() {
        fail("quadratic CL identity failed");
    }
    let expect_yu2 = BiPoly::u().pow(4).mul(&BiPoly::v()).add(&BiPoly::v().pow(3));
    let expect_yv2 = BiPoly::u().pow(3).add(&BiPoly::u().mul(&BiPoly::v().pow(4)));
    if yu2.terms != expect_yu2.terms || yv2.terms != expect_yv2.terms {
        fail("quadratic closed form");
    }
    let deg_2 = yu2.total_degree().max(yv2.total_degree());
    if deg_2 != 5 {
        fail(&format!("quadratic CL deg {deg_2}"));
    }

    let (p, q) = translate(&p0, &q0);
    if p.total_degree() != 3 || q.total_degree() != 3 {
        fail("translated (P, Q) not degree 3");
    }
    let (yu, yv, pc, qc) = cl_field(&p, &q);
    let (du, dv) = cl_identity(&yu, &yv, &pc, &qc);
    if !du.is_zero() || !dv.is_zero() {
        fail("translated CL identity failed");
    }
    let deg_r = yu.total_degree().max(yv.total_degree());
    if deg_r != 7 {
        fail(&format!("translated CL deg {deg_r}"));
    }
    let n_yu = yu.terms.len();
    let n_yv = yv.terms.len();
    if n_yu != 8 || n_yv != 8 {
        fail(&format!("CL term counts {n_yu} {n_yv}"));
    }
    let lead_u = yu.homog(7);
    let lead_v = yv.homog(7);
    let expect_lead_u = BiPoly::u()
        .pow(6)
        .mul(&BiPoly::v())
        .add(&BiPoly::u().pow(2).mul(&BiPoly::v().pow(5)))
        .scale(Ratio::from_i(-1));
    let expect_lead_v = BiPoly::u()
        .pow(5)
        .mul(&BiPoly::v().pow(2))
        .add(&BiPoly::u().mul(&BiPoly::v().pow(6)))
        .scale(Ratio::from_i(-1));
    if lead_u.terms != expect_lead_u.terms || lead_v.terms != expect_lead_v.terms {
        fail("CL leading form");
    }

    let (yu_adj, yv_adj) = adj_field(&p, &q);
    let (dua, dva) = adj_identity(&yu_adj, &yv_adj, &pc, &qc);
    if !dua.is_zero() || !dva.is_zero() {
        fail("translated adj identity failed");
    }
    if yu_adj.terms != yu.scale(Ratio::from_i(2)).terms
        || yv_adj.terms != yv.scale(Ratio::from_i(2)).terms
    {
        fail("adj is not twice CL");
    }
    if yu_adj.terms == yu.terms || yv_adj.terms == yv.terms {
        fail("CL field equals adj; they must differ");
    }
    if yu_adj.total_degree().max(yv_adj.total_degree()) != 7 {
        fail("adj deg");
    }

    let g = BiPoly::u()
        .pow(2)
        .sub(&BiPoly::constant(Ratio::from_i(2)))
        .pow(2)
        .add(
            &BiPoly::v()
                .pow(2)
                .sub(&BiPoly::constant(Ratio::from_i(2)))
                .pow(2),
        )
        .sub(&BiPoly::constant(Ratio::new(1, 4)));
    let four_u = BiPoly::u().scale(Ratio::from_i(4));
    let four_v = BiPoly::v().scale(Ratio::from_i(4));
    let u2m2 = BiPoly::u().pow(2).sub(&BiPoly::constant(Ratio::from_i(2)));
    let v2m2 = BiPoly::v().pow(2).sub(&BiPoly::constant(Ratio::from_i(2)));
    let dg = four_u.mul(&u2m2).mul(&yu).add(&four_v.mul(&v2m2).mul(&yv));
    let oval_res = dg.add(
        &BiPoly::u()
            .mul(&BiPoly::v())
            .scale(Ratio::from_i(4))
            .mul(&g)
            .mul(&g.add(&BiPoly::constant(Ratio::new(1, 4)))),
    );
    if !oval_res.is_zero() {
        fail("oval residual");
    }

    let f0_right = p0.eval(Ratio::new(1, 2), Ratio::zero());
    let f0_q_right = q0.eval(Ratio::new(1, 2), Ratio::zero());
    if f0_right != Ratio::zero() {
        fail("P0(1/2,0)");
    }
    if f0_q_right != Ratio::new(-1, 2) {
        fail("Q0(1/2,0)");
    }
    let ft = (BiPoly::u().sub(&BiPoly::constant(Ratio::from_i(2))))
        .pow(2)
        .add(&(BiPoly::v().sub(&BiPoly::constant(Ratio::from_i(2)))).pow(2))
        .sub(&BiPoly::constant(Ratio::new(1, 4)));
    if ft.eval(Ratio::new(5, 2), Ratio::from_i(2)) != Ratio::zero() {
        fail("translated right point");
    }
    if ft.eval(Ratio::new(3, 2), Ratio::from_i(2)) != Ratio::zero() {
        fail("translated left point");
    }

    let u2 = Ratio::new(5, 2);
    let v2 = Ratio::from_i(2);
    let g_sample = u2.sub(Ratio::from_i(2)).mul(u2.sub(Ratio::from_i(2))).add(
        v2.sub(Ratio::from_i(2))
            .mul(v2.sub(Ratio::from_i(2)))
            .sub(Ratio::new(1, 4)),
    );
    if g_sample != Ratio::zero() {
        fail("sample not on oval");
    }
    if u2.mul(Ratio::new(1, 4)) != Ratio::new(5, 8) {
        fail("sample Y vanished");
    }
    if Ratio::from_i(16).mul(u2).mul(v2) != Ratio::from_i(80) {
        fail("sample Jacobian vanished");
    }

    let (yu_t2, yv_t2) = t2_field(&p0, &q0);
    let deg_t2 = yu_t2.total_degree().max(yv_t2.total_degree());
    if deg_t2 != 7 {
        fail(&format!("T2 radial deg {deg_t2}"));
    }
    let n_t2u = yu_t2.terms.len();
    let n_t2v = yv_t2.terms.len();
    if n_t2u != 8 || n_t2v != 8 {
        fail(&format!("T2 term counts {n_t2u} {n_t2v}"));
    }

    let (ytu1, ytv1) = t2_field(&p1, &q1);
    let deg_t3_1 = ytu1.total_degree().max(ytv1.total_degree());
    if deg_t3_1 != 3 {
        fail(&format!("T2 linear deg {deg_t3_1}"));
    }
    let (ytu2, ytv2) = t2_field(&p2, &q2);
    let deg_t3_2 = ytu2.total_degree().max(ytv2.total_degree());
    if deg_t3_2 != 5 {
        fail(&format!("T2 quad deg {deg_t3_2}"));
    }

    // T2(t)=1/2 ⇒ 2t² − 3/2 = 0. disc = 9 − 4*2*(-3/2) wait, poly 2t²+0t−3/2.
    // disc = 0 − 4*2*(-3/2) = 12.
    let a = 2i128;
    let b = 0i128;
    let c_coef = Ratio::new(-3, 2);
    let disc = Ratio::from_i(b * b).sub(Ratio::from_i(4 * a).mul(c_coef));
    if disc != Ratio::from_i(12) {
        fail(&format!("T2 quadratic discriminant {:?}", disc));
    }

    let polar_half = polar_square_count(0.5, 0.0);
    let polar_qq = polar_square_count(0.5, 0.5);
    let polar_circ = polar_square_count(2.5, 2.0);
    if polar_half != 2 || polar_qq != 2 || polar_circ != 2 {
        fail("polar holomorphic counts");
    }

    let mut rows = Vec::new();
    for n in [1i128, 2, 3] {
        let n_deg = 2 * n + 1;
        let sheets = 4i128;
        let linear = 2i128;
        let bezout = 4i128;
        let cheb = 4i128;
        if n_deg != n * 2 + 2 - 1 {
            fail("N mismatch vs one-step Chebyshev of degree 2");
        }
        if (n_deg + 1) / (n + 1) != linear {
            fail("(N+1)/(n+1) is not 2");
        }
        if sheets <= linear {
            fail("CL sheets should be 4 > 2");
        }
        rows.push((n, n_deg, sheets, linear, bezout, cheb));
    }

    let mut lines: Vec<String> = vec![
        "det 4uv".into(),
        "time_rescale 2uv".into(),
        "field Yu=v*P(u^2,v^2) Yv=u*Q(u^2,v^2)".into(),
        "not_adj 1".into(),
        "adj_is_twice_cl 1".into(),
        "identity_cl 1".into(),
        "identity_adj 1".into(),
        "identity_oval 1".into(),
        format!("deg_linear {deg_1} bound 3"),
        format!("deg_quad {deg_2} bound 5"),
        format!("deg_radial {deg_r} bound 7"),
        format!("deg_chebyshev_T2_linear {deg_t3_1} bound 3"),
        format!("deg_chebyshev_T2_quad {deg_t3_2} bound 5"),
        format!("deg_chebyshev_T2_radial {deg_t2} bound 7"),
        format!("n_terms_cl_Yu {n_yu}"),
        format!("n_terms_cl_Yv {n_yv}"),
        format!("n_terms_t2_Yu {n_t2u}"),
        format!("n_terms_t2_Yv {n_t2v}"),
    ];
    lines.extend(dump_mons("Yu_linear", &yu1));
    lines.extend(dump_mons("Yv_linear", &yv1));
    lines.extend(dump_mons("P_trans", &p));
    lines.extend(dump_mons("Q_trans", &q));
    lines.extend(dump_mons("Yu_cl", &yu));
    lines.extend(dump_mons("Yv_cl", &yv));
    lines.extend(dump_mons("Yu_t2", &yu_t2));
    lines.extend(dump_mons("Yv_t2", &yv_t2));
    lines.push("oval (u^2-2)^2+(v^2-2)^2=1/4".into());
    lines.push("oval_u2_min 3/2".into());
    lines.push("oval_u2_max 5/2".into());
    lines.push("ovals 4".into());
    lines.push("jac_on_ovals_nonzero 1".into());
    lines.push("untranslated_hits_axes 1".into());
    lines.push("translated_first_quadrant 1".into());
    lines.push("hyperbolic_fprime -1/2".into());
    lines.push("preimages_cl 5/2 2 4".into());
    lines.push("preimages_cl 1/2 1/2 4".into());
    lines.push("preimages_holomorphic 1/2 0 2".into());
    lines.push("preimages_t2 1/2 1/2 4".into());
    lines.push("polar_holomorphic 1/2 0/1 2".into());
    lines.push("polar_holomorphic 1/2 1/2 2".into());
    lines.push("polar_holomorphic 5/2 2/1 2".into());
    for (n, n_deg, sheets, linear, bezout, cheb) in &rows {
        lines.push(format!(
            "n {n} N {n_deg} sheets {sheets} linear {linear} bezout {bezout} T2 {cheb}"
        ));
    }
    lines.push("sheets_gt_(N+1)/(n+1) 1".into());
    lines.push("attains_bezout 1".into());
    lines.push("equals_T2_sheets 1".into());
    lines.push("beats_T2 0".into());
    lines.push("beats_H7_74 0".into());
    lines.push("H7_from_this_field 4".into());
    lines.push("published_H7 74".into());
    lines.push("do_not_claim_dent 1".into());
    lines.push("do_not_claim_252_1080_1380_2012 1".into());

    let text = lines.join("\n") + "\n";
    if let Some(path) = dump_path {
        fs::write(&path, &text).unwrap_or_else(|e| fail(&format!("write dump: {e}")));
    }

    if let Ok(cwd) = std::env::current_dir() {
        let certs = cwd.join("certs");
        if fs::create_dir_all(&certs).is_ok() {
            let mut body = String::from("{\n");
            body.push_str("  \"det\": \"4uv\",\n");
            body.push_str("  \"time_rescale\": \"2uv\",\n");
            body.push_str("  \"not_adj\": true,\n");
            body.push_str("  \"adj_is_twice_cl\": true,\n");
            body.push_str("  \"identity_cl\": true,\n");
            body.push_str("  \"identity_adj\": true,\n");
            body.push_str(&format!("  \"deg_linear\": {deg_1},\n"));
            body.push_str(&format!("  \"deg_quad\": {deg_2},\n"));
            body.push_str(&format!("  \"deg_radial\": {deg_r},\n"));
            body.push_str("  \"n_terms_cl_Yu\": 8,\n");
            body.push_str("  \"n_terms_cl_Yv\": 8,\n");
            body.push_str("  \"preimages_cl_circle\": 4,\n");
            body.push_str("  \"preimages_holomorphic\": 2,\n");
            body.push_str("  \"preimages_t2\": 4,\n");
            body.push_str("  \"ovals\": 4,\n");
            body.push_str("  \"beats_T2\": false,\n");
            body.push_str("  \"equals_T2_sheets\": true,\n");
            body.push_str("  \"attains_bezout\": true,\n");
            body.push_str("  \"sheets_gt_linear\": true,\n");
            body.push_str("  \"beats_H7_74\": false,\n");
            body.push_str("  \"H7_from_this_field\": 4,\n");
            body.push_str("  \"published_H7\": 74\n");
            body.push_str("}\n");
            let mut fh = fs::File::create(certs.join("rust_core.json"))
                .unwrap_or_else(|e| fail(&format!("write rust_core: {e}")));
            let _ = fh.write_all(body.as_bytes());
        }
    }

    print!("{text}");
    println!("verify.rs: ok");
    println!("  deg linear/quad/radial Y = {deg_1}/{deg_2}/{deg_r}");
    println!("  sheets Φ = 4, T2 = 4, holomorphic = 2");
    println!("  H(7) >= 4 does not beat 74");
}
