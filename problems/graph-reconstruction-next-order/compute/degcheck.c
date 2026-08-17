/* degcheck.c — histogram degree sequences of graph6 input. */
#define MAXN 64
#include "gtools.h"
#include "nauty.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXSEQ 64

typedef struct {
    unsigned char seq[MAXN];
    unsigned long long count;
} rec_t;

static rec_t *tab;
static size_t ntab, ctab;

static int same(const unsigned char *a, const unsigned char *b, int n)
{
    return memcmp(a, b, (size_t)n) == 0;
}

int main(void)
{
    char *line;
    graph g[MAXN];
    unsigned long long nread = 0;
    ctab = 16;
    tab = calloc(ctab, sizeof(rec_t));
    while ((line = gtools_getline(stdin)) != NULL) {
        if (line[0] == '>' || line[0] == 0 || line[0] == 'r')
            continue;
        int n = graphsize(line);
        stringtograph(line, g, 1);
        unsigned char seq[MAXN];
        for (int i = 0; i < n; i++)
            seq[i] = (unsigned char)POPCOUNT(g[i]);
        /* insertion sort */
        for (int i = 1; i < n; i++) {
            unsigned char k = seq[i];
            int j = i - 1;
            while (j >= 0 && seq[j] > k) {
                seq[j + 1] = seq[j];
                j--;
            }
            seq[j + 1] = k;
        }
        size_t i;
        for (i = 0; i < ntab; i++)
            if (same(tab[i].seq, seq, n)) {
                tab[i].count++;
                break;
            }
        if (i == ntab) {
            if (ntab == ctab) {
                ctab *= 2;
                tab = realloc(tab, ctab * sizeof(rec_t));
            }
            memset(&tab[ntab], 0, sizeof(rec_t));
            memcpy(tab[ntab].seq, seq, (size_t)n);
            tab[ntab].count = 1;
            ntab++;
        }
        nread++;
    }
    printf("read=%llu sequences=%zu\n", nread, ntab);
    for (size_t k = 0; k < ntab; k++) {
        printf("%llu :", tab[k].count);
        for (int i = 0; i < 14 && tab[k].seq[i]; i++)
            printf(" %u", (unsigned)tab[k].seq[i]);
        /* print all n=14 including zeros */
        printf("  [");
        for (int i = 0; i < 14; i++)
            printf("%s%u", i ? "," : "", (unsigned)tab[k].seq[i]);
        printf("]\n");
    }
    return 0;
}
