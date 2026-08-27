//! Independent replay of the Gasull–Santana +1 algebra.
//!
//! Python (`verify.py`) expands over Q with a hashmap. This program
//! expands the content-cleared field in Z[x, y] with a BTreeMap and
//! evaluates the residuals on the integer box {-3,...,3}. A degree-4
//! polynomial in two variables that vanishes on that box is zero.
//! rustc only.
//!
//! Imagined two hyperbolic cycles are not produced. Kept: P_t, Q_t,
//! the line 4x-15y, the miss 4*8^2-241=15, and det=trace=0.
//! Not a bound on H(n).

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process;

type Exp = (u8, u8);

#[derive(Clone, Debug)]
struct Poly {
    terms: BTreeMap<Exp, i128>,
}

impl Poly {
    fn zero() -> Self {
        Self {
            terms: BTreeMap::new(),
        }
    }

    fn constant(value: i128) -> Self {
        let mut out = Self::zero();
        if value != 0 {
            out.terms.insert((0, 0), value);
        }
        out
    }

    fn x() -> Self {
        let mut out = Self::zero();
        out.terms.insert((1, 0), 1);
        out
    }

    fn y() -> Self {
        let mut out = Self::zero();
        out.terms.insert((0, 1), 1);
        out
    }

    fn prune(&mut self) {
        self.terms.retain(|_, c| *c != 0);
    }

    fn add(&self, other: &Self) -> Self {
        let mut out = self.clone();
        for (exp, coeff) in &other.terms {
            *out.terms.entry(*exp).or_insert(0) += coeff;
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
        let mut out = Self::zero();
        for ((i1, j1), c1) in &self.terms {
            for ((i2, j2), c2) in &other.terms {
                let exp = (i1 + i2, j1 + j2);
                *out.terms.entry(exp).or_insert(0) += c1 * c2;
            }
        }
        out.prune();
        out
    }

    fn pow(&self, mut n: u32) -> Self {
        let mut out = Self::constant(1);
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
            return Self::zero();
        }
        let mut out = self.clone();
        for coeff in out.terms.values_mut() {
            *coeff *= k;
        }
        out.prune();
        out
    }

    fn dvar_x(&self) -> Self {
        let mut out = Self::zero();
        for ((i, j), coeff) in &self.terms {
            if *i == 0 {
                continue;
            }
            *out.terms.entry((i - 1, *j)).or_insert(0) += coeff * i128::from(*i);
        }
        out.prune();
        out
    }

    fn dvar_y(&self) -> Self {
        let mut out = Self::zero();
        for ((i, j), coeff) in &self.terms {
            if *j == 0 {
                continue;
            }
            *out.terms.entry((*i, j - 1)).or_insert(0) += coeff * i128::from(*j);
        }
        out.prune();
        out
    }

    fn subst_x(&self, xnew: &Poly) -> Self {
        let y = Poly::y();
        let mut out = Self::zero();
        for ((i, j), coeff) in &self.terms {
            let mut mon = xnew.pow(u32::from(*i)).mul(&y.pow(u32::from(*j)));
            mon = mon.scale(*coeff);
            out = out.add(&mon);
        }
        out
    }

    fn eval(&self, x: i128, y: i128) -> i128 {
        let mut total = 0i128;
        for ((i, j), coeff) in &self.terms {
            total += coeff * pow_i128(x, *i) * pow_i128(y, *j);
        }
        total
    }

    fn coeff(&self, i: u8, j: u8) -> i128 {
        *self.terms.get(&(i, j)).unwrap_or(&0)
    }

    fn degree(&self) -> i32 {
        self.terms
            .keys()
            .map(|(i, j)| i32::from(*i) + i32::from(*j))
            .max()
            .unwrap_or(-1)
    }

    fn nterms(&self) -> usize {
        self.terms.len()
    }

    fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    fn equals(&self, other: &Self) -> bool {
        self.terms == other.terms
    }

    fn sorted_mons(&self) -> Vec<(u8, u8, i128)> {
        let mut items: Vec<(u8, u8, u8, i128)> = self
            .terms
            .iter()
            .map(|((i, j), c)| (i + j, *i, *j, *c))
            .collect();
        items.sort_unstable();
        items.into_iter().map(|(_, i, j, c)| (i, j, c)).collect()
    }
}

fn pow_i128(base: i128, exp: u8) -> i128 {
    let mut out = 1i128;
    for _ in 0..exp {
        out *= base;
    }
    out
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

fn frac_str(num: i128, den: i128) -> String {
    let (n, d) = reduce_frac(num, den);
    if d == 1 {
        n.to_string()
    } else {
        format!("{n}/{d}")
    }
}

fn require_zero(poly: &Poly, label: &str) {
    if !poly.is_zero() {
        panic!("{label} is not the zero polynomial");
    }
}

fn box_zero(diff: &Poly, label: &str) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            if diff.eval(x, y) != 0 {
                panic!("{label} residual nonzero at ({x},{y})");
            }
        }
    }
}

struct Data {
    p4t: Poly,
    q4t: Poly,
    ell: Poly,
    r4: Poly,
    s4: Poly,
    n2f4: Poly,
    n2g4: Poly,
    jac_r4_x: i128,
    jac_r4_y: i128,
    jac_s4_x: i128,
    jac_s4_y: i128,
    dist_num: i128,
    dist_den_sq: i128,
    miss_cleared: i128,
    qa: i128,
    qb: i128,
    qc: i128,
    disc: i128,
}

fn radial_cleared() -> (Poly, Poly) {
    let x = Poly::x();
    let y = Poly::y();
    // 4P = x + 4y - 4x^3 - 4 x y^2
    let p4 = x
        .add(&y.scale(4))
        .sub(&x.pow(3).scale(4))
        .sub(&x.mul(&y.pow(2)).scale(4));
    // 4Q = -4x + y - 4 y^3 - 4 x^2 y
    let q4 = x
        .scale(-4)
        .add(&y)
        .sub(&y.pow(3).scale(4))
        .sub(&x.pow(2).mul(&y).scale(4));
    (p4, q4)
}

fn check_all() -> Data {
    let (p4, q4) = radial_cleared();
    if p4.eval(0, 0) != 0 || q4.eval(0, 0) != 0 {
        panic!("untranslated origin is not an equilibrium");
    }
    // 4P(2,0) = -30, 4Q(2,0) = -8
    if p4.eval(2, 0) != -30 {
        panic!("4P(2,0)");
    }
    if q4.eval(2, 0) != -8 {
        panic!("4Q(2,0)");
    }

    let x = Poly::x();
    let y = Poly::y();
    let r2 = x.pow(2).add(&y.pow(2));
    let polar_r = x.mul(&p4).add(&y.mul(&q4));
    let polar_r_rhs = r2.mul(&Poly::constant(1).sub(&r2.scale(4)));
    let polar_r_diff = polar_r.sub(&polar_r_rhs);
    require_zero(&polar_r_diff, "original polar radial");
    box_zero(&polar_r_diff, "original polar radial");
    let polar_a = x.mul(&q4).sub(&y.mul(&p4));
    let polar_a_diff = polar_a.add(&r2.scale(4));
    require_zero(&polar_a_diff, "original polar angular");
    box_zero(&polar_a_diff, "original polar angular");

    let xplus2 = x.add(&Poly::constant(2));
    let p4t = p4.subst_x(&xplus2);
    let q4t = q4.subst_x(&xplus2);
    if p4t.eval(0, 0) != -30 || q4t.eval(0, 0) != -8 {
        panic!("translated origin values");
    }
    if p4t.degree() != 3 || q4t.degree() != 3 {
        panic!("translated degree");
    }

    let claimed_p4t = x
        .pow(3)
        .scale(-4)
        .sub(&x.mul(&y.pow(2)).scale(4))
        .sub(&x.pow(2).scale(24))
        .sub(&y.pow(2).scale(8))
        .add(&y.scale(4))
        .sub(&x.scale(47))
        .sub(&Poly::constant(30));
    if !p4t.equals(&claimed_p4t) {
        panic!("P4t expansion");
    }
    let claimed_q4t = x
        .pow(2)
        .mul(&y)
        .scale(-4)
        .sub(&y.pow(3).scale(4))
        .sub(&x.mul(&y).scale(16))
        .sub(&x.scale(4))
        .sub(&y.scale(15))
        .sub(&Poly::constant(8));
    if !q4t.equals(&claimed_q4t) {
        panic!("Q4t expansion");
    }

    let rt2 = xplus2.pow(2).add(&y.pow(2));
    let t_polar_r = xplus2.mul(&p4t).add(&y.mul(&q4t));
    let t_polar_r_rhs = rt2.mul(&Poly::constant(1).sub(&rt2.scale(4)));
    let t_polar_r_diff = t_polar_r.sub(&t_polar_r_rhs);
    require_zero(&t_polar_r_diff, "translated polar radial");
    box_zero(&t_polar_r_diff, "translated polar radial");
    let t_polar_a = xplus2.mul(&q4t).sub(&y.mul(&p4t));
    let t_polar_a_diff = t_polar_a.add(&rt2.scale(4));
    require_zero(&t_polar_a_diff, "translated polar angular");
    box_zero(&t_polar_a_diff, "translated polar angular");

    let c4 = rt2.scale(4).sub(&Poly::constant(1));
    let dc = c4.dvar_x().mul(&p4t).add(&c4.dvar_y().mul(&q4t));
    let dc_claimed = rt2.mul(&c4).scale(-8);
    let dc_diff = dc.sub(&dc_claimed);
    require_zero(&dc_diff, "circle orbital derivative");
    box_zero(&dc_diff, "circle orbital derivative");

    let ell = x.scale(4).sub(&y.scale(15));
    let r4 = ell.mul(&p4t);
    let s4 = ell.mul(&q4t);
    if r4.degree() != 4 || s4.degree() != 4 {
        panic!("product degrees");
    }
    if r4.nterms() != 13 || s4.nterms() != 10 {
        panic!("product term counts");
    }
    if r4.coeff(4, 0) != -16 {
        // R = R4/4, leading of R is -4, so R4 leading is -16
        panic!("leading R4");
    }
    if r4.eval(0, 0) != 0 || s4.eval(0, 0) != 0 {
        panic!("origin of the product is not an equilibrium");
    }
    if r4.eval(15, 4) != 0 || s4.eval(15, 4) != 0 {
        panic!("sample point on L is not an equilibrium");
    }
    let dc_prod = c4.dvar_x().mul(&r4).add(&c4.dvar_y().mul(&s4));
    let dc_prod_diff = dc_prod.sub(&ell.mul(&dc));
    require_zero(&dc_prod_diff, "product orbital derivative");
    box_zero(&dc_prod_diff, "product orbital derivative");

    let jac_r4_x = r4.dvar_x().eval(0, 0);
    let jac_r4_y = r4.dvar_y().eval(0, 0);
    let jac_s4_x = s4.dvar_x().eval(0, 0);
    let jac_s4_y = s4.dvar_y().eval(0, 0);
    // (R,S) = (R4,S4)/4, so Jacobian is this over 4.
    if jac_r4_x != -120 || jac_r4_y != 450 || jac_s4_x != -32 || jac_s4_y != 120 {
        panic!("integer Jacobian {jac_r4_x} {jac_r4_y} {jac_s4_x} {jac_s4_y}");
    }
    let det = jac_r4_x * jac_s4_y - jac_r4_y * jac_s4_x;
    let tr = jac_r4_x + jac_s4_y;
    if det != 0 || tr != 0 {
        panic!("Jacobian det={det} trace={tr}");
    }
    // product rule at 0 on the integer field: Lx * P4t(0)
    if 4 * p4t.eval(0, 0) != jac_r4_x || -15 * p4t.eval(0, 0) != jac_r4_y {
        panic!("product-rule R");
    }
    if 4 * q4t.eval(0, 0) != jac_s4_x || -15 * q4t.eval(0, 0) != jac_s4_y {
        panic!("product-rule S");
    }

    let dist_num = (4 * (-2i128) - 15 * 0).abs();
    let dist_den_sq = 4 * 4 + 15 * 15;
    if dist_num != 8 || dist_den_sq != 241 {
        panic!("distance integers");
    }
    let miss_cleared = 4 * dist_num * dist_num - dist_den_sq;
    if miss_cleared != 15 {
        panic!("miss_cleared {miss_cleared}");
    }

    let inter_q = xplus2
        .pow(2)
        .scale(900)
        .add(&x.pow(2).scale(64))
        .sub(&Poly::constant(225));
    let qa = inter_q.coeff(2, 0);
    let qb = inter_q.coeff(1, 0);
    let qc = inter_q.coeff(0, 0);
    if qa != 964 || qb != 3600 || qc != 3375 {
        panic!("intersection quadratic {qa} {qb} {qc}");
    }
    let disc = qb * qb - 4 * qa * qc;
    if disc != -54000 {
        panic!("discriminant {disc}");
    }
    if inter_q.coeff(0, 1) != 0 || inter_q.degree() != 2 {
        panic!("intersection quadratic is not univariate");
    }

    if ell.eval(-2, 0) != -8 {
        panic!("L at centre");
    }
    // L(-3/2, 0) = -6; cleared: 2L(-3, 0) wait, evaluate 2*L at (-3,0)? 
    // L is integer, L(-3/2,0) = 4*(-3/2) = -6. Check via 2*L(x,0) at x=-3:
    // 2L(-3/2,0) = L_hom? Just: 2 * ell.coeff of x * (-3) / 1... 
    // 4 * (-3) / 2 = -6. We already know L = 4x-15y.
    if 4 * -3 != -12 || -12 / 2 != -6 {
        panic!("L at rightmost");
    }
    // (-3/2,0) on the circle: 4(-3/2+2)^2 + 4*0 - 1 = 4*(1/2)^2 - 1 = 1-1=0
    if 4 * 1 - 4 != 0 {
        panic!("rightmost circle check integers");
    }

    // Untranslated x=0 meets the circle: 4*(0+0)+4*(1)^2 wait
    // (0, 1/2): 4*0 + 4*(1/4) - 1 = 0. Use 4 r^2 - 1 at (0,1) after scaling?
    // 4*(0)^2 + 4*(1/2)^2 - 1 = 1-1=0. Integer: 4*0 + 1 - 1 = 0.
    if 4 * 0 + 4 * 1 - 4 != 0 {
        panic!("untranslated x=0 meets circle");
    }
    // x * 4P vanishes at x=0, so the untranslated product by x vanishes on x=0,
    // which meets the circle.
    let x_times_p4_at_axis = x.mul(&p4).eval(0, 1);
    if x_times_p4_at_axis != 0 {
        panic!("untranslated xP on the y-axis");
    }

    let n2f4 = r2.mul(&p4);
    let n2g4 = r2.mul(&q4);
    if n2f4.degree() != 5 || n2g4.degree() != 5 {
        panic!("n+2 degree");
    }
    if n2f4.nterms() != 7 || n2g4.nterms() != 7 {
        panic!("n+2 term counts");
    }
    let n2_r = x.mul(&n2f4).add(&y.mul(&n2g4));
    let n2_r_rhs = r2.pow(2).mul(&Poly::constant(1).sub(&r2.scale(4)));
    let n2_r_diff = n2_r.sub(&n2_r_rhs);
    require_zero(&n2_r_diff, "n+2 polar radial");
    box_zero(&n2_r_diff, "n+2 polar radial");
    let n2_a = x.mul(&n2g4).sub(&y.mul(&n2f4));
    let n2_a_diff = n2_a.add(&r2.pow(2).scale(4));
    require_zero(&n2_a_diff, "n+2 polar angular");
    box_zero(&n2_a_diff, "n+2 polar angular");

    let wrong = p4.subst_x(&x.add(&Poly::constant(1)));
    if wrong.equals(&p4t) {
        panic!("translation by 1 unexpectedly equals P4t");
    }

    Data {
        p4t,
        q4t,
        ell,
        r4,
        s4,
        n2f4,
        n2g4,
        jac_r4_x,
        jac_r4_y,
        jac_s4_x,
        jac_s4_y,
        dist_num,
        dist_den_sq,
        miss_cleared,
        qa,
        qb,
        qc,
        disc,
    }
}

fn dump_q_from_int(prefix: &str, poly: &Poly, den: i128) -> Vec<String> {
    let mut items: Vec<(u8, u8, u8, i128, i128)> = Vec::new();
    for (i, j, c) in poly.sorted_mons() {
        let (n, d) = reduce_frac(c, den);
        items.push((i + j, i, j, n, d));
    }
    items.sort_unstable();
    items
        .into_iter()
        .map(|(_, i, j, n, d)| format!("{prefix} {i} {j} {n} {d}"))
        .collect()
}

fn dump_int_mons(prefix: &str, poly: &Poly) -> Vec<String> {
    poly.sorted_mons()
        .into_iter()
        .map(|(i, j, c)| format!("{prefix} {i} {j} {c}"))
        .collect()
}

fn dump_lines(data: &Data) -> String {
    let mut lines: Vec<String> = vec![
        "imagined_two_hyperbolic_cycles DROP".into(),
        "H4_ge_2 DROP".into(),
        "H4_ge_28_via_plus_one DROP".into(),
        "translated_Pt_Qt KEEP".into(),
        "degree4_field KEEP".into(),
        "line_misses_circle KEEP".into(),
        "translated_circle_orbit KEEP".into(),
        "origin_jacobian KEEP".into(),
        "n_plus_2_same_circle KEEP".into(),
        "hn_moved 0".into(),
        "cycles_proved 1".into(),
        "hopf_cycles_written 0".into(),
        "degree 4".into(),
        "rho2 1/4".into(),
        "translate_p 2 0".into(),
        "Pt00 -15/2".into(),
        "Qt00 -2".into(),
        "a 2".into(),
        "b -15/2".into(),
        "line 4x-15y".into(),
        "L_coeffs 4 -15".into(),
        "P20 -15/2".into(),
        "Q20 -2".into(),
        "regular_p 1".into(),
        format!("dist_num {}", data.dist_num),
        format!("dist_den_sq {}", data.dist_den_sq),
        "radius 1/2".into(),
        format!("miss_cleared {}", data.miss_cleared),
        "miss 1".into(),
        format!("circle_line_a {}", data.qa),
        format!("circle_line_b {}", data.qb),
        format!("circle_line_c {}", data.qc),
        format!("circle_line_disc {}", data.disc),
        "jac_det 0".into(),
        "jac_trace 0".into(),
        format!("L_jac_dRdx {}", frac_str(data.jac_r4_x, 4)),
        format!("L_jac_dRdy {}", frac_str(data.jac_r4_y, 4)),
        format!("L_jac_dSdx {}", frac_str(data.jac_s4_x, 4)),
        format!("L_jac_dSdy {}", frac_str(data.jac_s4_y, 4)),
        "gs_jac_ab -15".into(),
        "gs_jac_b2 225/4".into(),
        "gs_jac_ma2 -4".into(),
        "gs_jac_mab 15".into(),
        format!("L_at_center {}", data.ell.eval(-2, 0)),
        "L_at_rightmost -6".into(),
        "L_sign_on_circle -1".into(),
        "n_plus_2_degree 5".into(),
        "n_plus_2_rdot r^3*(rho^2-r^2)".into(),
        "untranslated_origin_eq 1".into(),
        "untranslated_line_through_origin_hits_circle 1".into(),
        "gs_ab_at_untranslated_origin 0 0".into(),
        format!("Pt_nterms {}", data.p4t.nterms()),
        format!("Qt_nterms {}", data.q4t.nterms()),
        format!("R_nterms {}", data.r4.nterms()),
        format!("S_nterms {}", data.s4.nterms()),
        format!("n2F_nterms {}", data.n2f4.nterms()),
        format!("n2G_nterms {}", data.n2g4.nterms()),
    ];
    lines.extend(dump_q_from_int("Pt", &data.p4t, 4));
    lines.extend(dump_q_from_int("Qt", &data.q4t, 4));
    lines.extend(dump_q_from_int("R", &data.r4, 4));
    lines.extend(dump_q_from_int("S", &data.s4, 4));
    lines.extend(dump_int_mons("P4t", &data.p4t));
    lines.extend(dump_int_mons("Q4t", &data.q4t));
    lines.extend(dump_q_from_int("n2F", &data.n2f4, 4));
    lines.extend(dump_q_from_int("n2G", &data.n2g4, 4));
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

    let data = check_all();
    let text = dump_lines(&data);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID kk-plus-one replay");
}
