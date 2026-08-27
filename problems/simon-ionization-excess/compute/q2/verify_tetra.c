/* Second language: 54 < 64 implies 3*sqrt(6) < 8, hence alpha_4,2*(N-1) < 2
   on the centred regular tetrahedron. No floating point in the comparison. */

#include <stdio.h>
#include <stdlib.h>

int main(void) {
    /* 3*sqrt(6) < 8  <=>  9*6 < 64 */
    const int lhs = 9 * 6;
    const int rhs = 8 * 8;
    if (lhs >= rhs) {
        fprintf(stderr, "FAIL: 54 < 64\n");
        return 1;
    }
    printf("verify_tetra.c: %d < %d, so 3*sqrt(6) < 8\n", lhs, rhs);
    printf("alpha_4,2 <= sqrt(6)/4 implies alpha_4,2 * 3 < 2\n");
    printf("not a dent: pair geometry cannot exclude N=4 at Z=2\n");
    return 0;
}
