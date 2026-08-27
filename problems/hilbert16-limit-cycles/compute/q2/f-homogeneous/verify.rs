//! Independent checker for the homogeneous / quasi-homogeneous identities.
//!
//! Python (`verify.py`) expands sparse monomials with a hashmap. This
//! program expands the same rings with a BTreeMap and evaluates the
//! concrete residuals on an integer box. A second algorithm, not a
//! replay of the sparse product: the scale identity is also checked
//! by evaluating P at (λx, λy) versus λ^n P(x, y).

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

    fn subst_xy(&self, xnew: &Poly, ynew: &Poly) -> Self {
        let mut map = BTreeMap::new();
        map.insert("x".to_string(), xnew.clone());
        map.insert("y".to_string(), ynew.clone());
        self.subst(&map)
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
            total += mon
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

fn scale_xy(vars: &[String], weight_y: u32) -> (Poly, Poly) {
    let lam = v(vars, "lam");
    let x = v(vars, "x");
    let y = v(vars, "y");
    (lam.mul(&x), lam.pow(weight_y).mul(&y))
}

fn radial_angular(vars: &[String], p: &Poly, q: &Poly) -> (Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    (x.mul(p).add(&y.mul(q)), x.mul(q).sub(&y.mul(p)))
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

fn json_str(map: &BTreeMap<String, Json>, key: &str) -> String {
    match map.get(key) {
        Some(Json::String(s)) => s.clone(),
        _ => panic!("missing string {key}"),
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

fn require_nonzero(poly: &Poly, label: &str) {
    if poly.is_zero() {
        panic!("{label} is unexpectedly zero");
    }
}

fn match_terms(vars: &[String], terms: &[BTreeMap<String, JsonAtom>], poly: &Poly, label: &str) {
    require_equal(&Poly::from_terms(vars, terms), poly, label);
}

fn homog2_field(vars: &[String]) -> (Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let a20 = v(vars, "a20");
    let a11 = v(vars, "a11");
    let a02 = v(vars, "a02");
    let b20 = v(vars, "b20");
    let b11 = v(vars, "b11");
    let b02 = v(vars, "b02");
    let p = a20
        .mul(&x.pow(2))
        .add(&a11.mul(&x).mul(&y))
        .add(&a02.mul(&y.pow(2)));
    let q = b20
        .mul(&x.pow(2))
        .add(&b11.mul(&x).mul(&y))
        .add(&b02.mul(&y.pow(2)));
    let (f, g) = radial_angular(vars, &p, &q);
    (p, q, f, g)
}

fn homog3_field(vars: &[String]) -> (Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let a30 = v(vars, "a30");
    let a21 = v(vars, "a21");
    let a12 = v(vars, "a12");
    let a03 = v(vars, "a03");
    let b30 = v(vars, "b30");
    let b21 = v(vars, "b21");
    let b12 = v(vars, "b12");
    let b03 = v(vars, "b03");
    let p = a30
        .mul(&x.pow(3))
        .add(&a21.mul(&x.pow(2)).mul(&y))
        .add(&a12.mul(&x).mul(&y.pow(2)))
        .add(&a03.mul(&y.pow(3)));
    let q = b30
        .mul(&x.pow(3))
        .add(&b21.mul(&x.pow(2)).mul(&y))
        .add(&b12.mul(&x).mul(&y.pow(2)))
        .add(&b03.mul(&y.pow(3)));
    let (f, g) = radial_angular(vars, &p, &q);
    (p, q, f, g)
}

fn circle_field(vars: &[String]) -> (Poly, Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let r2 = x.mul(&x).add(&y.mul(&y));
    let p = y.mul(&r2).neg();
    let q = x.mul(&r2);
    let (f, g) = radial_angular(vars, &p, &q);
    let g_claimed = r2.mul(&r2);
    (p, q, f, g, g_claimed)
}

fn ray_field(vars: &[String]) -> RayBundle {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p = x.mul(&x);
    let q = y.mul(&y);
    let (f, g) = radial_angular(vars, &p, &q);
    let g_factored = x.mul(&y).mul(&y.sub(&x));
    let zero = constant(vars, 0);
    let mut x0 = BTreeMap::new();
    x0.insert("x".to_string(), zero.clone());
    let mut y0 = BTreeMap::new();
    y0.insert("y".to_string(), zero);
    let mut yx = BTreeMap::new();
    yx.insert("y".to_string(), x.clone());
    let mut anti = BTreeMap::new();
    anti.insert("y".to_string(), x.neg());
    RayBundle {
        p: p.clone(),
        q: q.clone(),
        f: f.clone(),
        g,
        g_factored,
        ray_x0: p.subst(&x0),
        ray_y0: q.subst(&y0),
        ray_yx: p.sub(&q).subst(&yx),
        f_zero_line: f.subst(&anti),
        f_zero_line_normal: p.add(&q).subst(&anti),
    }
}

struct RayBundle {
    p: Poly,
    q: Poly,
    f: Poly,
    g: Poly,
    g_factored: Poly,
    ray_x0: Poly,
    ray_y0: Poly,
    ray_yx: Poly,
    f_zero_line: Poly,
    f_zero_line_normal: Poly,
}

fn scale_field(vars: &[String]) -> (Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p = y.pow(3).neg();
    let q = x.pow(3);
    let (xs, ys) = scale_xy(vars, 1);
    let lam = v(vars, "lam");
    let p_diff = p.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&p));
    let q_diff = q.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&q));
    (p, q, p_diff, q_diff)
}

fn qh_field(vars: &[String]) -> (Poly, Poly, Poly, Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p = constant(vars, 2).mul(&y);
    let q = x.pow(3).neg();
    let h = x.pow(4).add(&constant(vars, 4).mul(&y.pow(2)));
    let hx = h.dvar("x");
    let hy = h.dvar("y");
    let dhdt = hx.mul(&p).add(&hy.mul(&q));
    (h, hx, hy, p, q, dhdt)
}

fn qh_weight(vars: &[String]) -> (Poly, Poly, Poly) {
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p = constant(vars, 2).mul(&y);
    let q = x.pow(3).neg();
    let h = x.pow(4).add(&constant(vars, 4).mul(&y.pow(2)));
    let (xs, ys) = scale_xy(vars, 2);
    let lam = v(vars, "lam");
    (
        p.subst_xy(&xs, &ys).sub(&lam.pow(2).mul(&p)),
        q.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&q)),
        h.subst_xy(&xs, &ys).sub(&lam.pow(4).mul(&h)),
    )
}

fn insert_xy(values: &mut BTreeMap<String, i128>, x: i128, y: i128) {
    values.insert("x".into(), x);
    values.insert("y".into(), y);
}

fn check_negative(circ_p: &Poly, circ_q: &Poly) {
    let vars = &circ_p.vars;
    let x = v(vars, "x");
    let y = v(vars, "y");
    let p_bad = circ_p.add(&constant(vars, 1));
    let radial = x.mul(&p_bad).add(&y.mul(circ_q));
    if radial.is_zero() {
        panic!("perturbed circle field unexpectedly had F ≡ 0");
    }
    let mut vals = BTreeMap::new();
    insert_xy(&mut vals, 1, 0);
    if radial.eval(&vals) == 0 {
        panic!("perturbed F vanished at (1,0)");
    }
}

fn check_integer_box(circ: &(Poly, Poly, Poly, Poly, Poly), rays: &RayBundle, scale: &(Poly, Poly, Poly, Poly), qh: &(Poly, Poly, Poly, Poly, Poly, Poly), qw: &(Poly, Poly, Poly), h2_p: &Poly) {
    let (_circ_p, _circ_q, circ_f, circ_g, circ_g_claimed) = circ;
    let (sc_p, sc_q, sc_pd, sc_qd) = scale;
    let (h, _hx, _hy, _qp, _qq, dhdt) = qh;
    let (pw, qw_d, hw) = qw;

    for x in -3i128..=3 {
        for y in -3i128..=3 {
            let mut vals = BTreeMap::new();
            insert_xy(&mut vals, x, y);
            if circ_f.eval(&vals) != 0 {
                panic!("circles F nonzero at ({x},{y})");
            }
            let g = circ_g.eval(&vals);
            let claimed = circ_g_claimed.eval(&vals);
            if g != claimed {
                panic!("circles G mismatch at ({x},{y})");
            }
            if (x == 0 && y == 0) != (g == 0) {
                panic!("circles G zero-set failed at ({x},{y})");
            }
            if dhdt.eval(&vals) != 0 {
                panic!("qh dH/dt nonzero at ({x},{y})");
            }
            let hval = h.eval(&vals);
            if (x == 0 && y == 0) != (hval == 0) {
                panic!("H zero-set failed at ({x},{y})");
            }
            if x == 0 && rays.p.eval(&vals) != 0 {
                panic!("ray x=0 not invariant at y={y}");
            }
            if y == 0 && rays.q.eval(&vals) != 0 {
                panic!("ray y=0 not invariant at x={x}");
            }
            if y == x && rays.p.eval(&vals) != rays.q.eval(&vals) {
                panic!("ray y=x not invariant at x={x}");
            }
            let mut anti = BTreeMap::new();
            insert_xy(&mut anti, x, -x);
            if rays.f.eval(&anti) != 0 {
                panic!("F not zero on x+y=0 at x={x}");
            }
            if x != 0 && rays.f_zero_line_normal.eval(&vals) == 0 {
                panic!("F-zero line unexpectedly invariant at x={x}");
            }
        }
    }
    let mut probe = BTreeMap::new();
    insert_xy(&mut probe, 1, 0);
    if rays.f.eval(&probe) == 0 {
        panic!("rays F vanished at (1,0)");
    }

    for x in -3i128..=3 {
        for y in -3i128..=3 {
            for lam in -3i128..=3 {
                let mut vals = BTreeMap::new();
                insert_xy(&mut vals, x, y);
                vals.insert("lam".into(), lam);
                if sc_pd.eval(&vals) != 0 {
                    panic!("scale P residual at ({x},{y},{lam})");
                }
                if sc_qd.eval(&vals) != 0 {
                    panic!("scale Q residual at ({x},{y},{lam})");
                }
                let mut scaled = BTreeMap::new();
                insert_xy(&mut scaled, lam * x, lam * y);
                scaled.insert("lam".into(), 0);
                if sc_p.eval(&scaled) != lam.pow(3) * sc_p.eval(&vals) {
                    panic!("scale P eval identity at ({x},{y},{lam})");
                }
                if sc_q.eval(&scaled) != lam.pow(3) * sc_q.eval(&vals) {
                    panic!("scale Q eval identity at ({x},{y},{lam})");
                }
                if pw.eval(&vals) != 0 {
                    panic!("qh P weight residual at ({x},{y},{lam})");
                }
                if qw_d.eval(&vals) != 0 {
                    panic!("qh Q weight residual at ({x},{y},{lam})");
                }
                if hw.eval(&vals) != 0 {
                    panic!("qh H weight residual at ({x},{y},{lam})");
                }
            }
        }
    }

    let mut sample = BTreeMap::new();
    sample.insert("x".into(), 2);
    sample.insert("y".into(), -1);
    sample.insert("lam".into(), 3);
    sample.insert("a20".into(), 1);
    sample.insert("a11".into(), -2);
    sample.insert("a02".into(), 1);
    sample.insert("b20".into(), 0);
    sample.insert("b11".into(), 1);
    sample.insert("b02".into(), -1);
    let mut scaled = sample.clone();
    scaled.insert("x".into(), 3 * 2);
    scaled.insert("y".into(), 3 * -1);
    if h2_p.eval(&scaled) != 9 * h2_p.eval(&sample) {
        panic!("homog2 sample scale failed");
    }
}

struct Counts {
    homog2_p: usize,
    homog2_q: usize,
    homog2_f: usize,
    homog2_g: usize,
    homog3_p: usize,
    homog3_q: usize,
    homog3_f: usize,
    homog3_g: usize,
    circles_f: usize,
    circles_g: usize,
    rays_f: usize,
    rays_g: usize,
    f_zero_normal: usize,
    qh_dhdt: usize,
}

fn check_all() -> Counts {
    let h2_vars = names(&["x", "y", "lam", "a20", "a11", "a02", "b20", "b11", "b02"]);
    let (h2_p, h2_q, h2_f, h2_g) = homog2_field(&h2_vars);
    let (xs, ys) = scale_xy(&h2_vars, 1);
    let lam2 = v(&h2_vars, "lam");
    require_zero(&h2_p.subst_xy(&xs, &ys).sub(&lam2.pow(2).mul(&h2_p)), "homog2 P scale");
    require_zero(&h2_q.subst_xy(&xs, &ys).sub(&lam2.pow(2).mul(&h2_q)), "homog2 Q scale");
    require_zero(&h2_f.subst_xy(&xs, &ys).sub(&lam2.pow(3).mul(&h2_f)), "homog2 F scale");
    require_zero(&h2_g.subst_xy(&xs, &ys).sub(&lam2.pow(3).mul(&h2_g)), "homog2 G scale");

    let h3_vars = names(&[
        "x", "y", "lam", "a30", "a21", "a12", "a03", "b30", "b21", "b12", "b03",
    ]);
    let (h3_p, h3_q, h3_f, h3_g) = homog3_field(&h3_vars);
    let (xs3, ys3) = scale_xy(&h3_vars, 1);
    let lam3 = v(&h3_vars, "lam");
    require_zero(&h3_p.subst_xy(&xs3, &ys3).sub(&lam3.pow(3).mul(&h3_p)), "homog3 P scale");
    require_zero(&h3_q.subst_xy(&xs3, &ys3).sub(&lam3.pow(3).mul(&h3_q)), "homog3 Q scale");
    require_zero(&h3_f.subst_xy(&xs3, &ys3).sub(&lam3.pow(4).mul(&h3_f)), "homog3 F scale");
    require_zero(&h3_g.subst_xy(&xs3, &ys3).sub(&lam3.pow(4).mul(&h3_g)), "homog3 G scale");

    let xy = names(&["x", "y"]);
    let circ = circle_field(&xy);
    require_zero(&circ.2, "circles F");
    require_zero(&circ.3.sub(&circ.4), "circles G claimed");
    require_nonzero(&circ.3, "circles G");

    let rays = ray_field(&xy);
    require_nonzero(&rays.f, "rays F");
    require_zero(&rays.g.sub(&rays.g_factored), "rays G factor");
    require_zero(&rays.ray_x0, "ray x=0");
    require_zero(&rays.ray_y0, "ray y=0");
    require_zero(&rays.ray_yx, "ray y=x");
    require_zero(&rays.f_zero_line, "F zero line");
    require_nonzero(&rays.f_zero_line_normal, "F zero line normal");

    let scale_vars = names(&["x", "y", "lam"]);
    let scale = scale_field(&scale_vars);
    require_zero(&scale.2, "scale cubic P");
    require_zero(&scale.3, "scale cubic Q");

    let qh = qh_field(&xy);
    require_zero(&qh.5, "qh dH/dt");

    let qw_vars = names(&["x", "y", "lam"]);
    let qw = qh_weight(&qw_vars);
    require_zero(&qw.0, "qh P weight");
    require_zero(&qw.1, "qh Q weight");
    require_zero(&qw.2, "qh H weight");

    check_negative(&circ.0, &circ.1);
    check_integer_box(&circ, &rays, &scale, &qh, &qw, &h2_p);

    Counts {
        homog2_p: h2_p.term_count(),
        homog2_q: h2_q.term_count(),
        homog2_f: h2_f.term_count(),
        homog2_g: h2_g.term_count(),
        homog3_p: h3_p.term_count(),
        homog3_q: h3_q.term_count(),
        homog3_f: h3_f.term_count(),
        homog3_g: h3_g.term_count(),
        circles_f: circ.2.term_count(),
        circles_g: circ.3.term_count(),
        rays_f: rays.f.term_count(),
        rays_g: rays.g.term_count(),
        f_zero_normal: rays.f_zero_line_normal.term_count(),
        qh_dhdt: qh.5.term_count(),
    }
}

fn check_certificate(text: &str) {
    let root = parse_json(text);
    match &root {
        Json::Object(map) => {
            if json_str(map, "schema") != "hilbert16-f-homogeneous/v1" {
                panic!("schema mismatch");
            }
        }
        _ => panic!("root must be object"),
    }

    let h2 = obj(&root, "homog2");
    let h2_vars = strs(h2, "variables");
    let (p, q, f, g) = homog2_field(&h2_vars);
    let (xs, ys) = scale_xy(&h2_vars, 1);
    let lam = v(&h2_vars, "lam");
    match_terms(&h2_vars, &term_list(h2, "P"), &p, "cert homog2 P");
    match_terms(&h2_vars, &term_list(h2, "Q"), &q, "cert homog2 Q");
    match_terms(&h2_vars, &term_list(h2, "F"), &f, "cert homog2 F");
    match_terms(&h2_vars, &term_list(h2, "G"), &g, "cert homog2 G");
    match_terms(
        &h2_vars,
        &term_list(h2, "P_scaled_diff"),
        &p.subst_xy(&xs, &ys).sub(&lam.pow(2).mul(&p)),
        "cert homog2 P scale",
    );
    match_terms(
        &h2_vars,
        &term_list(h2, "Q_scaled_diff"),
        &q.subst_xy(&xs, &ys).sub(&lam.pow(2).mul(&q)),
        "cert homog2 Q scale",
    );
    match_terms(
        &h2_vars,
        &term_list(h2, "F_scaled_diff"),
        &f.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&f)),
        "cert homog2 F scale",
    );
    match_terms(
        &h2_vars,
        &term_list(h2, "G_scaled_diff"),
        &g.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&g)),
        "cert homog2 G scale",
    );

    let h3 = obj(&root, "homog3");
    let h3_vars = strs(h3, "variables");
    let (p, q, f, g) = homog3_field(&h3_vars);
    let (xs, ys) = scale_xy(&h3_vars, 1);
    let lam = v(&h3_vars, "lam");
    match_terms(&h3_vars, &term_list(h3, "P"), &p, "cert homog3 P");
    match_terms(&h3_vars, &term_list(h3, "Q"), &q, "cert homog3 Q");
    match_terms(&h3_vars, &term_list(h3, "F"), &f, "cert homog3 F");
    match_terms(&h3_vars, &term_list(h3, "G"), &g, "cert homog3 G");
    match_terms(
        &h3_vars,
        &term_list(h3, "P_scaled_diff"),
        &p.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&p)),
        "cert homog3 P scale",
    );
    match_terms(
        &h3_vars,
        &term_list(h3, "Q_scaled_diff"),
        &q.subst_xy(&xs, &ys).sub(&lam.pow(3).mul(&q)),
        "cert homog3 Q scale",
    );
    match_terms(
        &h3_vars,
        &term_list(h3, "F_scaled_diff"),
        &f.subst_xy(&xs, &ys).sub(&lam.pow(4).mul(&f)),
        "cert homog3 F scale",
    );
    match_terms(
        &h3_vars,
        &term_list(h3, "G_scaled_diff"),
        &g.subst_xy(&xs, &ys).sub(&lam.pow(4).mul(&g)),
        "cert homog3 G scale",
    );

    let circ = obj(&root, "circles");
    let xy = strs(circ, "variables");
    let (p, q, f, g, g_claimed) = circle_field(&xy);
    match_terms(&xy, &term_list(circ, "P"), &p, "cert circles P");
    match_terms(&xy, &term_list(circ, "Q"), &q, "cert circles Q");
    match_terms(&xy, &term_list(circ, "F"), &f, "cert circles F");
    match_terms(&xy, &term_list(circ, "G"), &g, "cert circles G");
    match_terms(&xy, &term_list(circ, "G_claimed"), &g_claimed, "cert circles G claimed");

    let rays_obj = obj(&root, "rays");
    let xy = strs(rays_obj, "variables");
    let rays = ray_field(&xy);
    match_terms(&xy, &term_list(rays_obj, "P"), &rays.p, "cert rays P");
    match_terms(&xy, &term_list(rays_obj, "Q"), &rays.q, "cert rays Q");
    match_terms(&xy, &term_list(rays_obj, "F"), &rays.f, "cert rays F");
    match_terms(&xy, &term_list(rays_obj, "G"), &rays.g, "cert rays G");
    match_terms(&xy, &term_list(rays_obj, "G_factored"), &rays.g_factored, "cert rays G factor");
    match_terms(&xy, &term_list(rays_obj, "ray_x0"), &rays.ray_x0, "cert ray x=0");
    match_terms(&xy, &term_list(rays_obj, "ray_y0"), &rays.ray_y0, "cert ray y=0");
    match_terms(&xy, &term_list(rays_obj, "ray_yx"), &rays.ray_yx, "cert ray y=x");
    match_terms(&xy, &term_list(rays_obj, "F_zero_line"), &rays.f_zero_line, "cert F zero line");
    match_terms(
        &xy,
        &term_list(rays_obj, "F_zero_line_normal"),
        &rays.f_zero_line_normal,
        "cert F zero line normal",
    );

    let scale = obj(&root, "scale");
    let sv = strs(scale, "variables");
    let (p, q, pd, qd) = scale_field(&sv);
    match_terms(&sv, &term_list(scale, "P"), &p, "cert scale P");
    match_terms(&sv, &term_list(scale, "Q"), &q, "cert scale Q");
    match_terms(&sv, &term_list(scale, "P_scaled_diff"), &pd, "cert scale P diff");
    match_terms(&sv, &term_list(scale, "Q_scaled_diff"), &qd, "cert scale Q diff");

    let qh = obj(&root, "quasihomogeneous");
    let qv = strs(qh, "variables");
    let (h, hx, hy, p, qpoly, dhdt) = qh_field(&qv);
    match_terms(&qv, &term_list(qh, "H"), &h, "cert qh H");
    match_terms(&qv, &term_list(qh, "Hx"), &hx, "cert qh Hx");
    match_terms(&qv, &term_list(qh, "Hy"), &hy, "cert qh Hy");
    match_terms(&qv, &term_list(qh, "P"), &p, "cert qh P");
    match_terms(&qv, &term_list(qh, "Q"), &qpoly, "cert qh Q");
    match_terms(&qv, &term_list(qh, "dHdt"), &dhdt, "cert qh dHdt");

    let qw = obj(&root, "quasihomogeneous_weight");
    let wv = strs(qw, "variables");
    let (pw, qw_d, hw) = qh_weight(&wv);
    match_terms(&wv, &term_list(qw, "P_weight_diff"), &pw, "cert qh P weight");
    match_terms(&wv, &term_list(qw, "Q_weight_diff"), &qw_d, "cert qh Q weight");
    match_terms(&wv, &term_list(qw, "H_weight_diff"), &hw, "cert qh H weight");
}

fn dump_lines(counts: &Counts) -> String {
    format!(
        "homog2 P terms {}\n\
         homog2 Q terms {}\n\
         homog2 F terms {}\n\
         homog2 G terms {}\n\
         homog2 P scale difference 0\n\
         homog2 Q scale difference 0\n\
         homog2 F scale difference 0\n\
         homog2 G scale difference 0\n\
         homog3 P terms {}\n\
         homog3 Q terms {}\n\
         homog3 F terms {}\n\
         homog3 G terms {}\n\
         homog3 P scale difference 0\n\
         homog3 Q scale difference 0\n\
         homog3 F scale difference 0\n\
         homog3 G scale difference 0\n\
         circles F terms {}\n\
         circles G terms {}\n\
         circles G claimed difference 0\n\
         rays F terms {}\n\
         rays G terms {}\n\
         rays G factor difference 0\n\
         ray x=0 residual 0\n\
         ray y=0 residual 0\n\
         ray y=x residual 0\n\
         F zero line residual 0\n\
         F zero line not invariant terms {}\n\
         scale cubic P difference 0\n\
         scale cubic Q difference 0\n\
         qh dHdt terms {}\n\
         qh H weight difference 0\n\
         qh P weight difference 0\n\
         qh Q weight difference 0\n\
         negative perturbation rejected\n\
         integer box zeros\n",
        counts.homog2_p,
        counts.homog2_q,
        counts.homog2_f,
        counts.homog2_g,
        counts.homog3_p,
        counts.homog3_q,
        counts.homog3_f,
        counts.homog3_g,
        counts.circles_f,
        counts.circles_g,
        counts.rays_f,
        counts.rays_g,
        counts.f_zero_normal,
        counts.qh_dhdt
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
    println!("VALID homogeneous / quasi-homogeneous identities");
}
