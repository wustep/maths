/* zonec -- exhaustive sweep of the Haas maximal stratum on one triangulation.
 *
 * Every maximal degree-8 T-curve on a fixed triangulation T has sign
 * distribution in the affine F_2 subspace  eta + span{delta_S : S a Harnack
 * split with edges in T}  (Haas, as stated in arXiv:2602.06888 v3 Thm 13).
 * export_span.py hands us that subspace's basis together with the already
 * built rhombus complex from fastcx.Complex, so this program rebuilds no
 * geometry: it Gray-code walks all 2^rank members of the subspace and
 * computes, for each, the component count and a canonical fingerprint of the
 * real scheme (tcore.h, same nesting logic as fastcx._scheme with the bracket
 * rendering replaced by a 128-bit canonical hash).
 *
 * It emits one witness per distinct fingerprint.  The scheme string of record
 * is then recomputed in Python from that witness by the exact pipeline; this
 * program is an accelerator that decides *which* sign vectors are worth
 * looking at, never the verifier.
 *
 * usage: zonec <task.txt> <shard> <nshards> <out.jsonl>
 */
#include "tcore.h"

int main(int argc, char **argv)
{
    if (argc != 5) { fprintf(stderr, "usage: zonec task shard nshards out\n"); return 1; }
    fclose(load_task(argv[1]));

    long shard = atol(argv[2]), nsh = atol(argv[3]);
    FILE *out = fopen(argv[4], "w");
    uint64_t total = (rnk >= 63) ? 0 : (1ULL << rnk);
    uint64_t lo = total * shard / nsh, hi = total * (shard + 1) / nsh;

    for (int i = 0; i < npts; i++) cursign[i] = eta_s[i];
    uint64_t g0 = lo ^ (lo >> 1), acc = 0;
    for (int i = 0; i < rnk; i++) if (g0 >> i & 1) acc ^= basis[i];
    for (int j = 0; j < npts; j++) if (acc >> j & 1) cursign[j] = -cursign[j];

    uint64_t prev = g0, evals = 0, maxev = 0, valid = 0, logged = 0;
    for (uint64_t m = lo; m < hi; m++) {
        uint64_t g = m ^ (m >> 1), diff = g ^ prev;
        while (diff) {
            uint64_t low = diff & (~diff + 1);
            uint64_t b = basis[__builtin_ctzll(low)];
            for (int j = 0; j < npts; j++) if (b >> j & 1) cursign[j] = -cursign[j];
            diff ^= low;
        }
        prev = g;
        int ok; H128 fp;
        int ncomp = evaluate(cursign, &ok, &fp);
        evals++;
        if (!ok) continue;
        valid++;
        if (ncomp == 22) maxev++;
        if (seen_fp(fp, ncomp)) continue;
        logged++;
        fprintf(out, "{\"kind\":\"WITNESS\",\"ncomp\":%d,\"sweep_index\":%llu,"
                     "\"fp\":\"%016llx%016llx\",\"signs\":[",
                ncomp, (unsigned long long)m,
                (unsigned long long)fp.a, (unsigned long long)fp.b);
        for (int j = 0; j < npts; j++)
            fprintf(out, "%s%d", j ? "," : "", cursign[j]);
        fprintf(out, "]}\n");
        fflush(out);
    }
    fprintf(out, "{\"kind\":\"summary\",\"rank\":%d,\"lo\":%llu,\"hi\":%llu,"
                 "\"evals\":%llu,\"valid\":%llu,\"maximal\":%llu,\"distinct\":%llu}\n",
            rnk, (unsigned long long)lo, (unsigned long long)hi,
            (unsigned long long)evals, (unsigned long long)valid,
            (unsigned long long)maxev, (unsigned long long)logged);
    fclose(out);
    fprintf(stderr, "rank=%d evals=%llu valid=%llu max=%llu distinct=%llu\n",
            rnk, (unsigned long long)evals, (unsigned long long)valid,
            (unsigned long long)maxev, (unsigned long long)logged);
    return 0;
}
