#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/*
 * Exact finite quadratic-residue sieve for n! + 1.
 *
 * The Python driver supplies odd primes p larger than the checked bound.  For
 * each p we build the complete bitset of square residues modulo p, update n!
 * modulo p sequentially, and remove n whenever n! + 1 is not in that bitset.
 * No floating point arithmetic or probable-residue test is used here.
 */

static inline int bit_get(const uint8_t *bits, uint64_t index) {
    return (bits[index >> 3] >> (index & 7)) & 1U;
}

static inline void bit_set(uint8_t *bits, uint64_t index) {
    bits[index >> 3] |= (uint8_t)(1U << (index & 7));
}

static inline void bit_clear(uint8_t *bits, uint64_t index) {
    bits[index >> 3] &= (uint8_t)~(1U << (index & 7));
}

static uint64_t parse_u64(const char *text, const char *label) {
    char *end = NULL;
    const uint64_t value = strtoull(text, &end, 10);
    if (text[0] == '\0' || end == NULL || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", label, text);
        exit(2);
    }
    return value;
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: %s BOUND MIN_N PRIME [PRIME ...]\n", argv[0]);
        return 2;
    }

    const uint64_t bound = parse_u64(argv[1], "bound");
    const uint64_t min_n = parse_u64(argv[2], "minimum n");
    if (min_n > bound) {
        fprintf(stderr, "minimum n exceeds bound\n");
        return 2;
    }

    const size_t alive_bytes = (size_t)((bound + 8U) >> 3);
    uint8_t *alive = calloc(alive_bytes, 1);
    if (alive == NULL) {
        fprintf(stderr, "could not allocate survivor bitset\n");
        return 3;
    }

    uint64_t survivors = bound - min_n + 1U;
    for (uint64_t n = min_n; n <= bound; ++n) {
        bit_set(alive, n);
    }
    printf("START,%" PRIu64 "\n", survivors);

    for (int argi = 3; argi < argc && survivors != 0; ++argi) {
        const uint64_t p = parse_u64(argv[argi], "prime");
        if (p <= bound || (p & 1U) == 0U) {
            fprintf(stderr, "modulus must be odd and exceed bound: %" PRIu64 "\n", p);
            free(alive);
            return 2;
        }

        const size_t residue_bytes = (size_t)((p + 7U) >> 3);
        uint8_t *is_square = calloc(residue_bytes, 1);
        if (is_square == NULL) {
            fprintf(stderr, "could not allocate residue bitset for %" PRIu64 "\n", p);
            free(alive);
            return 3;
        }

        /* (x+1)^2 = x^2 + 2x + 1.  One subtraction suffices here. */
        uint64_t square = 0;
        for (uint64_t x = 0; x <= p / 2U; ++x) {
            bit_set(is_square, square);
            const uint64_t increment = 2U * x + 1U;
            square += increment;
            if (square >= p) {
                square -= p;
            }
        }

        uint64_t factorial = 1;
        uint64_t eliminated = 0;
        for (uint64_t n = 0; n <= bound; ++n) {
            if (n != 0) {
                factorial = (factorial * n) % p;
            }
            if (!bit_get(alive, n)) {
                continue;
            }
            uint64_t target = factorial + 1U;
            if (target == p) {
                target = 0;
            }
            if (!bit_get(is_square, target)) {
                bit_clear(alive, n);
                ++eliminated;
            }
        }
        survivors -= eliminated;
        printf("PRIME,%" PRIu64 ",%" PRIu64 ",%" PRIu64 "\n", p, eliminated, survivors);
        fflush(stdout);
        free(is_square);
    }

    printf("SURVIVORS,%" PRIu64, survivors);
    uint64_t emitted = 0;
    for (uint64_t n = min_n; n <= bound && emitted < 100U; ++n) {
        if (bit_get(alive, n)) {
            printf(",%" PRIu64, n);
            ++emitted;
        }
    }
    putchar('\n');
    free(alive);
    return 0;
}
