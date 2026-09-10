use crate::LispError;
use crate::operation::{Dual, resolve_operation};
use crate::validate::validate_diagram_ref;
use adva_ir::{
    CertificateId, CheckStatus, DifferentialResult, DifferentiationCertificate,
    EvaluationCertificate, EvaluationResult, Observation, SharedProgramDiagram, WireProducer,
    WireRef,
};
use std::collections::{BTreeMap, BTreeSet};

struct RunResult {
    outputs: Vec<Dual>,
    executed_nodes: Vec<u32>,
    operation_rules: BTreeSet<String>,
}

/// Evaluate the recorded IEEE-754 operation versions, including special values.
/// Use [`evaluate_finite`] at finite numerical application boundaries.
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
            diagram_integrity: CheckStatus::Checked,
            operation_rules_checked: true,
        },
    })
}

/// Replay the recorded rules without imposing a finite-result policy.
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
            diagram_integrity: CheckStatus::Checked,
        },
    })
}

/// Require finite inputs and final values without reinterpreting operation rules.
/// Intermediate values and unused differentials are not certified finite.
pub fn evaluate_finite(
    diagram: &SharedProgramDiagram,
    inputs: &BTreeMap<String, f64>,
) -> Result<EvaluationResult, LispError> {
    require_finite_inputs(inputs)?;
    let mut result = evaluate(diagram, inputs)?;
    require_finite_values(&result.values)?;
    result.certificate.id =
        CertificateId::explicit(format!("evaluate:{}:finite-v1", diagram.function));
    result.certificate.scope =
        "PSC0 finite inputs and final scalar values; no error bound".to_owned();
    Ok(result)
}

/// Require finite inputs, final values and every final Jacobian component.
pub fn evaluate_with_finite_differential(
    diagram: &SharedProgramDiagram,
    inputs: &BTreeMap<String, f64>,
) -> Result<DifferentialResult, LispError> {
    require_finite_inputs(inputs)?;
    let mut result = evaluate_with_differential(diagram, inputs)?;
    require_finite_values(&result.values)?;
    for (row, gradient) in result.jacobian.iter().enumerate() {
        for (name, value) in gradient {
            if !value.is_finite() {
                return Err(LispError::Evaluation(format!(
                    "nonfinite derivative at output {row}, input {name:?}"
                )));
            }
        }
    }
    result.certificate.id =
        CertificateId::explicit(format!("differentiate:{}:finite-v1", diagram.function));
    result.certificate.scope =
        "PSC0 finite inputs, final values and Jacobian; no error bound".to_owned();
    Ok(result)
}

fn require_finite_inputs(inputs: &BTreeMap<String, f64>) -> Result<(), LispError> {
    for (name, value) in inputs {
        if !value.is_finite() {
            return Err(LispError::Evaluation(format!("nonfinite input {name:?}")));
        }
    }
    Ok(())
}

fn require_finite_values(values: &[f64]) -> Result<(), LispError> {
    for (index, value) in values.iter().enumerate() {
        if !value.is_finite() {
            return Err(LispError::Evaluation(format!("nonfinite output {index}")));
        }
    }
    Ok(())
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
    validate_diagram_ref(diagram)?;
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
        let spec = resolve_operation(&node.operation)?;
        spec.validate_wires(&node.inputs)?;
        spec.validate_outputs(&node.output_types)?;
        let arguments = node
            .inputs
            .iter()
            .map(|wire| read_wire(wire, &input_values, &node_values))
            .collect::<Result<Vec<_>, _>>()?;
        let outputs = spec.evaluate(&node.operation.parameters, &arguments)?;
        if outputs.len() != node.output_types.len() {
            return Err(LispError::Evaluation(format!(
                "operation {} produced {} outputs, expected {}",
                node.operation.name,
                outputs.len(),
                node.output_types.len()
            )));
        }
        operation_rules.insert(spec.rule_id());
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
