use crate::LispError;
use adva_ir::{OperationRef, Rational, ValueType, WireRef};
use std::collections::BTreeMap;

pub const BUILTIN_NAMESPACE: &str = "adva.builtin";
pub const BUILTIN_VERSION: u32 = 1;

const NO_TYPES: &[ValueType] = &[];
const ONE_REAL: &[ValueType] = &[ValueType::Real];
const TWO_REALS: &[ValueType] = &[ValueType::Real, ValueType::Real];
const NO_PARAMETERS: &[&str] = &[];
const VALUE_PARAMETER: &[&str] = &["value"];

/// How an operation transports source occurrences through its output wires.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LineageRule {
    /// Concatenate the input lineages and attach them to every output.
    MergeInputs,
    /// Create two fresh occurrence paths for every input occurrence.
    Copy,
    /// Consume the lineage without producing an output.
    Discard,
    /// Exchange two lineages without identifying them.
    Swap,
}

type DualEvaluator = fn(&BTreeMap<String, Rational>, &[Dual]) -> Result<Vec<Dual>, LispError>;

/// One versioned declaration of an operation's syntax, boundary, geometry, and
/// scalar differential realization.
#[derive(Clone, Debug)]
pub struct OperationSpec {
    pub namespace: &'static str,
    pub name: &'static str,
    pub version: u32,
    pub surface_form: bool,
    pub input_types: &'static [ValueType],
    pub output_types: &'static [ValueType],
    pub parameters: &'static [&'static str],
    pub lineage_rule: LineageRule,
    evaluator: DualEvaluator,
}

impl OperationSpec {
    pub fn rule_id(&self) -> String {
        format!("{}:{}@{}", self.namespace, self.name, self.version)
    }

    pub fn validate_reference(&self, operation: &OperationRef) -> Result<(), LispError> {
        let actual = operation
            .parameters
            .keys()
            .map(String::as_str)
            .collect::<Vec<_>>();
        if actual.as_slice() == self.parameters {
            Ok(())
        } else {
            Err(LispError::Type(format!(
                "operation {} expects parameters {:?}, got {actual:?}",
                self.rule_id(),
                self.parameters
            )))
        }
    }

    pub fn validate_wires(&self, inputs: &[WireRef]) -> Result<(), LispError> {
        let actual = inputs
            .iter()
            .map(|wire| wire.value_type)
            .collect::<Vec<_>>();
        if actual.as_slice() == self.input_types {
            Ok(())
        } else {
            Err(LispError::Type(format!(
                "operation {} expects inputs {:?}, got {actual:?}",
                self.rule_id(),
                self.input_types
            )))
        }
    }

    pub fn validate_outputs(&self, outputs: &[ValueType]) -> Result<(), LispError> {
        if outputs == self.output_types {
            Ok(())
        } else {
            Err(LispError::Type(format!(
                "operation {} declares outputs {:?}, got {outputs:?}",
                self.rule_id(),
                self.output_types
            )))
        }
    }

    fn validate_lineage_shape(&self) -> Result<(), LispError> {
        let valid = match self.lineage_rule {
            LineageRule::MergeInputs => true,
            LineageRule::Copy => self.input_types.len() == 1 && self.output_types.len() == 2,
            LineageRule::Discard => self.input_types.len() == 1 && self.output_types.is_empty(),
            LineageRule::Swap => self.input_types.len() == 2 && self.output_types.len() == 2,
        };
        if valid {
            Ok(())
        } else {
            Err(LispError::Type(format!(
                "operation {} has a boundary incompatible with lineage rule {:?}",
                self.rule_id(),
                self.lineage_rule
            )))
        }
    }

    pub(crate) fn evaluate(
        &self,
        parameters: &BTreeMap<String, Rational>,
        arguments: &[Dual],
    ) -> Result<Vec<Dual>, LispError> {
        (self.evaluator)(parameters, arguments)
    }
}

/// A scalar value together with its structural forward differential.
#[derive(Clone, Debug)]
pub(crate) struct Dual {
    pub value: f64,
    pub gradient: BTreeMap<String, f64>,
}

static BUILTIN_OPERATIONS: &[OperationSpec] = &[
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "constant",
        version: BUILTIN_VERSION,
        surface_form: false,
        input_types: NO_TYPES,
        output_types: ONE_REAL,
        parameters: VALUE_PARAMETER,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_constant,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "id",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_identity,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "copy",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: TWO_REALS,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::Copy,
        evaluator: evaluate_copy,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "discard",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: NO_TYPES,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::Discard,
        evaluator: evaluate_discard,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "swap",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: TWO_REALS,
        output_types: TWO_REALS,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::Swap,
        evaluator: evaluate_swap,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "add",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: TWO_REALS,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_add,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "mul",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: TWO_REALS,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_product,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "scale",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: TWO_REALS,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_product,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "neg",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_negation,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "sin",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_sine,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "cos",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_cosine,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "exp",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_exponential,
    },
    OperationSpec {
        namespace: BUILTIN_NAMESPACE,
        name: "log",
        version: BUILTIN_VERSION,
        surface_form: true,
        input_types: ONE_REAL,
        output_types: ONE_REAL,
        parameters: NO_PARAMETERS,
        lineage_rule: LineageRule::MergeInputs,
        evaluator: evaluate_logarithm,
    },
];

pub fn builtin_operation_specs() -> &'static [OperationSpec] {
    BUILTIN_OPERATIONS
}

pub fn builtin_surface_form(name: &str) -> bool {
    BUILTIN_OPERATIONS
        .iter()
        .any(|spec| spec.surface_form && spec.name == name)
}

pub fn resolve_operation(operation: &OperationRef) -> Result<&'static OperationSpec, LispError> {
    let spec = BUILTIN_OPERATIONS
        .iter()
        .find(|spec| {
            spec.namespace == operation.namespace
                && spec.name == operation.name
                && spec.version == operation.version
        })
        .ok_or_else(|| {
            LispError::Type(format!(
                "unsupported operation {}:{} v{}",
                operation.namespace, operation.name, operation.version
            ))
        })?;
    spec.validate_lineage_shape()?;
    spec.validate_reference(operation)?;
    Ok(spec)
}

fn evaluate_constant(
    parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    ensure_argument_count("constant", arguments, 0)?;
    let value = parameters
        .get("value")
        .expect("registry validation requires the constant value parameter");
    Ok(vec![Dual {
        value: value.as_f64(),
        gradient: BTreeMap::new(),
    }])
}

fn evaluate_identity(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    Ok(vec![unary_argument("id", arguments)?.clone()])
}

fn evaluate_copy(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let value = unary_argument("copy", arguments)?.clone();
    Ok(vec![value.clone(), value])
}

fn evaluate_discard(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    unary_argument("discard", arguments)?;
    Ok(Vec::new())
}

fn evaluate_swap(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let [left, right] = binary_arguments("swap", arguments)?;
    Ok(vec![right.clone(), left.clone()])
}

fn evaluate_add(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let [left, right] = binary_arguments("add", arguments)?;
    Ok(vec![Dual {
        value: left.value + right.value,
        gradient: combine_gradients(&left.gradient, 1.0, &right.gradient, 1.0),
    }])
}

fn evaluate_product(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let [left, right] = binary_arguments("product", arguments)?;
    Ok(vec![Dual {
        value: left.value * right.value,
        gradient: combine_gradients(
            &left.gradient,
            right.value,
            &right.gradient,
            left.value,
        ),
    }])
}

fn evaluate_negation(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let argument = unary_argument("neg", arguments)?;
    Ok(vec![Dual {
        value: -argument.value,
        gradient: scale_gradient(&argument.gradient, -1.0),
    }])
}

fn evaluate_sine(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let argument = unary_argument("sin", arguments)?;
    Ok(vec![Dual {
        value: argument.value.sin(),
        gradient: scale_gradient(&argument.gradient, argument.value.cos()),
    }])
}

fn evaluate_cosine(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let argument = unary_argument("cos", arguments)?;
    Ok(vec![Dual {
        value: argument.value.cos(),
        gradient: scale_gradient(&argument.gradient, -argument.value.sin()),
    }])
}

fn evaluate_exponential(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let argument = unary_argument("exp", arguments)?;
    let value = argument.value.exp();
    Ok(vec![Dual {
        value,
        gradient: scale_gradient(&argument.gradient, value),
    }])
}

fn evaluate_logarithm(
    _parameters: &BTreeMap<String, Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    let argument = unary_argument("log", arguments)?;
    if argument.value <= 0.0 {
        return Err(LispError::Evaluation(
            "log expects a positive Real value".to_owned(),
        ));
    }
    Ok(vec![Dual {
        value: argument.value.ln(),
        gradient: scale_gradient(&argument.gradient, 1.0 / argument.value),
    }])
}

fn ensure_argument_count(name: &str, arguments: &[Dual], count: usize) -> Result<(), LispError> {
    if arguments.len() == count {
        Ok(())
    } else {
        Err(LispError::Evaluation(format!(
            "operation {name} expects {count} arguments, got {}",
            arguments.len()
        )))
    }
}

fn unary_argument<'a>(name: &str, arguments: &'a [Dual]) -> Result<&'a Dual, LispError> {
    match arguments {
        [argument] => Ok(argument),
        _ => Err(LispError::Evaluation(format!(
            "operation {name} expects one argument"
        ))),
    }
}

fn binary_arguments<'a>(name: &str, arguments: &'a [Dual]) -> Result<[&'a Dual; 2], LispError> {
    match arguments {
        [left, right] => Ok([left, right]),
        _ => Err(LispError::Evaluation(format!(
            "operation {name} expects two arguments"
        ))),
    }
}

fn scale_gradient(gradient: &BTreeMap<String, f64>, scale: f64) -> BTreeMap<String, f64> {
    gradient
        .iter()
        .map(|(name, value)| (name.clone(), scale * value))
        .collect()
}

fn combine_gradients(
    left: &BTreeMap<String, f64>,
    left_scale: f64,
    right: &BTreeMap<String, f64>,
    right_scale: f64,
) -> BTreeMap<String, f64> {
    let mut result = scale_gradient(left, left_scale);
    for (name, value) in right {
        *result.entry(name.clone()).or_default() += right_scale * value;
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeSet;

    #[test]
    fn builtin_keys_and_surface_forms_are_unique() {
        let keys = BUILTIN_OPERATIONS
            .iter()
            .map(OperationSpec::rule_id)
            .collect::<BTreeSet<_>>();
        assert_eq!(keys.len(), BUILTIN_OPERATIONS.len());

        let surface_names = BUILTIN_OPERATIONS
            .iter()
            .filter(|spec| spec.surface_form)
            .map(|spec| spec.name)
            .collect::<BTreeSet<_>>();
        let surface_count = BUILTIN_OPERATIONS
            .iter()
            .filter(|spec| spec.surface_form)
            .count();
        assert_eq!(surface_names.len(), surface_count);
        assert!(!builtin_surface_form("constant"));
        for spec in BUILTIN_OPERATIONS {
            spec.validate_lineage_shape().unwrap();
        }
    }
}
