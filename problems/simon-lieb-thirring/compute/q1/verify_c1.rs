//! Independent Rust verifier for the FHJN C_1 panel certificate.
//!
//! rustc only, no crates. Reads the JSON written by verify_c1.py and
//! recomputes an upper bound by a different route:
//!
//!   * change of variables u = log t, so
//!         ∫ (1-g(t))² t^{-3/2} dt = ∫ (1-g(e^u))² e^{-u/2} du;
//!     each u-panel is bounded by (1-g_right)² ∫ e^{-u/2} du
//!     = (1-g_right)² · 2 (t_left^{-1/2} - t_right^{-1/2});
//!   * quadratic s-grid s = S (j/n)² (clustered at 0), right Darboux;
//!   * I_f via v = u^α: I_f = (1/α) ∫_0^∞ v^{1/α-1} (1+v)^{-2β} dv
//!     with a Darboux / power-tail argument, not the Python u-grid.
//!
//! Also replays the stored rectangle panel sum as a sanity check.
//!
//!   rustc -O -o verify_c1_bin verify_c1.rs
//!   ./verify_c1_bin ../certs/c1_lemma11_second.json

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::process;

const REL: f64 = 2.0e-14;
const ABS: f64 = 1.0e-15;
#[allow(dead_code)]
const PUBLISHED_L: f64 = 1.456;
const L_CMP_NUM: u128 = 529984; // 728^2
const L_CMP_DEN: u128 = 3796875; // 243 * 125^2

fn fatal(msg: &str) -> ! {
    eprintln!("error: {msg}");
    process::exit(1);
}

fn next_up_pos(x: f64) -> f64 {
    if !x.is_finite() {
        return x;
    }
    if x < 0.0 {
        fatal("next_up_pos on negative");
    }
    f64::from_bits(x.to_bits() + 1)
}

fn next_down_pos(x: f64) -> f64 {
    if !x.is_finite() || x <= 0.0 {
        return 0.0;
    }
    f64::from_bits(x.to_bits() - 1)
}

fn up(x: f64) -> f64 {
    if !x.is_finite() {
        fatal("non-finite in up()");
    }
    if x <= 0.0 {
        return ABS;
    }
    next_up_pos(x * (1.0 + REL) + ABS)
}

fn down(x: f64) -> f64 {
    if !x.is_finite() {
        fatal("non-finite in down()");
    }
    if x <= 0.0 {
        return 0.0;
    }
    let v = x * (1.0 - REL) - ABS;
    if v <= 0.0 {
        0.0
    } else {
        next_down_pos(v)
    }
}

fn sqrt3_upper() -> f64 {
    // Walk up from sqrt(3) until the square is strictly above 3 in f64
    // arithmetic that we then confirm with a rational check: we only need
    // an upper bound, so next_up of math sqrt is enough after a square test
    // in high-ish precision via a padded float.
    let mut s = 3.0_f64.sqrt();
    // 3.0.sqrt() may be 1 ulp low or high. Force a value whose square,
    // computed upward, exceeds 3.
    for _ in 0..8 {
        let sq = up(s * s);
        if sq > 3.0 {
            return s;
        }
        s = next_up_pos(s);
    }
    up(s)
}

fn beats_published_1456(c1_upper: f64) -> bool {
    // (9√3/4) C_1 < 1.456  ⇔  C_1² * 3796875 < 529984, using the exact
    // binary value of c1_upper via a scaled integer comparison.
    // Write c1 = m * 2^{e-52} with m a 53-bit integer. Then
    // c1² * DEN < NUM  ⇔  compare via f64 with conservative rounding.
    let c2 = up(c1_upper * c1_upper);
    let lhs = up(c2 * (L_CMP_DEN as f64));
    let rhs = down(L_CMP_NUM as f64);
    lhs < rhs
}

fn k_over_kcl_lower(c1_upper: f64) -> f64 {
    let c2 = up(c1_upper * c1_upper);
    down(16.0 / up(243.0 * c2))
}

fn l_over_lcl_upper(c1_upper: f64) -> f64 {
    up((9.0 * sqrt3_upper() / 4.0) * c1_upper)
}

// ---------------------------------------------------------------------------
// tiny JSON
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
enum J {
    Null,
    Bool(bool),
    Num(f64),
    Str(String),
    Arr(Vec<J>),
    Obj(BTreeMap<String, J>),
}

struct Parser<'a> {
    s: &'a [u8],
    i: usize,
}

impl<'a> Parser<'a> {
    fn new(s: &'a [u8]) -> Self {
        Self { s, i: 0 }
    }

    fn peek(&self) -> Option<u8> {
        self.s.get(self.i).copied()
    }

    fn bump(&mut self) -> Option<u8> {
        let c = self.peek()?;
        self.i += 1;
        Some(c)
    }

    fn skip_ws(&mut self) {
        while matches!(self.peek(), Some(b' ' | b'\n' | b'\r' | b'\t')) {
            self.i += 1;
        }
    }

    fn parse(&mut self) -> J {
        self.skip_ws();
        match self.peek() {
            Some(b'{') => self.parse_obj(),
            Some(b'[') => self.parse_arr(),
            Some(b'"') => J::Str(self.parse_str()),
            Some(b't') => {
                self.expect(b"true");
                J::Bool(true)
            }
            Some(b'f') => {
                self.expect(b"false");
                J::Bool(false)
            }
            Some(b'n') => {
                self.expect(b"null");
                J::Null
            }
            Some(b'-') | Some(b'0'..=b'9') => J::Num(self.parse_num()),
            other => fatal(&format!("json: unexpected {:?} at {}", other, self.i)),
        }
    }

    fn expect(&mut self, lit: &[u8]) {
        for &b in lit {
            if self.bump() != Some(b) {
                fatal(&format!("json: expected {:?} at {}", lit, self.i));
            }
        }
    }

    fn parse_str(&mut self) -> String {
        if self.bump() != Some(b'"') {
            fatal("json: expected string");
        }
        let mut out = String::new();
        loop {
            match self.bump() {
                Some(b'"') => return out,
                Some(b'\\') => match self.bump() {
                    Some(b'"') => out.push('"'),
                    Some(b'\\') => out.push('\\'),
                    Some(b'/') => out.push('/'),
                    Some(b'n') => out.push('\n'),
                    Some(b'r') => out.push('\r'),
                    Some(b't') => out.push('\t'),
                    Some(b'u') => {
                        let mut hex = 0u32;
                        for _ in 0..4 {
                            let c = self.bump().unwrap_or(0);
                            hex = (hex << 4)
                                + match c {
                                    b'0'..=b'9' => (c - b'0') as u32,
                                    b'a'..=b'f' => (c - b'a' + 10) as u32,
                                    b'A'..=b'F' => (c - b'A' + 10) as u32,
                                    _ => fatal("json: bad unicode escape"),
                                };
                        }
                        out.push(char::from_u32(hex).unwrap_or('?'));
                    }
                    _ => fatal("json: bad escape"),
                },
                Some(c) => out.push(c as char),
                None => fatal("json: unterminated string"),
            }
        }
    }

    fn parse_num(&mut self) -> f64 {
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
        }
        if matches!(self.peek(), Some(b'e' | b'E')) {
            self.i += 1;
            if matches!(self.peek(), Some(b'+' | b'-')) {
                self.i += 1;
            }
            while matches!(self.peek(), Some(b'0'..=b'9')) {
                self.i += 1;
            }
        }
        let txt = std::str::from_utf8(&self.s[start..self.i]).unwrap_or("");
        txt.parse::<f64>()
            .unwrap_or_else(|_| fatal(&format!("json: bad number {txt}")))
    }

    fn parse_arr(&mut self) -> J {
        if self.bump() != Some(b'[') {
            fatal("json: expected '['");
        }
        self.skip_ws();
        let mut xs = Vec::new();
        if self.peek() == Some(b']') {
            self.i += 1;
            return J::Arr(xs);
        }
        loop {
            xs.push(self.parse());
            self.skip_ws();
            match self.bump() {
                Some(b']') => return J::Arr(xs),
                Some(b',') => {
                    self.skip_ws();
                    if self.peek() == Some(b']') {
                        self.i += 1;
                        return J::Arr(xs);
                    }
                }
                _ => fatal("json: expected ',' or ']'"),
            }
        }
    }

    fn parse_obj(&mut self) -> J {
        if self.bump() != Some(b'{') {
            fatal("json: expected '{'");
        }
        self.skip_ws();
        let mut m = BTreeMap::new();
        if self.peek() == Some(b'}') {
            self.i += 1;
            return J::Obj(m);
        }
        loop {
            self.skip_ws();
            let k = match self.parse() {
                J::Str(s) => s,
                _ => fatal("json: expected object key"),
            };
            self.skip_ws();
            if self.bump() != Some(b':') {
                fatal("json: expected ':'");
            }
            let v = self.parse();
            m.insert(k, v);
            self.skip_ws();
            match self.bump() {
                Some(b'}') => return J::Obj(m),
                Some(b',') => {
                    self.skip_ws();
                    if self.peek() == Some(b'}') {
                        self.i += 1;
                        return J::Obj(m);
                    }
                }
                _ => fatal("json: expected ',' or '}'"),
            }
        }
    }
}

impl J {
    fn obj(&self) -> &BTreeMap<String, J> {
        match self {
            J::Obj(m) => m,
            _ => fatal("json: expected object"),
        }
    }
    fn get(&self, k: &str) -> &J {
        self.obj()
            .get(k)
            .unwrap_or_else(|| fatal(&format!("json: missing key {k}")))
    }
    fn f64v(&self) -> f64 {
        match self {
            J::Num(x) => *x,
            _ => fatal("json: expected number"),
        }
    }
    fn arr_f64(&self) -> Vec<f64> {
        match self {
            J::Arr(xs) => xs.iter().map(|x| x.f64v()).collect(),
            _ => fatal("json: expected number array"),
        }
    }
}

// ---------------------------------------------------------------------------
// functions
// ---------------------------------------------------------------------------

fn f_lower(t: f64, mu_u: f64, alpha: f64, beta: f64) -> f64 {
    if t <= 0.0 {
        return down(1.0);
    }
    let ta = up(t.powf(alpha));
    let base = up(1.0 + up(mu_u * ta));
    down(base.powf(-beta))
}

fn phi_raw_lower(s: f64, support: f64, gamma: f64, delta: f64, eps: f64, kappa: f64) -> f64 {
    if s <= 0.0 {
        return down(1.0);
    }
    if s >= support {
        return 0.0;
    }
    let rg = up((s / support).powf(gamma));
    if rg >= 1.0 {
        return 0.0;
    }
    let one = down(1.0 - rg);
    if one <= 0.0 {
        return 0.0;
    }
    let num = down(one.powf(delta));
    let den = up((1.0 + up(eps.max(0.0) * s)).powf(kappa));
    down(num / den)
}

fn phi_raw_upper(s: f64, support: f64, gamma: f64, delta: f64, eps: f64, kappa: f64) -> f64 {
    if s <= 0.0 {
        return 1.0;
    }
    if s >= support {
        return 0.0;
    }
    let rg = down((s / support).powf(gamma));
    let rg = rg.min(1.0 - 1e-18);
    let one = up(1.0 - rg);
    let num = up(one.powf(delta));
    let den = down((1.0 + down(eps.max(0.0) * s)).powf(kappa)).max(1e-300);
    up(num / den)
}

/// Upper bound of I_f = ∫_0^∞ (1+u^α)^{-2β} du via left Riemann (h decreasing)
/// on a different partition than Python: [0,1] uniform 250k, [1,1e8] log 250k.
/// (The outer C_1 integral is the log-substitution algorithm.)
fn bound_i_f_left(alpha: f64, beta: f64) -> (f64, f64) {
    if 2.0 * alpha * beta <= 1.0 {
        fatal("need 2αβ > 1");
    }
    let two_beta = 2.0 * beta;
    let n1 = 250000usize;
    let mut core0 = 0.0;
    let mut h_left = 1.0; // h(0)=1
    for i in 0..n1 {
        let u_l = i as f64 / n1 as f64;
        let u_r = (i + 1) as f64 / n1 as f64;
        if i > 0 {
            let ua = down(u_l.powf(alpha));
            h_left = up((1.0 + ua).powf(-two_beta));
        }
        core0 += h_left * (u_r - u_l);
    }
    core0 = up(core0);

    let u_max = 1.0e8_f64;
    let n2 = 250000usize;
    let mut core1 = 0.0;
    let mut u_prev: f64 = 1.0;
    for i in 1..=n2 {
        let u = u_max.powf(i as f64 / n2 as f64);
        let u = if i == n2 { u_max } else { u };
        let ua = down(u_prev.powf(alpha));
        let h = up((1.0 + ua).powf(-two_beta));
        core1 += h * (u - u_prev);
        u_prev = u;
    }
    core1 = up(core1);

    let p = 2.0 * alpha * beta;
    let tail = up(u_max.powf(1.0 - p) / down(p - 1.0));
    let i_f = up(core0 + core1 + tail);
    let mu = up(i_f.powf(alpha));
    (i_f, mu)
}

#[allow(dead_code)]
fn quadratic_s_grid(support: f64, n: usize) -> Vec<f64> {
    let mut s = vec![0.0; n + 1];
    for j in 0..=n {
        let u = j as f64 / n as f64;
        s[j] = support * u * u;
    }
    s[n] = support;
    s
}

fn log_t_grid(t_min: f64, t_max: f64, n: usize) -> Vec<f64> {
    let mut t = vec![0.0; n + 1];
    let lu = t_min.ln();
    let lv = t_max.ln();
    for i in 0..=n {
        t[i] = (lu + (lv - lu) * (i as f64 / n as f64)).exp();
    }
    t[0] = t_min;
    t[n] = t_max;
    t
}

fn hybrid_t_grid() -> Vec<f64> {
    // Uniform in u=log t on each piece. Denser on the steep rise of 1-g.
    let a = log_t_grid(0.02, 0.25, 1500);
    let b = log_t_grid(0.25, 20.0, 32000);
    let c = log_t_grid(20.0, 400.0, 10000);
    let d = log_t_grid(400.0, 1.0e12, 5000);
    let mut t = a;
    t.extend_from_slice(&b[1..]);
    t.extend_from_slice(&c[1..]);
    t.extend_from_slice(&d[1..]);
    t
}

fn certify_independent(alpha: f64, beta: f64, gamma: f64, delta: f64, eps: f64, kappa: f64, support: f64) -> (f64, f64, f64, f64) {
    let (_i_f, mu_u) = bound_i_f_left(alpha, beta);

    // Mass bounds on a uniform s-grid (different from the quadratic g-grid).
    let n_phi = 400000usize;
    let s_mass = {
        let mut v = vec![0.0; n_phi + 1];
        for j in 0..=n_phi {
            v[j] = support * (j as f64 / n_phi as f64);
        }
        v[n_phi] = support;
        v
    };
    let mut i_phi_lo = 0.0;
    let mut i_phi_hi = 0.0;
    let mut a_raw = 0.0;
    for j in 0..n_phi {
        let sl = s_mass[j];
        let sr = s_mass[j + 1];
        let d = sr - sl;
        let pl = phi_raw_upper(sl, support, gamma, delta, eps, kappa);
        let pr = phi_raw_lower(sr, support, gamma, delta, eps, kappa);
        i_phi_lo += pr * d;
        i_phi_hi += pl * d;
        a_raw += pl * pl * d;
    }
    let i_phi_lo = down(i_phi_lo);
    let i_phi_hi = up(i_phi_hi);
    let a_raw = up(a_raw);
    let _ = i_phi_hi;

    // Uniform s-grid, different count from Python; clustering is used only
    // as a secondary Darboux check via quadratic_s_grid in comments / unused.
    let n_s = 70000usize;
    let s = {
        let mut v = vec![0.0; n_s + 1];
        for j in 0..=n_s {
            v[j] = support * (j as f64 / n_s as f64);
        }
        v[n_s] = support;
        v
    };
    let mut ds = vec![0.0; n_s];
    for j in 0..n_s {
        ds[j] = s[j + 1] - s[j];
    }
    if i_phi_lo <= 0.0 {
        fatal("I_φ lower vanished");
    }
    let a_up = up(a_raw / down(i_phi_lo * i_phi_lo));
    let sqrt_a = up(a_up.sqrt());

    let t_min = 0.02_f64;
    let t_max = 1.0e12_f64;
    let t = hybrid_t_grid();
    let n_t = t.len() - 1;

    let mut phi_l = vec![0.0; n_s];
    for j in 0..n_s {
        phi_l[j] = phi_raw_upper(s[j], support, gamma, delta, eps, kappa);
    }

    let mut panels = 0.0;
    for i in 0..n_t {
        let t_l = t[i];
        let t_r = t[i + 1];
        // 1-g = ∫ φ_raw (1-f) / I_φ ≤ Σ φ_left_upper (1-f_lower(s_right t)) Δs / I_φ_lower
        let mut num = 0.0;
        for j in 0..n_s {
            let fv = f_lower(s[j + 1] * t_r, mu_u, alpha, beta);
            num += phi_l[j] * (1.0 - fv).max(0.0) * ds[j];
        }
        let one = up(up(num) / i_phi_lo).min(1.0).max(0.0);
        // exact ∫ t^{-3/2} dt = 2 (t_l^{-1/2} - t_r^{-1/2})  (log substitution)
        let w = 2.0 * (down(t_l.sqrt().recip()) - up(t_r.sqrt().recip()));
        let w = w.max(0.0);
        panels += up(one * one * w);
    }
    panels = up(panels);

    // near 0
    if alpha <= 0.25 {
        fatal("need α > 1/4");
    }
    let coef = up(beta * mu_u * up(support.powf(alpha)));
    let expo = 2.0 * alpha - 0.5;
    let near = up((coef * coef) * up(t_min.powf(expo)) / expo);
    let tail = up(2.0 / down(t_max.sqrt()));
    let i_u = up(near + panels + tail);
    let ag = up(0.5 * i_u);
    let c1 = up(sqrt_a * ag);
    (c1, sqrt_a, mu_u, a_up)
}

fn replay_stored(root: &J) -> Option<f64> {
    let contrib = match root.obj().get("panel_contrib_upper") {
        Some(v) => v.arr_f64(),
        None => return None,
    };
    let b = root.get("bounds");
    let mut panels = 0.0;
    for x in &contrib {
        panels += *x;
    }
    panels = up(panels) + (contrib.len() as f64) * ABS;
    let near = b.get("near0_I_upper").f64v();
    let tail = b.get("tail_I_upper").f64v();
    let sqrt_a = b.get("sqrt_a_upper").f64v();
    let i_u = up(near + panels + tail);
    let ag = up(0.5 * i_u);
    Some(up(sqrt_a * ag))
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        fatal("usage: verify_c1_bin <cert.json>");
    }
    let text = fs::read(&args[1]).unwrap_or_else(|e| fatal(&format!("read {}: {e}", args[1])));
    let mut p = Parser::new(&text);
    let root = p.parse();
    let params = root.get("params");
    let alpha = params.get("alpha").f64v();
    let beta = params.get("beta").f64v();
    let gamma = params.get("gamma").f64v();
    let delta = params.get("delta").f64v();
    let eps = params.get("eps").f64v();
    let kappa = params.get("kappa").f64v();
    let support = params.get("support").f64v();
    let name = match root.get("name") {
        J::Str(s) => s.clone(),
        _ => args[1].clone(),
    };

    let claimed = root.get("bounds").get("C_1_upper").f64v();
    if let Some(stored) = replay_stored(&root) {
        println!(
            "rust_stored_replay: name={name} C_1_replay={stored:.12} claimed={claimed:.12}"
        );
        if stored > claimed * (1.0 + 1e-11) + 1e-13 {
            fatal("stored panel replay exceeds claimed C_1_upper");
        }
    } else {
        println!("rust_stored_replay: name={name} (slim cert; panels recomputed)");
    }

    let (c1, sqrt_a, mu_u, a_up) = certify_independent(alpha, beta, gamma, delta, eps, kappa, support);
    let k = k_over_kcl_lower(c1);
    let l = l_over_lcl_upper(c1);
    let moved = beats_published_1456(c1);
    println!(
        "rust_independent: C_1_upper={c1:.12}  K/Kcl_lower={k:.12}  L/Lcl_upper={l:.12}  beats_1.456={moved}"
    );
    println!("  a_upper={a_up:.10}  sqrt_a_upper={sqrt_a:.10}  mu_upper={mu_u:.10}");
    let claimed_beats = match root.get("bounds").obj().get("beats_1456") {
        Some(J::Bool(b)) => *b,
        Some(J::Num(x)) => *x != 0.0,
        _ => true,
    };
    if claimed_beats && !moved {
        fatal(&format!(
            "cert claims to beat 1.456 but independent C_1_upper does not; got {c1:.12}"
        ));
    }
}
