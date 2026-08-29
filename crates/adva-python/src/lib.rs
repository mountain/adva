use adva_ir::{CompilationCertificate, DiagramValidationCertificate, SharedProgramDiagram};
use adva_lisp::{
    LinkedModules, compile_function, evaluate, evaluate_with_differential, import_diagram_json,
    link_modules as link_rust_modules, parse_module, validate_diagram,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::collections::BTreeMap;

type PyDifferential = (Vec<f64>, Vec<BTreeMap<String, f64>>, String);

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
            validation_certificate: validated.certificate,
        })
    }
}

#[pyclass(name = "Program", frozen, module = "adva._native", skip_from_py_object)]
#[derive(Clone, Debug)]
struct PyProgram {
    diagram: SharedProgramDiagram,
    compilation_certificate: Option<CompilationCertificate>,
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

    fn evaluate(&self, inputs: BTreeMap<String, f64>) -> PyResult<(Vec<f64>, String)> {
        let result = evaluate(&self.diagram, &inputs).map_err(py_error)?;
        let certificate = serde_json::to_string_pretty(&result.certificate).map_err(py_error)?;
        Ok((result.values, certificate))
    }

    fn value_and_gradient(&self, inputs: BTreeMap<String, f64>) -> PyResult<PyDifferential> {
        let result =
            evaluate_with_differential(&self.diagram, &inputs).map_err(py_error)?;
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
        validation_certificate: validated.certificate,
    })
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
    Ok(())
}
