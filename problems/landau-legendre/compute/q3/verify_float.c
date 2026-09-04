#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    const long double n = 70500000000000.0L;
    const long double delta = 4504880398387.0L / 20000000000000.0L;
    const long double previous = 901.0L / 4000.0L;
    const long double alpha = 2.0L + delta;
    const long double c = 22.0L / 25.0L;
    const long double log_n = logl(n);
    const long double x = expl((2.0L / alpha) * log_n);
    const long double a = expl((delta / alpha) * log_n);
    const long double b = (alpha - 1.0L) / 2.0L;
    const long double rhs = (44.0L / (25.0L * alpha)) * log_n;
    const long double condition5 = logl(a) - logl(rhs);
    const long double relative = b / x - 1.0L / (alpha * n * a);
    const long double taylor_overlap = condition5 + log1pl(relative);
    const long double derivative =
        delta / 2.0L * a
        - c
        - b * (1.0L - delta / 2.0L) * a / x
        + 0.5L / n;

    if (!isfinite(x) || !isfinite(a) || !isfinite(condition5)
            || !isfinite(taylor_overlap) || !isfinite(derivative)) {
        fputs("non-finite floating-point result\n", stderr);
        return EXIT_FAILURE;
    }
    if (!(delta < previous
            && x > 2.0e12L && x < 2.8e12L
            && a > 25.0L && a < 26.0L
            && condition5 < -5.0e-14L
            && taylor_overlap > 1.0e-14L
            && derivative > 1.9L)) {
        fprintf(stderr,
                "independent check failed: x=%.18Le A=%.18Le basic=%.18Le "
                "taylor=%.18Le derivative=%.18Le\n",
                x, a, condition5, taylor_overlap, derivative);
        return EXIT_FAILURE;
    }
    printf("PASS rh_delta_taylor_float x=%.18Le A=%.18Le basic=%.18Le "
           "taylor=%.18Le derivative=%.18Le\n",
           x, a, condition5, taylor_overlap, derivative);
    return EXIT_SUCCESS;
}
