#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026
"""
"""Command-line entry points for the UVOT subtraction pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from processing import process
from uvot_io.archive import get_obs_path
from uvot_io.batch import extract_input, index_inputs, missing_filenames, parse_manifest


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"


def main(obsid: int | str, filter_name: str):
    """Process one archive observation using the original command interface."""

    observation_path = get_obs_path(obsid, filter_name, DATA_DIR)
    result = process(
        observation_path,
        obsid,
        output_dir=DATA_DIR / "processed" / f"{obsid}_{filter_name}",
        reference_dir=DATA_DIR / "reference",
    )
    print("Done.")
    return result


def _format_missing_inputs(missing: list[str]) -> str:
    preview_limit = 20
    preview = "\n".join(f"  - {filename}" for filename in missing[:preview_limit])
    remaining = len(missing) - preview_limit
    if remaining > 0:
        preview += f"\n  - ... and {remaining} more"
    return (
        f"{len(missing)} manifest input file(s) are absent from the supplied "
        f"ZIP archive(s) and source directory/directories:\n{preview}\n"
        "Supply every split ZIP with --archive or add a directory with "
        "--source-dir."
    )


def batch_main(args: argparse.Namespace) -> int:
    """Extract and process each exact FITS extension named in a manifest."""

    entries = parse_manifest(args.manifest)
    members = index_inputs(args.archives, args.source_dirs)
    missing = missing_filenames(entries, members)
    if missing and not args.allow_missing:
        raise SystemExit(_format_missing_inputs(missing))

    input_dir = Path(args.input_dir)
    output_root = Path(args.output_dir)
    reference_dir = Path(args.reference_dir)
    failures: list[str] = []
    skipped = 0
    attempted = 0

    for position, entry in enumerate(entries, start=1):
        member = members.get(entry.filename)
        if member is None:
            skipped += 1
            print(
                f"[{position}/{len(entries)}] missing input: {entry.filename} "
                f"(manifest line {entry.line_number})"
            )
            continue

        print(
            f"[{position}/{len(entries)}] {entry.filename} "
            f"version={entry.version} EXTNAME={entry.extension_name}"
        )
        observation_path = extract_input(
            member, input_dir / entry.input_filename
        )
        attempted += 1
        try:
            process(
                observation_path,
                obs_extension_name=entry.extension_name,
                output_dir=output_root / entry.output_key,
                reference_dir=reference_dir,
            )
        except Exception as error:
            message = (
                f"{entry.filename}|{entry.version}|{entry.extension_name}: "
                f"{type(error).__name__}: {error}"
            )
            failures.append(message)
            print(f"FAILED: {message}", file=sys.stderr)
            if args.fail_fast:
                break

    print(
        f"Batch complete: {attempted - len(failures)} succeeded, "
        f"{len(failures)} failed, {skipped} missing."
    )
    if failures:
        print("Failed entries:", file=sys.stderr)
        print("\n".join(f"  - {message}" for message in failures), file=sys.stderr)
    return 1 if failures or skipped else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    single = subparsers.add_parser("single", help="process one archive observation")
    single.add_argument("obsid")
    single.add_argument("filter_name")

    batch = subparsers.add_parser(
        "batch", help="process filename|version|EXTNAME entries from a manifest"
    )
    batch.add_argument("--manifest", type=Path, required=True)
    batch.add_argument(
        "--archive",
        dest="archives",
        type=Path,
        action="append",
        default=[],
        help="input ZIP; specify once for every split archive",
    )
    batch.add_argument(
        "--source-dir",
        dest="source_dirs",
        type=Path,
        action="append",
        default=[],
        help="directory containing already-extracted *.img.gz input files",
    )
    batch.add_argument("--input-dir", type=Path, default=DATA_DIR / "input")
    batch.add_argument("--output-dir", type=Path, default=DATA_DIR / "processed")
    batch.add_argument("--reference-dir", type=Path, default=DATA_DIR / "reference")
    batch.add_argument(
        "--allow-missing",
        action="store_true",
        help="process available entries and report absent manifest inputs",
    )
    batch.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop after the first pipeline error instead of attempting later entries",
    )
    return parser


if __name__ == "__main__":
    # Preserve the documented legacy form: ``python main.py <obsid> <filter>``.
    if len(sys.argv) == 3 and sys.argv[1] not in {"single", "batch"}:
        main(sys.argv[1], sys.argv[2])
    else:
        parsed_args = build_parser().parse_args()
        if parsed_args.command == "single":
            main(parsed_args.obsid, parsed_args.filter_name)
        else:
            raise SystemExit(batch_main(parsed_args))
