use crate::LispError;
use adva_ir::{
    CertificateId, DifferentialResult, DifferentiationCertificate, EvaluationCertificate,
    EvaluationResult, Observation, SharedProgramDiagram, WireProducer, WireRef,
};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
struct Dual {
    value: f64,
    gradient: BTreeMap<String, f64>,
}

struct RunResult {
    outputs: Vec<Dual>,
    executed_nodes: Vec<u32>,
    operation_rules: BTreeSet<String>,
}

pub fn evaluate(
    diagram: &SharedProgramDiagram,
    inputs: &BTreeMap<String, f64>,
) -> Result<EvaluationResult, LispError> {
    let run = run(diagram, inputs)?;
    Ok(EvaluationResult {
        values: run.outputs.into_iter().map(|output| output.value).collect(),
        certificate: EvaluationCertificate {
            id: CertificateId::explicit(format!("evaluate:{}:v1", diagram.function)),
            scope: "PSC0 builtin scalar realization".to_owned(),
            executed_nodes: run.executed_nodes,
            input_types_checked: true,
            operation_rules_checked: true,
        },
    })
}

pub fn evaluate_with_differential(
    diagram: &SharedProgramDiagram,
    inputs: &BTreeMap<String, f64>,
) -> Result<DifferentialResult, LispError> {
    let run = run(diagram, inputs)?;
    Ok(DifferentialResult {
        values: run.outputs.iter().map(|output| output.value).collect(),
        jacobian: run
            .outputs
            .iter()
            .map(|output| output.gradient.clone())
            .collect(),
        certificate: DifferentiationCertificate {
            id: CertificateId::explicit(format!("differentiate:{}:v1", diagram.function)),
            scope: "PSC0 forward differential over builtin Real operations".to_owned(),
            method: "forward-mode structural differential".to_owned(),
            operation_rules: run.operation_rules.into_iter().collect(),
            input_types_checked: true,
        },
    })
}

pub fn observe_source_partition(diagram: &SharedProgramDiagram) -> Observation {
    Observation::SourcePartition {
        partition: diagram.source_partition(),
    }
}

pub fn observe_history(diagram: &SharedProgramDiagram) -> Observation {
    Observation::History {
        history: diagram.history.clone(),
    }
}

fn run(
    diagram: &SharedProgramDiagram,
    inputs: &BTreeMap<String, f64>,
) -> Result<RunResult, LispError> {
    validate_inputs(diagram, inputs)?;
    let input_values = diagram
        .signature
        .inputs
        .iter()
        .map(|port| Dual {
            value: inputs[&port.name],
            gradient: BTreeMap::from([(port.name.clone(), 1.0)]),
        })
        .collect::<Vec<_>>();
    let mut node_values = BTreeMap::new();
    let mut executed_nodes = Vec::new();
    let mut operation_rules = BTreeSet::new();

    for node in &diagram.nodes {
        let arguments = node
            .inputs
            .iter()
            .map(|wire| read_wire(wire, &input_values, &node_values))
            .collect::<Result<Vec<_>, _>>()?;
        let outputs = execute_operation(&node.operation.name, &node.operation.parameters, &arguments)?;
        if outputs.len() != node.output_types.len() {
            return Err(LispError::Evaluation(format!(
                "operation {} produced {} outputs, expected {}",
                node.operation.name,
                outputs.len(),
                node.output_types.len()
            )));
        }
        operation_rules.insert(node.operation.name.clone());
        executed_nodes.push(node.id.0);
        node_values.insert(node.id, outputs);
    }

    let outputs = diagram
        .outputs
        .iter()
        .map(|wire| read_wire(wire, &input_values, &node_values))
        .collect::<Result<_, _>>()?;
    Ok(RunResult {
        outputs,
        executed_nodes,
        operation_rules,
    })
}

fn validate_inputs(
    diagram: &SharedProgramDiagram,
    inputs: &BTreeMap<String, f64>,
) -> Result<(), LispError> {
    let expected = diagram
        .signature
        .inputs
        .iter()
        .map(|port| port.name.as_str())
        .collect::<BTreeSet<_>>();
    let actual = inputs.keys().map(String::as_str).collect::<BTreeSet<_>>();
    if expected == actual {
        Ok(())
    } else {
        Err(LispError::Evaluation(format!(
            "input names differ: expected {expected:?}, got {actual:?}"
        )))
    }
}

fn read_wire(
    wire: &WireRef,
    inputs: &[Dual],
    nodes: &BTreeMap<adva_ir::NodeId, Vec<Dual>>,
) -> Result<Dual, LispError> {
    let output = match &wire.producer {
        WireProducer::Input { index } => inputs.get(*index as usize),
        WireProducer::Node { node } => nodes
            .get(node)
            .and_then(|outputs| outputs.get(wire.output_index as usize)),
    };
    output.cloned().ok_or_else(|| {
        LispError::Evaluation(format!("wire references unavailable producer: {wire:?}"))
    })
}

fn execute_operation(
    name: &str,
    parameters: &BTreeMap<String, adva_ir::Rational>,
    arguments: &[Dual],
) -> Result<Vec<Dual>, LispError> {
    match name {
        "constant" => {
            let value = parameters.get("value").ok_or_else(|| {
                LispError::Evaluation("constant node has no value parameter".to_owned())
            })?;
            Ok(vec![Dual {
                value: value.as_f64(),
                gradient: BTreeMap::new(),
            }])
        }
        "id" => Ok(vec![unary_argument(name, arguments)?.clone()]),
        "copy" => {
            let value = unary_argument(name, arguments)?.clone();
            Ok(vec![value.clone(), value])
        }
        "discard" => {
            unary_argument(name, arguments)?;
            Ok(Vec::new())
        }
        "swap" => {
            let [left, right] = binary_arguments(name, arguments)?;
            Ok(vec![right.clone(), left.clone()])
        }
        "add" => {
            let [left, right] = binary_arguments(name, arguments)?;
            Ok(vec![Dual {
                value: left.value + right.value,
                gradient: combine_gradients(&left.gradient, 1.0, &right.gradient, 1.0),
            }])
        }
        "mul" | "scale" => {
            let [left, right] = binary_arguments(name, arguments)?;
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
        "neg" => {
            let argument = unary_argument(name, arguments)?;
            Ok(vec![Dual {
                value: -argument.value,
                gradient: scale_gradient(&argument.gradient, -1.0),
            }])
        }
        "sin" => {
            let argument = unary_argument(name, arguments)?;
            Ok(vec![Dual {
                value: argument.value.sin(),
                gradient: scale_gradient(&argument.gradient, argument.value.cos()),
            }])
        }
        "cos" => {
            let argument = unary_argument(name, arguments)?;
            Ok(vec![Dual {
                value: argument.value.cos(),
                gradient: scale_gradient(&argument.gradient, -argument.value.sin()),
            }])
        }
        "exp" => {
            let argument = unary_argument(name, arguments)?;
            let value = argument.value.exp();
            Ok(vec![Dual {
                value,
                gradient: scale_gradient(&argument.gradient, value),
            }])
        }
        "log" => {
            let argument = unary_argument(name, arguments)?;
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
        other => Err(LispError::Evaluation(format!(
            "no scalar realization for operation {other:?}"
        ))),
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

fn binary_arguments<'a>(
    name: &str,
    arguments: &'a [Dual],
) -> Result<[&'a Dual; 2], LispError> {
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

