use num_bigint::BigInt;
use num_traits::{One, Zero};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use thiserror::Error;

/// One variable power in a canonical commutative monomial.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VariablePowerV0 {
    pub variable: String,
    pub exponent: u32,
}

/// Canonical commutative monomial over named template holes.
#[derive(Clone, Debug, Default, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MonomialV0 {
    powers: Vec<VariablePowerV0>,
}

impl MonomialV0 {
    fn variable(name: &str) -> Result<Self, ArithmeticErrorV0> {
        if name.is_empty() {
            return Err(ArithmeticErrorV0::EmptyVariable);
        }
        Ok(Self {
            powers: vec![VariablePowerV0 {
                variable: name.to_owned(),
                exponent: 1,
            }],
        })
    }

    fn checked_multiply(&self, other: &Self) -> Result<Self, ArithmeticErrorV0> {
        let mut powers = BTreeMap::<String, u32>::new();
        for power in self.powers.iter().chain(&other.powers) {
            let current = powers.get(&power.variable).copied().unwrap_or(0);
            let exponent = current
                .checked_add(power.exponent)
                .ok_or(ArithmeticErrorV0::ExponentOverflow)?;
            powers.insert(power.variable.clone(), exponent);
        }
        Ok(Self {
            powers: powers
                .into_iter()
                .map(|(variable, exponent)| VariablePowerV0 { variable, exponent })
                .collect(),
        })
    }

    fn evaluate(&self, environment: &BTreeMap<String, BigInt>) -> Result<BigInt, ArithmeticErrorV0> {
        let mut value = BigInt::one();
        for power in &self.powers {
            let variable = environment
                .get(&power.variable)
                .ok_or_else(|| ArithmeticErrorV0::MissingVariable(power.variable.clone()))?;
            value *= variable.pow(power.exponent);
        }
        Ok(value)
    }
}

/// One nonzero term in a canonical sparse polynomial.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PolynomialTermV0 {
    pub coefficient: BigInt,
    pub monomial: MonomialV0,
}

/// Exact sparse polynomial over arbitrary-precision integer coefficients.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PolynomialV0 {
    terms: Vec<PolynomialTermV0>,
}

impl PolynomialV0 {
    #[must_use]
    pub const fn zero() -> Self {
        Self { terms: Vec::new() }
    }

    #[must_use]
    pub fn one() -> Self {
        Self::constant(BigInt::one())
    }

    #[must_use]
    pub fn constant(value: BigInt) -> Self {
        if value.is_zero() {
            Self::zero()
        } else {
            Self {
                terms: vec![PolynomialTermV0 {
                    coefficient: value,
                    monomial: MonomialV0::default(),
                }],
            }
        }
    }

    fn variable(name: &str) -> Result<Self, ArithmeticErrorV0> {
        Ok(Self {
            terms: vec![PolynomialTermV0 {
                coefficient: BigInt::one(),
                monomial: MonomialV0::variable(name)?,
            }],
        })
    }

    #[must_use]
    pub fn terms(&self) -> &[PolynomialTermV0] {
        &self.terms
    }

    #[must_use]
    pub fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    #[must_use]
    pub fn is_one(&self) -> bool {
        self == &Self::one()
    }

    fn from_map(terms: BTreeMap<MonomialV0, BigInt>) -> Self {
        Self {
            terms: terms
                .into_iter()
                .filter(|(_, coefficient)| !coefficient.is_zero())
                .map(|(monomial, coefficient)| PolynomialTermV0 {
                    coefficient,
                    monomial,
                })
                .collect(),
        }
    }

    #[must_use]
    pub fn sum(&self, other: &Self) -> Self {
        let mut terms = BTreeMap::<MonomialV0, BigInt>::new();
        for term in self.terms.iter().chain(&other.terms) {
            *terms.entry(term.monomial.clone()).or_default() += &term.coefficient;
        }
        Self::from_map(terms)
    }

    /// Multiply two exact polynomials.
    ///
    /// # Errors
    ///
    /// Returns [`ArithmeticErrorV0::ExponentOverflow`] if a variable exponent
    /// exceeds the bounded `u32` representation.
    pub fn checked_product(&self, other: &Self) -> Result<Self, ArithmeticErrorV0> {
        let mut terms = BTreeMap::<MonomialV0, BigInt>::new();
        for left in &self.terms {
            for right in &other.terms {
                let monomial = left.monomial.checked_multiply(&right.monomial)?;
                *terms.entry(monomial).or_default() += &left.coefficient * &right.coefficient;
            }
        }
        Ok(Self::from_map(terms))
    }

    /// Evaluate the canonical polynomial exactly.
    ///
    /// # Errors
    ///
    /// Returns [`ArithmeticErrorV0::MissingVariable`] when the environment is
    /// incomplete.
    pub fn evaluate(
        &self,
        environment: &BTreeMap<String, BigInt>,
    ) -> Result<BigInt, ArithmeticErrorV0> {
        let mut value = BigInt::zero();
        for term in &self.terms {
            value += &term.coefficient * term.monomial.evaluate(environment)?;
        }
        Ok(value)
    }
}

/// Pure finite add/multiply expression over exact integer atoms and holes.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ExactExprV0 {
    Constant { value: BigInt },
    Variable { name: String },
    Add {
        left: Box<Self>,
        right: Box<Self>,
    },
    Multiply {
        left: Box<Self>,
        right: Box<Self>,
    },
}

impl ExactExprV0 {
    #[must_use]
    pub fn constant(value: impl Into<BigInt>) -> Self {
        Self::Constant {
            value: value.into(),
        }
    }

    #[must_use]
    pub fn variable(name: impl Into<String>) -> Self {
        Self::Variable { name: name.into() }
    }

    #[must_use]
    pub fn sum(left: Self, right: Self) -> Self {
        Self::Add {
            left: Box::new(left),
            right: Box::new(right),
        }
    }

    #[must_use]
    pub fn product(left: Self, right: Self) -> Self {
        Self::Multiply {
            left: Box::new(left),
            right: Box::new(right),
        }
    }

    /// Normalize exactly into a sparse commutative polynomial.
    ///
    /// # Errors
    ///
    /// Returns an arithmetic error for an empty variable name or exponent
    /// overflow.
    pub fn normalize(&self) -> Result<PolynomialV0, ArithmeticErrorV0> {
        match self {
            Self::Constant { value } => Ok(PolynomialV0::constant(value.clone())),
            Self::Variable { name } => PolynomialV0::variable(name),
            Self::Add { left, right } => Ok(left.normalize()?.sum(&right.normalize()?)),
            Self::Multiply { left, right } => left
                .normalize()?
                .checked_product(&right.normalize()?),
        }
    }

    /// Evaluate exactly and reject zero at every visited expression node.
    ///
    /// # Errors
    ///
    /// Returns [`ArithmeticErrorV0::ZeroFault`] if a leaf or intermediate
    /// result is zero, and [`ArithmeticErrorV0::MissingVariable`] when a hole
    /// value is absent.
    pub fn evaluate_guarded(
        &self,
        environment: &BTreeMap<String, BigInt>,
    ) -> Result<BigInt, ArithmeticErrorV0> {
        let value = match self {
            Self::Constant { value } => value.clone(),
            Self::Variable { name } => environment
                .get(name)
                .cloned()
                .ok_or_else(|| ArithmeticErrorV0::MissingVariable(name.clone()))?,
            Self::Add { left, right } => {
                left.evaluate_guarded(environment)? + right.evaluate_guarded(environment)?
            }
            Self::Multiply { left, right } => {
                left.evaluate_guarded(environment)? * right.evaluate_guarded(environment)?
            }
        };
        if value.is_zero() {
            return Err(ArithmeticErrorV0::ZeroFault {
                expression: self.surface(),
            });
        }
        Ok(value)
    }

    #[must_use]
    pub fn surface(&self) -> String {
        match self {
            Self::Constant { value } => value.to_string(),
            Self::Variable { name } => name.clone(),
            Self::Add { left, right } => format!("({}+{})", left.surface(), right.surface()),
            Self::Multiply { left, right } => {
                format!("({}*{})", left.surface(), right.surface())
            }
        }
    }

    /// Count syntactic variable occurrences without identifying equal names
    /// with semantic occurrences.
    #[must_use]
    pub fn variable_occurrences(&self) -> BTreeMap<String, usize> {
        let mut occurrences = BTreeMap::new();
        self.accumulate_variable_occurrences(&mut occurrences);
        occurrences
    }

    fn accumulate_variable_occurrences(&self, occurrences: &mut BTreeMap<String, usize>) {
        match self {
            Self::Constant { .. } => {}
            Self::Variable { name } => {
                *occurrences.entry(name.clone()).or_default() += 1;
            }
            Self::Add { left, right } | Self::Multiply { left, right } => {
                left.accumulate_variable_occurrences(occurrences);
                right.accumulate_variable_occurrences(occurrences);
            }
        }
    }
}

/// Exact multiplicative transport residual, represented as `after / before`.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MultiplicativeResidualV0 {
    pub numerator: PolynomialV0,
    pub denominator: PolynomialV0,
}

impl MultiplicativeResidualV0 {
    #[must_use]
    pub fn identity() -> Self {
        Self {
            numerator: PolynomialV0::one(),
            denominator: PolynomialV0::one(),
        }
    }

    /// Construct an exact symbolic `after / before` residual.
    ///
    /// # Errors
    ///
    /// Rejects an identically zero side and any normalization failure.
    pub fn from_transition(
        before: &ExactExprV0,
        after: &ExactExprV0,
    ) -> Result<Self, ArithmeticErrorV0> {
        let denominator = before.normalize()?;
        let numerator = after.normalize()?;
        if denominator.is_zero() {
            return Err(ArithmeticErrorV0::ZeroPolynomial("before"));
        }
        if numerator.is_zero() {
            return Err(ArithmeticErrorV0::ZeroPolynomial("after"));
        }
        Ok(Self {
            numerator,
            denominator,
        })
    }

    /// Multiply two transport residuals exactly.
    ///
    /// # Errors
    ///
    /// Returns an arithmetic error if a monomial exponent overflows.
    pub fn checked_multiply(&self, other: &Self) -> Result<Self, ArithmeticErrorV0> {
        Ok(Self {
            numerator: self.numerator.checked_product(&other.numerator)?,
            denominator: self.denominator.checked_product(&other.denominator)?,
        })
    }

    #[must_use]
    pub fn is_one(&self) -> bool {
        self.numerator == self.denominator
    }
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum ArithmeticErrorV0 {
    #[error("template variable name must not be empty")]
    EmptyVariable,
    #[error("missing exact value for template variable {0:?}")]
    MissingVariable(String),
    #[error("monomial exponent exceeds the bounded u32 representation")]
    ExponentOverflow,
    #[error("the {0} side normalizes to the zero polynomial")]
    ZeroPolynomial(&'static str),
    #[error("multiplicative execution encountered zero at {expression}")]
    ZeroFault { expression: String },
}
