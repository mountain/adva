use crate::{FunctionName, IrError, ModuleName, QualifiedName};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::ops::Deref;

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
            numerator: i64::try_from(numerator / divisor).map_err(|_| IrError::RationalOverflow)?,
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

/// An ordered, typed open boundary without a chosen process orientation.
///
/// A frontier records only its finite port types and their order. It does not
/// imply tensor, product, source sharing, or a host-language tuple identity.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(transparent)]
pub struct TypedFrontier(Vec<ValueType>);

impl TypedFrontier {
    pub fn new(types: Vec<ValueType>) -> Self {
        Self(types)
    }

    pub fn types(&self) -> &[ValueType] {
        &self.0
    }

    pub fn into_types(self) -> Vec<ValueType> {
        self.0
    }
}

impl Deref for TypedFrontier {
    type Target = [ValueType];

    fn deref(&self) -> &Self::Target {
        self.types()
    }
}

/// The named input orientation of a typed program boundary.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(transparent)]
pub struct DomainFrontier(Vec<TypedPort>);

impl DomainFrontier {
    pub fn new(ports: Vec<TypedPort>) -> Self {
        Self(ports)
    }

    pub fn ports(&self) -> &[TypedPort] {
        &self.0
    }

    pub fn typed(&self) -> TypedFrontier {
        TypedFrontier::new(self.0.iter().map(|port| port.value_type).collect())
    }

    pub fn into_ports(self) -> Vec<TypedPort> {
        self.0
    }
}

impl Deref for DomainFrontier {
    type Target = [TypedPort];

    fn deref(&self) -> &Self::Target {
        self.ports()
    }
}

/// The output orientation of a typed program boundary.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(transparent)]
pub struct CodomainFrontier(TypedFrontier);

impl CodomainFrontier {
    pub fn new(types: Vec<ValueType>) -> Self {
        Self(TypedFrontier::new(types))
    }

    pub fn typed(&self) -> &TypedFrontier {
        &self.0
    }

    pub fn types(&self) -> &[ValueType] {
        self.0.types()
    }

    pub fn into_types(self) -> Vec<ValueType> {
        self.0.into_types()
    }
}

impl Deref for CodomainFrontier {
    type Target = [ValueType];

    fn deref(&self) -> &Self::Target {
        self.types()
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FunctionSignature {
    pub inputs: DomainFrontier,
    pub outputs: CodomainFrontier,
}

impl FunctionSignature {
    pub fn new(inputs: Vec<TypedPort>, outputs: Vec<ValueType>) -> Self {
        Self {
            inputs: DomainFrontier::new(inputs),
            outputs: CodomainFrontier::new(outputs),
        }
    }

    pub fn domain(&self) -> &DomainFrontier {
        &self.inputs
    }

    pub fn codomain(&self) -> &CodomainFrontier {
        &self.outputs
    }
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
    /// One named open occurrence supplied by the surrounding function boundary.
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
    /// Finite simultaneous substitution into another named open program.
    ///
    /// The arguments are programs, not already evaluated values. Rust checks
    /// their produced frontier against the callee's ordered open boundary
    /// before grafting the finite callee body into the shared diagram.
    Call {
        function: QualifiedName,
        arguments: Vec<ProgramTerm>,
    },
    Frontier {
        terms: Vec<ProgramTerm>,
    },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FunctionDefinition {
    pub name: FunctionName,
    /// The input ports are the ordered holes of this open program.
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

    #[test]
    fn signature_keeps_domain_and_codomain_orientations() {
        let signature = FunctionSignature::new(
            vec![TypedPort {
                name: "x".to_owned(),
                value_type: ValueType::Real,
            }],
            vec![ValueType::Bool, ValueType::Real],
        );

        assert_eq!(signature.domain().ports()[0].name, "x");
        assert_eq!(signature.domain().typed().types(), &[ValueType::Real]);
        assert_eq!(
            signature.codomain().typed().types(),
            &[ValueType::Bool, ValueType::Real]
        );
    }

    #[test]
    fn frontier_newtypes_preserve_the_version_one_json_shape() {
        let signature = FunctionSignature::new(
            vec![TypedPort {
                name: "x".to_owned(),
                value_type: ValueType::Real,
            }],
            vec![ValueType::Real],
        );

        let encoded = serde_json::to_value(signature).unwrap();
        assert_eq!(encoded["inputs"][0]["name"], "x");
        assert_eq!(encoded["inputs"][0]["value_type"], "real");
        assert_eq!(encoded["outputs"][0], "real");
    }
}
