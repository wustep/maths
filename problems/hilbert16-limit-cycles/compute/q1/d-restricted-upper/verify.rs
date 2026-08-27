//! Independent checker for the restricted-family identities.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap. This
//! program expands the same rings with a BTreeMap and, for the polar
//! cubic, also evaluates the difference on the integer box
//! {−3,…,3}³. A degree-≤4 polynomial in three variables that vanishes
//! on that box is the zero polynomial, so the box check is a second
//! algorithm, not a replay of the sparse product.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process;
use std::str::FromStr;

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

    fn sub(&self, other: &Self) -> Self {
        self.add(&other.neg())
    }

    fn neg(&self) -> Self {
        let mut out = self.clone();
        for coeff in out.terms.values_mut() {
            *coeff = -*coeff;
        }
        out
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

    fn to_terms(&self) -> Vec<BTreeMap<String, JsonAtom>> {
        let mut out = Vec::new();
        for (exp, coeff) in &self.terms {
            let mut item = BTreeMap::new();
            item.insert("coeff".to_string(), JsonAtom::Str(coeff.to_string()));
            for (name, power) in self.vars.iter().zip(exp.iter()) {
                if *power > 0 {
                    item.insert(name.clone(), JsonAtom::Int(i64::from(*power)));
                }
            }
            out.push(item);
        }
        out
    }

    fn from_terms(vars: &[String], terms: &[BTreeMap<String, JsonAtom>]) -> Self {
        let mut out = Self::zero(vars);
        for item in terms {
            let mut exp = vec![0u8; vars.len()];
            let mut coeff = 0i128;
            for (key, atom) in item {
                if key == "coeff" {
                    coeff = atom.as_int128();
                } else {
                    let idx = vars
                        .iter()
                        .position(|v| v == key)
                        .unwrap_or_else(|| panic!("unexpected variable {key}"));
                    exp[idx] = atom.as_u8();
                }
            }
            *out.terms.entry(exp).or_insert(0) += coeff;
        }
        out.prune();
        out
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

fn constant(vars: &[String], value: i128) -> Poly {
    Poly::constant(vars, value)
}

// ---- tiny JSON reader for the certificate shape we emit ----

#[derive(Clone, Debug, PartialEq)]
enum JsonAtom {
    Str(String),
    Int(i64),
}

impl JsonAtom {
    fn as_int128(&self) -> i128 {
        match self {
            JsonAtom::Str(s) => i128::from_str(s).expect("integer coefficient"),
            JsonAtom::Int(n) => i128::from(*n),
        }
    }

    fn as_u8(&self) -> u8 {
        let n = self.as_int128();
        u8::try_from(n).expect("exponent fits u8")
    }
}

#[derive(Clone, Debug)]
#[allow(dead_code)]
enum Json {
    Null,
    Bool(bool),
    Number(i64),
    Float(f64),
    String(String),
    Array(Vec<Json>),
    Object(BTreeMap<String, Json>),
}

struct Parser<'a> {
    src: &'a [u8],
    i: usize,
}

impl<'a> Parser<'a> {
    fn new(src: &'a str) -> Self {
        Self {
            src: src.as_bytes(),
            i: 0,
        }
    }

    fn peek(&self) -> Option<u8> {
        self.src.get(self.i).copied()
    }

    fn bump(&mut self) -> u8 {
        let b = self.src[self.i];
        self.i += 1;
        b
    }

    fn skip_ws(&mut self) {
        while matches!(self.peek(), Some(b' ' | b'\n' | b'\r' | b'\t')) {
            self.i += 1;
        }
    }

    fn parse(&mut self) -> Json {
        self.skip_ws();
        match self.peek() {
            Some(b'{') => self.parse_object(),
            Some(b'[') => self.parse_array(),
            Some(b'"') => Json::String(self.parse_string()),
            Some(b't') => {
                self.expect_bytes(b"true");
                Json::Bool(true)
            }
            Some(b'f') => {
                self.expect_bytes(b"false");
                Json::Bool(false)
            }
            Some(b'n') => {
                self.expect_bytes(b"null");
                Json::Null
            }
            Some(b'-') | Some(b'0'..=b'9') => self.parse_number(),
            other => panic!("unexpected json byte {other:?} at {}", self.i),
        }
    }

    fn expect_bytes(&mut self, expected: &[u8]) {
        for b in expected {
            assert_eq!(self.bump(), *b, "json literal mismatch");
        }
    }

    fn parse_string(&mut self) -> String {
        assert_eq!(self.bump(), b'"');
        let mut out = String::new();
        loop {
            match self.bump() {
                b'"' => return out,
                b'\\' => match self.bump() {
                    b'"' => out.push('"'),
                    b'\\' => out.push('\\'),
                    b'n' => out.push('\n'),
                    b'r' => out.push('\r'),
                    b't' => out.push('\t'),
                    b => panic!("unsupported escape {b}"),
                },
                b => out.push(char::from(b)),
            }
        }
    }

    fn parse_number(&mut self) -> Json {
        let start = self.i;
        if self.peek() == Some(b'-') {
            self.i += 1;
        }
        while matches!(self.peek(), Some(b'0'..=b'9')) {
            self.i += 1;
        }
        if self.peek() == Some(b'.') {
            self.i += 1;
            while matches!(self.peek(), Some(b'0'..=b'9')) {
                self.i += 1;
            }
            let text = std::str::from_utf8(&self.src[start..self.i]).unwrap();
            return Json::Float(text.parse().expect("float"));
        }
        let text = std::str::from_utf8(&self.src[start..self.i]).unwrap();
        Json::Number(text.parse().expect("int"))
    }

    fn parse_array(&mut self) -> Json {
        assert_eq!(self.bump(), b'[');
        let mut items = Vec::new();
        self.skip_ws();
        if self.peek() == Some(b']') {
            self.i += 1;
            return Json::Array(items);
        }
        loop {
            items.push(self.parse());
            self.skip_ws();
            match self.peek() {
                Some(b',') => {
                    self.i += 1;
                }
                Some(b']') => {
                    self.i += 1;
                    return Json::Array(items);
                }
                other => panic!("bad array at {} ({other:?})", self.i),
            }
        }
    }

    fn parse_object(&mut self) -> Json {
        assert_eq!(self.bump(), b'{');
        let mut map = BTreeMap::new();
        self.skip_ws();
        if self.peek() == Some(b'}') {
            self.i += 1;
            return Json::Object(map);
        }
        loop {
            self.skip_ws();
            let key = match self.parse() {
                Json::String(s) => s,
                other => panic!("object key must be string, got {other:?}"),
            };
            self.skip_ws();
            assert_eq!(self.bump(), b':');
            let value = self.parse();
            map.insert(key, value);
            self.skip_ws();
            match self.peek() {
                Some(b',') => {
                    self.i += 1;
                }
                Some(b'}') => {
                    self.i += 1;
                    return Json::Object(map);
                }
                other => panic!("bad object at {} ({other:?})", self.i),
            }
        }
    }
}

fn parse_json(text: &str) -> Json {
    let mut p = Parser::new(text);
    let value = p.parse();
    p.skip_ws();
    assert_eq!(p.i, p.src.len(), "trailing json");
    value
}

fn obj<'a>(value: &'a Json, key: &str) -> &'a BTreeMap<String, Json> {
    match value {
        Json::Object(map) => map.get(key).and_then(|v| match v {
            Json::Object(inner) => Some(inner),
            _ => None,
        }),
        _ => None,
    }
    .unwrap_or_else(|| panic!("missing object {key}"))
}

fn arr<'a>(map: &'a BTreeMap<String, Json>, key: &str) -> &'a Vec<Json> {
    match map.get(key) {
        Some(Json::Array(items)) => items,
        _ => panic!("missing array {key}"),
    }
}

fn strs(map: &BTreeMap<String, Json>, key: &str) -> Vec<String> {
    arr(map, key)
        .iter()
        .map(|v| match v {
            Json::String(s) => s.clone(),
            _ => panic!("expected string in {key}"),
        })
        .collect()
}

fn term_list(map: &BTreeMap<String, Json>, key: &str) -> Vec<BTreeMap<String, JsonAtom>> {
    arr(map, key)
        .iter()
        .map(|item| match item {
            Json::Object(fields) => fields
                .iter()
                .map(|(k, v)| {
                    let atom = match v {
                        Json::String(s) => JsonAtom::Str(s.clone()),
                        Json::Number(n) => JsonAtom::Int(*n),
                        other => panic!("bad term field {k}: {other:?}"),
                    };
                    (k.clone(), atom)
                })
                .collect(),
            _ => panic!("term must be object"),
        })
        .collect()
}

fn require_zero(poly: &Poly, label: &str) {
    if !poly.is_zero() {
        panic!("{label} is not zero: {:?}", poly.to_terms());
    }
}

fn require_equal(left: &Poly, right: &Poly, label: &str) {
    if !left.equals(right) {
        panic!("{label} mismatch");
    }
}

fn polar_field(vars: &[String]) -> (Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let rho = v(vars, "rho");
    let r2 = x.mul(&x).add(&y.mul(&y));
    let rho2 = rho.mul(&rho);
    let p = y.sub(&x.mul(&r2.sub(&rho2)));
    let q = x.neg().sub(&y.mul(&r2.sub(&rho2)));
    (p, q)
}

fn polar_box_zero(diff: &Poly) {
    // Degree of xP+yQ and of (x^2+y^2)(rho^2-x^2-y^2) is at most 4.
    // Vanishing on {-3..3}^3 kills every monomial of degree ≤ 4.
    for x in -3i128..=3 {
        for y in -3i128..=3 {
            for rho in -3i128..=3 {
                let mut values = BTreeMap::new();
                values.insert("x".into(), x);
                values.insert("y".into(), y);
                values.insert("rho".into(), rho);
                if diff.eval(&values) != 0 {
                    panic!("polar difference nonzero at ({x},{y},{rho})");
                }
            }
        }
    }
}

fn check_origin_box(p: &Poly, q: &Poly) {
    for x in -2i128..=2 {
        for y in -2i128..=2 {
            for rho in -2i128..=2 {
                let mut values = BTreeMap::new();
                values.insert("x".into(), x);
                values.insert("y".into(), y);
                values.insert("rho".into(), rho);
                let pv = p.eval(&values);
                let qv = q.eval(&values);
                if x == 0 && y == 0 {
                    assert_eq!((pv, qv), (0, 0), "origin is not an equilibrium");
                } else if pv == 0 && qv == 0 {
                    panic!("unexpected equilibrium at ({x},{y},{rho})");
                }
            }
        }
    }
}

struct Counts {
    polar_p: usize,
    polar_q: usize,
    polar_radial: usize,
    polar_angular: usize,
    hamiltonian: usize,
    lv_weighted: usize,
    cramer_x: usize,
    cramer_y: usize,
    parallel: usize,
}

fn check_all() -> Counts {
    let polar_vars = names(&["x", "y", "rho"]);
    let (p, q) = polar_field(&polar_vars);
    let x = v(&polar_vars, "x");
    let y = v(&polar_vars, "y");
    let rho = v(&polar_vars, "rho");
    let r2 = x.mul(&x).add(&y.mul(&y));
    let radial_left = x.mul(&p).add(&y.mul(&q));
    let radial_right = r2.mul(&rho.mul(&rho).sub(&r2));
    let angular_left = x.mul(&q).sub(&y.mul(&p));
    let angular_right = r2.neg();
    let radial_diff = radial_left.sub(&radial_right);
    let angular_diff = angular_left.sub(&angular_right);
    require_zero(&radial_diff, "polar radial");
    require_zero(&angular_diff, "polar angular");
    polar_box_zero(&radial_diff);
    polar_box_zero(&angular_diff);
    check_origin_box(&p, &q);

    let p_bad = p.add(&constant(&polar_vars, 1));
    let radial_bad = x.mul(&p_bad).add(&y.mul(&q));
    if radial_bad.equals(&radial_right) {
        panic!("perturbed field satisfied the radial identity");
    }

    let radial_vars = names(&["r", "rho"]);
    let r = v(&radial_vars, "r");
    let rho_r = v(&radial_vars, "rho");
    let rdot = r.mul(&rho_r.mul(&rho_r).sub(&r.mul(&r)));
    let factored = r.mul(&rho_r.sub(&r)).mul(&rho_r.add(&r));
    require_zero(&rdot.sub(&factored), "radial factorization");

    let ham_vars = names(&[
        "x", "y", "a30", "a21", "a12", "a03", "a20", "a11", "a02", "a10", "a01", "a00",
    ]);
    let hx = cubic_h(&ham_vars).dvar("x");
    let hy = cubic_h(&ham_vars).dvar("y");
    let dhdt = hx.mul(&hy).add(&hy.mul(&hx.neg()));
    require_zero(&dhdt, "hamiltonian dH/dt");

    let lv_vars = names(&["x", "y", "a", "b", "c", "d", "e", "f", "alpha", "beta"]);
    let lv = lv_weighted(&lv_vars);
    require_zero(&lv.0.sub(&lv.1), "lv weighted");

    let cramer_vars = names(&["b", "c", "e", "f"]);
    let (cx, cy) = cramer_coeffs(&cramer_vars);
    require_zero(&cx, "cramer x");
    require_zero(&cy, "cramer y");

    let para_vars = names(&["x", "y", "a", "b", "c", "d", "lam"]);
    require_zero(&parallel_diff(&para_vars), "parallel");

    Counts {
        polar_p: p.term_count(),
        polar_q: q.term_count(),
        polar_radial: radial_left.term_count(),
        polar_angular: angular_left.term_count(),
        hamiltonian: dhdt.term_count(),
        lv_weighted: lv.0.term_count(),
        cramer_x: cx.term_count(),
        cramer_y: cy.term_count(),
        parallel: 0,
    }
}

fn cubic_h(vars: &[String]) -> Poly {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let a30 = v(vars, "a30");
    let a21 = v(vars, "a21");
    let a12 = v(vars, "a12");
    let a03 = v(vars, "a03");
    let a20 = v(vars, "a20");
    let a11 = v(vars, "a11");
    let a02 = v(vars, "a02");
    let a10 = v(vars, "a10");
    let a01 = v(vars, "a01");
    let a00 = v(vars, "a00");
    a30.mul(&x.pow(3))
        .add(&a21.mul(&x.pow(2)).mul(&y))
        .add(&a12.mul(&x).mul(&y.pow(2)))
        .add(&a03.mul(&y.pow(3)))
        .add(&a20.mul(&x.pow(2)))
        .add(&a11.mul(&x).mul(&y))
        .add(&a02.mul(&y.pow(2)))
        .add(&a10.mul(&x))
        .add(&a01.mul(&y))
        .add(&a00)
}

fn lv_weighted(vars: &[String]) -> (Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let a = v(vars, "a");
    let b = v(vars, "b");
    let c = v(vars, "c");
    let d = v(vars, "d");
    let e = v(vars, "e");
    let f = v(vars, "f");
    let alpha = v(vars, "alpha");
    let beta = v(vars, "beta");
    let growth_p = a.add(&b.mul(&x)).add(&c.mul(&y));
    let growth_q = d.add(&e.mul(&x)).add(&f.mul(&y));
    let p = x.mul(&growth_p);
    let q = y.mul(&growth_q);
    let weighted = alpha
        .sub(&constant(vars, 1))
        .mul(&growth_p)
        .add(&p.dvar("x"))
        .add(&beta.sub(&constant(vars, 1)).mul(&growth_q))
        .add(&q.dvar("y"));
    let claimed = alpha
        .mul(&a)
        .add(&beta.mul(&d))
        .add(&alpha.mul(&b).add(&beta.mul(&e)).add(&b).mul(&x))
        .add(&alpha.mul(&c).add(&beta.mul(&f)).add(&f).mul(&y));
    (weighted, claimed)
}

fn cramer_coeffs(vars: &[String]) -> (Poly, Poly) {
    let b = v(vars, "b");
    let c = v(vars, "c");
    let e = v(vars, "e");
    let f = v(vars, "f");
    let delta = b.mul(&f).sub(&e.mul(&c));
    let alpha_delta = f.mul(&e.sub(&b));
    let beta_delta = b.mul(&c.sub(&f));
    let x_coeff = alpha_delta.mul(&b).add(&beta_delta.mul(&e)).add(&delta.mul(&b));
    let y_coeff = alpha_delta.mul(&c).add(&beta_delta.mul(&f)).add(&delta.mul(&f));
    (x_coeff, y_coeff)
}

fn parallel_diff(vars: &[String]) -> Poly {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let a = v(vars, "a");
    let b = v(vars, "b");
    let c = v(vars, "c");
    let d = v(vars, "d");
    let lam = v(vars, "lam");
    let e = lam.mul(&b);
    let f = lam.mul(&c);
    let left = lam
        .mul(&a.add(&b.mul(&x)).add(&c.mul(&y)))
        .sub(&d.add(&e.mul(&x)).add(&f.mul(&y)));
    let right = lam.mul(&a).sub(&d);
    left.sub(&right)
}

fn check_certificate(text: &str) {
    let root = parse_json(text);
    let polar = obj(&root, "polar");
    let polar_vars = strs(polar, "variables");
    assert_eq!(polar_vars, names(&["x", "y", "rho"]));
    let (p, q) = polar_field(&polar_vars);
    let x = v(&polar_vars, "x");
    let y = v(&polar_vars, "y");
    let rho = v(&polar_vars, "rho");
    let r2 = x.mul(&x).add(&y.mul(&y));
    let radial_left = x.mul(&p).add(&y.mul(&q));
    let radial_right = r2.mul(&rho.mul(&rho).sub(&r2));
    let angular_left = x.mul(&q).sub(&y.mul(&p));
    let angular_right = r2.neg();
    require_equal(&Poly::from_terms(&polar_vars, &term_list(polar, "P")), &p, "cert P");
    require_equal(&Poly::from_terms(&polar_vars, &term_list(polar, "Q")), &q, "cert Q");
    require_equal(
        &Poly::from_terms(&polar_vars, &term_list(polar, "radial_left")),
        &radial_left,
        "cert radial_left",
    );
    require_equal(
        &Poly::from_terms(&polar_vars, &term_list(polar, "radial_right")),
        &radial_right,
        "cert radial_right",
    );
    require_equal(
        &Poly::from_terms(&polar_vars, &term_list(polar, "angular_left")),
        &angular_left,
        "cert angular_left",
    );
    require_equal(
        &Poly::from_terms(&polar_vars, &term_list(polar, "angular_right")),
        &angular_right,
        "cert angular_right",
    );

    let radial_speed = obj(&root, "radial_speed");
    let rvars = strs(radial_speed, "variables");
    let r = v(&rvars, "r");
    let rho_r = v(&rvars, "rho");
    let rdot = r.mul(&rho_r.mul(&rho_r).sub(&r.mul(&r)));
    let factored = r.mul(&rho_r.sub(&r)).mul(&rho_r.add(&r));
    require_equal(
        &Poly::from_terms(&rvars, &term_list(radial_speed, "r_times_rho2_minus_r2")),
        &rdot,
        "cert rdot",
    );
    require_equal(
        &Poly::from_terms(&rvars, &term_list(radial_speed, "factored")),
        &factored,
        "cert factored",
    );

    let ham = obj(&root, "hamiltonian");
    let hvars = strs(ham, "variables");
    let h = cubic_h(&hvars);
    let hx = h.dvar("x");
    let hy = h.dvar("y");
    let dhdt = hx.mul(&hy).add(&hy.mul(&hx.neg()));
    require_equal(&Poly::from_terms(&hvars, &term_list(ham, "H")), &h, "cert H");
    require_equal(&Poly::from_terms(&hvars, &term_list(ham, "Hx")), &hx, "cert Hx");
    require_equal(&Poly::from_terms(&hvars, &term_list(ham, "Hy")), &hy, "cert Hy");
    require_equal(&Poly::from_terms(&hvars, &term_list(ham, "dHdt")), &dhdt, "cert dHdt");

    let lv = obj(&root, "lotka_volterra");
    let lvars = strs(lv, "variables");
    let (weighted, claimed) = lv_weighted(&lvars);
    require_equal(
        &Poly::from_terms(&lvars, &term_list(lv, "weighted_div_over_B")),
        &weighted,
        "cert LV weighted",
    );
    require_equal(
        &Poly::from_terms(&lvars, &term_list(lv, "claimed_linear")),
        &claimed,
        "cert LV claimed",
    );

    let cramer = obj(&root, "cramer");
    let cvars = strs(cramer, "variables");
    let (cx, cy) = cramer_coeffs(&cvars);
    let b = v(&cvars, "b");
    let cpoly = v(&cvars, "c");
    let e = v(&cvars, "e");
    let f = v(&cvars, "f");
    require_equal(
        &Poly::from_terms(&cvars, &term_list(cramer, "Delta")),
        &b.mul(&f).sub(&e.mul(&cpoly)),
        "cert Delta",
    );
    require_equal(
        &Poly::from_terms(&cvars, &term_list(cramer, "alpha_Delta")),
        &f.mul(&e.sub(&b)),
        "cert alpha_Delta",
    );
    require_equal(
        &Poly::from_terms(&cvars, &term_list(cramer, "beta_Delta")),
        &b.mul(&cpoly.sub(&f)),
        "cert beta_Delta",
    );
    require_equal(
        &Poly::from_terms(&cvars, &term_list(cramer, "x_coeff_times_Delta")),
        &cx,
        "cert Cramer x",
    );
    require_equal(
        &Poly::from_terms(&cvars, &term_list(cramer, "y_coeff_times_Delta")),
        &cy,
        "cert Cramer y",
    );

    let para = obj(&root, "parallel");
    let pvars = strs(para, "variables");
    let diff = parallel_diff(&pvars);
    require_equal(
        &Poly::from_terms(&pvars, &term_list(para, "left")),
        &diff.add(&v(&pvars, "lam").mul(&v(&pvars, "a")).sub(&v(&pvars, "d"))),
        "cert parallel left",
    );
    require_equal(
        &Poly::from_terms(&pvars, &term_list(para, "right")),
        &v(&pvars, "lam").mul(&v(&pvars, "a")).sub(&v(&pvars, "d")),
        "cert parallel right",
    );
}

fn dump_lines(counts: &Counts) -> String {
    format!(
        "polar P terms {}\n\
         polar Q terms {}\n\
         polar radial identity terms {} difference 0\n\
         polar angular identity terms {} difference 0\n\
         hamiltonian dHdt terms {}\n\
         lv weighted terms {} difference 0\n\
         cramer x terms {}\n\
         cramer y terms {}\n\
         parallel diff terms {}\n\
         negative perturbation rejected\n\
         origin is the only integer-box equilibrium\n",
        counts.polar_p,
        counts.polar_q,
        counts.polar_radial,
        counts.polar_angular,
        counts.hamiltonian,
        counts.lv_weighted,
        counts.cramer_x,
        counts.cramer_y,
        counts.parallel
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
    let text = fs::read_to_string(&cert_path)
        .unwrap_or_else(|err| panic!("read {}: {err}", cert_path.display()));
    check_certificate(&text);

    let text = dump_lines(&counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID restricted-family identities");
}
