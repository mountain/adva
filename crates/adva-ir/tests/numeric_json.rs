#[test]
fn json_decodes_the_k28_input_without_changing_its_bits() {
    let decoded: f64 = serde_json::from_str("0.9999999962747097").unwrap();
    let expected = 1.0 - 2.0_f64.powi(-28);
    assert_eq!(decoded.to_bits(), expected.to_bits());
}

#[test]
fn finite_json_numbers_round_trip_bit_for_bit() {
    for value in [
        0.0,
        -0.0,
        f64::from_bits(1),
        f64::MIN_POSITIVE,
        f64::MAX,
        1.0 - 2.0_f64.powi(-28),
        1.0 + 2.0_f64.powi(-28),
        1.0 / 3.0,
        -1.0 / 3.0,
    ] {
        let encoded = serde_json::to_string(&value).unwrap();
        let decoded: f64 = serde_json::from_str(&encoded).unwrap();
        assert_eq!(decoded.to_bits(), value.to_bits(), "{encoded}");
    }
}
