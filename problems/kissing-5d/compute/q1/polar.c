/* Exact polar-vertex enumeration for a rational 40-point code in R^5.
 *
 * Input (stdin):
 *   SCALE n
 *   n lines of 5 integers (SCALE * coordinates)
 *
 * A vertex solves A x = (SCALE,...,SCALE) for five linearly independent
 * integer rows A.  |x|^2 = |z|^2 / d^2 with z_j = det(A^{(j)}), d = det(A).
 * Feasible iff <z, p> ≤ d * SCALE for every input row p (sign of d).
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef int64_t i64;

static int SCALE;
static int N;
static i64 P[64][5];

static i64 det3(i64 a, i64 b, i64 c, i64 d, i64 e, i64 f, i64 g, i64 h, i64 i)
{
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}

static i64 det4(const i64 M[4][4])
{
    return (
        M[0][0] * det3(M[1][1], M[1][2], M[1][3], M[2][1], M[2][2], M[2][3], M[3][1], M[3][2], M[3][3])
        - M[0][1] * det3(M[1][0], M[1][2], M[1][3], M[2][0], M[2][2], M[2][3], M[3][0], M[3][2], M[3][3])
        + M[0][2] * det3(M[1][0], M[1][1], M[1][3], M[2][0], M[2][1], M[2][3], M[3][0], M[3][1], M[3][3])
        - M[0][3] * det3(M[1][0], M[1][1], M[1][2], M[2][0], M[2][1], M[2][2], M[3][0], M[3][1], M[3][2])
    );
}

static i64 det5(const i64 A[5][5])
{
    i64 total = 0;
    i64 sign = 1;
    for (int j = 0; j < 5; j++) {
        i64 minor[4][4];
        for (int i = 1; i < 5; i++) {
            int col = 0;
            for (int k = 0; k < 5; k++) {
                if (k == j) continue;
                minor[i - 1][col++] = A[i][k];
            }
        }
        total += sign * A[0][j] * det4(minor);
        sign = -sign;
    }
    return total;
}

static i64 cramer(const i64 A[5][5], int col, const i64 rhs[5])
{
    i64 B[5][5];
    memcpy(B, A, sizeof B);
    for (int i = 0; i < 5; i++) B[i][col] = rhs[i];
    return det5(B);
}

static void kernel4(const i64 rows[4][5], i64 r[5])
{
    for (int j = 0; j < 5; j++) {
        i64 minor[4][4];
        for (int i = 0; i < 4; i++) {
            int col = 0;
            for (int k = 0; k < 5; k++) {
                if (k == j) continue;
                minor[i][col++] = rows[i][k];
            }
        }
        r[j] = ((j % 2 == 0) ? 1 : -1) * det4(minor);
    }
}

int main(void)
{
    if (scanf("%d %d", &SCALE, &N) != 2) return 1;
    if (N <= 0 || N > 64) return 1;
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < 5; j++) {
            if (scanf("%lld", (long long *)&P[i][j]) != 1) return 1;
        }
    }

    i64 rhs[5] = {SCALE, SCALE, SCALE, SCALE, SCALE};
    long n_combos = 0, n_indep = 0, n_vert = 0;
    int have_max = 0;
    i64 max_z2 = 0, max_d2 = 1;
    i64 max_z[5] = {0};
    i64 max_d = 0;
    int max_idx[5] = {0};

    for (int a = 0; a < N; a++)
    for (int b = a + 1; b < N; b++)
    for (int c = b + 1; c < N; c++)
    for (int d = c + 1; d < N; d++)
    for (int e = d + 1; e < N; e++) {
        n_combos++;
        i64 A[5][5];
        int idxs[5] = {a, b, c, d, e};
        for (int i = 0; i < 5; i++)
            memcpy(A[i], P[idxs[i]], 5 * sizeof(i64));
        i64 det = det5(A);
        if (det == 0) continue;
        n_indep++;
        i64 z[5];
        for (int j = 0; j < 5; j++) z[j] = cramer(A, j, rhs);
        int ok = 1;
        for (int i = 0; i < N; i++) {
            i64 ip = 0;
            for (int j = 0; j < 5; j++) ip += z[j] * P[i][j];
            if (det > 0) {
                if (ip > det * (i64)SCALE) { ok = 0; break; }
            } else {
                if (ip < det * (i64)SCALE) { ok = 0; break; }
            }
        }
        if (!ok) continue;
        n_vert++;
        i64 z2 = 0;
        for (int j = 0; j < 5; j++) z2 += z[j] * z[j];
        i64 den = det * det;
        if (!have_max || z2 * max_d2 > max_z2 * den) {
            have_max = 1;
            max_z2 = z2;
            max_d2 = den;
            max_d = det;
            memcpy(max_z, z, sizeof z);
            memcpy(max_idx, idxs, sizeof idxs);
        }
    }

    int unbounded = 0;
    i64 ray[5] = {0};
    for (int a = 0; a < N && !unbounded; a++)
    for (int b = a + 1; b < N && !unbounded; b++)
    for (int c = b + 1; c < N && !unbounded; c++)
    for (int d = c + 1; d < N && !unbounded; d++) {
        i64 rows[4][5];
        int idxs[4] = {a, b, c, d};
        for (int i = 0; i < 4; i++) memcpy(rows[i], P[idxs[i]], 5 * sizeof(i64));
        i64 r[5];
        kernel4(rows, r);
        if (!r[0] && !r[1] && !r[2] && !r[3] && !r[4]) continue;
        for (int s = 0; s < 2 && !unbounded; s++) {
            i64 rr[5];
            i64 sg = (s == 0) ? 1 : -1;
            for (int j = 0; j < 5; j++) rr[j] = sg * r[j];
            int good = 1;
            for (int i = 0; i < N; i++) {
                i64 ip = 0;
                for (int j = 0; j < 5; j++) ip += rr[j] * P[i][j];
                if (ip > 0) { good = 0; break; }
            }
            if (good) {
                unbounded = 1;
                memcpy(ray, rr, sizeof rr);
            }
        }
    }

    /* reduce max_z2 / max_d2 */
    i64 num = max_z2, den = max_d2;
    i64 aa = num < 0 ? -num : num, bb = den < 0 ? -den : den;
    while (bb) { i64 t = aa % bb; aa = bb; bb = t; }
    if (aa == 0) aa = 1;
    num /= aa; den /= aa;
    if (den < 0) { num = -num; den = -den; }
    int lt2 = have_max && !unbounded && (num * 1 < 2 * den);

    printf("{\n");
    printf("  \"n_points\": %d,\n", N);
    printf("  \"scale\": %d,\n", SCALE);
    printf("  \"n_5subsets\": %ld,\n", n_combos);
    printf("  \"n_independent\": %ld,\n", n_indep);
    printf("  \"n_vertices\": %ld,\n", n_vert);
    printf("  \"bounded\": %s,\n", unbounded ? "false" : "true");
    printf("  \"max_norm2\": \"%lld/%lld\",\n", (long long)num, (long long)den);
    printf("  \"max_norm2_lt_2\": %s,\n", lt2 ? "true" : "false");
    printf("  \"maximal_as_spherical_code\": %s,\n", lt2 ? "true" : "false");
    printf("  \"max_vertex\": {\"support\": [%d, %d, %d, %d, %d], \"z\": [%lld, %lld, %lld, %lld, %lld], \"d\": %lld, \"norm2\": \"%lld/%lld\"}\n",
           max_idx[0], max_idx[1], max_idx[2], max_idx[3], max_idx[4],
           (long long)max_z[0], (long long)max_z[1], (long long)max_z[2],
           (long long)max_z[3], (long long)max_z[4],
           (long long)max_d, (long long)num, (long long)den);
    printf("}\n");
    return 0;
}
