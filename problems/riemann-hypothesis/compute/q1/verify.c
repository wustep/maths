#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static void require(int condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        exit(1);
    }
    printf("PASS: %s\n", message);
}

int main(void) {
    const long long verified_height = 3000175332800LL;
    const long long candidate_x = 6000000185827LL;

    require(806250LL + 87677LL == 893927LL,
            "candidate rational numerator");
    require(893927LL * 5LL < 5000000LL,
            "candidate target is below 1/5");
    require(2LL * verified_height - candidate_x == 350479773LL,
            "candidate height margin numerator");

    require(3720000000LL + 279993289LL == 3999993289LL,
            "rounded Polymath row numerator");
    require(3999993289LL < 4000000000LL,
            "rounded Polymath row arithmetic is below 1/5");

    /* Independent long-double replay of the printed 2011 Lehmer data. */
    const long double xkm1 = 15908045004746.2438923212L;
    const long double xk = 15908045004746.86578030774L;
    const long double xkp1 = 15908045004746.86578988024L;
    const long double xkp2 = 15908045004747.4673564758L;
    const long double verified_t = 3293531632.415L;
    const long double delta = 0.00000957250L;
    const long double pi = acosl(-1.0L);
    const long double g =
        2.0L * logl(xkp1) / powl(xkp1 - xkp2, 2.0L)
        + 2.0L * logl(xk) / powl(xk - xkm1, 2.0L)
        + (logl(xk) + logl(xkp1)) * pi * pi / 12.0L
        + 4.0e10L / powl(xk - 2.0L * verified_t, 2.0L)
        + 4.0L;
    const long double delta_squared_g = delta * delta * g;
    const long double lambda =
        (powl(1.0L - 1.25L * delta_squared_g, 0.8L) - 1.0L)
        / (8.0L * g);

    require(g > 379.1994L && g < 379.1995L,
            "Lehmer G lies in the printed corridor");
    require(delta_squared_g < 3.47471e-8L,
            "Lehmer delta squared G is below the printed upper bound");
    require(lambda > -1.1455e-11L && lambda < -1.1453e-11L,
            "Lehmer lambda rounds to -1.14541e-11");
    printf("INFO: C replay G=%.15Lf lambda=%.15Le\n", g, lambda);
    puts("PASS riemann_hypothesis_q1_c");
    return 0;
}
