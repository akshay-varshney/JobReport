from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from job_report.models import JobRecord

VALID_STATUSES = {"success", "failed"}


class InputFileError(Exception):
    """Raised when the input file cannot be parsed as a usable JSON document."""


def read_records(path: str | Path) -> tuple[list[JobRecord], list[str]]:
    """Read valid job records and return validation errors for skipped records."""
    try:
        with Path(path).open(encoding="utf-8") as file:
            raw_data = json.load(file)
    except json.JSONDecodeError as error:
        raise InputFileError(f"Invalid JSON: {error}") from error
    except OSError as error:
        raise InputFileError(f"Could not read input file: {error}") from error

    if not isinstance(raw_data, list):
        raise InputFileError("Input JSON must be an array of job records")

    records: list[JobRecord] = []
    errors: list[str] = []
    seen_attempts: set[tuple[str, int]] = set()

    for index, item in enumerate(raw_data):
        try:
            record = _parse_record(item)
            key = (record.job_id, record.attempt)
            if key in seen_attempts:
                raise ValueError(f"duplicate attempt for job_id={record.job_id!r}, attempt={record.attempt}")
            seen_attempts.add(key)
            records.append(record)
        except ValueError as error:
            errors.append(f"record {index}: {error}")

    return records, errors


def _parse_record(item: Any) -> JobRecord:
    if not isinstance(item, dict):
        raise ValueError("record must be an object")

    job_id = _required_string(item, "job_id")
    status = _required_string(item, "status")
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")

    started_at = _required_datetime(item, "started_at")
    finished_at = _required_datetime(item, "finished_at")
    if finished_at < started_at:
        raise ValueError("finished_at must be greater than or equal to started_at")

    attempt = item.get("attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt <= 0:
        raise ValueError("attempt must be a positive integer")

    return JobRecord(
        job_id=job_id,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        attempt=attempt,
    )


def _required_string(item: dict[str, Any], field_name: str) -> str:
    value = item.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _required_datetime(item: dict[str, Any], field_name: str) -> datetime:
    value = item.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO 8601 timestamp string")

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field_name} must be a valid ISO 8601 timestamp") from error

    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone information")

    return parsed
