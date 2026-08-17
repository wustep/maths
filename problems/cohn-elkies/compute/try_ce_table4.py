"""Try the Cohn–Elkies 2003 Table 4 d=2 roots with exact rationals."""

from ce_laguerre import (
    build_certificate,
    last_positive_root_numeric,
    build_G,
    qq,
    hex_R,
    center_density,
    ratio_vs_hex,
)

# Table 4, n=2: 2πr² = 7.25520; forced double roots to two decimals.
CE_T = ["2177/100", "2902/100", "5079/100", "6534/100", "9019/100"]
CE_R = "72552/10000"  # 7.2552


def main():
    print("hex R =", hex_R())
    print("CE printed R = 7.25520, dens =", center_density(qq("72552/10000")))
    print("trying exact G from Table 4 two-decimal roots")
    built = build_G(5, [qq(t) for t in CE_T])
    if built is None:
        print("G kernel empty")
        return 1
    G, a = built
    last = last_positive_root_numeric(G)
    print("last positive root of G =", last)
    print("a_odd (first few)", a[:4], "...")

    candidates = [
        "72552/10000",
        "72553/10000",
        "7256/1000",
        "726/100",
        "73/10",
        "1451/200",
        "2903/400",
        "5807/800",
        "72553/10000",
        "18139/2500",
        "363/50",
    ]
    # Also: last + epsilon if last is known
    if last is not None:
        for den in (100, 200, 500, 1000, 2000, 5000, 10000, 20000):
            num = int(last * den) + 1
            candidates.append(f"{num}/{den}")

    seen = set()
    best = None
    for Rs in candidates:
        if Rs in seen:
            continue
        seen.add(Rs)
        R = qq(Rs)
        if last is not None and float(R) < last - 1e-12:
            continue
        cert = build_certificate(5, CE_T, Rs)
        if cert is None:
            print(f"R={Rs}: build failed")
            continue
        ok = cert["signs"]["theorem32_ok"]
        print(
            f"R={Rs}={float(qq(Rs)):.8f}  dens={cert['center_density_float']:.8f}  "
            f"ratio={cert['ratio_vs_hex_float']:.8f}  ok={ok}  "
            f"hat_extra={cert['signs']['hatF_extra_positive_roots']}  "
            f"F_after={cert['signs']['F_roots_after_R']}  "
            f"div={cert['signs']['hatF_divides_tR2']}"
        )
        if ok:
            if best is None or qq(Rs) < qq(best["R"]):
                best = cert
    if best:
        print("BEST OK R", best["R"], best["center_density_float"], best["ratio_vs_hex_float"])
        return 0
    print("no certified R from Table 4 seeds")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
