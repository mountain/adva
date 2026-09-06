//! Bounded exact prime-extension verification for Research 0148.
//!
//! These research artifacts neither extend `adva.ir` nor allocate semantic
//! identities. A finite certificate does not certify `Universe(Prime)` or
//! authorize native `free`. Divisibility remainders may be zero: the nonzero
//! guards of the six-word A/M witness calculus do not apply here.

use serde::{Deserialize, Serialize};

/// Version-zero finite prime-extension request schema.
pub const PRIME_EXTENSION_REQUEST_SCHEMA_V0: &str = "adva.prime-extension.request.research";
/// Version-zero finite prime-extension result schema.
pub const PRIME_EXTENSION_RESULT_SCHEMA_V0: &str = "adva.prime-extension.result.research";

/// Exact candidate data supplied by an external producer.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PrimeExtensionRequestV0 {
    /// Research request schema, distinct from `adva.ir`.
    pub schema: String,
    /// Only version zero is admitted.
    pub version: u32,
    /// At most six strictly increasing prime candidates in `2..=13`.
    pub primes: Vec<u64>,
    /// Proposed product-plus-one, at most 65535.
    pub n: u64,
    /// Proposed prime outside the input list, in `2..=65535`.
    pub q: u64,
    /// Proposed positive cofactor, at most 65535.
    pub k: u64,
    /// Logical verification allowance, at most 1024; zero is permitted.
    pub fuel: u32,
}

/// A checker-produced result with an explicit checked divisor prefix.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PrimeExtensionResultV0 {
    /// Research result schema.
    pub schema: String,
    /// Research version zero.
    pub version: u32,
    /// Exact input, absent only when decoding or input admission failed.
    pub request: Option<PrimeExtensionRequestV0>,
    /// `FiniteExtensionVerified`, `Blocked`, or `Unknown`.
    pub status: String,
    /// The completed check or retained stopping reason.
    pub reason: String,
    /// Logical checks actually charged in this invocation.
    pub fuel_spent: u32,
    /// Unused declared logical allowance.
    pub fuel_remaining: u32,
    /// Checked triples `[input_candidate, divisor, remainder]` in order.
    pub input_divisor_checks: Vec<[u64; 3]>,
    /// Checked pairs `[divisor, remainder]` for the proposed outside prime.
    pub q_divisor_checks: Vec<[u64; 2]>,
    /// Always `NotImplemented`: the universal proof remains external.
    pub native_universe: String,
    /// Always `NotGranted`: this result supplies no native free authority.
    pub native_free: String,
    /// Only a verified finite certificate may be retained as checked evidence.
    pub allowed_action: Option<String>,
}

impl PrimeExtensionResultV0 {
    fn pending(request: PrimeExtensionRequestV0) -> Self {
        Self {
            schema: PRIME_EXTENSION_RESULT_SCHEMA_V0.into(),
            version: 0,
            fuel_remaining: request.fuel,
            request: Some(request),
            status: "Unknown".into(),
            reason: "fuel exhausted before the next required check".into(),
            fuel_spent: 0,
            input_divisor_checks: Vec::new(),
            q_divisor_checks: Vec::new(),
            native_universe: "NotImplemented".into(),
            native_free: "NotGranted".into(),
            allowed_action: None,
        }
    }

    fn charge(&mut self) -> bool {
        if self.fuel_remaining == 0 {
            return false;
        }
        self.fuel_remaining -= 1;
        self.fuel_spent += 1;
        true
    }

    fn blocked(mut self, reason: &str) -> Self {
        self.status = "Blocked".into();
        self.reason = reason.into();
        self
    }
}

/// Return a refusal when there is no decodable, bounded input request.
pub fn reject_prime_extension_input_v0(reason: &str) -> PrimeExtensionResultV0 {
    PrimeExtensionResultV0 {
        schema: PRIME_EXTENSION_RESULT_SCHEMA_V0.into(),
        version: 0,
        request: None,
        status: "Blocked".into(),
        reason: reason.into(),
        fuel_spent: 0,
        fuel_remaining: 0,
        input_divisor_checks: Vec::new(),
        q_divisor_checks: Vec::new(),
        native_universe: "NotImplemented".into(),
        native_free: "NotGranted".into(),
        allowed_action: None,
    }
}

/// Check one supplied outside-prime certificate using only bounded integers.
///
/// Fuel counts the structural admission, each input admission, each divisor,
/// each product step, the successor equality, factor equality, nonmembership,
/// and final admission. Parsing and output persistence use separate fixed
/// byte bounds in the CLI; the logical ledger does not measure CPU time.
/// Two constant-time length checks precede cloning and logical metering;
/// oversized input is moved directly into a refusal without cloning it.
/// Exhaustion retains a prefix and never promotes partially checked data.
pub fn verify_prime_extension_v0(request: PrimeExtensionRequestV0) -> PrimeExtensionResultV0 {
    if request.primes.len() > 6 || request.schema.len() > 128 {
        return PrimeExtensionResultV0::pending(request)
            .blocked("request shape exceeds the fixed research profile");
    }
    let mut result = PrimeExtensionResultV0::pending(request.clone());
    if request.fuel > 1024 {
        return result.blocked("declared fuel exceeds 1024");
    }
    if !result.charge() {
        return result;
    }
    if request.schema != PRIME_EXTENSION_REQUEST_SCHEMA_V0
        || request.version != 0
        || request.primes.len() > 6
        || request.n > 65535
        || !(2..=65535).contains(&request.q)
        || !(1..=65535).contains(&request.k)
    {
        return result.blocked("request is outside the fixed research profile");
    }

    let mut product = 1_u64;
    let mut previous = 0_u64;
    for &prime in &request.primes {
        if !result.charge() {
            return result;
        }
        if !(2..=13).contains(&prime) || prime <= previous {
            return result.blocked("inputs must be strictly increasing integers in 2..=13");
        }
        previous = prime;
        for divisor in 2..prime {
            if !result.charge() {
                return result;
            }
            let remainder = prime % divisor;
            result
                .input_divisor_checks
                .push([prime, divisor, remainder]);
            if remainder == 0 {
                return result.blocked("an input candidate is composite");
            }
        }
        if !result.charge() {
            return result;
        }
        let Some(next_product) = product.checked_mul(prime) else {
            return result.blocked("checked input product overflowed");
        };
        product = next_product;
    }
    if !result.charge() {
        return result;
    }
    if product.checked_add(1) != Some(request.n) {
        return result.blocked("n differs from the exact input product plus one");
    }
    if !result.charge() {
        return result;
    }
    if request.q.checked_mul(request.k) != Some(request.n) {
        return result.blocked("q times k differs from n");
    }
    if !result.charge() {
        return result;
    }
    if request.primes.contains(&request.q) {
        return result.blocked("q is not outside the input list");
    }
    for divisor in 2..request.q {
        if !result.charge() {
            return result;
        }
        let remainder = request.q % divisor;
        result.q_divisor_checks.push([divisor, remainder]);
        if remainder == 0 {
            return result.blocked("the proposed outside prime is composite");
        }
    }
    if !result.charge() {
        return result;
    }
    result.status = "FiniteExtensionVerified".into();
    result.reason =
        "exact successor, factorization, nonmembership and prime coverage checked".into();
    result.allowed_action = Some("retain-finite-prime-certificate".into());
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    fn request(primes: &[u64], n: u64, q: u64, k: u64) -> PrimeExtensionRequestV0 {
        PrimeExtensionRequestV0 {
            schema: PRIME_EXTENSION_REQUEST_SCHEMA_V0.into(),
            version: 0,
            primes: primes.into(),
            n,
            q,
            k,
            fuel: 1024,
        }
    }

    #[test]
    fn main_certificate_checks_all_divisors_and_limits_authority() {
        let result = verify_prime_extension_v0(request(&[2, 3, 5], 31, 31, 1));
        assert_eq!(result.status, "FiniteExtensionVerified");
        assert_eq!(result.q_divisor_checks.len(), 29);
        assert_eq!(result.q_divisor_checks.last(), Some(&[30, 1]));
        assert_eq!(result.fuel_spent + result.fuel_remaining, 1024);
        assert_eq!(result.native_free, "NotGranted");
        assert_eq!(result.native_universe, "NotImplemented");
    }

    #[test]
    fn outside_prime_can_be_smaller_and_empty_input_is_valid() {
        for input in [request(&[3], 4, 2, 2), request(&[], 2, 2, 1)] {
            let result = verify_prime_extension_v0(input);
            assert_eq!(result.status, "FiniteExtensionVerified");
            assert!(result.q_divisor_checks.is_empty());
        }
    }

    #[test]
    fn composite_successor_has_a_valid_outside_prime() {
        let result = verify_prime_extension_v0(request(&[2, 3, 5, 7, 11, 13], 30031, 59, 509));
        assert_eq!(result.status, "FiniteExtensionVerified");
        assert_eq!(result.q_divisor_checks.len(), 57);
    }

    #[test]
    fn forged_factor_and_composite_claims_are_refused() {
        for input in [
            request(&[2, 3, 5], 31, 31, 2),
            request(&[4], 5, 5, 1),
            request(&[3], 4, 4, 1),
        ] {
            let result = verify_prime_extension_v0(input);
            assert_eq!(result.status, "Blocked");
            assert!(result.allowed_action.is_none());
        }
        let result = verify_prime_extension_v0(request(&[3], 4, 4, 1));
        assert_eq!(result.q_divisor_checks, vec![[2, 0]]);
    }

    #[test]
    fn zero_and_partial_fuel_retain_unknown_without_authority() {
        let mut input = request(&[2, 3, 5], 31, 31, 1);
        input.fuel = 0;
        let zero = verify_prime_extension_v0(input.clone());
        assert_eq!(zero.status, "Unknown");
        assert_eq!(zero.fuel_spent, 0);
        input.fuel = 18;
        let partial = verify_prime_extension_v0(input);
        assert_eq!(partial.status, "Unknown");
        assert_eq!(partial.fuel_spent, 18);
        assert!(!partial.q_divisor_checks.is_empty());
        assert!(partial.allowed_action.is_none());
    }

    #[test]
    fn boolean_numeric_fields_and_unknown_fields_fail_decoding() {
        let input = request(&[2, 3, 5], 31, 31, 1);
        let mut value = serde_json::to_value(&input).expect("fixture serializes");
        value["q"] = serde_json::Value::Bool(true);
        assert!(serde_json::from_value::<PrimeExtensionRequestV0>(value).is_err());
        let mut value = serde_json::to_value(input).expect("fixture serializes");
        value["native_free"] = serde_json::Value::Bool(true);
        assert!(serde_json::from_value::<PrimeExtensionRequestV0>(value).is_err());
    }
}
