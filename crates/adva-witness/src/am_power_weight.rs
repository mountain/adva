//! Exact rank-one rational addition/multiplication power--weight carrier.
//!
//! The native notion of a rate of change in this reading is the action of the
//! addition and multiplication generators on a power--weight carrier. It is not
//! a Jacobian, not a matrix, and not a matrix product. One carrier term is
//!
//! ```text
//! c * e^q * Phi_{nu,w},      Phi_{nu,w} = a^nu * e^{(w - nu) v}
//! ```
//!
//! with an integer addition power `nu`, rational weights `w` and `q`, and an
//! exact rational coefficient `c`. A canonical carrier element
//! ([`AmElement`]) is a finite map from the key `(nu, w, q)` to `c`; zero
//! coefficients are dropped, so equality and ordering are canonical.
//!
//! The carrier obeys the following exact laws:
//!
//! - product: `Phi_{nu,w} * Phi_{mu,z} = Phi_{nu+mu, w+z}` and
//!   `e^q * e^r = e^{q+r}`, so exp labels add and coefficients multiply;
//! - addition generator: `A(Phi_{nu,w}) = nu * Phi_{nu-1,w-1}`, and a term with
//!   `nu = 0` vanishes;
//! - multiplication generator: `M(Phi_{nu,w}) = w * Phi_{nu,w}`;
//! - eigenvalue shift: `(M - m)` acts by the exact factor `w - m`;
//! - PBW identity: `M^n A^m = A^m (M - m)^n`, checkable through
//!   [`AmElement::pbw_residual`] as an exact residual element that is zero when
//!   the identity holds.
//!
//! Every value in this module is an exact rational built from
//! [`num_bigint::BigInt`] numerator and denominator pairs. There is no floating
//! point arithmetic anywhere in this module.
//!
//! # Ordinary terms and resonant primitives
//!
//! Two primitives are undefined on a resonant stratum of the carrier: `A^{-1}`
//! at `nu = -1` and `M^{-1}` at `w = 0`. Resonance is never folded silently into
//! the base algebra. It is a typed outcome
//! ([`LogarithmicExtension`], [`JordanExtension`]) gated by a declared
//! [`ResonancePolicy`]; the default policy [`ResonancePolicy::OrdinaryOnly`]
//! fails closed with [`AmError::ResonanceUnderOrdinaryOnly`].
//!
//! # Polynomial submodule
//!
//! An element lies in the polynomial submodule exactly when every term has
//! `q = 0` and `w = nu`, so that `Phi_{nu,nu} = a^nu` and the term is the
//! monomial `c * a^nu`. Substitution ([`compose_polynomial`]) and evaluation
//! ([`evaluate_at`]) are guarded: they refuse any element outside that
//! submodule with a typed error instead of extending the reading implicitly.
//!
//! This module creates no stable API, no `ValueType`, no `OperationSpec`, no IR
//! version, no `Seal`, and no terminology home. It is a bounded exact-arithmetic
//! research reading.

use num_bigint::BigInt;
use num_traits::{One, Signed, Zero};
use std::cmp::Ordering;
use std::collections::BTreeMap;
use std::collections::btree_map::Entry;
use std::fmt;
use thiserror::Error;

/// Declared finite bound on the addition power that a polynomial reading may
/// materialize as an ascending coefficient list.
///
/// The bound exists so that reading a coefficient vector or evaluating an
/// element is a bounded operation rather than an allocation proportional to an
/// arbitrary declared power. Exceeding it is a typed error, never a panic.
pub const MAX_POLYNOMIAL_DEGREE: i64 = 4096;

/// Typed failure of an exact power--weight carrier operation.
///
/// The variants are the declared failure surface of this module. No function in
/// this module returns a partial value on failure: every failure is one of these
/// typed errors.
#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum AmError {
    /// A rational was constructed with a zero denominator.
    #[error("a rational denominator may not be zero")]
    ZeroDenominator,
    /// A division by the exact rational zero was requested.
    #[error("division by the exact rational zero")]
    DivisionByZero,
    /// A resonant primitive was requested while the policy admits only the
    /// ordinary stratum.
    #[error("{primitive} is resonant at nu = {nu}, w = {w}; OrdinaryOnly admits no extension here")]
    ResonanceUnderOrdinaryOnly {
        /// The primitive that met the resonance, either `A^-1` or `M^-1`.
        primitive: &'static str,
        /// The addition power of the resonant term.
        nu: i64,
        /// The multiplication weight of the resonant term.
        w: ExactRational,
    },
    /// Polynomial composition was requested for an element outside the
    /// polynomial submodule.
    #[error("polynomial composition needs q = 0 and w = nu in every term of both elements")]
    NonPolynomialComposition,
    /// Polynomial evaluation was requested for an element outside the
    /// polynomial submodule.
    #[error("polynomial evaluation needs q = 0 and w = nu in every term")]
    NonPolynomialEvaluation,
    /// An addition-power arithmetic step left the range of `i64`.
    #[error("addition-power arithmetic overflowed i64")]
    ExponentOverflow,
    /// A negative addition power was read as an ascending polynomial
    /// coefficient.
    #[error("nu = {nu} is a negative power and has no ascending coefficient reading")]
    NegativeExponent {
        /// The offending addition power.
        nu: i64,
    },
    /// An addition power exceeded the declared finite reading bound.
    #[error("addition power {nu} exceeds the declared reading bound {bound}")]
    DegreeBeyondBound {
        /// The offending addition power.
        nu: i64,
        /// The declared bound, [`MAX_POLYNOMIAL_DEGREE`].
        bound: i64,
    },
    /// A logarithmic extension was declared with a witness that is not
    /// strictly positive.
    #[error("the logarithmic extension needs a witness a > 0, got {witness}")]
    NonPositiveWitness {
        /// The refused witness.
        witness: ExactRational,
    },
}

/// An exact rational number, always reduced with a positive denominator.
///
/// Numerator and denominator are [`BigInt`], so no magnitude limit is imposed
/// by the host machine word size. Zero is represented as `0/1` and is the only
/// representation of zero.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ExactRational {
    numerator: BigInt,
    denominator: BigInt,
}

impl ExactRational {
    /// The exact rational zero, represented as `0/1`.
    pub fn zero() -> Self {
        Self {
            numerator: BigInt::zero(),
            denominator: BigInt::one(),
        }
    }

    /// The exact rational one, represented as `1/1`.
    pub fn one() -> Self {
        Self {
            numerator: BigInt::one(),
            denominator: BigInt::one(),
        }
    }

    /// The exact rational whose value is the integer `value`.
    pub fn integer(value: i64) -> Self {
        Self {
            numerator: BigInt::from(value),
            denominator: BigInt::one(),
        }
    }

    /// Builds a reduced rational from an arbitrary numerator and denominator.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ZeroDenominator`] when `denominator` is zero. A
    /// negative denominator is normalized onto the numerator.
    pub fn new(numerator: BigInt, denominator: BigInt) -> Result<Self, AmError> {
        if denominator.is_zero() {
            return Err(AmError::ZeroDenominator);
        }
        Ok(Self::normalize(numerator, denominator))
    }

    /// Convenience wrapper around [`ExactRational::new`] for machine-word
    /// literals.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ZeroDenominator`] when `denominator` is zero.
    pub fn from_parts(numerator: i64, denominator: i64) -> Result<Self, AmError> {
        Self::new(BigInt::from(numerator), BigInt::from(denominator))
    }

    /// Reduces a numerator/denominator pair to the canonical form.
    fn normalize(mut numerator: BigInt, mut denominator: BigInt) -> Self {
        if numerator.is_zero() {
            return Self::zero();
        }
        if denominator.is_negative() {
            numerator = -numerator;
            denominator = -denominator;
        }
        let divisor = greatest_common_divisor(&numerator, &denominator);
        if !divisor.is_one() {
            numerator /= &divisor;
            denominator /= &divisor;
        }
        Self {
            numerator,
            denominator,
        }
    }

    /// The numerator of the canonical form.
    pub fn numerator(&self) -> &BigInt {
        &self.numerator
    }

    /// The positive denominator of the canonical form.
    pub fn denominator(&self) -> &BigInt {
        &self.denominator
    }

    /// Whether the value is exactly zero.
    pub fn is_zero(&self) -> bool {
        self.numerator.is_zero()
    }

    /// Whether the value is exactly one.
    pub fn is_one(&self) -> bool {
        self.denominator.is_one() && self.numerator.is_one()
    }

    /// Whether the value is strictly positive.
    pub fn is_positive(&self) -> bool {
        self.numerator.is_positive()
    }

    /// Whether the value is an integer, that is, its denominator is one.
    pub fn is_integer(&self) -> bool {
        self.denominator.is_one()
    }

    /// The exact sum of two rationals.
    pub fn add(&self, other: &Self) -> Self {
        let numerator = &self.numerator * &other.denominator + &other.numerator * &self.denominator;
        let denominator = &self.denominator * &other.denominator;
        Self::normalize(numerator, denominator)
    }

    /// The exact product of two rationals.
    pub fn multiply(&self, other: &Self) -> Self {
        Self::normalize(
            &self.numerator * &other.numerator,
            &self.denominator * &other.denominator,
        )
    }

    /// The exact difference of two rationals.
    pub fn subtract(&self, other: &Self) -> Self {
        self.add(&other.negate())
    }

    /// The exact additive inverse.
    pub fn negate(&self) -> Self {
        Self {
            numerator: -&self.numerator,
            denominator: self.denominator.clone(),
        }
    }

    /// The exact quotient `self / other`.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::DivisionByZero`] when `other` is exactly zero.
    pub fn divide(&self, other: &Self) -> Result<Self, AmError> {
        if other.is_zero() {
            return Err(AmError::DivisionByZero);
        }
        Ok(Self::normalize(
            &self.numerator * &other.denominator,
            &self.denominator * &other.numerator,
        ))
    }

    /// The exact `exponent`-th power, with `x^0 = 1` including for `x = 0`.
    pub fn power(&self, exponent: u32) -> Self {
        let mut result = Self::one();
        let mut factor = self.clone();
        let mut remaining = exponent;
        while remaining > 0 {
            if remaining % 2 == 1 {
                result = result.multiply(&factor);
            }
            remaining /= 2;
            if remaining > 0 {
                factor = factor.multiply(&factor);
            }
        }
        result
    }

    /// A deterministic surface reading.
    ///
    /// Integers read as their numerator alone, for example `"0"` or `"2"`.
    /// Non-integers read as `"numerator/denominator"` with a positive
    /// denominator, for example `"3/8"` or `"-1/2"`.
    pub fn surface(&self) -> String {
        if self.denominator.is_one() {
            self.numerator.to_string()
        } else {
            format!("{}/{}", self.numerator, self.denominator)
        }
    }
}

impl fmt::Display for ExactRational {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.surface())
    }
}

impl Ord for ExactRational {
    fn cmp(&self, other: &Self) -> Ordering {
        // Both denominators are positive in the canonical form, so the
        // cross-product comparison is exact and total.
        (&self.numerator * &other.denominator).cmp(&(&other.numerator * &self.denominator))
    }
}

impl PartialOrd for ExactRational {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Euclid's algorithm on the absolute values of two non-zero integers.
fn greatest_common_divisor(left: &BigInt, right: &BigInt) -> BigInt {
    let mut current = left.abs();
    let mut next = right.abs();
    while !next.is_zero() {
        let remainder = &current % &next;
        current = next;
        next = remainder;
    }
    current
}

/// Canonical key of one power--weight term: `(nu, w, q)`.
///
/// The key is the whole carrier address of the term. Two terms with the same
/// key are the same carrier term and are always accumulated into one
/// coefficient.
pub type AmTermKey = (i64, ExactRational, ExactRational);

/// A canonical exact element of the rank-one rational power--weight carrier.
///
/// The element is a finite map from [`AmTermKey`] to a coefficient. Terms whose
/// exact coefficient is zero are dropped, so the representation, its equality,
/// and its ordering are canonical.
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct AmElement {
    terms: BTreeMap<AmTermKey, ExactRational>,
}

impl AmElement {
    /// The zero element, which has no terms.
    pub fn zero() -> Self {
        Self {
            terms: BTreeMap::new(),
        }
    }

    /// The multiplicative unit `1 = Phi_{0,0} = e^0`.
    pub fn one() -> Self {
        Self::constant(ExactRational::one())
    }

    /// The carrier variable `a = Phi_{1,1}`.
    ///
    /// This element lies in the polynomial submodule and is the variable that
    /// [`compose_polynomial`] and [`evaluate_at`] read.
    pub fn variable_a() -> Self {
        Self::monomial(
            1,
            ExactRational::one(),
            ExactRational::zero(),
            ExactRational::one(),
        )
    }

    /// The constant element with the exact rational value `value`.
    ///
    /// The result is the zero element when `value` is zero.
    pub fn constant(value: ExactRational) -> Self {
        Self::monomial(0, ExactRational::zero(), ExactRational::zero(), value)
    }

    /// The exp atom `e^exponent`, carried as the term `Phi_{0,0} * e^q`.
    ///
    /// An exp atom is not in the polynomial submodule unless the exponent is
    /// zero, in which case it is the constant one.
    pub fn exp_atom(exponent: ExactRational) -> Self {
        Self::monomial(0, ExactRational::zero(), exponent, ExactRational::one())
    }

    /// A single term `coefficient * e^q * Phi_{nu,w}`.
    ///
    /// A zero coefficient yields the zero element.
    pub fn monomial(
        nu: i64,
        w: ExactRational,
        q: ExactRational,
        coefficient: ExactRational,
    ) -> Self {
        let mut element = Self::zero();
        element.add_term((nu, w, q), coefficient);
        element
    }

    /// Builds an element from an arbitrary finite term sequence.
    ///
    /// Repeated keys accumulate and zero coefficients are dropped, so the
    /// result is canonical whatever order the input uses.
    pub fn from_terms<I>(terms: I) -> Self
    where
        I: IntoIterator<Item = (AmTermKey, ExactRational)>,
    {
        let mut element = Self::zero();
        for (key, coefficient) in terms {
            element.add_term(key, coefficient);
        }
        element
    }

    /// Adds `coefficient` at `key`, accumulating with any existing value and
    /// dropping the key when the exact sum is zero.
    pub fn add_term(&mut self, key: AmTermKey, coefficient: ExactRational) {
        if coefficient.is_zero() {
            return;
        }
        match self.terms.entry(key) {
            Entry::Vacant(slot) => {
                slot.insert(coefficient);
            }
            Entry::Occupied(mut slot) => {
                let sum = slot.get().add(&coefficient);
                if sum.is_zero() {
                    slot.remove();
                } else {
                    *slot.get_mut() = sum;
                }
            }
        }
    }

    /// The canonical term map, ordered by key.
    pub fn terms(&self) -> &BTreeMap<AmTermKey, ExactRational> {
        &self.terms
    }

    /// The number of non-zero terms.
    pub fn term_count(&self) -> usize {
        self.terms.len()
    }

    /// Whether the element is exactly zero.
    pub fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    /// Whether every term has `q = 0` and `w = nu`.
    ///
    /// Such an element is a rational polynomial in `a` with no `v`-dependence.
    /// This is the exact guard used by [`compose_polynomial`] and
    /// [`evaluate_at`]. A negative `nu` satisfies the shape guard but has no
    /// ascending coefficient reading and is refused separately by
    /// [`AmElement::polynomial_coefficients`].
    pub fn is_polynomial(&self) -> bool {
        self.terms
            .keys()
            .all(|(nu, w, q)| q.is_zero() && *w == ExactRational::integer(*nu))
    }

    /// The exact sum of two elements.
    pub fn add(&self, other: &Self) -> Self {
        let mut sum = self.clone();
        for (key, coefficient) in &other.terms {
            sum.add_term(key.clone(), coefficient.clone());
        }
        sum
    }

    /// The exact additive inverse.
    pub fn negate(&self) -> Self {
        let mut result = Self::zero();
        for (key, coefficient) in &self.terms {
            result.add_term(key.clone(), coefficient.negate());
        }
        result
    }

    /// The exact difference of two elements.
    pub fn subtract(&self, other: &Self) -> Self {
        self.add(&other.negate())
    }

    /// The element with every coefficient multiplied by `factor`.
    pub fn scale(&self, factor: &ExactRational) -> Self {
        let mut result = Self::zero();
        for (key, coefficient) in &self.terms {
            result.add_term(key.clone(), coefficient.multiply(factor));
        }
        result
    }

    /// The exact carrier product.
    ///
    /// The law is `Phi_{nu,w} * Phi_{mu,z} = Phi_{nu+mu, w+z}` with
    /// `e^q * e^r = e^{q+r}`: addition powers and weights add, exp labels add,
    /// and coefficients multiply.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ExponentOverflow`] when an addition-power sum leaves
    /// the range of `i64`.
    pub fn multiply(&self, other: &Self) -> Result<Self, AmError> {
        let mut product = Self::zero();
        for ((nu, w, q), left) in &self.terms {
            for ((mu, z, r), right) in &other.terms {
                let power = nu.checked_add(*mu).ok_or(AmError::ExponentOverflow)?;
                let key = (power, w.add(z), q.add(r));
                product.add_term(key, left.multiply(right));
            }
        }
        Ok(product)
    }

    /// The exact `exponent`-th carrier power, with `element^0 = 1`.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ExponentOverflow`] when an addition-power sum leaves
    /// the range of `i64`.
    pub fn power(&self, exponent: u32) -> Result<Self, AmError> {
        let mut result = Self::one();
        let mut factor = self.clone();
        let mut remaining = exponent;
        while remaining > 0 {
            if remaining % 2 == 1 {
                result = result.multiply(&factor)?;
            }
            remaining /= 2;
            if remaining > 0 {
                factor = factor.multiply(&factor)?;
            }
        }
        Ok(result)
    }

    /// The action of the addition generator: `A(Phi_{nu,w}) = nu * Phi_{nu-1,w-1}`.
    ///
    /// A term with `nu = 0` vanishes.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ExponentOverflow`] when `nu - 1` leaves the range of
    /// `i64`.
    pub fn apply_a(&self) -> Result<Self, AmError> {
        let mut image = Self::zero();
        for ((nu, w, q), coefficient) in &self.terms {
            if *nu == 0 {
                continue;
            }
            let next_nu = nu.checked_sub(1).ok_or(AmError::ExponentOverflow)?;
            let next_w = w.subtract(&ExactRational::one());
            let next_coefficient = coefficient.multiply(&ExactRational::integer(*nu));
            image.add_term((next_nu, next_w, q.clone()), next_coefficient);
        }
        Ok(image)
    }

    /// The `exponent`-fold action of the addition generator `A`.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ExponentOverflow`] when the repeated subtraction of
    /// one leaves the range of `i64`.
    pub fn apply_a_power(&self, exponent: u32) -> Result<Self, AmError> {
        let mut image = self.clone();
        for _ in 0..exponent {
            image = image.apply_a()?;
        }
        Ok(image)
    }

    /// The action of the multiplication generator: `M(Phi_{nu,w}) = w * Phi_{nu,w}`.
    ///
    /// A term with `w = 0` vanishes.
    pub fn apply_m(&self) -> Self {
        let mut image = Self::zero();
        for ((nu, w, q), coefficient) in &self.terms {
            image.add_term((*nu, w.clone(), q.clone()), coefficient.multiply(w));
        }
        image
    }

    /// The `exponent`-fold action of the multiplication generator `M`, acting
    /// by the exact factor `w^exponent`.
    pub fn apply_m_power(&self, exponent: u32) -> Self {
        let mut image = Self::zero();
        for ((nu, w, q), coefficient) in &self.terms {
            let weight = w.power(exponent);
            image.add_term((*nu, w.clone(), q.clone()), coefficient.multiply(&weight));
        }
        image
    }

    /// The action of `(M - shift)^exponent`, acting by the exact factor
    /// `(w - shift)^exponent`.
    pub fn apply_m_minus_power(&self, shift: &ExactRational, exponent: u32) -> Self {
        let mut image = Self::zero();
        for ((nu, w, q), coefficient) in &self.terms {
            let weight = w.subtract(shift).power(exponent);
            image.add_term((*nu, w.clone(), q.clone()), coefficient.multiply(&weight));
        }
        image
    }

    /// The exact residual of the PBW identity `M^n A^m = A^m (M - m)^n`.
    ///
    /// `a_power` is the declaration of `m` and `m_power` the declaration of
    /// `n`, both small finite counts. The residual is
    /// `M^n A^m(element) - A^m (M - m)^n(element)`, computed with exact
    /// generator actions; it is the zero element exactly when the identity
    /// holds on this element.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ExponentOverflow`] when an addition-power step leaves
    /// the range of `i64`. The shift `m` is read as an exact rational, so a
    /// declared count is never silently truncated.
    pub fn pbw_residual(&self, a_power: u32, m_power: u32) -> Result<Self, AmError> {
        let shift = ExactRational::integer(i64::from(a_power));
        let left = self.apply_a_power(a_power)?.apply_m_power(m_power);
        let right = self
            .apply_m_minus_power(&shift, m_power)
            .apply_a_power(a_power)?;
        Ok(left.subtract(&right))
    }

    /// The ordinary inverse action of `A` on the non-resonant stratum.
    ///
    /// For `nu != -1` the term maps to `Phi_{nu+1,w+1} / (nu+1)`. The
    /// resonant stratum `nu = -1` is typed, never folded into the base algebra.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ResonanceUnderOrdinaryOnly`] when any term has
    /// `nu = -1` and `policy` is [`ResonancePolicy::OrdinaryOnly`], which is
    /// the fail-closed default. Returns [`AmError::ExponentOverflow`] when
    /// `nu + 1` leaves the range of `i64`.
    pub fn apply_a_inverse(&self, policy: ResonancePolicy) -> Result<AdditionInverse, AmError> {
        let mut ordinary = Self::zero();
        let mut contributions: Vec<LogarithmicContribution> = Vec::new();
        for ((nu, w, q), coefficient) in &self.terms {
            if *nu == -1 {
                if policy == ResonancePolicy::OrdinaryOnly {
                    return Err(AmError::ResonanceUnderOrdinaryOnly {
                        primitive: "A^-1",
                        nu: *nu,
                        w: w.clone(),
                    });
                }
                contributions.push(LogarithmicContribution {
                    resonant_w: w.clone(),
                    exponent_label: q.clone(),
                    coefficient: coefficient.clone(),
                });
                continue;
            }
            let next_nu = nu.checked_add(1).ok_or(AmError::ExponentOverflow)?;
            let next_w = w.add(&ExactRational::one());
            let divisor = ExactRational::integer(next_nu);
            ordinary.add_term((next_nu, next_w, q.clone()), coefficient.divide(&divisor)?);
        }
        if contributions.is_empty() {
            Ok(AdditionInverse::Ordinary(ordinary))
        } else {
            Ok(AdditionInverse::Logarithmic {
                ordinary,
                extension: LogarithmicExtension {
                    witness_a: canonical_logarithmic_witness(),
                    contributions,
                },
            })
        }
    }

    /// The ordinary inverse action of `M` on the non-resonant stratum.
    ///
    /// For `w != 0` the term maps to `Phi_{nu,w} / w`. The resonant stratum
    /// `w = 0` is typed, never folded into the base algebra.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::ResonanceUnderOrdinaryOnly`] when any term has
    /// `w = 0` and `policy` is [`ResonancePolicy::OrdinaryOnly`], which is the
    /// fail-closed default. Returns [`AmError::DivisionByZero`] only if a
    /// non-resonant term were to divide by an exact zero, which the resonance
    /// branch already excludes.
    pub fn apply_m_inverse(
        &self,
        policy: ResonancePolicy,
    ) -> Result<MultiplicationInverse, AmError> {
        let mut ordinary = Self::zero();
        let mut contributions: Vec<JordanContribution> = Vec::new();
        for ((nu, w, q), coefficient) in &self.terms {
            if w.is_zero() {
                if policy == ResonancePolicy::OrdinaryOnly {
                    return Err(AmError::ResonanceUnderOrdinaryOnly {
                        primitive: "M^-1",
                        nu: *nu,
                        w: w.clone(),
                    });
                }
                contributions.push(JordanContribution {
                    nu: *nu,
                    exponent_label: q.clone(),
                    coefficient: coefficient.clone(),
                });
                continue;
            }
            ordinary.add_term((*nu, w.clone(), q.clone()), coefficient.divide(w)?);
        }
        if contributions.is_empty() {
            Ok(MultiplicationInverse::Ordinary(ordinary))
        } else {
            Ok(MultiplicationInverse::Jordan {
                ordinary,
                extension: JordanExtension { contributions },
            })
        }
    }

    /// Reads a polynomial-submodule element as its ascending coefficient list
    /// `[c_0, c_1, ...]`, where the element is `sum c_k a^k`.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::NonPolynomialEvaluation`] when the guard
    /// [`AmElement::is_polynomial`] fails, [`AmError::NegativeExponent`] when a
    /// term has a negative addition power, and [`AmError::DegreeBeyondBound`]
    /// when a power exceeds [`MAX_POLYNOMIAL_DEGREE`].
    pub fn polynomial_coefficients(&self) -> Result<Vec<ExactRational>, AmError> {
        if !self.is_polynomial() {
            return Err(AmError::NonPolynomialEvaluation);
        }
        let mut degree = 0_i64;
        for (nu, _, _) in self.terms.keys() {
            if *nu < 0 {
                return Err(AmError::NegativeExponent { nu: *nu });
            }
            if *nu > MAX_POLYNOMIAL_DEGREE {
                return Err(AmError::DegreeBeyondBound {
                    nu: *nu,
                    bound: MAX_POLYNOMIAL_DEGREE,
                });
            }
            degree = degree.max(*nu);
        }
        let mut coefficients = vec![ExactRational::zero(); degree as usize + 1];
        for ((nu, _, _), coefficient) in &self.terms {
            coefficients[*nu as usize] = coefficient.clone();
        }
        Ok(coefficients)
    }

    /// A deterministic surface reading of the element in canonical key order.
    ///
    /// Each term reads as its coefficient, then `Phi_{nu,w}` when the key is
    /// not `(0, 0)`, then `e^q` when the exp label is not zero. The zero
    /// element reads as `"0"`.
    pub fn surface(&self) -> String {
        if self.terms.is_empty() {
            return "0".to_owned();
        }
        let mut parts = Vec::with_capacity(self.terms.len());
        for ((nu, w, q), coefficient) in &self.terms {
            let mut part = coefficient.surface();
            if *nu != 0 || !w.is_zero() {
                part.push_str(&format!(" * Phi_{{{},{}}}", nu, w.surface()));
            }
            if !q.is_zero() {
                part.push_str(&format!(" * e^{}", q.surface()));
            }
            parts.push(part);
        }
        parts.join(" + ")
    }
}

/// The canonical declared positive witness `a = 1` used when a resonant
/// logarithmic extension is produced without an explicit witness.
///
/// The witness is a declaration, not a measurement: it records that the
/// extension `e^{(w+1)v} log a` is admitted on a strictly positive stratum.
/// [`LogarithmicExtension::with_witness`] re-declares a different positive
/// witness and refuses a non-positive one.
pub fn canonical_logarithmic_witness() -> ExactRational {
    ExactRational::one()
}

/// Declared policy for the two resonant primitives `A^{-1}` and `M^{-1}`.
///
/// The default is [`ResonancePolicy::OrdinaryOnly`]: resonance is a typed error
/// and the primitive fails closed.
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub enum ResonancePolicy {
    /// Only the ordinary stratum is admitted. A resonant term is a typed error.
    #[default]
    OrdinaryOnly,
    /// The resonant term is reported as its typed extension instead of being
    /// folded into the base algebra.
    DeclaredExtension,
}

/// One resonant contribution to a logarithmic extension.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LogarithmicContribution {
    /// The multiplication weight `w` of the resonant `nu = -1` term.
    resonant_w: ExactRational,
    /// The exp label `q` the resonant term carried.
    exponent_label: ExactRational,
    /// The coefficient `c` of the resonant term.
    coefficient: ExactRational,
}

impl LogarithmicContribution {
    /// The multiplication weight `w` of the resonant term.
    pub fn resonant_w(&self) -> &ExactRational {
        &self.resonant_w
    }

    /// The declared exponent weight `w + 1` of the extension `e^{(w+1)v} log a`.
    pub fn extension_weight(&self) -> ExactRational {
        self.resonant_w.add(&ExactRational::one())
    }

    /// The exp label of the resonant term.
    pub fn exponent_label(&self) -> &ExactRational {
        &self.exponent_label
    }

    /// The coefficient of the resonant term.
    pub fn coefficient(&self) -> &ExactRational {
        &self.coefficient
    }
}

/// Typed outcome of the resonant addition primitive `A^{-1}` at `nu = -1`.
///
/// The extension is `c * e^q * e^{(w+1)v} * log a`, admitted only on the
/// declared stratum `a > 0` that the carried witness names. The extension is
/// not an element of the base power--weight algebra.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LogarithmicExtension {
    witness_a: ExactRational,
    contributions: Vec<LogarithmicContribution>,
}

impl LogarithmicExtension {
    /// The required positive witness `a > 0`.
    pub fn witness_a(&self) -> &ExactRational {
        &self.witness_a
    }

    /// The resonant contributions, in canonical key order.
    pub fn contributions(&self) -> &[LogarithmicContribution] {
        &self.contributions
    }

    /// A copy of this extension carrying a different declared witness.
    ///
    /// # Errors
    ///
    /// Returns [`AmError::NonPositiveWitness`] when `witness_a` is not strictly
    /// positive. The witness is a declaration `a > 0`, so it is never silently
    /// defaulted or dropped.
    pub fn with_witness(&self, witness_a: ExactRational) -> Result<Self, AmError> {
        if !witness_a.is_positive() {
            return Err(AmError::NonPositiveWitness { witness: witness_a });
        }
        Ok(Self {
            witness_a,
            contributions: self.contributions.clone(),
        })
    }

    /// A deterministic surface reading, including the positive witness.
    pub fn surface(&self) -> String {
        let parts: Vec<String> = self
            .contributions
            .iter()
            .map(|contribution| {
                format!(
                    "{} * e^({} * v) * log(a){}",
                    contribution.coefficient.surface(),
                    contribution.extension_weight().surface(),
                    if contribution.exponent_label.is_zero() {
                        String::new()
                    } else {
                        format!(" * e^{}", contribution.exponent_label.surface())
                    }
                )
            })
            .collect();
        format!(
            "{} with witness a = {}",
            parts.join(" + "),
            self.witness_a.surface()
        )
    }
}

/// Typed outcome of the resonant multiplication primitive `M^{-1}` at `w = 0`.
///
/// The extension is `c * e^q * v * Phi_{nu,0}`, admitted only on the declared
/// Jordan stratum. The extension is not an element of the base power--weight
/// algebra.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct JordanExtension {
    contributions: Vec<JordanContribution>,
}

impl JordanExtension {
    /// The resonant contributions, in canonical key order.
    pub fn contributions(&self) -> &[JordanContribution] {
        &self.contributions
    }

    /// A deterministic surface reading.
    pub fn surface(&self) -> String {
        let parts: Vec<String> = self
            .contributions
            .iter()
            .map(|contribution| {
                format!(
                    "{} * v * Phi_{{{},0}}{}",
                    contribution.coefficient.surface(),
                    contribution.nu,
                    if contribution.exponent_label.is_zero() {
                        String::new()
                    } else {
                        format!(" * e^{}", contribution.exponent_label.surface())
                    }
                )
            })
            .collect();
        parts.join(" + ")
    }
}

/// One resonant contribution to a Jordan extension.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct JordanContribution {
    /// The addition power `nu` of the resonant `w = 0` term.
    nu: i64,
    /// The exp label `q` the resonant term carried.
    exponent_label: ExactRational,
    /// The coefficient `c` of the resonant term.
    coefficient: ExactRational,
}

impl JordanContribution {
    /// The addition power `nu` of the resonant term.
    pub fn nu(&self) -> i64 {
        self.nu
    }

    /// The exp label of the resonant term.
    pub fn exponent_label(&self) -> &ExactRational {
        &self.exponent_label
    }

    /// The coefficient of the resonant term.
    pub fn coefficient(&self) -> &ExactRational {
        &self.coefficient
    }
}

/// Typed outcome of [`AmElement::apply_a_inverse`].
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum AdditionInverse {
    /// Every non-resonant term admitted the ordinary primitive.
    Ordinary(AmElement),
    /// The ordinary part of the non-resonant terms, together with the typed
    /// logarithmic extension of the resonant `nu = -1` part.
    Logarithmic {
        /// The ordinary preimage of the non-resonant terms.
        ordinary: AmElement,
        /// The typed extension of the resonant terms.
        extension: LogarithmicExtension,
    },
}

/// Typed outcome of [`AmElement::apply_m_inverse`].
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum MultiplicationInverse {
    /// Every non-resonant term admitted the ordinary primitive.
    Ordinary(AmElement),
    /// The ordinary part of the non-resonant terms, together with the typed
    /// Jordan extension of the resonant `w = 0` part.
    Jordan {
        /// The ordinary preimage of the non-resonant terms.
        ordinary: AmElement,
        /// The typed extension of the resonant terms.
        extension: JordanExtension,
    },
}

/// Substitutes `inner` into `outer`, computing `outer(inner)` in the carrier.
///
/// # Errors
///
/// Both elements must lie in the polynomial submodule: every term of both must
/// have `q = 0` and `w = nu`. Otherwise this returns
/// [`AmError::NonPolynomialComposition`] and no partial result. A term with a
/// negative addition power has no polynomial power and returns
/// [`AmError::NegativeExponent`]; an addition-power sum outside `i64` returns
/// [`AmError::ExponentOverflow`].
///
/// The guard is the reason a `v`-carrying or exp-carrying element is never
/// substituted implicitly: substitution is defined on the polynomial submodule
/// only, and the caller must ask for any wider reading elsewhere.
pub fn compose_polynomial(outer: &AmElement, inner: &AmElement) -> Result<AmElement, AmError> {
    if !outer.is_polynomial() || !inner.is_polynomial() {
        return Err(AmError::NonPolynomialComposition);
    }
    let mut result = AmElement::zero();
    for ((nu, _, _), coefficient) in outer.terms() {
        let exponent = u32::try_from(*nu).map_err(|_| {
            if *nu < 0 {
                AmError::NegativeExponent { nu: *nu }
            } else {
                AmError::ExponentOverflow
            }
        })?;
        let powered = inner.power(exponent)?;
        result = result.add(&powered.scale(coefficient));
    }
    Ok(result)
}

/// Evaluates a polynomial-submodule element at the exact rational `a_value`.
///
/// # Errors
///
/// Returns [`AmError::NonPolynomialEvaluation`] when the guard
/// [`AmElement::is_polynomial`] fails, [`AmError::DivisionByZero`] when a
/// negative addition power meets `a_value = 0`, and
/// [`AmError::DegreeBeyondBound`] when a power exceeds
/// [`MAX_POLYNOMIAL_DEGREE`].
pub fn evaluate_at(element: &AmElement, a_value: &ExactRational) -> Result<ExactRational, AmError> {
    if !element.is_polynomial() {
        return Err(AmError::NonPolynomialEvaluation);
    }
    let mut total = ExactRational::zero();
    for ((nu, _, _), coefficient) in element.terms() {
        let value = if *nu >= 0 {
            a_value.power(u32::try_from(*nu).map_err(|_| AmError::DegreeBeyondBound {
                nu: *nu,
                bound: MAX_POLYNOMIAL_DEGREE,
            })?)
        } else {
            let magnitude = nu.checked_neg().ok_or(AmError::ExponentOverflow)?;
            ExactRational::one().divide(&a_value.power(u32::try_from(magnitude).map_err(
                |_| AmError::DegreeBeyondBound {
                    nu: *nu,
                    bound: MAX_POLYNOMIAL_DEGREE,
                },
            )?))?
        };
        total = total.add(&coefficient.multiply(&value));
    }
    Ok(total)
}

/// An exact affine step `x -> dilation * x + translation`.
///
/// # Chronological composition
///
/// [`AffineStep::then`] is chronological: applying `step.then(next)` equals
/// applying `step` first and then applying `next`. Written in the normal form
/// `T_b D_k`, where `D_k` scales by `k` and `T_b` then translates by `b`, the
/// chronological composite of `T_b D_k` followed by `T_c D_ell` is
/// `T_{c + ell*b} D_{ell*k}`.
///
/// The transposed parameter reading `(b + k*c, k*ell)` is the composite of the
/// same two normal forms in the opposite chronological order, that is with
/// `next` applied first: `T_b D_k` after `T_c D_ell` gives the pair
/// `(b + k*c, k*ell)`. The two readings are recorded together so that the
/// order convention is never left implicit; the chronological law above is the
/// one this type implements and tests.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AffineStep {
    /// The dilation factor applied first.
    pub dilation: ExactRational,
    /// The translation applied after the dilation.
    pub translation: ExactRational,
}

impl AffineStep {
    /// The step `x -> dilation * x + translation`.
    pub fn new(dilation: ExactRational, translation: ExactRational) -> Self {
        Self {
            dilation,
            translation,
        }
    }

    /// The identity step `x -> x`.
    pub fn identity() -> Self {
        Self::new(ExactRational::one(), ExactRational::zero())
    }

    /// Applies the step to an exact rational value.
    pub fn apply(&self, value: &ExactRational) -> ExactRational {
        self.dilation.multiply(value).add(&self.translation)
    }

    /// The chronological composite: `self` first, then `next`.
    ///
    /// With `self = T_b D_k` and `next = T_c D_ell` the result is
    /// `T_{c + ell*b} D_{ell*k}`.
    pub fn then(&self, next: &Self) -> Self {
        Self {
            dilation: next.dilation.multiply(&self.dilation),
            translation: next
                .translation
                .add(&next.dilation.multiply(&self.translation)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A test-only exact rational constructor.
    fn rational(numerator: i64, denominator: i64) -> ExactRational {
        ExactRational::from_parts(numerator, denominator).expect("declared test rational")
    }

    #[test]
    fn rationals_reduce_with_a_positive_denominator() -> Result<(), AmError> {
        assert_eq!(ExactRational::new(2.into(), 4.into())?, rational(1, 2));
        assert_eq!(
            ExactRational::new((-1).into(), (-2).into())?,
            rational(1, 2)
        );
        assert_eq!(ExactRational::new(1.into(), (-2).into())?, rational(-1, 2));
        assert_eq!(rational(0, 7), ExactRational::zero());
        assert_eq!(rational(0, 7).surface(), "0");
        assert_eq!(rational(3, 8).surface(), "3/8");
        assert_eq!(rational(1, -2).surface(), "-1/2");
        assert_eq!(rational(-6, -3).surface(), "2");
        assert_eq!(rational(3, 8).numerator(), &BigInt::from(3));
        assert_eq!(rational(3, 8).denominator(), &BigInt::from(8));
        assert!(rational(1, 2).is_positive());
        assert!(!rational(-1, 2).is_positive());
        assert!(rational(4, 2).is_integer());
        assert!(!rational(1, 2).is_integer());
        assert!(ExactRational::one().is_one());
        assert_eq!(rational(2, 3).add(&rational(1, 6)), rational(5, 6));
        assert_eq!(rational(2, 3).multiply(&rational(3, 4)), rational(1, 2));
        assert_eq!(rational(2, 3).negate(), rational(-2, 3));
        assert_eq!(rational(2, 3).divide(&rational(4, 9))?, rational(3, 2));
        assert_eq!(rational(-2, 3).power(3), rational(-8, 27));
        assert_eq!(ExactRational::zero().power(0), ExactRational::one());
        assert_eq!(rational(2, 3).subtract(&rational(5, 6)), rational(-1, 6));
        assert_eq!(
            ExactRational::new(1.into(), 0.into()),
            Err(AmError::ZeroDenominator)
        );
        assert_eq!(
            rational(1, 2).divide(&ExactRational::zero()),
            Err(AmError::DivisionByZero)
        );
        assert!(rational(1, 3) < rational(1, 2));
        assert!(rational(-1, 2) < rational(-1, 3));
        Ok(())
    }

    #[test]
    fn product_law_adds_powers_weights_and_exp_labels() -> Result<(), AmError> {
        let left = AmElement::monomial(2, rational(3, 2), rational(1, 3), rational(1, 2));
        let right = AmElement::monomial(5, rational(-1, 2), rational(2, 3), rational(-3, 4));
        assert_eq!(
            left.multiply(&right)?,
            AmElement::monomial(7, rational(1, 1), rational(1, 1), rational(-3, 8))
        );
        // A term with a zero coefficient is dropped, so zero is canonical.
        assert!(AmElement::monomial(1, rational(1, 1), rational(0, 1), rational(0, 1)).is_zero());
        assert!(AmElement::zero().is_zero());
        // The product is bilinear and the unit is Phi_{0,0}.
        let mixed = AmElement::from_terms([
            ((1, rational(1, 1), rational(0, 1)), rational(3, 4)),
            ((2, rational(2, 1), rational(1, 5)), rational(-1, 3)),
        ]);
        assert_eq!(AmElement::one().multiply(&mixed)?, mixed);
        assert_eq!(
            mixed.multiply(&AmElement::variable_a())?,
            AmElement::from_terms([
                ((2, rational(2, 1), rational(0, 1)), rational(3, 4)),
                ((3, rational(3, 1), rational(1, 5)), rational(-1, 3)),
            ])
        );
        assert_eq!(
            mixed.add(&mixed.negate()),
            AmElement::zero(),
            "additive inverses cancel exactly"
        );
        Ok(())
    }

    #[test]
    fn exp_labels_add_and_the_polynomial_module_refuses_them() -> Result<(), AmError> {
        let product =
            AmElement::exp_atom(rational(1, 2)).multiply(&AmElement::exp_atom(rational(-1, 3)))?;
        assert_eq!(product, AmElement::exp_atom(rational(1, 6)));
        assert_eq!(product.term_count(), 1);
        assert!(!product.is_polynomial());
        assert_eq!(
            product.polynomial_coefficients(),
            Err(AmError::NonPolynomialEvaluation)
        );
        let scaled = AmElement::exp_atom(rational(1, 2))
            .scale(&rational(2, 1))
            .multiply(&AmElement::exp_atom(rational(-1, 3)).scale(&rational(3, 1)))?;
        assert_eq!(
            scaled,
            AmElement::exp_atom(rational(1, 6)).scale(&rational(6, 1))
        );
        assert_eq!(
            AmElement::exp_atom(rational(0, 1)),
            AmElement::one(),
            "the zero exp label is the multiplicative unit"
        );
        Ok(())
    }

    #[test]
    fn generators_act_by_power_and_weight() -> Result<(), AmError> {
        let element = AmElement::monomial(3, rational(5, 2), rational(1, 4), rational(2, 3));
        assert_eq!(
            element.apply_a()?,
            AmElement::monomial(2, rational(3, 2), rational(1, 4), rational(2, 1))
        );
        assert_eq!(
            element.apply_m(),
            AmElement::monomial(3, rational(5, 2), rational(1, 4), rational(5, 3))
        );
        assert!(
            AmElement::monomial(0, rational(1, 3), rational(1, 7), rational(5, 2))
                .apply_a()?
                .is_zero(),
            "a term with nu = 0 vanishes under A"
        );
        assert!(
            AmElement::monomial(4, rational(0, 1), rational(1, 7), rational(5, 2))
                .apply_m()
                .is_zero(),
            "a term with w = 0 vanishes under M"
        );
        assert_eq!(element.apply_a_power(0)?, element);
        assert_eq!(element.apply_m_power(0), element);
        assert_eq!(
            element.apply_a_power(3)?,
            element.apply_a()?.apply_a()?.apply_a()?
        );
        assert_eq!(
            element.apply_m_minus_power(&rational(1, 4), 2),
            element.scale(&rational(81, 16)),
            "(M - 1/4)^2 acts by (5/2 - 1/4)^2 = 81/16 on this term"
        );
        Ok(())
    }

    #[test]
    fn pbw_identity_has_zero_residual_and_a_nonzero_wrong_control() -> Result<(), AmError> {
        let element = AmElement::from_terms([
            ((5, rational(3, 2), rational(1, 3)), rational(2, 3)),
            ((2, rational(1, 2), rational(-1, 5)), rational(-7, 4)),
            ((0, rational(0, 1), rational(1, 2)), rational(5, 1)),
        ]);
        for (a_power, m_power) in [(1_u32, 1_u32), (2, 3), (3, 2), (4, 4)] {
            assert!(
                element.pbw_residual(a_power, m_power)?.is_zero(),
                "M^{m_power} A^{a_power} = A^{a_power} (M - {a_power})^{m_power}"
            );
        }
        // Negative control: dropping the shift leaves a nonzero residual, so the
        // residual is a real check and not a tautology.
        let unshifted = element
            .apply_a_power(2)?
            .apply_m_power(2)
            .subtract(&element.apply_m_power(2).apply_a_power(2)?);
        assert!(!unshifted.is_zero());
        // Negative control: the generators do not commute, M A - A M = -nu ...
        let commutator = element
            .apply_a()?
            .apply_m()
            .subtract(&element.apply_m().apply_a()?);
        assert!(!commutator.is_zero());
        Ok(())
    }

    #[test]
    fn resonances_are_typed_under_both_policies() -> Result<(), AmError> {
        let resonant_a = AmElement::monomial(-1, rational(2, 1), rational(1, 3), rational(-3, 4));
        assert_eq!(
            resonant_a.apply_a_inverse(ResonancePolicy::OrdinaryOnly),
            Err(AmError::ResonanceUnderOrdinaryOnly {
                primitive: "A^-1",
                nu: -1,
                w: rational(2, 1),
            })
        );
        let declared = resonant_a.apply_a_inverse(ResonancePolicy::DeclaredExtension)?;
        match declared {
            AdditionInverse::Logarithmic {
                ordinary,
                extension,
            } => {
                assert!(ordinary.is_zero());
                assert_eq!(extension.witness_a(), &rational(1, 1));
                assert!(extension.witness_a().is_positive());
                assert_eq!(extension.contributions().len(), 1);
                let contribution = &extension.contributions()[0];
                assert_eq!(contribution.resonant_w(), &rational(2, 1));
                assert_eq!(contribution.extension_weight(), rational(3, 1));
                assert_eq!(contribution.exponent_label(), &rational(1, 3));
                assert_eq!(contribution.coefficient(), &rational(-3, 4));
                assert!(extension.surface().contains("log(a)"));
                assert!(
                    extension
                        .with_witness(rational(0, 1))
                        .is_err_and(|error| matches!(error, AmError::NonPositiveWitness { .. }))
                );
                assert!(extension.with_witness(rational(-1, 4)).is_err());
                assert_eq!(
                    extension.with_witness(rational(5, 1))?.witness_a(),
                    &rational(5, 1)
                );
            }
            AdditionInverse::Ordinary(_) => panic!("expected a logarithmic extension"),
        }
        // The non-resonant stratum stays ordinary and exact.
        assert_eq!(
            AmElement::monomial(2, rational(5, 2), rational(0, 1), rational(3, 4))
                .apply_a_inverse(ResonancePolicy::OrdinaryOnly)?,
            AdditionInverse::Ordinary(AmElement::monomial(
                3,
                rational(7, 2),
                rational(0, 1),
                rational(1, 4)
            ))
        );

        let resonant_m = AmElement::monomial(2, rational(0, 1), rational(1, 5), rational(7, 2));
        assert_eq!(
            resonant_m.apply_m_inverse(ResonancePolicy::OrdinaryOnly),
            Err(AmError::ResonanceUnderOrdinaryOnly {
                primitive: "M^-1",
                nu: 2,
                w: rational(0, 1),
            })
        );
        match resonant_m.apply_m_inverse(ResonancePolicy::DeclaredExtension)? {
            MultiplicationInverse::Jordan {
                ordinary,
                extension,
            } => {
                assert!(ordinary.is_zero());
                assert_eq!(extension.contributions().len(), 1);
                let contribution = &extension.contributions()[0];
                assert_eq!(contribution.nu(), 2);
                assert_eq!(contribution.exponent_label(), &rational(1, 5));
                assert_eq!(contribution.coefficient(), &rational(7, 2));
                assert!(extension.surface().contains("v * Phi_{2,0}"));
            }
            MultiplicationInverse::Ordinary(_) => panic!("expected a Jordan extension"),
        }
        assert_eq!(
            AmElement::monomial(1, rational(3, 4), rational(0, 1), rational(5, 2))
                .apply_m_inverse(ResonancePolicy::OrdinaryOnly)?,
            MultiplicationInverse::Ordinary(AmElement::monomial(
                1,
                rational(3, 4),
                rational(0, 1),
                rational(10, 3)
            ))
        );
        assert_eq!(ResonancePolicy::default(), ResonancePolicy::OrdinaryOnly);
        Ok(())
    }

    #[test]
    fn polynomial_guard_refuses_a_v_carrying_element() -> Result<(), AmError> {
        // Phi_{0,1} = e^v carries v-dependence and is not a polynomial.
        let carrying_v = AmElement::monomial(0, rational(1, 1), rational(0, 1), rational(1, 1));
        assert_eq!(
            carrying_v,
            AmElement::exp_atom(rational(0, 1)).multiply(&carrying_v)?
        );
        assert!(!carrying_v.is_polynomial());
        assert_eq!(
            evaluate_at(&carrying_v, &rational(1, 1)),
            Err(AmError::NonPolynomialEvaluation)
        );
        assert_eq!(
            compose_polynomial(&carrying_v, &AmElement::variable_a()),
            Err(AmError::NonPolynomialComposition)
        );
        assert_eq!(
            compose_polynomial(&AmElement::variable_a(), &carrying_v),
            Err(AmError::NonPolynomialComposition)
        );
        assert_eq!(
            carrying_v.polynomial_coefficients(),
            Err(AmError::NonPolynomialEvaluation)
        );

        // Composition and evaluation on the polynomial submodule stay exact.
        let outer = AmElement::variable_a().power(2)?.add(&AmElement::one());
        let inner = AmElement::variable_a().add(&AmElement::constant(rational(3, 1)));
        let composed = compose_polynomial(&outer, &inner)?;
        assert_eq!(
            composed.polynomial_coefficients()?,
            vec![rational(10, 1), rational(6, 1), rational(1, 1)]
        );
        assert_eq!(evaluate_at(&composed, &rational(1, 2))?, rational(53, 4));
        assert_eq!(evaluate_at(&outer, &rational(0, 1))?, rational(1, 1));
        assert!(composed.is_polynomial());

        // A negative power passes the shape guard but has no polynomial reading.
        let inverse_power =
            AmElement::monomial(-1, rational(-1, 1), rational(0, 1), rational(1, 1));
        assert!(inverse_power.is_polynomial());
        assert_eq!(
            inverse_power.polynomial_coefficients(),
            Err(AmError::NegativeExponent { nu: -1 })
        );
        assert_eq!(
            evaluate_at(&inverse_power, &ExactRational::zero()),
            Err(AmError::DivisionByZero)
        );
        assert_eq!(
            evaluate_at(&inverse_power, &rational(2, 1))?,
            rational(1, 2)
        );
        assert_eq!(
            compose_polynomial(&inverse_power, &AmElement::variable_a()),
            Err(AmError::NegativeExponent { nu: -1 })
        );
        Ok(())
    }

    #[test]
    fn exponent_overflow_is_typed_and_not_a_panic() -> Result<(), AmError> {
        let top = AmElement::monomial(
            i64::MAX,
            ExactRational::integer(i64::MAX),
            rational(0, 1),
            rational(1, 1),
        );
        assert_eq!(
            top.multiply(&AmElement::variable_a()),
            Err(AmError::ExponentOverflow)
        );
        assert_eq!(
            top.apply_a_inverse(ResonancePolicy::OrdinaryOnly),
            Err(AmError::ExponentOverflow)
        );
        let bottom = AmElement::monomial(
            i64::MIN,
            ExactRational::integer(i64::MIN),
            rational(0, 1),
            rational(1, 1),
        );
        assert_eq!(bottom.apply_a(), Err(AmError::ExponentOverflow));
        assert_eq!(
            AmElement::monomial(
                MAX_POLYNOMIAL_DEGREE + 1,
                ExactRational::integer(MAX_POLYNOMIAL_DEGREE + 1),
                rational(0, 1),
                rational(1, 1)
            )
            .polynomial_coefficients(),
            Err(AmError::DegreeBeyondBound {
                nu: MAX_POLYNOMIAL_DEGREE + 1,
                bound: MAX_POLYNOMIAL_DEGREE,
            })
        );
        Ok(())
    }

    #[test]
    fn affine_composition_is_chronological_and_order_sensitive() -> Result<(), AmError> {
        let step = AffineStep::new(rational(2, 3), rational(1, 2));
        let next = AffineStep::new(rational(5, 4), rational(-1, 3));
        let chronological = step.then(&next);
        assert_eq!(chronological.dilation, rational(5, 6));
        assert_eq!(chronological.translation, rational(7, 24));
        for numerator in -6..=6 {
            let value = rational(numerator, 7);
            assert_eq!(
                chronological.apply(&value),
                next.apply(&step.apply(&value)),
                "step.then(next) applies step first and then next"
            );
        }
        assert_eq!(step.then(&AffineStep::identity()), step);
        assert_eq!(AffineStep::identity().then(&step), step);
        assert_eq!(step.apply(&rational(0, 1)), rational(1, 2));

        // Negative control: the wrong order differs, both as a step and as a map.
        let reversed = next.then(&step);
        assert_ne!(reversed, chronological);
        assert_ne!(
            reversed.apply(&rational(0, 1)),
            chronological.apply(&rational(0, 1))
        );
        assert_eq!(reversed.translation, rational(5, 18));
        Ok(())
    }

    #[test]
    fn surface_readings_are_deterministic() {
        assert_eq!(AmElement::zero().surface(), "0");
        assert_eq!(AmElement::variable_a().surface(), "1 * Phi_{1,1}");
        assert_eq!(
            AmElement::from_terms([
                ((2, rational(2, 1), rational(0, 1)), rational(1, 8)),
                ((1, rational(1, 1), rational(0, 1)), rational(3, 8)),
            ])
            .surface(),
            "3/8 * Phi_{1,1} + 1/8 * Phi_{2,2}"
        );
        assert_eq!(AmElement::exp_atom(rational(1, 6)).surface(), "1 * e^1/6");
    }
}
