use adva_ir::{
    CompilationCertificate, DiagramValidationCertificate, GraftTraceArtifact, NodeId,
    SharedProgramDiagram, TriadicDomainV0, TriadicObserverPolicyV0,
};
use adva_lisp::{
    LinkedModules, advance_causal_cut as advance_cut, analyze_causal_cut as analyze_cut,
    analyze_program_slice as analyze_slice,
    analyze_program_slice_with_graft as analyze_slice_with_graft,
    analyze_triadic_observer_transition_v0 as analyze_triadic_transition,
    analyze_triadic_observer_transition_with_graft_v0 as analyze_triadic_transition_with_graft,
    compile_function, compose_program_slices as compose_slices,
    compose_program_slices_with_graft as compose_slices_with_graft,
    compose_triadic_observer_transitions_v0 as compose_triadic_transitions,
    compose_triadic_observer_transitions_with_graft_v0 as compose_triadic_transitions_with_graft,
    evaluate, evaluate_with_differential, import_diagram_json, link_modules as link_rust_modules,
    parse_module, validate_diagram,
};
use adva_witness::{
    CarrierRouteV0, MechanismOutputV0, ReloadPlanV0, load_adva_document_v0,
    save_adva_document_v0,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::collections::BTreeMap;

type PyDifferential = (Vec<f64>, Vec<BTreeMap<String, f64>>, String);
type PyCertifiedProcess = (String, String);

#[pyclass(
    name = "Workspace",
    frozen,
    module = "adva._native",
    skip_from_py_object
)]
#[derive(Clone, Debug)]
struct PyWorkspace {
    linked: LinkedModules,
}

#[pymethods]
impl PyWorkspace {
    fn module_names(&self) -> Vec<String> {
        self.linked.module_names()
    }

    fn function(&self, module: &str, function: &str) -> PyResult<PyProgram> {
        let artifact = compile_function(&self.linked, module, function).map_err(py_error)?;
        let validated = validate_diagram(artifact.result).map_err(py_error)?;
        Ok(PyProgram {
            diagram: validated.result,
            compilation_certificate: Some(artifact.certificate),
            graft_trace: Some(artifact.graft_trace),
            validation_certificate: validated.certificate,
        })
    }
}

#[pyclass(name = "Program", frozen, module = "adva._native", skip_from_py_object)]
#[derive(Clone, Debug)]
struct PyProgram {
    diagram: SharedProgramDiagram,
    compilation_certificate: Option<CompilationCertificate>,
    graft_trace: Option<GraftTraceArtifact>,
    validation_certificate: DiagramValidationCertificate,
}

#[pymethods]
impl PyProgram {
    #[getter]
    fn qualified_name(&self) -> String {
        self.diagram.function.to_string()
    }

    fn signature_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.diagram.signature).map_err(py_error)
    }

    fn ir_json(&self) -> PyResult<String> {
        self.diagram.to_json().map_err(py_error)
    }

    fn compilation_certificate_json(&self) -> PyResult<Option<String>> {
        self.compilation_certificate
            .as_ref()
            .map(|certificate| serde_json::to_string_pretty(certificate).map_err(py_error))
            .transpose()
    }

    fn validation_certificate_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.validation_certificate).map_err(py_error)
    }

    fn history_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.diagram.history).map_err(py_error)
    }

    fn source_partition_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.diagram.source_partition()).map_err(py_error)
    }

    fn graft_trace(&self) -> PyResult<Option<PyCertifiedProcess>> {
        let Some(artifact) = &self.graft_trace else {
            return Ok(None);
        };
        Ok(Some((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        )))
    }

    fn causal_cut(&self, completed: Vec<u32>) -> PyResult<PyCertifiedProcess> {
        let completed = completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let artifact = analyze_cut(&self.diagram, &completed).map_err(py_error)?;
        Ok((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        ))
    }

    fn advance_causal_cut(&self, completed: Vec<u32>, event: u32) -> PyResult<PyCertifiedProcess> {
        let completed = completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let artifact = advance_cut(&self.diagram, &completed, NodeId(event)).map_err(py_error)?;
        Ok((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        ))
    }

    fn program_slice(
        &self,
        lower_completed: Vec<u32>,
        upper_completed: Vec<u32>,
    ) -> PyResult<PyCertifiedProcess> {
        let lower_completed = lower_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let upper_completed = upper_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let artifact = match &self.graft_trace {
            Some(graft_trace) => analyze_slice_with_graft(
                &self.diagram,
                &graft_trace.result,
                &lower_completed,
                &upper_completed,
            ),
            None => analyze_slice(&self.diagram, &lower_completed, &upper_completed),
        }
        .map_err(py_error)?;
        Ok((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        ))
    }

    fn compose_program_slices(
        &self,
        lower_completed: Vec<u32>,
        middle_completed: Vec<u32>,
        upper_completed: Vec<u32>,
    ) -> PyResult<PyCertifiedProcess> {
        let lower_completed = lower_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let middle_completed = middle_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let upper_completed = upper_completed.into_iter().map(NodeId).collect::<Vec<_>>();

        let artifact = match &self.graft_trace {
            Some(graft_trace) => {
                let left = analyze_slice_with_graft(
                    &self.diagram,
                    &graft_trace.result,
                    &lower_completed,
                    &middle_completed,
                )
                .map_err(py_error)?;
                let right = analyze_slice_with_graft(
                    &self.diagram,
                    &graft_trace.result,
                    &middle_completed,
                    &upper_completed,
                )
                .map_err(py_error)?;
                compose_slices_with_graft(
                    &self.diagram,
                    &graft_trace.result,
                    &left.result,
                    &right.result,
                )
            }
            None => {
                let left = analyze_slice(&self.diagram, &lower_completed, &middle_completed)
                    .map_err(py_error)?;
                let right = analyze_slice(&self.diagram, &middle_completed, &upper_completed)
                    .map_err(py_error)?;
                compose_slices(&self.diagram, &left.result, &right.result)
            }
        }
        .map_err(py_error)?;
        Ok((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        ))
    }

    fn triadic_observer_transition_v0(
        &self,
        input_domains: Vec<String>,
        lower_completed: Vec<u32>,
        upper_completed: Vec<u32>,
    ) -> PyResult<PyCertifiedProcess> {
        let policy = triadic_policy(input_domains)?;
        let lower_completed = lower_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let upper_completed = upper_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let artifact = match &self.graft_trace {
            Some(graft_trace) => analyze_triadic_transition_with_graft(
                &self.diagram,
                &graft_trace.result,
                &policy,
                &lower_completed,
                &upper_completed,
            ),
            None => analyze_triadic_transition(
                &self.diagram,
                &policy,
                &lower_completed,
                &upper_completed,
            ),
        }
        .map_err(py_error)?;
        Ok((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        ))
    }

    fn compose_triadic_observer_transitions_v0(
        &self,
        input_domains: Vec<String>,
        lower_completed: Vec<u32>,
        middle_completed: Vec<u32>,
        upper_completed: Vec<u32>,
    ) -> PyResult<PyCertifiedProcess> {
        let policy = triadic_policy(input_domains)?;
        let lower_completed = lower_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let middle_completed = middle_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let upper_completed = upper_completed.into_iter().map(NodeId).collect::<Vec<_>>();
        let artifact = match &self.graft_trace {
            Some(graft_trace) => {
                let left = analyze_triadic_transition_with_graft(
                    &self.diagram,
                    &graft_trace.result,
                    &policy,
                    &lower_completed,
                    &middle_completed,
                )
                .map_err(py_error)?;
                let right = analyze_triadic_transition_with_graft(
                    &self.diagram,
                    &graft_trace.result,
                    &policy,
                    &middle_completed,
                    &upper_completed,
                )
                .map_err(py_error)?;
                compose_triadic_transitions_with_graft(
                    &self.diagram,
                    &graft_trace.result,
                    &policy,
                    &left.result,
                    &right.result,
                )
            }
            None => {
                let left = analyze_triadic_transition(
                    &self.diagram,
                    &policy,
                    &lower_completed,
                    &middle_completed,
                )
                .map_err(py_error)?;
                let right = analyze_triadic_transition(
                    &self.diagram,
                    &policy,
                    &middle_completed,
                    &upper_completed,
                )
                .map_err(py_error)?;
                compose_triadic_transitions(&self.diagram, &policy, &left.result, &right.result)
            }
        }
        .map_err(py_error)?;
        Ok((
            serde_json::to_string_pretty(&artifact.result).map_err(py_error)?,
            serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
        ))
    }

    fn evaluate(&self, inputs: BTreeMap<String, f64>) -> PyResult<(Vec<f64>, String)> {
        let result = evaluate(&self.diagram, &inputs).map_err(py_error)?;
        let certificate = serde_json::to_string_pretty(&result.certificate).map_err(py_error)?;
        Ok((result.values, certificate))
    }

    fn value_and_gradient(&self, inputs: BTreeMap<String, f64>) -> PyResult<PyDifferential> {
        let result = evaluate_with_differential(&self.diagram, &inputs).map_err(py_error)?;
        let certificate = serde_json::to_string_pretty(&result.certificate).map_err(py_error)?;
        Ok((result.values, result.jacobian, certificate))
    }
}

#[pyfunction]
fn compile_module(source: &str) -> PyResult<PyWorkspace> {
    link_modules(vec![source.to_owned()])
}

#[pyfunction]
fn link_modules(sources: Vec<String>) -> PyResult<PyWorkspace> {
    let modules = sources
        .iter()
        .map(|source| parse_module(source))
        .collect::<Result<Vec<_>, _>>()
        .map_err(py_error)?;
    let linked = link_rust_modules(modules).map_err(py_error)?;
    Ok(PyWorkspace { linked })
}

#[pyfunction]
fn load_program_json(source: &str) -> PyResult<PyProgram> {
    let validated = import_diagram_json(source).map_err(py_error)?;
    Ok(PyProgram {
        diagram: validated.result,
        compilation_certificate: None,
        graft_trace: None,
        validation_certificate: validated.certificate,
    })
}

#[pyfunction]
fn save_adva_document_json(path: &str, output_json: &str) -> PyResult<(String, u64)> {
    let output: MechanismOutputV0 = serde_json::from_str(output_json).map_err(py_error)?;
    let receipt = save_adva_document_v0(path, output).map_err(py_error)?;
    Ok((receipt.document_digest, receipt.bytes_written))
}

#[pyfunction]
fn load_adva_document_json(path: &str, routes_json: &str) -> PyResult<(String, String)> {
    let routes: [CarrierRouteV0; 3] = serde_json::from_str(routes_json).map_err(py_error)?;
    let plan = ReloadPlanV0::from_routes(routes).map_err(py_error)?;
    let artifact = load_adva_document_v0(path, &plan).map_err(py_error)?;
    Ok((
        serde_json::to_string_pretty(&artifact.input).map_err(py_error)?,
        serde_json::to_string_pretty(&artifact.certificate).map_err(py_error)?,
    ))
}

fn triadic_policy(input_domains: Vec<String>) -> PyResult<TriadicObserverPolicyV0> {
    let input_domains = input_domains
        .into_iter()
        .map(|domain| match domain.as_str() {
            "construction" => Ok(TriadicDomainV0::Construction),
            "space" => Ok(TriadicDomainV0::Space),
            "time" => Ok(TriadicDomainV0::Time),
            _ => Err(PyValueError::new_err(format!(
                "unknown triadic observer domain {domain:?}"
            ))),
        })
        .collect::<PyResult<Vec<_>>>()?;
    Ok(TriadicObserverPolicyV0 { input_domains })
}

fn py_error(error: impl std::fmt::Display) -> PyErr {
    PyValueError::new_err(error.to_string())
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyWorkspace>()?;
    module.add_class::<PyProgram>()?;
    module.add_function(wrap_pyfunction!(compile_module, module)?)?;
    module.add_function(wrap_pyfunction!(link_modules, module)?)?;
    module.add_function(wrap_pyfunction!(load_program_json, module)?)?;
    module.add_function(wrap_pyfunction!(save_adva_document_json, module)?)?;
    module.add_function(wrap_pyfunction!(load_adva_document_json, module)?)?;
    Ok(())
}
