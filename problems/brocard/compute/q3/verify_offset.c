#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

struct row {
    uint64_t offset;
    uint64_t prime_residue;
    uint64_t target_numerator;
    uint64_t target_denominator;
};

static uint64_t powmod(uint64_t base, uint64_t exponent, uint64_t modulus) {
    uint64_t result = 1;
    while (exponent != 0) {
        if (exponent & 1U) {
            result = (result * base) % modulus;
        }
        base = (base * base) % modulus;
        exponent >>= 1U;
    }
    return result;
}

static int is_prime(uint64_t value) {
    if (value < 2) return 0;
    if ((value & 1U) == 0) return value == 2;
    for (uint64_t divisor = 3; divisor * divisor <= value; divisor += 2) {
        if (value % divisor == 0) return 0;
    }
    return 1;
}

static uint64_t factorial_mod(uint64_t n, uint64_t modulus) {
    uint64_t result = 1;
    for (uint64_t factor = 2; factor <= n; ++factor) {
        result = (result * factor) % modulus;
    }
    return result;
}

int main(int argc, char **argv) {
    const uint64_t bound = argc == 2 ? strtoull(argv[1], NULL, 10) : 10000;
    const struct row rows[] = {{2, 3, 2, 1}, {2, 5, 2, 1},
                               {3, 3, 1, 2}, {3, 5, 1, 2}};
    if (bound < 13) return 2;

    puts("Wilson-offset Brocard certificate sample");
    printf("prime_bound=%" PRIu64 "\n", bound);
    for (size_t index = 0; index < sizeof(rows) / sizeof(rows[0]); ++index) {
        const struct row row = rows[index];
        uint64_t count = 0, first = 0, last = 0;
        for (uint64_t p = row.offset + 1; p <= bound; ++p) {
            if (p % 8 != row.prime_residue || !is_prime(p)) continue;
            const uint64_t n = p - row.offset;
            const uint64_t observed = (factorial_mod(n, p) + 1) % p;
            const uint64_t inverse = powmod(row.target_denominator, p - 2, p);
            const uint64_t expected = (row.target_numerator * inverse) % p;
            if (observed != expected || expected == 0 ||
                powmod(expected, (p - 1) / 2, p) != p - 1) {
                fprintf(stderr, "row failed at c=%" PRIu64 ", p=%" PRIu64 "\n",
                        row.offset, p);
                return 1;
            }
            if (count == 0) first = p;
            last = p;
            ++count;
        }
        printf("offset=%" PRIu64 ",prime_mod_8=%" PRIu64
               ",index_mod_8=%" PRIu64 ",count=%" PRIu64
               ",first=%" PRIu64 ",last=%" PRIu64 "\n",
               row.offset, row.prime_residue,
               (row.prime_residue + 8 - row.offset % 8) % 8,
               count, first, last);
    }
    puts("verification=PASS");
    return 0;
}
