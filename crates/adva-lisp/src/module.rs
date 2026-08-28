use crate::LispError;
use adva_ir::{FunctionDefinition, FunctionName, ModuleDefinition, ModuleIr, ModuleName};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
pub struct LinkedModules {
    modules: BTreeMap<ModuleName, ModuleDefinition>,
}

impl LinkedModules {
    pub fn module_names(&self) -> Vec<String> {
        self.modules.keys().map(|name| name.0.clone()).collect()
    }

    pub fn module(&self, name: &ModuleName) -> Result<&ModuleDefinition, LispError> {
        self.modules
            .get(name)
            .ok_or_else(|| LispError::Module(format!("unknown module {name}")))
    }

    pub fn function(
        &self,
        module: &ModuleName,
        function: &FunctionName,
    ) -> Result<&FunctionDefinition, LispError> {
        self.module(module)?
            .definitions
            .iter()
            .find(|definition| &definition.name == function)
            .ok_or_else(|| {
                LispError::Module(format!("unknown function {module}/{function}"))
            })
    }
}

pub fn link_modules(modules: Vec<ModuleIr>) -> Result<LinkedModules, LispError> {
    let mut linked = BTreeMap::new();
    for module_ir in modules {
        module_ir.validate_version()?;
        let name = module_ir.module.name.clone();
        if linked.insert(name.clone(), module_ir.module).is_some() {
            return Err(LispError::Module(format!(
                "duplicate module definition {name}"
            )));
        }
    }

    for module in linked.values() {
        validate_exports(module)?;
        validate_imports(module, &linked)?;
    }
    validate_acyclic_imports(&linked)?;
    Ok(LinkedModules { modules: linked })
}

fn validate_exports(module: &ModuleDefinition) -> Result<(), LispError> {
    let definitions: BTreeSet<_> = module
        .definitions
        .iter()
        .map(|definition| &definition.name)
        .collect();
    let mut seen = BTreeSet::new();
    for export in &module.exports {
        if !seen.insert(export) {
            return Err(LispError::Module(format!(
                "duplicate export {export} in module {}",
                module.name
            )));
        }
        if !definitions.contains(export) {
            return Err(LispError::Module(format!(
                "module {} exports undefined function {export}",
                module.name
            )));
        }
    }
    Ok(())
}

fn validate_imports(
    module: &ModuleDefinition,
    linked: &BTreeMap<ModuleName, ModuleDefinition>,
) -> Result<(), LispError> {
    for import in &module.imports {
        let imported_module = linked.get(&import.module).ok_or_else(|| {
            LispError::Module(format!(
                "module {} imports missing module {}",
                module.name, import.module
            ))
        })?;
        for name in &import.names {
            if !imported_module.exports.contains(name) {
                return Err(LispError::Module(format!(
                    "module {} imports non-exported function {}/{}",
                    module.name, import.module, name
                )));
            }
        }
    }
    Ok(())
}

fn validate_acyclic_imports(
    modules: &BTreeMap<ModuleName, ModuleDefinition>,
) -> Result<(), LispError> {
    let mut visiting = BTreeSet::new();
    let mut visited = BTreeSet::new();
    for module in modules.keys() {
        visit_module(module, modules, &mut visiting, &mut visited)?;
    }
    Ok(())
}

fn visit_module(
    name: &ModuleName,
    modules: &BTreeMap<ModuleName, ModuleDefinition>,
    visiting: &mut BTreeSet<ModuleName>,
    visited: &mut BTreeSet<ModuleName>,
) -> Result<(), LispError> {
    if visited.contains(name) {
        return Ok(());
    }
    if !visiting.insert(name.clone()) {
        return Err(LispError::Module(format!(
            "cyclic module import involving {name}"
        )));
    }
    let module = modules
        .get(name)
        .ok_or_else(|| LispError::Module(format!("unknown module {name}")))?;
    for import in &module.imports {
        visit_module(&import.module, modules, visiting, visited)?;
    }
    visiting.remove(name);
    visited.insert(name.clone());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parse_module;

    #[test]
    fn cyclic_imports_are_rejected() {
        let left = parse_module(
            "(module left (import right g) (export f) (def f (fn ((x Real)) Real (use x))))",
        )
        .unwrap();
        let right = parse_module(
            "(module right (import left f) (export g) (def g (fn ((x Real)) Real (use x))))",
        )
        .unwrap();
        assert!(link_modules(vec![left, right]).is_err());
    }
}

