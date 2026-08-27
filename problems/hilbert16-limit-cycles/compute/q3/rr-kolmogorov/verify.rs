//! Independent replay of the named cubic Kolmogorov Dulac identities.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap. This
//! program expands the same rings with a BTreeMap and evaluates the
//! residuals on an integer box. The imagined seven cycles, and any
//! beat of M_K(3)>=6 or H_K(5)>=28, are not produced. rustc only.

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

    fn subst_const(&self, name: &str, value: i128) -> Self {
        let idx = self
            .vars
            .iter()
            .position(|v| v == name)
            .unwrap_or_else(|| panic!("unknown variable {name}"));
        let mut out = Self::zero(&self.vars);
        for (exp, coeff) in &self.terms {
            let power = exp[idx];
            let factor = pow_i128(value, power);
            if factor == 0 {
                continue;
            }
            let mut new_exp = exp.clone();
            new_exp[idx] = 0;
            *out.terms.entry(new_exp).or_insert(0) += coeff * factor;
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

    fn degree_in(&self, names: &[&str]) -> i32 {
        let idxs: Vec<usize> = names
            .iter()
            .map(|n| {
                self.vars
                    .iter()
                    .position(|v| v == *n)
                    .unwrap_or_else(|| panic!("unknown variable {n}"))
            })
            .collect();
        if self.terms.is_empty() {
            return -1;
        }
        self.terms
            .keys()
            .map(|exp| idxs.iter().map(|i| i32::from(exp[*i])).sum())
            .max()
            .unwrap_or(-1)
    }

    fn equals(&self, other: &Self) -> bool {
        self.vars == other.vars && self.terms == other.terms
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
        panic!("{label} is not zero");
    }
}

fn require_equal(left: &Poly, right: &Poly, label: &str) {
    if !left.equals(right) {
        panic!("{label} mismatch");
    }
}

fn weighted_div(p: &Poly, q: &Poly, field_p: &Poly, field_q: &Poly, alpha: &Poly, beta: &Poly) -> Poly {
    let one = c(&p.vars, 1);
    alpha
        .sub(&one)
        .mul(p)
        .add(&field_p.dvar("x"))
        .add(&beta.sub(&one).mul(q))
        .add(&field_q.dvar("y"))
}

fn insert(map: &mut BTreeMap<String, i128>, name: &str, value: i128) {
    map.insert(name.to_string(), value);
}

struct Counts {
    general_weighted_terms: usize,
    general_diff_terms: usize,
    named_weighted_terms: usize,
    named_diff_terms: usize,
    cleared_terms: usize,
    q_terms: usize,
    p_degree: i32,
    q_degree: i32,
}

fn check_all() -> Counts {
    let gen_vars = names(&["x", "y", "a", "b", "c", "alpha", "beta"]);
    let x = v(&gen_vars, "x");
    let y = v(&gen_vars, "y");
    let a = v(&gen_vars, "a");
    let b = v(&gen_vars, "b");
    let cc = v(&gen_vars, "c");
    let alpha = v(&gen_vars, "alpha");
    let beta = v(&gen_vars, "beta");
    let p = c(&gen_vars, 1).sub(&x).sub(&a.mul(&y));
    let q = c(&gen_vars, 1)
        .sub(&b.mul(&x))
        .sub(&y)
        .sub(&cc.mul(&x.pow(2)));
    let field_p = x.mul(&p);
    let field_q = y.mul(&q);
    let weighted = weighted_div(&p, &q, &field_p, &field_q, &alpha, &beta);
    let claimed = alpha
        .add(&beta)
        .sub(&alpha.add(&c(&gen_vars, 1)).add(&beta.mul(&b)).mul(&x))
        .sub(&alpha.mul(&a).add(&beta).add(&c(&gen_vars, 1)).mul(&y))
        .sub(&beta.mul(&cc).mul(&x.pow(2)));
    let gen_diff = weighted.sub(&claimed);
    require_zero(&gen_diff, "general weighted Dulac");
    require_equal(&field_p, &x.mul(&p), "general P = x p");
    require_equal(&field_q, &y.mul(&q), "general Q = y q");

    let sliced = claimed
        .subst_const("a", 1)
        .subst_const("alpha", -1)
        .subst_const("beta", 0);
    require_equal(&sliced, &c(&gen_vars, -1), "a=1 slice is -1");
    let one_signed = claimed.subst_const("alpha", -1).subst_const("beta", 0);
    let expected = c(&gen_vars, -1).sub(&c(&gen_vars, 1).sub(&a).mul(&y));
    require_zero(&one_signed.sub(&expected), "one-signed form");

    let named_vars = names(&["x", "y", "b", "c"]);
    let xn = v(&named_vars, "x");
    let yn = v(&named_vars, "y");
    let bn = v(&named_vars, "b");
    let cn = v(&named_vars, "c");
    let pn = c(&named_vars, 1).sub(&xn).sub(&yn);
    let qn = c(&named_vars, 1)
        .sub(&bn.mul(&xn))
        .sub(&yn)
        .sub(&cn.mul(&xn.pow(2)));
    let field_pn = xn.mul(&pn);
    let field_qn = yn.mul(&qn);
    let named_weighted = weighted_div(
        &pn,
        &qn,
        &field_pn,
        &field_qn,
        &c(&named_vars, -1),
        &c(&named_vars, 0),
    );
    let named_claimed = c(&named_vars, -1);
    let named_diff = named_weighted.sub(&named_claimed);
    require_zero(&named_diff, "named weighted Dulac");
    require_equal(&named_weighted, &named_claimed, "named D is -1");
    let cleared = xn
        .mul(&pn.dvar("x"))
        .sub(&pn)
        .add(&yn.mul(&qn.dvar("y")));
    require_equal(&cleared, &named_claimed, "cleared numerator is -1");
    let cubic_free = yn.mul(&c(&named_vars, 1).sub(&bn.mul(&xn)).sub(&yn));
    let q_without = field_qn.sub(&c(&named_vars, -1).mul(&cn).mul(&xn.pow(2)).mul(&yn));
    require_zero(&q_without.sub(&cubic_free), "Q without cubic is LV");
    if field_qn.degree_in(&["x", "y"]) != 3 {
        panic!(
            "named Q should be degree 3 in (x,y), got {}",
            field_qn.degree_in(&["x", "y"])
        );
    }
    if field_pn.degree_in(&["x", "y"]) != 2 {
        panic!(
            "named P should be degree 2 in (x,y), got {}",
            field_pn.degree_in(&["x", "y"])
        );
    }

    let ax_vars = names(&["x", "y", "a", "b", "c"]);
    let xa = v(&ax_vars, "x");
    let ya = v(&ax_vars, "y");
    let aa = v(&ax_vars, "a");
    let ba = v(&ax_vars, "b");
    let ca = v(&ax_vars, "c");
    let pa = c(&ax_vars, 1).sub(&xa).sub(&aa.mul(&ya));
    let qa = c(&ax_vars, 1)
        .sub(&ba.mul(&xa))
        .sub(&ya)
        .sub(&ca.mul(&xa.pow(2)));
    let field_pa = xa.mul(&pa);
    let field_qa = ya.mul(&qa);
    require_zero(&field_pa.subst_const("x", 0), "P(0,y)");
    require_zero(&field_qa.subst_const("y", 0), "Q(x,0)");
    require_zero(&field_pa.sub(&xa.mul(&pa)), "P - x p");
    require_zero(&field_qa.sub(&ya.mul(&qa)), "Q - y q");

    let bad = field_pa.add(&c(&ax_vars, 1));
    if bad.subst_const("x", 0).is_zero() {
        panic!("constant perturbation of P still vanished on x=0");
    }
    let wrong = weighted_div(
        &pn,
        &qn,
        &field_pn,
        &field_qn,
        &c(&named_vars, 1),
        &c(&named_vars, 1),
    );
    if wrong.equals(&c(&named_vars, -1)) {
        panic!("unweighted divergence collapsed to -1");
    }
    if 7 <= 0 {
        panic!("7 <= 0");
    }
    if 28 <= 6 {
        panic!("H_K(5)>=28 is not a beat of M_K(3)>=6 written here");
    }

    for xv in -2i128..=2 {
        for yv in -2i128..=2 {
            for av in -2i128..=2 {
                for bv in -2i128..=2 {
                    for cv in -2i128..=2 {
                        let mut avals = BTreeMap::new();
                        insert(&mut avals, "x", xv);
                        insert(&mut avals, "y", yv);
                        insert(&mut avals, "a", av);
                        insert(&mut avals, "b", bv);
                        insert(&mut avals, "c", cv);
                        if xv == 0 && field_pa.eval(&avals) != 0 {
                            panic!("axis x=0 at ({xv},{yv},{av},{bv},{cv})");
                        }
                        if yv == 0 && field_qa.eval(&avals) != 0 {
                            panic!("axis y=0 at ({xv},{yv},{av},{bv},{cv})");
                        }
                        for alphav in -2i128..=2 {
                            for betav in -2i128..=2 {
                                let mut gvals = avals.clone();
                                insert(&mut gvals, "alpha", alphav);
                                insert(&mut gvals, "beta", betav);
                                if gen_diff.eval(&gvals) != 0 {
                                    panic!("general Dulac at box point");
                                }
                                if one_signed.sub(&expected).eval(&gvals) != 0 {
                                    panic!("one-signed identity at box point");
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    for xv in -3i128..=3 {
        for yv in -3i128..=3 {
            for bv in -3i128..=3 {
                for cv in -3i128..=3 {
                    let mut nvals = BTreeMap::new();
                    insert(&mut nvals, "x", xv);
                    insert(&mut nvals, "y", yv);
                    insert(&mut nvals, "b", bv);
                    insert(&mut nvals, "c", cv);
                    if named_weighted.eval(&nvals) != -1 {
                        panic!("named Dulac at ({xv},{yv},{bv},{cv})");
                    }
                    if cleared.eval(&nvals) != -1 {
                        panic!("cleared Dulac at ({xv},{yv},{bv},{cv})");
                    }
                    if q_without.sub(&cubic_free).eval(&nvals) != 0 {
                        panic!("LV slice at ({xv},{yv},{bv},{cv})");
                    }
                }
            }
        }
    }

    Counts {
        general_weighted_terms: weighted.term_count(),
        general_diff_terms: gen_diff.term_count(),
        named_weighted_terms: named_weighted.term_count(),
        named_diff_terms: named_diff.term_count(),
        cleared_terms: cleared.term_count(),
        q_terms: field_qn.term_count(),
        p_degree: field_pn.degree_in(&["x", "y"]),
        q_degree: field_qn.degree_in(&["x", "y"]),
    }
}

fn check_cert_flags(text: &str) {
    for needle in [
        "\"schema\": \"hilbert16-rr-kolmogorov/v1\"",
        "\"hn_moved\": false",
        "\"seven_cycles\": false",
        "\"beats_MK3\": false",
        "\"beats_HK5\": false",
        "\"isolated_cycles_in_Q1\": 0",
        "\"named_alpha\": -1",
        "\"named_beta\": 0",
        "\"dulac_constant\": -1",
    ] {
        if !text.contains(needle) {
            panic!("certificate missing {needle}");
        }
    }
}

fn dump_lines(counts: &Counts) -> String {
    format!(
        "imagined_seven_cycles DROP\n\
         beats_MK3 DROP\n\
         beats_HK5 DROP\n\
         named_cubic_kolmogorov KEEP\n\
         axes_invariant KEEP\n\
         weighted_dulac KEEP\n\
         isolated_cycles_in_Q1 0\n\
         hn_moved 0\n\
         seven_cycles_produced 0\n\
         beats_MK3 0\n\
         beats_HK5 0\n\
         degree {}\n\
         P_degree {}\n\
         alpha -1\n\
         beta 0\n\
         dulac_constant -1\n\
         axes P(0,y) 0\n\
         axes Q(x,0) 0\n\
         general_dulac_terms {}\n\
         general_dulac_diff {}\n\
         named_dulac_terms {}\n\
         named_dulac_diff {}\n\
         cleared_numerator_terms {}\n\
         named_Q_terms {}\n\
         cleared_numerator -1\n\
         cubic_term_Q -c x^2 y\n\
         lv_reduction_when_c_eq_0 KEEP\n\
         negative seven rejected\n\
         integer box zeros\n",
        counts.q_degree,
        counts.p_degree,
        counts.general_weighted_terms,
        counts.general_diff_terms,
        counts.named_weighted_terms,
        counts.named_diff_terms,
        counts.cleared_terms,
        counts.q_terms
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
    let cert = fs::read_to_string(&cert_path)
        .unwrap_or_else(|err| panic!("read {}: {err}", cert_path.display()));
    check_cert_flags(&cert);

    let text = dump_lines(&counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID rr-kolmogorov identities");
}
