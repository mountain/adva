use adva_ir::Rational;

#[test]
fn exact_ratios_round_once_at_unit_boundaries_and_ties() {
    let one = 1.0_f64.to_bits();
    let cases = [
        (9_007_199_254_740_995, 9_007_199_254_740_994, one),
        (9_007_199_254_740_992, 9_007_199_254_740_993, one - 1),
        (9_007_199_254_740_993, 9_007_199_254_740_994, one - 1),
        // Exactly halfway: the even significand wins on either side.
        (9_007_199_254_740_993, 9_007_199_254_740_992, one),
        (9_007_199_254_740_995, 9_007_199_254_740_992, one + 2),
        (1, 3, 0x3fd5_5555_5555_5555),
        (i64::MAX, 1, (2.0_f64.powi(63)).to_bits()),
        (1, i64::MAX, (2.0_f64.powi(-63)).to_bits()),
    ];
    for (n, d, expected) in cases {
        for sign in [-1, 1] {
            let actual = Rational::new(sign * n, d).unwrap().as_f64().to_bits();
            let sign_bit = if sign < 0 { 1 << 63 } else { 0 };
            assert_eq!(actual, expected | sign_bit, "{sign} * {n}/{d}");
        }
    }
    // Every ratio is strictly below the midpoint above one, independently of
    // the implementation's quotient/remainder arithmetic.
    for d in (1_i64 << 53) + 2..=(1_i64 << 53) + 257 {
        assert_eq!(Rational::new(d + 1, d).unwrap().as_f64(), 1.0);
    }
}

#[test]
fn full_signed_range_and_zero_do_not_overflow() {
    for (n, d, expected) in [
        (i64::MIN, 1, -2.0_f64.powi(63)),
        (i64::MIN, i64::MIN, 1.0),
        (1, i64::MIN, -2.0_f64.powi(-63)),
        (0, 1, 0.0),
        (0, -1, -0.0),
    ] {
        assert_eq!(
            Rational {
                numerator: n,
                denominator: d
            }
            .as_f64()
            .to_bits(),
            expected.to_bits()
        );
    }
}
