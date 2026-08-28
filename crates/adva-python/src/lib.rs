use adva_ir::CompilationArtifact;
use adva_lisp::{
    LinkedModules, compile_function, evaluate, evaluate_with_differential,
    link_modules as link_rust_modules, parse_module,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::collections::BTreeMap;

#[pyclass(name = "Workspace", frozen, module = "adva._native")]
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
        Ok(PyProgram { artifact })
    }
}

#[pyclass(name = "Program", frozen, module = "adva._native")]
#[derive(Clone, Debug)]
struct PyProgram {
    artifact: CompilationArtifact,
}

#[pymethods]
impl PyProgram {
    #[getter]
    fn qualified_name(&self) -> String {
        self.artifact.result.function.to_string()
    }

    fn signature_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.artifact.result.signature).map_err(py_error)
    }

    fn ir_json(&self) -> PyResult<String> {
        self.artifact.result.to_json().map_err(py_error)
    }

    fn compilation_certificate_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.artifact.certificate).map_err(py_error)
    }

    fn history_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.artifact.result.history).map_err(py_error)
    }

    fn source_partition_json(&self) -> PyResult<String> {
        serde_json::to_string_pretty(&self.artifact.result.source_partition()).map_err(py_error)
    }

    fn evaluate(&self, inputs: BTreeMap<String, f64>) -> PyResult<(Vec<f64>, String)> {
        let result = evaluate(&self.artifact.result, &inputs).map_err(py_error)?;
        let certificate = serde_json::to_string_pretty(&result.certificate).map_err(py_error)?;
        Ok((result.values, certificate))
    }

    fn value_and_gradient(
        &self,
        inputs: BTreeMap<String, f64>,
    ) -> PyResult<(Vec<f64>, Vec<BTreeMap<String, f64>>, String)> {
        let result =
            evaluate_with_differential(&self.artifact.result, &inputs).map_err(py_error)?;
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

fn py_error(error: impl std::fmt::Display) -> PyErr {
    PyValueError::new_err(error.to_string())
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyWorkspace>()?;
    module.add_class::<PyProgram>()?;
    module.add_function(wrap_pyfunction!(compile_module, module)?)?;
    module.add_function(wrap_pyfunction!(link_modules, module)?)?;
    Ok(())
}
