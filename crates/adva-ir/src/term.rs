use crate::{FunctionName, IrError, ModuleName, QualifiedName};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ValueType {
    Real,
    Bool,
}

impl ValueType {
    pub fn parse(name: &str) -> Option<Self> {
        match name {
            "Real" => Some(Self::Real),
            "Bool" => Some(Self::Bool),
            _ => None,
        }
    }

    pub fn lisp_name(self) -> &'static str {
        match self {
            Self::Real => "Real",
            Self::Bool => "Bool",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Rational {
    pub numerator: i64,
    pub denominator: i64,
}

impl Rational {
    pub const ZERO: Self = Self {
        numerator: 0,
        denominator: 1,
    };
    pub const ONE: Self = Self {
        numerator: 1,
        denominator: 1,
    };

    /// Construct a reduced rational with a positive denominator.
    ///
    /// # Errors
    ///
    /// Returns [`IrError::ZeroDenominator`] for zero denominators and
    /// [`IrError::RationalOverflow`] when sign normalization cannot fit in the
    /// signed 64-bit representation.
    pub fn new(numerator: i64, denominator: i64) -> Result<Self, IrError> {
        if denominator == 0 {
            return Err(IrError::ZeroDenominator);
        }
        let mut numerator = i128::from(numerator);
        let mut denominator = i128::from(denominator);
        if denominator < 0 {
            numerator = -numerator;
            denominator = -denominator;
        }
        let divisor = gcd(numerator.abs(), denominator);
        Ok(Self {
            numerator: i64::try_from(numerator / divisor)
                .map_err(|_| IrError::RationalOverflow)?,
            denominator: i64::try_from(denominator / divisor)
                .map_err(|_| IrError::RationalOverflow)?,
        })
    }

    pub fn integer(value: i64) -> Self {
        Self {
            numerator: value,
            denominator: 1,
        }
    }

    /// Numerically realize the exact rational as an IEEE-754 scalar.
    #[allow(clippy::cast_precision_loss)]
    pub fn as_f64(self) -> f64 {
        self.numerator as f64 / self.denominator as f64
    }
}

fn gcd(mut left: i128, mut right: i128) -> i128 {
    while right != 0 {
        (left, right) = (right, left % right);
    }
    left.max(1)
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TypedPort {
    pub name: String,
    pub value_type: ValueType,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FunctionSignature {
    pub inputs: Vec<TypedPort>,
    pub outputs: Vec<ValueType>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct OperationRef {
    pub namespace: String,
    pub name: String,
    pub version: u32,
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub parameters: BTreeMap<String, Rational>,
}

impl OperationRef {
    pub fn builtin(name: impl Into<String>) -> Self {
        Self {
            namespace: "adva.builtin".to_owned(),
            name: name.into(),
            version: 1,
            parameters: BTreeMap::new(),
        }
    }

    pub fn constant(value: Rational) -> Self {
        Self {
            namespace: "adva.builtin".to_owned(),
            name: "constant".to_owned(),
            version: 1,
            parameters: BTreeMap::from([("value".to_owned(), value)]),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ProgramTerm {
    Use {
        port: String,
    },
    Constant {
        value: Rational,
    },
    Apply {
        operation: OperationRef,
        arguments: Vec<ProgramTerm>,
    },
    Call {
        function: QualifiedName,
        arguments: Vec<ProgramTerm>,
    },
    Tensor {
        terms: Vec<ProgramTerm>,
    },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FunctionDefinition {
    pub name: FunctionName,
    pub signature: FunctionSignature,
    pub body: ProgramTerm,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ModuleImport {
    pub module: ModuleName,
    pub names: Vec<FunctionName>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ModuleDefinition {
    pub name: ModuleName,
    pub imports: Vec<ModuleImport>,
    pub exports: Vec<FunctionName>,
    pub definitions: Vec<FunctionDefinition>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rational_is_normalized() {
        assert_eq!(Rational::new(6, -8).unwrap(), Rational::new(-3, 4).unwrap());
    }
}
