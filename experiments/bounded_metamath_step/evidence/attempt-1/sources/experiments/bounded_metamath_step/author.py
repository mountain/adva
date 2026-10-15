"""Author the ordinary Adva instruction list; this is not a runtime oracle.

The emitted program owns every proof-stack change, substitution-token copy,
type/scope judgment and final comparison. Native execution never imports this
file. The tiny database and labels are deliberately fixed in the instruction
list; there is no host-provided assertion callback or .mm parser.

Project-original contribution under Unknown v0.3. Authored by ChatGPT (OpenAI),
submitted through Mingli Yuan's authorized account proxy; account use is not
his authorship, review or correctness guarantee.
"""

import json
from pathlib import Path

REGISTERS = [
    ("proof_stack", "stack"),
    ("token_build", "stack"),
    ("input", "data"),
    ("proof", "data"),
    ("expected", "data"),
    ("expected_type_data", "data"),
    ("expected_tokens", "data"),
    ("item", "data"),
    ("expression", "data"),
    ("expression_type_data", "data"),
    ("expression_tokens", "data"),
    ("token_data", "data"),
    ("new_tokens", "data"),
    ("new_type_data", "data"),
    ("result", "data"),
    ("proof_length", "integer"),
    ("proof_index", "integer"),
    ("expected_type", "integer"),
    ("expected_length", "integer"),
    ("index", "integer"),
    ("token", "integer"),
    ("depth", "integer"),
    ("expression_type", "integer"),
    ("expression_length", "integer"),
    ("label", "integer"),
    ("actual_token", "integer"),
    ("expected_token", "integer"),
    ("scratch", "integer"),
    ("constant", "integer"),
    ("one", "integer"),
    ("mode", "integer"),
    ("test", "boolean"),
]
R = {name: index for index, (name, _) in enumerate(REGISTERS)}


class Author:
    def __init__(self):
        self.code = []
        self.labels = {}
        self.serial = 0
        self.rejections = set()

    def fresh(self, stem):
        self.serial += 1
        return f"{stem}_{self.serial}"

    def mark(self, name):
        if name in self.labels:
            raise ValueError(f"duplicate label: {name}")
        self.labels[name] = len(self.code)

    def emit(self, opcode, **args):
        registers = {"dst", "src", "left", "right", "stack", "condition", "index"}
        out = {"op": opcode}
        for key, value in args.items():
            if key in registers and isinstance(value, str):
                value = R[value]
            elif key == "fields":
                value = [R[name] for name in value]
            out[key] = value
        self.code.append(out)

    def const(self, dst, value):
        self.emit("constant", dst=dst, value=value)

    def jump(self, target):
        self.emit("jump", target=target)

    def branch(self, yes, no):
        self.emit("branch", condition="test", yes=yes, no=no)

    def reject_label(self, reason):
        self.rejections.add(reason)
        return "reject_" + reason.replace(" ", "_")

    def compare_constant(self, src, value):
        self.const("constant", value)
        self.emit("equal", left=src, right="constant", dst="test")

    def require_value(self, src, value, reason):
        good = self.fresh("checked")
        self.compare_constant(src, value)
        self.branch(good, self.reject_label(reason))
        self.mark(good)

    def require_member(self, src, values, reason):
        good = self.fresh("member")
        for value in values:
            again = self.fresh("next_member")
            self.compare_constant(src, value)
            self.branch(good, again)
            self.mark(again)
        self.jump(self.reject_label(reason))
        self.mark(good)

    def node(self, src, tag, reason, arity=None):
        self.emit("tag", src=src, dst="scratch")
        self.require_value("scratch", tag, reason)
        if arity is not None:
            self.emit("length", src=src, dst="scratch")
            self.require_value("scratch", arity, reason)

    def integer(self, src, dst, reason):
        self.emit("tag", src=src, dst="scratch")
        self.require_value("scratch", -1, reason)
        self.emit("as_integer", src=src, dst=dst)

    def field(self, src, index, dst, arity):
        self.emit("field", src=src, arity=arity, index=index, dst=dst)

    def increment(self, register):
        self.emit("add", left=register, right="one", dst=register)

    def loop(self, start, done, index, length):
        self.mark(start)
        self.emit("equal", left=index, right=length, dst="test")
        body = self.fresh("loop_body")
        self.branch(done, body)
        self.mark(body)

    def author(self):
        self.const("one", 1)
        self.emit("clear", stack="proof_stack")
        self.emit("clear", stack="token_build")
        self.emit("input", dst="input")
        self.node("input", 10, "unsupported proof", 2)
        self.field("input", 0, "proof", 2)
        self.field("input", 1, "expected", 2)
        self.node("proof", 11, "unsupported proof")
        self.emit("length", src="proof", dst="proof_length")
        self.require_member("proof_length", range(9), "proof bound")

        # Check the entire expected expression before interpreting proof labels.
        self.node("expected", 1, "unsupported expression", 2)
        self.field("expected", 0, "expected_type_data", 2)
        self.field("expected", 1, "expected_tokens", 2)
        self.integer("expected_type_data", "expected_type", "unsupported expression")
        self.require_member("expected_type", [1, 2, 3], "unsupported expression")
        self.node("expected_tokens", 2, "unsupported expression")
        self.emit("length", src="expected_tokens", dst="expected_length")
        self.require_member("expected_length", range(1, 5), "token bound")
        self.const("index", 0)
        self.loop("validate_tokens", "validate_labels_start", "index", "expected_length")
        self.emit("field_dynamic", src="expected_tokens", index="index", dst="token_data")
        self.integer("token_data", "token", "unsupported token")
        self.require_member("token", [4, 5, 10, 11], "unsupported token")
        self.increment("index")
        self.jump("validate_tokens")

        self.mark("validate_labels_start")
        self.const("proof_index", 0)
        self.loop("validate_labels", "execute_start", "proof_index", "proof_length")
        self.emit("field_dynamic", src="proof", index="proof_index", dst="item")
        self.integer("item", "label", "unsupported proof")
        self.increment("proof_index")
        self.jump("validate_labels")

        self.mark("execute_start")
        self.const("proof_index", 0)
        self.loop("proof_loop", "finish", "proof_index", "proof_length")
        self.emit("field_dynamic", src="proof", index="proof_index", dst="item")
        self.emit("as_integer", src="item", dst="label")
        for value, destination in [
            (100, "floating_q"),
            (101, "constant_term_a"),
            (102, self.reject_label("inactive label")),
            (200, "assertion"),
            (201, "assertion"),
            (202, "assertion"),
        ]:
            more = self.fresh("dispatch")
            self.compare_constant("label", value)
            self.branch(destination, more)
            self.mark(more)
        self.jump(self.reject_label("unknown label"))

        # These are the only two push rules. Label 101 is the constant axiom
        # $a term a $., avoiding a second active $f for the variable q.
        self.mark("floating_q")
        self.const("expression_type", 1)
        self.const("token", 11)
        self.jump("push_singleton")
        self.mark("constant_term_a")
        self.const("expression_type", 3)
        self.const("token", 5)
        self.mark("push_singleton")
        self.emit("box_integer", src="token", dst="token_data")
        self.emit("node", tag=2, fields=["token_data"], dst="new_tokens")
        self.emit("box_integer", src="expression_type", dst="new_type_data")
        self.emit("node", tag=1, fields=["new_type_data", "new_tokens"], dst="result")
        self.jump("push_result")

        self.mark("assertion")
        self.emit("stack_length", stack="proof_stack", dst="depth")
        present = self.fresh("present")
        self.compare_constant("depth", 0)
        self.branch(self.reject_label("stack underflow"), present)
        self.mark(present)
        self.emit("pop", stack="proof_stack", dst="expression")
        # Proof-stack values are exclusively constructed by this program.
        self.field("expression", 0, "expression_type_data", 2)
        self.field("expression", 1, "expression_tokens", 2)
        self.emit("as_integer", src="expression_type_data", dst="expression_type")
        self.require_value("expression_type", 1, "type mismatch")
        self.emit("length", src="expression_tokens", dst="expression_length")
        self.emit("clear", stack="token_build")
        self.compare_constant("label", 201)
        self.branch("negation", "non_negation")

        # ax201: wff p -> wff ~ p. The source tokens are copied by a loop.
        self.mark("negation")
        self.require_member("expression_length", [1, 2, 3], "token bound")
        self.const("token", 4)
        self.emit("box_integer", src="token", dst="token_data")
        self.emit("push", stack="token_build", src="token_data")
        self.const("expression_type", 1)
        self.const("mode", 1)
        self.jump("substitute_start")

        self.mark("non_negation")
        self.const("expression_type", 2)
        self.compare_constant("label", 202)
        self.branch("repeated_variable", "single_variable")
        # ax202: wff p -> |- p p. Both occurrences use the same token source.
        self.mark("repeated_variable")
        self.require_member("expression_length", [1, 2], "token bound")
        self.const("mode", 2)
        self.jump("substitute_start")
        self.mark("single_variable")
        self.const("mode", 1)

        self.mark("substitute_start")
        self.const("index", 0)
        self.loop("substitute_tokens", "substitute_pass_done", "index", "expression_length")
        self.emit("field_dynamic", src="expression_tokens", index="index", dst="token_data")
        self.emit("push", stack="token_build", src="token_data")
        self.increment("index")
        self.jump("substitute_tokens")
        self.mark("substitute_pass_done")
        self.compare_constant("mode", 2)
        self.branch("second_occurrence", "pack_substitution")
        self.mark("second_occurrence")
        self.const("mode", 1)
        self.jump("substitute_start")
        self.mark("pack_substitution")
        self.emit("pack", stack="token_build", tag=2, dst="new_tokens")
        self.emit("box_integer", src="expression_type", dst="new_type_data")
        self.emit("node", tag=1, fields=["new_type_data", "new_tokens"], dst="result")

        self.mark("push_result")
        self.emit("stack_length", stack="proof_stack", dst="depth")
        room = self.fresh("stack_room")
        self.compare_constant("depth", 4)
        self.branch(self.reject_label("stack overflow"), room)
        self.mark(room)
        self.emit("push", stack="proof_stack", src="result")
        self.increment("proof_index")
        self.jump("proof_loop")

        self.mark("finish")
        self.emit("stack_length", stack="proof_stack", dst="depth")
        self.require_value("depth", 1, "non-singleton proof stack")
        self.emit("pop", stack="proof_stack", dst="result")
        self.field("result", 0, "expression_type_data", 2)
        self.field("result", 1, "expression_tokens", 2)
        self.emit("as_integer", src="expression_type_data", dst="expression_type")
        self.emit("equal", left="expression_type", right="expected_type", dst="test")
        self.branch("compare_lengths", self.reject_label("type mismatch"))
        self.mark("compare_lengths")
        self.emit("length", src="expression_tokens", dst="expression_length")
        self.emit("equal", left="expression_length", right="expected_length", dst="test")
        self.branch("compare_tokens_start", self.reject_label("wrong substitution"))
        self.mark("compare_tokens_start")
        self.const("index", 0)
        self.loop("compare_tokens", "success", "index", "expression_length")
        self.emit("field_dynamic", src="expression_tokens", index="index", dst="token_data")
        self.emit("as_integer", src="token_data", dst="actual_token")
        self.emit("field_dynamic", src="expected_tokens", index="index", dst="token_data")
        self.emit("as_integer", src="token_data", dst="expected_token")
        self.emit("equal", left="actual_token", right="expected_token", dst="test")
        same = self.fresh("same_token")
        self.branch(same, self.reject_label("wrong substitution"))
        self.mark(same)
        self.increment("index")
        self.jump("compare_tokens")
        self.mark("success")
        self.emit("return", src="result")

        for reason in sorted(self.rejections):
            self.mark(self.reject_label(reason))
            self.emit("reject", reason=reason)
        for instruction in self.code:
            for key in ("target", "yes", "no"):
                if key in instruction:
                    instruction[key] = self.labels[instruction[key]]
        return {
            "schema": "adva.data-machine.program.research.v1",
            "name": "bounded-metamath-proof-step-v0",
            "registers": [{"name": name, "kind": kind} for name, kind in REGISTERS],
            "code": self.code,
        }


def generated():
    author = Author()
    return author.author(), author.labels


if __name__ == "__main__":
    destination = Path(__file__).resolve().parents[2] / "programs/bounded-metamath-step"
    destination.mkdir(parents=True, exist_ok=True)
    program, labels = generated()
    for filename, value in [("checker.adva", program), ("instruction-labels.json", labels)]:
        (destination / filename).write_text(json.dumps(value, indent=2) + "\n")
    print(json.dumps({"registers": len(REGISTERS), "instructions": len(program["code"])}))
