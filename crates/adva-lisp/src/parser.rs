use crate::LispError;
use crate::operation::builtin_surface_form;
use adva_ir::{
    FunctionDefinition, FunctionName, FunctionSignature, ModuleDefinition, ModuleImport, ModuleIr,
    ModuleName, OperationRef, ProgramTerm, QualifiedName, Rational, TypedPort, ValueType,
};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Eq, PartialEq)]
enum SExpr {
    Atom(String),
    List(Vec<Self>),
}

impl SExpr {
    fn atom(&self) -> Result<&str, LispError> {
        match self {
            Self::Atom(value) => Ok(value),
            Self::List(_) => Err(LispError::Syntax("expected symbol".to_owned())),
        }
    }

    fn list(&self) -> Result<&[Self], LispError> {
        match self {
            Self::List(items) => Ok(items),
            Self::Atom(_) => Err(LispError::Syntax("expected list".to_owned())),
        }
    }
}

pub fn parse_module(source: &str) -> Result<ModuleIr, LispError> {
    let expression = read(source)?;
    let items = expression.list()?;
    if items.len() < 2 || items[0].atom()? != "module" {
        return Err(LispError::Syntax(
            "top-level form must be (module name ...)".to_owned(),
        ));
    }
    let module_name = ModuleName::explicit(items[1].atom()?);
    let forms = &items[2..];

    let mut imports = Vec::new();
    let mut exports = Vec::new();
    let mut definition_names = BTreeSet::new();
    for form in forms {
        let form_items = form.list()?;
        let head = form_items
            .first()
            .ok_or_else(|| LispError::Syntax("empty module form".to_owned()))?
            .atom()?;
        match head {
            "import" => imports.push(parse_import(form_items)?),
            "export" => {
                for item in &form_items[1..] {
                    exports.push(FunctionName::explicit(item.atom()?));
                }
            }
            "def" => {
                if form_items.len() != 3 {
                    return Err(LispError::Syntax("(def name (fn ...))".to_owned()));
                }
                let name = form_items[1].atom()?.to_owned();
                if !definition_names.insert(name.clone()) {
                    return Err(LispError::Module(format!(
                        "duplicate definition {name:?} in module {module_name}"
                    )));
                }
            }
            other => {
                return Err(LispError::Syntax(format!("unknown module form {other:?}")));
            }
        }
    }

    let import_map = build_import_map(&imports)?;
    let mut definitions = Vec::new();
    for form in forms {
        let form_items = form.list()?;
        if form_items[0].atom()? == "def" {
            definitions.push(parse_definition(
                form_items,
                &module_name,
                &definition_names,
                &import_map,
            )?);
        }
    }

    Ok(ModuleIr::new(ModuleDefinition {
        name: module_name,
        imports,
        exports,
        definitions,
    }))
}

fn parse_import(items: &[SExpr]) -> Result<ModuleImport, LispError> {
    if items.len() < 3 {
        return Err(LispError::Syntax(
            "imports list explicit names: (import module name ...)".to_owned(),
        ));
    }
    Ok(ModuleImport {
        module: ModuleName::explicit(items[1].atom()?),
        names: items[2..]
            .iter()
            .map(|item| item.atom().map(FunctionName::explicit))
            .collect::<Result<_, _>>()?,
    })
}

fn build_import_map(imports: &[ModuleImport]) -> Result<BTreeMap<String, ModuleName>, LispError> {
    let mut result = BTreeMap::new();
    for import in imports {
        for name in &import.names {
            if result
                .insert(name.0.clone(), import.module.clone())
                .is_some()
            {
                return Err(LispError::Module(format!(
                    "imported name {:?} is ambiguous",
                    name.0
                )));
            }
        }
    }
    Ok(result)
}

fn parse_definition(
    items: &[SExpr],
    module: &ModuleName,
    local_names: &BTreeSet<String>,
    imports: &BTreeMap<String, ModuleName>,
) -> Result<FunctionDefinition, LispError> {
    let name = FunctionName::explicit(items[1].atom()?);
    let function = items[2].list()?;
    if function.len() != 4 || function[0].atom()? != "fn" {
        return Err(LispError::Syntax(
            "function form is (fn ((name Type) ...) ResultType body)".to_owned(),
        ));
    }
    let inputs = parse_inputs(&function[1])?;
    let outputs = parse_outputs(&function[2])?;
    let body = parse_term(&function[3], module, local_names, imports)?;
    Ok(FunctionDefinition {
        name,
        signature: FunctionSignature { inputs, outputs },
        body,
    })
}

fn parse_inputs(expression: &SExpr) -> Result<Vec<TypedPort>, LispError> {
    let mut names = BTreeSet::new();
    expression
        .list()?
        .iter()
        .map(|item| {
            let pair = item.list()?;
            if pair.len() != 2 {
                return Err(LispError::Syntax("input is (name Type)".to_owned()));
            }
            let name = pair[0].atom()?.to_owned();
            if !names.insert(name.clone()) {
                return Err(LispError::Module(format!("duplicate input {name:?}")));
            }
            Ok(TypedPort {
                name,
                value_type: parse_type(pair[1].atom()?)?,
            })
        })
        .collect()
}

fn parse_outputs(expression: &SExpr) -> Result<Vec<ValueType>, LispError> {
    match expression {
        SExpr::Atom(name) => Ok(vec![parse_type(name)?]),
        SExpr::List(items) => {
            if items.first().map(SExpr::atom).transpose()? != Some("outputs") {
                return Err(LispError::Syntax(
                    "multiple results use (outputs Type ...)".to_owned(),
                ));
            }
            items[1..]
                .iter()
                .map(|item| parse_type(item.atom()?))
                .collect()
        }
    }
}

fn parse_type(name: &str) -> Result<ValueType, LispError> {
    ValueType::parse(name).ok_or_else(|| LispError::Type(format!("unknown type {name:?}")))
}

fn parse_term(
    expression: &SExpr,
    module: &ModuleName,
    local_names: &BTreeSet<String>,
    imports: &BTreeMap<String, ModuleName>,
) -> Result<ProgramTerm, LispError> {
    if let SExpr::Atom(atom) = expression {
        return Ok(ProgramTerm::Constant {
            value: parse_rational(atom)?,
        });
    }
    let items = expression.list()?;
    let head = items
        .first()
        .ok_or_else(|| LispError::Syntax("empty term".to_owned()))?
        .atom()?;
    match head {
        "use" => {
            if items.len() != 2 {
                return Err(LispError::Syntax("(use port)".to_owned()));
            }
            Ok(ProgramTerm::Use {
                port: items[1].atom()?.to_owned(),
            })
        }
        "tensor" => Ok(ProgramTerm::Tensor {
            terms: parse_arguments(&items[1..], module, local_names, imports)?,
        }),
        "call" => {
            if items.len() < 2 {
                return Err(LispError::Syntax("(call function argument ...)".to_owned()));
            }
            Ok(ProgramTerm::Call {
                function: resolve_call(items[1].atom()?, module, local_names, imports)?,
                arguments: parse_arguments(&items[2..], module, local_names, imports)?,
            })
        }
        operation if builtin_surface_form(operation) => Ok(ProgramTerm::Apply {
            operation: OperationRef::builtin(operation),
            arguments: parse_arguments(&items[1..], module, local_names, imports)?,
        }),
        other => Err(LispError::Syntax(format!("unknown operation {other:?}"))),
    }
}

fn parse_arguments(
    items: &[SExpr],
    module: &ModuleName,
    local_names: &BTreeSet<String>,
    imports: &BTreeMap<String, ModuleName>,
) -> Result<Vec<ProgramTerm>, LispError> {
    items
        .iter()
        .map(|item| parse_term(item, module, local_names, imports))
        .collect()
}

fn resolve_call(
    name: &str,
    module: &ModuleName,
    local_names: &BTreeSet<String>,
    imports: &BTreeMap<String, ModuleName>,
) -> Result<QualifiedName, LispError> {
    if let Some((module_name, function)) = name.split_once('/') {
        return Ok(QualifiedName::new(module_name, function));
    }
    if local_names.contains(name) {
        return Ok(QualifiedName::new(module.0.clone(), name));
    }
    imports
        .get(name)
        .map(|imported_module| QualifiedName::new(imported_module.0.clone(), name))
        .ok_or_else(|| LispError::Module(format!("unresolved call {name:?}")))
}

fn parse_rational(atom: &str) -> Result<Rational, LispError> {
    if let Some((numerator, denominator)) = atom.split_once('/') {
        let numerator = numerator
            .parse::<i64>()
            .map_err(|_| LispError::Syntax(format!("invalid rational {atom:?}")))?;
        let denominator = denominator
            .parse::<i64>()
            .map_err(|_| LispError::Syntax(format!("invalid rational {atom:?}")))?;
        return Ok(Rational::new(numerator, denominator)?);
    }
    atom.parse::<i64>()
        .map(Rational::integer)
        .map_err(|_| LispError::Syntax(format!("bare symbol {atom:?}; use (use {atom})")))
}

fn read(source: &str) -> Result<SExpr, LispError> {
    let tokens = tokenize(source);
    let mut position = 0;
    let expression = parse_tokens(&tokens, &mut position)?;
    if position != tokens.len() {
        return Err(LispError::Syntax(
            "multiple top-level expressions".to_owned(),
        ));
    }
    Ok(expression)
}

fn tokenize(source: &str) -> Vec<String> {
    let mut result = Vec::new();
    let mut current = String::new();
    let mut comment = false;
    for character in source.chars() {
        if comment {
            if character == '\n' {
                comment = false;
            }
            continue;
        }
        match character {
            ';' => {
                if !current.is_empty() {
                    result.push(std::mem::take(&mut current));
                }
                comment = true;
            }
            '(' | ')' => {
                if !current.is_empty() {
                    result.push(std::mem::take(&mut current));
                }
                result.push(character.to_string());
            }
            character if character.is_whitespace() => {
                if !current.is_empty() {
                    result.push(std::mem::take(&mut current));
                }
            }
            _ => current.push(character),
        }
    }
    if !current.is_empty() {
        result.push(current);
    }
    result
}

fn parse_tokens(tokens: &[String], position: &mut usize) -> Result<SExpr, LispError> {
    let token = tokens
        .get(*position)
        .ok_or_else(|| LispError::Syntax("unexpected end of input".to_owned()))?;
    *position += 1;
    match token.as_str() {
        "(" => {
            let mut items = Vec::new();
            while tokens.get(*position).map(String::as_str) != Some(")") {
                if *position >= tokens.len() {
                    return Err(LispError::Syntax("unclosed list".to_owned()));
                }
                items.push(parse_tokens(tokens, position)?);
            }
            *position += 1;
            Ok(SExpr::List(items))
        }
        ")" => Err(LispError::Syntax("unexpected ')'".to_owned())),
        atom => Ok(SExpr::Atom(atom.to_owned())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn module_round_trip_preserves_explicit_calls() {
        let ir = parse_module(
            "(module m (export twice) (def twice (fn ((x Real)) Real (add (copy (use x))))))",
        )
        .unwrap();
        let json = ir.to_json().unwrap();
        assert_eq!(ModuleIr::from_json(&json).unwrap(), ir);
    }

    #[test]
    fn bare_symbols_are_not_host_values() {
        let error =
            parse_module("(module m (export f) (def f (fn ((x Real)) Real x)))").unwrap_err();
        assert!(error.to_string().contains("bare symbol"));
    }
}
