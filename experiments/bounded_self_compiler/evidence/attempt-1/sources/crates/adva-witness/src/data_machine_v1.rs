//! A separately versioned, bounded research language for programs over data.
//! No PSC0 terms, identities, operations or certificate meanings are changed.
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

pub const DATA_MACHINE_PROGRAM_V1: &str = "adva.data-machine.program.research.v1";
pub const DATA_MACHINE_RUN_V1: &str = "adva.data-machine.run.research.v1";
pub const DATA_MACHINE_MAX_FUEL_V1: u32 = 200000;
pub const DATA_MACHINE_MAX_BYTES_V1: usize = 524288;
pub const DATA_MACHINE_MAX_REPORT_V1: usize = 64 * 1024 * 1024;
const MAX_STATE_NODES: usize = 131072;
const MAX_SEGMENTS: usize = 16;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachineDataV1 {
    Integer { value: i64 },
    Node { tag: u8, fields: Vec<MachineDataV1> },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MachineTypeV1 {
    Integer,
    Boolean,
    Data,
    Stack,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachineValueV1 {
    Integer { value: i64 },
    Boolean { value: bool },
    Data { value: MachineDataV1 },
    Stack { items: Vec<MachineDataV1> },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MachineRegisterV1 {
    pub name: String,
    pub kind: MachineTypeV1,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachineInstructionV1 {
    Length {
        src: usize,
        dst: usize,
    },
    FieldDynamic {
        src: usize,
        index: usize,
        dst: usize,
    },
    Pack {
        stack: usize,
        tag: u8,
        dst: usize,
    },
    StackLength {
        stack: usize,
        dst: usize,
    },
    Input {
        dst: usize,
    },
    Constant {
        dst: usize,
        value: i64,
    },
    Copy {
        src: usize,
        dst: usize,
    },
    Clear {
        stack: usize,
    },
    Push {
        stack: usize,
        src: usize,
    },
    Pop {
        stack: usize,
        dst: usize,
    },
    IsEmpty {
        stack: usize,
        dst: usize,
    },
    Tag {
        src: usize,
        dst: usize,
    },
    Field {
        src: usize,
        arity: usize,
        index: usize,
        dst: usize,
    },
    AsInteger {
        src: usize,
        dst: usize,
    },
    BoxInteger {
        src: usize,
        dst: usize,
    },
    Node {
        tag: u8,
        fields: Vec<usize>,
        dst: usize,
    },
    Add {
        left: usize,
        right: usize,
        dst: usize,
    },
    Multiply {
        left: usize,
        right: usize,
        dst: usize,
    },
    Equal {
        left: usize,
        right: usize,
        dst: usize,
    },
    Jump {
        target: usize,
    },
    Branch {
        condition: usize,
        yes: usize,
        no: usize,
    },
    Return {
        src: usize,
    },
    Reject {
        reason: String,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DataMachineProgramV1 {
    pub schema: String,
    pub name: String,
    pub registers: Vec<MachineRegisterV1>,
    pub code: Vec<MachineInstructionV1>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachinePhaseV1 {
    Running,
    Returned { value: MachineDataV1 },
    Rejected { reason: String },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DataMachineStateV1 {
    pub pc: usize,
    pub registers: Vec<Option<MachineValueV1>>,
    pub spent: u32,
    pub phase: MachinePhaseV1,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MachineEventV1 {
    pub pc: usize,
    pub next_pc: usize,
    pub state_digest: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum DataMachineStatusV1 {
    Returned,
    Rejected,
    Suspended,
    FuelExhausted,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MachineSegmentV1 {
    pub start: u32,
    pub end: u32,
    pub replayed: u32,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DataMachineRunV1 {
    pub schema: String,
    pub profile: String,
    pub program: DataMachineProgramV1,
    pub input: MachineDataV1,
    pub fuel: u32,
    pub state: DataMachineStateV1,
    pub trace: Vec<MachineEventV1>,
    pub status: DataMachineStatusV1,
    pub segments: Vec<MachineSegmentV1>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct DataMachineReceptionV1 {
    pub profile: String,
    pub verified_steps: u32,
    pub state: DataMachineStateV1,
}

pub fn data_machine_profile_v1() -> String {
    let mut h = blake3::Hasher::new();
    h.update(b"adva.data-machine.transition.v1\0");
    h.update(include_bytes!("data_machine_v1.rs"));
    h.update(include_bytes!("../../../Cargo.lock"));
    h.finalize().to_hex().to_string()
}

fn data_size(value: &MachineDataV1) -> Result<usize, String> {
    let mut pending = vec![(value, 1)];
    let mut count = 0;
    while let Some((node, depth)) = pending.pop() {
        count += 1;
        if count > 16384 || depth > 48 {
            return Err("data capacity exceeded".into());
        }
        if let MachineDataV1::Node { fields, .. } = node {
            if fields.len() > 2048 {
                return Err("node arity exceeds 2048".into());
            }
            pending.extend(fields.iter().map(|child| (child, depth + 1)));
        }
    }
    Ok(count)
}

fn check_state(state: &DataMachineStateV1) -> Result<(), String> {
    let mut nodes = 0;
    for value in state.registers.iter().flatten() {
        nodes += match value {
            MachineValueV1::Data { value } => data_size(value)?,
            MachineValueV1::Stack { items } => {
                if items.len() > 4096 {
                    return Err("stack capacity exceeded".into());
                }
                items
                    .iter()
                    .try_fold(0, |n, d| Ok::<_, String>(n + data_size(d)?))?
            }
            _ => 1,
        };
    }
    if let MachinePhaseV1::Returned { value } = &state.phase {
        nodes += data_size(value)?;
    }
    if nodes > MAX_STATE_NODES {
        return Err("state capacity exceeded".into());
    }
    Ok(())
}

pub fn validate_data_machine_program_v1(program: &DataMachineProgramV1) -> Result<(), String> {
    use MachineInstructionV1 as I;
    use MachineTypeV1 as T;
    if program.schema != DATA_MACHINE_PROGRAM_V1
        || program.name.is_empty()
        || program.name.len() > 64
        || program.registers.is_empty()
        || program.registers.len() > 64
        || program.code.is_empty()
        || program.code.len() > 2048
    {
        return Err("invalid program schema or capacity".into());
    }
    let mut names = BTreeSet::new();
    for register in &program.registers {
        if register.name.is_empty()
            || register.name.len() > 32
            || !register
                .name
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || b == b'_')
            || !names.insert(&register.name)
        {
            return Err("invalid or duplicate register name".into());
        }
    }
    let reg = |index: usize, kind: T| -> Result<(), String> {
        if program.registers.get(index).map(|r| r.kind) != Some(kind) {
            return Err("register type/index mismatch".into());
        }
        Ok(())
    };
    let jump = |target: usize| -> Result<(), String> {
        if target >= program.code.len() {
            return Err("jump outside program".into());
        }
        Ok(())
    };
    for instruction in &program.code {
        match instruction {
            I::Length { src, dst } => {
                reg(*src, T::Data)?;
                reg(*dst, T::Integer)?;
            }
            I::FieldDynamic { src, index, dst } => {
                reg(*src, T::Data)?;
                reg(*index, T::Integer)?;
                reg(*dst, T::Data)?;
            }
            I::Pack { stack, dst, .. } => {
                reg(*stack, T::Stack)?;
                reg(*dst, T::Data)?;
            }
            I::StackLength { stack, dst } => {
                reg(*stack, T::Stack)?;
                reg(*dst, T::Integer)?;
            }
            I::Input { dst } => reg(*dst, T::Data)?,
            I::Constant { dst, .. } => reg(*dst, T::Integer)?,
            I::Copy { src, dst } => {
                let kind = program
                    .registers
                    .get(*src)
                    .ok_or("copy index outside program")?
                    .kind;
                reg(*dst, kind)?;
            }
            I::Clear { stack } => reg(*stack, T::Stack)?,
            I::Push { stack, src } => {
                reg(*stack, T::Stack)?;
                reg(*src, T::Data)?;
            }
            I::Pop { stack, dst } => {
                reg(*stack, T::Stack)?;
                reg(*dst, T::Data)?;
            }
            I::IsEmpty { stack, dst } => {
                reg(*stack, T::Stack)?;
                reg(*dst, T::Boolean)?;
            }
            I::Tag { src, dst } | I::AsInteger { src, dst } => {
                reg(*src, T::Data)?;
                reg(*dst, T::Integer)?;
            }
            I::BoxInteger { src, dst } => {
                reg(*src, T::Integer)?;
                reg(*dst, T::Data)?;
            }
            I::Field {
                src,
                arity,
                index,
                dst,
            } => {
                reg(*src, T::Data)?;
                reg(*dst, T::Data)?;
                if *arity > 2048 || index >= arity {
                    return Err("invalid field shape".into());
                }
            }
            I::Node { fields, dst, .. } => {
                reg(*dst, T::Data)?;
                if fields.len() > 2048 {
                    return Err("node arity exceeds 2048".into());
                }
                for field in fields {
                    reg(*field, T::Data)?;
                }
            }
            I::Add { left, right, dst } | I::Multiply { left, right, dst } => {
                reg(*left, T::Integer)?;
                reg(*right, T::Integer)?;
                reg(*dst, T::Integer)?;
            }
            I::Equal { left, right, dst } => {
                reg(*left, T::Integer)?;
                reg(*right, T::Integer)?;
                reg(*dst, T::Boolean)?;
            }
            I::Jump { target } => jump(*target)?,
            I::Branch { condition, yes, no } => {
                reg(*condition, T::Boolean)?;
                jump(*yes)?;
                jump(*no)?;
            }
            I::Return { src } => reg(*src, T::Data)?,
            I::Reject { reason } => {
                if reason.is_empty() || reason.len() > 128 {
                    return Err("invalid rejection reason".into());
                }
            }
        }
    }
    if !matches!(
        program.code.last(),
        Some(I::Return { .. } | I::Reject { .. } | I::Jump { .. } | I::Branch { .. })
    ) {
        return Err("program can fall off its last instruction".into());
    }
    if serde_json::to_vec(program)
        .map_err(|e| e.to_string())?
        .len()
        > DATA_MACHINE_MAX_BYTES_V1
    {
        return Err("program exceeds byte limit".into());
    }
    Ok(())
}

fn initial(program: &DataMachineProgramV1) -> DataMachineStateV1 {
    DataMachineStateV1 {
        pc: 0,
        registers: vec![None; program.registers.len()],
        spent: 0,
        phase: MachinePhaseV1::Running,
    }
}

impl DataMachineStateV1 {
    fn value(&self, index: usize) -> Result<&MachineValueV1, String> {
        self.registers
            .get(index)
            .and_then(Option::as_ref)
            .ok_or_else(|| "uninitialized register".into())
    }
    fn data(&self, index: usize) -> Result<&MachineDataV1, String> {
        match self.value(index)? {
            MachineValueV1::Data { value } => Ok(value),
            _ => Err("expected data register".into()),
        }
    }
    fn integer(&self, index: usize) -> Result<i64, String> {
        match self.value(index)? {
            MachineValueV1::Integer { value } => Ok(*value),
            _ => Err("expected integer register".into()),
        }
    }
    fn stack(&self, index: usize) -> Result<&Vec<MachineDataV1>, String> {
        match self.value(index)? {
            MachineValueV1::Stack { items } => Ok(items),
            _ => Err("expected stack register".into()),
        }
    }
    fn set(&mut self, index: usize, value: MachineValueV1) {
        self.registers[index] = Some(value);
    }
}

fn apply(
    instruction: &MachineInstructionV1,
    input: &MachineDataV1,
    s: &mut DataMachineStateV1,
) -> Result<(), String> {
    use MachineInstructionV1 as I;
    use MachineValueV1 as V;
    s.pc += 1;
    match instruction {
        I::Length { src, dst } => {
            let MachineDataV1::Node { fields, .. } = s.data(*src)? else {
                return Err("expected node data".into());
            };
            s.set(
                *dst,
                V::Integer {
                    value: fields.len() as i64,
                },
            );
        }
        I::FieldDynamic { src, index, dst } => {
            let index = usize::try_from(s.integer(*index)?).map_err(|_| "negative field index")?;
            let MachineDataV1::Node { fields, .. } = s.data(*src)? else {
                return Err("expected node data".into());
            };
            let value = fields.get(index).ok_or("field index outside node")?.clone();
            s.set(*dst, V::Data { value });
        }
        I::Pack { stack, tag, dst } => {
            let value = MachineDataV1::Node {
                tag: *tag,
                fields: s.stack(*stack)?.clone(),
            };
            data_size(&value)?;
            s.set(*dst, V::Data { value });
        }
        I::StackLength { stack, dst } => {
            s.set(
                *dst,
                V::Integer {
                    value: s.stack(*stack)?.len() as i64,
                },
            );
        }
        I::Input { dst } => s.set(
            *dst,
            V::Data {
                value: input.clone(),
            },
        ),
        I::Constant { dst, value } => s.set(*dst, V::Integer { value: *value }),
        I::Copy { src, dst } => s.set(*dst, s.value(*src)?.clone()),
        I::Clear { stack } => s.set(*stack, V::Stack { items: vec![] }),
        I::Push { stack, src } => {
            let mut items = s.stack(*stack)?.clone();
            if items.len() >= 4096 {
                return Err("stack capacity exceeded".into());
            }
            items.push(s.data(*src)?.clone());
            s.set(*stack, V::Stack { items });
        }
        I::Pop { stack, dst } => {
            let mut items = s.stack(*stack)?.clone();
            let value = items.pop().ok_or("empty stack")?;
            s.set(*stack, V::Stack { items });
            s.set(*dst, V::Data { value });
        }
        I::IsEmpty { stack, dst } => s.set(
            *dst,
            V::Boolean {
                value: s.stack(*stack)?.is_empty(),
            },
        ),
        I::Tag { src, dst } => {
            let value = match s.data(*src)? {
                MachineDataV1::Integer { .. } => -1,
                MachineDataV1::Node { tag, .. } => i64::from(*tag),
            };
            s.set(*dst, V::Integer { value });
        }
        I::Field {
            src,
            arity,
            index,
            dst,
        } => {
            let value = match s.data(*src)? {
                MachineDataV1::Node { fields, .. } if fields.len() == *arity => {
                    fields[*index].clone()
                }
                _ => return Err("data shape mismatch".into()),
            };
            s.set(*dst, V::Data { value });
        }
        I::AsInteger { src, dst } => {
            let MachineDataV1::Integer { value } = s.data(*src)? else {
                return Err("expected integer data".into());
            };
            s.set(*dst, V::Integer { value: *value });
        }
        I::BoxInteger { src, dst } => s.set(
            *dst,
            V::Data {
                value: MachineDataV1::Integer {
                    value: s.integer(*src)?,
                },
            },
        ),
        I::Node { tag, fields, dst } => {
            let fields = fields
                .iter()
                .map(|r| s.data(*r).cloned())
                .collect::<Result<Vec<_>, _>>()?;
            let value = MachineDataV1::Node { tag: *tag, fields };
            data_size(&value)?;
            s.set(*dst, V::Data { value });
        }
        I::Add { left, right, dst } | I::Multiply { left, right, dst } => {
            let a = s.integer(*left)?;
            let b = s.integer(*right)?;
            let value = if matches!(instruction, I::Add { .. }) {
                a.checked_add(b)
            } else {
                a.checked_mul(b)
            }
            .ok_or("integer overflow")?;
            s.set(*dst, V::Integer { value });
        }
        I::Equal { left, right, dst } => s.set(
            *dst,
            V::Boolean {
                value: s.integer(*left)? == s.integer(*right)?,
            },
        ),
        I::Jump { target } => s.pc = *target,
        I::Branch { condition, yes, no } => {
            let V::Boolean { value } = s.value(*condition)? else {
                return Err("expected boolean register".into());
            };
            s.pc = if *value { *yes } else { *no };
        }
        I::Return { src } => {
            s.phase = MachinePhaseV1::Returned {
                value: s.data(*src)?.clone(),
            }
        }
        I::Reject { reason } => return Err(reason.clone()),
    }
    check_state(s)
}

fn step(
    program: &DataMachineProgramV1,
    input: &MachineDataV1,
    state: &mut DataMachineStateV1,
) -> Result<MachineEventV1, String> {
    if state.phase != MachinePhaseV1::Running {
        return Err("step after terminal state".into());
    }
    let pc = state.pc;
    let instruction = program.code.get(pc).ok_or("program counter outside code")?;
    let mut next = state.clone();
    if let Err(reason) = apply(instruction, input, &mut next) {
        next = state.clone(); // Failed instructions have no partial data writes.
        next.phase = MachinePhaseV1::Rejected { reason };
    }
    next.spent += 1;
    let state_digest = blake3::hash(&serde_json::to_vec(&next).map_err(|e| e.to_string())?)
        .to_hex()
        .to_string();
    let event = MachineEventV1 {
        pc,
        next_pc: next.pc,
        state_digest,
    };
    *state = next;
    Ok(event)
}

fn status(state: &DataMachineStateV1, fuel: u32) -> DataMachineStatusV1 {
    match state.phase {
        MachinePhaseV1::Returned { .. } => DataMachineStatusV1::Returned,
        MachinePhaseV1::Rejected { .. } => DataMachineStatusV1::Rejected,
        MachinePhaseV1::Running if state.spent == fuel => DataMachineStatusV1::FuelExhausted,
        MachinePhaseV1::Running => DataMachineStatusV1::Suspended,
    }
}

fn context(program: &DataMachineProgramV1, input: &MachineDataV1, fuel: u32) -> Result<(), String> {
    validate_data_machine_program_v1(program)?;
    data_size(input)?;
    if fuel > DATA_MACHINE_MAX_FUEL_V1 {
        return Err("fuel exceeds profile".into());
    }
    Ok(())
}

fn advance(
    mut run: DataMachineRunV1,
    quantum: u32,
    replayed: u32,
) -> Result<DataMachineRunV1, String> {
    if quantum > DATA_MACHINE_MAX_FUEL_V1 || run.segments.len() >= MAX_SEGMENTS {
        return Err("quantum or continuation count exceeds profile".into());
    }
    let start = run.state.spent;
    for _ in 0..quantum {
        if run.state.spent == run.fuel || run.state.phase != MachinePhaseV1::Running {
            break;
        }
        run.trace
            .push(step(&run.program, &run.input, &mut run.state)?);
    }
    run.status = status(&run.state, run.fuel);
    run.segments.push(MachineSegmentV1 {
        start,
        end: run.state.spent,
        replayed,
    });
    if serde_json::to_vec(&run).map_err(|e| e.to_string())?.len() > DATA_MACHINE_MAX_REPORT_V1 {
        return Err("run exceeds report capacity".into());
    }
    Ok(run)
}

pub fn run_data_machine_v1(
    program: &DataMachineProgramV1,
    input: &MachineDataV1,
    fuel: u32,
    quantum: u32,
) -> Result<DataMachineRunV1, String> {
    context(program, input, fuel)?;
    advance(
        DataMachineRunV1 {
            schema: DATA_MACHINE_RUN_V1.into(),
            profile: data_machine_profile_v1(),
            program: program.clone(),
            input: input.clone(),
            fuel,
            state: initial(program),
            trace: vec![],
            status: DataMachineStatusV1::Suspended,
            segments: vec![],
        },
        quantum,
        0,
    )
}

pub fn verify_data_machine_run_v1(
    program: &DataMachineProgramV1,
    input: &MachineDataV1,
    fuel: u32,
    run: &DataMachineRunV1,
) -> Result<DataMachineReceptionV1, String> {
    context(program, input, fuel)?;
    if run.schema != DATA_MACHINE_RUN_V1
        || run.profile != data_machine_profile_v1()
        || run.program != *program
        || run.input != *input
        || run.fuel != fuel
        || run.trace.len() > fuel as usize
        || run.segments.is_empty()
        || run.segments.len() > MAX_SEGMENTS
    {
        return Err("checkpoint context mismatch".into());
    }
    let mut state = initial(program);
    for event in &run.trace {
        if *event != step(program, input, &mut state)? {
            return Err("checkpoint trace mismatch".into());
        }
    }
    if state != run.state || run.status != status(&state, fuel) {
        return Err("checkpoint state/status mismatch".into());
    }
    let mut end = 0;
    for (index, segment) in run.segments.iter().enumerate() {
        if segment.start != end
            || segment.end < end
            || segment.end > state.spent
            || segment.replayed != if index == 0 { 0 } else { end }
        {
            return Err("checkpoint segment accounting mismatch".into());
        }
        end = segment.end;
    }
    if end != state.spent {
        return Err("checkpoint segment coverage mismatch".into());
    }
    Ok(DataMachineReceptionV1 {
        profile: run.profile.clone(),
        verified_steps: state.spent,
        state,
    })
}

pub fn resume_data_machine_v1(
    program: &DataMachineProgramV1,
    input: &MachineDataV1,
    fuel: u32,
    run: &DataMachineRunV1,
    quantum: u32,
) -> Result<DataMachineRunV1, String> {
    let checked = verify_data_machine_run_v1(program, input, fuel, run)?;
    if checked.state.phase != MachinePhaseV1::Running {
        return Err("terminal execution cannot continue".into());
    }
    let mut resumed = run.clone();
    resumed.state = checked.state;
    advance(resumed, quantum, checked.verified_steps)
}
