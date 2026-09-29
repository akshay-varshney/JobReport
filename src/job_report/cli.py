from __future__ import annotations

import argparse
import json
import sys

from job_report.reader import InputFileError, read_records
from job_report.summary import summarize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarise job execution records from a JSON file")
    parser.add_argument("input_file", help="Path to a JSON file containing job execution records")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the summary JSON")
    args = parser.parse_args(argv)

    try:
        records, errors = read_records(args.input_file)
    except InputFileError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for error in errors:
        print(f"warning: skipped {error}", file=sys.stderr)

    indent = 2 if args.pretty else None
    print(json.dumps(summarize(records).to_dict(), indent=indent))
    return 0
