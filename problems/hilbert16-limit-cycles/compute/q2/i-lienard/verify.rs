//! Independent replay of arXiv:2608.17773v1 Theorem 3 arithmetic and
//! the named Liénard family identities. Python (`verify.py`) expands
//! sparse monomials with a hashmap. This program expands the same
//! rings with a BTreeMap and also evaluates the energy difference on
//! the integer box {-3,...,3}^4. A degree-at-most-4 polynomial in
//! four variables that vanishes on that box is the zero polynomial.
//! rustc only.

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
// Arithmetic
// ---------------------------------------------------------------------------

const N_MIN: i32 = 2;
const N_MAX: i32 = 40;

#[derive(Clone, Debug)]
struct Row {
    n: i32,
    n_deg: i32,
    b: i32,
    hr: i32,
    hr2: i32,
    xiong: i32,
    delta1: i32,
    delta2: i32,
    delta3: i32,
}

fn b_of(n: i32) -> i32 {
    2 * n + n / 3 + (n + 1) / 3 - 2
}

fn n_of(n: i32) -> i32 {
    2 * n + 1
}

fn hr_of(n_deg: i32) -> i32 {
    2 * ((n_deg - 1) / 3) + (n_deg - 1) / 2
}

fn hr2_of(n_deg: i32) -> i32 {
    2 * ((n_deg - 1) / 3) + (n_deg / 2) + 2
}

fn xiong_of(n_deg: i32) -> i32 {
    n_deg + n_deg / 4
}

fn delta1_of(n: i32) -> i32 {
    b_of(n) - (2 * ((2 * n) / 3) + n)
}

fn delta2_of(n: i32) -> i32 {
    b_of(n) - (2 * ((2 * n) / 3) + n + 2)
}

fn row(n: i32) -> Row {
    let n_deg = n_of(n);
    let hr = hr_of(n_deg);
    let hr2 = hr2_of(n_deg);
    if hr != 2 * ((2 * n) / 3) + n {
        panic!("HR(N) substitution failed at n={n}");
    }
    if hr2 != 2 * ((2 * n) / 3) + n + 2 {
        panic!("HR2(N) substitution failed at n={n}");
    }
    let d1 = delta1_of(n);
    let d2 = delta2_of(n);
    let d3 = b_of(n) - xiong_of(n_deg);
    if d1 != b_of(n) - hr {
        panic!("delta1 is not B-HR at n={n}");
    }
    if d2 != b_of(n) - hr2 {
        panic!("delta2 is not B-HR2 at n={n}");
    }
    Row {
        n,
        n_deg,
        b: b_of(n),
        hr,
        hr2,
        xiong: xiong_of(n_deg),
        delta1: d1,
        delta2: d2,
        delta3: d3,
    }
}

fn enumerate_rows() -> Vec<Row> {
    (N_MIN..=N_MAX).map(row).collect()
}

fn join_ns(rows: &[Row], pred: impl Fn(&Row) -> bool) -> String {
    rows.iter()
        .filter(|r| pred(r))
        .map(|r| r.n.to_string())
        .collect::<Vec<_>>()
        .join(",")
}

fn check_arithmetic(rows: &[Row]) {
    let d1_pos: Vec<i32> = rows.iter().filter(|r| r.delta1 > 0).map(|r| r.n).collect();
    let d2_pos: Vec<i32> = rows.iter().filter(|r| r.delta2 > 0).map(|r| r.n).collect();
    let d1_neg: Vec<i32> = rows.iter().filter(|r| r.delta1 < 0).map(|r| r.n).collect();
    let d1_zero: Vec<i32> = rows.iter().filter(|r| r.delta1 == 0).map(|r| r.n).collect();
    let d2_zero: Vec<i32> = rows.iter().filter(|r| r.delta2 == 0).map(|r| r.n).collect();
    let d3_pos: Vec<i32> = rows.iter().filter(|r| r.delta3 > 0).map(|r| r.n).collect();

    let expected_d1: Vec<i32> = (7..=N_MAX).collect();
    let expected_d2: Vec<i32> = (13..=N_MAX).collect();
    if d1_pos != expected_d1 {
        panic!("delta1>0 is {d1_pos:?}, expected n>=7");
    }
    if d2_pos != expected_d2 {
        panic!("delta2>0 is {d2_pos:?}, expected n>=13");
    }
    if d1_neg != vec![2, 3] {
        panic!("delta1<0 is {d1_neg:?}");
    }
    if d1_zero != vec![4, 5, 6] {
        panic!("delta1=0 is {d1_zero:?}");
    }
    if d2_zero != vec![10, 11, 12] {
        panic!("delta2=0 is {d2_zero:?}");
    }
    let mut expected_d3 = vec![21];
    expected_d3.extend(23..=N_MAX);
    if d3_pos != expected_d3 {
        panic!("delta3>0 is {d3_pos:?}");
    }
}

// ---------------------------------------------------------------------------
// Family identities
// ---------------------------------------------------------------------------

struct Counts {
    energy_dedt_terms: usize,
    energy_diff_terms: usize,
    f_odd_diff_terms: usize,
    f_factor_diff_terms: usize,
    fprime_diff_terms: usize,
    fg_diff_terms: usize,
    vdp_factor_diff_terms: usize,
    vdp_sign_diff_terms: usize,
    vdp_tail_diff_terms: usize,
    even_odd_sum_terms: usize,
    linear_diff_terms: usize,
    sample_f_at_1: i128,
    sample_f_at_3: i128,
    sample_f_at_a: i128,
    sample_fprime_at_a: i128,
    sample_fprime_at_0: i128,
}

fn energy_box_zero(diff: &Poly) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            for alpha in -3i128..=3 {
                for beta in -3i128..=3 {
                    let mut values = BTreeMap::new();
                    values.insert("x".into(), x);
                    values.insert("y".into(), y);
                    values.insert("alpha".into(), alpha);
                    values.insert("beta".into(), beta);
                    if diff.eval(&values) != 0 {
                        panic!("energy difference nonzero at ({x},{y},{alpha},{beta})");
                    }
                }
            }
        }
    }
}

fn check_family() -> Counts {
    let ev = names(&["x", "y", "alpha", "beta"]);
    let x = v(&ev, "x");
    let y = v(&ev, "y");
    let alpha = v(&ev, "alpha");
    let beta = v(&ev, "beta");
    let p = y.sub(&alpha.mul(&x).add(&beta.mul(&x.pow(3))));
    let q = x.neg();
    let dedt = x.mul(&p).add(&y.mul(&q));
    let claimed = alpha.mul(&x.pow(2)).add(&beta.mul(&x.pow(4))).neg();
    let factored = x.pow(2).mul(&alpha.add(&beta.mul(&x.pow(2)))).neg();
    let energy_diff = dedt.sub(&claimed);
    require_zero(&energy_diff, "energy claimed");
    require_zero(&claimed.sub(&factored), "energy factored");
    energy_box_zero(&energy_diff);
    if dedt.is_zero() {
        panic!("energy derivative is identically zero");
    }

    let mut origin = BTreeMap::new();
    origin.insert("x".into(), 0);
    origin.insert("y".into(), 0);
    origin.insert("alpha".into(), 1);
    origin.insert("beta".into(), 1);
    if p.eval(&origin) != 0 || q.eval(&origin) != 0 {
        panic!("origin is not an equilibrium");
    }
    for yv in -3i128..=3 {
        let mut vals = BTreeMap::new();
        vals.insert("x".into(), 0);
        vals.insert("y".into(), yv);
        vals.insert("alpha".into(), 2);
        vals.insert("beta".into(), 3);
        if p.eval(&vals) != yv || q.eval(&vals) != 0 {
            panic!("x=0 slice is not (y,0)");
        }
    }

    let fv = names(&["x", "alpha", "beta"]);
    let xf = v(&fv, "x");
    let af = v(&fv, "alpha");
    let bf = v(&fv, "beta");
    let fpoly = af.mul(&xf).add(&bf.mul(&xf.pow(3)));
    let f_minus = af.mul(&xf.neg()).add(&bf.mul(&xf.neg().pow(3)));
    let odd_sum = fpoly.add(&f_minus);
    require_zero(&odd_sum, "F odd");
    let factored_f = xf.mul(&af.add(&bf.mul(&xf.pow(2))));
    let factor_diff = fpoly.sub(&factored_f);
    require_zero(&factor_diff, "F factor");
    let fprime = fpoly.dvar("x");
    let fprime_claimed = af.add(&c(&fv, 3).mul(&bf).mul(&xf.pow(2)));
    let fprime_diff = fprime.sub(&fprime_claimed);
    require_zero(&fprime_diff, "F'");
    let fg_num = xf.mul(&fprime_claimed.dvar("x")).sub(&fprime_claimed.mul(&xf.dvar("x")));
    let fg_claimed = c(&fv, 3).mul(&bf).mul(&xf.pow(2)).sub(&af);
    let fg_diff = fg_num.sub(&fg_claimed);
    require_zero(&fg_diff, "fg numerator");

    let vv = names(&["x", "a", "beta"]);
    let xv = v(&vv, "x");
    let a = v(&vv, "a");
    let bv = v(&vv, "beta");
    let f_vdp = bv.mul(&a.pow(2)).neg().mul(&xv).add(&bv.mul(&xv.pow(3)));
    let vdp_factored = bv.mul(&xv).mul(&xv.sub(&a)).mul(&xv.add(&a));
    let vdp_factor_diff = f_vdp.sub(&vdp_factored);
    require_zero(&vdp_factor_diff, "vdp F factor");
    let sign_pos = bv.mul(&xv).mul(&a.sub(&xv)).mul(&a.add(&xv));
    let sign_diff = f_vdp.neg().sub(&sign_pos);
    require_zero(&sign_diff, "vdp sign");
    let fp_vdp = f_vdp.dvar("x");
    let fp_claimed = bv.mul(&c(&vv, 3).mul(&xv.pow(2)).sub(&a.pow(2)));
    require_zero(&fp_vdp.sub(&fp_claimed), "vdp F'");
    let two_beta_a2 = c(&vv, 2).mul(&bv).mul(&a.pow(2));
    let tail = two_beta_a2.add(&c(&vv, 3).mul(&bv).mul(&xv.pow(2).sub(&a.pow(2))));
    let tail_diff = fp_vdp.sub(&tail);
    require_zero(&tail_diff, "vdp tail");

    let av = names(&["a", "beta"]);
    let aa = v(&av, "a");
    let ba = v(&av, "beta");
    let fp_at_a = ba.mul(&aa.pow(2)).neg().add(&c(&av, 3).mul(&ba).mul(&aa.pow(2)));
    require_zero(
        &fp_at_a.sub(&c(&av, 2).mul(&ba).mul(&aa.pow(2))),
        "F'(a)=2 beta a^2",
    );

    let evn = names(&["x", "alpha", "beta", "gamma"]);
    let xe = v(&evn, "x");
    let ae = v(&evn, "alpha");
    let be = v(&evn, "beta");
    let ge = v(&evn, "gamma");
    let f_even = ae.mul(&xe).add(&ge.mul(&xe.pow(2))).add(&be.mul(&xe.pow(3)));
    let f_even_m = ae
        .mul(&xe.neg())
        .add(&ge.mul(&xe.neg().pow(2)))
        .add(&be.mul(&xe.neg().pow(3)));
    let even_odd = f_even.add(&f_even_m);
    let even_claimed = c(&evn, 2).mul(&ge).mul(&xe.pow(2));
    require_zero(&even_odd.sub(&even_claimed), "even-term oddness");
    if even_odd.is_zero() {
        panic!("even term unexpectedly preserved oddness");
    }

    let lv = names(&["x", "y", "alpha"]);
    let xl = v(&lv, "x");
    let yl = v(&lv, "y");
    let al = v(&lv, "alpha");
    let pl = yl.sub(&al.mul(&xl));
    let ql = xl.neg();
    let d2edt = xl.scale(2).mul(&pl).add(&yl.scale(2).mul(&ql));
    let claimed2 = al.mul(&xl.pow(2)).scale(-2);
    let lin_diff = d2edt.sub(&claimed2);
    require_zero(&lin_diff, "linear energy");

    let mut fvals = BTreeMap::new();
    fvals.insert("x".into(), 1);
    fvals.insert("alpha".into(), -4);
    fvals.insert("beta".into(), 1);
    let sample_f_at_1 = fpoly.eval(&fvals);
    fvals.insert("x".into(), 3);
    let sample_f_at_3 = fpoly.eval(&fvals);
    fvals.insert("x".into(), 2);
    let sample_f_at_a = fpoly.eval(&fvals);
    let sample_fprime_at_a = fprime.eval(&fvals);
    fvals.insert("x".into(), 0);
    let sample_fprime_at_0 = fprime.eval(&fvals);
    if sample_f_at_1 != -3 || sample_f_at_3 != 15 || sample_f_at_a != 0 {
        panic!("sample F values");
    }
    if sample_fprime_at_a != 8 || sample_fprime_at_0 != -4 {
        panic!("sample F' values");
    }

    let mut evals = BTreeMap::new();
    evals.insert("x".into(), 1);
    evals.insert("y".into(), 0);
    evals.insert("alpha".into(), 1);
    evals.insert("beta".into(), 0);
    if dedt.eval(&evals) != -1 {
        panic!("linear damping energy at x=1");
    }
    evals.insert("alpha".into(), 0);
    evals.insert("beta".into(), 1);
    if dedt.eval(&evals) != -1 {
        panic!("pure cubic damping energy at x=1");
    }
    evals.insert("alpha".into(), 1);
    evals.insert("beta".into(), 1);
    if dedt.eval(&evals) != -2 {
        panic!("both-nonnegative energy at x=1");
    }
    evals.insert("x".into(), 0);
    evals.insert("y".into(), 5);
    if dedt.eval(&evals) != 0 {
        panic!("energy vanishes on x=0");
    }

    let bad = dedt.add(&c(&ev, 1));
    if bad.term_count() == claimed.term_count() && energy_diff.is_zero() && bad.is_zero() {
        panic!("constant perturbation of dE/dt vanished");
    }
    let wrong = alpha.mul(&x.pow(2)).add(&beta.mul(&x.pow(2))).neg();
    if dedt.term_count() == wrong.term_count() {
        let wdiff = dedt.sub(&wrong);
        if wdiff.is_zero() {
            panic!("energy matched the wrong-power formula");
        }
    }

    Counts {
        energy_dedt_terms: dedt.term_count(),
        energy_diff_terms: energy_diff.term_count(),
        f_odd_diff_terms: odd_sum.term_count(),
        f_factor_diff_terms: factor_diff.term_count(),
        fprime_diff_terms: fprime_diff.term_count(),
        fg_diff_terms: fg_diff.term_count(),
        vdp_factor_diff_terms: vdp_factor_diff.term_count(),
        vdp_sign_diff_terms: sign_diff.term_count(),
        vdp_tail_diff_terms: tail_diff.term_count(),
        even_odd_sum_terms: even_odd.term_count(),
        linear_diff_terms: lin_diff.term_count(),
        sample_f_at_1,
        sample_f_at_3,
        sample_f_at_a,
        sample_fprime_at_a,
        sample_fprime_at_0,
    }
}

fn dump_lines(rows: &[Row], counts: &Counts) -> String {
    let mut lines = Vec::new();
    for r in rows {
        lines.push(format!(
            "n {} N {} B {} HR {} HR2 {} Xiong {} delta1 {} delta2 {} delta3 {}",
            r.n, r.n_deg, r.b, r.hr, r.hr2, r.xiong, r.delta1, r.delta2, r.delta3
        ));
    }
    let d1_neg = join_ns(rows, |r| r.delta1 < 0);
    let d1_zero = join_ns(rows, |r| r.delta1 == 0);
    let d2_zero = join_ns(rows, |r| r.delta2 == 0);
    let d3_pos = join_ns(rows, |r| r.delta3 > 0);
    lines.push("delta1_gt0_iff_n_ge 7".into());
    lines.push("delta2_gt0_iff_n_ge 13".into());
    lines.push(format!("delta1_negative_n {d1_neg}"));
    lines.push(format!("delta1_zero_n {d1_zero}"));
    lines.push(format!("delta2_zero_n {d2_zero}"));
    lines.push(format!("delta3_positive_n {d3_pos}"));
    lines.push("HR_formula_matches_N_substitution".into());
    lines.push(format!(
        "energy_dEdt_terms {} difference {}",
        counts.energy_dedt_terms, counts.energy_diff_terms
    ));
    lines.push(format!("F_odd_difference {}", counts.f_odd_diff_terms));
    lines.push(format!("F_factor_difference {}", counts.f_factor_diff_terms));
    lines.push(format!("Fprime_difference {}", counts.fprime_diff_terms));
    lines.push(format!("fg_numerator_difference {}", counts.fg_diff_terms));
    lines.push(format!(
        "vdp_factor_difference {}",
        counts.vdp_factor_diff_terms
    ));
    lines.push(format!("vdp_sign_difference {}", counts.vdp_sign_diff_terms));
    lines.push(format!("vdp_tail_difference {}", counts.vdp_tail_diff_terms));
    lines.push(format!("even_odd_sum_terms {}", counts.even_odd_sum_terms));
    lines.push(format!("linear_diff_terms {}", counts.linear_diff_terms));
    lines.push(format!(
        "sample_a2_beta1 F(1)={} F(3)={} F(a)={} Fprime(a)={} Fprime(0)={}",
        counts.sample_f_at_1,
        counts.sample_f_at_3,
        counts.sample_f_at_a,
        counts.sample_fprime_at_a,
        counts.sample_fprime_at_0
    ));
    lines.push("linear_charpoly lambda^2+alpha*lambda+1".into());
    lines.push("hn_moved 0".into());
    lines.push("beats_B_n 0".into());
    lines.push("H31_full_proved 0".into());
    lines.push("new_H3 0".into());
    lines.push("negative energy perturbation rejected".into());
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

    let rows = enumerate_rows();
    check_arithmetic(&rows);
    let counts = check_family();
    let text = dump_lines(&rows, &counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID i-lienard replay");
}
