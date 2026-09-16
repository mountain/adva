"""Project-original labelled assembly of a bounded Adva research program.

ChatGPT (OpenAI), through Mingli Yuan's account proxy; Unknown v0.3.
This host assembler only resolves instruction labels; it computes no answer.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
code, labels = [], {}


def emit(op, **fields):
    code.append(dict(op=op, **fields))


def label(name):
    assert name not in labels
    labels[name] = len(code)


def integer_range(reg, maximum, name):
    emit("constant", dst=6, value=1)
    emit("constant", dst=8, value=maximum)
    label(name)
    emit("equal", left=reg, right=6, dst=10)
    emit("branch", condition=10, yes=name+"_done", no=name+"_next")
    label(name+"_next")
    emit("equal", left=6, right=8, dst=10)
    emit("branch", condition=10, yes="reject", no=name+"_inc")
    label(name+"_inc")
    emit("add", left=6, right=7, dst=6)
    emit("jump", target=name)
    label(name+"_done")


def ordered(left, right, maximum, name):
    emit("copy", src=left, dst=6)
    emit("constant", dst=8, value=maximum)
    label(name)
    emit("equal", left=6, right=right, dst=10)
    emit("branch", condition=10, yes=name+"_done", no=name+"_next")
    label(name+"_next")
    emit("equal", left=6, right=8, dst=10)
    emit("branch", condition=10, yes="reject", no=name+"_inc")
    label(name+"_inc")
    emit("add", left=6, right=7, dst=6)
    emit("jump", target=name)
    label(name+"_done")


emit("input", dst=11)
emit("tag", src=11, dst=5)
emit("constant", dst=7, value=0)
emit("equal", left=5, right=7, dst=10)
emit("branch", condition=10, yes="read", no="reject")
label("read")
for i in range(4):
    emit("field", src=11, arity=4, index=i, dst=12)
    emit("as_integer", src=12, dst=i)
emit("constant", dst=7, value=1)
for reg, maximum in [(0, 6), (1, 6), (2, 8), (3, 8)]:
    integer_range(reg, maximum, "range_"+str(reg))
ordered(1, 0, 6, "k_le_n")
ordered(2, 3, 8, "a_le_b")

# E = n*a/[k*(a+b)]; positivity and order were checked first.
emit("add", left=2, right=3, dst=4)
emit("multiply", left=0, right=2, dst=5)
emit("multiply", left=1, right=4, dst=9)
emit("box_integer", src=5, dst=12)
emit("box_integer", src=9, dst=15)
emit("node", tag=1, fields=[12, 15], dst=13)
emit("equal", left=5, right=9, dst=10)
emit("branch", condition=10, yes="matched", no="unmatched")
label("matched")
emit("constant", dst=6, value=1)
emit("jump", target="match_flag")
label("unmatched")
emit("constant", dst=6, value=0)
label("match_flag")
emit("box_integer", src=6, dst=11)

# Var(J/k) = n*a*b/[k^2*(a+b)^2]; no square root or floating point.
emit("multiply", left=5, right=3, dst=5)
emit("multiply", left=9, right=9, dst=9)
emit("box_integer", src=5, dst=12)
emit("box_integer", src=9, dst=15)
emit("node", tag=2, fields=[12, 15], dst=14)
emit("equal", left=0, right=1, dst=10)
emit("branch", condition=10, yes="full", no="partial")
label("full")
emit("constant", dst=6, value=1)
emit("jump", target="coverage_flag")
label("partial")
emit("constant", dst=6, value=0)
label("coverage_flag")
emit("box_integer", src=6, dst=12)
emit("node", tag=4, fields=[11, 12], dst=15)

# The full-support subset has positive mass a^n/(a+b)^n.
# When k<n it witnesses an omitted candidate; not the complete tail mass.
emit("constant", dst=5, value=1)
emit("constant", dst=9, value=1)
emit("constant", dst=6, value=0)
label("power")
emit("multiply", left=5, right=2, dst=5)
emit("multiply", left=9, right=4, dst=9)
emit("add", left=6, right=7, dst=6)
emit("equal", left=6, right=0, dst=10)
emit("branch", condition=10, yes="power_done", no="power")
label("power_done")
emit("equal", left=0, right=1, dst=10)
emit("branch", condition=10, yes="no_gap", no="gap_output")
label("no_gap")
emit("constant", dst=5, value=0)
label("gap_output")
emit("box_integer", src=5, dst=11)
emit("box_integer", src=9, dst=12)
emit("node", tag=3, fields=[15, 11, 12], dst=15)
emit("node", tag=0, fields=[13, 14, 15], dst=15)
emit("return", src=15)
label("reject")
emit("reject", reason="outside mean-constraint-match finite domain")

for ins in code:
    for key in ("yes", "no", "target"):
        if key in ins:
            ins[key] = labels[ins[key]]
assert len(code) <= 128, len(code)
names = ["n", "k", "a", "b", "sum", "num", "counter", "one", "maximum", "den",
         "test", "input", "temp", "mean", "variance", "result"]
registers = [dict(name=name, kind="integer" if i<10 else "boolean" if i==10 else "data")
             for i, name in enumerate(names)]
program = dict(schema="adva.data-machine.program.research.v0", name="mean-constraint-match",
               registers=registers, code=code)
(HERE/"mean-constraint-match.adva").write_text(json.dumps(program, indent=2)+"\n")
(HERE/"input.json").write_text(json.dumps(dict(kind="node", tag=0,
    fields=[dict(kind="integer", value=v) for v in (3, 1, 1, 2)]), indent=2)+"\n")
print(json.dumps(dict(instructions=len(code), registers=len(registers))))
