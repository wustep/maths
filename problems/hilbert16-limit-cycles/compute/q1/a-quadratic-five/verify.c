/* Direct differentiation check of the Poincaré–Lyapunov identity.

   Reads f_coeffs.txt (written by lyapunov.py). Rebuilds F, computes
   dF/dt along the unperturbed Shi field, and checks that every
   monomial of degree ≤ 8 equals the corresponding monomial of
   V3 (x²+y²)⁴ with V3 = 35625/8 (V1 = V2 = 0).

   This is not the recursive Lyapunov construction: it only
   differentiates the stored F.
*/

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    __int128 n;
    __int128 d;
} Q;

static __int128 iabs128(__int128 a) { return a < 0 ? -a : a; }

static __int128 igcd(__int128 a, __int128 b) {
    a = iabs128(a);
    b = iabs128(b);
    while (b) {
        __int128 t = a % b;
        a = b;
        b = t;
    }
    return a ? a : 1;
}

static Q qmake(__int128 n, __int128 d) {
    if (d == 0) {
        fprintf(stderr, "zero denominator\n");
        exit(1);
    }
    if (d < 0) {
        n = -n;
        d = -d;
    }
    __int128 g = igcd(n, d);
    Q q;
    q.n = n / g;
    q.d = d / g;
    return q;
}

static Q qadd(Q a, Q b) {
    return qmake(a.n * b.d + b.n * a.d, a.d * b.d);
}

static Q qmul(Q a, Q b) { return qmake(a.n * b.n, a.d * b.d); }

static Q qzero(void) { return qmake(0, 1); }

static int qeq(Q a, Q b) { return a.n == b.n && a.d == b.d; }

static void die(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}

/* acc[i][j] = coefficient of x^i y^j, i+j ≤ 8 */
static Q acc[9][9];

static void add_mon(int i, int j, Q c) {
    if (i < 0 || j < 0 || i + j > 8) {
        return;
    }
    acc[i][j] = qadd(acc[i][j], c);
}

int main(void) {
    FILE *fp = fopen("f_coeffs.txt", "r");
    if (!fp) {
        die("cannot open f_coeffs.txt");
    }

    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            acc[i][j] = qzero();
        }
    }

    Q V[4];
    V[1] = V[2] = V[3] = qmake(0, 1);
    int saw_F = 0;

    char line[256];
    while (fgets(line, sizeof line, fp)) {
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\0') {
            continue;
        }
        if (line[0] == 'F') {
            int deg, i, j;
            long long num, den;
            if (sscanf(line, "F %d %d %d %lld %lld", &deg, &i, &j, &num, &den) != 5) {
                die("bad F line");
            }
            if (i + j != deg || den == 0) {
                die("inconsistent F monomial");
            }
            saw_F++;
            Q c = qmake(num, den);
            /* d/dt (c x^i y^j) = c ( i x^{i-1} y^j P + j x^i y^{j-1} Q )
               P = -y - 10 x^2 + 5 x y + y^2
               Q =  x +      x^2 - 25 x y
            */
            if (i > 0) {
                Q ci = qmul(c, qmake(i, 1));
                add_mon(i - 1, j + 1, qmul(ci, qmake(-1, 1))); /* -y */
                add_mon(i + 1, j, qmul(ci, qmake(-10, 1)));    /* -10 x^2 */
                add_mon(i, j + 1, qmul(ci, qmake(5, 1)));      /* 5 x y */
                add_mon(i - 1, j + 2, qmul(ci, qmake(1, 1)));  /* y^2 */
            }
            if (j > 0) {
                Q cj = qmul(c, qmake(j, 1));
                add_mon(i + 1, j - 1, cj);                     /* x */
                add_mon(i + 2, j - 1, cj);                     /* x^2 */
                add_mon(i + 1, j, qmul(cj, qmake(-25, 1)));    /* -25 x y */
            }
        } else if (line[0] == 'V') {
            int k;
            long long num, den;
            if (sscanf(line, "V %d %lld %lld", &k, &num, &den) != 3) {
                die("bad V line");
            }
            if (k < 1 || k > 3) {
                die("V index");
            }
            V[k] = qmake(num, den);
        } else {
            die("unknown line");
        }
    }
    fclose(fp);

    if (saw_F < 10) {
        die("too few F monomials");
    }
    if (!qeq(V[1], qmake(0, 1)) || !qeq(V[2], qmake(0, 1))) {
        die("V1 or V2 not zero");
    }
    if (!qeq(V[3], qmake(35625, 8))) {
        die("V3 is not 35625/8");
    }

    /* target = V3 (x^2 + y^2)^4
       = V3 (x^8 + 4 x^6 y^2 + 6 x^4 y^4 + 4 x^2 y^6 + y^8) */
    Q T[9][9];
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) {
            T[i][j] = qzero();
        }
    }
    T[8][0] = V[3];
    T[6][2] = qmul(V[3], qmake(4, 1));
    T[4][4] = qmul(V[3], qmake(6, 1));
    T[2][6] = qmul(V[3], qmake(4, 1));
    T[0][8] = V[3];

    int bad = 0;
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9 - i; j++) {
            if (!qeq(acc[i][j], T[i][j])) {
                fprintf(stderr,
                        "mismatch x^%d y^%d: got %lld/%lld want %lld/%lld\n",
                        i, j,
                        (long long)acc[i][j].n, (long long)acc[i][j].d,
                        (long long)T[i][j].n, (long long)T[i][j].d);
                bad = 1;
            }
        }
    }
    if (bad) {
        die("identity failed");
    }
    printf("verify.c OK  dF/dt = (35625/8) (x^2+y^2)^4 + O(9)\n");
    return 0;
}
