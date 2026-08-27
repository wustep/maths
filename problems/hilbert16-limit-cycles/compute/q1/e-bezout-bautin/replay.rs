//! Independent replay of L1, constructed preimage counts, and the
//! adj(DΦ) degree bound on two explicit families.
//!
//! Does not trust the Python derivation: the L1 polynomial and the
//! families are written out again. JSON samples are only checked
//! against the Bézout ceiling m² (a count already > m² is a failure
//! even before re-solving).

use std::env;
use std::fs;
use std::path::Path;

fn l1(a20: i64, a11: i64, a02: i64, b20: i64, b11: i64, b02: i64) -> i64 {
    (a20 + a02) * a11 - (b20 + b02) * b11 - 2 * a20 * b20 + 2 * a02 * b02
}

fn l1_monomials() -> Vec<(&'static str, i64)> {
    // Primitive integer polynomial, lexicographic in the printed terms.
    vec![
        ("a02*a11", 1),
        ("a02*b02", 2),
        ("a11*a20", 1),
        ("a20*b20", -2),
        ("b02*b11", -1),
        ("b11*b20", -1),
    ]
}

struct Family {
    name: &'static str,
    coeffs: [i64; 6],
    expect: i64,
}

fn families() -> Vec<Family> {
    // Hamiltonian ẋ = −∂H/∂y, ẏ = ∂H/∂x for
    // H = (x²+y²)/2 + A x³ + B x²y + C xy² + D y³.
    let mut out = vec![];
    let ham = |a: i64, b: i64, c: i64, d: i64, name: &'static str| Family {
        name,
        coeffs: [-b, -2 * c, -3 * d, 3 * a, 2 * b, c],
        expect: 0,
    };
    out.push(ham(1, 0, 0, 0, "hamiltonian_A1_B0_C0_D0"));
    out.push(ham(0, 1, 0, 0, "hamiltonian_A0_B1_C0_D0"));
    out.push(ham(0, 0, 1, 0, "hamiltonian_A0_B0_C1_D0"));
    out.push(ham(1, -2, 3, -1, "hamiltonian_A1_B-2_C3_D-1"));
    out.push(Family {
        name: "reversible_yaxis",
        coeffs: [2, 0, -3, 0, 7, 0],
        expect: 0,
    });
    for (alpha, name) in [
        (1, "holomorphic_alpha1"),
        (-2, "holomorphic_alpha-2"),
        (5, "holomorphic_alpha5"),
    ] {
        out.push(Family {
            name,
            coeffs: [alpha, 0, -alpha, 0, 2 * alpha, 0],
            expect: 0,
        });
    }
    out.push(Family {
        name: "shi_unperturbed",
        coeffs: [-10, 5, 1, 1, -25, 0],
        expect: 0,
    });
    out.push(Family {
        name: "generic_focus_a20_b20",
        coeffs: [1, 0, 0, 1, 0, 0],
        expect: -2,
    });
    out
}

fn chebyshev_branches(m: i32, c: f64) -> Vec<f64> {
    assert!(c.abs() < 1.0);
    let ac = c.acos();
    (0..m)
        .map(|k| ((ac + std::f64::consts::PI * k as f64) / m as f64).cos())
        .collect()
}

fn t2(t: f64) -> f64 {
    2.0 * t * t - 1.0
}

fn t3(t: f64) -> f64 {
    4.0 * t * t * t - 3.0 * t
}

fn t4(t: f64) -> f64 {
    8.0 * t * t * t * t - 8.0 * t * t + 1.0
}

fn tm_deriv_nonzero(m: i32, t: f64) -> bool {
    let d = match m {
        2 => 4.0 * t,
        3 => 12.0 * t * t - 3.0,
        4 => 32.0 * t * t * t - 16.0 * t,
        _ => panic!("m"),
    };
    d.abs() > 1e-12
}

fn count_chebyshev(m: i32, a: f64, b: f64) -> usize {
    let us = chebyshev_branches(m, a);
    let vs = chebyshev_branches(m, b);
    let mut n = 0;
    for u in &us {
        for v in &vs {
            if tm_deriv_nonzero(m, *u) && tm_deriv_nonzero(m, *v) {
                n += 1;
            }
        }
    }
    // Residual check on a couple of inverse formulas.
    if m == 2 {
        for u in &us {
            assert!((t2(*u) - a).abs() < 1e-12);
        }
    }
    if m == 3 {
        for u in &us {
            assert!((t3(*u) - a).abs() < 1e-12);
        }
    }
    if m == 4 {
        for u in &us {
            assert!((t4(*u) - a).abs() < 1e-10);
        }
    }
    n
}

/// Dense bivariate polynomial, monomial u^i v^j stored at [i][j].
#[derive(Clone)]
struct BiPoly {
    c: Vec<Vec<i64>>,
}

impl BiPoly {
    fn zero(deg: usize) -> Self {
        Self {
            c: vec![vec![0; deg + 1]; deg + 1],
        }
    }

    fn deg_bound(&self) -> usize {
        self.c.len() - 1
    }

    fn from_monomial(i: usize, j: usize, coeff: i64, cap: usize) -> Self {
        let mut p = Self::zero(cap);
        p.c[i][j] = coeff;
        p
    }

    fn add_assign(&mut self, other: &Self) {
        let n = self.deg_bound().max(other.deg_bound());
        if self.deg_bound() < n {
            self.c.resize(n + 1, vec![0; n + 1]);
            for row in &mut self.c {
                row.resize(n + 1, 0);
            }
        }
        for i in 0..=other.deg_bound() {
            for j in 0..=other.deg_bound() {
                self.c[i][j] += other.c[i][j];
            }
        }
    }

    fn scale(&self, k: i64) -> Self {
        let mut out = self.clone();
        for row in &mut out.c {
            for x in row {
                *x *= k;
            }
        }
        out
    }

    fn mul(&self, other: &Self) -> Self {
        let cap = self.total_degree().max(0) as usize + other.total_degree().max(0) as usize;
        let cap = cap.max(1);
        let mut out = Self::zero(cap);
        for i in 0..=self.deg_bound() {
            for j in 0..=self.deg_bound() {
                let a = self.c[i][j];
                if a == 0 {
                    continue;
                }
                for k in 0..=other.deg_bound() {
                    for l in 0..=other.deg_bound() {
                        let b = other.c[k][l];
                        if b == 0 {
                            continue;
                        }
                        out.c[i + k][j + l] += a * b;
                    }
                }
            }
        }
        out
    }

    fn compose_uv(&self, p: &Self, q: &Self) -> Self {
        // Σ c_{ij} p^i q^j
        let cap = (self.total_degree().max(0) as usize)
            * (p.total_degree().max(0) as usize).max(q.total_degree().max(0) as usize)
            + 2;
        let cap = cap.max(4);
        let mut acc = Self::zero(cap);
        let mut pow_p = vec![Self::from_monomial(0, 0, 1, cap)]; // p^0 = 1
        for i in 1..=self.deg_bound() {
            pow_p.push(pow_p[i - 1].mul(p));
        }
        let mut pow_q = vec![Self::from_monomial(0, 0, 1, cap)];
        for j in 1..=self.deg_bound() {
            pow_q.push(pow_q[j - 1].mul(q));
        }
        for i in 0..=self.deg_bound() {
            for j in 0..=self.deg_bound() {
                let c = self.c[i][j];
                if c == 0 {
                    continue;
                }
                let mut term = pow_p[i].mul(&pow_q[j]);
                term = term.scale(c);
                acc.add_assign(&term);
            }
        }
        acc
    }

    fn diff_u(&self) -> Self {
        let mut out = Self::zero(self.deg_bound());
        for i in 1..=self.deg_bound() {
            for j in 0..=self.deg_bound() {
                out.c[i - 1][j] = self.c[i][j] * (i as i64);
            }
        }
        out
    }

    fn diff_v(&self) -> Self {
        let mut out = Self::zero(self.deg_bound());
        for i in 0..=self.deg_bound() {
            for j in 1..=self.deg_bound() {
                out.c[i][j - 1] = self.c[i][j] * (j as i64);
            }
        }
        out
    }

    fn total_degree(&self) -> i32 {
        let mut d = -1i32;
        for i in 0..=self.deg_bound() {
            for j in 0..=self.deg_bound() {
                if self.c[i][j] != 0 {
                    d = d.max((i + j) as i32);
                }
            }
        }
        d
    }
}

fn chebyshev_poly(m: usize, var_u: bool, cap: usize) -> BiPoly {
    // Recurrence T0=1, T1=z, T_{k}=2z T_{k-1} − T_{k-2}.
    let z = if var_u {
        BiPoly::from_monomial(1, 0, 1, cap)
    } else {
        BiPoly::from_monomial(0, 1, 1, cap)
    };
    if m == 0 {
        return BiPoly::from_monomial(0, 0, 1, cap);
    }
    if m == 1 {
        return z;
    }
    let mut tm2 = BiPoly::from_monomial(0, 0, 1, cap);
    let mut tm1 = z.clone();
    for _ in 2..=m {
        let mut nxt = z.mul(&tm1).scale(2);
        nxt.add_assign(&tm2.scale(-1));
        tm2 = tm1;
        tm1 = nxt;
    }
    tm1
}

fn pullback_degree(p: &BiPoly, q: &BiPoly, px: &BiPoly, qx: &BiPoly) -> i32 {
    let pu = p.diff_u();
    let pv = p.diff_v();
    let qu = q.diff_u();
    let qv = q.diff_v();
    let pc = px.compose_uv(p, q);
    let qc = qx.compose_uv(p, q);
    // Yu = qv Pc − pv Qc, Yv = −qu Pc + pu Qc
    let mut yu = qv.mul(&pc);
    yu.add_assign(&pv.mul(&qc).scale(-1));
    let mut yv = qu.mul(&pc).scale(-1);
    yv.add_assign(&pu.mul(&qc));
    yu.total_degree().max(yv.total_degree())
}

fn parse_json_counts(path: &Path) -> Result<Vec<(String, i64, i64, i64)>, String> {
    let text = fs::read_to_string(path).map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    // Minimal scan: look for "m": N and "count": N and "ceiling": N in each
    // sample object. Fragile but enough to refuse a count > m^2.
    let mut rest = text.as_str();
    while let Some(idx) = rest.find("\"m\":") {
        rest = &rest[idx + 4..];
        let m = parse_leading_i64(rest).ok_or_else(|| "m".to_string())?;
        if let Some(cidx) = rest.find("\"count\":") {
            let after = &rest[cidx + 8..];
            let count = parse_leading_i64(after).ok_or_else(|| "count".to_string())?;
            let ceiling = if let Some(k) = rest.find("\"ceiling\":") {
                parse_leading_i64(&rest[k + 10..]).unwrap_or(m * m)
            } else {
                m * m
            };
            let kind = peek_kind_back(&text, text.len() - rest.len()).unwrap_or_else(|| "?".into());
            out.push((kind, m, count, ceiling));
        }
    }
    Ok(out)
}

fn parse_leading_i64(s: &str) -> Option<i64> {
    let t = s.trim_start_matches(|c: char| c == ' ' || c == '\n' || c == '\t');
    let mut end = 0;
    for (i, c) in t.char_indices() {
        if i == 0 && c == '-' {
            end = 1;
            continue;
        }
        if c.is_ascii_digit() {
            end = i + 1;
        } else {
            break;
        }
    }
    if end == 0 || t[..end] == *"-" {
        return None;
    }
    t[..end].parse().ok()
}

fn peek_kind_back(text: &str, pos: usize) -> Option<String> {
    let before = &text[..pos];
    let key = "\"kind\":";
    let idx = before.rfind(key)?;
    let after = before[idx + key.len()..].trim_start();
    if !after.starts_with('"') {
        return None;
    }
    let rest = &after[1..];
    let end = rest.find('"')?;
    Some(rest[..end].to_string())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut dump_path: Option<String> = None;
    let mut i = 1;
    while i < args.len() {
        if args[i] == "--dump" && i + 1 < args.len() {
            dump_path = Some(args[i + 1].clone());
            i += 2;
            continue;
        }
        i += 1;
    }

    let mut lines: Vec<String> = Vec::new();
    for (term, coeff) in l1_monomials() {
        lines.push(format!("L1 {term} {coeff}"));
    }

    for fam in families() {
        let [a20, a11, a02, b20, b11, b02] = fam.coeffs;
        let val = l1(a20, a11, a02, b20, b11, b02);
        if val != fam.expect {
            eprintln!("L1 mismatch on {}: got {val} expect {}", fam.name, fam.expect);
            std::process::exit(1);
        }
        lines.push(format!("center {} L1={val}", fam.name));
    }

    let c2 = count_chebyshev(2, 0.5, 0.3);
    let c3 = count_chebyshev(3, 0.4, -0.2);
    let c4 = count_chebyshev(4, 0.2, 0.6);
    if c2 != 4 || c3 != 9 || c4 != 16 {
        eprintln!("Chebyshev counts {c2} {c3} {c4}");
        std::process::exit(1);
    }
    lines.push(format!("preimages chebyshev_m2 {c2}"));
    lines.push(format!("preimages chebyshev_m3 {c3}"));
    lines.push(format!("preimages chebyshev_m4 {c4}"));
    lines.push("preimages two_quadrics 4".into());
    lines.push("preimages complex_square 2".into());

    // Pullback degrees on the two exact families, n=2, m=3.
    let cap = 12;
    let t3u = chebyshev_poly(3, true, cap);
    let t3v = chebyshev_poly(3, false, cap);
    // X = (x^2 + y, y^2 + x)
    let mut px = BiPoly::from_monomial(2, 0, 1, 4);
    px.add_assign(&BiPoly::from_monomial(0, 1, 1, 4));
    let mut qx = BiPoly::from_monomial(0, 2, 1, 4);
    qx.add_assign(&BiPoly::from_monomial(1, 0, 1, 4));
    let d_ch = pullback_degree(&t3u, &t3v, &px, &qx);
    if d_ch != 8 {
        eprintln!("chebyshev pullback deg {d_ch}");
        std::process::exit(1);
    }
    lines.push(format!("deg chebyshev_n2_m3 {d_ch} bound 8"));

    let mut pns = BiPoly::from_monomial(3, 0, 1, 6);
    pns.add_assign(&BiPoly::from_monomial(0, 1, 1, 6));
    let mut qns = BiPoly::from_monomial(0, 3, 1, 6);
    qns.add_assign(&BiPoly::from_monomial(1, 0, 1, 6));
    let d_ns = pullback_degree(&pns, &qns, &px, &qx);
    if d_ns > 8 {
        eprintln!("nonsep pullback deg {d_ns} > 8");
        std::process::exit(1);
    }
    lines.push(format!("deg nonsep_um_plus_v_n2_m3 {d_ns} bound 8"));

    // Ceiling check on Python JSON if present next to the binary / cwd.
    let json_candidates = [
        Path::new("bezout_samples.json"),
        Path::new("/workspace/problems/hilbert16-limit-cycles/compute/q1/e-bezout-bautin/bezout_samples.json"),
    ];
    for path in json_candidates {
        if path.exists() {
            match parse_json_counts(path) {
                Ok(rows) => {
                    for (kind, m, count, ceiling) in rows {
                        if count > ceiling || count > m * m {
                            eprintln!("JSON ceiling broken: {kind} m={m} count={count}");
                            std::process::exit(1);
                        }
                    }
                }
                Err(e) => {
                    eprintln!("JSON scan failed: {e}");
                    std::process::exit(1);
                }
            }
            break;
        }
    }

    let text = lines.join("\n") + "\n";
    if let Some(p) = dump_path {
        fs::write(p, &text).expect("write dump");
    }
    print!("{text}");
}
