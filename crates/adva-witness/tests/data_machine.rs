use adva_witness::*;

fn program() -> DataMachineProgramV0 {
    serde_json::from_str(include_str!(
        "../../../programs/bounded-interpreter/interpreter.adva"
    ))
    .unwrap()
}
fn integer(value: i64) -> MachineDataV0 {
    MachineDataV0::Integer { value }
}
fn node(tag: u8, fields: Vec<MachineDataV0>) -> MachineDataV0 {
    MachineDataV0::Node { tag, fields }
}
fn literal(value: i64) -> MachineDataV0 {
    node(0, vec![integer(value)])
}
fn sample() -> MachineDataV0 {
    node(1, vec![literal(2), node(2, vec![literal(3), literal(4)])])
}
fn returned(run: &DataMachineRunV0, expected: i64) {
    assert_eq!(run.status, DataMachineStatusV0::Returned);
    assert_eq!(
        run.state.phase,
        MachinePhaseV0::Returned {
            value: integer(expected)
        }
    );
}

#[test]
fn one_program_interprets_distinct_trees_and_exact_large_integers() {
    let p = program();
    for (input, expected) in [
        (literal(-7), -7),
        (sample(), 14),
        (
            node(1, vec![literal(9_007_199_254_740_993), literal(2)]),
            9_007_199_254_740_995,
        ),
    ] {
        let run = run_data_machine_v0(&p, &input, 2048, 2048).unwrap();
        returned(&run, expected);
        let receipt = verify_data_machine_run_v0(&p, &input, 2048, &run).unwrap();
        assert_eq!(receipt.verified_steps as usize, run.trace.len());
    }
}

#[test]
fn changing_adva_arithmetic_changes_execution() {
    let mut p = program();
    let input = node(1, vec![literal(2), literal(3)]);
    returned(&run_data_machine_v0(&p, &input, 2048, 2048).unwrap(), 5);
    for instruction in &mut p.code {
        if let MachineInstructionV0::Add { left, right, dst } = *instruction {
            *instruction = MachineInstructionV0::Multiply { left, right, dst };
        }
    }
    returned(&run_data_machine_v0(&p, &input, 2048, 2048).unwrap(), 6);
}

#[test]
fn suspension_replays_and_preserves_full_trace_and_lifetime_fuel() {
    let (p, input) = (program(), sample());
    let whole = run_data_machine_v0(&p, &input, 2048, 2048).unwrap();
    let prefix = run_data_machine_v0(&p, &input, 2048, 17).unwrap();
    assert_eq!(prefix.status, DataMachineStatusV0::Suspended);
    let resumed = resume_data_machine_v0(&p, &input, 2048, &prefix, 2048).unwrap();
    assert_eq!(whole.trace, resumed.trace);
    assert_eq!(whole.state, resumed.state);
    assert_eq!(resumed.segments[1].replayed, 17);
    assert!(resume_data_machine_v0(&p, &input, 2048, &resumed, 1).is_err());
    let exhausted = run_data_machine_v0(&p, &input, 17, 2048).unwrap();
    let still = resume_data_machine_v0(&p, &input, 17, &exhausted, 2048).unwrap();
    assert_eq!(still.status, DataMachineStatusV0::FuelExhausted);
    assert_eq!(still.trace, exhausted.trace);
    assert_eq!(still.state.spent, 17);
    assert!(resume_data_machine_v0(&p, &input, 18, &exhausted, 1).is_err());
}

#[test]
fn checkpoints_require_independent_context_and_every_original_edge() {
    let (p, input) = (program(), sample());
    let run = run_data_machine_v0(&p, &input, 2048, 17).unwrap();
    assert!(verify_data_machine_run_v0(&p, &literal(0), 2048, &run).is_err());
    let mut changed = p.clone();
    changed.name.push('x');
    assert!(verify_data_machine_run_v0(&changed, &input, 2048, &run).is_err());
    let mut mutations = vec![run.clone(); 8];
    mutations[0].state.pc += 1;
    mutations[1].state.spent = 0;
    mutations[2].trace[2].state_digest = "00".into();
    mutations[3].trace[2].pc += 1;
    mutations[4].trace.remove(2);
    mutations[5].profile = "old-profile".into();
    mutations[6].segments[0].end = 1;
    mutations[7].status = DataMachineStatusV0::Returned;
    for mutation in mutations {
        assert!(resume_data_machine_v0(&p, &input, 2048, &mutation, 1).is_err());
    }
}

#[test]
fn malformed_object_inputs_and_overflow_reject_with_checked_traces() {
    let p = program();
    for input in [
        node(99, vec![]),
        node(0, vec![]),
        node(0, vec![node(0, vec![])]),
        node(1, vec![literal(1), literal(2), literal(3)]),
        integer(1),
        node(1, vec![literal(i64::MAX), literal(1)]),
        node(2, vec![literal(i64::MIN), literal(-1)]),
        node(1, vec![literal(i64::MIN), literal(-1)]),
    ] {
        let run = run_data_machine_v0(&p, &input, 2048, 2048).unwrap();
        assert_eq!(run.status, DataMachineStatusV0::Rejected);
        assert_eq!(run.state.spent as usize, run.trace.len());
        verify_data_machine_run_v0(&p, &input, 2048, &run).unwrap();
    }
}

#[test]
fn generic_construction_and_copy_do_not_call_the_arithmetic_interpreter() {
    let mut p = program();
    p.code = vec![
        MachineInstructionV0::Input { dst: 2 },
        MachineInstructionV0::Copy { src: 2, dst: 3 },
        MachineInstructionV0::Node {
            tag: 77,
            fields: vec![2, 3],
            dst: 4,
        },
        MachineInstructionV0::Return { src: 4 },
    ];
    let run = run_data_machine_v0(&p, &integer(5), 10, 10).unwrap();
    assert_eq!(
        run.state.phase,
        MachinePhaseV0::Returned {
            value: node(77, vec![integer(5), integer(5)])
        }
    );
}

#[test]
fn bounded_loop_and_zero_fuel_remain_unknown_not_nonhalting_proofs() {
    let mut p = program();
    p.code = vec![MachineInstructionV0::Jump { target: 0 }];
    let run = run_data_machine_v0(&p, &integer(0), 23, 2048).unwrap();
    assert_eq!(run.status, DataMachineStatusV0::FuelExhausted);
    assert_eq!(run.trace.len(), 23);
    let zero = run_data_machine_v0(&p, &integer(0), 0, 2048).unwrap();
    assert_eq!(zero.status, DataMachineStatusV0::FuelExhausted);
    assert!(zero.trace.is_empty());
    assert_eq!(zero.state.phase, MachinePhaseV0::Running);
}

#[test]
fn static_types_targets_and_all_bytecode_branches_are_validated_before_running() {
    let p = program();
    let mut bad = p.clone();
    bad.code[0] = MachineInstructionV0::Clear { stack: 2 };
    assert!(run_data_machine_v0(&bad, &sample(), 0, 0).is_err());
    bad = p.clone();
    bad.code[0] = MachineInstructionV0::Jump {
        target: p.code.len(),
    };
    assert!(validate_data_machine_program_v0(&bad).is_err());
    bad = p.clone();
    bad.code.push(MachineInstructionV0::Input { dst: 2 });
    assert!(validate_data_machine_program_v0(&bad).is_err());
    bad = p.clone();
    bad.registers[1].name = bad.registers[0].name.clone();
    assert!(validate_data_machine_program_v0(&bad).is_err());
    bad = p;
    bad.code[0] = MachineInstructionV0::Field {
        src: 2,
        arity: 1,
        index: 1,
        dst: 3,
    };
    assert!(validate_data_machine_program_v0(&bad).is_err());
}

#[test]
fn invalid_shapes_cannot_cross_the_serde_integer_boundary() {
    for source in [
        r#"{"kind":"integer","value":true}"#,
        r#"{"kind":"integer","value":1.0}"#,
        r#"{"kind":"integer","value":1,"extra":0}"#,
        r#"{"kind":"integer","value":1,"value":2}"#,
    ] {
        assert!(serde_json::from_str::<MachineDataV0>(source).is_err());
    }
    let mut data = integer(0);
    for _ in 0..12 {
        data = node(0, vec![data]);
    }
    assert!(run_data_machine_v0(&program(), &data, 0, 0).is_err());
    assert!(run_data_machine_v0(&program(), &sample(), 2049, 1).is_err());
}

#[test]
fn failed_instruction_is_charged_and_has_no_partial_data_writes() {
    let mut p = program();
    p.code = vec![
        MachineInstructionV0::Clear { stack: 0 },
        MachineInstructionV0::Pop { stack: 0, dst: 2 },
        MachineInstructionV0::Return { src: 2 },
    ];
    let prefix = run_data_machine_v0(&p, &integer(0), 10, 1).unwrap();
    let run = resume_data_machine_v0(&p, &integer(0), 10, &prefix, 1).unwrap();
    assert_eq!(run.state.registers, prefix.state.registers);
    assert_eq!(run.state.pc, 1);
    assert_eq!(run.state.spent, 2);
    assert_eq!(run.status, DataMachineStatusV0::Rejected);
}

#[test]
fn stack_capacity_rejects_and_continuation_count_is_finite() {
    let mut p = program();
    p.code = vec![
        MachineInstructionV0::Clear { stack: 0 },
        MachineInstructionV0::Input { dst: 2 },
        MachineInstructionV0::Push { stack: 0, src: 2 },
        MachineInstructionV0::Jump { target: 2 },
    ];
    let run = run_data_machine_v0(&p, &integer(0), 2048, 2048).unwrap();
    assert_eq!(
        run.state.phase,
        MachinePhaseV0::Rejected {
            reason: "stack capacity exceeded".into()
        }
    );
    p.code = vec![MachineInstructionV0::Jump { target: 0 }];
    let mut run = run_data_machine_v0(&p, &integer(0), 2048, 0).unwrap();
    for _ in 1..16 {
        run = resume_data_machine_v0(&p, &integer(0), 2048, &run, 0).unwrap();
    }
    assert!(resume_data_machine_v0(&p, &integer(0), 2048, &run, 0).is_err());
}

#[test]
fn return_on_last_unit_of_fuel_is_success() {
    let mut p = program();
    p.code = vec![
        MachineInstructionV0::Input { dst: 2 },
        MachineInstructionV0::Return { src: 2 },
    ];
    returned(&run_data_machine_v0(&p, &integer(7), 2, 2).unwrap(), 7);
}
