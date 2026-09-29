# Job Report

Command-line Python application that reads job execution records from a JSON file, validates them, and prints a summary.

It uses only the Python standard library. Input reading, validation, aggregation, and command-line handling are in separate modules.

## Input format

The input file must contain a JSON array. Each item should look like this:

```json
{
  "job_id": "job-1",
  "status": "success",
  "started_at": "2026-09-28T10:00:00+00:00",
  "finished_at": "2026-09-28T10:05:00+00:00",
  "attempt": 1
}
```

Required fields:

- `job_id`: non-empty string
- `status`: `success` or `failed`
- `started_at`: timezone-aware ISO 8601 timestamp
- `finished_at`: timezone-aware ISO 8601 timestamp
- `attempt`: positive integer

## Output

The program prints JSON like this:

```json
{
  "total_jobs": 3,
  "successful_jobs": 2,
  "failed_jobs": 1,
  "average_successful_duration_seconds": 210.0,
  "jobs_requiring_retries": 1
}
```

## How to run

Requires Python 3.10+. No third-party dependencies.

Recommended: install the package in editable mode from the project root, then use the `job-report` command:

```bash
python -m pip install -e .
job-report examples/jobs.json --pretty
```

Without installing, point Python at the `src` directory:

```bash
PYTHONPATH=src python -m job_report examples/jobs.json
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m job_report examples/jobs.json
```

Pretty output:

```bash
PYTHONPATH=src python -m job_report examples/jobs.json --pretty
```

The sample file intentionally contains one invalid record (empty `job_id`), so a warning is printed to stderr.

Exit codes: `0` on success (even if some records were skipped), `2` for file-level errors (missing file, invalid JSON, non-array JSON).

## How to run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Assumptions

- Each record represents one job attempt.
- `(job_id, attempt)` must be unique.
- `total_jobs` counts distinct `job_id` values, not raw records.
- The highest attempt number is treated as the final attempt for a job.
- A job is successful if its final attempt has status `success`.
- A job is failed if its final attempt has status `failed`.
- A job required retries if it has more than one valid attempt, or if its final attempt number is greater than 1 (an `attempt = 2` record implies an earlier attempt, even if that record is missing or invalid).
- Duration is calculated as `finished_at - started_at`.
- Average successful-job duration uses the final successful attempt for each successful job.
- Invalid records are reported to stderr and skipped.
- Invalid JSON or a non-array JSON value is a file-level error.

## Project structure

```text
job-report/
├── examples/
│   └── jobs.json
├── DESIGN.md
├── src/
│   └── job_report/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── models.py
│       ├── reader.py
│       └── summary.py
└── tests/
    ├── test_cli.py
    ├── test_reader.py
    └── test_summary.py
```

## Improvements if there was more time

- Add JSON Lines support for large files.
- Add CSV output.
- Add logging instead of plain-text stderr warnings.
- Add type checking and linting.
- Add more detailed error reporting with field-level error codes.
- Add a formal JSON Schema for input validation.
- Add command-line filtering options (e.g. by status or date range).
- Add more validation-focused tests (timestamps, attempt values, file-level errors).

## Design documentation

See `DESIGN.md` for the design overview, block diagram, module responsibilities, data flow, error-handling strategy, and trade-offs.
