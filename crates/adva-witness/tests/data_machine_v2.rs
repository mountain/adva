use adva_witness::*;

fn program(code: Vec<MachineInstructionV2>) -> DataMachineProgramV2 {
    DataMachineProgramV2 {
        schema: DATA_MACHINE_PROGRAM_V2.into(),
        name: "generic-v2-boundaries".into(),
        registers: vec![
            MachineRegisterV2 {
                name: "data".into(),
                kind: MachineTypeV2::Data,
            },
            MachineRegisterV2 {
                name: "index".into(),
                kind: MachineTypeV2::Integer,
            },
            MachineRegisterV2 {
                name: "stack".into(),
                kind: MachineTypeV2::Stack,
            },
            MachineRegisterV2 {
                name: "result".into(),
                kind: MachineTypeV2::Data,
            },
        ],
        code,
    }
}
fn integer(value: i64) -> MachineDataV2 {
    MachineDataV2::Integer { value }
}
fn input() -> MachineDataV2 {
    MachineDataV2::Node {
        tag: 7,
        fields: vec![integer(3), integer(9)],
    }
}

#[test]
fn generic_dynamic_fields_pack_and_lengths_preserve_order_without_consumption() {
    use MachineInstructionV2 as I;
    let p = program(vec![
        I::Input { dst: 0 },
        I::Length { src: 0, dst: 1 },
        I::BoxInteger { src: 1, dst: 3 },
        I::Clear { stack: 2 },
        I::Push { stack: 2, src: 3 },
        I::Constant { dst: 1, value: 1 },
        I::FieldDynamic {
            src: 0,
            index: 1,
            dst: 3,
        },
        I::Push { stack: 2, src: 3 },
        I::Pack {
            stack: 2,
            tag: 77,
            dst: 3,
        },
        I::StackLength { stack: 2, dst: 1 },
        I::Return { src: 3 },
    ]);
    let r = run_data_machine_v2(&p, &input(), 20, 20).unwrap();
    assert_eq!(
        r.state.phase,
        MachinePhaseV2::Returned {
            value: MachineDataV2::Node {
                tag: 77,
                fields: vec![integer(2), integer(9)]
            }
        }
    );
    assert_eq!(
        r.state.registers[1],
        Some(MachineValueV2::Integer { value: 2 })
    );
    assert_eq!(
        r.state.registers[2],
        Some(MachineValueV2::Stack {
            items: vec![integer(2), integer(9)]
        })
    );
    verify_data_machine_run_v2(&p, &input(), 20, &r).unwrap();
}

#[test]
fn invalid_dynamic_access_rolls_back_and_charges_the_failing_instruction() {
    use MachineInstructionV2 as I;
    for (index, data, reason) in [
        (-1, input(), "negative field index"),
        (2, input(), "field index outside node"),
        (0, integer(7), "expected node data"),
    ] {
        let p = program(vec![
            I::Input { dst: 0 },
            I::Constant {
                dst: 1,
                value: index,
            },
            I::FieldDynamic {
                src: 0,
                index: 1,
                dst: 0,
            },
            I::Return { src: 0 },
        ]);
        let prefix = run_data_machine_v2(&p, &data, 20, 2).unwrap();
        let r = resume_data_machine_v2(&p, &data, 20, &prefix, 20).unwrap();
        assert_eq!(r.state.registers, prefix.state.registers);
        assert_eq!(r.state.spent, 3);
        assert_eq!(r.state.pc, 2);
        assert_eq!(
            r.state.phase,
            MachinePhaseV2::Rejected {
                reason: reason.into()
            }
        );
    }
}

#[test]
fn new_operations_validate_all_register_types_before_zero_fuel_execution() {
    use MachineInstructionV2 as I;
    for bad in [
        I::Length { src: 1, dst: 1 },
        I::FieldDynamic {
            src: 0,
            index: 0,
            dst: 0,
        },
        I::Pack {
            stack: 0,
            tag: 0,
            dst: 3,
        },
        I::StackLength { stack: 2, dst: 0 },
    ] {
        let p = program(vec![bad, I::Return { src: 0 }]);
        assert!(run_data_machine_v2(&p, &input(), 0, 0).is_err());
    }
}

#[test]
fn expanded_profile_remains_finite_and_distinct_from_v0() {
    use MachineInstructionV2 as I;
    let p = program(vec![I::Input { dst: 0 }, I::Return { src: 0 }]);
    assert_ne!(data_machine_profile_v0(), data_machine_profile_v2());
    assert!(run_data_machine_v2(&p, &input(), 200001, 0).is_err());
    let wide = MachineDataV2::Node {
        tag: 0,
        fields: vec![integer(0); 4097],
    };
    assert!(run_data_machine_v2(&p, &wide, 0, 0).is_err());
    let mut deep = integer(0);
    for _ in 0..48 {
        deep = MachineDataV2::Node {
            tag: 0,
            fields: vec![deep],
        };
    }
    assert!(run_data_machine_v2(&p, &deep, 0, 0).is_err());
    let prefix = run_data_machine_v2(&p, &input(), 1, 1).unwrap();
    let still = resume_data_machine_v2(&p, &input(), 1, &prefix, 10).unwrap();
    assert_eq!(still.status, DataMachineStatusV2::FuelExhausted);
    assert_eq!(still.trace, prefix.trace);
    assert!(resume_data_machine_v2(&p, &input(), 2, &prefix, 10).is_err());
}

#[test]
fn code_and_data_arity_fit_4096_but_not_4097_and_v1_stays_frozen() {
    use MachineInstructionV2 as I;
    let mut code = vec![I::Copy { src: 0, dst: 0 }; 4096];
    code[0] = I::Input { dst: 0 };
    code[4095] = I::Return { src: 0 };
    let p = program(code);
    let wide = MachineDataV2::Node {
        tag: 0,
        fields: vec![integer(0); 4096],
    };
    assert!(run_data_machine_v2(&p, &wide, 0, 0).is_ok());
    let mut old_json = serde_json::to_value(&p).unwrap();
    old_json["schema"] = DATA_MACHINE_PROGRAM_V1.into();
    let old: DataMachineProgramV1 = serde_json::from_value(old_json).unwrap();
    assert!(run_data_machine_v1(&old, &MachineDataV1::Integer { value: 0 }, 0, 0).is_err());
    let mut oversized = p.clone();
    oversized.code.push(I::Return { src: 0 });
    assert!(run_data_machine_v2(&oversized, &integer(0), 0, 0).is_err());
    let too_many_nodes = MachineDataV2::Node {
        tag: 0,
        fields: vec![wide; 4],
    };
    assert!(run_data_machine_v2(&p, &too_many_nodes, 0, 0).is_err());
}

#[test]
fn common_domain_states_and_traces_match_but_profiles_do_not() {
    use MachineInstructionV2 as I;
    let p = program(vec![
        I::Input { dst: 0 },
        I::Constant { dst: 1, value: -1 },
        I::FieldDynamic {
            src: 0,
            index: 1,
            dst: 0,
        },
        I::Return { src: 0 },
    ]);
    let mut old_json = serde_json::to_value(&p).unwrap();
    old_json["schema"] = DATA_MACHINE_PROGRAM_V1.into();
    let old: DataMachineProgramV1 = serde_json::from_value(old_json).unwrap();
    let old_input: MachineDataV1 =
        serde_json::from_value(serde_json::to_value(input()).unwrap()).unwrap();
    let before = run_data_machine_v1(&old, &old_input, 20, 20).unwrap();
    let after = run_data_machine_v2(&p, &input(), 20, 20).unwrap();
    assert_eq!(
        serde_json::to_value(&before.state).unwrap(),
        serde_json::to_value(&after.state).unwrap()
    );
    assert_eq!(
        serde_json::to_value(&before.trace).unwrap(),
        serde_json::to_value(&after.trace).unwrap()
    );
    assert_ne!(before.profile, after.profile);
    let foreign: DataMachineRunV2 =
        serde_json::from_value(serde_json::to_value(before).unwrap()).unwrap();
    assert!(verify_data_machine_run_v2(&p, &input(), 20, &foreign).is_err());
    let mut changed = after.clone();
    changed.profile = data_machine_profile_v1();
    assert!(resume_data_machine_v2(&p, &input(), 20, &changed, 20).is_err());
}
