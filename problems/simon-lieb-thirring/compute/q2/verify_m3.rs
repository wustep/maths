// Independent rustc-only envelope of Carvalho Corso–Ried M_3.
//
// Same Clausen series as verify_m3.py, different n_terms and a coarser
// tail. Conversion L/Lcl = (π/3) exp(3 CI_2(2π/3) / (2π)).
//
//    rustc -O -o verify_m3_bin verify_m3.rs
//    ./verify_m3_bin [certs/m3_ccr.json]

use std::env;
use std::fs;
use std::process::ExitCode;

const REL: f64 = 2.0e-14;
const ABS: f64 = 1.0e-15;
const FHJN: f64 = 1.456;
const Q1: f64 = 1.45576;
const CCR: f64 = 1.44655;
const N_TERMS: usize = 15000;

fn up(x: f64) -> f64 {
    if !x.is_finite() {
        panic!("non-finite");
    }
    (x.abs() * (1.0 + REL) + ABS) * x.signum()
}

fn down(x: f64) -> f64 {
    if !x.is_finite() || x <= 0.0 {
        return 0.0;
    }
    (x * (1.0 - REL) - ABS).max(0.0)
}

fn exp_up(x: f64) -> f64 {
    // Taylor, n = 20 (different from the Python 24).
    if x < 0.0 {
        panic!("exp_up expects x >= 0");
    }
    let n = 20;
    let mut term = 1.0;
    let mut s = 1.0;
    for k in 1..n {
        term *= x / (k as f64);
        s += term;
    }
    let rem = term * (x / (n as f64));
    if rem >= 0.5 {
        panic!("exp_up remainder too large");
    }
    up(s / (1.0 - rem))
}

fn clausen_upper() -> (f64, f64, f64) {
    // Pairwise: even m and odd m accumulated separately, then added
    // (Python uses a single Kahan sum).
    let mut even = 0.0;
    let mut odd = 0.0;
    for m in 0..N_TERMS {
        let a = (3 * m + 1) as f64;
        let b = (3 * m + 2) as f64;
        let t = 1.0 / (a * a) - 1.0 / (b * b);
        if m % 2 == 0 {
            even += t;
        } else {
            odd += t;
        }
    }
    let partial = even + odd;
    let partial_up = partial * (1.0 + REL * (N_TERMS as f64)) + ABS * (N_TERMS as f64);
    // Coarser than Python: Σ_{m≥N} 1/(9 m^3) < 1/(9) * 1/(2 (N-2)^2)
    // = 1/(18 (N-2)^2), using N-2 instead of N-1.
    let tail = 1.0 / (18.0 * ((N_TERMS - 2) as f64).powi(2));
    let sum_up = up(up(partial_up) + up(tail));
    let sqrt3_up = up(3.0_f64.sqrt());
    let ci2_up = up(sqrt3_up * 0.5 * sum_up);
    (ci2_up, partial, tail)
}

fn parse_json_f64(text: &str, key: &str) -> Option<f64> {
    let pat = format!("\"{}\"", key);
    let i = text.find(&pat)?;
    let rest = &text[i + pat.len()..];
    let rest = rest.trim_start_matches(|c: char| c == ' ' || c == ':' || c == '\n');
    let tok: String = rest
        .chars()
        .take_while(|c| c.is_ascii_digit() || *c == '.' || *c == 'e' || *c == 'E' || *c == '+' || *c == '-')
        .collect();
    tok.parse().ok()
}

fn main() -> ExitCode {
    let pi_up = up(std::f64::consts::PI);
    let pi_dn = down(std::f64::consts::PI);
    let (ci2_up, partial, tail) = clausen_upper();
    let arg_up = up((3.0 * ci2_up) / (2.0 * pi_dn));
    let e = exp_up(arg_up);
    let l_up = up((pi_up / 3.0) * e);
    let sqrt3_dn = down(3.0_f64.sqrt());
    let h3 = up(up(3.0 / (4.0 * sqrt3_dn)) * e);
    let m3_up = up((16.0 * pi_up / 81.0) * h3);
    let k_lo = down(16.0 / (243.0 * m3_up * m3_up));

    println!("=== q2 verify_m3.rs: Clausen envelope (n={}) ===", N_TERMS);
    println!("CI2_partial        = {:.15e}", (3.0_f64.sqrt()) * 0.5 * partial);
    println!("CI2_upper          = {:.15e}  tail={:.3e}", ci2_up, tail);
    println!("M3_upper           = {:.15e}", m3_up);
    println!("L/Lcl_upper        = {:.15e}", l_up);
    println!("K/Kcl_lower        = {:.15e}", k_lo);
    println!("beats FHJN 1.456   = {}", l_up < FHJN);
    println!("below q1 1.45576   = {}", l_up < Q1);
    println!("below 1.45         = {}", l_up < 1.45);
    println!("beats CCR 1.44655  = {}", l_up < CCR);

    if l_up >= FHJN {
        eprintln!("error: rust envelope missed FHJN 1.456");
        return ExitCode::from(1);
    }
    if l_up >= Q1 {
        eprintln!("error: rust envelope missed q1 1.45576");
        return ExitCode::from(1);
    }
    if l_up >= 1.45 {
        eprintln!("error: rust envelope is not below 1.45");
        return ExitCode::from(1);
    }

    if let Some(path) = env::args().nth(1) {
        let text = fs::read_to_string(&path).expect("read cert");
        let py_l = parse_json_f64(&text, "L_over_Lcl_upper").expect("L in cert");
        let py_m = parse_json_f64(&text, "M3_upper").expect("M3 in cert");
        println!("python L_upper      = {:.15e}", py_l);
        println!("python M3_upper     = {:.15e}", py_m);
        // Both must sit in (1.44655, 1.45). They need not match digitwise.
        if py_l >= 1.45 || py_l < CCR {
            eprintln!("error: python L_upper outside the expected window");
            return ExitCode::from(1);
        }
        if l_up < CCR {
            eprintln!("error: rust L_upper unexpectedly below CCR 1.44655");
            return ExitCode::from(1);
        }
    }

    println!("ok: rust Clausen envelope");
    ExitCode::SUCCESS
}
