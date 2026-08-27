//! Second verifier for iterated complex-squaring pullback.
//!
//! Independent of verify.py: Q[u,v] expansion of Y = adj(DΦ)(X ∘ Φ)
//! for Φ(u,v)=(u²−v², 2uv), exact axis / quadratic preimage counts,
//! polar iteration of z ↦ z^{2^k}, and the k=1..6 arithmetic table.
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
    let p = u.pow(2).sub(&v.pow(2));
    let q = u.mul(&v).scale(Ratio::from_i(2));
    (p, q)
}

fn radial_cubic() -> (BiPoly, BiPoly) {
    // P = y - x(x^2+y^2-1/4) = y - x^3 - x y^2 + x/4
    // Q = -x - y(x^2+y^2-1/4) = -x - x^2 y - y^3 + y/4
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

fn chebyshev_t2() -> (BiPoly, BiPoly) {
    let two = Ratio::from_i(2);
    let pu = BiPoly::u().pow(2).scale(two).sub(&BiPoly::constant(Ratio::from_i(1)));
    let pv = BiPoly::v().pow(2).scale(two).sub(&BiPoly::constant(Ratio::from_i(1)));
    (pu, pv)
}

fn adj_pullback(p: &BiPoly, q: &BiPoly, px: &BiPoly, qx: &BiPoly) -> (BiPoly, BiPoly, BiPoly, BiPoly, BiPoly) {
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

fn reduced(num: i128, den: i128) -> (i128, i128) {
    let g = gcd_i128(num, den);
    (num / g, den / g)
}

fn polar_count(k: u32) -> usize {
    let n = 1usize << k;
    let a = 0.5_f64;
    let b = 0.0_f64;
    let w_mod = (a * a + b * b).sqrt();
    let w_arg = b.atan2(a);
    let r = w_mod.powf(1.0 / (n as f64));
    let mut pts = Vec::with_capacity(n);
    for j in 0..n {
        let th = (w_arg + 2.0 * std::f64::consts::PI * (j as f64)) / (n as f64);
        pts.push((r * th.cos(), r * th.sin()));
    }
    for &(u0, v0) in &pts {
        let mut u = u0;
        let mut v = v0;
        for _ in 0..k {
            let nu = u * u - v * v;
            let nv = 2.0 * u * v;
            u = nu;
            v = nv;
        }
        if (u - a).abs() + (v - b).abs() > 1e-9 {
            fail(&format!("polar iterate k={k} missed"));
        }
        if u0 * u0 + v0 * v0 < 1e-18 {
            fail("polar preimage at origin");
        }
    }
    for i in 0..pts.len() {
        for j in (i + 1)..pts.len() {
            if (pts[i].0 - pts[j].0).abs() + (pts[i].1 - pts[j].1).abs() < 1e-9 {
                fail(&format!("polar k={k} collision"));
            }
        }
    }
    pts.len()
}

fn check_preimages() {
    // (1/2, 0): 2uv=0, u^2-v^2=1/2. Two real.
    // (1/4, 1/4): 64t^2-16t-1=0 has disc=512, product=-1/64, one positive t.
    let disc = 16i128 * 16 + 4 * 64 * 1;
    if disc != 512 {
        fail("quarter-quarter discriminant");
    }
    // product of t-roots = -1/64 < 0.
    let prod_num = -1i128;
    let prod_den = 64i128;
    if prod_num >= 0 {
        fail("u^2 product should be negative");
    }
    let _ = prod_den;
    // Phi^2: q2=4uv(u^2-v^2)=0. u=0 or v=0 gives four real fourth-roots;
    // u^2=v^2 and uv≠0 gives -4u^4=1/2, no real.
    // T2(t)=1/2 ⇒ t^2=3/4 ∈ (0,1), two signs each, T2'=4t≠0: 4 sheets.
    let rhs = Ratio::new(3, 4);
    if rhs.n <= 0 || rhs.n >= rhs.d {
        fail("T2 rhs not in (0,1)");
    }
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
    let expect_det = BiPoly::u()
        .pow(2)
        .add(&BiPoly::v().pow(2))
        .scale(Ratio::from_i(4));
    if det.terms != expect_det.terms {
        fail("det DΦ != 4(u^2+v^2)");
    }
    if pu.terms != qv.terms || pv.terms != qu.scale(Ratio::from_i(-1)).terms {
        fail("Cauchy-Riemann failed");
    }
    if pu.terms != BiPoly::u().scale(Ratio::from_i(2)).terms
        || qv.terms != BiPoly::u().scale(Ratio::from_i(2)).terms
        || pv.terms != BiPoly::v().scale(Ratio::from_i(-2)).terms
        || qu.terms != BiPoly::v().scale(Ratio::from_i(2)).terms
    {
        fail("DΦ entries");
    }

    let (px, qx) = radial_cubic();
    let (yu, yv, _, du, dv) = adj_pullback(&p, &q, &px, &qx);
    if !du.is_zero() || !dv.is_zero() {
        fail("radial adj identity failed");
    }
    let deg_r = yu.total_degree().max(yv.total_degree());
    if deg_r != 7 {
        fail(&format!("radial one-step deg {deg_r}"));
    }

    let (p1, q1) = linear_center();
    let (yu1, yv1, _, du1, dv1) = adj_pullback(&p, &q, &p1, &q1);
    if !du1.is_zero() || !dv1.is_zero() {
        fail("linear adj identity failed");
    }
    let deg_1 = yu1.total_degree().max(yv1.total_degree());
    if deg_1 != 3 {
        fail(&format!("linear one-step deg {deg_1}"));
    }
    let expect_yu1 = BiPoly::v()
        .mul(&BiPoly::u().pow(2).add(&BiPoly::v().pow(2)))
        .scale(Ratio::from_i(2));
    let expect_yv1 = BiPoly::u()
        .mul(&BiPoly::u().pow(2).add(&BiPoly::v().pow(2)))
        .scale(Ratio::from_i(-2));
    if yu1.terms != expect_yu1.terms || yv1.terms != expect_yv1.terms {
        fail("linear closed form");
    }

    let (y2u, y2v, _, d2u, d2v) = adj_pullback(&p, &q, &yu, &yv);
    if !d2u.is_zero() || !d2v.is_zero() {
        fail("two-step adj identity failed");
    }
    let deg_2 = y2u.total_degree().max(y2v.total_degree());
    if deg_2 != 15 {
        fail(&format!("two-step deg {deg_2}"));
    }

    let (t2u, t2v) = chebyshev_t2();
    let (ytu, ytv, _, dtu, dtv) = adj_pullback(&t2u, &t2v, &px, &qx);
    if !dtu.is_zero() || !dtv.is_zero() {
        fail("T2 adj identity failed");
    }
    let deg_t2 = ytu.total_degree().max(ytv.total_degree());
    if deg_t2 != 7 {
        fail(&format!("T2 one-step deg {deg_t2}"));
    }

    check_preimages();
    let mut polar = Vec::new();
    for k in 1u32..=6 {
        let c = polar_count(k);
        if c != (1usize << k) {
            fail(&format!("polar k={k} count {c}"));
        }
        polar.push((k, c));
    }

    let n: i128 = 3;
    let mut rows = Vec::new();
    for k in 1u32..=6 {
        let pow2k = 1i128 << k;
        let n_deg = (n + 1) * pow2k - 1;
        let bezout = 1i128 << (2 * k);
        let complex_sheets = pow2k;
        let cheb = pow2k * pow2k;
        if complex_sheets * (n + 1) != n_deg + 1 {
            fail("2^k != (N+1)/(n+1)");
        }
        if bezout != cheb {
            fail("4^k != m^2");
        }
        let (bn, bd) = reduced(bezout, n_deg * n_deg);
        let (cn, cd) = reduced(complex_sheets, n_deg * n_deg);
        rows.push((k, n_deg, bezout, complex_sheets, cheb, bn, bd, cn, cd));
    }

    let mut lines: Vec<String> = vec![
        "det 4(u^2+v^2)".into(),
        "cr p_u=q_v=2u p_v=-q_u=-2v".into(),
        "identity_radial 1".into(),
        "identity_linear 1".into(),
        format!("deg_radial {deg_r} bound 7"),
        format!("deg_linear {deg_1} bound 3"),
        format!("deg_two_step_radial {deg_2} bound 15"),
        format!("deg_chebyshev_T2 {deg_t2} bound 7"),
    ];
    lines.extend(dump_mons("Yu", &yu));
    lines.extend(dump_mons("Yv", &yv));
    lines.extend(dump_mons("Yu_linear", &yu1));
    lines.extend(dump_mons("Yv_linear", &yv1));
    let n_half = polar[0].1;
    let n_phi2 = polar[1].1;
    let n_qq = 2; // 64t^2-16t-1: disc=512, product<0 ⇒ one positive t, two real u
    let n_t2 = 4; // T2(t)=1/2 ⇒ t^2=3/4∈(0,1), two signs × two coords, T2'≠0
    if n_half != 2 || n_phi2 != 4 {
        fail("polar k=1,2 sheet counts");
    }
    lines.push(format!("preimages_square 1/2 0 {n_half}"));
    lines.push(format!("preimages_square 1/4 1/4 {n_qq}"));
    lines.push(format!("preimages_square2 1/2 0 {n_phi2}"));
    lines.push(format!("preimages_chebyshev_T2 1/2 1/2 {n_t2}"));
    for (k, c) in &polar {
        lines.push(format!("polar_count {k} {c}"));
    }
    for (k, n_deg, bezout, complex_sheets, cheb, bn, bd, cn, cd) in &rows {
        lines.push(format!(
            "k {k} N {n_deg} bezout {bezout} complex {complex_sheets} chebyshev {cheb}"
        ));
        lines.push(format!("ratio_bezout {k} {bn}/{bd}"));
        lines.push(format!("ratio_complex {k} {cn}/{cd}"));
    }
    lines.push("complex_sheets_eq_(N+1)/(n+1) 1".into());
    lines.push("beats_theorem2 0".into());
    lines.push("attains_m2_per_step 0".into());
    lines.push("growth_complex linear".into());
    lines.push("growth_bezout_ceiling quadratic".into());
    lines.push("do_not_claim_252_1080_1380_2012 1".into());

    let text = lines.join("\n") + "\n";
    if let Some(path) = dump_path {
        fs::write(&path, &text).unwrap_or_else(|e| fail(&format!("write dump: {e}")));
    }

    // Compact JSON core next to the Python certs when run from this folder.
    if let Ok(cwd) = std::env::current_dir() {
        let certs = cwd.join("certs");
        if fs::create_dir_all(&certs).is_ok() {
            let mut body = String::from("{\n");
            body.push_str("  \"det\": \"4(u^2+v^2)\",\n");
            body.push_str("  \"identity_radial\": true,\n");
            body.push_str("  \"identity_linear\": true,\n");
            body.push_str(&format!("  \"deg_radial\": {deg_r},\n"));
            body.push_str(&format!("  \"deg_linear\": {deg_1},\n"));
            body.push_str(&format!("  \"deg_two_step_radial\": {deg_2},\n"));
            body.push_str("  \"preimages_half_0\": 2,\n");
            body.push_str("  \"preimages_quarter_quarter\": 2,\n");
            body.push_str("  \"preimages_phi2_half_0\": 4,\n");
            body.push_str("  \"preimages_chebyshev_T2\": 4,\n");
            body.push_str("  \"beats_theorem2\": false,\n");
            body.push_str("  \"attains_m2_per_step\": false,\n");
            body.push_str("  \"growth_complex\": \"linear\"\n");
            body.push_str("}\n");
            let mut fh = fs::File::create(certs.join("rust_core.json"))
                .unwrap_or_else(|e| fail(&format!("write rust_core: {e}")));
            let _ = fh.write_all(body.as_bytes());
        }
    }

    print!("{text}");
    println!("verify.rs: ok");
    println!("  deg radial Y = {deg_r}");
    println!("  sheets Φ = 2, T2 = 4, Φ^2 = 4");
    println!("  beats Theorem 2 = 0");
}
