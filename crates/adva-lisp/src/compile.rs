use crate::operation::{LineageRule, resolve_operation};
use crate::validate::validate_diagram_ref;
use crate::{LinkedModules, LispError};
use adva_ir::{
    CertificateId, CheckStatus, CompilationArtifact, CompilationCertificate, FunctionDefinition,
    FunctionName, GraftArgumentRegion, GraftFrame, GraftFrameId, GraftFrameKind, GraftHoleBinding,
    GraftPathStep, GraftRegionRole, GraftScopePath, GraftTrace, GraftTraceArtifact,
    GraftTraceCertificate, History, HistoryEvent, IR_SCHEMA, IR_VERSION, ModuleName, NodeId,
    Occurrence, OccurrenceId, OccurrencePath, OperationNode, OperationRef, ProgramTerm,
    QualifiedName, SharedProgramDiagram, SourceId, ValueType, WireProducer, WireRef,
};
use std::collections::{BTreeMap, BTreeSet};

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

#[derive(Clone, Debug)]
struct LoweringContext {
    parent_frame: GraftFrameId,
    path: GraftScopePath,
    region_in_parent: GraftRegionRole,
}

impl LoweringContext {
    fn child(&self, step: GraftPathStep) -> Self {
        Self {
            parent_frame: self.parent_frame.clone(),
            path: self.path.child(step),
            region_in_parent: self.region_in_parent.clone(),
        }
    }

    fn inside_frame(
        frame: GraftFrameId,
        path: GraftScopePath,
        region_in_parent: GraftRegionRole,
    ) -> Self {
        Self {
            parent_frame: frame,
            path,
            region_in_parent,
        }
    }
}

struct Compiler<'a> {
    linked: &'a LinkedModules,
    root_function: QualifiedName,
    nodes: Vec<OperationNode>,
    occurrences: Vec<Occurrence>,
    history: Vec<HistoryEvent>,
    occurrence_paths: BTreeMap<OccurrenceId, OccurrencePath>,
    next_node: u32,
    next_occurrence: u32,
    call_stack: Vec<QualifiedName>,
    graft_frames: Vec<Option<GraftFrame>>,
}

impl<'a> Compiler<'a> {
    fn new(linked: &'a LinkedModules, root_function: QualifiedName) -> Self {
        Self {
            linked,
            root_function,
            nodes: Vec::new(),
            occurrences: Vec::new(),
            history: Vec::new(),
            occurrence_paths: BTreeMap::new(),
            next_node: 0,
            next_occurrence: 0,
            call_stack: Vec::new(),
            graft_frames: Vec::new(),
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

    fn root_frame_id(&self) -> GraftFrameId {
        GraftFrameId::explicit(format!("graft:{}:root", self.root_function))
    }

    fn call_frame_id(&self, path: &GraftScopePath) -> GraftFrameId {
        GraftFrameId::explicit(format!(
            "graft:{}:{}",
            self.root_function,
            scope_path_key(path)
        ))
    }

    fn reserve_graft_frame(&mut self) -> usize {
        let slot = self.graft_frames.len();
        self.graft_frames.push(None);
        slot
    }

    fn set_graft_frame(&mut self, slot: usize, frame: GraftFrame) -> Result<(), LispError> {
        let target = self
            .graft_frames
            .get_mut(slot)
            .ok_or_else(|| LispError::Module(format!("missing graft frame slot {slot}")))?;
        if target.is_some() {
            return Err(LispError::Module(format!(
                "graft frame slot {slot} was finalized twice"
            )));
        }
        *target = Some(frame);
        Ok(())
    }

    fn node_region(&self, start: usize) -> Vec<NodeId> {
        self.nodes[start..].iter().map(|node| node.id).collect()
    }

    fn finalized_graft_trace(&self, root: GraftFrameId) -> Result<GraftTrace, LispError> {
        let mut frames = self
            .graft_frames
            .iter()
            .enumerate()
            .map(|(slot, frame)| {
                frame.clone().ok_or_else(|| {
                    LispError::Module(format!("graft frame slot {slot} was not finalized"))
                })
            })
            .collect::<Result<Vec<_>, _>>()?;
        let positions = frames
            .iter()
            .enumerate()
            .map(|(index, frame)| (frame.id.clone(), index))
            .collect::<BTreeMap<_, _>>();
        if positions.len() != frames.len() {
            return Err(LispError::Module(
                "deterministic graft frame paths are not unique".to_owned(),
            ));
        }
        let relations = frames
            .iter()
            .filter_map(|frame| {
                frame
                    .parent
                    .as_ref()
                    .map(|parent| (parent.clone(), frame.id.clone()))
            })
            .collect::<Vec<_>>();
        for (parent, child) in relations {
            let parent_index = positions.get(&parent).copied().ok_or_else(|| {
                LispError::Module(format!("graft frame {child} has missing parent {parent}"))
            })?;
            frames[parent_index].children.push(child);
        }
        Ok(GraftTrace { root, frames })
    }

    fn lower_term(
        &mut self,
        term: &ProgramTerm,
        scope: &mut ResourceScope,
        current_module: &ModuleName,
        context: &LoweringContext,
    ) -> Result<Vec<WireRef>, LispError> {
        match term {
            ProgramTerm::Use { port } => scope.consume(port),
            ProgramTerm::Constant { value } => {
                let operation = OperationRef::constant(*value);
                self.lower_operation(operation, Vec::new())
            }
            ProgramTerm::Frontier { terms } => {
                let mut result = Vec::new();
                for (index, term) in terms.iter().enumerate() {
                    let context = context.child(GraftPathStep::FrontierTerm {
                        index: checked_u32(index, "frontier term index")?,
                    });
                    result.extend(self.lower_term(term, scope, current_module, &context)?);
                }
                Ok(result)
            }
            ProgramTerm::Apply {
                operation,
                arguments,
            } => {
                let mut inputs = Vec::new();
                for (index, argument) in arguments.iter().enumerate() {
                    let context = context.child(GraftPathStep::ApplyArgument {
                        index: checked_u32(index, "operation argument index")?,
                    });
                    inputs.extend(self.lower_term(argument, scope, current_module, &context)?);
                }
                self.lower_operation(operation.clone(), inputs)
            }
            ProgramTerm::Call {
                function,
                arguments,
            } => self.lower_boundary_substitution(
                function,
                arguments,
                scope,
                current_module,
                context,
            ),
        }
    }

    /// Graft actual argument programs into the callee's ordered open boundary.
    ///
    /// This is PSC0's bounded substitution mechanism. It introduces no local
    /// binder or implicit sharing; each argument is lowered under the caller's
    /// linear resource scope before the finite callee body is instantiated.
    fn lower_boundary_substitution(
        &mut self,
        function: &QualifiedName,
        arguments: &[ProgramTerm],
        caller_scope: &mut ResourceScope,
        current_module: &ModuleName,
        context: &LoweringContext,
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
        let caller = self
            .call_stack
            .last()
            .cloned()
            .ok_or_else(|| LispError::Module("missing caller frame".to_owned()))?;
        let frame_id = self.call_frame_id(&context.path);
        let frame_slot = self.reserve_graft_frame();
        let mut argument_regions = Vec::new();
        let mut argument_outputs = Vec::new();
        for (argument_index, argument) in arguments.iter().enumerate() {
            let argument_index = checked_u32(argument_index, "call argument index")?;
            let start = self.nodes.len();
            let argument_context = LoweringContext::inside_frame(
                frame_id.clone(),
                context.path.child(GraftPathStep::CallArgument {
                    index: argument_index,
                }),
                GraftRegionRole::Argument {
                    index: argument_index,
                },
            );
            let outputs =
                self.lower_term(argument, caller_scope, current_module, &argument_context)?;
            let nodes = self.node_region(start);
            for (output_index, wire) in outputs.iter().enumerate() {
                argument_outputs.push((
                    argument_index,
                    checked_u32(output_index, "call argument output index")?,
                    wire.clone(),
                ));
            }
            argument_regions.push(GraftArgumentRegion {
                argument_index,
                nodes,
                outputs,
            });
        }
        if argument_outputs.len() != definition.signature.inputs.len() {
            return Err(LispError::Type(format!(
                "call to {function} expects {} inputs, got {}",
                definition.signature.inputs.len(),
                argument_outputs.len()
            )));
        }
        for ((_, _, wire), port) in argument_outputs
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

        let call_history_index = checked_u32(self.history.len(), "call history index")?;
        self.history.push(HistoryEvent::Call {
            function: function.clone(),
        });
        let entry_wires = argument_outputs
            .iter()
            .map(|(_, _, wire)| wire.clone())
            .collect::<Vec<_>>();
        let holes = definition
            .signature
            .inputs
            .ports()
            .iter()
            .cloned()
            .zip(argument_outputs.iter())
            .enumerate()
            .map(
                |(hole_index, (hole, (argument_index, argument_output_index, wire)))| {
                    Ok(GraftHoleBinding {
                        hole_index: checked_u32(hole_index, "callee hole index")?,
                        hole,
                        argument_index: Some(*argument_index),
                        argument_output_index: *argument_output_index,
                        entry_wire: wire.clone(),
                    })
                },
            )
            .collect::<Result<Vec<_>, LispError>>()?;
        self.call_stack.push(function.clone());
        let mut callee_scope = ResourceScope::from_pairs(
            definition
                .signature
                .inputs
                .iter()
                .zip(entry_wires.iter().cloned())
                .map(|(port, wire)| (port.name.clone(), wire)),
        );
        let body_start = self.nodes.len();
        let body_context = LoweringContext::inside_frame(
            frame_id.clone(),
            context.path.child(GraftPathStep::CalleeBody),
            GraftRegionRole::CalleeBody,
        );
        let outputs = self.lower_term(
            &definition.body,
            &mut callee_scope,
            &function.module,
            &body_context,
        );
        self.call_stack.pop();
        let outputs = outputs?;
        callee_scope.ensure_consumed(function)?;
        check_output_types(function, &definition, &outputs)?;
        let frame = GraftFrame {
            id: frame_id,
            scope_path: context.path.clone(),
            kind: GraftFrameKind::Call,
            parent: Some(context.parent_frame.clone()),
            children: Vec::new(),
            region_in_parent: context.region_in_parent.clone(),
            caller,
            callee: function.clone(),
            boundary: definition.signature.clone(),
            arguments: argument_regions,
            holes,
            body_region: self.node_region(body_start),
            entry_wires,
            exit_wires: outputs.clone(),
            call_history_index: Some(call_history_index),
        };
        self.set_graft_frame(frame_slot, frame)?;
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
    let mut compiler = Compiler::new(linked, qualified.clone());
    compiler.call_stack.push(qualified.clone());
    let root_frame_id = compiler.root_frame_id();
    let root_frame_slot = compiler.reserve_graft_frame();

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
    let root_entry_wires = input_wires
        .iter()
        .map(|(_, wire)| wire.clone())
        .collect::<Vec<_>>();
    let mut scope = ResourceScope::from_pairs(input_wires);
    let root_context = LoweringContext::inside_frame(
        root_frame_id.clone(),
        GraftScopePath::new(vec![GraftPathStep::RootBody]),
        GraftRegionRole::RootBody,
    );
    let outputs = compiler.lower_term(&definition.body, &mut scope, &module_name, &root_context)?;
    scope.ensure_consumed(&qualified)?;
    check_output_types(&qualified, &definition, &outputs)?;
    let root_holes = definition
        .signature
        .inputs
        .ports()
        .iter()
        .cloned()
        .zip(root_entry_wires.iter().cloned())
        .enumerate()
        .map(|(hole_index, (hole, entry_wire))| {
            Ok(GraftHoleBinding {
                hole_index: checked_u32(hole_index, "root hole index")?,
                hole,
                argument_index: None,
                argument_output_index: 0,
                entry_wire,
            })
        })
        .collect::<Result<Vec<_>, LispError>>()?;
    compiler.set_graft_frame(
        root_frame_slot,
        GraftFrame {
            id: root_frame_id.clone(),
            scope_path: GraftScopePath::default(),
            kind: GraftFrameKind::Root,
            parent: None,
            children: Vec::new(),
            region_in_parent: GraftRegionRole::Root,
            caller: qualified.clone(),
            callee: qualified.clone(),
            boundary: definition.signature.clone(),
            arguments: Vec::new(),
            holes: root_holes,
            body_region: compiler.node_region(0),
            entry_wires: root_entry_wires,
            exit_wires: outputs.clone(),
            call_history_index: None,
        },
    )?;
    let graft_trace = compiler.finalized_graft_trace(root_frame_id)?;

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
    let graft_trace_certificate = validate_graft_trace(&diagram, &graft_trace)?;
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
        graft_trace: GraftTraceArtifact {
            result: graft_trace,
            certificate: graft_trace_certificate,
        },
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

fn checked_u32(value: usize, label: &str) -> Result<u32, LispError> {
    u32::try_from(value).map_err(|_| LispError::Module(format!("{label} exceeds u32")))
}

fn scope_path_key(path: &GraftScopePath) -> String {
    path.steps()
        .iter()
        .map(|step| match step {
            GraftPathStep::RootBody => "root-body".to_owned(),
            GraftPathStep::ApplyArgument { index } => format!("apply-{index}"),
            GraftPathStep::FrontierTerm { index } => format!("frontier-{index}"),
            GraftPathStep::CallArgument { index } => format!("call-argument-{index}"),
            GraftPathStep::CalleeBody => "callee-body".to_owned(),
        })
        .collect::<Vec<_>>()
        .join("/")
}

fn expected_root_frame_id(function: &QualifiedName) -> GraftFrameId {
    GraftFrameId::explicit(format!("graft:{function}:root"))
}

fn expected_call_frame_id(function: &QualifiedName, path: &GraftScopePath) -> GraftFrameId {
    GraftFrameId::explicit(format!("graft:{function}:{}", scope_path_key(path)))
}

pub(crate) fn validate_graft_trace(
    diagram: &SharedProgramDiagram,
    trace: &GraftTrace,
) -> Result<GraftTraceCertificate, LispError> {
    validate_diagram_ref(diagram)?;
    if trace.frames.is_empty() {
        return graft_error("a graft trace must contain its root frame");
    }
    let positions = trace
        .frames
        .iter()
        .enumerate()
        .map(|(index, frame)| (frame.id.clone(), index))
        .collect::<BTreeMap<_, _>>();
    if positions.len() != trace.frames.len() {
        return graft_error("graft frame identifiers are not unique");
    }
    let root_index = positions
        .get(&trace.root)
        .copied()
        .ok_or_else(|| LispError::Validation("graft trace root is missing".to_owned()))?;
    let expected_root = expected_root_frame_id(&diagram.function);
    if trace.root != expected_root {
        return graft_error(format!(
            "graft trace root {} differs from deterministic root {expected_root}",
            trace.root
        ));
    }

    let known_nodes = diagram
        .nodes
        .iter()
        .map(|node| node.id)
        .collect::<BTreeSet<_>>();
    let diagram_wires = diagram
        .nodes
        .iter()
        .flat_map(|node| node.inputs.iter())
        .chain(diagram.outputs.iter())
        .collect::<Vec<_>>();
    let mut expected_children = trace
        .frames
        .iter()
        .map(|frame| (frame.id.clone(), Vec::new()))
        .collect::<BTreeMap<_, _>>();
    for frame in &trace.frames {
        if let Some(parent) = &frame.parent {
            let children = expected_children.get_mut(parent).ok_or_else(|| {
                LispError::Validation(format!(
                    "graft frame {} has missing parent {parent}",
                    frame.id
                ))
            })?;
            children.push(frame.id.clone());
        }
    }

    let mut linked_call_events = BTreeSet::new();
    for (frame_index, frame) in trace.frames.iter().enumerate() {
        let expected_id = match frame.kind {
            GraftFrameKind::Root => expected_root_frame_id(&diagram.function),
            GraftFrameKind::Call => expected_call_frame_id(&diagram.function, &frame.scope_path),
        };
        if frame.id != expected_id {
            return graft_error(format!(
                "graft frame {} differs from deterministic path identifier {expected_id}",
                frame.id
            ));
        }
        if frame.children != expected_children[&frame.id] {
            return graft_error(format!(
                "graft frame {} children do not match parent links",
                frame.id
            ));
        }
        validate_frame_shape(
            diagram,
            trace,
            frame_index,
            root_index,
            frame,
            &positions,
            &known_nodes,
            &diagram_wires,
            &mut linked_call_events,
        )?;
    }

    let call_events = diagram
        .history
        .prefix
        .iter()
        .enumerate()
        .filter_map(|(index, event)| matches!(event, HistoryEvent::Call { .. }).then_some(index))
        .collect::<BTreeSet<_>>();
    if linked_call_events != call_events {
        return graft_error("graft frames do not link every call history event exactly once");
    }

    Ok(GraftTraceCertificate {
        id: CertificateId::explicit(format!("graft-trace:{}:v1", diagram.function)),
        scope: "compiler-emitted PSC0 finite nested call frames; unchanged adva.ir v1 diagram"
            .to_owned(),
        diagram_integrity: CheckStatus::Checked,
        deterministic_frame_ids: CheckStatus::Checked,
        parent_child_nesting: CheckStatus::Checked,
        ordered_hole_bindings: CheckStatus::Checked,
        argument_body_regions: CheckStatus::Checked,
        boundary_maps: CheckStatus::Checked,
        call_history_links: CheckStatus::Checked,
        frame_ids: trace.frames.iter().map(|frame| frame.id.clone()).collect(),
    })
}

#[allow(clippy::too_many_arguments)]
fn validate_frame_shape(
    diagram: &SharedProgramDiagram,
    trace: &GraftTrace,
    frame_index: usize,
    root_index: usize,
    frame: &GraftFrame,
    positions: &BTreeMap<GraftFrameId, usize>,
    known_nodes: &BTreeSet<NodeId>,
    diagram_wires: &[&WireRef],
    linked_call_events: &mut BTreeSet<usize>,
) -> Result<(), LispError> {
    validate_region(&frame.body_region, known_nodes, "graft body region")?;
    for wire in frame.entry_wires.iter().chain(frame.exit_wires.iter()) {
        if !diagram_wires.contains(&wire) {
            return graft_error(format!(
                "graft frame {} boundary contains a non-diagram wire",
                frame.id
            ));
        }
    }
    let exit_types = frame
        .exit_wires
        .iter()
        .map(|wire| wire.value_type)
        .collect::<Vec<_>>();
    if exit_types.as_slice() != frame.boundary.codomain().types() {
        return graft_error(format!(
            "graft frame {} exit wires do not match its codomain",
            frame.id
        ));
    }
    validate_arguments_and_holes(frame, known_nodes, diagram_wires)?;

    if frame_index == root_index {
        if frame.kind != GraftFrameKind::Root
            || frame.parent.is_some()
            || frame.region_in_parent != GraftRegionRole::Root
            || !frame.scope_path.steps().is_empty()
            || frame.caller != diagram.function
            || frame.callee != diagram.function
            || frame.boundary != diagram.signature
            || !frame.arguments.is_empty()
            || frame.call_history_index.is_some()
            || frame.body_region != diagram.nodes.iter().map(|node| node.id).collect::<Vec<_>>()
            || frame.exit_wires != diagram.outputs
        {
            return graft_error("the graft root frame does not match the compiled diagram");
        }
        return Ok(());
    }

    if frame.kind != GraftFrameKind::Call {
        return graft_error(format!("non-root graft frame {} is not a call", frame.id));
    }
    let parent_id = frame.parent.as_ref().ok_or_else(|| {
        LispError::Validation(format!("call graft frame {} has no parent", frame.id))
    })?;
    let parent = &trace.frames[positions[parent_id]];
    validate_scope_nesting(parent, frame)?;
    validate_child_region(parent, frame)?;

    let history_index = frame.call_history_index.ok_or_else(|| {
        LispError::Validation(format!("call graft frame {} has no history link", frame.id))
    })?;
    let history_index = usize::try_from(history_index)
        .map_err(|_| LispError::Validation("call history index exceeds usize".to_owned()))?;
    match diagram.history.prefix.get(history_index) {
        Some(HistoryEvent::Call { function }) if function == &frame.callee => {}
        _ => {
            return graft_error(format!(
                "graft frame {} does not match call history index {history_index}",
                frame.id
            ));
        }
    }
    if !linked_call_events.insert(history_index) {
        return graft_error(format!(
            "call history index {history_index} is linked more than once"
        ));
    }
    Ok(())
}

fn validate_arguments_and_holes(
    frame: &GraftFrame,
    known_nodes: &BTreeSet<NodeId>,
    diagram_wires: &[&WireRef],
) -> Result<(), LispError> {
    let mut argument_nodes = BTreeSet::new();
    for (index, argument) in frame.arguments.iter().enumerate() {
        if argument.argument_index != checked_u32(index, "graft argument index")? {
            return graft_error(format!(
                "graft frame {} argument indices are not ordered",
                frame.id
            ));
        }
        let nodes = validate_region(&argument.nodes, known_nodes, "graft argument region")?;
        if !argument_nodes.is_disjoint(&nodes) {
            return graft_error(format!("graft frame {} argument regions overlap", frame.id));
        }
        argument_nodes.extend(nodes);
        for wire in &argument.outputs {
            if !diagram_wires.contains(&wire) {
                return graft_error(format!(
                    "graft frame {} argument contains a non-diagram wire",
                    frame.id
                ));
            }
        }
    }
    let body_nodes = frame.body_region.iter().copied().collect::<BTreeSet<_>>();
    if !argument_nodes.is_disjoint(&body_nodes) {
        return graft_error(format!(
            "graft frame {} argument and callee-body regions overlap",
            frame.id
        ));
    }
    if frame.holes.len() != frame.boundary.domain().ports().len()
        || frame.entry_wires.len() != frame.holes.len()
    {
        return graft_error(format!(
            "graft frame {} hole boundary has the wrong arity",
            frame.id
        ));
    }
    for (index, ((binding, hole), entry_wire)) in frame
        .holes
        .iter()
        .zip(frame.boundary.domain().ports())
        .zip(frame.entry_wires.iter())
        .enumerate()
    {
        if binding.hole_index != checked_u32(index, "graft hole index")?
            || &binding.hole != hole
            || &binding.entry_wire != entry_wire
            || binding.entry_wire.value_type != hole.value_type
        {
            return graft_error(format!(
                "graft frame {} has an invalid ordered hole binding",
                frame.id
            ));
        }
        match binding.argument_index {
            None if frame.kind == GraftFrameKind::Root => {
                if binding.argument_output_index != 0
                    || binding.entry_wire.producer
                        != (WireProducer::Input {
                            index: binding.hole_index,
                        })
                {
                    return graft_error("root hole does not map to its exact program input");
                }
            }
            Some(argument_index) if frame.kind == GraftFrameKind::Call => {
                let argument_index = usize::try_from(argument_index).map_err(|_| {
                    LispError::Validation("graft argument index exceeds usize".to_owned())
                })?;
                let output_index =
                    usize::try_from(binding.argument_output_index).map_err(|_| {
                        LispError::Validation("graft argument output exceeds usize".to_owned())
                    })?;
                let output = frame
                    .arguments
                    .get(argument_index)
                    .and_then(|argument| argument.outputs.get(output_index));
                if output != Some(&binding.entry_wire) {
                    return graft_error(format!(
                        "graft frame {} hole does not map to its argument output",
                        frame.id
                    ));
                }
            }
            _ => {
                return graft_error(format!(
                    "graft frame {} mixes root and call hole binding kinds",
                    frame.id
                ));
            }
        }
    }
    Ok(())
}

fn validate_scope_nesting(parent: &GraftFrame, child: &GraftFrame) -> Result<(), LispError> {
    let parent_path = parent.scope_path.steps();
    let child_path = child.scope_path.steps();
    if child_path.len() <= parent_path.len() || !child_path.starts_with(parent_path) {
        return graft_error(format!(
            "graft frame {} path is not strictly nested under {}",
            child.id, parent.id
        ));
    }
    let first_descent = &child_path[parent_path.len()];
    let expected_role = match first_descent {
        GraftPathStep::RootBody if parent.kind == GraftFrameKind::Root => GraftRegionRole::RootBody,
        GraftPathStep::CallArgument { index } if parent.kind == GraftFrameKind::Call => {
            GraftRegionRole::Argument { index: *index }
        }
        GraftPathStep::CalleeBody if parent.kind == GraftFrameKind::Call => {
            GraftRegionRole::CalleeBody
        }
        _ => {
            return graft_error(format!(
                "graft frame {} path does not enter a parent scope region",
                child.id
            ));
        }
    };
    if child.region_in_parent != expected_role {
        return graft_error(format!(
            "graft frame {} region role disagrees with its scope path",
            child.id
        ));
    }
    let expected_caller = match child.region_in_parent {
        GraftRegionRole::RootBody | GraftRegionRole::Argument { .. } => &parent.caller,
        GraftRegionRole::CalleeBody => &parent.callee,
        GraftRegionRole::Root => {
            return graft_error("a child graft frame cannot have the root role");
        }
    };
    if &child.caller != expected_caller {
        return graft_error(format!(
            "graft frame {} caller disagrees with its parent region",
            child.id
        ));
    }
    Ok(())
}

fn validate_child_region(parent: &GraftFrame, child: &GraftFrame) -> Result<(), LispError> {
    let parent_region = match child.region_in_parent {
        GraftRegionRole::RootBody | GraftRegionRole::CalleeBody => &parent.body_region,
        GraftRegionRole::Argument { index } => {
            let index = usize::try_from(index).map_err(|_| {
                LispError::Validation("graft parent argument index exceeds usize".to_owned())
            })?;
            &parent
                .arguments
                .get(index)
                .ok_or_else(|| {
                    LispError::Validation(format!(
                        "graft frame {} references missing parent argument {index}",
                        child.id
                    ))
                })?
                .nodes
        }
        GraftRegionRole::Root => return graft_error("a child frame cannot occupy the root region"),
    };
    let parent_nodes = parent_region.iter().copied().collect::<BTreeSet<_>>();
    let child_nodes = child
        .arguments
        .iter()
        .flat_map(|argument| argument.nodes.iter().copied())
        .chain(child.body_region.iter().copied())
        .collect::<BTreeSet<_>>();
    if !child_nodes.is_subset(&parent_nodes) {
        return graft_error(format!(
            "graft frame {} contains nodes outside its parent region",
            child.id
        ));
    }
    Ok(())
}

fn validate_region(
    nodes: &[NodeId],
    known_nodes: &BTreeSet<NodeId>,
    label: &str,
) -> Result<BTreeSet<NodeId>, LispError> {
    let region = nodes.iter().copied().collect::<BTreeSet<_>>();
    if region.len() != nodes.len() {
        return graft_error(format!("{label} repeats a node"));
    }
    if !region.is_subset(known_nodes) {
        return graft_error(format!("{label} contains an unknown node"));
    }
    Ok(region)
}

fn graft_error<T>(message: impl Into<String>) -> Result<T, LispError> {
    Err(LispError::Validation(message.into()))
}
