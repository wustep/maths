/* Upper bounds only. Reuse q1's exact arithmetic and three-step endgame,
 * stopping a target at its first witness. No failed search is a lower bound.
 * gcc -O3 -fopenmp find_witness.c -o find_witness
 * find_witness STEPS TARGETS > witnesses.txt
 * TARGETS has fewer than 1024 rows, each "name value". Output: JSON lines.
 */
#define main q1_main
#include "../q1/slp_search.c"
#undef main

static bool emitted[MAXT];
static int pending;

static void emit_hits(void) {
    for (int t = 0; t < ntargets; ++t) {
        if (emitted[t] || targets[t].best > g_steps) continue;
        /* Keep q1's JSON witness; the Python driver extracts its values. */
        printf("{\"value\":\"%s\",\"steps\":%d,\"program\":%s}\n",
               targets[t].dec, targets[t].best, targets[t].witness);
        fflush(stdout);
        emitted[t] = true;
        --pending;
    }
}

static void leaf(ctx_t *c) {
    leafinfo_t li;
    memset(li.remdone, 0, sizeof li.remdone);
    li.smax = c->set[0];
    for (int i = 1; i < c->nset; ++i)
        if (vcmp(c, &c->set[i], &li.smax) > 0) li.smax = c->set[i];
    bool first = true;
    li.qcount = 0;
    for (int q = 0; q < c->qlen; ++q) {
        if (c->hstate[hfind(c, &c->queue[q])] != ST_INQ) continue;
        ++li.qcount;
        if (first) { li.qmin = li.qmax = c->queue[q]; first = false; }
        else {
            if (vcmp(c, &c->queue[q], &li.qmin) < 0) li.qmin = c->queue[q];
            if (vcmp(c, &c->queue[q], &li.qmax) > 0) li.qmax = c->queue[q];
        }
    }
    uint32_t mark = c->arena_top;
    for (int t = 0; t < ntargets; ++t) {
        if (emitted[t]) continue;
        endgame(c, t, &li);
        c->arena_top = mark;
    }
    emit_hits();
}

static void witness_dfs(ctx_t *c, int start) {
    if (!pending) return;
    if (c->nset - 1 == g_depth) { leaf(c); return; }
    int end = c->qlen;
    for (int q = start; q < end && pending; ++q) {
        val_t v = c->queue[q];
        push_value(c, &v, q);
        for (int t = 0; t < ntargets; ++t)
            if (!emitted[t] && veq(c, &v, &targets[t].v))
                record_hit(c, t, c->nset - 1, NULL, 0);
        emit_hits();
        witness_dfs(c, q + 1);
        pop_value(c);
    }
}

int main(int argc, char **argv) {
    if (argc != 3) return 2;
    g_steps = atoi(argv[1]);
    if (g_steps < 4 || g_steps > 10) return 2;
    g_depth = g_steps - 3;
    load_targets(argv[2]);
    pending = ntargets;
    ctx_t *c = malloc(sizeof *c);
    if (!c) return 2;
    ctx_init(c);
    witness_dfs(c, 0);
    fprintf(stderr, "%d/%d targets have witnesses\n", ntargets - pending, ntargets);
    free(c->arena);
    free(c);
    return pending ? 1 : 0;
}
