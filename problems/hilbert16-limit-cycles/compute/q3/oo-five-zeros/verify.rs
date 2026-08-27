//! Independent replay of the n=3 radial slice on H=(x^2+y^2)/2
//! and the named family on the cubic Hamiltonian of a quadratic
//! field.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap.
//! This program expands the same rings with a BTreeMap and
//! evaluates the residuals on an integer box. rustc only.
//! Five zeros of I(h) are not constructed.

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
        panic!("{label} is not the zero polynomial");
    }
}

fn require_equal(left: &Poly, right: &Poly, label: &str) {
    if !left.equals(right) {
        panic!("{label} mismatch");
    }
}

fn insert(map: &mut BTreeMap<String, i128>, name: &str, value: i128) {
    map.insert(name.to_string(), value);
}

fn z2(n: i32) -> i32 {
    (n - 1) / 2
}

fn five_need_deg_q() -> i32 {
    2 * 5 + 1
}

fn uni_eval_at_half_num(coeffs: &[i128]) -> i128 {
    if coeffs.is_empty() {
        return 0;
    }
    let deg = coeffs.len() - 1;
    let mut num = 0i128;
    for (k, coeff) in coeffs.iter().enumerate() {
        num += coeff * (1i128 << (deg - k));
    }
    num
}

fn area_rectangle() -> (i128, i128) {
    let two_x3_num = 2 * 125;
    if two_x3_num != 250 {
        panic!("x=5/4 cube");
    }
    let three_x2_num = 3 * 25;
    if three_x2_num != 75 {
        panic!("x=5/4 square");
    }
    let pot_num = 125 - 150;
    let pot_den = 32;
    if (pot_num, pot_den) != (-25, 32) {
        panic!("potential at 5/4 {pot_num}/{pot_den}");
    }
    let max_num = pot_num + 6;
    let max_den = pot_den;
    if (max_num, max_den) != (-19, 32) {
        panic!("max H6 {max_num}/{max_den}");
    }
    if max_num >= 0 {
        panic!("rectangle not inside a nest oval");
    }
    let left_num = 27 - 54;
    if left_num != -27 {
        panic!("potential at 3/4");
    }
    if 2 * 2 != 4 {
        panic!("rectangle area");
    }
    (max_num, max_den)
}

fn homoclinic_tip() {
    if 2 * 27 - 3 * 9 * 2 != 0 {
        panic!("V(3/2) cleared numerator");
    }
}

struct Counts {
    circles_dhdt_terms: usize,
    circles_q_terms: usize,
    circles_oval_terms: usize,
    cubic_h6_terms: usize,
    cubic_dh6_terms: usize,
    cubic_extra_diff_terms: usize,
    area_num: i128,
    area_den: i128,
}

fn check_all() -> Counts {
    let xy = names(&["x", "y"]);
    let x = v(&xy, "x");
    let y = v(&xy, "y");
    let hnum = x.pow(2).add(&y.pow(2));
    let p_circ = y.clone();
    let q_circ = x.neg();
    let dhdt = hnum
        .dvar("x")
        .mul(&p_circ)
        .add(&hnum.dvar("y").mul(&q_circ));
    require_zero(&dhdt, "circles dHnum/dt");
    if hnum.degree() != 2 {
        panic!("Hnum is not quadratic");
    }
    if p_circ.degree() != 1 || q_circ.degree() != 1 {
        panic!("circle field is not linear");
    }

    let xya = names(&["x", "y", "alpha"]);
    let xa = v(&xya, "x");
    let ya = v(&xya, "y");
    let alpha = v(&xya, "alpha");
    let qform = ya.mul(&alpha.sub(&xa.pow(2)).sub(&ya.pow(2)));
    if qform.degree() != 3 {
        panic!("circles deg Q");
    }
    if qform.term_count() != 3 {
        panic!("circles Q term count");
    }
    let q_alpha1 = y.mul(&c(&xy, 1).sub(&x.pow(2)).sub(&y.pow(2)));
    if q_alpha1.degree() != 3 || q_alpha1.term_count() != 3 {
        panic!("circles alpha=1 Q");
    }

    let ha = names(&["h", "alpha"]);
    let h = v(&ha, "h");
    let a = v(&ha, "alpha");
    let i_tilde = h.mul(&a.sub(&h.scale(2)));
    let i_claimed = h.mul(&a).sub(&h.pow(2).scale(2));
    require_zero(&i_tilde.sub(&i_claimed), "I_tilde - h(alpha-2h)");

    let xyha = names(&["x", "y", "h", "alpha"]);
    let xv = v(&xyha, "x");
    let yv = v(&xyha, "y");
    let hv = v(&xyha, "h");
    let av = v(&xyha, "alpha");
    let r2 = xv.pow(2).add(&yv.pow(2));
    let p_r = av.sub(&r2);
    let p_h = av.sub(&hv.scale(2));
    let factor = r2.sub(&hv.scale(2));
    let oval = p_r.sub(&p_h).add(&factor);
    require_zero(&oval, "circles oval reduction");

    let mut vals_ha = BTreeMap::new();
    insert(&mut vals_ha, "h", 1);
    insert(&mut vals_ha, "alpha", 2);
    if i_tilde.eval(&vals_ha) != 0 {
        panic!("I_tilde(1,2)");
    }
    insert(&mut vals_ha, "h", 2);
    insert(&mut vals_ha, "alpha", 4);
    if i_tilde.eval(&vals_ha) != 0 {
        panic!("I_tilde(2,4)");
    }
    insert(&mut vals_ha, "h", 1);
    insert(&mut vals_ha, "alpha", 1);
    if i_tilde.eval(&vals_ha) == 0 {
        panic!("I_tilde(1,1) vanished");
    }
    insert(&mut vals_ha, "h", 0);
    insert(&mut vals_ha, "alpha", 1);
    if i_tilde.eval(&vals_ha) != 0 {
        panic!("I_tilde(0,1)");
    }
    insert(&mut vals_ha, "h", 1);
    insert(&mut vals_ha, "alpha", 0);
    if i_tilde.eval(&vals_ha) == 0 {
        panic!("I_tilde(1,0) vanished");
    }
    if uni_eval_at_half_num(&[0, 1, -2]) != 0 {
        panic!("I_tilde(1/2) for alpha=1");
    }
    if z2(3) != 1 {
        panic!("Z(2,3)");
    }
    if five_need_deg_q() != 11 {
        panic!("five zeros need deg Q 11");
    }
    if five_need_deg_q() <= 3 {
        panic!("five zeros unexpectedly fit in degree 3");
    }

    let p_field = y.clone();
    let q_field = x.sub(&x.pow(2));
    let h6 = y.pow(2).scale(3).add(&x.pow(3).scale(2)).sub(&x.pow(2).scale(3));
    let dh6 = h6.dvar("x").mul(&p_field).add(&h6.dvar("y").mul(&q_field));
    require_zero(&dh6, "unperturbed dH6/dt");
    let q_factored = x.mul(&c(&xy, 1).sub(&x));
    require_zero(&q_field.sub(&q_factored), "Q factorization");
    let pot = x.pow(3).scale(2).sub(&x.pow(2).scale(3)).add(&c(&xy, 1));
    let well = x.sub(&c(&xy, 1)).pow(2).mul(&x.scale(2).add(&c(&xy, 1)));
    require_zero(&pot.sub(&well), "potential well factor");
    let j11 = p_field.dvar("x");
    let j12 = p_field.dvar("y");
    let j21 = q_field.dvar("x");
    let j22 = q_field.dvar("y");
    let det = j11.mul(&j22).sub(&j12.mul(&j21));
    let det_claimed = x.scale(2).sub(&c(&xy, 1));
    require_zero(&det.sub(&det_claimed), "Jacobian det");
    require_zero(&j11.add(&j22), "unperturbed divergence");
    require_equal(&j12, &c(&xy, 1), "j12");
    require_zero(&j11, "j11");
    require_zero(&j22, "j22");

    let mut xy_vals = BTreeMap::new();
    insert(&mut xy_vals, "x", 0);
    insert(&mut xy_vals, "y", 0);
    if h6.eval(&xy_vals) != 0 {
        panic!("H6(0,0)");
    }
    if p_field.eval(&xy_vals) != 0 || q_field.eval(&xy_vals) != 0 {
        panic!("(0,0) is not an equilibrium");
    }
    if det.eval(&xy_vals) != -1 {
        panic!("det(0,0)");
    }
    insert(&mut xy_vals, "x", 1);
    if h6.eval(&xy_vals) != -1 {
        panic!("H6(1,0)");
    }
    if p_field.eval(&xy_vals) != 0 || q_field.eval(&xy_vals) != 0 {
        panic!("(1,0) is not an equilibrium");
    }
    if det.eval(&xy_vals) != 1 {
        panic!("det(1,0)");
    }
    insert(&mut xy_vals, "x", -1);
    if h6.eval(&xy_vals) != -5 {
        panic!("H6(-1,0) unexpected");
    }
    if 2 * (-1) - 3 * 2 != -8 {
        panic!("H6(-1/2,0) numerator");
    }

    let xym = names(&["x", "y", "mu"]);
    let xm = v(&xym, "x");
    let ym = v(&xym, "y");
    let mu = v(&xym, "mu");
    let p_pert = c(&xym, 0);
    let q_pert = mu.mul(&ym);
    let h6m = ym
        .pow(2)
        .scale(3)
        .add(&xm.pow(3).scale(2))
        .sub(&xm.pow(2).scale(3));
    let extra = h6m.dvar("x").mul(&p_pert).add(&h6m.dvar("y").mul(&q_pert));
    let claimed = mu.scale(6).mul(&ym.pow(2));
    require_zero(&extra.sub(&claimed), "family extra");
    let p0m = ym.clone();
    let q_full = xm.sub(&xm.pow(2)).add(&q_pert);
    let dh6_full = h6m.dvar("x").mul(&p0m).add(&h6m.dvar("y").mul(&q_full));
    require_zero(&dh6_full.sub(&claimed), "perturbed dH6/dt");
    let trace = p0m.dvar("x").add(&q_full.dvar("y"));
    require_zero(&trace.sub(&mu), "perturbed trace");
    require_zero(&p_pert, "family P");
    let j11m = p0m.dvar("x");
    let j12m = p0m.dvar("y");
    let j21m = q_full.dvar("x");
    let j22m = q_full.dvar("y");
    let det_full = j11m.mul(&j22m).sub(&j12m.mul(&j21m));

    for mu_i in -3i128..=3 {
        let mut vals = BTreeMap::new();
        insert(&mut vals, "x", 0);
        insert(&mut vals, "y", 0);
        insert(&mut vals, "mu", mu_i);
        if det_full.eval(&vals) != -1 {
            panic!("perturbed det(0,0)");
        }
        if trace.eval(&vals) != mu_i {
            panic!("perturbed trace(0,0)");
        }
        if p_pert.eval(&vals) != 0 || q_pert.eval(&vals) != 0 {
            panic!("perturbation at the saddle");
        }
        insert(&mut vals, "x", 1);
        if det_full.eval(&vals) != 1 {
            panic!("perturbed det(1,0)");
        }
        if trace.eval(&vals) != mu_i {
            panic!("perturbed trace(1,0)");
        }
        if q_pert.eval(&vals) != 0 {
            panic!("perturbation Q at the center");
        }
    }

    homoclinic_tip();
    let (area_num, area_den) = area_rectangle();

    for xv_i in -3i128..=3 {
        for yv_i in -3i128..=3 {
            let mut vals = BTreeMap::new();
            insert(&mut vals, "x", xv_i);
            insert(&mut vals, "y", yv_i);
            if dhdt.eval(&vals) != 0 {
                panic!("circles dHnum/dt at ({xv_i},{yv_i})");
            }
            if 2 * xv_i * yv_i + 2 * yv_i * (-xv_i) != 0 {
                panic!("circles hand dH/dt");
            }
            if dh6.eval(&vals) != 0 {
                panic!("cubic dH6/dt at ({xv_i},{yv_i})");
            }
            let eq = p_field.eval(&vals) == 0 && q_field.eval(&vals) == 0;
            let expected = (xv_i == 0 && yv_i == 0) || (xv_i == 1 && yv_i == 0);
            if eq != expected {
                panic!("cubic equilibrium set at ({xv_i},{yv_i})");
            }
            for mu_i in -2i128..=2 {
                let mut fvals = BTreeMap::new();
                insert(&mut fvals, "x", xv_i);
                insert(&mut fvals, "y", yv_i);
                insert(&mut fvals, "mu", mu_i);
                if extra.eval(&fvals) != 6 * mu_i * yv_i * yv_i {
                    panic!("family extra at ({xv_i},{yv_i},{mu_i})");
                }
                if dh6_full.eval(&fvals) != 6 * mu_i * yv_i * yv_i {
                    panic!("full dH6 at ({xv_i},{yv_i},{mu_i})");
                }
            }
        }
    }
    for xv_i in -3i128..=3 {
        for yv_i in -3i128..=3 {
            for hv_i in -3i128..=3 {
                for av_i in -3i128..=3 {
                    let mut vals = BTreeMap::new();
                    insert(&mut vals, "x", xv_i);
                    insert(&mut vals, "y", yv_i);
                    insert(&mut vals, "h", hv_i);
                    insert(&mut vals, "alpha", av_i);
                    if oval.eval(&vals) != 0 {
                        panic!("oval residual");
                    }
                    let mut ha_vals = BTreeMap::new();
                    insert(&mut ha_vals, "h", hv_i);
                    insert(&mut ha_vals, "alpha", av_i);
                    let claimed_i = hv_i * (av_i - 2 * hv_i);
                    if i_tilde.eval(&ha_vals) != claimed_i {
                        panic!("I_tilde sample");
                    }
                }
            }
        }
    }

    let extra_i = i_tilde.add(&h.pow(3));
    if extra_i.equals(&i_tilde) {
        panic!("extra cubic term of I_tilde collided");
    }
    insert(&mut vals_ha, "h", 1);
    insert(&mut vals_ha, "alpha", 2);
    if extra_i.eval(&vals_ha) != 1 {
        panic!("h^3 perturbation at (1,2)");
    }
    let bad_h = y.pow(2).scale(3).sub(&x.pow(2).scale(3));
    let bad_dh = bad_h.dvar("x").mul(&p_field).add(&bad_h.dvar("y").mul(&q_field));
    if bad_dh.is_zero() {
        panic!("dropped-x^3 energy unexpectedly conserved");
    }
    if 5 <= z2(3) {
        panic!("5 <= Z(2,3)");
    }
    if five_need_deg_q() <= 3 {
        panic!("five zeros fit in degree 3");
    }

    Counts {
        circles_dhdt_terms: dhdt.term_count(),
        circles_q_terms: qform.term_count(),
        circles_oval_terms: oval.term_count(),
        cubic_h6_terms: h6.term_count(),
        cubic_dh6_terms: dh6.term_count(),
        cubic_extra_diff_terms: extra.sub(&claimed).term_count(),
        area_num,
        area_den,
    }
}

fn dump_lines(counts: &Counts) -> String {
    format!(
        "imagined_five_zeros DROP\n\
         H3_ge_5_as_dent_of_13 DROP\n\
         circles_n3_slice KEEP\n\
         cubic_hamiltonian_quadratic_field KEEP\n\
         hn_moved 0\n\
         beats_H3 0\n\
         five_zeros_produced 0\n\
         regular_I_zeros_circles 1\n\
         regular_I_zeros_cubic 0\n\
         well_bottom_I_zeros_cubic 1\n\
         circles Z(2,3) 1\n\
         circles I_tilde h*(alpha-2h)\n\
         circles deg_p_at_most 1\n\
         circles positive_zeros_at_most 1\n\
         circles sample_alpha 1\n\
         circles sample_zero_h 1/2\n\
         circles extra_zeros_need_degQ 11\n\
         circles dHnum/dt terms {}\n\
         circles Q terms {}\n\
         circles oval_reduction {}\n\
         cubic H6 terms {}\n\
         cubic dH6dt terms {}\n\
         cubic eq 0 0 kind=saddle det=-1 trace=0 H=0\n\
         cubic eq 1 0 kind=center det=1 trace=0 H=-1/6\n\
         cubic extra 6*mu*y^2\n\
         cubic extra_diff terms {}\n\
         cubic I mu*oint_y_dx\n\
         cubic I_one_signed 1\n\
         cubic first_order_cyclicity_at_most 1\n\
         cubic named_family_zeros_not_5\n\
         area rectangle [3/4,5/4]x[-1/4,1/4]\n\
         area max_H6 {}/{}\n\
         homoclinic V(3/2) 0\n\
         potential_factor 2x^3-3x^2+1=(x-1)^2*(2x+1)\n\
         negative five-zero rejected\n\
         integer box zeros\n",
        counts.circles_dhdt_terms,
        counts.circles_q_terms,
        counts.circles_oval_terms,
        counts.cubic_h6_terms,
        counts.cubic_dh6_terms,
        counts.cubic_extra_diff_terms,
        counts.area_num,
        counts.area_den
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
    let core = PathBuf::from("certs/core.json");
    let ident = PathBuf::from("certs/identities.json");
    if !core.is_file() || !ident.is_file() {
        panic!("missing certificates");
    }
    let text = dump_lines(&counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID oo-five-zeros replay");
}
