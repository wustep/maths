/*
 * Independent exact-three-sum verifier for a binary matrix.
 *
 * This program shares no code with the QM_5^3 builder.  It parses the matrix
 * text, derives the columns, checks rank and projectivity, then exhaustively
 * enumerates unordered sets of 0, 1, 2, and 3 distinct columns.  Success
 * requires every syndrome to occur as an XOR of exactly three distinct
 * columns (and hence also as a sum of two or three columns).
 *
 * Build and run from problems/covering/:
 *
 *   gcc -O3 -std=c11 -Wall -Wextra compute/verify_three_sum.c \
 *       -o compute/verify_three_sum
 *   compute/verify_three_sum compute/H_r10_n50.txt 10 50
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int redundancy;
    size_t length;
    uint32_t *columns;
} Matrix;

static void die(const char *message) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
}

static void die_path(const char *message, const char *path) {
    fprintf(stderr, "FAIL: %s %s: %s\n", message, path, strerror(errno));
    exit(1);
}

static size_t parse_row(char *line, unsigned char **bits, size_t *capacity) {
    char *cursor = line;
    size_t count = 0;
    while (*cursor != '\0') {
        while (*cursor == ' ' || *cursor == '\t' ||
               *cursor == '\r' || *cursor == '\n') {
            ++cursor;
        }
        if (*cursor == '\0' || *cursor == '#') {
            break;
        }
        if ((*cursor != '0' && *cursor != '1') ||
            (cursor[1] != '\0' && cursor[1] != '#' &&
             cursor[1] != ' ' && cursor[1] != '\t' &&
             cursor[1] != '\r' && cursor[1] != '\n')) {
            die("matrix contains a token other than 0 or 1");
        }
        if (count == *capacity) {
            size_t next = *capacity == 0 ? 1024 : 2 * *capacity;
            unsigned char *grown = realloc(*bits, next * sizeof(**bits));
            if (grown == NULL) {
                die("out of memory while parsing a matrix row");
            }
            *bits = grown;
            *capacity = next;
        }
        (*bits)[count++] = (unsigned char)(*cursor - '0');
        ++cursor;
    }
    return count;
}

static Matrix read_matrix(const char *path) {
    FILE *file = fopen(path, "r");
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t got;
    unsigned char *row_bits = NULL;
    size_t row_capacity = 0;
    Matrix matrix = {0, 0, NULL};
    if (file == NULL) {
        die_path("cannot open", path);
    }
    while ((got = getline(&line, &line_capacity, file)) >= 0) {
        char *cursor = line;
        size_t row_length;
        (void)got;
        while (*cursor == ' ' || *cursor == '\t' ||
               *cursor == '\r' || *cursor == '\n') {
            ++cursor;
        }
        if (*cursor == '\0' || *cursor == '#') {
            continue;
        }
        if (matrix.redundancy >= 31) {
            die("this verifier supports at most 30 matrix rows");
        }
        row_length = parse_row(cursor, &row_bits, &row_capacity);
        if (row_length == 0) {
            continue;
        }
        if (matrix.length == 0) {
            matrix.length = row_length;
            matrix.columns = calloc(matrix.length, sizeof(*matrix.columns));
            if (matrix.columns == NULL) {
                die("out of memory allocating columns");
            }
        } else if (row_length != matrix.length) {
            die("matrix is ragged");
        }
        for (size_t column = 0; column < matrix.length; ++column) {
            matrix.columns[column] |=
                (uint32_t)row_bits[column] << matrix.redundancy;
        }
        ++matrix.redundancy;
    }
    if (ferror(file)) {
        die_path("error reading", path);
    }
    free(line);
    free(row_bits);
    fclose(file);
    if (matrix.redundancy == 0 || matrix.length == 0) {
        die("matrix has no data rows");
    }
    return matrix;
}

static long parse_expected(const char *text, const char *name) {
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0' || value <= 0) {
        fprintf(stderr, "FAIL: invalid expected %s: %s\n", name, text);
        exit(1);
    }
    return value;
}

static int binary_rank(const uint32_t *columns, size_t length) {
    uint32_t basis[31] = {0};
    int rank = 0;
    for (size_t index = 0; index < length; ++index) {
        uint32_t value = columns[index];
        while (value != 0) {
            int pivot = 31 - __builtin_clz(value);
            if (basis[pivot] != 0) {
                value ^= basis[pivot];
            } else {
                basis[pivot] = value;
                ++rank;
                break;
            }
        }
    }
    return rank;
}

int main(int argc, char **argv) {
    Matrix matrix;
    uint64_t space;
    unsigned char *weights;
    uint64_t exact[4] = {0, 0, 0, 0};
    uint64_t union_count = 0;
    uint64_t two_or_three = 0;
    uint64_t triples = 0;
    int rank;

    if (argc != 4) {
        fprintf(stderr, "usage: %s MATRIX EXPECTED_R EXPECTED_N\n", argv[0]);
        return 2;
    }
    matrix = read_matrix(argv[1]);
    if (matrix.redundancy != parse_expected(argv[2], "redundancy") ||
        matrix.length != (size_t)parse_expected(argv[3], "length")) {
        fprintf(stderr, "FAIL: shape is %d x %zu, expected %s x %s\n",
                matrix.redundancy, matrix.length, argv[2], argv[3]);
        free(matrix.columns);
        return 1;
    }
    space = UINT64_C(1) << matrix.redundancy;
    weights = calloc((size_t)space, 1);
    if (weights == NULL) {
        die("out of memory allocating syndrome flags");
    }

    weights[0] |= 1U;
    for (size_t left = 0; left < matrix.length; ++left) {
        uint32_t a = matrix.columns[left];
        if (a == 0 || (uint64_t)a >= space) {
            die("matrix has a zero or out-of-range column");
        }
        if (weights[a] & 2U) {
            die("matrix has a repeated column");
        }
        weights[a] |= 2U;
        for (size_t middle = 0; middle < left; ++middle) {
            uint32_t ab = a ^ matrix.columns[middle];
            weights[ab] |= 4U;
            for (size_t right = 0; right < middle; ++right) {
                weights[ab ^ matrix.columns[right]] |= 8U;
                ++triples;
            }
        }
    }
    rank = binary_rank(matrix.columns, matrix.length);
    if (rank != matrix.redundancy) {
        die("matrix does not have full binary rank");
    }
    for (uint64_t syndrome = 0; syndrome < space; ++syndrome) {
        unsigned char flags = weights[syndrome];
        for (int weight = 0; weight <= 3; ++weight) {
            exact[weight] += (flags >> weight) & 1U;
        }
        union_count += flags != 0;
        two_or_three += (flags & 12U) != 0;
    }
    if (exact[3] != space || union_count != space || two_or_three != space) {
        fprintf(stderr,
                "FAIL: exact_three=%" PRIu64 "/%" PRIu64
                " union_le3=%" PRIu64 "/%" PRIu64
                " two_or_three=%" PRIu64 "/%" PRIu64 "\n",
                exact[3], space, union_count, space, two_or_three, space);
        free(weights);
        free(matrix.columns);
        return 1;
    }
    printf("PASS matrix=%s r=%d n=%zu rank=%d distinct_nonzero=%zu "
           "exact0=%" PRIu64 " exact1=%" PRIu64 " exact2=%" PRIu64
           " exact3=%" PRIu64 "/%" PRIu64 " triples=%" PRIu64
           " two_or_three=%" PRIu64 "/%" PRIu64 "\n",
           argv[1], matrix.redundancy, matrix.length, rank, matrix.length,
           exact[0], exact[1], exact[2], exact[3], space, triples,
           two_or_three, space);
    free(weights);
    free(matrix.columns);
    return 0;
}
