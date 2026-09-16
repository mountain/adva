#!/usr/bin/env python3
"""Problem card and round worksheet validation.

Item two of `docs/TOOLING_WORKFLOW.md` section 6. The card is the ten-field table of
section 2; a round adds the attempt list and the handoff summary of section 3.

This command validates a card; it never fills one in. Missing information is reported
field by field and kept missing, because a tool that supplies the answer erases the
one thing the card exists to record. The rules it enforces are the ones the workflow
states:

- all ten fields are present and non-empty;
- changing the question, the check scope or the budget requires a successor round with
  a predecessor reference and a recorded reason (section 2);
- every attempt declares its command, output directory, stop condition and budget, and
  a failed or refused attempt keeps its first failure (section 3 step 3);
- an attempt that could not run keeps `not-run` with its reason rather than a silent
  omission (section 8);
- the handoff carries the question, candidates, checks, evidence and residuals, and
  states whether the receiver confirmed it is the same question (section 3 step 5).

Usage:

    python3 scripts/problem_card.py template
    python3 scripts/problem_card.py check path/to/card.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

FIELDS = [
    ("raw_question", "原始问题", "对方实际要解决什么；保留原文或准确来源。"),
    ("objects_and_versions", "对象与版本", "代码提交、输入、数据版本；区分原始文件、摘录、重建和缺失。"),
    ("success_condition", "成功条件", "哪个可观察行为算成功，谁或哪个检查器作出哪一种判断。"),
    ("interpretation_and_assumptions", "解释与前提", "对象如何进入模型；假设了什么，哪些部分还没有对应关系。"),
    ("candidates", "当前候选", "不同解法或解释；保留彼此尚不能区分的地方。"),
    ("check_scope", "检查范围", "输入集合、语言片段、覆盖条件，以及是否有充分性证明。"),
    ("budget", "本轮预算", "执行、检查、重试、子进程、读写和保存共同使用的有限预算。"),
    ("round_result", "本轮结果", "原始输出、实际检查、反例或错误；不能只保存摘要分数。"),
    ("remaining_questions", "剩余问题", "未覆盖输入、未知前提、缺失解释、实现缺口或预算耗尽。"),
    ("next_step", "下一步", "改变哪种观察、方法或前提；为什么可能得到不同结论。"),
]
# Every field of the card is prose except the budget, which is the declared finite
# budget itself and is validated as numbers rather than as text.
TEXT_FIELDS = [field for field in FIELDS if field[0] != "budget"]
HANDOFF_FIELDS = ["question", "candidates", "checks", "evidence", "residuals"]
OUTCOMES = {"completed", "failed", "refused", "not-run"}
BUDGET_PARTS = ("launches", "cpu_seconds", "host_work_units", "wall_seconds", "output_bytes")


def template() -> str:
    rows = "\n".join(f"| {label} | `{key}` | | {hint} |" for key, label, hint in FIELDS)
    skeleton = {
        "question_id": "", "round": 1, "predecessor": None, "change_reason": "",
        **{key: "" for key, _, _ in TEXT_FIELDS},
        "budget": {"wall_seconds": 0, "launches": 0},
        "stop_conditions": [],
        "attempts": [{"command": "", "tool_and_version": "", "input": "",
                      "output_dir": "", "stop_condition": "",
                      "budget": {"wall_seconds": 0, "launches": 0},
                      "outcome": "not-run", "reason": "", "first_failure": ""}],
        "handoff": {**{field: "" for field in HANDOFF_FIELDS},
                    "receiver_confirms_same_question": False},
    }
    return (
        "# 问题卡（一轮一个问题）\n\n"
        "| 项目 | key | 内容 | 要写清楚的内容 |\n|---|---|---|---|\n"
        f"{rows}\n\n"
        "改题目、改检查范围或改预算，请新建一轮并填写 `predecessor` 与 `change_reason`。\n\n"
        "## 供检查器读取的骨架\n\n```json\n"
        + json.dumps(skeleton, indent=2, ensure_ascii=False)
        + "\n```\n"
    )


def is_text(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def check_budget(budget, problems: list[str], where: str) -> None:
    if not isinstance(budget, dict):
        problems.append(f"{where}: budget must be an object with finite numbers")
        return
    declared = [key for key in BUDGET_PARTS
                if isinstance(budget.get(key), (int, float)) and not isinstance(budget.get(key), bool)
                and budget[key] > 0]
    if "wall_seconds" not in declared:
        problems.append(f"{where}: budget declares no positive wall_seconds")
    if len(declared) < 2:
        problems.append(f"{where}: budget declares only {declared or 'nothing'}; a finite round "
                        "budget needs a time bound and at least one work bound")


def check_card(card: dict, path: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for key, label, _ in TEXT_FIELDS:
        if not is_text(card.get(key)):
            problems.append(f"missing field `{key}` ({label})")
    if not is_text(card.get("question_id")):
        problems.append("missing field `question_id`: a round must be attributable")
    if not isinstance(card.get("round"), int) or isinstance(card.get("round"), bool) \
            or card.get("round", 0) < 1:
        problems.append("field `round` must be a positive integer")
    check_budget(card.get("budget"), problems, "card")
    stops = card.get("stop_conditions")
    if not isinstance(stops, list) or not stops or not all(is_text(item) for item in stops):
        problems.append("field `stop_conditions` must be a non-empty list of statements")

    attempts = card.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        problems.append("field `attempts` must hold at least one bounded attempt")
    else:
        for index, attempt in enumerate(attempts):
            where = f"attempts[{index}]"
            if not isinstance(attempt, dict):
                problems.append(f"{where}: must be an object")
                continue
            for key in ("command", "output_dir", "stop_condition"):
                if not is_text(attempt.get(key)):
                    problems.append(f"{where}: missing `{key}`")
            check_budget(attempt.get("budget"), problems, where)
            outcome = attempt.get("outcome")
            if outcome not in OUTCOMES:
                problems.append(f"{where}: outcome {outcome!r} is not one of {sorted(OUTCOMES)}")
            if outcome in {"failed", "refused"} and not is_text(attempt.get("first_failure")):
                problems.append(f"{where}: outcome {outcome} must retain `first_failure`")
            if outcome == "not-run" and not is_text(attempt.get("reason")):
                problems.append(f"{where}: outcome not-run must retain `reason`")

    handoff = card.get("handoff")
    if not isinstance(handoff, dict):
        problems.append("field `handoff` must be an object")
    else:
        for key in HANDOFF_FIELDS:
            if not is_text(handoff.get(key)):
                problems.append(f"handoff: missing `{key}`")
        confirmed = handoff.get("receiver_confirms_same_question")
        if not isinstance(confirmed, bool):
            problems.append("handoff: `receiver_confirms_same_question` must be true or false")
        elif not confirmed:
            problems.append("handoff: the receiver has not confirmed this is the same question; "
                            "the round stays open rather than complete")

    predecessor = card.get("predecessor")
    if predecessor:
        previous_path = (path.parent / predecessor).resolve()
        if not previous_path.exists():
            problems.append(f"predecessor {predecessor} does not exist beside this card")
        else:
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
            changed = [key for key in ("raw_question", "check_scope", "budget")
                       if previous.get(key) != card.get(key)]
            if changed and not is_text(card.get("change_reason")):
                problems.append("predecessor round, but " + ", ".join(changed)
                                + " changed with no `change_reason`: a changed question, scope or "
                                  "budget needs its own recorded reason")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("template", help="print the problem card and a JSON skeleton")
    check = sub.add_parser("check", help="validate a filled card")
    check.add_argument("card")
    args = parser.parse_args()

    if args.action == "template":
        print(template())
        return 0

    path = pathlib.Path(args.card)
    if not path.exists():
        print(f"{path} does not exist", file=sys.stderr)
        return 1
    card = json.loads(path.read_text(encoding="utf-8"))
    problems = check_card(card, path)
    if problems:
        print(f"{path}: incomplete — {len(problems)} open item(s), none filled in for you:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"{path}: complete for round {card['round']} of {card['question_id']} "
          f"with {len(card['attempts'])} attempt(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
