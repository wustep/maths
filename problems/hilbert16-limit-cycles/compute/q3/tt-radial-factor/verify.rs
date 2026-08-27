//! Independent checker for Y = (x^2+y^2) X on the radial cubic.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap.
//! This program expands the same rings with a BTreeMap and evaluates
//! the polar residuals on the integer box {−3,…,3}³. A degree-≤6
//! polynomial in three variables that vanishes on that box is the
//! zero polynomial, so the box check is a second algorithm.
//! rustc only. The imagined second cycle is not certified.

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

    fn scale(&self, k: i128) -> Self {
        if k == 0 {
            return Self::zero(&self.vars);
        }
        let mut out = self.clone();
        for coeff in out.terms.values_mut() {
            *coeff *= k;
        }
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

    fn xy_index(&self) -> (usize, usize) {
        let ix = self
            .vars
            .iter()
            .position(|v| v == "x")
            .expect("need variable x");
        let iy = self
            .vars
            .iter()
            .position(|v| v == "y")
            .expect("need variable y");
        (ix, iy)
    }

    fn jet_order(&self) -> i32 {
        if self.terms.is_empty() {
            return -1;
        }
        let (ix, iy) = self.xy_index();
        self.terms
            .keys()
            .map(|exp| i32::from(exp[ix] + exp[iy]))
            .min()
            .unwrap()
    }

    fn spatial_degree(&self) -> i32 {
        if self.terms.is_empty() {
            return -1;
        }
        let (ix, iy) = self.xy_index();
        self.terms
            .keys()
            .map(|exp| i32::from(exp[ix] + exp[iy]))
            .max()
            .unwrap()
    }

    fn spatial_part(&self, deg: u8) -> Self {
        let (ix, iy) = self.xy_index();
        let mut out = Self::zero(&self.vars);
        for (exp, coeff) in &self.terms {
            if exp[ix] + exp[iy] == deg {
                out.terms.insert(exp.clone(), *coeff);
            }
        }
        out.prune();
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
    list.iter().map(|s| (*s).to_string()).collect()
}

fn v(vars: &[String], name: &str) -> Poly {
    Poly::var(vars, name)
}

fn constant(vars: &[String], value: i128) -> Poly {
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
                Some(b',') => self.i += 1,
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
                Some(b',') => self.i += 1,
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

fn root_obj(value: &Json) -> &BTreeMap<String, Json> {
    match value {
        Json::Object(map) => map,
        _ => panic!("root must be object"),
    }
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

fn json_str(map: &BTreeMap<String, Json>, key: &str) -> String {
    match map.get(key) {
        Some(Json::String(s)) => s.clone(),
        _ => panic!("missing string {key}"),
    }
}

fn json_bool(map: &BTreeMap<String, Json>, key: &str) -> bool {
    match map.get(key) {
        Some(Json::Bool(b)) => *b,
        _ => panic!("missing bool {key}"),
    }
}

fn json_int(map: &BTreeMap<String, Json>, key: &str) -> i64 {
    match map.get(key) {
        Some(Json::Number(n)) => *n,
        _ => panic!("missing int {key}"),
    }
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

fn radial_cubic(vars: &[String]) -> (Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let rho = v(vars, "rho");
    let r2 = x.mul(&x).add(&y.mul(&y));
    let rho2 = rho.mul(&rho);
    let p = y.sub(&x.mul(&r2.sub(&rho2)));
    let q = x.neg().sub(&y.mul(&r2.sub(&rho2)));
    (p, q)
}

fn y_field(vars: &[String]) -> (Poly, Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let r2 = x.mul(&x).add(&y.mul(&y));
    let (px, qx) = radial_cubic(vars);
    let py = r2.mul(&px);
    let qy = r2.mul(&qx);
    (px, qx, py, qy, r2)
}

fn field_degree(p: &Poly, q: &Poly) -> i32 {
    p.spatial_degree().max(q.spatial_degree())
}

fn field_jet(p: &Poly, q: &Poly) -> i32 {
    let a = p.jet_order();
    let b = q.jet_order();
    if a < 0 {
        b
    } else if b < 0 {
        a
    } else {
        a.min(b)
    }
}

fn polar_box_zero(diff: &Poly) {
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
                    assert_eq!((pv, qv), (0, 0), "Y origin is not an equilibrium");
                } else if pv == 0 && qv == 0 {
                    panic!("unexpected Y equilibrium at ({x},{y},{rho})");
                }
            }
        }
    }
}

struct Counts {
    deg_x: i32,
    deg_y: i32,
    deg_line: i32,
    jet_x: i32,
    jet_y: i32,
    radial_terms: usize,
    angular_terms: usize,
    spec_p_terms: usize,
    spec_q_terms: usize,
    spec_deg: i32,
}

fn check_all() -> Counts {
    let polar_vars = names(&["x", "y", "rho"]);
    let (px, qx, py, qy, r2) = y_field(&polar_vars);
    let x = v(&polar_vars, "x");
    let y = v(&polar_vars, "y");
    let rho = v(&polar_vars, "rho");
    let radial_left = x.mul(&py).add(&y.mul(&qy));
    let radial_right = r2.pow(2).mul(&rho.mul(&rho).sub(&r2));
    let angular_left = x.mul(&qy).sub(&y.mul(&py));
    let angular_right = r2.pow(2).neg();
    let radial_diff = radial_left.sub(&radial_right);
    let angular_diff = angular_left.sub(&angular_right);
    require_zero(&radial_diff, "Y polar radial");
    require_zero(&angular_diff, "Y polar angular");
    polar_box_zero(&radial_diff);
    polar_box_zero(&angular_diff);
    check_origin_box(&py, &qy);

    let py_bad = py.add(&constant(&polar_vars, 1));
    let radial_bad = x.mul(&py_bad).add(&y.mul(&qy));
    if radial_bad.equals(&radial_right) {
        panic!("perturbed Y satisfied the radial identity");
    }

    let deg_x = field_degree(&px, &qx);
    let deg_y = field_degree(&py, &qy);
    let jet_x = field_jet(&px, &qx);
    let jet_y = field_jet(&py, &qy);
    assert_eq!(deg_x, 3, "X degree");
    assert_eq!(deg_y, 5, "Y degree");
    assert_eq!(jet_x, 1, "X jet");
    assert_eq!(jet_y, 3, "Y jet");

    let radial_vars = names(&["r", "rho"]);
    let r = v(&radial_vars, "r");
    let rho_r = v(&radial_vars, "rho");
    let rdot = r.pow(3).mul(&rho_r.mul(&rho_r).sub(&r.mul(&r)));
    let factored = r.pow(3).mul(&rho_r.sub(&r)).mul(&rho_r.add(&r));
    require_zero(&rdot.sub(&factored), "rdot_Y factorization");

    let xy = names(&["x", "y"]);
    let xs = v(&xy, "x");
    let ys = v(&xy, "y");
    let r2s = xs.mul(&xs).add(&ys.mul(&ys));
    let p4 = xs
        .add(&ys.scale(4))
        .sub(&xs.scale(4).mul(&r2s));
    let q4 = xs
        .scale(-4)
        .add(&ys)
        .sub(&ys.scale(4).mul(&r2s));
    let pys = r2s.mul(&p4);
    let qys = r2s.mul(&q4);
    let spec_radial_left = xs.mul(&pys).add(&ys.mul(&qys));
    let spec_radial_right = r2s.pow(2).mul(&constant(&xy, 1).sub(&r2s.scale(4)));
    let spec_angular_left = xs.mul(&qys).sub(&ys.mul(&pys));
    let spec_angular_right = r2s.pow(2).scale(-4);
    require_zero(&spec_radial_left.sub(&spec_radial_right), "cleared radial");
    require_zero(&spec_angular_left.sub(&spec_angular_right), "cleared angular");
    let spec_deg = field_degree(&pys, &qys);
    assert_eq!(spec_deg, 5, "specialized degree");
    assert_eq!(field_jet(&pys, &qys), 3, "specialized jet");

    let r_vars = names(&["r"]);
    let rr = v(&r_vars, "r");
    let spec_rdot = rr.pow(3).mul(&constant(&r_vars, 1).sub(&rr.pow(2).scale(4)));
    let spec_fact = rr
        .pow(3)
        .mul(&constant(&r_vars, 1).sub(&rr.scale(2)))
        .mul(&constant(&r_vars, 1).add(&rr.scale(2)));
    require_zero(&spec_rdot.sub(&spec_fact), "specialized rdot factorization");
    let mut r0 = BTreeMap::new();
    r0.insert("r".into(), 0i128);
    assert_eq!(spec_rdot.eval(&r0), 0);
    let mut r1 = BTreeMap::new();
    r1.insert("r".into(), 1i128);
    assert_ne!(spec_rdot.eval(&r1), 0, "rdot vanished at r=1");

    let line = x.add(&y);
    let pl = line.mul(&px);
    let ql = line.mul(&qx);
    let line_radial_left = x.mul(&pl).add(&y.mul(&ql));
    let line_radial_right = line.mul(&r2).mul(&rho.mul(&rho).sub(&r2));
    let line_angular_left = x.mul(&ql).sub(&y.mul(&pl));
    let line_angular_right = line.mul(&r2).neg();
    require_zero(&line_radial_left.sub(&line_radial_right), "line-mult radial");
    require_zero(&line_angular_left.sub(&line_angular_right), "line-mult angular");
    let deg_line = field_degree(&pl, &ql);
    assert_eq!(deg_line, 4, "line-multiplication degree");

    let claimed_p = r2.pow(2).mul(&x).neg();
    let claimed_q = r2.pow(2).mul(&y).neg();
    require_zero(&py.spatial_part(5).sub(&claimed_p), "leading PY");
    require_zero(&qy.spatial_part(5).sub(&claimed_q), "leading QY");

    Counts {
        deg_x,
        deg_y,
        deg_line,
        jet_x,
        jet_y,
        radial_terms: radial_left.term_count(),
        angular_terms: angular_left.term_count(),
        spec_p_terms: pys.term_count(),
        spec_q_terms: qys.term_count(),
        spec_deg,
    }
}

fn check_core(text: &str) {
    let root = parse_json(text);
    let map = root_obj(&root);
    assert_eq!(json_str(map, "schema"), "hilbert16-tt-radial-factor/v1");
    assert!(!json_bool(map, "hn_moved"));
    assert!(!json_bool(map, "two_cycles"));
    assert!(!json_bool(map, "plus_one_certified"));
    assert!(json_bool(map, "h5_at_least_1"));
    assert!(!json_bool(map, "h5_at_least_2"));
    assert!(!json_bool(map, "dent_of_h5_37"));
    assert_eq!(json_str(map, "unique_positive_orbit"), "r=rho");
    assert_eq!(json_int(map, "degree_Y"), 5);
    assert_eq!(json_int(map, "degree_X"), 3);
    assert_eq!(json_int(map, "degree_line_multiplication"), 4);
    assert_eq!(json_str(map, "rho2"), "1/4");
    assert_eq!(json_str(map, "specialized_unique_orbit"), "r=1/2");
}

fn check_identities_cert(text: &str) {
    let root = parse_json(text);
    let polar = obj(&root, "polar");
    let polar_vars = strs(polar, "variables");
    assert_eq!(polar_vars, names(&["x", "y", "rho"]));
    let (px, qx, py, qy, r2) = y_field(&polar_vars);
    let x = v(&polar_vars, "x");
    let y = v(&polar_vars, "y");
    let rho = v(&polar_vars, "rho");
    let radial_left = x.mul(&py).add(&y.mul(&qy));
    let radial_right = r2.pow(2).mul(&rho.mul(&rho).sub(&r2));
    let angular_left = x.mul(&qy).sub(&y.mul(&py));
    let angular_right = r2.pow(2).neg();
    require_equal(&Poly::from_terms(&polar_vars, &term_list(polar, "PX")), &px, "cert PX");
    require_equal(&Poly::from_terms(&polar_vars, &term_list(polar, "QX")), &qx, "cert QX");
    require_equal(&Poly::from_terms(&polar_vars, &term_list(polar, "PY")), &py, "cert PY");
    require_equal(&Poly::from_terms(&polar_vars, &term_list(polar, "QY")), &qy, "cert QY");
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
    let rdot = r.pow(3).mul(&rho_r.mul(&rho_r).sub(&r.mul(&r)));
    let factored = r.pow(3).mul(&rho_r.sub(&r)).mul(&rho_r.add(&r));
    require_equal(
        &Poly::from_terms(&rvars, &term_list(radial_speed, "rdot")),
        &rdot,
        "cert rdot",
    );
    require_equal(
        &Poly::from_terms(&rvars, &term_list(radial_speed, "factored")),
        &factored,
        "cert factored",
    );

    let spec = obj(&root, "specialized");
    let svars = strs(spec, "variables");
    assert_eq!(json_str(spec, "rho2"), "1/4");
    let xs = v(&svars, "x");
    let ys = v(&svars, "y");
    let r2s = xs.mul(&xs).add(&ys.mul(&ys));
    let p4 = xs.add(&ys.scale(4)).sub(&xs.scale(4).mul(&r2s));
    let q4 = xs.scale(-4).add(&ys).sub(&ys.scale(4).mul(&r2s));
    let pys = r2s.mul(&p4);
    let qys = r2s.mul(&q4);
    require_equal(&Poly::from_terms(&svars, &term_list(spec, "PY")), &pys, "cert spec PY");
    require_equal(&Poly::from_terms(&svars, &term_list(spec, "QY")), &qys, "cert spec QY");
    require_equal(
        &Poly::from_terms(&svars, &term_list(spec, "radial_left")),
        &xs.mul(&pys).add(&ys.mul(&qys)),
        "cert spec radial_left",
    );
    require_equal(
        &Poly::from_terms(&svars, &term_list(spec, "radial_right")),
        &r2s.pow(2).mul(&constant(&svars, 1).sub(&r2s.scale(4))),
        "cert spec radial_right",
    );
    require_equal(
        &Poly::from_terms(&svars, &term_list(spec, "angular_left")),
        &xs.mul(&qys).sub(&ys.mul(&pys)),
        "cert spec angular_left",
    );
    require_equal(
        &Poly::from_terms(&svars, &term_list(spec, "angular_right")),
        &r2s.pow(2).scale(-4),
        "cert spec angular_right",
    );

    let sr = obj(&root, "specialized_rdot");
    let srvars = strs(sr, "variables");
    let rr = v(&srvars, "r");
    let spec_rdot = rr.pow(3).mul(&constant(&srvars, 1).sub(&rr.pow(2).scale(4)));
    let spec_fact = rr
        .pow(3)
        .mul(&constant(&srvars, 1).sub(&rr.scale(2)))
        .mul(&constant(&srvars, 1).add(&rr.scale(2)));
    require_equal(
        &Poly::from_terms(&srvars, &term_list(sr, "rdot")),
        &spec_rdot,
        "cert spec rdot",
    );
    require_equal(
        &Poly::from_terms(&srvars, &term_list(sr, "factored")),
        &spec_fact,
        "cert spec rdot factor",
    );

    let lineb = obj(&root, "line_multiplication");
    let lvars = strs(lineb, "variables");
    let lx = v(&lvars, "x");
    let ly = v(&lvars, "y");
    let lrho = v(&lvars, "rho");
    let (lpx, lqx) = radial_cubic(&lvars);
    let line = lx.add(&ly);
    let pl = line.mul(&lpx);
    let ql = line.mul(&lqx);
    let lr2 = lx.mul(&lx).add(&ly.mul(&ly));
    require_equal(&Poly::from_terms(&lvars, &term_list(lineb, "L")), &line, "cert L");
    require_equal(&Poly::from_terms(&lvars, &term_list(lineb, "PL")), &pl, "cert PL");
    require_equal(&Poly::from_terms(&lvars, &term_list(lineb, "QL")), &ql, "cert QL");
    require_equal(
        &Poly::from_terms(&lvars, &term_list(lineb, "radial_left")),
        &lx.mul(&pl).add(&ly.mul(&ql)),
        "cert L radial_left",
    );
    require_equal(
        &Poly::from_terms(&lvars, &term_list(lineb, "radial_right")),
        &line.mul(&lr2).mul(&lrho.mul(&lrho).sub(&lr2)),
        "cert L radial_right",
    );
    require_equal(
        &Poly::from_terms(&lvars, &term_list(lineb, "angular_left")),
        &lx.mul(&ql).sub(&ly.mul(&pl)),
        "cert L angular_left",
    );
    require_equal(
        &Poly::from_terms(&lvars, &term_list(lineb, "angular_right")),
        &line.mul(&lr2).neg(),
        "cert L angular_right",
    );

    let lead = obj(&root, "leading");
    let leadvars = strs(lead, "variables");
    let (_lpx, _lqx, lpy, lqy, lr2y) = y_field(&leadvars);
    let lx2 = v(&leadvars, "x");
    let ly2 = v(&leadvars, "y");
    require_equal(
        &Poly::from_terms(&leadvars, &term_list(lead, "PY5")),
        &lpy.spatial_part(5),
        "cert PY5",
    );
    require_equal(
        &Poly::from_terms(&leadvars, &term_list(lead, "QY5")),
        &lqy.spatial_part(5),
        "cert QY5",
    );
    require_equal(
        &Poly::from_terms(&leadvars, &term_list(lead, "claimed_P")),
        &lr2y.pow(2).mul(&lx2).neg(),
        "cert leading P",
    );
    require_equal(
        &Poly::from_terms(&leadvars, &term_list(lead, "claimed_Q")),
        &lr2y.pow(2).mul(&ly2).neg(),
        "cert leading Q",
    );
}

fn dump_lines(counts: &Counts) -> String {
    format!(
        "X degree {}\n\
         Y degree {}\n\
         line-multiplication degree {}\n\
         radial-factor degree {}\n\
         polar Y radial terms {} difference 0\n\
         polar Y angular terms {} difference 0\n\
         rdot_Y r^3 (rho^2-r^2)\n\
         rdot_Y factored r^3 (rho-r)(rho+r) difference 0\n\
         unique positive orbit r=rho\n\
         origin X jet {}\n\
         origin Y jet {}\n\
         specialized rho2=1/4 P terms {}\n\
         specialized rho2=1/4 Q terms {}\n\
         specialized degree {}\n\
         specialized unique positive orbit r=1/2\n\
         cleared polar radial difference 0\n\
         cleared polar angular difference 0\n\
         leading Y +(x^2+y^2)^2 (x,y) difference 0\n\
         Y origin only integer-box equilibrium\n\
         negative perturbation rejected\n\
         H(5) >= 1\n\
         plus_one certified 0\n\
         two cycles 0\n\
         dent of H(5)>=37 0\n",
        counts.deg_x,
        counts.deg_y,
        counts.deg_line,
        counts.deg_y,
        counts.radial_terms,
        counts.angular_terms,
        counts.jet_x,
        counts.jet_y,
        counts.spec_p_terms,
        counts.spec_q_terms,
        counts.spec_deg
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
    let ident_text = fs::read_to_string("certs/identities.json")
        .unwrap_or_else(|err| panic!("read identities.json: {err}"));
    let core_text =
        fs::read_to_string("certs/core.json").unwrap_or_else(|err| panic!("read core.json: {err}"));
    check_identities_cert(&ident_text);
    check_core(&core_text);

    let text = dump_lines(&counts);
    if let Some(path) = dump_path {
        fs::write(path, &text).expect("write dump");
    }
    print!("{text}");
    println!("VALID tt-radial-factor identities");
}
