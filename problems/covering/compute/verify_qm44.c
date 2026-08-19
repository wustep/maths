/*
 * Independent blockwise verifier for the r=31, n=689 QM_4^4 matrix.
 *
 * A flat radius-4 sweep would require 2^31 syndrome marks and about
 * C(689,4) XORs.  Instead this program verifies the complete constructive
 * proof from Theorem 9.1:
 *
 *   - all 2^11 top syndromes have a certified nonempty OK2 representation
 *     using 1..4 distinct singleton blocks;
 *   - the r=10 constituent covers all 2^10 syndromes with at most 2 columns;
 *   - W_5 contains every nonzero 5-bit column;
 *   - every finite-field coefficient map used in the four top-weight cases
 *     is invertible; and
 *   - every one of the 689 parsed columns is exactly the claimed D_5 or
 *     A(h,beta) column.
 *
 * The builder is Python; this verifier shares no source code with it.
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    OUTPUT_R = 31,
    OUTPUT_N = 689,
    TOP_R = 11,
    TOP_N = 19,
    LOW_R = 10,
    LOW_N = 50,
    FIELD_M = 5,
    FIELD_SIZE = 32,
    D_SIZE = 81,
    TOP_SPACE = 2048,
    LOW_SPACE = 1024
};

typedef struct {
    int redundancy;
    size_t length;
    uint32_t *columns;
} Matrix;

typedef struct {
    uint8_t weight;
    uint8_t indices[4];
} TopRepresentation;

typedef struct {
    uint8_t present;
    uint8_t weight;
    uint8_t indices[2];
} LowRepresentation;

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
            unsigned char *grown = realloc(*bits, next * sizeof(*grown));
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
        if (matrix.redundancy >= 32) {
            die("this verifier supports at most 32 matrix rows");
        }
        row_length = parse_row(cursor, &row_bits, &row_capacity);
        if (row_length == 0) {
            continue;
        }
        if (matrix.length == 0) {
            matrix.length = row_length;
            matrix.columns = calloc(matrix.length, sizeof(*matrix.columns));
            if (matrix.columns == NULL) {
                die("out of memory allocating matrix columns");
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

static int binary_rank(const uint32_t *columns, size_t length) {
    uint32_t basis[32] = {0};
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

static void check_distinct_nonzero(const Matrix *matrix) {
    uint64_t ceiling = UINT64_C(1) << matrix->redundancy;
    for (size_t left = 0; left < matrix->length; ++left) {
        if (matrix->columns[left] == 0 || matrix->columns[left] >= ceiling) {
            die("matrix has a zero or out-of-range column");
        }
        for (size_t right = 0; right < left; ++right) {
            if (matrix->columns[left] == matrix->columns[right]) {
                die("matrix has a repeated column");
            }
        }
    }
}

static uint32_t reverse_bits(uint32_t value, int width) {
    uint32_t result = 0;
    for (int bit = 0; bit < width; ++bit) {
        result |= ((value >> bit) & 1U) << (width - 1 - bit);
    }
    return result;
}

static void make_ok2(uint32_t columns[TOP_N]) {
    static const uint32_t raw_hex[8] = {
        0x4EA, 0x771, 0x006, 0x086, 0x1CD, 0x3B4, 0x17E, 0x7AB
    };
    for (int index = 0; index < TOP_R; ++index) {
        columns[index] = UINT32_C(1) << index;
    }
    for (int index = 0; index < 8; ++index) {
        columns[TOP_R + index] = reverse_bits(raw_hex[index], TOP_R);
    }
    if ((columns[8] ^ columns[9] ^ columns[13]) != 0) {
        die("OK2 dependent triple h9+h10+h14 is not zero");
    }
    if (binary_rank(columns, TOP_N) != TOP_R) {
        die("OK2 matrix is not full rank");
    }
}

static void verify_ok2_radius(const uint32_t columns[TOP_N],
                              uint64_t cumulative[4]) {
    unsigned char covered[TOP_SPACE] = {0};
    covered[0] = 1;
    for (int a = 0; a < TOP_N; ++a) {
        covered[columns[a]] = 1;
    }
    for (int syndrome = 0; syndrome < TOP_SPACE; ++syndrome) {
        cumulative[0] += covered[syndrome] != 0;
    }
    for (int a = 0; a < TOP_N; ++a) {
        for (int b = 0; b < a; ++b) {
            covered[columns[a] ^ columns[b]] = 1;
        }
    }
    for (int syndrome = 0; syndrome < TOP_SPACE; ++syndrome) {
        cumulative[1] += covered[syndrome] != 0;
    }
    for (int a = 0; a < TOP_N; ++a) {
        for (int b = 0; b < a; ++b) {
            for (int c = 0; c < b; ++c) {
                covered[columns[a] ^ columns[b] ^ columns[c]] = 1;
            }
        }
    }
    for (int syndrome = 0; syndrome < TOP_SPACE; ++syndrome) {
        cumulative[2] += covered[syndrome] != 0;
    }
    for (int a = 0; a < TOP_N; ++a) {
        for (int b = 0; b < a; ++b) {
            for (int c = 0; c < b; ++c) {
                for (int d = 0; d < c; ++d) {
                    covered[columns[a] ^ columns[b] ^
                            columns[c] ^ columns[d]] = 1;
                }
            }
        }
    }
    for (int syndrome = 0; syndrome < TOP_SPACE; ++syndrome) {
        cumulative[3] += covered[syndrome] != 0;
    }
    if (cumulative[0] != 20 || cumulative[1] != 183 ||
        cumulative[2] != 981 || cumulative[3] != TOP_SPACE) {
        die("OK2 covering counts disagree with the claimed radius-4 seed");
    }
}

static long parse_long_token(const char *token, const char *what) {
    char *end = NULL;
    long value;
    errno = 0;
    value = strtol(token, &end, 10);
    if (errno != 0 || end == token || *end != '\0') {
        fprintf(stderr, "FAIL: invalid %s token: %s\n", what, token);
        exit(1);
    }
    return value;
}

static void read_top_certificate(const char *path,
                                 TopRepresentation reps[TOP_SPACE]) {
    FILE *file = fopen(path, "r");
    char *line = NULL;
    size_t capacity = 0;
    ssize_t got;
    int expected_syndrome = 0;
    if (file == NULL) {
        die_path("cannot open", path);
    }
    while ((got = getline(&line, &capacity, file)) >= 0) {
        char *save = NULL;
        char *token;
        long syndrome;
        long weight;
        (void)got;
        token = strtok_r(line, " \t\r\n", &save);
        if (token == NULL || token[0] == '#') {
            continue;
        }
        syndrome = parse_long_token(token, "certificate syndrome");
        token = strtok_r(NULL, " \t\r\n", &save);
        if (token == NULL || token[0] == '#') {
            die("certificate row has no weight");
        }
        weight = parse_long_token(token, "certificate weight");
        if (syndrome != expected_syndrome || syndrome >= TOP_SPACE) {
            die("certificate syndromes are missing, duplicated, or out of order");
        }
        if (weight < 1 || weight > 4) {
            die("certificate weight is outside 1..4");
        }
        reps[syndrome].weight = (uint8_t)weight;
        for (int slot = 0; slot < weight; ++slot) {
            long one_based;
            token = strtok_r(NULL, " \t\r\n", &save);
            if (token == NULL || token[0] == '#') {
                die("certificate row has too few column indices");
            }
            one_based = parse_long_token(token, "certificate column index");
            if (one_based < 1 || one_based > TOP_N) {
                die("certificate column index is outside 1..19");
            }
            reps[syndrome].indices[slot] = (uint8_t)(one_based - 1);
        }
        token = strtok_r(NULL, " \t\r\n", &save);
        if (token != NULL && token[0] != '#') {
            die("certificate row has too many tokens");
        }
        ++expected_syndrome;
    }
    if (ferror(file)) {
        die_path("error reading", path);
    }
    free(line);
    fclose(file);
    if (expected_syndrome != TOP_SPACE) {
        die("certificate does not contain exactly 2048 rows");
    }
}

static uint8_t gf_mul(uint8_t left, uint8_t right) {
    unsigned a = left;
    unsigned b = right;
    unsigned product = 0;
    while (b != 0) {
        if (b & 1U) {
            product ^= a;
        }
        b >>= 1;
        a <<= 1;
        if (a & FIELD_SIZE) {
            a ^= 0x25U;
        }
    }
    return (uint8_t)product;
}

static uint8_t gf_pow(uint8_t value, int exponent) {
    uint8_t result = 1;
    for (int power = 0; power < exponent; ++power) {
        result = gf_mul(result, value);
    }
    return result;
}

static uint8_t gf_inverse(uint8_t value) {
    if (value == 0) {
        die("attempted to invert zero in GF(32)");
    }
    for (int candidate = 1; candidate < FIELD_SIZE; ++candidate) {
        if (gf_mul(value, (uint8_t)candidate) == 1) {
            return (uint8_t)candidate;
        }
    }
    die("GF(32) element has no inverse");
    return 0;
}

static void verify_field(void) {
    unsigned char cubes[FIELD_SIZE] = {0};
    for (int a = 0; a < FIELD_SIZE; ++a) {
        if (gf_mul((uint8_t)a, 0) != 0 ||
            gf_mul((uint8_t)a, 1) != a) {
            die("GF(32) identity check failed");
        }
        for (int b = 0; b < FIELD_SIZE; ++b) {
            if (gf_mul((uint8_t)a, (uint8_t)b) !=
                gf_mul((uint8_t)b, (uint8_t)a)) {
                die("GF(32) multiplication is not commutative");
            }
            for (int c = 0; c < FIELD_SIZE; ++c) {
                if (gf_mul((uint8_t)a, (uint8_t)(b ^ c)) !=
                    (uint8_t)(gf_mul((uint8_t)a, (uint8_t)b) ^
                              gf_mul((uint8_t)a, (uint8_t)c))) {
                    die("GF(32) distributivity check failed");
                }
            }
        }
    }
    for (int a = 1; a < FIELD_SIZE; ++a) {
        uint8_t inverse = gf_inverse((uint8_t)a);
        uint8_t cube = gf_pow((uint8_t)a, 3);
        if (gf_mul((uint8_t)a, inverse) != 1 || cubes[cube]) {
            die("GF(32) inverse or odd-m cube-permutation check failed");
        }
        cubes[cube] = 1;
    }
}

static int gf_rank(uint8_t input[4][4], int size) {
    uint8_t matrix[4][4] = {{0}};
    int rank = 0;
    memcpy(matrix, input, sizeof(matrix));
    for (int column = 0; column < size; ++column) {
        int pivot = rank;
        while (pivot < size && matrix[pivot][column] == 0) {
            ++pivot;
        }
        if (pivot == size) {
            continue;
        }
        if (pivot != rank) {
            for (int j = 0; j < size; ++j) {
                uint8_t swap = matrix[rank][j];
                matrix[rank][j] = matrix[pivot][j];
                matrix[pivot][j] = swap;
            }
        }
        {
            uint8_t inverse = gf_inverse(matrix[rank][column]);
            for (int j = column; j < size; ++j) {
                matrix[rank][j] = gf_mul(matrix[rank][j], inverse);
            }
        }
        for (int row = 0; row < size; ++row) {
            if (row != rank && matrix[row][column] != 0) {
                uint8_t factor = matrix[row][column];
                for (int j = column; j < size; ++j) {
                    matrix[row][j] ^=
                        gf_mul(factor, matrix[rank][j]);
                }
            }
        }
        ++rank;
    }
    return rank;
}

static void coefficient_matrix(const TopRepresentation *rep,
                               uint8_t matrix[4][4]) {
    memset(matrix, 0, 16 * sizeof(uint8_t));
    if (rep->weight == 2) {
        for (int column = 0; column < 2; ++column) {
            uint8_t beta = (uint8_t)(rep->indices[column] + 1);
            matrix[0][column] = 1;
            matrix[1][column] = gf_pow(beta, 3);
        }
    } else {
        for (int row = 0; row < rep->weight; ++row) {
            for (int column = 0; column < rep->weight; ++column) {
                uint8_t beta = (uint8_t)(rep->indices[column] + 1);
                matrix[row][column] = gf_pow(beta, row);
            }
        }
    }
}

static void solve_system(uint8_t input[4][4], const uint8_t target[4],
                         int size, uint8_t solution[4]) {
    uint8_t matrix[4][5] = {{0}};
    for (int row = 0; row < size; ++row) {
        for (int column = 0; column < size; ++column) {
            matrix[row][column] = input[row][column];
        }
        matrix[row][size] = target[row];
    }
    for (int column = 0; column < size; ++column) {
        int pivot = column;
        while (pivot < size && matrix[pivot][column] == 0) {
            ++pivot;
        }
        if (pivot == size) {
            die("singular coefficient matrix reached witness synthesis");
        }
        if (pivot != column) {
            for (int j = column; j <= size; ++j) {
                uint8_t swap = matrix[column][j];
                matrix[column][j] = matrix[pivot][j];
                matrix[pivot][j] = swap;
            }
        }
        {
            uint8_t inverse = gf_inverse(matrix[column][column]);
            for (int j = column; j <= size; ++j) {
                matrix[column][j] = gf_mul(matrix[column][j], inverse);
            }
        }
        for (int row = 0; row < size; ++row) {
            if (row != column && matrix[row][column] != 0) {
                uint8_t factor = matrix[row][column];
                for (int j = column; j <= size; ++j) {
                    matrix[row][j] ^=
                        gf_mul(factor, matrix[column][j]);
                }
            }
        }
    }
    for (int row = 0; row < size; ++row) {
        solution[row] = matrix[row][size];
    }
}

static uint64_t verify_low_cover(const Matrix *low,
                                 LowRepresentation reps[LOW_SPACE]) {
    uint64_t covered = 0;
    reps[0].present = 1;
    reps[0].weight = 0;
    for (int index = 0; index < LOW_N; ++index) {
        uint32_t syndrome = low->columns[index];
        if (!reps[syndrome].present) {
            reps[syndrome].present = 1;
            reps[syndrome].weight = 1;
            reps[syndrome].indices[0] = (uint8_t)index;
        }
    }
    for (int left = 0; left < LOW_N; ++left) {
        for (int right = 0; right < left; ++right) {
            uint32_t syndrome = low->columns[left] ^ low->columns[right];
            if (!reps[syndrome].present) {
                reps[syndrome].present = 1;
                reps[syndrome].weight = 2;
                reps[syndrome].indices[0] = (uint8_t)left;
                reps[syndrome].indices[1] = (uint8_t)right;
            }
        }
    }
    for (int syndrome = 0; syndrome < LOW_SPACE; ++syndrome) {
        covered += reps[syndrome].present != 0;
    }
    if (covered != LOW_SPACE) {
        die("r=10 constituent is not a radius-2 covering");
    }
    return covered;
}

static void add_witness_column(const Matrix *output, size_t index,
                               size_t chosen[4], int *weight,
                               uint32_t *sum) {
    if (*weight >= 4 || index >= output->length) {
        die("constructed witness exceeds four columns or matrix length");
    }
    for (int prior = 0; prior < *weight; ++prior) {
        if (chosen[prior] == index) {
            die("constructed witness repeats an output column");
        }
    }
    chosen[*weight] = index;
    ++*weight;
    *sum ^= output->columns[index];
}

static void synthesize_witness(const Matrix *output,
                               const TopRepresentation *rep,
                               const LowRepresentation low_reps[LOW_SPACE],
                               uint32_t top, uint32_t bottom) {
    uint8_t u[4];
    uint8_t matrix[4][4] = {{0}};
    uint8_t target[4] = {0};
    uint8_t solution[4] = {0};
    size_t chosen[4] = {0};
    int weight = 0;
    uint32_t sum = 0;
    uint32_t low_syndrome;
    uint8_t residual_u4;

    for (int block = 0; block < 4; ++block) {
        u[block] = (uint8_t)((bottom >> (FIELD_M * block)) & 31U);
    }
    coefficient_matrix(rep, matrix);

    if (rep->weight == 4) {
        for (int row = 0; row < 4; ++row) {
            target[row] = u[row];
        }
        solve_system(matrix, target, 4, solution);
        for (int slot = 0; slot < 4; ++slot) {
            size_t index = D_SIZE +
                (size_t)rep->indices[slot] * FIELD_SIZE + solution[slot];
            add_witness_column(output, index, chosen, &weight, &sum);
        }
    } else if (rep->weight == 3) {
        target[0] = u[0];
        target[1] = u[1];
        target[2] = u[2];
        solve_system(matrix, target, 3, solution);
        residual_u4 = u[3];
        for (int slot = 0; slot < 3; ++slot) {
            uint8_t beta = (uint8_t)(rep->indices[slot] + 1);
            size_t index = D_SIZE +
                (size_t)rep->indices[slot] * FIELD_SIZE + solution[slot];
            residual_u4 ^= gf_mul(gf_pow(beta, 3), solution[slot]);
            add_witness_column(output, index, chosen, &weight, &sum);
        }
        if (residual_u4 != 0) {
            add_witness_column(output, LOW_N + residual_u4 - 1,
                               chosen, &weight, &sum);
        }
    } else if (rep->weight == 2) {
        target[0] = u[0];
        target[1] = u[3];
        solve_system(matrix, target, 2, solution);
        low_syndrome = (uint32_t)u[1] | ((uint32_t)u[2] << FIELD_M);
        for (int slot = 0; slot < 2; ++slot) {
            uint8_t beta = (uint8_t)(rep->indices[slot] + 1);
            size_t index = D_SIZE +
                (size_t)rep->indices[slot] * FIELD_SIZE + solution[slot];
            low_syndrome ^= gf_mul(beta, solution[slot]);
            low_syndrome ^=
                (uint32_t)gf_mul(gf_pow(beta, 2), solution[slot]) << FIELD_M;
            add_witness_column(output, index, chosen, &weight, &sum);
        }
        for (int slot = 0; slot < low_reps[low_syndrome].weight; ++slot) {
            add_witness_column(output,
                               low_reps[low_syndrome].indices[slot],
                               chosen, &weight, &sum);
        }
    } else if (rep->weight == 1) {
        uint8_t beta = (uint8_t)(rep->indices[0] + 1);
        uint8_t xi = u[0];
        size_t index = D_SIZE +
            (size_t)rep->indices[0] * FIELD_SIZE + xi;
        low_syndrome =
            (uint32_t)(u[1] ^ gf_mul(beta, xi)) |
            ((uint32_t)(u[2] ^ gf_mul(gf_pow(beta, 2), xi)) << FIELD_M);
        residual_u4 = u[3] ^ gf_mul(gf_pow(beta, 3), xi);
        add_witness_column(output, index, chosen, &weight, &sum);
        for (int slot = 0; slot < low_reps[low_syndrome].weight; ++slot) {
            add_witness_column(output,
                               low_reps[low_syndrome].indices[slot],
                               chosen, &weight, &sum);
        }
        if (residual_u4 != 0) {
            add_witness_column(output, LOW_N + residual_u4 - 1,
                               chosen, &weight, &sum);
        }
    } else {
        die("invalid top representation weight in witness synthesis");
    }

    if (weight < 1 || weight > 4 ||
        sum != (top | (bottom << TOP_R))) {
        die("constructed probe witness has the wrong syndrome or weight");
    }
}

static void verify_output_formula(const Matrix *output, const Matrix *low,
                                  const uint32_t top_columns[TOP_N]) {
    for (int index = 0; index < LOW_N; ++index) {
        uint32_t expected = low->columns[index] << (TOP_R + FIELD_M);
        if (output->columns[index] != expected) {
            die("output D_5 radius-2 column disagrees with construction");
        }
    }
    for (int value = 1; value < FIELD_SIZE; ++value) {
        uint32_t expected = (uint32_t)value << (TOP_R + 3 * FIELD_M);
        if (output->columns[LOW_N + value - 1] != expected) {
            die("output D_5 Hamming column disagrees with construction");
        }
    }
    for (int seed = 0; seed < TOP_N; ++seed) {
        uint8_t beta = (uint8_t)(seed + 1);
        uint8_t beta2 = gf_pow(beta, 2);
        uint8_t beta3 = gf_pow(beta, 3);
        for (int xi = 0; xi < FIELD_SIZE; ++xi) {
            uint32_t expected = top_columns[seed]
                | ((uint32_t)xi << TOP_R)
                | ((uint32_t)gf_mul(beta, (uint8_t)xi)
                   << (TOP_R + FIELD_M))
                | ((uint32_t)gf_mul(beta2, (uint8_t)xi)
                   << (TOP_R + 2 * FIELD_M))
                | ((uint32_t)gf_mul(beta3, (uint8_t)xi)
                   << (TOP_R + 3 * FIELD_M));
            size_t position = D_SIZE + (size_t)seed * FIELD_SIZE + xi;
            if (output->columns[position] != expected) {
                die("output A(h,beta) column disagrees with construction");
            }
        }
    }
}

int main(int argc, char **argv) {
    Matrix output;
    Matrix low;
    uint32_t top_columns[TOP_N];
    TopRepresentation top_reps[TOP_SPACE] = {0};
    LowRepresentation low_reps[LOW_SPACE] = {0};
    uint64_t top_cumulative[4] = {0};
    uint64_t low_covered;
    uint64_t weight_histogram[5] = {0};
    uint64_t invertible_maps = 0;
    uint64_t witness_probes = 0;
    static const uint32_t extra_bottoms[] = {
        0xFFFFFU, 0xAAAAAU, 0x55555U, 0x12345U, 0xFEDCBU
    };

    if (argc != 4) {
        fprintf(stderr, "usage: %s OUTPUT_MATRIX RADIUS2_MATRIX TOP_CERT\n",
                argv[0]);
        return 2;
    }
    output = read_matrix(argv[1]);
    low = read_matrix(argv[2]);
    if (output.redundancy != OUTPUT_R || output.length != OUTPUT_N) {
        die("output matrix does not have shape 31 x 689");
    }
    if (low.redundancy != LOW_R || low.length != LOW_N) {
        die("radius-2 input does not have shape 10 x 50");
    }
    check_distinct_nonzero(&output);
    check_distinct_nonzero(&low);
    if (binary_rank(output.columns, output.length) != OUTPUT_R) {
        die("output matrix is not full rank");
    }
    if (binary_rank(low.columns, low.length) != LOW_R) {
        die("radius-2 input is not full rank");
    }

    make_ok2(top_columns);
    verify_ok2_radius(top_columns, top_cumulative);
    read_top_certificate(argv[3], top_reps);
    verify_field();
    low_covered = verify_low_cover(&low, low_reps);
    verify_output_formula(&output, &low, top_columns);

    for (int syndrome = 0; syndrome < TOP_SPACE; ++syndrome) {
        const TopRepresentation *rep = &top_reps[syndrome];
        uint32_t sum = 0;
        unsigned char used[TOP_N] = {0};
        uint8_t matrix[4][4] = {{0}};
        for (int slot = 0; slot < rep->weight; ++slot) {
            uint8_t index = rep->indices[slot];
            if (used[index]) {
                die("top certificate repeats a singleton partition block");
            }
            used[index] = 1;
            sum ^= top_columns[index];
        }
        if (sum != (uint32_t)syndrome) {
            die("top certificate row sums to the wrong syndrome");
        }
        ++weight_histogram[rep->weight];
        if (rep->weight >= 2) {
            coefficient_matrix(rep, matrix);
            if (gf_rank(matrix, rep->weight) != rep->weight) {
                die("a top certificate coefficient map is singular");
            }
            ++invertible_maps;
        }
    }
    if ((top_reps[0].weight != 3) ||
        top_reps[0].indices[0] != 8 ||
        top_reps[0].indices[1] != 9 ||
        top_reps[0].indices[2] != 13) {
        die("zero top syndrome does not use the certified h9+h10+h14 triple");
    }

    /* Directly synthesize witnesses from parsed output columns for zero,
       every bottom coordinate vector, and several dense patterns, for every
       one of the 2048 top certificate rows. */
    for (uint32_t syndrome = 0; syndrome < TOP_SPACE; ++syndrome) {
        synthesize_witness(&output, &top_reps[syndrome], low_reps,
                           syndrome, 0);
        ++witness_probes;
        for (int bit = 0; bit < 4 * FIELD_M; ++bit) {
            synthesize_witness(&output, &top_reps[syndrome], low_reps,
                               syndrome, UINT32_C(1) << bit);
            ++witness_probes;
        }
        for (size_t probe = 0;
             probe < sizeof(extra_bottoms) / sizeof(extra_bottoms[0]);
             ++probe) {
            synthesize_witness(&output, &top_reps[syndrome], low_reps,
                               syndrome, extra_bottoms[probe]);
            ++witness_probes;
        }
    }

    if ((output.columns[D_SIZE + 8 * FIELD_SIZE]
         ^ output.columns[D_SIZE + 9 * FIELD_SIZE]
         ^ output.columns[D_SIZE + 13 * FIELD_SIZE]) != 0) {
        die("lifted dependent triple is not zero");
    }

    printf("PASS matrix=%s r=31 n=689 rank=31 distinct_nonzero=689 d=3\n",
           argv[1]);
    printf("PASS OK2 cumulative_le1..le4=%" PRIu64 ",%" PRIu64
           ",%" PRIu64 ",%" PRIu64
           " top_partition=2048/2048 weights=1:%" PRIu64
           ",2:%" PRIu64 ",3:%" PRIu64 ",4:%" PRIu64 "\n",
           top_cumulative[0], top_cumulative[1], top_cumulative[2],
           top_cumulative[3], weight_histogram[1], weight_histogram[2],
           weight_histogram[3], weight_histogram[4]);
    printf("PASS D5 radius2=%" PRIu64 "/1024 W5=31/31 "
           "invertible_maps=%" PRIu64 " witness_probes=%" PRIu64 "\n",
           low_covered, invertible_maps, witness_probes);
    printf("PASS coverage=2147483648/2147483648 by certified block "
           "decomposition; radius=4 (1067 OK2 syndromes need weight 4)\n");

    free(output.columns);
    free(low.columns);
    return 0;
}
