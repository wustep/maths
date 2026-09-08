/* ABI-only bridge. All mathematical formulas and iteration live in Rust.
 * FLINT/Arb is shared with the first producer; this is not a second backend.
 */
#include <flint/arb.h>
#include <stdlib.h>

void *ball_new(void) {
    arb_ptr p = malloc(sizeof(arb_struct));
    if (!p) abort();
    arb_init(p);
    return p;
}
void ball_free(arb_ptr p) { arb_clear(p); free(p); }
void ball_int(arb_ptr p, long n) { arb_set_si(p, n); }
void ball_pi(arb_ptr p, long bits) { arb_const_pi(p, bits); }
void ball_add(arb_ptr r, arb_srcptr a, arb_srcptr b, long bits) { arb_add(r,a,b,bits); }
void ball_sub(arb_ptr r, arb_srcptr a, arb_srcptr b, long bits) { arb_sub(r,a,b,bits); }
void ball_mul(arb_ptr r, arb_srcptr a, arb_srcptr b, long bits) { arb_mul(r,a,b,bits); }
void ball_div(arb_ptr r, arb_srcptr a, arb_srcptr b, long bits) { arb_div(r,a,b,bits); }
void ball_log(arb_ptr r, arb_srcptr a, long bits) { arb_log(r,a,bits); }
void ball_exp(arb_ptr r, arb_srcptr a, long bits) { arb_exp(r,a,bits); }
void ball_expm1(arb_ptr r, arb_srcptr a, long bits) { arb_expm1(r,a,bits); }
void ball_sqrt(arb_ptr r, arb_srcptr a, long bits) { arb_sqrt(r,a,bits); }
void ball_abs(arb_ptr r, arb_srcptr a) { arb_abs(r,a); }
void ball_max(arb_ptr r, arb_srcptr a, arb_srcptr b, long bits) { arb_max(r,a,b,bits); }
int ball_gt(arb_srcptr a, arb_srcptr b) { return arb_gt(a,b); }
int ball_finite(arb_srcptr a) { return arb_is_finite(a); }
char *ball_text(arb_srcptr a) { return arb_get_str(a,35,0); }
void ball_text_free(char *p) { flint_free(p); }
