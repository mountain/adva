"""One receiving preflight before the frozen full campaign."""
import argparse
import json
from pathlib import Path
import resource
import time

from campaign import Campaign, HERE, ROOT, digest, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (805306368,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (15,) * 2)
    args.output.mkdir(parents=True, exist_ok=False)
    contract = json.loads((HERE / "contract.json").read_text())
    campaign = Campaign(args.binary.resolve(), args.output.resolve(), contract)
    started = time.monotonic()
    try:
        data = json.loads((ROOT / "programs/bounded-interpreter/input.json").read_text())
        result, _ = campaign.launch("sample", data)
        campaign.check(result["state"]["phase"]["value"]["value"] == 14)
        save(args.output / "result.json", {"status": "Passed", "native_steps": result["state"]["spent"],
             "reference_steps": campaign.budget.steps, "wall_seconds": time.monotonic() - started,
             "source_sha256": {name: digest(ROOT / name) for name in (
                 "crates/adva-witness/src/data_machine.rs", "experiments/bounded_native_interpreter/reference.py",
                 "programs/bounded-interpreter/interpreter.adva")}})
        print((args.output / "result.json").read_text())
    except Exception as exc:
        save(args.output / "failure.json", {"error": type(exc).__name__, "message": str(exc)})
        raise


if __name__ == "__main__":
    main()
