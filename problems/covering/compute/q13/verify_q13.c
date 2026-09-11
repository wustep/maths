#define _POSIX_C_SOURCE 200809L

/*
 * Independent q13 verifier for ell_2(44,3) <= 52351.
 *
 * This program shares no code with build_qm43.py.  It uses one 8 MiB bitset
 * to exhaust all 2^26 syndromes under the 34-block seed partition, repeats
 * the sweep for its 65-block refinement, checks that the latter really is a
 * refinement, verifies GF(64), and compares all 52,351 output columns with
 * Construction QM_4^3.  It deliberately does not allocate or sweep 2^44.
 */

#include <errno.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    SEED_R = 26,
    SEED_N = 817,
    COARSE_P = 34,
    REFINED_P = 65,
    FIELD_M = 6,
    FIELD_SIZE = 64,
    OUTPUT_R = 44,
    OUTPUT_N = 52351,
    PUBLISHED_N = 52415
};

struct cover_counts {
    uint64_t through_two;
    uint64_t through_three;
};

static void fail(const char *format, ...)
{
    va_list arguments;
    va_start(arguments, format);
    fputs("FAIL: ", stderr);
    vfprintf(stderr, format, arguments);
    fputc('\n', stderr);
    va_end(arguments);
    exit(EXIT_FAILURE);
}

static uint64_t *read_matrix(
    const char *path, size_t expected_rows, size_t expected_columns)
{
    FILE *handle = fopen(path, "r");
    if (handle == NULL)
        fail("cannot open matrix %s: %s", path, strerror(errno));

    uint64_t *columns = calloc(expected_columns, sizeof(*columns));
    if (columns == NULL)
        fail("cannot allocate columns for %s", path);

    char *line = NULL;
    size_t capacity = 0;
    size_t row = 0;
    while (getline(&line, &capacity, handle) >= 0) {
        char *comment = strchr(line, '#');
        if (comment != NULL)
            *comment = '\0';

        char *save = NULL;
        char *token = strtok_r(line, " \t\r\n", &save);
        if (token == NULL)
            continue;
        if (row >= expected_rows)
            fail("%s has more than %zu non-comment rows", path, expected_rows);

        size_t column = 0;
        do {
            if (column >= expected_columns)
                fail("%s row %zu has more than %zu entries",
                     path, row, expected_columns);
            if (strcmp(token, "0") != 0 && strcmp(token, "1") != 0)
                fail("%s row %zu column %zu is not binary: %s",
                     path, row, column, token);
            if (token[0] == '1')
                columns[column] |= UINT64_C(1) << row;
            ++column;
            token = strtok_r(NULL, " \t\r\n", &save);
        } while (token != NULL);
        if (column != expected_columns)
            fail("%s row %zu has %zu entries, expected %zu",
                 path, row, column, expected_columns);
        ++row;
    }
    free(line);
    if (ferror(handle))
        fail("error reading matrix %s", path);
    if (fclose(handle) != 0)
        fail("error closing matrix %s", path);
    if (row != expected_rows)
        fail("%s has %zu rows, expected %zu", path, row, expected_rows);
    return columns;
}

static int *read_partition(const char *path, size_t expected_length)
{
    FILE *handle = fopen(path, "r");
    if (handle == NULL)
        fail("cannot open partition %s: %s", path, strerror(errno));
    int *labels = malloc(expected_length * sizeof(*labels));
    if (labels == NULL)
        fail("cannot allocate labels for %s", path);

    char *line = NULL;
    size_t capacity = 0;
    size_t count = 0;
    while (getline(&line, &capacity, handle) >= 0) {
        char *comment = strchr(line, '#');
        if (comment != NULL)
            *comment = '\0';
        char *save = NULL;
        for (char *token = strtok_r(line, " \t\r\n", &save);
             token != NULL;
             token = strtok_r(NULL, " \t\r\n", &save)) {
            if (count >= expected_length)
                fail("%s has more than %zu labels", path, expected_length);
            char *end = NULL;
            errno = 0;
            long value = strtol(token, &end, 10);
            if (errno != 0 || end == token || *end != '\0' || value < 0 ||
                value > 1000000)
                fail("%s contains invalid label %s", path, token);
            labels[count++] = (int)value;
        }
    }
    free(line);
    if (ferror(handle))
        fail("error reading partition %s", path);
    if (fclose(handle) != 0)
        fail("error closing partition %s", path);
    if (count != expected_length)
        fail("%s has %zu labels, expected %zu", path, count, expected_length);
    return labels;
}

static int count_blocks(const int *labels, size_t length, int expected)
{
    unsigned char *seen = calloc((size_t)expected, 1);
    if (seen == NULL)
        fail("cannot allocate block census");
    for (size_t index = 0; index < length; ++index) {
        if (labels[index] < 0 || labels[index] >= expected)
            fail("partition label %d outside 0..%d", labels[index], expected - 1);
        seen[labels[index]] = 1;
    }
    for (int block = 0; block < expected; ++block)
        if (!seen[block])
            fail("partition block %d is empty", block);
    free(seen);
    return expected;
}

static int highest_bit(uint64_t value)
{
    int bit = -1;
    while (value != 0) {
        value >>= 1;
        ++bit;
    }
    return bit;
}

static int binary_rank(const uint64_t *columns, size_t length)
{
    uint64_t basis[64] = {0};
    int rank = 0;
    for (size_t index = 0; index < length; ++index) {
        uint64_t value = columns[index];
        while (value != 0) {
            int pivot = highest_bit(value);
            if (basis[pivot] != 0)
                value ^= basis[pivot];
            else {
                basis[pivot] = value;
                ++rank;
                break;
            }
        }
    }
    return rank;
}

static int compare_u64(const void *left, const void *right)
{
    uint64_t a = *(const uint64_t *)left;
    uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static void verify_columns(
    const uint64_t *columns, size_t length, int redundancy, const char *name)
{
    uint64_t limit = UINT64_C(1) << redundancy;
    for (size_t index = 0; index < length; ++index)
        if (columns[index] == 0 || columns[index] >= limit)
            fail("%s column %zu is zero or outside F_2^%d", name, index, redundancy);
    if (binary_rank(columns, length) != redundancy)
        fail("%s has rank %d, expected %d",
             name, binary_rank(columns, length), redundancy);

    uint64_t *sorted = malloc(length * sizeof(*sorted));
    if (sorted == NULL)
        fail("cannot allocate duplicate check for %s", name);
    memcpy(sorted, columns, length * sizeof(*sorted));
    qsort(sorted, length, sizeof(*sorted), compare_u64);
    for (size_t index = 1; index < length; ++index)
        if (sorted[index] == sorted[index - 1])
            fail("%s repeats column value %" PRIu64, name, sorted[index]);
    free(sorted);
}

static inline void mark(uint64_t *bits, uint32_t value)
{
    bits[value >> 6] |= UINT64_C(1) << (value & 63U);
}

static uint64_t count_marked(const uint64_t *bits, size_t words)
{
    uint64_t count = 0;
    for (size_t index = 0; index < words; ++index)
        count += (uint64_t)__builtin_popcountll(bits[index]);
    return count;
}

static struct cover_counts verify_partition(
    const uint64_t *columns, const int *labels, const char *name)
{
    const uint32_t space = UINT32_C(1) << SEED_R;
    const size_t words = (size_t)space / 64;
    uint64_t *covered = calloc(words, sizeof(*covered));
    if (covered == NULL)
        fail("cannot allocate the 8 MiB syndrome bitset for %s", name);

    mark(covered, 0);
    for (size_t left = 0; left < SEED_N; ++left) {
        mark(covered, (uint32_t)columns[left]);
        for (size_t right = 0; right < left; ++right) {
            if (labels[left] != labels[right])
                mark(covered, (uint32_t)(columns[left] ^ columns[right]));
        }
    }
    struct cover_counts counts;
    counts.through_two = count_marked(covered, words);

    for (size_t left = 0; left < SEED_N; ++left) {
        for (size_t middle = 0; middle < left; ++middle) {
            if (labels[left] == labels[middle])
                continue;
            uint64_t pair = columns[left] ^ columns[middle];
            for (size_t right = 0; right < middle; ++right) {
                if (labels[right] == labels[left] ||
                    labels[right] == labels[middle])
                    continue;
                mark(covered, (uint32_t)(pair ^ columns[right]));
            }
        }
    }
    counts.through_three = count_marked(covered, words);
    free(covered);

    if (counts.through_two >= space)
        fail("%s unexpectedly has covering radius at most two", name);
    if (counts.through_three != space)
        fail("%s covers only %" PRIu64 "/%" PRIu32 " syndromes",
             name, counts.through_three, space);
    return counts;
}

static void verify_refinement(const int *coarse, const int *refined)
{
    int parent[REFINED_P];
    for (int block = 0; block < REFINED_P; ++block)
        parent[block] = -1;
    for (size_t index = 0; index < SEED_N; ++index) {
        int child = refined[index];
        if (parent[child] == -1)
            parent[child] = coarse[index];
        else if (parent[child] != coarse[index])
            fail("refined block %d crosses coarse blocks %d and %d",
                 child, parent[child], coarse[index]);
    }
}

static uint8_t gf_multiply(uint8_t left, uint8_t right)
{
    const uint16_t modulus = UINT16_C(0x43); /* x^6 + x + 1 */
    uint16_t a = left;
    uint16_t product = 0;
    while (right != 0) {
        if (right & 1U)
            product ^= a;
        right >>= 1;
        a <<= 1;
        if (a & FIELD_SIZE)
            a ^= modulus;
    }
    if (product >= FIELD_SIZE)
        fail("GF(64) multiplication escaped the field");
    return (uint8_t)product;
}

static void verify_field(void)
{
    for (int value = 0; value < FIELD_SIZE; ++value) {
        if (gf_multiply((uint8_t)value, 0) != 0 ||
            gf_multiply((uint8_t)value, 1) != value)
            fail("GF(64) identity failed at %d", value);
    }
    for (int left = 1; left < FIELD_SIZE; ++left) {
        int inverses = 0;
        for (int right = 1; right < FIELD_SIZE; ++right)
            inverses += gf_multiply((uint8_t)left, (uint8_t)right) == 1;
        if (inverses != 1)
            fail("GF(64) element %d has %d inverses", left, inverses);
    }
}

static void expect_column(
    const uint64_t *output, size_t index, uint64_t expected, const char *part)
{
    if (index >= OUTPUT_N)
        fail("output ended before %s column %zu", part, index);
    if (output[index] != expected)
        fail("output column %zu fails %s: got %" PRIu64 ", expected %" PRIu64,
             index, part, output[index], expected);
}

static void verify_construction_identity(
    const uint64_t *seed, const int *refined, const uint64_t *output)
{
    const unsigned shift_u1 = SEED_R;
    const unsigned shift_u2 = SEED_R + FIELD_M;
    const unsigned shift_u3 = SEED_R + 2 * FIELD_M;
    size_t index = 0;

    /* D_3 = (0_{r0+m}, W_m, 0_m). */
    for (uint64_t value = 1; value < FIELD_SIZE; ++value)
        expect_column(output, index++, value << shift_u2, "D_3");

    for (size_t seed_index = 0; seed_index < SEED_N; ++seed_index) {
        int label = refined[seed_index];
        if (label == 0) { /* star */
            for (uint64_t xi = 0; xi < FIELD_SIZE; ++xi)
                expect_column(
                    output, index++, seed[seed_index] | (xi << shift_u3),
                    "A(h,star)");
        } else {
            uint8_t beta = (uint8_t)(label - 1);
            uint8_t beta_squared = gf_multiply(beta, beta);
            for (uint8_t xi = 0; xi < FIELD_SIZE; ++xi) {
                uint64_t expected = seed[seed_index]
                    | ((uint64_t)xi << shift_u1)
                    | ((uint64_t)gf_multiply(beta, xi) << shift_u2)
                    | ((uint64_t)gf_multiply(beta_squared, xi) << shift_u3);
                expect_column(output, index++, expected, "A(h,beta)");
            }
        }
    }
    if (index != OUTPUT_N)
        fail("construction consumed %zu columns, expected %d", index, OUTPUT_N);
}

int main(int argc, char **argv)
{
    if (argc != 5) {
        fprintf(stderr,
                "usage: %s SEED_MATRIX COARSE_PARTITION REFINED_PARTITION OUTPUT_MATRIX\n",
                argv[0]);
        return EXIT_FAILURE;
    }

    uint64_t *seed = read_matrix(argv[1], SEED_R, SEED_N);
    int *coarse = read_partition(argv[2], SEED_N);
    int *refined = read_partition(argv[3], SEED_N);
    uint64_t *output = read_matrix(argv[4], OUTPUT_R, OUTPUT_N);

    verify_columns(seed, SEED_N, SEED_R, "seed");
    verify_columns(output, OUTPUT_N, OUTPUT_R, "output");
    count_blocks(coarse, SEED_N, COARSE_P);
    count_blocks(refined, SEED_N, REFINED_P);
    verify_refinement(coarse, refined);

    struct cover_counts coarse_counts =
        verify_partition(seed, coarse, "34-block seed partition");
    struct cover_counts refined_counts =
        verify_partition(seed, refined, "65-block seed partition");

    verify_field();
    verify_construction_identity(seed, refined, output);

    if (SEED_N < REFINED_P || REFINED_P != FIELD_SIZE + 1)
        fail("QM_4^3 indicator hypothesis failed");
    if (OUTPUT_N != FIELD_SIZE * (SEED_N + 1) - 1 ||
        OUTPUT_R != SEED_R + 3 * FIELD_M)
        fail("QM_4^3 parameter identity failed");
    if (PUBLISHED_N - OUTPUT_N != 64)
        fail("published comparison failed");
    uint64_t radius_two_volume =
        UINT64_C(1) + OUTPUT_N + (uint64_t)OUTPUT_N * (OUTPUT_N - 1) / 2;
    if (radius_two_volume >= (UINT64_C(1) << OUTPUT_R))
        fail("radius-two volume control unexpectedly failed");

    printf(
        "PASS seed_r=%d seed_n=%d rank=%d coarse_p=%d "
        "coarse_le2=%" PRIu64 "/%u coarse_le3=%" PRIu64 "/%u "
        "refined_p=%d refined_le2=%" PRIu64 "/%u "
        "refined_le3=%" PRIu64 "/%u refinement=yes "
        "GF64_modulus=0x43 indicators=65 output_r=%d output_n=%d "
        "output_rank=%d distinct_nonzero=%d identity_columns=%d "
        "coverage=THEOREM_6_1 published=%d improvement=%d peak_bitmap_bytes=%u\n",
        SEED_R, SEED_N, SEED_R, COARSE_P,
        coarse_counts.through_two, 1U << SEED_R,
        coarse_counts.through_three, 1U << SEED_R,
        REFINED_P,
        refined_counts.through_two, 1U << SEED_R,
        refined_counts.through_three, 1U << SEED_R,
        OUTPUT_R, OUTPUT_N, OUTPUT_R, OUTPUT_N, OUTPUT_N,
        PUBLISHED_N, PUBLISHED_N - OUTPUT_N, (1U << SEED_R) / 8);

    free(output);
    free(refined);
    free(coarse);
    free(seed);
    return EXIT_SUCCESS;
}
