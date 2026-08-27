//! Independent checker for L1 at the three PT Darboux centers.
//!
//! Python (`verify.py`) expands with sympy and re-derives Poincaré V1.
//! This program expands the same degree-4 field with a sparse bivariate
//! map, puts each translated jet into the q1 normal form over Q(√11),
//! and evaluates
//!     L1 = L1_E + 3 a30 + a12 + b21 + 3 b03
//! with its own rational / Q(√11) arithmetic. The imagined H(4) ≥ 29
//! claim is not certified here.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process;
use std::str::FromStr;

fn gcd_i128(mut a: i128, mut b: i128) -> i128 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    if a == 0 {
        1
    } else {
        a
    }
}

fn binom(n: u8, k: u8) -> i128 {
    if k > n {
        return 0;
    }
    let mut out = 1i128;
    for t in 0..k {
        out = out * i128::from(n - t) / i128::from(t + 1);
    }
    out
}

fn pow_i128(base: i128, exp: u8) -> i128 {
    let mut out = 1i128;
    for _ in 0..exp {
        out *= base;
    }
    out
}

// ---------------------------------------------------------------------------
// Q and Q(√11)
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Rat {
    n: i128,
    d: i128,
}

impl Rat {
    fn new(n: i128, d: i128) -> Self {
        assert!(d != 0, "zero denominator");
        let g = gcd_i128(n, d);
        let mut n = n / g;
        let mut d = d / g;
        if d < 0 {
            n = -n;
            d = -d;
        }
        Self { n, d }
    }

    fn from_i(n: i128) -> Self {
        Self::new(n, 1)
    }

    fn zero() -> Self {
        Self::from_i(0)
    }

    fn is_zero(self) -> bool {
        self.n == 0
    }

    fn neg(self) -> Self {
        Self::new(-self.n, self.d)
    }

    fn add(self, other: Self) -> Self {
        Self::new(self.n * other.d + other.n * self.d, self.d * other.d)
    }

    fn sub(self, other: Self) -> Self {
        self.add(other.neg())
    }

    fn mul(self, other: Self) -> Self {
        Self::new(self.n * other.n, self.d * other.d)
    }

    fn div(self, other: Self) -> Self {
        Self::new(self.n * other.d, self.d * other.n)
    }

    fn fmt(self) -> String {
        if self.d == 1 {
            format!("{}", self.n)
        } else {
            format!("{}/{}", self.n, self.d)
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Alg {
    a: Rat,
    b: Rat,
}

impl Alg {
    fn rat(r: Rat) -> Self {
        Self { a: r, b: Rat::zero() }
    }

    fn int(n: i128) -> Self {
        Self::rat(Rat::from_i(n))
    }

    fn zero() -> Self {
        Self::int(0)
    }

    fn sqrt11(coeff: Rat) -> Self {
        Self { a: Rat::zero(), b: coeff }
    }

    fn is_zero(self) -> bool {
        self.a.is_zero() && self.b.is_zero()
    }

    fn add(self, other: Self) -> Self {
        Self {
            a: self.a.add(other.a),
            b: self.b.add(other.b),
        }
    }

    fn mul(self, other: Self) -> Self {
        Self {
            a: self.a.mul(other.a).add(self.b.mul(other.b).mul(Rat::from_i(11))),
            b: self.a.mul(other.b).add(self.b.mul(other.a)),
        }
    }

    fn div(self, other: Self) -> Self {
        let den = other.a.mul(other.a).sub(other.b.mul(other.b).mul(Rat::from_i(11)));
        let num_a = self.a.mul(other.a).sub(self.b.mul(other.b).mul(Rat::from_i(11)));
        let num_b = self.b.mul(other.a).sub(self.a.mul(other.b));
        Self {
            a: num_a.div(den),
            b: num_b.div(den),
        }
    }

    fn pow(self, n: u8) -> Self {
        let mut out = Self::int(1);
        for _ in 0..n {
            out = out.mul(self);
        }
        out
    }

    fn fmt(self) -> String {
        if self.b.is_zero() {
            return self.a.fmt();
        }
        let irr = format!("{}*sqrt(11)", self.b.fmt());
        if self.a.is_zero() {
            irr
        } else if self.b.n > 0 {
            format!("{}+{irr}", self.a.fmt())
        } else {
            format!("{}{irr}", self.a.fmt())
        }
    }
}

#[derive(Clone, Copy, Debug)]
struct Aff {
    c0: Alg,
    c1: Alg,
}

impl Aff {
    fn from_int_mu(c0: i128, c1: i128) -> Self {
        Self {
            c0: Alg::int(c0),
            c1: Alg::int(c1),
        }
    }

    fn is_zero(self) -> bool {
        self.c0.is_zero() && self.c1.is_zero()
    }

    fn add(self, other: Self) -> Self {
        Self {
            c0: self.c0.add(other.c0),
            c1: self.c1.add(other.c1),
        }
    }

    fn scale(self, k: Alg) -> Self {
        Self {
            c0: self.c0.mul(k),
            c1: self.c1.mul(k),
        }
    }

    fn mul(self, other: Self) -> Quad {
        Quad {
            c0: self.c0.mul(other.c0),
            c1: self.c0.mul(other.c1).add(self.c1.mul(other.c0)),
            c2: self.c1.mul(other.c1),
        }
    }

    fn fmt(self) -> String {
        Quad {
            c0: self.c0,
            c1: self.c1,
            c2: Alg::zero(),
        }
        .fmt()
    }
}

#[derive(Clone, Copy, Debug)]
struct Quad {
    c0: Alg,
    c1: Alg,
    c2: Alg,
}

impl Quad {
    fn from_aff(a: Aff) -> Self {
        Self {
            c0: a.c0,
            c1: a.c1,
            c2: Alg::zero(),
        }
    }

    fn add(self, other: Self) -> Self {
        Self {
            c0: self.c0.add(other.c0),
            c1: self.c1.add(other.c1),
            c2: self.c2.add(other.c2),
        }
    }

    fn scale(self, k: i128) -> Self {
        let k = Alg::int(k);
        Self {
            c0: self.c0.mul(k),
            c1: self.c1.mul(k),
            c2: self.c2.mul(k),
        }
    }

    fn fmt(self) -> String {
        let mut parts: Vec<String> = Vec::new();
        if !self.c0.is_zero() {
            parts.push(self.c0.fmt());
        }
        if !self.c1.is_zero() {
            parts.push(format!("{}*mu", self.c1.fmt()));
        }
        if !self.c2.is_zero() {
            parts.push(format!("{}*mu^2", self.c2.fmt()));
        }
        if parts.is_empty() {
            return "0".into();
        }
        let mut out = parts[0].clone();
        for part in parts.iter().skip(1) {
            if part.starts_with('-') {
                out.push_str(part);
            } else {
                out.push('+');
                out.push_str(part);
            }
        }
        out
    }
}

// ---------------------------------------------------------------------------
// Bivariate integer polynomials
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
struct Bi {
    terms: BTreeMap<(u8, u8), i128>,
}

impl Bi {
    fn zero() -> Self {
        Self {
            terms: BTreeMap::new(),
        }
    }

    fn constant(value: i128) -> Self {
        let mut out = Self::zero();
        if value != 0 {
            out.terms.insert((0, 0), value);
        }
        out
    }

    fn monom(i: u8, j: u8, coeff: i128) -> Self {
        let mut out = Self::zero();
        if coeff != 0 {
            out.terms.insert((i, j), coeff);
        }
        out
    }

    fn prune(&mut self) {
        self.terms.retain(|_, c| *c != 0);
    }

    fn add(&self, other: &Self) -> Self {
        let mut out = self.clone();
        for (exp, coeff) in &other.terms {
            *out.terms.entry(*exp).or_insert(0) += coeff;
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

    fn scale(&self, k: i128) -> Self {
        if k == 0 {
            return Self::zero();
        }
        let mut out = self.clone();
        for coeff in out.terms.values_mut() {
            *coeff *= k;
        }
        out
    }

    fn mul(&self, other: &Self) -> Self {
        let mut out = Self::zero();
        for (&(i1, j1), c1) in &self.terms {
            for (&(i2, j2), c2) in &other.terms {
                *out.terms.entry((i1 + i2, j1 + j2)).or_insert(0) += c1 * c2;
            }
        }
        out.prune();
        out
    }

    fn pow(&self, mut n: u32) -> Self {
        let mut out = Self::constant(1);
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

    fn dx(&self) -> Self {
        let mut out = Self::zero();
        for (&(i, j), coeff) in &self.terms {
            if i == 0 {
                continue;
            }
            *out.terms.entry((i - 1, j)).or_insert(0) += coeff * i128::from(i);
        }
        out.prune();
        out
    }

    fn dy(&self) -> Self {
        let mut out = Self::zero();
        for (&(i, j), coeff) in &self.terms {
            if j == 0 {
                continue;
            }
            *out.terms.entry((i, j - 1)).or_insert(0) += coeff * i128::from(j);
        }
        out.prune();
        out
    }

    fn eval(&self, x: i128, y: i128) -> i128 {
        let mut total = 0i128;
        for (&(i, j), coeff) in &self.terms {
            total += coeff * pow_i128(x, i) * pow_i128(y, j);
        }
        total
    }

    fn coeff(&self, i: u8, j: u8) -> i128 {
        self.terms.get(&(i, j)).copied().unwrap_or(0)
    }

    fn homog(&self, deg: u8) -> Self {
        let mut out = Self::zero();
        for (&(i, j), coeff) in &self.terms {
            if i + j == deg {
                out.terms.insert((i, j), *coeff);
            }
        }
        out
    }

    fn degree(&self) -> i32 {
        self.terms
            .keys()
            .map(|(i, j)| i32::from(*i + *j))
            .max()
            .unwrap_or(-1)
    }

    fn translate(&self, x0: i128, y0: i128) -> Self {
        let mut out = Self::zero();
        for (&(i, j), coeff) in &self.terms {
            for ku in 0..=i {
                for kv in 0..=j {
                    let c = *coeff
                        * binom(i, ku)
                        * pow_i128(x0, i - ku)
                        * binom(j, kv)
                        * pow_i128(y0, j - kv);
                    *out.terms.entry((ku, kv)).or_insert(0) += c;
                }
            }
        }
        out.prune();
        out
    }

    fn fmt_xy(&self) -> String {
        let mut items: Vec<((u8, u8), i128)> = self
            .terms
            .iter()
            .filter(|(_, c)| **c != 0)
            .map(|(e, c)| (*e, *c))
            .collect();
        items.sort_by(|a, b| b.0 .0.cmp(&a.0 .0).then(b.0 .1.cmp(&a.0 .1)));
        if items.is_empty() {
            return "0".into();
        }
        let mut chunks = Vec::new();
        for ((i, j), coeff) in items {
            let mut vars = String::new();
            if i == 1 {
                vars.push_str("*x");
            } else if i > 1 {
                vars.push_str(&format!("*x^{i}"));
            }
            if j == 1 {
                vars.push_str("*y");
            } else if j > 1 {
                vars.push_str(&format!("*y^{j}"));
            }
            let body = if vars.is_empty() {
                coeff.to_string()
            } else if coeff == 1 {
                vars[1..].to_string()
            } else if coeff == -1 {
                format!("-{}", &vars[1..])
            } else {
                format!("{coeff}{vars}")
            };
            if chunks.is_empty() {
                chunks.push(body);
            } else if body.starts_with('-') {
                chunks.push(body);
            } else {
                chunks.push(format!("+{body}"));
            }
        }
        chunks.concat()
    }

    fn from_terms(terms: &[BTreeMap<String, JsonAtom>]) -> Self {
        let mut out = Self::zero();
        for item in terms {
            let mut i = 0u8;
            let mut j = 0u8;
            let mut coeff = 0i128;
            for (key, atom) in item {
                if key == "coeff" {
                    coeff = atom.as_int128();
                } else if key == "x" {
                    i = atom.as_u8();
                } else if key == "y" {
                    j = atom.as_u8();
                } else {
                    panic!("unexpected term key {key}");
                }
            }
            *out.terms.entry((i, j)).or_insert(0) += coeff;
        }
        out.prune();
        out
    }

    fn equals(&self, other: &Self) -> bool {
        self.terms == other.terms
    }
}

fn x() -> Bi {
    Bi::monom(1, 0, 1)
}

fn y() -> Bi {
    Bi::monom(0, 1, 1)
}

fn primitive_field() -> (Bi, Bi) {
    let xx = x();
    let yy = y();
    let inner = xx
        .pow(3)
        .add(&xx.pow(2).scale(2))
        .sub(&xx.mul(&yy.pow(2)))
        .sub(&xx.scale(3))
        .add(&Bi::constant(4));
    let p = yy.mul(&inner);
    let q = xx
        .pow(4)
        .scale(15)
        .sub(&xx.pow(3).scale(21))
        .add(&xx.pow(2).mul(&yy.pow(2)).scale(3))
        .sub(&xx.pow(2).scale(15))
        .add(&xx.mul(&yy.pow(2)).scale(7))
        .sub(&xx.scale(11))
        .sub(&yy.pow(4).scale(2))
        .add(&yy.pow(2).scale(6));
    (p, q)
}

// ---------------------------------------------------------------------------
// L1
// ---------------------------------------------------------------------------

struct Jet {
    a20: Aff,
    a11: Aff,
    a02: Aff,
    b20: Aff,
    b11: Aff,
    b02: Aff,
    a30: Aff,
    a12: Aff,
    b21: Aff,
    b03: Aff,
}

fn l1_e(j: &Jet) -> Quad {
    j.a20
        .add(j.a02)
        .mul(j.a11)
        .add(j.a02.mul(j.b02).scale(2))
        .add(j.a20.mul(j.b20).scale(-2))
        .add(j.b20.add(j.b02).mul(j.b11).scale(-1))
}

fn l1_cubic(j: &Jet) -> Quad {
    Quad::from_aff(j.a30)
        .scale(3)
        .add(Quad::from_aff(j.a12))
        .add(Quad::from_aff(j.b21))
        .add(Quad::from_aff(j.b03).scale(3))
}

fn l1_full(j: &Jet) -> Quad {
    l1_e(j).add(l1_cubic(j))
}

fn l1_int(a20: i128, a11: i128, a02: i128, b20: i128, b11: i128, b02: i128) -> i128 {
    (a20 + a02) * a11 - (b20 + b02) * b11 - 2 * a20 * b20 + 2 * a02 * b02
}

fn check_families() {
    assert_eq!(l1_int(1, 0, 0, 1, 0, 0), -2, "generic focus");
    // Hamiltonian A=1, B=-2, C=3, D=-1.
    assert_eq!(l1_int(2, -6, 3, 3, -4, 3), 0, "hamiltonian");
    assert_eq!(l1_int(-10, 5, 1, 1, -25, 0), 0, "shi");
}

fn scale_monom(old: Aff, i: u8, j: u8, alpha: Alg, beta: Alg, den: Alg) -> Aff {
    // old * alpha^i * beta^j / den
    let factor = alpha.pow(i).mul(beta.pow(j)).div(den);
    old.scale(factor)
}

fn normal_form(p0: &Bi, dp: &Bi, q0: &Bi, dq: &Bi, x0: i128, y0: i128) -> (Aff, Option<(Quad, Quad, Quad)>) {
    let pt0 = p0.translate(x0, y0);
    let qt0 = q0.translate(x0, y0);
    let dpt = dp.translate(x0, y0);
    let dqt = dq.translate(x0, y0);
    assert_eq!(p0.eval(x0, y0), 0);
    assert_eq!(q0.eval(x0, y0), 0);
    assert_eq!(dp.eval(x0, y0), 0);
    assert_eq!(dq.eval(x0, y0), 0);

    let jxx0 = p0.dx().eval(x0, y0);
    let jxy0 = p0.dy().eval(x0, y0);
    let jyx0 = q0.dx().eval(x0, y0);
    let jyy0 = q0.dy().eval(x0, y0);
    let jxx1 = dp.dx().eval(x0, y0);
    let _jxy1 = dp.dy().eval(x0, y0);
    let _jyx1 = dq.dx().eval(x0, y0);
    let jyy1 = dq.dy().eval(x0, y0);
    let trace = Aff::from_int_mu(jxx0 + jyy0, jxx1 + jyy1);
    if !trace.is_zero() {
        return (trace, None);
    }
    assert_eq!(jxx0, 0);
    assert_eq!(jyy0, 0);
    assert_eq!(jxx1, 0);
    assert_eq!(jyy1, 0);
    let p_lin = jxy0;
    let q_lin = jyx0;
    let omega2 = -p_lin * q_lin;
    assert!(omega2 > 0, "det must be positive");

    let (alpha, beta, omega) = if x0 == 0 && y0 == 0 {
        assert_eq!((p_lin, q_lin, omega2), (4, -11, 44));
        (
            Alg::int(1),
            Alg::sqrt11(Rat::new(-1, 2)),
            Alg::sqrt11(Rat::from_i(2)),
        )
    } else {
        assert_eq!((p_lin, q_lin, omega2), (-8, 8, 64));
        (Alg::int(1), Alg::int(1), Alg::int(8))
    };

    let den_p = alpha.mul(omega);
    let den_q = beta.mul(omega);
    let aff = |base: &Bi, extra: &Bi, i: u8, j: u8| Aff::from_int_mu(base.coeff(i, j), extra.coeff(i, j));

    let a10 = scale_monom(aff(&pt0, &dpt, 1, 0), 1, 0, alpha, beta, den_p);
    let a01 = scale_monom(aff(&pt0, &dpt, 0, 1), 0, 1, alpha, beta, den_p);
    let b10 = scale_monom(aff(&qt0, &dqt, 1, 0), 1, 0, alpha, beta, den_q);
    let b01 = scale_monom(aff(&qt0, &dqt, 0, 1), 0, 1, alpha, beta, den_q);
    assert!(a10.is_zero(), "normal a10");
    assert!(b01.is_zero(), "normal b01");
    assert_eq!(a01.c0, Alg::int(-1), "normal a01");
    assert!(a01.c1.is_zero());
    assert_eq!(b10.c0, Alg::int(1), "normal b10");
    assert!(b10.c1.is_zero());

    let jet = Jet {
        a20: scale_monom(aff(&pt0, &dpt, 2, 0), 2, 0, alpha, beta, den_p),
        a11: scale_monom(aff(&pt0, &dpt, 1, 1), 1, 1, alpha, beta, den_p),
        a02: scale_monom(aff(&pt0, &dpt, 0, 2), 0, 2, alpha, beta, den_p),
        b20: scale_monom(aff(&qt0, &dqt, 2, 0), 2, 0, alpha, beta, den_q),
        b11: scale_monom(aff(&qt0, &dqt, 1, 1), 1, 1, alpha, beta, den_q),
        b02: scale_monom(aff(&qt0, &dqt, 0, 2), 0, 2, alpha, beta, den_q),
        a30: scale_monom(aff(&pt0, &dpt, 3, 0), 3, 0, alpha, beta, den_p),
        a12: scale_monom(aff(&pt0, &dpt, 1, 2), 1, 2, alpha, beta, den_p),
        b21: scale_monom(aff(&qt0, &dqt, 2, 1), 2, 1, alpha, beta, den_q),
        b03: scale_monom(aff(&qt0, &dqt, 0, 3), 0, 3, alpha, beta, den_q),
    };
    (trace, Some((l1_e(&jet), l1_cubic(&jet), l1_full(&jet))))
}

fn jacobian_unperturbed(p: &Bi, q: &Bi, x0: i128, y0: i128) -> (i128, i128, i128, i128, i128, i128) {
    let jxx = p.dx().eval(x0, y0);
    let jxy = p.dy().eval(x0, y0);
    let jyx = q.dx().eval(x0, y0);
    let jyy = q.dy().eval(x0, y0);
    let trace = jxx + jyy;
    let det = jxx * jyy - jxy * jyx;
    (jxx, jxy, jyx, jyy, trace, det)
}

fn user_dp() -> Bi {
    // x(x-1)y = x^2 y - x y
    x().pow(2).mul(&y()).sub(&x().mul(&y()))
}

fn tracefree_dp() -> Bi {
    // x(x-1)^2 y
    x().mul(&x().sub(&Bi::constant(1)).pow(2)).mul(&y())
}

fn x2_dp() -> Bi {
    // x^2 (x-1)^2
    x().pow(2).mul(&x().sub(&Bi::constant(1)).pow(2))
}

// ---------------------------------------------------------------------------
// Tiny JSON reader (certificate shape only)
// ---------------------------------------------------------------------------

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
        u8::try_from(self.as_int128()).expect("exponent fits u8")
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

fn arr<'a>(map: &'a BTreeMap<String, Json>, key: &str) -> &'a Vec<Json> {
    match map.get(key) {
        Some(Json::Array(items)) => items,
        _ => panic!("missing array {key}"),
    }
}

fn json_str(map: &BTreeMap<String, Json>, key: &str) -> String {
    match map.get(key) {
        Some(Json::String(s)) => s.clone(),
        _ => panic!("missing string {key}"),
    }
}

fn json_i64(map: &BTreeMap<String, Json>, key: &str) -> i64 {
    match map.get(key) {
        Some(Json::Number(n)) => *n,
        _ => panic!("missing number {key}"),
    }
}

fn str_list(items: &[Json]) -> Vec<String> {
    items
        .iter()
        .map(|v| match v {
            Json::String(s) => s.clone(),
            _ => panic!("expected string"),
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

// ---------------------------------------------------------------------------
// Drivers
// ---------------------------------------------------------------------------

struct CenterRow {
    x0: i128,
    y0: i128,
    jxx: i128,
    jxy: i128,
    jyx: i128,
    jyy: i128,
    det: i128,
    l1_e: String,
    l1_c: String,
    l1_f: String,
}

fn check_all() -> (
    Vec<CenterRow>,
    [String; 4],
    [String; 3],
    [String; 3],
    [String; 3],
    [String; 3],
) {
    check_families();
    let (p, q) = primitive_field();
    assert_eq!(p.degree(), 4);
    assert_eq!(q.degree(), 4);
    let z = Bi::zero();
    let centers = [(0i128, 0i128), (1, 2), (1, -2)];
    let expect_j = [(0, 4, -11, 0), (0, -8, 8, 0), (0, -8, 8, 0)];
    let expect_det = [44i128, 64, 64];
    let mut rows = Vec::new();
    for (idx, (x0, y0)) in centers.iter().copied().enumerate() {
        assert_eq!(p.eval(x0, y0), 0);
        assert_eq!(q.eval(x0, y0), 0);
        let (jxx, jxy, jyx, jyy, trace, det) = jacobian_unperturbed(&p, &q, x0, y0);
        assert_eq!(trace, 0);
        assert_eq!(det, expect_det[idx]);
        assert_eq!((jxx, jxy, jyx, jyy), expect_j[idx]);
        let (tr, l1s) = normal_form(&p, &z, &q, &z, x0, y0);
        assert!(tr.is_zero());
        let (le, lc, lf) = l1s.expect("unperturbed is a weak focus / center");
        assert_eq!(lf.fmt(), "0", "unperturbed L1_full at ({x0},{y0})");
        rows.push(CenterRow {
            x0,
            y0,
            jxx,
            jxy,
            jyx,
            jyy,
            det,
            l1_e: le.fmt(),
            l1_c: lc.fmt(),
            l1_f: lf.fmt(),
        });
    }
    assert_eq!(rows[0].l1_e, "0");
    assert_eq!(rows[1].l1_e, "9/2");
    assert_eq!(rows[2].l1_e, "-9/2");
    assert_eq!(rows[0].l1_c, "0");
    assert_eq!(rows[1].l1_c, "-9/2");
    assert_eq!(rows[2].l1_c, "9/2");

    let origin_p2 = p.homog(2).fmt_xy();
    let origin_q2 = q.homog(2).fmt_xy();
    let origin_p3 = p.homog(3).fmt_xy();
    let origin_q3 = q.homog(3).fmt_xy();
    assert_eq!(origin_p2, "-3*x*y");
    assert_eq!(origin_q2, "-15*x^2+6*y^2");
    assert_eq!(origin_p3, "2*x^2*y");
    assert_eq!(origin_q3, "-21*x^3+7*x*y^2");
    assert_eq!(p.homog(1).fmt_xy(), "4*y");
    assert_eq!(q.homog(1).fmt_xy(), "-11*x");

    let mut user_tr = Vec::new();
    let mut user_l1 = Vec::new();
    let udp = user_dp();
    for (x0, y0) in centers {
        let (tr, l1s) = normal_form(&p, &udp, &q, &z, x0, y0);
        user_tr.push(tr.fmt());
        user_l1.push(match l1s {
            None => "strong".into(),
            Some((_, _, lf)) => lf.fmt(),
        });
    }
    assert_eq!(user_tr, ["0", "2*mu", "-2*mu"]);
    assert_eq!(user_l1, ["0", "strong", "strong"]);

    let mut tf_l1 = Vec::new();
    let tdp = tracefree_dp();
    for (x0, y0) in centers {
        let (tr, l1s) = normal_form(&p, &tdp, &q, &z, x0, y0);
        assert!(tr.is_zero());
        tf_l1.push(l1s.unwrap().2.fmt());
    }
    assert_eq!(tf_l1, ["0", "-1*mu", "1*mu"]);

    let mut x2_l1 = Vec::new();
    let xdp = x2_dp();
    for (x0, y0) in centers {
        let (tr, l1s) = normal_form(&p, &xdp, &q, &z, x0, y0);
        assert!(tr.is_zero());
        x2_l1.push(l1s.unwrap().2.fmt());
    }
    assert_eq!(
        x2_l1,
        [
            "-351/968*sqrt(11)*mu",
            "-1/8*mu",
            "-1/8*mu"
        ]
    );

    (
        rows,
        [origin_p2, origin_q2, origin_p3, origin_q3],
        user_tr.try_into().unwrap(),
        user_l1.try_into().unwrap(),
        tf_l1.try_into().unwrap(),
        x2_l1.try_into().unwrap(),
    )
}

fn check_certificate(text: &str, x2_l1: &[String]) {
    let root = parse_json(text);
    let (p, q) = primitive_field();
    let field = obj(&root, "field");
    assert_eq!(json_i64(field, "deg_P"), 4);
    assert_eq!(json_i64(field, "deg_Q"), 4);
    let p_cert = Bi::from_terms(&term_list(field, "P"));
    let q_cert = Bi::from_terms(&term_list(field, "Q"));
    assert!(p.equals(&p_cert), "cert P");
    assert!(q.equals(&q_cert), "cert Q");

    match &root {
        Json::Object(map) => {
            assert_eq!(json_str(map, "schema"), "hilbert16-gg-pt-lyapunov/v1");
        }
        _ => panic!("root"),
    }

    let centers = match &root {
        Json::Object(map) => arr(map, "centers"),
        _ => panic!("centers"),
    };
    let dets: Vec<i64> = centers
        .iter()
        .map(|c| match c {
            Json::Object(m) => json_i64(m, "det"),
            _ => panic!("center"),
        })
        .collect();
    assert_eq!(dets, vec![44, 64, 64]);
    let l1f: Vec<String> = centers
        .iter()
        .map(|c| match c {
            Json::Object(m) => json_str(m, "L1_full"),
            _ => panic!("center"),
        })
        .collect();
    assert_eq!(l1f, ["0", "0", "0"]);
    let l1e: Vec<String> = centers
        .iter()
        .map(|c| match c {
            Json::Object(m) => json_str(m, "L1_E"),
            _ => panic!("center"),
        })
        .collect();
    assert_eq!(l1e, ["0", "9/2", "-9/2"]);

    let jet = obj(&root, "origin_jet");
    assert_eq!(json_str(jet, "P2"), "-3*x*y");
    assert_eq!(json_str(jet, "Q2"), "-15*x^2+6*y^2");
    assert_eq!(json_str(jet, "P3"), "2*x^2*y");
    assert_eq!(json_str(jet, "Q3"), "-21*x^3+7*x*y^2");

    let perts = obj(&root, "perturbations");
    let user = perts.get("user_xy").and_then(|v| match v {
        Json::Object(m) => Some(m),
        _ => None,
    }).expect("user_xy");
    assert_eq!(str_list(arr(user, "traces")), ["0", "2*mu", "-2*mu"]);
    assert_eq!(str_list(arr(user, "L1_full")), ["0", "strong", "strong"]);
    let tf = perts.get("tracefree_xy").and_then(|v| match v {
        Json::Object(m) => Some(m),
        _ => None,
    }).expect("tracefree_xy");
    assert_eq!(str_list(arr(tf, "L1_full")), ["0", "-1*mu", "1*mu"]);
    let x2 = perts.get("x2_shift").and_then(|v| match v {
        Json::Object(m) => Some(m),
        _ => None,
    }).expect("x2_shift");
    assert_eq!(str_list(arr(x2, "L1_full")), x2_l1);
}

fn dump_lines(
    rows: &[CenterRow],
    origin: &[String; 4],
    user_tr: &[String; 3],
    user_l1: &[String; 3],
    tf_l1: &[String; 3],
    x2_l1: &[String; 3],
) -> String {
    let mut lines = vec![
        "status DROP 29 KEEP L1=0".to_string(),
        "field_degree 4 4".to_string(),
    ];
    for r in rows {
        lines.push(format!(
            "center {} {} equilibrium 1 trace 0 det {}",
            r.x0, r.y0, r.det
        ));
    }
    for r in rows {
        lines.push(format!(
            "jacobian {} {} {} {} {} {}",
            r.x0, r.y0, r.jxx, r.jxy, r.jyx, r.jyy
        ));
    }
    lines.push(format!("origin_after_linear P2 {}", origin[0]));
    lines.push(format!("origin_after_linear Q2 {}", origin[1]));
    lines.push(format!("origin_after_linear P3 {}", origin[2]));
    lines.push(format!("origin_after_linear Q3 {}", origin[3]));
    lines.push(format!(
        "L1_E_unperturbed {} {} {}",
        rows[0].l1_e, rows[1].l1_e, rows[2].l1_e
    ));
    lines.push(format!(
        "L1_cubic_unperturbed {} {} {}",
        rows[0].l1_c, rows[1].l1_c, rows[2].l1_c
    ));
    lines.push(format!(
        "L1_full_unperturbed {} {} {}",
        rows[0].l1_f, rows[1].l1_f, rows[2].l1_f
    ));
    for (term, coeff) in [
        ("a02*a11", 1),
        ("a02*b02", 2),
        ("a11*a20", 1),
        ("a20*b20", -2),
        ("b02*b11", -1),
        ("b11*b20", -1),
    ] {
        lines.push(format!("L1_E {term} {coeff}"));
    }
    for (term, coeff) in [("a12", 1), ("a30", 3), ("b03", 3), ("b21", 1)] {
        lines.push(format!("L1_cubic {term} {coeff}"));
    }
    lines.push("V1_over_L1 1/8".into());
    lines.push("generic_focus_L1 -2".into());
    lines.push("hamiltonian_L1 0".into());
    lines.push(format!(
        "user_pert_trace {} {} {}",
        user_tr[0], user_tr[1], user_tr[2]
    ));
    lines.push(format!(
        "user_pert_L1_full {} {} {}",
        user_l1[0], user_l1[1], user_l1[2]
    ));
    lines.push(format!(
        "tf_pert_L1_full {} {} {}",
        tf_l1[0], tf_l1[1], tf_l1[2]
    ));
    lines.push(format!(
        "x2_pert_L1_full {} {} {}",
        x2_l1[0], x2_l1[1], x2_l1[2]
    ));
    let mut text = lines.join("\n");
    text.push('\n');
    text
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

    let (rows, origin, user_tr, user_l1, tf_l1, x2_l1) = check_all();

    let cert_path = PathBuf::from("certs/lyapunov.json");
    let text = fs::read_to_string(&cert_path)
        .unwrap_or_else(|err| panic!("read {}: {err}", cert_path.display()));
    check_certificate(&text, &x2_l1);

    let dump = dump_lines(&rows, &origin, &user_tr, &user_l1, &tf_l1, &x2_l1);
    if let Some(path) = dump_path {
        fs::write(path, &dump).expect("write dump");
    }
    print!("{dump}");
    println!("VALID gg-pt-lyapunov identities");
}
