//! Independent checker for the Prohens–Torregrosa Darboux seed and
//! the quadratic contact identities.
//!
//! Python (`verify.py`) expands with sympy. This program expands the
//! same rings with a BTreeMap, computes Res_y as a 4×4 Sylvester
//! determinant, and evaluates the cleared dH/dt numerator on the
//! integer box {−6,…,6}².

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

    fn degree(&self) -> i32 {
        if self.terms.is_empty() {
            return -1;
        }
        self.terms
            .keys()
            .map(|exp| exp.iter().map(|p| i32::from(*p)).sum::<i32>())
            .max()
            .unwrap()
    }

    fn degree_in(&self, name: &str) -> i32 {
        let idx = self
            .vars
            .iter()
            .position(|v| v == name)
            .unwrap_or_else(|| panic!("unknown variable {name}"));
        if self.terms.is_empty() {
            return -1;
        }
        self.terms
            .keys()
            .map(|exp| i32::from(exp[idx]))
            .max()
            .unwrap()
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

    fn content(&self) -> i128 {
        let mut g: Option<i128> = None;
        for coeff in self.terms.values() {
            let a = coeff.abs();
            g = Some(match g {
                None => a,
                Some(cur) => gcd_i128(cur, a),
            });
        }
        g.unwrap_or(0)
    }
}

fn gcd_i128(mut a: i128, mut b: i128) -> i128 {
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a.abs()
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

fn json_i64(map: &BTreeMap<String, Json>, key: &str) -> i64 {
    match map.get(key) {
        Some(Json::Number(n)) => *n,
        _ => panic!("missing number {key}"),
    }
}

fn int_list(map: &BTreeMap<String, Json>, key: &str) -> Vec<i64> {
    arr(map, key)
        .iter()
        .map(|v| match v {
            Json::Number(n) => *n,
            _ => panic!("expected number in {key}"),
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

// ---- identities ----

fn a_poly(vars: &[String]) -> Poly {
    let x = v(vars, "x");
    let y = v(vars, "y");
    x.pow(4)
        .scale(2)
        .sub(&x.pow(2))
        .add(&y.pow(2))
        .sub(&x.scale(2))
        .sub(&constant(vars, 2))
}

fn b_poly(vars: &[String]) -> Poly {
    let x = v(vars, "x");
    let y = v(vars, "y");
    x.pow(5)
        .scale(8)
        .sub(&x.pow(3).scale(5))
        .add(&x.mul(&y.pow(2)).scale(5))
        .sub(&x.pow(2).scale(10))
        .sub(&x.scale(5))
        .sub(&constant(vars, 4))
}

struct Darboux {
    inner: Poly,
    p_raw: Poly,
    q_raw: Poly,
    p: Poly,
    q: Poly,
    numer: Poly,
}

fn darboux_field(vars: &[String]) -> Darboux {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let a = a_poly(vars);
    let b = b_poly(vars);
    let ax = a.dvar("x");
    let ay = a.dvar("y");
    let bx = b.dvar("x");
    let by = b.dvar("y");
    require_equal(&ay, &y.scale(2), "A_y");
    require_equal(&by, &x.mul(&y).scale(10), "B_y");
    let claimed_ax = x
        .pow(3)
        .scale(8)
        .sub(&x.scale(2))
        .sub(&constant(vars, 2));
    require_equal(&ax, &claimed_ax, "A_x");
    let claimed_bx = x
        .pow(4)
        .scale(40)
        .sub(&x.pow(2).scale(15))
        .add(&y.pow(2).scale(5))
        .sub(&x.scale(20))
        .sub(&constant(vars, 5));
    require_equal(&bx, &claimed_bx, "B_x");

    let inner = b.neg().add(&x.scale(4).mul(&a));
    let p_raw = b.scale(-5).mul(&ay).add(&a.scale(4).mul(&by));
    let q_raw = b.scale(5).mul(&ax).sub(&a.scale(4).mul(&bx));
    require_equal(&p_raw, &y.scale(10).mul(&inner), "P_raw = 10 y inner");
    assert_eq!(p_raw.content(), 10, "P_raw content");
    assert_eq!(q_raw.content(), 10, "Q_raw content");
    let p = p_raw.scale(1).terms.iter().fold(Poly::zero(vars), |acc, (e, c)| {
        let mut one = Poly::zero(vars);
        one.terms.insert(e.clone(), c / 10);
        acc.add(&one)
    });
    let q = q_raw.terms.iter().fold(Poly::zero(vars), |acc, (e, c)| {
        let mut one = Poly::zero(vars);
        one.terms.insert(e.clone(), c / 10);
        acc.add(&one)
    });
    let claimed_p = y.mul(
        &x.pow(3)
            .add(&x.pow(2).scale(2))
            .sub(&x.mul(&y.pow(2)))
            .sub(&x.scale(3))
            .add(&constant(vars, 4)),
    );
    let claimed_q = x
        .pow(4)
        .scale(15)
        .sub(&x.pow(3).scale(21))
        .add(&x.pow(2).mul(&y.pow(2)).scale(3))
        .sub(&x.pow(2).scale(15))
        .add(&x.mul(&y.pow(2)).scale(7))
        .sub(&x.scale(11))
        .sub(&y.pow(4).scale(2))
        .add(&y.pow(2).scale(6));
    require_equal(&p, &claimed_p, "primitive P");
    require_equal(&q, &claimed_q, "primitive Q");

    let numer = b
        .scale(5)
        .mul(&ax)
        .sub(&a.scale(4).mul(&bx))
        .mul(&p)
        .add(&b.scale(5).mul(&ay).sub(&a.scale(4).mul(&by)).mul(&q));
    Darboux {
        inner,
        p_raw,
        q_raw,
        p,
        q,
        numer,
    }
}

fn eval_xy(poly: &Poly, x: i128, y: i128) -> i128 {
    let mut values = BTreeMap::new();
    values.insert("x".into(), x);
    values.insert("y".into(), y);
    poly.eval(&values)
}

fn jacobian_at(p: &Poly, q: &Poly, x: i128, y: i128) -> (i128, i128, i128, i128) {
    (
        eval_xy(&p.dvar("x"), x, y),
        eval_xy(&p.dvar("y"), x, y),
        eval_xy(&q.dvar("x"), x, y),
        eval_xy(&q.dvar("y"), x, y),
    )
}

fn dhdt_box_zero(numer: &Poly) {
    // Degree of the cleared numerator is at most 12. Vanishing on
    // {-6..6}² kills every bivariate monomial of degree ≤ 12.
    for x in -6i128..=6 {
        for y in -6i128..=6 {
            if eval_xy(numer, x, y) != 0 {
                panic!("dH/dt numerator nonzero at ({x},{y})");
            }
        }
    }
}

fn cubic20(vars: &[String]) -> (Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let h = x
        .pow(4)
        .scale(-8)
        .sub(&y.pow(4))
        .sub(&x.pow(3).scale(4))
        .add(&x.pow(2).scale(2))
        .add(&y.pow(2).scale(2));
    let p = y.pow(3).sub(&y);
    let q = x.pow(3).scale(-8).sub(&x.pow(2).scale(3)).add(&x);
    let dhdt = h.dvar("x").mul(&p).add(&h.dvar("y").mul(&q));
    (h, p, q, dhdt)
}

fn generic_quadratic(vars: &[String]) -> (Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p = v(vars, "a00")
        .add(&v(vars, "a10").mul(&x))
        .add(&v(vars, "a01").mul(&y))
        .add(&v(vars, "a20").mul(&x.pow(2)))
        .add(&v(vars, "a11").mul(&x).mul(&y))
        .add(&v(vars, "a02").mul(&y.pow(2)));
    let q = v(vars, "b00")
        .add(&v(vars, "b10").mul(&x))
        .add(&v(vars, "b01").mul(&y))
        .add(&v(vars, "b20").mul(&x.pow(2)))
        .add(&v(vars, "b11").mul(&x).mul(&y))
        .add(&v(vars, "b02").mul(&y.pow(2)));
    (p, q)
}

fn coeff_in_y(poly: &Poly, power: u8) -> Poly {
    let y_idx = poly
        .vars
        .iter()
        .position(|n| n == "y")
        .expect("y variable");
    let rest: Vec<String> = poly
        .vars
        .iter()
        .cloned()
        .filter(|n| n != "y")
        .collect();
    let mut out = Poly::zero(&rest);
    for (exp, coeff) in &poly.terms {
        if exp[y_idx] != power {
            continue;
        }
        let mut new_exp = Vec::new();
        for (i, pwr) in exp.iter().enumerate() {
            if i != y_idx {
                new_exp.push(*pwr);
            }
        }
        *out.terms.entry(new_exp).or_insert(0) += *coeff;
    }
    out.prune();
    out
}

fn lift_to(poly: &Poly, vars: &[String]) -> Poly {
    let mut out = Poly::zero(vars);
    for (exp, coeff) in &poly.terms {
        let mut new_exp = vec![0u8; vars.len()];
        for (name, power) in poly.vars.iter().zip(exp.iter()) {
            if *power == 0 {
                continue;
            }
            let idx = vars
                .iter()
                .position(|v| v == name)
                .unwrap_or_else(|| panic!("lift missing {name}"));
            new_exp[idx] = *power;
        }
        *out.terms.entry(new_exp).or_insert(0) += *coeff;
    }
    out.prune();
    out
}

fn det_matrix(m: &[Vec<Poly>]) -> Poly {
    let n = m.len();
    assert!(n > 0);
    if n == 1 {
        return m[0][0].clone();
    }
    if n == 2 {
        return m[0][0].mul(&m[1][1]).sub(&m[0][1].mul(&m[1][0]));
    }
    let vars = &m[0][0].vars;
    let mut acc = Poly::zero(vars);
    for j in 0..n {
        let mut minor = Vec::new();
        for i in 1..n {
            let mut row = Vec::new();
            for k in 0..n {
                if k != j {
                    row.push(m[i][k].clone());
                }
            }
            minor.push(row);
        }
        let cof = if j % 2 == 0 {
            m[0][j].clone()
        } else {
            m[0][j].neg()
        };
        acc = acc.add(&cof.mul(&det_matrix(&minor)));
    }
    acc
}

fn sylvester_res_y(p: &Poly, q: &Poly) -> Poly {
    let rest: Vec<String> = p.vars.iter().cloned().filter(|n| n != "y").collect();
    let p2 = coeff_in_y(p, 2);
    let p1 = coeff_in_y(p, 1);
    let p0 = coeff_in_y(p, 0);
    let q2 = coeff_in_y(q, 2);
    let q1 = coeff_in_y(q, 1);
    let q0 = coeff_in_y(q, 0);
    let z = Poly::zero(&rest);
    let m = vec![
        vec![p2.clone(), p1.clone(), p0.clone(), z.clone()],
        vec![z.clone(), p2, p1, p0],
        vec![q2.clone(), q1.clone(), q0.clone(), z.clone()],
        vec![z, q2, q1, q0],
    ];
    det_matrix(&m)
}

fn shi_field(vars: &[String]) -> (Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p = y
        .neg()
        .sub(&x.pow(2).scale(10))
        .add(&x.mul(&y).scale(5))
        .add(&y.pow(2));
    let q = x.add(&x.pow(2)).sub(&x.mul(&y).scale(25));
    (p, q)
}

fn vandermonde(vars: &[String]) -> (Poly, [Poly; 9]) {
    let t1 = v(vars, "t1");
    let t2 = v(vars, "t2");
    let t3 = v(vars, "t3");
    let one = constant(vars, 1);
    let mat = vec![
        vec![one.clone(), t1.clone(), t1.pow(2)],
        vec![one.clone(), t2.clone(), t2.pow(2)],
        vec![one, t3.clone(), t3.pow(2)],
    ];
    let det = det_matrix(&mat);
    let claimed = t1
        .sub(&t2)
        .mul(&t1.sub(&t3))
        .mul(&t2.sub(&t3))
        .neg();
    require_equal(&det, &claimed, "Vandermonde det");

    // Cofactor adjugate: adj = C^T, C_ij = (-1)^{i+j} det minor_ij.
    let mut cof = vec![vec![Poly::zero(vars); 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            let mut minor = Vec::new();
            for r in 0..3 {
                if r == i {
                    continue;
                }
                let mut row = Vec::new();
                for c in 0..3 {
                    if c != j {
                        row.push(mat[r][c].clone());
                    }
                }
                minor.push(row);
            }
            let mut entry = det_matrix(&minor);
            if (i + j) % 2 == 1 {
                entry = entry.neg();
            }
            cof[i][j] = entry;
        }
    }
    let mut diffs = Vec::new();
    for i in 0..3 {
        for j in 0..3 {
            let mut acc = Poly::zero(vars);
            for k in 0..3 {
                // (adj V)_{ik} = C_ki
                acc = acc.add(&cof[k][i].mul(&mat[k][j]));
            }
            if i == j {
                acc = acc.sub(&det);
            }
            require_zero(&acc, "vandermonde adj V - det I");
            diffs.push(acc);
        }
    }
    (
        det,
        [
            diffs[0].clone(),
            diffs[1].clone(),
            diffs[2].clone(),
            diffs[3].clone(),
            diffs[4].clone(),
            diffs[5].clone(),
            diffs[6].clone(),
            diffs[7].clone(),
            diffs[8].clone(),
        ],
    )
}

struct Counts {
    inner_degree: i32,
    p_terms: usize,
    q_terms: usize,
    p_degree: i32,
    q_degree: i32,
    content: i128,
    dhdt_terms: usize,
    det00: i128,
    det12: i128,
    det1m2: i128,
    cubic_dhdt: usize,
    cubic_trace: i128,
    cubic_det: i128,
    line_p_deg: i32,
    line_q_deg: i32,
    vandermonde_diffs: usize,
    shi_real: usize,
    shi_res_deg: i32,
    generic_res_deg: i32,
    cubic_collinear: usize,
}

fn check_all() -> Counts {
    let xy = names(&["x", "y"]);
    let field = darboux_field(&xy);
    assert_eq!(field.inner.degree(), 3, "inner degree");
    assert_eq!(field.p.degree(), 4, "P degree");
    assert_eq!(field.q.degree(), 4, "Q degree");
    require_zero(&field.numer, "dH/dt numerator");
    dhdt_box_zero(&field.numer);

    let centers = [(0i128, 0i128), (1, 2), (1, -2)];
    let mut dets = Vec::new();
    for (x, y) in centers {
        if eval_xy(&field.p, x, y) != 0 || eval_xy(&field.q, x, y) != 0 {
            panic!("({x},{y}) is not an equilibrium");
        }
        let (jxx, jxy, jyx, jyy) = jacobian_at(&field.p, &field.q, x, y);
        if jxx + jyy != 0 {
            panic!("trace at ({x},{y})");
        }
        let det = jxx * jyy - jxy * jyx;
        if det <= 0 {
            panic!("det at ({x},{y}) is {det}");
        }
        dets.push(det);
    }
    assert_eq!(dets, vec![44, 64, 64]);
    let j00 = jacobian_at(&field.p, &field.q, 0, 0);
    assert_eq!(j00, (0, 4, -11, 0));
    let j12 = jacobian_at(&field.p, &field.q, 1, 2);
    assert_eq!(j12, (0, -8, 8, 0));
    assert_eq!(jacobian_at(&field.p, &field.q, 1, -2), j12);

    let p_bad = field.p.add(&constant(&xy, 1));
    let numer_bad = field
        .q_raw
        .mul(&p_bad)
        .add(&field.p_raw.neg().mul(&field.q));
    if numer_bad.is_zero() {
        panic!("perturbed field unexpectedly had dH/dt = 0");
    }

    let (h20, p20, q20, dh20) = cubic20(&xy);
    require_zero(&dh20, "cubic20 dH/dt");
    require_equal(&p20.scale(4), &h20.dvar("y").neg(), "4 P = -H_y");
    require_equal(&q20.scale(4), &h20.dvar("x"), "4 Q = H_x");
    let (cxx, cxy, cyx, cyy) = jacobian_at(&p20, &q20, 0, 0);
    assert_eq!((cxx + cyy, cxx * cyy - cxy * cyx), (0, 1));
    // P(t,0) = 0; Q(t,0) = -t(8t^2 + 3t - 1).
    let line_vars = names(&["t"]);
    let t = v(&line_vars, "t");
    let p20_line = p20.terms.iter().fold(Poly::zero(&line_vars), |acc, (e, c)| {
        // substitute y=0, x=t
        let y_idx = 1; // vars are x,y
        if e[y_idx] != 0 {
            return acc;
        }
        let mut one = Poly::zero(&line_vars);
        let mut exp = vec![0u8; 1];
        exp[0] = e[0];
        one.terms.insert(exp, *c);
        acc.add(&one)
    });
    require_zero(&p20_line, "cubic20 P(t,0)");
    let q20_line = q20.terms.iter().fold(Poly::zero(&line_vars), |acc, (e, c)| {
        if e[1] != 0 {
            return acc;
        }
        let mut one = Poly::zero(&line_vars);
        let mut exp = vec![0u8; 1];
        exp[0] = e[0];
        one.terms.insert(exp, *c);
        acc.add(&one)
    });
    let claimed_q_line = t
        .neg()
        .mul(&t.pow(2).scale(8).add(&t.scale(3)).sub(&constant(&line_vars, 1)));
    require_equal(&q20_line, &claimed_q_line, "cubic20 Q(t,0)");
    // disc(8t^2 + 3t - 1) = 9 + 32 = 41.
    assert_eq!(3i128 * 3 - 4 * 8 * (-1), 41);

    let line_coeff_vars = names(&["t", "a00", "a10", "a20", "b00", "b10", "b20"]);
    let p_line = v(&line_coeff_vars, "a00")
        .add(&v(&line_coeff_vars, "a10").mul(&v(&line_coeff_vars, "t")))
        .add(&v(&line_coeff_vars, "a20").mul(&v(&line_coeff_vars, "t").pow(2)));
    let q_line = v(&line_coeff_vars, "b00")
        .add(&v(&line_coeff_vars, "b10").mul(&v(&line_coeff_vars, "t")))
        .add(&v(&line_coeff_vars, "b20").mul(&v(&line_coeff_vars, "t").pow(2)));
    assert_eq!(p_line.degree_in("t"), 2);
    assert_eq!(q_line.degree_in("t"), 2);

    let van_vars = names(&["t1", "t2", "t3"]);
    let (_det, diffs) = vandermonde(&van_vars);
    assert!(diffs.iter().all(|d| d.is_zero()));

    let quad_vars = names(&[
        "x", "y", "a00", "a10", "a01", "a20", "a11", "a02", "b00", "b10", "b01", "b20", "b11",
        "b02",
    ]);
    let (gp, gq) = generic_quadratic(&quad_vars);
    let res = sylvester_res_y(&gp, &gq);
    assert_eq!(res.degree_in("x"), 4);

    let (shi_p, shi_q) = shi_field(&xy);
    let shi_res = sylvester_res_y(&shi_p, &shi_q);
    let claimed_shi = v(&names(&["x"]), "x")
        .pow(4)
        .scale(-6124)
        .add(&v(&names(&["x"]), "x").pow(3).scale(102))
        .add(&v(&names(&["x"]), "x").pow(2).scale(-24));
    require_equal(&shi_res, &claimed_shi, "Shi Res_y");
    assert_eq!(eval_xy(&shi_p, 0, 0), 0);
    assert_eq!(eval_xy(&shi_q, 0, 0), 0);
    assert_eq!(eval_xy(&shi_p, 0, 1), 0);
    assert_eq!(eval_xy(&shi_q, 0, 1), 0);
    let disc = 102i128 * 102 - 4 * 6124 * 24;
    assert_eq!(disc, -577500);
    assert!(disc < 0);
    assert_eq!(shi_res.degree_in("x"), 4);

    Counts {
        inner_degree: field.inner.degree(),
        p_terms: field.p.term_count(),
        q_terms: field.q.term_count(),
        p_degree: field.p.degree(),
        q_degree: field.q.degree(),
        content: 10,
        dhdt_terms: field.numer.term_count(),
        det00: dets[0],
        det12: dets[1],
        det1m2: dets[2],
        cubic_dhdt: dh20.term_count(),
        cubic_trace: 0,
        cubic_det: 1,
        line_p_deg: 2,
        line_q_deg: 2,
        vandermonde_diffs: 0,
        shi_real: 2,
        shi_res_deg: 4,
        generic_res_deg: 4,
        cubic_collinear: 3,
    }
}

fn check_certificate(text: &str) {
    let root = parse_json(text);
    let xy = names(&["x", "y"]);
    let field = darboux_field(&xy);
    let darboux = obj(&root, "darboux");
    assert_eq!(strs(darboux, "variables"), xy);
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "A")),
        &a_poly(&xy),
        "cert A",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "B")),
        &b_poly(&xy),
        "cert B",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "inner")),
        &field.inner,
        "cert inner",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "P")),
        &field.p,
        "cert P",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "Q")),
        &field.q,
        "cert Q",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "P_raw")),
        &field.p_raw,
        "cert P_raw",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "Q_raw")),
        &field.q_raw,
        "cert Q_raw",
    );
    require_equal(
        &Poly::from_terms(&xy, &term_list(darboux, "dHdt_numer")),
        &field.numer,
        "cert dHdt",
    );
    assert_eq!(json_i64(darboux, "content"), 10);
    assert_eq!(json_i64(darboux, "deg_P"), 4);
    assert_eq!(json_i64(darboux, "deg_Q"), 4);

    let centers = obj(&root, "centers");
    assert_eq!(int_list(centers, "traces"), vec![0, 0, 0]);
    assert_eq!(int_list(centers, "dets"), vec![44, 64, 64]);

    let (h20, p20, q20, dh20) = cubic20(&xy);
    let cubic = obj(&root, "cubic20");
    require_equal(&Poly::from_terms(&xy, &term_list(cubic, "H")), &h20, "cert H20");
    require_equal(&Poly::from_terms(&xy, &term_list(cubic, "P")), &p20, "cert P20");
    require_equal(&Poly::from_terms(&xy, &term_list(cubic, "Q")), &q20, "cert Q20");
    require_equal(&Poly::from_terms(&xy, &term_list(cubic, "dHdt")), &dh20, "cert dH20");
    assert_eq!(json_i64(cubic, "collinear_equilibria"), 3);

    let line_vars = names(&["t", "a00", "a10", "a20", "b00", "b10", "b20"]);
    let line = obj(&root, "line");
    let p_line = v(&line_vars, "a00")
        .add(&v(&line_vars, "a10").mul(&v(&line_vars, "t")))
        .add(&v(&line_vars, "a20").mul(&v(&line_vars, "t").pow(2)));
    let q_line = v(&line_vars, "b00")
        .add(&v(&line_vars, "b10").mul(&v(&line_vars, "t")))
        .add(&v(&line_vars, "b20").mul(&v(&line_vars, "t").pow(2)));
    require_equal(
        &Poly::from_terms(&line_vars, &term_list(line, "P_on_y0")),
        &p_line,
        "cert P(t,0)",
    );
    require_equal(
        &Poly::from_terms(&line_vars, &term_list(line, "Q_on_y0")),
        &q_line,
        "cert Q(t,0)",
    );

    let van_vars = names(&["t1", "t2", "t3"]);
    let (det, _) = vandermonde(&van_vars);
    let van = obj(&root, "vandermonde");
    require_equal(
        &Poly::from_terms(&van_vars, &term_list(van, "det")),
        &det,
        "cert vandermonde det",
    );
    require_equal(
        &Poly::from_terms(&van_vars, &term_list(van, "claimed_det")),
        &det,
        "cert claimed det",
    );

    let (shi_p, shi_q) = shi_field(&xy);
    let shi = obj(&root, "shi");
    require_equal(&Poly::from_terms(&xy, &term_list(shi, "P")), &shi_p, "cert Shi P");
    require_equal(&Poly::from_terms(&xy, &term_list(shi, "Q")), &shi_q, "cert Shi Q");
    let shi_res = sylvester_res_y(&shi_p, &shi_q);
    let x_only = names(&["x"]);
    require_equal(
        &Poly::from_terms(&x_only, &term_list(shi, "res_y")),
        &shi_res,
        "cert Shi res",
    );
    assert_eq!(json_i64(shi, "leftover_discriminant"), -577500);

    let quad_vars = names(&[
        "x", "y", "a00", "a10", "a01", "a20", "a11", "a02", "b00", "b10", "b01", "b20", "b11",
        "b02",
    ]);
    let (gp, gq) = generic_quadratic(&quad_vars);
    let res = sylvester_res_y(&gp, &gq);
    let res_vars: Vec<String> = quad_vars.iter().cloned().filter(|n| n != "y").collect();
    let res_lifted = lift_to(&res, &res_vars);
    let rblock = obj(&root, "resultant");
    require_equal(
        &Poly::from_terms(&res_vars, &term_list(rblock, "res_y")),
        &res_lifted,
        "cert generic res",
    );
    assert_eq!(json_i64(rblock, "deg_x"), 4);
}

fn dump_lines(c: &Counts) -> String {
    format!(
        "darboux inner degree {}\n\
         darboux primitive P terms {} degree {}\n\
         darboux primitive Q terms {} degree {}\n\
         darboux content {}\n\
         darboux dHdt numer terms {}\n\
         centers traces 0 0 0 dets {} {} {}\n\
         cubic20 dHdt terms {}\n\
         cubic20 origin trace {} det {}\n\
         line P(t,0) degree {}\n\
         line Q(t,0) degree {}\n\
         vandermonde diffs {}\n\
         shi real equilibria {}\n\
         shi res_y degree {}\n\
         generic res_y degree {}\n\
         cubic20 collinear equilibria {}\n\
         negative perturbation rejected\n",
        c.inner_degree,
        c.p_terms,
        c.p_degree,
        c.q_terms,
        c.q_degree,
        c.content,
        c.dhdt_terms,
        c.det00,
        c.det12,
        c.det1m2,
        c.cubic_dhdt,
        c.cubic_trace,
        c.cubic_det,
        c.line_p_deg,
        c.line_q_deg,
        c.vandermonde_diffs,
        c.shi_real,
        c.shi_res_deg,
        c.generic_res_deg,
        c.cubic_collinear
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
    println!("VALID pt-darboux identities");
}
