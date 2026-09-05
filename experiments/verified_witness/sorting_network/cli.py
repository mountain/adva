from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import cast

from .model import (
    PROGRAM_ORDER,
    DepthReport,
    ProgramName,
    SearchCheckpoint,
    SearchConfig,
    SearchResult,
    canonical_json,
)
from .search import run_search, verify_result_file


def parse_programs(value: str) -> tuple[ProgramName, ...]:
    if value == "all":
        return PROGRAM_ORDER
    names = tuple(item.strip() for item in value.split(",") if item.strip())
    invalid = set(names) - set(PROGRAM_ORDER)
    if invalid:
        raise argparse.ArgumentTypeError(f"unknown programs: {sorted(invalid)!r}")
    return tuple(cast(ProgramName, item) for item in names)


def add_search_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--channels", type=int, required=True)
    parser.add_argument("--max-depth", type=int, required=True)
    parser.add_argument("--beam-width", type=int, default=64)
    parser.add_argument("--spatial-branching", type=int, default=32)
    parser.add_argument("--construction-branching", type=int, default=16)
    parser.add_argument("--temporal-branching", type=int, default=16)
    parser.add_argument("--temporal-backtrack", type=int, default=2)
    parser.add_argument("--exhaustive-layer-channels", type=int, default=8)
    parser.add_argument("--programs", type=parse_programs, default=PROGRAM_ORDER)
    parser.add_argument("--max-oracle-mib", type=int, default=512)
    parser.add_argument("--evaluation-cache-entries", type=int, default=4096)
    parser.add_argument("--allow-large-oracle", action="store_true")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)


def config_from_args(args: argparse.Namespace) -> SearchConfig:
    return SearchConfig(
        channels=args.channels,
        max_depth=args.max_depth,
        beam_width=args.beam_width,
        spatial_branching=args.spatial_branching,
        construction_branching=args.construction_branching,
        temporal_branching=args.temporal_branching,
        temporal_backtrack=args.temporal_backtrack,
        exhaustive_layer_channels=args.exhaustive_layer_channels,
        enabled_programs=args.programs,
        max_oracle_bytes=args.max_oracle_mib * 1024 * 1024,
        evaluation_cache_entries=args.evaluation_cache_entries,
        allow_large_oracle=args.allow_large_oracle,
    )


def print_depth_report(report: DepthReport) -> None:
    print(
        canonical_json({"event": "depth-complete", **report.to_data()}),
        file=sys.stderr,
        flush=True,
    )


def print_result_summary(result: SearchResult) -> None:
    verification = result.verification
    print(
        canonical_json(
            {
                "status": result.status,
                "channels": verification.channels,
                "depth": verification.depth,
                "size": verification.size,
                "residual_count": verification.residual_count,
                "network_sha256": verification.network_sha256,
            }
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="run a new bounded search")
    add_search_arguments(search_parser)

    resume_parser = subparsers.add_parser("resume", help="continue from a checkpoint")
    resume_parser.add_argument("checkpoint", type=Path)
    resume_parser.add_argument("--max-depth", type=int, required=True)
    resume_parser.add_argument("--output", type=Path, required=True)

    verify_parser = subparsers.add_parser("verify", help="verify a result or network JSON")
    verify_parser.add_argument("path", type=Path)
    verify_parser.add_argument("--max-oracle-mib", type=int, default=512)
    verify_parser.add_argument("--allow-large-oracle", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "search":
        config = config_from_args(args)
        result = run_search(
            config,
            checkpoint_path=args.checkpoint,
            progress=print_depth_report,
        )
        result.write(args.output)
        print_result_summary(result)
        return 0 if result.status == "Found" else 2

    if args.command == "resume":
        checkpoint = SearchCheckpoint.read(args.checkpoint)
        config = replace(checkpoint.config, max_depth=args.max_depth)
        result = run_search(
            config,
            checkpoint=checkpoint,
            checkpoint_path=args.checkpoint,
            progress=print_depth_report,
        )
        result.write(args.output)
        print_result_summary(result)
        return 0 if result.status == "Found" else 2

    report = verify_result_file(
        args.path,
        max_oracle_bytes=args.max_oracle_mib * 1024 * 1024,
        allow_large_oracle=args.allow_large_oracle,
    )
    print(canonical_json(report.to_data()))
    return 0 if report.sorted else 1
