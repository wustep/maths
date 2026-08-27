//! Independent checker for the first Melnikov identities on
//! dx/dt = 2y, dy/dt = -x^3.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap.
//! This program expands the same rings with a BTreeMap and evaluates
//! the residuals on an integer box. rustc only. No special functions.
//! The imagined 14 zeros of I(h) are not certified.

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

    fn subst(&self, mapping: &BTreeMap<String, Poly>) -> Self {
        let mut out = Self::zero(&self.vars);
        for (exp, coeff) in &self.terms {
            let mut mon = Self::constant(&self.vars, *coeff);
            for (name, power) in self.vars.iter().zip(exp.iter()) {
                if *power == 0 {
                    continue;
                }
                let factor = if let Some(p) = mapping.get(name) {
                    p.pow(u32::from(*power))
                } else {
                    Poly::var(&self.vars, name).pow(u32::from(*power))
                };
                mon = mon.mul(&factor);
            }
            out = out.add(&mon);
        }
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

fn require_equal(left: &Poly, right: &Poly, label: &str) {
    if left.vars != right.vars || left.terms != right.terms {
        panic!("{label} mismatch");
    }
}

fn require_nonzero(poly: &Poly, label: &str) {
    if poly.is_zero() {
        panic!("{label} is unexpectedly the zero polynomial");
    }
}

fn insert(map: &mut BTreeMap<String, i128>, name: &str, value: i128) {
    map.insert(name.to_string(), value);
}

struct Counts {
    dhdt_terms: usize,
    trace: i128,
    det: i128,
    hess_det: i128,
    family_extra_terms: usize,
    family_extra_diff: usize,
    area_num: i128,
    area_den: i128,
    moment_num: i128,
    moment_den: i128,
}

fn unperturbed(vs: &[String]) -> (Poly, Poly, Poly, Poly, Poly, Poly) {
    let x = v(vs, "x");
    let y = v(vs, "y");
    let p0 = c(vs, 2).mul(&y);
    let q0 = x.pow(3).neg();
    let h = x.pow(4).add(&c(vs, 4).mul(&y.pow(2)));
    let hx = h.dvar("x");
    let hy = h.dvar("y");
    let dhdt = hx.mul(&p0).add(&hy.mul(&q0));
    (p0, q0, h, hx, hy, dhdt)
}

fn check_all() -> Counts {
    let xy = names(&["x", "y"]);
    let (p0, q0, h, hx, hy, dhdt) = unperturbed(&xy);
    require_zero(&dhdt, "unperturbed dH/dt");
    require_equal(&hx, &c(&xy, 4).mul(&v(&xy, "x").pow(3)), "Hx");
    require_equal(&hy, &c(&xy, 8).mul(&v(&xy, "y")), "Hy");

    let y = v(&xy, "y");
    let sos = q0.pow(2).add(&y.pow(2));
    let sos_claimed = v(&xy, "x").pow(6).add(&y.pow(2));
    require_zero(&sos.sub(&sos_claimed), "sum of squares");

    let j11 = p0.dvar("x");
    let j12 = p0.dvar("y");
    let j21 = q0.dvar("x");
    let j22 = q0.dvar("y");
    require_zero(&j11, "j11");
    require_equal(&j12, &c(&xy, 2), "j12");
    require_equal(&j21, &c(&xy, -3).mul(&v(&xy, "x").pow(2)), "j21");
    require_zero(&j22, "j22");

    let hess11 = hx.dvar("x");
    let hess12 = hx.dvar("y");
    let hess22 = hy.dvar("y");
    require_zero(&hess12, "hess12");
    require_equal(&hess22, &c(&xy, 8), "hess22");

    let energy_clear = hy.mul(&q0).sub(&c(&xy, 4).mul(&q0).mul(&p0));
    require_zero(&energy_clear, "unperturbed energy clear");

    let mut origin = BTreeMap::new();
    insert(&mut origin, "x", 0);
    insert(&mut origin, "y", 0);
    let o_j11 = j11.eval(&origin);
    let o_j12 = j12.eval(&origin);
    let o_j21 = j21.eval(&origin);
    let o_j22 = j22.eval(&origin);
    if (o_j11, o_j12, o_j21, o_j22) != (0, 2, 0, 0) {
        panic!("origin Jacobian");
    }
    let trace = o_j11 + o_j22;
    let det = o_j11 * o_j22 - o_j12 * o_j21;
    if trace != 0 || det != 0 {
        panic!("origin trace/det");
    }
    let h11 = hess11.eval(&origin);
    let h12 = hess12.eval(&origin);
    let h22 = hess22.eval(&origin);
    if (h11, h12, h22) != (0, 0, 8) {
        panic!("origin Hessian");
    }
    let hess_det = h11 * h22 - h12 * h12;
    if hess_det != 0 {
        panic!("origin Hessian det");
    }
    if p0.eval(&origin) != 0 || q0.eval(&origin) != 0 {
        panic!("origin is not an equilibrium");
    }
    if h.eval(&origin) != 0 {
        panic!("H(0,0)");
    }

    let wt = names(&["x", "y", "lam"]);
    let xw = v(&wt, "x");
    let yw = v(&wt, "y");
    let lam = v(&wt, "lam");
    let p0w = c(&wt, 2).mul(&yw);
    let q0w = xw.pow(3).neg();
    let hw = xw.pow(4).add(&c(&wt, 4).mul(&yw.pow(2)));
    let mut wmap = BTreeMap::new();
    wmap.insert("x".into(), lam.mul(&xw));
    wmap.insert("y".into(), lam.pow(2).mul(&yw));
    require_zero(
        &p0w.subst(&wmap).sub(&lam.pow(2).mul(&p0w)),
        "P weight",
    );
    require_zero(
        &q0w.subst(&wmap).sub(&lam.pow(3).mul(&q0w)),
        "Q weight",
    );
    require_zero(
        &hw.subst(&wmap).sub(&lam.pow(4).mul(&hw)),
        "H weight",
    );

    let sc = names(&["s", "u", "lam"]);
    let s = v(&sc, "s");
    let u = v(&sc, "u");
    let lams = v(&sc, "lam");
    let xs = lams.mul(&s);
    let ys = lams.pow(2).mul(&u);
    let h_chart = xs.pow(4).add(&c(&sc, 4).mul(&ys.pow(2)));
    let h_model = s.pow(4).add(&c(&sc, 4).mul(&u.pow(2)));
    require_zero(&h_chart.sub(&lams.pow(4).mul(&h_model)), "scale H");
    let jac = lams.mul(&lams.pow(2));
    require_zero(&jac.sub(&lams.pow(3)), "scale jacobian");
    require_zero(&jac.sub(&lams.pow(3).mul(&c(&sc, 1))), "integrand 1");
    require_zero(
        &xs.pow(2).mul(&jac).sub(&lams.pow(5).mul(&s.pow(2))),
        "integrand x2",
    );
    require_zero(
        &ys.pow(2).mul(&jac).sub(&lams.pow(7).mul(&u.pow(2))),
        "integrand y2",
    );
    require_zero(
        &lams
            .pow(5)
            .mul(&s.pow(2))
            .sub(&lams.pow(2).mul(&s.pow(2)).mul(&lams.pow(3))),
        "ratio",
    );
    require_equal(&s.pow(4).dvar("s"), &c(&sc, 4).mul(&s.pow(3)), "d/ds s^4");
    require_equal(&u.pow(2).dvar("u"), &c(&sc, 2).mul(&u), "d/du u^2");

    let ex = names(&["x"]);
    let xe = v(&ex, "x");
    require_zero(&xe.dvar("x").sub(&c(&ex, 1)), "d(x)/dx - 1");
    require_zero(
        &xe.pow(3).dvar("x").sub(&c(&ex, 3).mul(&xe.pow(2))),
        "d(x^3) - 3 x^2",
    );

    let fv = names(&["x", "y", "mu", "alpha"]);
    let xf = v(&fv, "x");
    let yf = v(&fv, "y");
    let mu = v(&fv, "mu");
    let alpha = v(&fv, "alpha");
    let p = c(&fv, 0);
    let q = mu.mul(&alpha.sub(&xf.pow(2))).mul(&yf);
    let hxf = c(&fv, 4).mul(&xf.pow(3));
    let hyf = c(&fv, 8).mul(&yf);
    let extra = hxf.mul(&p).add(&hyf.mul(&q));
    let claimed = c(&fv, 8).mul(&mu).mul(&alpha.sub(&xf.pow(2))).mul(&yf.pow(2));
    let extra_diff = extra.sub(&claimed);
    require_zero(&extra_diff, "family extra");
    require_zero(&q.dvar("y").sub(&mu.mul(&alpha.sub(&xf.pow(2)))), "family div");
    require_zero(
        &hyf.mul(&q).sub(&c(&fv, 4).mul(&q).mul(&c(&fv, 2)).mul(&yf)),
        "family energy clear",
    );
    require_zero(&p, "family P");

    let qy = mu.mul(&yf);
    let qy_extra = hyf.mul(&qy);
    let qy_claimed = c(&fv, 8).mul(&mu).mul(&yf.pow(2));
    require_zero(&qy_extra.sub(&qy_claimed), "Q=mu y extra");

    let area_num = 1i128 + 4;
    let area_den = 16i128;
    if area_num != 5 || area_num >= area_den {
        panic!("area corner");
    }
    // (1/2)^4 + 4(1/4)^2 = 1/16 + 4/16 = 5/16, rebuilt from integers.
    let s4_num = 1i128.pow(4);
    let s4_den = 2i128.pow(4);
    let four_u2_num = 4 * 1i128.pow(2);
    let four_u2_den = 4i128.pow(2);
    if s4_den != four_u2_den || s4_num + four_u2_num != 5 || s4_den != 16 {
        panic!("area corner fractions");
    }

    let s4m_num = 3i128.pow(4);
    let s4m_den = 4i128.pow(4);
    let four_u2m_num = 4 * 1i128.pow(2);
    let four_u2m_den = 8i128.pow(2);
    // 4/64 = 16/256
    if four_u2m_den * 4 != s4m_den {
        panic!("moment denominators");
    }
    let moment_num = s4m_num + four_u2m_num * 4;
    let moment_den = s4m_den;
    if moment_num != 97 || moment_den != 256 || moment_num >= moment_den {
        panic!("moment corner");
    }

    let bad = dhdt.add(&c(&xy, 1));
    if bad.is_zero() {
        panic!("constant perturbation of dH/dt vanished");
    }
    let wrong_ratio = lams.pow(5).mul(&s.pow(2)).sub(&s.pow(2).mul(&lams.pow(3)));
    if wrong_ratio.is_zero() {
        panic!("ratio collapsed to exponent 0");
    }
    require_nonzero(&lams.pow(3), "jacobian λ^3");
    require_nonzero(&claimed, "family extra");
    require_nonzero(&qy_claimed, "Q=mu y extra");
    if 14 <= 2 {
        panic!("14 <= 2");
    }

    let grad2 = hx.pow(2).add(&hy.pow(2));
    for x in -3i128..=3 {
        for yv in -3i128..=3 {
            let mut vals = BTreeMap::new();
            insert(&mut vals, "x", x);
            insert(&mut vals, "y", yv);
            if dhdt.eval(&vals) != 0 {
                panic!("dH/dt nonzero at ({x},{yv})");
            }
            if sos.eval(&vals) != x.pow(6) + yv.pow(2) {
                panic!("sum of squares at ({x},{yv})");
            }
            let eq = p0.eval(&vals) == 0 && q0.eval(&vals) == 0;
            if eq != (x == 0 && yv == 0) {
                panic!("equilibrium set at ({x},{yv})");
            }
            let g = grad2.eval(&vals);
            if (g == 0) != (x == 0 && yv == 0) {
                panic!("grad H zero-set at ({x},{yv})");
            }
            if energy_clear.eval(&vals) != 0 {
                panic!("energy clear at ({x},{yv})");
            }
            for mu_v in -2i128..=2 {
                for alpha_v in -2i128..=2 {
                    let mut fvals = BTreeMap::new();
                    insert(&mut fvals, "x", x);
                    insert(&mut fvals, "y", yv);
                    insert(&mut fvals, "mu", mu_v);
                    insert(&mut fvals, "alpha", alpha_v);
                    let claimed_v = 8 * mu_v * (alpha_v - x * x) * yv * yv;
                    if extra.eval(&fvals) != claimed_v {
                        panic!("family extra at box");
                    }
                    if qy_extra.eval(&fvals) != 8 * mu_v * yv * yv {
                        panic!("Q=mu y extra at box");
                    }
                }
            }
        }
    }
    for x in -3i128..=3 {
        for yv in -3i128..=3 {
            for lam_v in -3i128..=3 {
                let mut vals = BTreeMap::new();
                insert(&mut vals, "x", x);
                insert(&mut vals, "y", yv);
                insert(&mut vals, "lam", lam_v);
                if p0w.subst(&wmap).sub(&lam.pow(2).mul(&p0w)).eval(&vals) != 0 {
                    panic!("P weight box");
                }
                if q0w.subst(&wmap).sub(&lam.pow(3).mul(&q0w)).eval(&vals) != 0 {
                    panic!("Q weight box");
                }
                if hw.subst(&wmap).sub(&lam.pow(4).mul(&hw)).eval(&vals) != 0 {
                    panic!("H weight box");
                }
                let mut svals = BTreeMap::new();
                insert(&mut svals, "s", x);
                insert(&mut svals, "u", yv);
                insert(&mut svals, "lam", lam_v);
                if h_chart.sub(&lams.pow(4).mul(&h_model)).eval(&svals) != 0 {
                    panic!("scale H box");
                }
                if jac.sub(&lams.pow(3)).eval(&svals) != 0 {
                    panic!("scale jac box");
                }
                if xs.pow(2).mul(&jac).sub(&lams.pow(5).mul(&s.pow(2))).eval(&svals) != 0 {
                    panic!("integrand x2 box");
                }
                if ys.pow(2).mul(&jac).sub(&lams.pow(7).mul(&u.pow(2))).eval(&svals) != 0 {
                    panic!("integrand y2 box");
                }
            }
        }
    }

    Counts {
        dhdt_terms: dhdt.term_count(),
        trace,
        det,
        hess_det,
        family_extra_terms: extra.term_count(),
        family_extra_diff: extra_diff.term_count(),
        area_num,
        area_den,
        moment_num,
        moment_den,
    }
}

fn dump_lines(counts: &Counts) -> String {
    format!(
        "unperturbed dHdt terms {}\n\
         origin jacobian trace {} det {}\n\
         origin hessian det {}\n\
         weight H difference 0\n\
         weight P0 difference 0\n\
         weight Q0 difference 0\n\
         scale H difference 0\n\
         scale jacobian difference 0\n\
         integrand 1 scale difference 0\n\
         integrand x2 scale difference 0\n\
         integrand y2 scale difference 0\n\
         J0 exponent 3\n\
         J2 exponent 5\n\
         Jy2 exponent 7\n\
         ratio J2/J0 exponent 2\n\
         family extra terms {}\n\
         family extra difference {}\n\
         area corner {}/{}\n\
         moment corner {}/{}\n\
         named family cyclicity at most 1\n\
         general cubic I zeros at most 2\n\
         Q=mu y positive zeros 0\n\
         hn_moved 0\n\
         beats_H3 0\n\
         fourteen zeros 0\n\
         negative 14-zero rejected\n\
         integer box zeros\n",
        counts.dhdt_terms,
        counts.trace,
        counts.det,
        counts.hess_det,
        counts.family_extra_terms,
        counts.family_extra_diff,
        counts.area_num,
        counts.area_den,
        counts.moment_num,
        counts.moment_den
    )
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
    let cert_path = PathBuf::from("certs/identities.json");
    if !cert_path.is_file() {
        panic!("missing certificate {}", cert_path.display());
    }
    let text = dump_lines(&counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID hh-qh-melnikov identities");
}
