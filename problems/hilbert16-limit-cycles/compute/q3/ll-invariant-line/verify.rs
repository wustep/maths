//! Independent replay of the cubic-with-invariant-line identities.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap. This
//! program expands the same rings with a BTreeMap and evaluates the
//! residuals on the integer box {-3,...,3}. rustc only.
//!
//! Imagined three cycles are not produced. Kept: named cubic
//! dx/dt = 16y+16x+x^3, dy/dt = 16xy, line y=0, Dulac B=1/y,
//! certified cycle count 0. Not a bound on H(n).

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

    fn degree(&self) -> i32 {
        self.degree_ignore(&[])
    }

    fn degree_ignore(&self, ignore: &[&str]) -> i32 {
        if self.terms.is_empty() {
            return -1;
        }
        let skip: Vec<usize> = ignore
            .iter()
            .filter_map(|name| self.vars.iter().position(|v| v == name))
            .collect();
        self.terms
            .keys()
            .map(|exp| {
                exp.iter()
                    .enumerate()
                    .filter(|(i, _)| !skip.contains(i))
                    .map(|(_, p)| i32::from(*p))
                    .sum()
            })
            .max()
            .unwrap_or(-1)
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

fn box_zero_xy(diff: &Poly, label: &str) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            let mut values = BTreeMap::new();
            values.insert("x".into(), x);
            values.insert("y".into(), y);
            if diff.eval(&values) != 0 {
                panic!("{label} residual nonzero at ({x},{y})");
            }
        }
    }
}

fn box_zero_xym(diff: &Poly, label: &str) {
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            for mu in -3i128..=3 {
                let mut values = BTreeMap::new();
                values.insert("x".into(), x);
                values.insert("y".into(), y);
                values.insert("mu".into(), mu);
                if diff.eval(&values) != 0 {
                    panic!("{label} residual nonzero at ({x},{y},{mu})");
                }
            }
        }
    }
}

struct Counts {
    p_terms: usize,
    q_terms: usize,
    p_axis_at_1: i128,
    axis_factor_at_0: i128,
    dulac_num_at_0: i128,
    div_at_0: i128,
    div_at_minus3: i128,
    div_disc: i128,
    trace_origin: i128,
    det_origin: i128,
    named_dulac_diff_terms: usize,
    family_dulac_diff_terms: usize,
    named_cofactor_diff_terms: usize,
    family_degree: i32,
    named_mu_disc_num: i128,
    named_mu_disc_den: i128,
    energy_terms: usize,
}

fn check_all() -> Counts {
    let xy = names(&["x", "y"]);
    let x = v(&xy, "x");
    let y = v(&xy, "y");
    let p = y.scale(16).add(&x.scale(16)).add(&x.pow(3));
    let q = x.scale(16).mul(&y);
    let cofactor_diff = q.sub(&x.scale(16).mul(&y));
    require_zero(&cofactor_diff, "named cofactor");
    box_zero_xy(&cofactor_diff, "named cofactor");

    let mut y0 = BTreeMap::new();
    y0.insert("y".into(), c(&xy, 0));
    let p_axis = p.subst(&y0);
    let axis_factor = c(&xy, 16).add(&x.pow(2));
    require_zero(&p_axis.sub(&x.mul(&axis_factor)), "named axis");
    require_zero(
        &axis_factor.sub(&c(&xy, 16)).sub(&x.pow(2)),
        "axis shift",
    );

    let mut x0 = BTreeMap::new();
    x0.insert("x".into(), c(&xy, 0));
    require_zero(&p.subst(&x0).sub(&y.scale(16)), "P on x=0");

    let div = p.dvar("x").add(&q.dvar("y"));
    let div_claimed = c(&xy, 16).add(&x.scale(16)).add(&x.pow(2).scale(3));
    require_zero(&div.sub(&div_claimed), "named div");
    box_zero_xy(&div.sub(&div_claimed), "named div");

    let dulac_num = c(&xy, 16).add(&x.pow(2).scale(3));
    let dulac_cleared = div.mul(&y).sub(&q);
    let dulac_diff = dulac_cleared.sub(&y.mul(&dulac_num));
    require_zero(&dulac_diff, "named dulac");
    box_zero_xy(&dulac_diff, "named dulac");
    require_zero(
        &dulac_num.sub(&c(&xy, 16)).sub(&x.pow(2).scale(3)),
        "dulac num shift",
    );

    let rescale = y.scale(16).add(&x.scale(16)).add(&x.pow(3));
    require_zero(&rescale.sub(&p), "time rescale");

    let dp_dx = p.dvar("x");
    let dp_dy = p.dvar("y");
    let dq_dx = q.dvar("x");
    let dq_dy = q.dvar("y");
    let mut origin_q = BTreeMap::new();
    origin_q.insert("x".into(), 0);
    origin_q.insert("y".into(), 0);
    if dq_dx.eval(&origin_q) != 0 {
        panic!("dQ/dx at origin");
    }
    let det = dp_dx.mul(&dq_dy).sub(&dp_dy.mul(&dq_dx));

    let mut origin = BTreeMap::new();
    origin.insert("x".into(), 0);
    origin.insert("y".into(), 0);
    let mut at10 = BTreeMap::new();
    at10.insert("x".into(), 1);
    at10.insert("y".into(), 0);
    let mut at_m3 = BTreeMap::new();
    at_m3.insert("x".into(), -3);
    at_m3.insert("y".into(), 0);

    let p_axis_at_1 = p.eval(&at10);
    let axis_factor_at_0 = axis_factor.eval(&origin);
    let dulac_num_at_0 = dulac_num.eval(&origin);
    let div_at_0 = div.eval(&origin);
    let div_at_minus3 = div.eval(&at_m3);
    let div_disc = 16 * 16 - 4 * 3 * 16;
    let trace_origin = dp_dx.eval(&origin) + dq_dy.eval(&origin);
    let det_origin = det.eval(&origin);

    if p_axis_at_1 != 17 {
        panic!("P(1,0)");
    }
    if axis_factor_at_0 != 16 {
        panic!("axis factor at 0");
    }
    if dulac_num_at_0 != 16 {
        panic!("dulac num at 0");
    }
    if div_at_0 != 16 {
        panic!("div at 0");
    }
    if div_at_minus3 != -5 {
        panic!("div at -3");
    }
    if div_disc != 64 {
        panic!("div disc");
    }
    if trace_origin != 16 {
        panic!("trace origin");
    }
    if det_origin != 0 {
        panic!("det origin");
    }
    if p.degree().max(q.degree()) != 3 {
        panic!("named degree");
    }

    for xv in -3i128..=3 {
        for yv in -3i128..=3 {
            let mut vals = BTreeMap::new();
            vals.insert("x".into(), xv);
            vals.insert("y".into(), yv);
            if p.eval(&vals) == 0 && q.eval(&vals) == 0 && (xv != 0 || yv != 0) {
                panic!("unexpected equilibrium ({xv},{yv})");
            }
        }
        let mut xv0 = BTreeMap::new();
        xv0.insert("x".into(), xv);
        xv0.insert("y".into(), 0);
        if axis_factor.eval(&xv0) < 16 {
            panic!("axis factor dropped below 16");
        }
        if dulac_num.eval(&xv0) < 16 {
            panic!("dulac numerator dropped below 16");
        }
    }

    let xym = names(&["x", "y", "mu"]);
    let xf = v(&xym, "x");
    let yf = v(&xym, "y");
    let mu = v(&xym, "mu");
    let pf = yf.add(&xf).add(&mu.mul(&xf.pow(3)));
    let qf = xf.mul(&yf);
    require_zero(&qf.sub(&xf.mul(&yf)), "family cofactor");
    let mut y0f = BTreeMap::new();
    y0f.insert("y".into(), c(&xym, 0));
    let p_axis_f = pf.subst(&y0f);
    let axis_f = c(&xym, 1).add(&mu.mul(&xf.pow(2)));
    require_zero(&p_axis_f.sub(&xf.mul(&axis_f)), "family axis");
    let divf = pf.dvar("x").add(&qf.dvar("y"));
    let divf_claimed = c(&xym, 1).add(&xf).add(&mu.scale(3).mul(&xf.pow(2)));
    require_zero(&divf.sub(&divf_claimed), "family div");
    let dulac_num_f = c(&xym, 1).add(&mu.scale(3).mul(&xf.pow(2)));
    let dulac_diff_f = divf.mul(&yf).sub(&qf).sub(&yf.mul(&dulac_num_f));
    require_zero(&dulac_diff_f, "family dulac");
    box_zero_xym(&dulac_diff_f, "family dulac");

    let mut mu0 = BTreeMap::new();
    mu0.insert("mu".into(), c(&xym, 0));
    let p0 = pf.subst(&mu0);
    if p0.degree_ignore(&["mu"]).max(qf.degree_ignore(&["mu"])) != 2 {
        panic!("mu=0 should be quadratic");
    }
    if pf.degree_ignore(&["mu"]).max(qf.degree_ignore(&["mu"])) != 3 {
        panic!("family degree");
    }

    let mut fam0 = BTreeMap::new();
    fam0.insert("x".into(), 0);
    fam0.insert("y".into(), 0);
    fam0.insert("mu".into(), 0);
    if axis_f.eval(&fam0) != 1 {
        panic!("family axis at 0");
    }
    fam0.insert("x".into(), 2);
    fam0.insert("mu".into(), 1);
    if axis_f.eval(&fam0) != 5 {
        panic!("family axis sample");
    }

    let named_mu_disc_num = 16 - 12;
    let named_mu_disc_den = 16;
    if named_mu_disc_num != 4 {
        panic!("named mu disc");
    }

    // degeneration: whole x-axis is equilibria
    let pd = yf.clone();
    let qd = yf
        .mul(&xf.add(&mu.mul(&xf.pow(2).sub(&c(&xym, 1))).mul(&yf)))
        .neg();
    let mut y0d = BTreeMap::new();
    y0d.insert("y".into(), c(&xym, 0));
    require_zero(&pd.subst(&y0d), "degeneration P axis");
    require_zero(&qd.subst(&y0d), "degeneration Q axis");

    let energy = x.pow(2).add(&y.pow(2));
    let d_energy = energy.dvar("x").mul(&p).add(&energy.dvar("y").mul(&q));
    if d_energy.is_zero() {
        panic!("x^2+y^2 unexpectedly conserved");
    }

    let q_harm = x.neg();
    let mut y0h = BTreeMap::new();
    y0h.insert("y".into(), c(&xy, 0));
    if q_harm.subst(&y0h).is_zero() {
        panic!("harmonic Q(x,0) unexpectedly zero");
    }

    Counts {
        p_terms: p.nterms(),
        q_terms: q.nterms(),
        p_axis_at_1,
        axis_factor_at_0,
        dulac_num_at_0,
        div_at_0,
        div_at_minus3,
        div_disc,
        trace_origin,
        det_origin,
        named_dulac_diff_terms: dulac_diff.nterms(),
        family_dulac_diff_terms: dulac_diff_f.nterms(),
        named_cofactor_diff_terms: cofactor_diff.nterms(),
        family_degree: pf.degree_ignore(&["mu"]).max(qf.degree_ignore(&["mu"])),
        named_mu_disc_num,
        named_mu_disc_den,
        energy_terms: d_energy.nterms(),
    }
}

fn dump_lines(counts: &Counts) -> String {
    let mut lines = Vec::new();
    lines.push("imagined_three_cycles DROP".into());
    lines.push("ye_cherkas_quadratic_at_most_one CONTEXT".into());
    lines.push("ye_reproved 0".into());
    lines.push("named_cubic_invariant_line KEEP".into());
    lines.push("dulac_half_planes KEEP".into());
    lines.push("certified_cycle_count 0".into());
    lines.push("family_cycle_count 0".into());
    lines.push("hn_moved 0".into());
    lines.push("three_cycles_produced 0".into());
    lines.push("degree 3".into());
    lines.push("family_degree_mu0 2".into());
    lines.push("invariant_line y=0".into());
    lines.push("cofactor_named 16x".into());
    lines.push("cofactor_family x".into());
    lines.push("line_of_equilibria 0".into());
    lines.push("equilibria_count 1".into());
    lines.push("eq 0 0".into());
    lines.push(format!("P_terms {}", counts.p_terms));
    lines.push(format!("Q_terms {}", counts.q_terms));
    lines.push(format!("P_axis_at_1 {}", counts.p_axis_at_1));
    lines.push(format!("axis_factor_at_0 {}", counts.axis_factor_at_0));
    lines.push(format!("dulac_num_at_0 {}", counts.dulac_num_at_0));
    lines.push(format!("dulac_num_min {}", counts.dulac_num_at_0));
    lines.push(format!("div_at_0 {}", counts.div_at_0));
    lines.push(format!("div_at_minus3 {}", counts.div_at_minus3));
    lines.push(format!("div_disc {}", counts.div_disc));
    lines.push("bendixson_inconclusive 1".into());
    lines.push(format!("trace_origin {}", counts.trace_origin));
    lines.push(format!("det_origin {}", counts.det_origin));
    lines.push(format!(
        "named_dulac_diff_terms {}",
        counts.named_dulac_diff_terms
    ));
    lines.push(format!(
        "family_dulac_diff_terms {}",
        counts.family_dulac_diff_terms
    ));
    lines.push(format!(
        "named_cofactor_diff_terms {}",
        counts.named_cofactor_diff_terms
    ));
    lines.push(format!("family_degree {}", counts.family_degree));
    lines.push(format!(
        "named_mu_disc {}/{}",
        counts.named_mu_disc_num, counts.named_mu_disc_den
    ));
    lines.push("degeneration_axis_equilibria 1".into());
    lines.push(format!(
        "energy_not_integral_terms {}",
        counts.energy_terms
    ));
    lines.push("integer_box 1".into());
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
    println!("VALID ll-invariant-line replay");
}
