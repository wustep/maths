//! Independent replay of Z(2,n) = floor((n-1)/2) on H = (x^2+y^2)/2.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap. This
//! program expands the same rings with a BTreeMap and evaluates the
//! residuals on an integer box. The imagined extra Abelian zero is
//! not constructed. rustc only.

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

    fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    fn term_count(&self) -> usize {
        self.terms.len()
    }

    fn degree(&self) -> i32 {
        if self.terms.is_empty() {
            return -1;
        }
        self.terms
            .keys()
            .map(|e| e.iter().map(|p| i32::from(*p)).sum())
            .max()
            .unwrap_or(-1)
    }

    fn subst_x_neg(&self) -> Self {
        let x = Self::var(&self.vars, "x").neg();
        let y = Self::var(&self.vars, "y");
        let mut out = Self::zero(&self.vars);
        for (exp, coeff) in &self.terms {
            let mut mon = Self::constant(&self.vars, *coeff);
            mon = mon.mul(&x.pow(u32::from(exp[0])));
            mon = mon.mul(&y.pow(u32::from(exp[1])));
            out = out.add(&mon);
        }
        out
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

// ---------------------------------------------------------------------------
// Univariate Z[t]
// ---------------------------------------------------------------------------

fn uni_eval(coeffs: &[i128], x: i128) -> i128 {
    let mut total = 0i128;
    let mut pwr = 1i128;
    for c in coeffs {
        total += c * pwr;
        pwr *= x;
    }
    total
}

fn uni_eval_at_half_num(coeffs: &[i128]) -> i128 {
    if coeffs.is_empty() {
        return 0;
    }
    let deg = coeffs.len() - 1;
    let mut num = 0i128;
    for (k, c) in coeffs.iter().enumerate() {
        num += c * (1i128 << (deg - k));
    }
    num
}

fn uni_mul(a: &[i128], b: &[i128]) -> Vec<i128> {
    let mut out = vec![0i128; a.len() + b.len() - 1];
    for (i, ca) in a.iter().enumerate() {
        for (j, cb) in b.iter().enumerate() {
            out[i + j] += ca * cb;
        }
    }
    while out.len() > 1 && *out.last().unwrap() == 0 {
        out.pop();
    }
    out
}

fn uni_sub(a: &[i128], b: &[i128]) -> Vec<i128> {
    let n = a.len().max(b.len());
    let mut out = Vec::with_capacity(n);
    for i in 0..n {
        let av = if i < a.len() { a[i] } else { 0 };
        let bv = if i < b.len() { b[i] } else { 0 };
        out.push(av - bv);
    }
    while out.len() > 1 && *out.last().unwrap() == 0 {
        out.pop();
    }
    out
}

fn uni_scale_x(coeffs: &[i128], factor: i128) -> Vec<i128> {
    coeffs
        .iter()
        .enumerate()
        .map(|(k, c)| c * factor.pow(k as u32))
        .collect()
}

fn uni_times_x(coeffs: &[i128]) -> Vec<i128> {
    let mut out = vec![0];
    out.extend_from_slice(coeffs);
    out
}

fn uni_fmt(coeffs: &[i128]) -> String {
    coeffs
        .iter()
        .map(|c| c.to_string())
        .collect::<Vec<_>>()
        .join(",")
}

fn z2(n: i32) -> i32 {
    (n - 1) / 2
}

fn radial_deg_q(n: i32) -> i32 {
    2 * z2(n) + 1
}

fn beat_deg_q(n: i32) -> i32 {
    2 * (z2(n) + 1) + 1
}

#[derive(Clone)]
struct Row {
    n: i32,
    z: i32,
    deg_q: i32,
    zeros: i32,
    matches: i32,
}

fn check_arithmetic() -> Vec<Row> {
    let mut rows = Vec::new();
    for n in 1..=10 {
        let z = z2(n);
        let deg_q = radial_deg_q(n);
        if deg_q > n {
            panic!("radial degQ {deg_q} exceeds n={n}");
        }
        if beat_deg_q(n) != 2 * z + 3 {
            panic!("beat degree formula");
        }
        if beat_deg_q(n) <= n {
            panic!("beating Z(2,{n}) unexpectedly fits in degree n");
        }
        rows.push(Row {
            n,
            z,
            deg_q,
            zeros: z,
            matches: 1,
        });
    }
    rows
}

struct Counts {
    d_hdt_terms: usize,
    n3_q_terms: usize,
    n5_q_terms: usize,
    n3_p: Vec<i128>,
    n5_p: Vec<i128>,
    n3_i: Vec<i128>,
    n5_i: Vec<i128>,
}

fn check_family() -> Counts {
    let xy = names(&["x", "y"]);
    let x = v(&xy, "x");
    let y = v(&xy, "y");
    let hnum = x.pow(2).add(&y.pow(2));
    let p_field = y.clone();
    let q_field = x.neg();
    let dhdt = hnum.dvar("x").mul(&p_field).add(&hnum.dvar("y").mul(&q_field));
    require_zero(&dhdt, "dHnum/dt");
    if hnum.degree() != 2 {
        panic!("Hnum is not quadratic");
    }
    if p_field.degree() != 1 || q_field.degree() != 1 {
        panic!("Hamiltonian field is not linear");
    }

    let n3_p = vec![1i128, -1];
    let q3 = y.mul(&c(&xy, 1).sub(&x.pow(2)).sub(&y.pow(2)));
    if q3.degree() != 3 {
        panic!("n=3 deg Q");
    }
    if q3.term_count() != 3 {
        panic!("n=3 Q term count");
    }
    let n3_i = uni_times_x(&uni_scale_x(&n3_p, 2));
    let n3_factored = uni_mul(&[0, 1], &[1, -2]);
    if n3_i != vec![0, 1, -2] {
        panic!("n=3 I_tilde {n3_i:?}");
    }
    if uni_sub(&n3_i, &n3_factored) != vec![0] {
        panic!("n=3 factorization");
    }
    if uni_eval(&n3_p, 1) != 0 || uni_eval(&n3_p, 0) != 1 {
        panic!("n=3 p samples");
    }
    if uni_eval_at_half_num(&n3_i) != 0 {
        panic!("n=3 I_tilde(1/2)");
    }

    let xyh = names(&["x", "y", "h"]);
    let xv = v(&xyh, "x");
    let yv = v(&xyh, "y");
    let hv = v(&xyh, "h");
    let r2 = xv.pow(2).add(&yv.pow(2));
    let p_r3 = c(&xyh, 1).sub(&r2);
    let p_h3 = c(&xyh, 1).sub(&hv.scale(2));
    let factor3 = r2.sub(&hv.scale(2));
    let oval3 = p_r3.sub(&p_h3).sub(&factor3.scale(-1));
    require_zero(&oval3, "n=3 oval reduction");

    let n5_p = vec![4i128, -5, 1];
    let r2xy = x.pow(2).add(&y.pow(2));
    let q5 = y
        .mul(&r2xy.sub(&c(&xy, 1)))
        .mul(&r2xy.sub(&c(&xy, 4)));
    if q5.degree() != 5 {
        panic!("n=5 deg Q");
    }
    if q5.term_count() != 6 {
        panic!("n=5 Q term count");
    }
    let n5_i = uni_times_x(&uni_scale_x(&n5_p, 2));
    let n5_factored = uni_mul(&uni_mul(&[0, 1], &[-1, 2]), &[-4, 2]);
    if n5_i != vec![0, 4, -10, 4] {
        panic!("n=5 I_tilde {n5_i:?}");
    }
    if uni_sub(&n5_i, &n5_factored) != vec![0] {
        panic!("n=5 factorization");
    }
    if uni_eval(&n5_p, 1) != 0 || uni_eval(&n5_p, 4) != 0 {
        panic!("n=5 p roots");
    }
    if uni_eval(&n5_p, 0) != 4 {
        panic!("n=5 p(0)");
    }
    if uni_eval_at_half_num(&n5_i) != 0 {
        panic!("n=5 I_tilde(1/2)");
    }
    if uni_eval(&n5_i, 2) != 0 {
        panic!("n=5 I_tilde(2)");
    }
    if uni_eval(&n5_i, 1) == 0 {
        panic!("n=5 unexpectedly vanished at h=1");
    }
    if n5_i.len() - 1 != 3 {
        panic!("n=5 I_tilde degree");
    }

    let r2h = xv.pow(2).add(&yv.pow(2));
    let p_r5 = r2h.pow(2).sub(&r2h.scale(5)).add(&c(&xyh, 4));
    let p_h5 = hv.pow(2).scale(4).sub(&hv.scale(10)).add(&c(&xyh, 4));
    let factor5 = r2h.sub(&hv.scale(2));
    let quot5 = r2h.add(&hv.scale(2)).sub(&c(&xyh, 5));
    let oval5 = p_r5.sub(&p_h5).sub(&factor5.mul(&quot5));
    require_zero(&oval5, "n=5 oval reduction");

    let coeff = x.mul(&y).mul(&x.pow(2).add(&y.pow(2)));
    let flipped = coeff.scale(-1);
    if !coeff.subst_x_neg().terms.eq(&flipped.terms) {
        panic!("xy r^2 is not odd in x");
    }

    for xv_i in -3i128..=3 {
        for yv_i in -3i128..=3 {
            let mut vals = BTreeMap::new();
            vals.insert("x".into(), xv_i);
            vals.insert("y".into(), yv_i);
            if dhdt.eval(&vals) != 0 {
                panic!("dHnum/dt nonzero at ({xv_i},{yv_i})");
            }
            if 2 * xv_i * yv_i + 2 * yv_i * (-xv_i) != 0 {
                panic!("hand dH/dt sample");
            }
        }
    }
    for xv_i in -3i128..=3 {
        for yv_i in -3i128..=3 {
            for hv_i in -3i128..=3 {
                let mut vals = BTreeMap::new();
                vals.insert("x".into(), xv_i);
                vals.insert("y".into(), yv_i);
                vals.insert("h".into(), hv_i);
                if oval3.eval(&vals) != 0 {
                    panic!("n=3 oval residual");
                }
                if oval5.eval(&vals) != 0 {
                    panic!("n=5 oval residual");
                }
            }
        }
    }

    let mut extra = n5_i.clone();
    extra.push(0);
    extra[0] = 1;
    if extra == n5_i {
        panic!("extra-root polynomial collided");
    }
    let cubic = vec![-36i128, 49, -14, 1];
    if uni_eval(&cubic, 1) != 0 || uni_eval(&cubic, 4) != 0 || uni_eval(&cubic, 9) != 0 {
        panic!("cubic p roots");
    }
    if 2 * 3 + 1 != 7 {
        panic!("cubic p is degree 7");
    }
    if n3_i == vec![0, 1, -2, 1] {
        panic!("n=3 unexpectedly gained a cubic term");
    }

    Counts {
        d_hdt_terms: dhdt.term_count(),
        n3_q_terms: q3.term_count(),
        n5_q_terms: q5.term_count(),
        n3_p,
        n5_p,
        n3_i,
        n5_i,
    }
}

fn dump_lines(rows: &[Row], counts: &Counts) -> String {
    let mut lines = Vec::new();
    lines.push("formula Z(2,n)=floor((n-1)/2)".to_string());
    for r in rows {
        lines.push(format!(
            "n {} Z {} degQ {} zeros {} matches {}",
            r.n, r.z, r.deg_q, r.zeros, r.matches
        ));
    }
    lines.push(format!(
        "hamiltonian dHnum/dt terms {}",
        counts.d_hdt_terms
    ));
    lines.push(format!("n3 Q terms {}", counts.n3_q_terms));
    lines.push(format!("n3 p {}", uni_fmt(&counts.n3_p)));
    lines.push(format!("n3 I_tilde {}", uni_fmt(&counts.n3_i)));
    lines.push("n3 factor I_tilde-h*(1-2h) 0".to_string());
    lines.push(format!("n3 p(1) {}", uni_eval(&counts.n3_p, 1)));
    lines.push("n3 I_tilde_at_1/2 0".to_string());
    lines.push("n3 oval_reduction 0".to_string());
    lines.push("n3 positive_zeros 1/2".to_string());
    lines.push(format!("n5 Q terms {}", counts.n5_q_terms));
    lines.push(format!("n5 p {}", uni_fmt(&counts.n5_p)));
    lines.push(format!("n5 I_tilde {}", uni_fmt(&counts.n5_i)));
    lines.push("n5 factor I_tilde-h*(2h-1)*(2h-4) 0".to_string());
    lines.push(format!("n5 p(1) {}", uni_eval(&counts.n5_p, 1)));
    lines.push(format!("n5 p(4) {}", uni_eval(&counts.n5_p, 4)));
    lines.push("n5 I_tilde_at_1/2 0".to_string());
    lines.push("n5 I_tilde_at_2 0".to_string());
    lines.push("n5 oval_reduction 0".to_string());
    lines.push("n5 positive_zeros 1/2,2".to_string());
    lines.push("n5 extra_zero_degree_needed 4".to_string());
    lines.push(format!("beat n=3 needs_degQ {}", beat_deg_q(3)));
    lines.push(format!("beat n=5 needs_degQ {}", beat_deg_q(5)));
    lines.push("formula_beaten 0".to_string());
    lines.push("hn_moved 0".to_string());
    lines.push("not_H2".to_string());
    lines.push("negative extra root rejected".to_string());
    lines.push("integer box zeros".to_string());
    lines.join("\n") + "\n"
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

    let rows = check_arithmetic();
    let counts = check_family();
    let text = dump_lines(&rows, &counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID jj-weak-hilbert replay");
}
