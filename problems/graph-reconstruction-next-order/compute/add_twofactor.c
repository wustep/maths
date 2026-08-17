/* add_twofactor.c
 *
 * Read graphs in graph6 (intended: 4-regular on 14 vertices). For each G,
 * emit every simple supergraph G∪F where F is a nonempty 2-regular graph
 * (disjoint union of cycles of length ≥ 3) using only non-edges of G.
 *
 * Then G∪F has degrees deg_G(v) or deg_G(v)+2. If G is 4-regular this is
 * exactly the {4,6}-biregular graphs, each exactly once as a labelled pair
 * (G,F). Pipe through shortg to drop isomorphs.
 *
 * Usage: add_twofactor [--smin A] [--smax B] [--maxout N]
 */

#define MAXN 64
#include "gtools.h"
#include "nauty.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int smin = 3;
static int smax = 64;
static unsigned long long maxout = 0;
static unsigned long long n_in = 0;
static unsigned long long n_out = 0;
static unsigned long long n_dead = 0;

static graph g0[MAXN];
static graph work[MAXN];
static int ncur;
static int degF[MAXN];
static setword allowed[MAXN]; /* bit j (nauty numbering) set if ij is a non-edge */
static int supp[MAXN];
static int slen;
static int support_live;

static void emit(void)
{
    writeg6(stdout, work, 1, ncur);
    n_out++;
    if (maxout && n_out >= maxout)
        exit(0);
}

/* nauty bit for vertex j, m=1 */
static setword vbit(int j)
{
    setword b = 0;
    ADDELEMENT(&b, j);
    return b;
}

/* 2-factor on a FIXED support supp[0..slen-1]. Every support vertex must end at deg 2. */
static void rec_on_support(int idx)
{
    if (idx == slen) {
        emit();
        return;
    }
    int v = supp[idx];
    if (degF[v] == 2) {
        rec_on_support(idx + 1);
        return;
    }
    if (degF[v] > 2)
        return;
    /* need 2-degF[v] more neighbours in the support, later or any with spare capacity */
    for (int j = 0; j < slen; j++) {
        int w = supp[j];
        if (w <= v)
            continue;
        if (degF[w] >= 2)
            continue;
        if (!ISELEMENT(&allowed[v], w))
            continue;
        if (ISELEMENT(GRAPHROW(work, v, 1), w))
            continue;
        ADDONEEDGE(work, v, w, 1);
        degF[v]++;
        degF[w]++;
        if (degF[v] < 2)
            rec_on_support(idx); /* still filling v */
        else
            rec_on_support(idx + 1);
        DELONEEDGE(work, v, w, 1);
        degF[v]--;
        degF[w]--;
    }
}

static void enum_supports(int start, int need)
{
    if (need == 0) {
        memset(degF, 0, sizeof(int) * (size_t)ncur);
        rec_on_support(0);
        return;
    }
    for (int i = start; i <= ncur - need; i++) {
        supp[slen++] = i;
        enum_supports(i + 1, need - 1);
        slen--;
    }
}

static void process(graph *g, int n)
{
    ncur = n;
    memcpy(work, g, n * sizeof(graph));
    memset(degF, 0, sizeof(degF));
    slen = 0;
    for (int i = 0; i < n; i++) {
        allowed[i] = 0;
        for (int j = 0; j < n; j++) {
            if (i == j)
                continue;
            if (!ISELEMENT(GRAPHROW(g, i, 1), j))
                ADDELEMENT(&allowed[i], j);
        }
    }
    int lo = smin;
    int hi = smax;
    if (hi > n)
        hi = n;
    if (lo < 3)
        lo = 3;
    for (int s = lo; s <= hi; s++) {
        slen = 0;
        enum_supports(0, s);
    }
}

static void usage(void)
{
    fprintf(stderr,
            "Usage: add_twofactor [--smin A] [--smax B] [--maxout N]\n"
            "  Read graph6; write G∪F for every complement 2-factor F with\n"
            "  |support| in [smin,smax].\n");
}

int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--smin") == 0 && i + 1 < argc)
            smin = atoi(argv[++i]);
        else if (strcmp(argv[i], "--smax") == 0 && i + 1 < argc)
            smax = atoi(argv[++i]);
        else if (strcmp(argv[i], "--maxout") == 0 && i + 1 < argc)
            maxout = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "-h") == 0) {
            usage();
            return 0;
        } else {
            fprintf(stderr, "unknown arg %s\n", argv[i]);
            usage();
            return 1;
        }
    }

    char *line;
    while ((line = gtools_getline(stdin)) != NULL) {
        if (line[0] == '>' || line[0] == 0)
            continue;
        int n = graphsize(line);
        if (n < 3 || n > 64)
            continue;
        stringtograph(line, g0, 1);
        n_in++;
        process(g0, n);
        if ((n_in & 0x3FF) == 0)
            fprintf(stderr, "add_twofactor: in=%llu out=%llu\n", n_in, n_out);
    }
    fprintf(stderr, "add_twofactor: in=%llu out=%llu\n", n_in, n_out);
    (void)n_dead;
    (void)vbit;
    return 0;
}
