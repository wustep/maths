#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    const long double n = 70500000000000.0L;
    const long double delta = 901.0L / 4000.0L;
    const long double published = 2253.0L / 10000.0L;
    const long double alpha = 2.0L + delta;
    const long double log_n = logl(n);
    const long double exponent = delta / alpha;
    const long double coefficient = 44.0L / (25.0L * alpha);
    const long double overlap = exponent * log_n - logl(coefficient * log_n);
    const long double monotonicity = exponent * log_n - 1.0L;

    if (!isfinite(overlap) || !isfinite(monotonicity)) {
        fputs("non-finite floating-point result\n", stderr);
        return EXIT_FAILURE;
    }
    if (!(delta < published && overlap > 0.00007L && monotonicity > 2.0L)) {
        fprintf(stderr, "independent sign check failed: %.18Le %.18Le\n",
                overlap, monotonicity);
        return EXIT_FAILURE;
    }
    printf("PASS rh_delta_float overlap=%.18Le monotonicity=%.18Le\n",
           overlap, monotonicity);
    return EXIT_SUCCESS;
}
