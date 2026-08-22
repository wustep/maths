/* Independent replay: read a whitespace-separated 0/1 parity-check matrix,
 * check F_2-rank and that every syndrome is a sum of at most two columns.
 * Shares no code with the search or with verify_graph.py.
 *   usage: verify_H <file.txt>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc, char **argv){
    FILE *f = fopen(argv[1], "r");
    if (!f){ perror(argv[1]); return 2; }
    static int bits[64][8192]; int nrow = 0, ncol = -1;
    char line[262144];
    while (fgets(line, sizeof line, f)){
        if (line[0] == '#' || line[0] == '\n') continue;
        int c = 0; char *p = line;
        while (*p){
            if (*p == '0' || *p == '1') bits[nrow][c++] = *p - '0';
            p++;
        }
        if (ncol < 0) ncol = c; else if (c != ncol){ printf("ragged row\n"); return 2; }
        nrow++;
    }
    fclose(f);
    uint32_t col[8192];
    for (int j = 0; j < ncol; j++){ uint32_t v = 0; for (int i = 0; i < nrow; i++) v |= (uint32_t)bits[i][j] << i; col[j] = v; }
    for (int j = 0; j < ncol; j++){
        if (!col[j]){ printf("zero column %d\n", j); return 1; }
        for (int i = 0; i < j; i++) if (col[i] == col[j]){ printf("repeated column %d %d\n", i, j); return 1; }
    }
    uint32_t bas[64]; int nb = 0;
    for (int j = 0; j < ncol; j++){ uint32_t c = col[j];
        for (int i = 0; i < nb; i++) if ((c ^ bas[i]) < c) c ^= bas[i];
        if (c){ bas[nb++] = c; for (int i = nb-1; i > 0 && bas[i] > bas[i-1]; i--){ uint32_t t = bas[i]; bas[i] = bas[i-1]; bas[i-1] = t; } } }
    size_t N = (size_t)1 << nrow;
    unsigned char *cov = calloc(N, 1);
    cov[0] = 1;
    for (int j = 0; j < ncol; j++) cov[col[j]] = 1;
    for (int i = 0; i < ncol; i++) for (int j = i+1; j < ncol; j++) cov[col[i] ^ col[j]] = 1;
    size_t got = 0; for (size_t s = 0; s < N; s++) got += cov[s];
    printf("%s: r=%d n=%d rank=%d covered=%zu/%zu %s\n", argv[1], nrow, ncol, nb, got, N,
           (got == N && nb == nrow) ? "OK" : "FAIL");
    free(cov);
    return (got == N && nb == nrow) ? 0 : 1;
}
