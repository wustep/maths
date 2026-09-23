/* Independent q16 certificate. Reuses q13's matrix parser and seed sweep,
 * then separately checks GF(32) and every QM_4^3 construction column. */
#define main q13_original_main
#include "../q13/verify_q13.c"
#undef main

enum { Q16_P = 33, Q16_Q = 32, Q16_R = 41, Q16_N = 26175 };

static uint8_t q16_mul(uint8_t a, uint8_t b)
{
    uint8_t product = 0;
    while (b) {
        if (b & 1) product ^= a;
        b >>= 1;
        a <<= 1;
        if (a & Q16_Q) a ^= 0x25;
    }
    if (product >= Q16_Q) fail("GF(32) product out of range");
    return product;
}

int main(int argc, char **argv)
{
    if (argc != 4)
        fail("usage: verify_q16 seed partition output");
    uint64_t *seed = read_matrix(argv[1], SEED_R, SEED_N);
    int *labels = read_partition(argv[2], SEED_N);
    uint64_t *output = read_matrix(argv[3], Q16_R, Q16_N);
    verify_columns(seed, SEED_N, SEED_R, "seed");
    verify_columns(output, Q16_N, Q16_R, "output");
    count_blocks(labels, SEED_N, Q16_P);
    struct cover_counts coverage = verify_partition(seed, labels, "q16 33-block partition");
    for (int a = 1; a < Q16_Q; ++a) {
        int inverses = 0;
        for (int b = 1; b < Q16_Q; ++b)
            inverses += q16_mul((uint8_t)a, (uint8_t)b) == 1;
        if (inverses != 1) fail("GF(32) element %d has %d inverses", a, inverses);
    }
    size_t index = 0;
    for (uint64_t v = 1; v < Q16_Q; ++v) {
        uint64_t expected = v << (SEED_R + 5);
        if (output[index++] != expected) fail("D_3 column mismatch");
    }
    for (int h = 0; h < SEED_N; ++h) {
        int label = labels[h];
        uint8_t beta = (uint8_t)(label - 1);
        uint8_t beta2 = q16_mul(beta, beta);
        for (uint8_t xi = 0; xi < Q16_Q; ++xi) {
            uint64_t expected = label == 0
                ? seed[h] | ((uint64_t)xi << (SEED_R + 10))
                : seed[h] | ((uint64_t)xi << SEED_R)
                  | ((uint64_t)q16_mul(beta, xi) << (SEED_R + 5))
                  | ((uint64_t)q16_mul(beta2, xi) << (SEED_R + 10));
            if (output[index++] != expected)
                fail("QM_4^3 identity mismatch at seed column %d xi %u", h, xi);
        }
    }
    if (index != Q16_N || Q16_N != Q16_Q * (SEED_N + 1) - 1 ||
        Q16_R != SEED_R + 15 || SEED_N < Q16_P || Q16_P != Q16_Q + 1)
        fail("QM_4^3 parameter failure");
    if (26206 - Q16_N != 31 || 26238 - Q16_N != 63)
        fail("comparison arithmetic failure");
    if (UINT64_C(1) + Q16_N + (uint64_t)Q16_N * (Q16_N - 1) / 2 >=
        (UINT64_C(1) << Q16_R)) fail("radius-two volume check failure");
    printf("PASS seed=(%d,%d) p=%d le2=%" PRIu64 "/%u le3=%" PRIu64
           "/%u GF32=0x25 output=(%d,%d) rank=%d identities=%zu"
           " published=26238 previous=26206 improvement=63\n",
           SEED_R, SEED_N, Q16_P, coverage.through_two, 1U << SEED_R,
           coverage.through_three, 1U << SEED_R,
           Q16_R, Q16_N, Q16_R, index);
    free(seed); free(labels); free(output);
    return 0;
}
