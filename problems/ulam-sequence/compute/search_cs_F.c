/* Exact Frobenius majorant of the CS constrained joint spectral radius.
 *
 * For every admissible word W of length L,
 *     ||W||_2 ≤ ||W||_F = sqrt(sum W_ij^2),
 * and sum W_ij^2 is an integer.  The output max_F2 is therefore an exact
 * integer certificate that a_n = O(C^n) with C = (max_F2)^{1/(2L)}.
 *
 * Build: cc -O3 -o search_cs_F search_cs_F.c -lm
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef int64_t i64;

static const i64 T[3][4][4] = {
    {{1, 0, 0, 1}, {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}},
    {{0, 1, 1, 0}, {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}},
    {{1, 0, 1, 0}, {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}},
};

static void mul_left(i64 out[4][4], int which, const i64 in[4][4]) {
    const i64(*A)[4] = T[which];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            i64 s = 0;
            for (int k = 0; k < 4; k++) s += A[i][k] * in[k][j];
            out[i][j] = s;
        }
    }
}

static void eye(i64 A[4][4]) {
    memset(A, 0, 16 * sizeof(i64));
    A[0][0] = A[1][1] = A[2][2] = A[3][3] = 1;
}

static i64 frobenius2(const i64 A[4][4]) {
    i64 s = 0;
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) s += A[i][j] * A[i][j];
    return s;
}

static int Lglob;
static unsigned long nwords;
static i64 bestF2;
static int bestFw[64], curw[64];
static i64 stack[64][4][4];

static void dfs(int depth, int last) {
    if (depth == Lglob) {
        nwords++;
        i64 f2 = frobenius2(stack[depth]);
        if (f2 > bestF2) {
            bestF2 = f2;
            memcpy(bestFw, curw, Lglob * sizeof(int));
        }
        return;
    }
    for (int k = 0; k < 3; k++) {
        if (k == 2 && last == 2) continue;
        curw[depth] = k + 1;
        mul_left(stack[depth + 1], k, stack[depth]);
        dfs(depth + 1, k);
    }
}

static void print_word(const int *w, int L) {
    for (int i = 0; i < L; i++) putchar('0' + w[i]);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s L\n", argv[0]);
        return 2;
    }
    Lglob = atoi(argv[1]);
    if (Lglob < 1 || Lglob > 40) {
        fprintf(stderr, "L out of range\n");
        return 2;
    }
    bestF2 = 0;
    nwords = 0;
    eye(stack[0]);
    clock_t t0 = clock();
    dfs(0, -1);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    double invL = 1.0 / (double)Lglob;
    printf("{\n");
    printf("  \"L\": %d,\n", Lglob);
    printf("  \"nwords\": %lu,\n", nwords);
    printf("  \"seconds\": %.4f,\n", secs);
    printf("  \"max_F2\": %lld,\n", (long long)bestF2);
    printf("  \"CF\": %.16f,\n", pow((double)bestF2, 0.5 * invL));
    printf("  \"wordF\": \"");
    print_word(bestFw, Lglob);
    printf("\"\n");
    printf("}\n");
    return 0;
}
