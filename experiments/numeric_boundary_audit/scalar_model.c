/* C binary64 reproduction of the inspected Rust scalar operation order.
 * This is not a Rust or Adva execution. No fast-math or reassociation.
 */
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static unsigned long long bits(double x) {
    uint64_t value;
    memcpy(&value, &x, sizeof value);
    return (unsigned long long)value;
}

int main(void) {
    if (FLT_RADIX != 2 || DBL_MANT_DIG != 53 || sizeof(double) != 8 || FLT_EVAL_METHOD != 0)
        return 2;
    const int exponents[] = {1010, 1013, 1014, 1020, 1010};
    const int scales[] = {10, 10, 10, 10, 20};
    printf("{\"float_radix\":%d,\"double_mantissa_bits\":%d,\"float_eval_method\":%d,\"log_chain\":[", FLT_RADIX, DBL_MANT_DIG, FLT_EVAL_METHOD);
    for (int i = 0; i < 5; i++) {
        volatile double x = ldexp(1.0, -exponents[i]);
        volatile double a = ldexp(1.0, -scales[i]);
        volatile double value = a * x;
        volatile double reciprocal = 1.0 / value;
        double current = reciprocal * a;
        double alternative = a / value;
        printf("%s{\"x_exponent\":%d,\"scale_exponent\":%d,\"intermediate_bits\":\"%016llx\",\"current_gradient_bits\":\"%016llx\",\"alternative_gradient_bits\":\"%016llx\",\"log_value_finite\":%s}",
               i ? "," : "", exponents[i], scales[i], bits(value), bits(current), bits(alternative), isfinite(log(value)) ? "true" : "false");
    }
    const int64_t numerators[] = {INT64_C(9007199254740992), INT64_C(9007199254740993), 1};
    const int64_t denominators[] = {INT64_C(9007199254740993), INT64_C(9007199254740994), 1024};
    printf("],\"rational_conversion\":[");
    for (int i = 0; i < 3; i++) {
        volatile int64_t n = numerators[i], d = denominators[i];
        volatile double nf = (double)n, df = (double)d;
        printf("%s{\"numerator\":%lld,\"denominator\":%lld,\"current_bits\":\"%016llx\"}",
               i ? "," : "", (long long)n, (long long)d, bits(nf / df));
    }
    printf("]}\n");
    return 0;
}
