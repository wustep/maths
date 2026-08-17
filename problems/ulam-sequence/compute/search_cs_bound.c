/* Enumerate admissible CS majorant words of length L and record max norms.
 *
 * Alphabet {1,2,3} = {T1, T2, T3}, no two consecutive 3s.
 * Reports max spectral 2-norm, 1-norm, inf-norm, and sqrt(||.||_1 ||.||_inf).
 *
 * Build: cc -O3 -ffast-math -o search_cs_bound search_cs_bound.c -lm
 * Run:   ./search_cs_bound 15
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef int64_t i64;

static const i64 T[3][4][4] = {
    /* T1 Type I: a_n + a_{n-3} */
    {{1, 0, 0, 1}, {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}},
    /* T2 Type II: a_{n-1} + a_{n-2} */
    {{0, 1, 1, 0}, {1, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}},
    /* T3 Eggleton: a_n + a_{n-2} */
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

/* Largest eigenvalue of 4x4 symmetric PSD matrix by Jacobi. */
static double max_eig_sym4(double S[4][4]) {
    double A[4][4];
    memcpy(A, S, sizeof(A));
    for (int iter = 0; iter < 40; iter++) {
        int p = 0, q = 1;
        double off = 0.0;
        for (int i = 0; i < 4; i++) {
            for (int j = i + 1; j < 4; j++) {
                double v = fabs(A[i][j]);
                if (v > off) {
                    off = v;
                    p = i;
                    q = j;
                }
            }
        }
        if (off < 1e-18 * (1.0 + fabs(A[0][0]) + fabs(A[1][1]) + fabs(A[2][2]) +
                           fabs(A[3][3])))
            break;
        double app = A[p][p], aqq = A[q][q], apq = A[p][q];
        double tau = (aqq - app) / (2.0 * apq);
        double t = (tau >= 0 ? 1.0 : -1.0) / (fabs(tau) + sqrt(1.0 + tau * tau));
        double c = 1.0 / sqrt(1.0 + t * t);
        double s = t * c;
        A[p][p] = app - t * apq;
        A[q][q] = aqq + t * apq;
        A[p][q] = A[q][p] = 0.0;
        for (int k = 0; k < 4; k++) {
            if (k == p || k == q) continue;
            double aik = A[k][p], aiq = A[k][q];
            A[k][p] = A[p][k] = c * aik - s * aiq;
            A[k][q] = A[q][k] = s * aik + c * aiq;
        }
    }
    double m = A[0][0];
    for (int i = 1; i < 4; i++)
        if (A[i][i] > m) m = A[i][i];
    return m;
}

static double opnorm2(const i64 A[4][4]) {
    double S[4][4];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            double s = 0.0;
            for (int k = 0; k < 4; k++)
                s += (double)A[k][i] * (double)A[k][j]; /* (A^T A)_ij */
            S[i][j] = s;
        }
    }
    double lam = max_eig_sym4(S);
    if (lam < 0) lam = 0;
    return sqrt(lam);
}

static i64 opnorm1(const i64 A[4][4]) {
    i64 m = 0;
    for (int j = 0; j < 4; j++) {
        i64 s = 0;
        for (int i = 0; i < 4; i++) s += A[i][j] < 0 ? -A[i][j] : A[i][j];
        if (s > m) m = s;
    }
    return m;
}

static i64 opnorminf(const i64 A[4][4]) {
    i64 m = 0;
    for (int i = 0; i < 4; i++) {
        i64 s = 0;
        for (int j = 0; j < 4; j++) s += A[i][j] < 0 ? -A[i][j] : A[i][j];
        if (s > m) m = s;
    }
    return m;
}

static int Lglob;
static unsigned long nwords;
static double best2, best1inf;
static i64 best1, bestinf, bestF2, bestGersh;
static int best2w[64], best1w[64], bestinfw[64], best1infw[64], bestFw[64],
    bestGw[64];
static int curw[64];
static i64 stack[64][4][4];

static i64 frobenius2(const i64 A[4][4]) {
    i64 s = 0;
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) s += A[i][j] * A[i][j];
    return s;
}

/* λ_max(A^T A) ≤ max row-sum of A^T A (entries of A^T A are nonnegative). */
static i64 gershgorin_ATA(const i64 A[4][4]) {
    i64 B[4][4];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            i64 s = 0;
            for (int k = 0; k < 4; k++) s += A[k][i] * A[k][j];
            B[i][j] = s;
        }
    }
    i64 m = 0;
    for (int i = 0; i < 4; i++) {
        i64 s = 0;
        for (int j = 0; j < 4; j++) s += B[i][j];
        if (s > m) m = s;
    }
    return m;
}

static void consider(int L, const i64 A[4][4]) {
    nwords++;
    double n2 = opnorm2(A);
    i64 n1 = opnorm1(A);
    i64 ninf = opnorminf(A);
    double g = sqrt((double)n1 * (double)ninf);
    i64 f2 = frobenius2(A);
    i64 ger = gershgorin_ATA(A);
    if (n2 > best2) {
        best2 = n2;
        memcpy(best2w, curw, L * sizeof(int));
    }
    if (n1 > best1) {
        best1 = n1;
        memcpy(best1w, curw, L * sizeof(int));
    }
    if (ninf > bestinf) {
        bestinf = ninf;
        memcpy(bestinfw, curw, L * sizeof(int));
    }
    if (g > best1inf) {
        best1inf = g;
        memcpy(best1infw, curw, L * sizeof(int));
    }
    if (f2 > bestF2) {
        bestF2 = f2;
        memcpy(bestFw, curw, L * sizeof(int));
    }
    if (ger > bestGersh) {
        bestGersh = ger;
        memcpy(bestGw, curw, L * sizeof(int));
    }
}

static void dfs(int depth, int last) {
    if (depth == Lglob) {
        consider(Lglob, stack[depth]);
        return;
    }
    for (int k = 0; k < 3; k++) {
        if (k == 2 && last == 2) continue; /* 2 here is T3 */
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
    best2 = best1inf = 0;
    best1 = bestinf = bestF2 = bestGersh = 0;
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
    printf("  \"C2\": %.16f,\n", pow(best2, invL));
    printf("  \"C1\": %.16f,\n", pow((double)best1, invL));
    printf("  \"Cinf\": %.16f,\n", pow((double)bestinf, invL));
    printf("  \"C1inf\": %.16f,\n", pow(best1inf, invL));
    printf("  \"CF\": %.16f,\n", pow((double)bestF2, 0.5 * invL));
    printf("  \"Cgersh\": %.16f,\n", pow((double)bestGersh, 0.5 * invL));
    printf("  \"max_n2\": %.16f,\n", best2);
    printf("  \"max_n1\": %lld,\n", (long long)best1);
    printf("  \"max_ninf\": %lld,\n", (long long)bestinf);
    printf("  \"max_n1inf\": %.16f,\n", best1inf);
    printf("  \"max_F2\": %lld,\n", (long long)bestF2);
    printf("  \"max_gersh\": %lld,\n", (long long)bestGersh);
    printf("  \"word2\": \"");
    print_word(best2w, Lglob);
    printf("\",\n");
    printf("  \"word1\": \"");
    print_word(best1w, Lglob);
    printf("\",\n");
    printf("  \"wordinf\": \"");
    print_word(bestinfw, Lglob);
    printf("\",\n");
    printf("  \"word1inf\": \"");
    print_word(best1infw, Lglob);
    printf("\",\n");
    printf("  \"wordF\": \"");
    print_word(bestFw, Lglob);
    printf("\",\n");
    printf("  \"wordG\": \"");
    print_word(bestGw, Lglob);
    printf("\"\n");
    printf("}\n");
    return 0;
}
