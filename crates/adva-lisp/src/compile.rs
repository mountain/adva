use crate::operation::{LineageRule, resolve_operation};
use crate::validate::validate_diagram_ref;
use crate::{LinkedModules, LispError};
use adva_ir::{
    CertificateId, CheckStatus, CompilationArtifact, CompilationCertificate, FunctionDefinition,
    FunctionName, History, HistoryEvent, IR_SCHEMA, IR_VERSION, ModuleName, NodeId, Occurrence,
    OccurrenceId, OccurrencePath, OperationNode, OperationRef, ProgramTerm, QualifiedName,
    SharedProgramDiagram, SourceId, ValueType, WireProducer, WireRef,
};
use std::collections::BTreeMap;

#[derive(Clone, Debug)]
struct Resource {
    wires: Vec<WireRef>,
    used: bool,
}

#[derive(Clone, Debug)]
struct ResourceScope {
    resources: BTreeMap<String, Resource>,
}

impl ResourceScope {
    fn from_pairs(pairs: impl IntoIterator<Item = (String, WireRef)>) -> Self {
        Self {
            resources: pairs
                .into_iter()
                .map(|(name, wire)| {
                    (
                        name,
                        Resource {
                            wires: vec![wire],
                            used: false,
                        },
                    )
                })
                .collect(),
        }
    }

    fn consume(&mut self, name: &str) -> Result<Vec<WireRef>, LispError> {
        let resource = self
            .resources
            .get_mut(name)
            .ok_or_else(|| LispError::Linearity(format!("unknown input resource {name:?}")))?;
        if resource.used {
            return Err(LispError::Linearity(format!(
                "input {name:?} is used more than once; use explicit copy"
            )));
        }
        resource.used = true;
        Ok(resource.wires.clone())
    }

    fn ensure_consumed(&self, function: &QualifiedName) -> Result<(), LispError> {
        let unused: Vec<_> = self
            .resources
            .iter()
            .filter(|(_, resource)| !resource.used)
            .map(|(name, _)| name.clone())
            .collect();
        if unused.is_empty() {
            Ok(())
        } else {
            Err(LispError::Linearity(format!(
                "function {function} leaves inputs {unused:?} unused; use explicit discard"
            )))
        }
    }
}

struct Compiler<'a> {
    linked: &'a LinkedModules,
    nodes: Vec<OperationNode>,
    occurrences: Vec<Occurrence>,
    history: Vec<HistoryEvent>,
    occurrence_paths: BTreeMap<OccurrenceId, OccurrencePath>,
    next_node: u32,
    next_occurrence: u32,
    call_stack: Vec<QualifiedName>,
}

impl<'a> Compiler<'a> {
    fn new(linked: &'a LinkedModules) -> Self {
        Self {
            linked,
            nodes: Vec::new(),
            occurrences: Vec::new(),
            history: Vec::new(),
            occurrence_paths: BTreeMap::new(),
            next_node: 0,
            next_occurrence: 0,
            call_stack: Vec::new(),
        }
    }

    fn fresh_node(&mut self) -> NodeId {
        let id = NodeId(self.next_node);
        self.next_node += 1;
        id
    }

    fn fresh_occurrence(&mut self, source: SourceId, path: OccurrencePath) -> OccurrenceId {
        let id = OccurrenceId::explicit(format!("occ:{}", self.next_occurrence));
        self.next_occurrence += 1;
        self.occurrences.push(Occurrence {
            id: id.clone(),
            source,
            path: path.clone(),
        });
        self.occurrence_paths.insert(id.clone(), path);
        id
    }

    fn occurrence(&self, id: &OccurrenceId) -> Result<&Occurrence, LispError> {
        self.occurrences
            .iter()
            .find(|occurrence| &occurrence.id == id)
            .ok_or_else(|| LispError::Module(format!("missing occurrence {id}")))
    }

    fn lower_term(
        &mut self,
        term: &ProgramTerm,
        scope: &mut ResourceScope,
        current_module: &ModuleName,
    ) -> Result<Vec<WireRef>, LispError> {
        match term {
            ProgramTerm::Use { port } => scope.consume(port),
            ProgramTerm::Constant { value } => {
                let operation = OperationRef::constant(*value);
                self.lower_operation(operation, Vec::new())
            }
            ProgramTerm::Frontier { terms } => {
                let mut result = Vec::new();
                for term in terms {
                    result.extend(self.lower_term(term, scope, current_module)?);
                }
                Ok(result)
            }
            ProgramTerm::Apply {
                operation,
                arguments,
            } => {
                let mut inputs = Vec::new();
                for argument in arguments {
                    inputs.extend(self.lower_term(argument, scope, current_module)?);
                }
                self.lower_operation(operation.clone(), inputs)
            }
            ProgramTerm::Call {
                function,
                arguments,
            } => self.lower_call(function, arguments, scope, current_module),
        }
    }

    fn lower_call(
        &mut self,
        function: &QualifiedName,
        arguments: &[ProgramTerm],
        caller_scope: &mut ResourceScope,
        current_module: &ModuleName,
    ) -> Result<Vec<WireRef>, LispError> {
        self.ensure_call_is_visible(current_module, function)?;
        if self.call_stack.contains(function) {
            return Err(LispError::Module(format!(
                "recursive call to {function} is outside PSC0"
            )));
        }
        let definition = self
            .linked
            .function(&function.module, &function.function)?
            .clone();
        let mut argument_wires = Vec::new();
        for argument in arguments {
            argument_wires.extend(self.lower_term(argument, caller_scope, current_module)?);
        }
        if argument_wires.len() != definition.signature.inputs.len() {
            return Err(LispError::Type(format!(
                "call to {function} expects {} inputs, got {}",
                definition.signature.inputs.len(),
                argument_wires.len()
            )));
        }
        for (wire, port) in argument_wires
            .iter()
            .zip(definition.signature.inputs.ports())
        {
            if wire.value_type != port.value_type {
                return Err(LispError::Type(format!(
                    "call to {function} passes {:?} to {}:{:?}",
                    wire.value_type, port.name, port.value_type
                )));
            }
        }

        self.history.push(HistoryEvent::Call {
            function: function.clone(),
        });
        self.call_stack.push(function.clone());
        let mut callee_scope = ResourceScope::from_pairs(
            definition
                .signature
                .inputs
                .iter()
                .zip(argument_wires)
                .map(|(port, wire)| (port.name.clone(), wire)),
        );
        let outputs = self.lower_term(&definition.body, &mut callee_scope, &function.module)?;
        callee_scope.ensure_consumed(function)?;
        self.call_stack.pop();
        check_output_types(function, &definition, &outputs)?;
        Ok(outputs)
    }

    fn ensure_call_is_visible(
        &self,
        current_module: &ModuleName,
        function: &QualifiedName,
    ) -> Result<(), LispError> {
        if current_module == &function.module {
            return Ok(());
        }
        let module = self.linked.module(current_module)?;
        let visible = module.imports.iter().any(|import| {
            import.module == function.module && import.names.contains(&function.function)
        });
        if visible {
            Ok(())
        } else {
            Err(LispError::Module(format!(
                "module {current_module} does not import {function}"
            )))
        }
    }

    fn lower_operation(
        &mut self,
        operation: OperationRef,
        inputs: Vec<WireRef>,
    ) -> Result<Vec<WireRef>, LispError> {
        let spec = resolve_operation(&operation)?;
        spec.validate_wires(&inputs)?;
        match spec.lineage_rule {
            LineageRule::Copy => self.emit_copy(operation, inputs, spec.output_types.to_vec()),
            LineageRule::Discard => {
                self.emit_discard(operation, inputs, spec.output_types.to_vec())
            }
            LineageRule::Swap => self.emit_swap(operation, inputs, spec.output_types.to_vec()),
            LineageRule::MergeInputs => {
                self.emit_operation(operation, inputs, spec.output_types.to_vec())
            }
        }
    }

    fn emit_copy(
        &mut self,
        operation: OperationRef,
        inputs: Vec<WireRef>,
        output_types: Vec<ValueType>,
    ) -> Result<Vec<WireRef>, LispError> {
        let input = &inputs[0];
        let node = self.fresh_node();
        let mut output_lineages = [Vec::new(), Vec::new()];
        for parent in &input.lineage {
            let occurrence = self.occurrence(parent)?.clone();
            let mut children = Vec::new();
            for (branch, output_lineage) in output_lineages.iter_mut().enumerate() {
                let child = self.fresh_occurrence(
                    occurrence.source.clone(),
                    occurrence.path.branch(branch as u32),
                );
                output_lineage.push(child.clone());
                children.push(child);
            }
            self.history.push(HistoryEvent::Copy {
                node,
                parent: parent.clone(),
                children,
            });
        }
        self.nodes.push(OperationNode {
            id: node,
            operation: operation.clone(),
            inputs,
            output_types: output_types.clone(),
        });
        self.history
            .push(HistoryEvent::Operation { node, operation });
        Ok(output_lineages
            .into_iter()
            .zip(output_types)
            .enumerate()
            .map(|(index, (lineage, value_type))| WireRef {
                producer: WireProducer::Node { node },
                output_index: index as u32,
                value_type,
                lineage,
            })
            .collect())
    }

    fn emit_discard(
        &mut self,
        operation: OperationRef,
        inputs: Vec<WireRef>,
        output_types: Vec<ValueType>,
    ) -> Result<Vec<WireRef>, LispError> {
        let node = self.fresh_node();
        self.nodes.push(OperationNode {
            id: node,
            operation: operation.clone(),
            inputs,
            output_types,
        });
        self.history
            .push(HistoryEvent::Operation { node, operation });
        Ok(Vec::new())
    }

    fn emit_swap(
        &mut self,
        operation: OperationRef,
        inputs: Vec<WireRef>,
        output_types: Vec<ValueType>,
    ) -> Result<Vec<WireRef>, LispError> {
        let node = self.fresh_node();
        let lineages = [inputs[1].lineage.clone(), inputs[0].lineage.clone()];
        self.nodes.push(OperationNode {
            id: node,
            operation: operation.clone(),
            inputs,
            output_types: output_types.clone(),
        });
        self.history
            .push(HistoryEvent::Operation { node, operation });
        Ok(lineages
            .into_iter()
            .zip(output_types)
            .enumerate()
            .map(|(index, (lineage, value_type))| WireRef {
                producer: WireProducer::Node { node },
                output_index: index as u32,
                value_type,
                lineage,
            })
            .collect())
    }

    fn emit_operation(
        &mut self,
        operation: OperationRef,
        inputs: Vec<WireRef>,
        output_types: Vec<ValueType>,
    ) -> Result<Vec<WireRef>, LispError> {
        let node = self.fresh_node();
        let lineage = inputs
            .iter()
            .flat_map(|wire| wire.lineage.iter().cloned())
            .collect::<Vec<_>>();
        self.nodes.push(OperationNode {
            id: node,
            operation: operation.clone(),
            inputs,
            output_types: output_types.clone(),
        });
        self.history
            .push(HistoryEvent::Operation { node, operation });
        Ok(output_types
            .into_iter()
            .enumerate()
            .map(|(index, value_type)| WireRef {
                producer: WireProducer::Node { node },
                output_index: index as u32,
                value_type,
                lineage: lineage.clone(),
            })
            .collect())
    }
}

pub fn compile_function(
    linked: &LinkedModules,
    module: &str,
    function: &str,
) -> Result<CompilationArtifact, LispError> {
    let module_name = ModuleName::explicit(module);
    let function_name = FunctionName::explicit(function);
    let qualified = QualifiedName {
        module: module_name.clone(),
        function: function_name.clone(),
    };
    let definition = linked.function(&module_name, &function_name)?.clone();
    let mut compiler = Compiler::new(linked);
    compiler.call_stack.push(qualified.clone());

    let mut input_wires = Vec::new();
    for (index, port) in definition.signature.inputs.ports().iter().enumerate() {
        let source =
            SourceId::explicit(format!("source:{module}/{function}:{index}:{}", port.name));
        let occurrence = compiler.fresh_occurrence(source.clone(), OccurrencePath::root());
        compiler.history.push(HistoryEvent::Source {
            source,
            occurrence: occurrence.clone(),
        });
        input_wires.push((
            port.name.clone(),
            WireRef {
                producer: WireProducer::Input {
                    index: index as u32,
                },
                output_index: 0,
                value_type: port.value_type,
                lineage: vec![occurrence],
            },
        ));
    }
    let mut scope = ResourceScope::from_pairs(input_wires);
    let outputs = compiler.lower_term(&definition.body, &mut scope, &module_name)?;
    scope.ensure_consumed(&qualified)?;
    check_output_types(&qualified, &definition, &outputs)?;

    let diagram = SharedProgramDiagram {
        schema: IR_SCHEMA.to_owned(),
        version: IR_VERSION,
        module: module_name,
        function: qualified,
        signature: definition.signature.clone(),
        nodes: compiler.nodes,
        outputs,
        occurrences: compiler.occurrences,
        history: History {
            prefix: compiler.history,
            occurrence_paths: compiler.occurrence_paths,
            rewrite_trace: Vec::new(),
        },
    };
    validate_diagram_ref(&diagram)?;
    let certificate = CompilationCertificate {
        id: CertificateId::explicit(format!("compile:{module}/{function}:v1")),
        scope: "PSC0 finite acyclic module lowering".to_owned(),
        boundary: definition.signature,
        module_links: CheckStatus::Checked,
        linear_use: CheckStatus::Checked,
        types: CheckStatus::Checked,
        call_history: CheckStatus::Checked,
        diagram_integrity: CheckStatus::Checked,
    };
    Ok(CompilationArtifact {
        result: diagram,
        certificate,
    })
}

fn check_output_types(
    function: &QualifiedName,
    definition: &FunctionDefinition,
    outputs: &[WireRef],
) -> Result<(), LispError> {
    let actual = outputs
        .iter()
        .map(|wire| wire.value_type)
        .collect::<Vec<_>>();
    if actual.as_slice() == definition.signature.outputs.types() {
        Ok(())
    } else {
        Err(LispError::Type(format!(
            "function {function} declares outputs {:?}, got {actual:?}",
            definition.signature.outputs
        )))
    }
}
