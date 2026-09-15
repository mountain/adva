//! A separately versioned, bounded research language for programs over data.
//! No PSC0 terms, identities, operations or certificate meanings are changed.
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

pub const DATA_MACHINE_PROGRAM_V0: &str = "adva.data-machine.program.research.v0";
pub const DATA_MACHINE_RUN_V0: &str = "adva.data-machine.run.research.v0";
pub const DATA_MACHINE_MAX_FUEL_V0: u32 = 2048;
pub const DATA_MACHINE_MAX_BYTES_V0: usize = 32768;
pub const DATA_MACHINE_MAX_REPORT_V0: usize = 2 * 1024 * 1024;
const MAX_STATE_NODES: usize = 8192;
const MAX_SEGMENTS: usize = 16;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachineDataV0 {
    Integer { value: i64 },
    Node { tag: u8, fields: Vec<MachineDataV0> },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MachineTypeV0 {
    Integer,
    Boolean,
    Data,
    Stack,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachineValueV0 {
    Integer { value: i64 },
    Boolean { value: bool },
    Data { value: MachineDataV0 },
    Stack { items: Vec<MachineDataV0> },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MachineRegisterV0 {
    pub name: String,
    pub kind: MachineTypeV0,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachineInstructionV0 {
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
pub struct DataMachineProgramV0 {
    pub schema: String,
    pub name: String,
    pub registers: Vec<MachineRegisterV0>,
    pub code: Vec<MachineInstructionV0>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MachinePhaseV0 {
    Running,
    Returned { value: MachineDataV0 },
    Rejected { reason: String },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DataMachineStateV0 {
    pub pc: usize,
    pub registers: Vec<Option<MachineValueV0>>,
    pub spent: u32,
    pub phase: MachinePhaseV0,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MachineEventV0 {
    pub pc: usize,
    pub next_pc: usize,
    pub state_digest: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum DataMachineStatusV0 {
    Returned,
    Rejected,
    Suspended,
    FuelExhausted,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MachineSegmentV0 {
    pub start: u32,
    pub end: u32,
    pub replayed: u32,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DataMachineRunV0 {
    pub schema: String,
    pub profile: String,
    pub program: DataMachineProgramV0,
    pub input: MachineDataV0,
    pub fuel: u32,
    pub state: DataMachineStateV0,
    pub trace: Vec<MachineEventV0>,
    pub status: DataMachineStatusV0,
    pub segments: Vec<MachineSegmentV0>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct DataMachineReceptionV0 {
    pub profile: String,
    pub verified_steps: u32,
    pub state: DataMachineStateV0,
}

pub fn data_machine_profile_v0() -> String {
    let mut h = blake3::Hasher::new();
    h.update(b"adva.data-machine.transition.v0\0");
    h.update(include_bytes!("data_machine.rs"));
    h.update(include_bytes!("../../../Cargo.lock"));
    h.finalize().to_hex().to_string()
}

fn data_size(value: &MachineDataV0) -> Result<usize, String> {
    let mut pending = vec![(value, 1)];
    let mut count = 0;
    while let Some((node, depth)) = pending.pop() {
        count += 1;
        if count > 127 || depth > 12 {
            return Err("data capacity exceeded".into());
        }
        if let MachineDataV0::Node { fields, .. } = node {
            if fields.len() > 8 {
                return Err("node arity exceeds 8".into());
            }
            pending.extend(fields.iter().map(|child| (child, depth + 1)));
        }
    }
    Ok(count)
}

fn check_state(state: &DataMachineStateV0) -> Result<(), String> {
    let mut nodes = 0;
    for value in state.registers.iter().flatten() {
        nodes += match value {
            MachineValueV0::Data { value } => data_size(value)?,
            MachineValueV0::Stack { items } => {
                if items.len() > 256 {
                    return Err("stack capacity exceeded".into());
                }
                items
                    .iter()
                    .try_fold(0, |n, d| Ok::<_, String>(n + data_size(d)?))?
            }
            _ => 1,
        };
    }
    if let MachinePhaseV0::Returned { value } = &state.phase {
        nodes += data_size(value)?;
    }
    if nodes > MAX_STATE_NODES {
        return Err("state capacity exceeded".into());
    }
    Ok(())
}

pub fn validate_data_machine_program_v0(program: &DataMachineProgramV0) -> Result<(), String> {
    use MachineInstructionV0 as I;
    use MachineTypeV0 as T;
    if program.schema != DATA_MACHINE_PROGRAM_V0
        || program.name.is_empty()
        || program.name.len() > 64
        || program.registers.is_empty()
        || program.registers.len() > 16
        || program.code.is_empty()
        || program.code.len() > 128
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
                if *arity > 8 || index >= arity {
                    return Err("invalid field shape".into());
                }
            }
            I::Node { fields, dst, .. } => {
                reg(*dst, T::Data)?;
                if fields.len() > 8 {
                    return Err("node arity exceeds 8".into());
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
        > DATA_MACHINE_MAX_BYTES_V0
    {
        return Err("program exceeds byte limit".into());
    }
    Ok(())
}

fn initial(program: &DataMachineProgramV0) -> DataMachineStateV0 {
    DataMachineStateV0 {
        pc: 0,
        registers: vec![None; program.registers.len()],
        spent: 0,
        phase: MachinePhaseV0::Running,
    }
}

impl DataMachineStateV0 {
    fn value(&self, index: usize) -> Result<&MachineValueV0, String> {
        self.registers
            .get(index)
            .and_then(Option::as_ref)
            .ok_or_else(|| "uninitialized register".into())
    }
    fn data(&self, index: usize) -> Result<&MachineDataV0, String> {
        match self.value(index)? {
            MachineValueV0::Data { value } => Ok(value),
            _ => Err("expected data register".into()),
        }
    }
    fn integer(&self, index: usize) -> Result<i64, String> {
        match self.value(index)? {
            MachineValueV0::Integer { value } => Ok(*value),
            _ => Err("expected integer register".into()),
        }
    }
    fn stack(&self, index: usize) -> Result<&Vec<MachineDataV0>, String> {
        match self.value(index)? {
            MachineValueV0::Stack { items } => Ok(items),
            _ => Err("expected stack register".into()),
        }
    }
    fn set(&mut self, index: usize, value: MachineValueV0) {
        self.registers[index] = Some(value);
    }
}

fn apply(
    instruction: &MachineInstructionV0,
    input: &MachineDataV0,
    s: &mut DataMachineStateV0,
) -> Result<(), String> {
    use MachineInstructionV0 as I;
    use MachineValueV0 as V;
    s.pc += 1;
    match instruction {
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
            if items.len() >= 256 {
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
                MachineDataV0::Integer { .. } => -1,
                MachineDataV0::Node { tag, .. } => i64::from(*tag),
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
                MachineDataV0::Node { fields, .. } if fields.len() == *arity => {
                    fields[*index].clone()
                }
                _ => return Err("data shape mismatch".into()),
            };
            s.set(*dst, V::Data { value });
        }
        I::AsInteger { src, dst } => {
            let MachineDataV0::Integer { value } = s.data(*src)? else {
                return Err("expected integer data".into());
            };
            s.set(*dst, V::Integer { value: *value });
        }
        I::BoxInteger { src, dst } => s.set(
            *dst,
            V::Data {
                value: MachineDataV0::Integer {
                    value: s.integer(*src)?,
                },
            },
        ),
        I::Node { tag, fields, dst } => {
            let fields = fields
                .iter()
                .map(|r| s.data(*r).cloned())
                .collect::<Result<Vec<_>, _>>()?;
            let value = MachineDataV0::Node { tag: *tag, fields };
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
            s.phase = MachinePhaseV0::Returned {
                value: s.data(*src)?.clone(),
            }
        }
        I::Reject { reason } => return Err(reason.clone()),
    }
    check_state(s)
}

fn step(
    program: &DataMachineProgramV0,
    input: &MachineDataV0,
    state: &mut DataMachineStateV0,
) -> Result<MachineEventV0, String> {
    if state.phase != MachinePhaseV0::Running {
        return Err("step after terminal state".into());
    }
    let pc = state.pc;
    let instruction = program.code.get(pc).ok_or("program counter outside code")?;
    let mut next = state.clone();
    if let Err(reason) = apply(instruction, input, &mut next) {
        next = state.clone(); // Failed instructions have no partial data writes.
        next.phase = MachinePhaseV0::Rejected { reason };
    }
    next.spent += 1;
    let state_digest = blake3::hash(&serde_json::to_vec(&next).map_err(|e| e.to_string())?)
        .to_hex()
        .to_string();
    let event = MachineEventV0 {
        pc,
        next_pc: next.pc,
        state_digest,
    };
    *state = next;
    Ok(event)
}

fn status(state: &DataMachineStateV0, fuel: u32) -> DataMachineStatusV0 {
    match state.phase {
        MachinePhaseV0::Returned { .. } => DataMachineStatusV0::Returned,
        MachinePhaseV0::Rejected { .. } => DataMachineStatusV0::Rejected,
        MachinePhaseV0::Running if state.spent == fuel => DataMachineStatusV0::FuelExhausted,
        MachinePhaseV0::Running => DataMachineStatusV0::Suspended,
    }
}

fn context(program: &DataMachineProgramV0, input: &MachineDataV0, fuel: u32) -> Result<(), String> {
    validate_data_machine_program_v0(program)?;
    data_size(input)?;
    if fuel > DATA_MACHINE_MAX_FUEL_V0 {
        return Err("fuel exceeds profile".into());
    }
    Ok(())
}

fn advance(
    mut run: DataMachineRunV0,
    quantum: u32,
    replayed: u32,
) -> Result<DataMachineRunV0, String> {
    if quantum > DATA_MACHINE_MAX_FUEL_V0 || run.segments.len() >= MAX_SEGMENTS {
        return Err("quantum or continuation count exceeds profile".into());
    }
    let start = run.state.spent;
    for _ in 0..quantum {
        if run.state.spent == run.fuel || run.state.phase != MachinePhaseV0::Running {
            break;
        }
        run.trace
            .push(step(&run.program, &run.input, &mut run.state)?);
    }
    run.status = status(&run.state, run.fuel);
    run.segments.push(MachineSegmentV0 {
        start,
        end: run.state.spent,
        replayed,
    });
    if serde_json::to_vec(&run).map_err(|e| e.to_string())?.len() > DATA_MACHINE_MAX_REPORT_V0 {
        return Err("run exceeds report capacity".into());
    }
    Ok(run)
}

pub fn run_data_machine_v0(
    program: &DataMachineProgramV0,
    input: &MachineDataV0,
    fuel: u32,
    quantum: u32,
) -> Result<DataMachineRunV0, String> {
    context(program, input, fuel)?;
    advance(
        DataMachineRunV0 {
            schema: DATA_MACHINE_RUN_V0.into(),
            profile: data_machine_profile_v0(),
            program: program.clone(),
            input: input.clone(),
            fuel,
            state: initial(program),
            trace: vec![],
            status: DataMachineStatusV0::Suspended,
            segments: vec![],
        },
        quantum,
        0,
    )
}

pub fn verify_data_machine_run_v0(
    program: &DataMachineProgramV0,
    input: &MachineDataV0,
    fuel: u32,
    run: &DataMachineRunV0,
) -> Result<DataMachineReceptionV0, String> {
    context(program, input, fuel)?;
    if run.schema != DATA_MACHINE_RUN_V0
        || run.profile != data_machine_profile_v0()
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
    Ok(DataMachineReceptionV0 {
        profile: run.profile.clone(),
        verified_steps: state.spent,
        state,
    })
}

pub fn resume_data_machine_v0(
    program: &DataMachineProgramV0,
    input: &MachineDataV0,
    fuel: u32,
    run: &DataMachineRunV0,
    quantum: u32,
) -> Result<DataMachineRunV0, String> {
    let checked = verify_data_machine_run_v0(program, input, fuel, run)?;
    if checked.state.phase != MachinePhaseV0::Running {
        return Err("terminal execution cannot continue".into());
    }
    let mut resumed = run.clone();
    resumed.state = checked.state;
    advance(resumed, quantum, checked.verified_steps)
}
