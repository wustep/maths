// Independent rustc-only replay of the two closed alternative constants
// used in q3: Weidl C(1/2) (Simpson, different n) and Seiringer–Solovej
// R_1 from an Airy-series sign bracket.
//
//    rustc -O -o verify_alt_bin verify_alt.rs
//    ./verify_alt_bin

fn simpson<F: Fn(f64) -> f64>(f: F, a: f64, b: f64, n: usize) -> f64 {
    let n = if n % 2 == 0 { n } else { n + 1 };
    let h = (b - a) / (n as f64);
    let mut s = f(a) + f(b);
    for i in 1..n {
        let x = a + (i as f64) * h;
        s += if i % 2 == 1 { 4.0 * f(x) } else { 2.0 * f(x) };
    }
    s * h / 3.0
}

fn weidl_c_half() -> (f64, f64, f64) {
    let eta = 0.5_f64;
    let u0 = (2.0 / (2.0 + 3.0_f64.sqrt())).sqrt();
    let tmax = 1.0 - u0;
    // I0 via t = s^{2/eta} = s^4
    let smax = tmax.powf(eta / 2.0);
    let i0 = (2.0 / eta)
        * simpson(
            |s| {
                let t = if s <= 0.0 { 0.0 } else { s.powf(2.0 / eta) };
                (1.0 - t) * (2.0 - t).powf((eta - 1.0) / 2.0)
            },
            0.0,
            smax,
            120000,
        );
    let i1 = simpson(
        |t| (1.0 - t) * t.powf(eta / 2.0) * (2.0 - t).powf((eta - 3.0) / 2.0),
        0.0,
        tmax,
        120000,
    );
    let a = (2.0 / 3.0) * (1.0 + 2.0 / 3.0_f64.sqrt()).sqrt();
    let th = a.powf(1.0 - eta) / (1.0 - eta)
        + 0.5_f64.sqrt() * 1.5_f64.powf(eta) * (i0 + (2.0 / 3.0) * i1);
    let th12 = 2.0_f64.powf(eta) / (eta * (1.0 - eta) * (1.0 + eta));
    let m = 2.0; // min_N (1+N)^{1/2}(1+1/N)^{1/2} at N=1
    let den = (eta.powf(eta) * (1.0 - eta).powf(1.0 - eta)).sqrt();
    let c = (th12 / th) * m / den;
    (c, i0, i1)
}

fn gamma_one_third() -> f64 {
    // Γ(1/3) ≈ 2.678938534707748
    2.678938534707748
}

fn gamma_two_thirds() -> f64 {
    // Γ(2/3) ≈ 1.3541179394264005
    1.3541179394264005
}

fn ai_series(z: f64) -> f64 {
    let c1 = 3.0_f64.powf(-2.0 / 3.0) / gamma_two_thirds();
    let c2 = 3.0_f64.powf(-1.0 / 3.0) / gamma_one_third();
    let z3 = z * z * z;
    let mut fk = 1.0;
    let mut gk = z;
    let mut f = fk;
    let mut g = gk;
    for k in 0..36 {
        fk *= z3 / (((3 * k + 2) as f64) * ((3 * k + 3) as f64));
        gk *= z3 / (((3 * k + 3) as f64) * ((3 * k + 4) as f64));
        f += fk;
        g += gk;
    }
    c1 * f - c2 * g
}

fn main() {
    let (c, i0, i1) = weidl_c_half();
    let l_half: f64 = 0.5;
    let eta: f64 = 0.5;
    let three_over_16: f64 = 3.0 / 16.0;
    let l_ss = c * l_half.powf(1.0 - eta) * three_over_16.powf(eta);
    let lcl = 2.0 / (3.0 * std::f64::consts::PI);
    let weidl_ratio = l_ss / lcl;

    // Wider than the Python 1e-10 bracket so a few ulp of Γ(1/3) cannot
    // flip the sign. |a| still sits in (2.3380, 2.3382), hence R_1 ~ 0.132.
    let lo = -2.3382;
    let hi = -2.3380;
    let ai_lo = ai_series(lo);
    let ai_hi = ai_series(hi);
    assert!(ai_lo < 0.0 && ai_hi > 0.0, "Airy bracket failed");
    let r1 = (3.0 / (-lo)).powi(3) / 16.0; // smaller |a| → larger R_1
    let ss_ratio = 1.0 / r1.sqrt();

    println!("=== q3 verify_alt.rs ===");
    println!("Weidl C(1/2)     = {:.8}", c);
    println!("Weidl I0,I1      = {:.8}, {:.8}", i0, i1);
    println!("Weidl L/Lcl      = {:.8}", weidl_ratio);
    println!("Ai(lo), Ai(hi)   = {:.3e}, {:.3e}", ai_lo, ai_hi);
    println!("SS R1 (best a)   = {:.8}", r1);
    println!("SS L/Lcl         = {:.8}", ss_ratio);
    println!("beats CCR 1.44655 (Weidl) = {}", weidl_ratio < 1.44655);
    println!("beats CCR 1.44655 (SS)    = {}", ss_ratio < 1.44655);

    if weidl_ratio < 1.44655 {
        eprintln!("error: Weidl interpolation unexpectedly below CCR");
        std::process::exit(1);
    }
    if ss_ratio < 1.44655 {
        eprintln!("error: SS R_1 unexpectedly below CCR");
        std::process::exit(1);
    }
    if c < 2.0 || c > 4.0 {
        eprintln!("error: Weidl C(1/2) outside the expected window");
        std::process::exit(1);
    }
    if !(0.12..0.14).contains(&r1) {
        eprintln!("error: R_1 outside the expected window");
        std::process::exit(1);
    }
    println!("ok: alternative-method envelopes sit above CCR");
}
