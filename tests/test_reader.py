from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from job_report.reader import InputFileError, read_records


class ReadRecordsTests(unittest.TestCase):
    def test_reads_valid_records(self) -> None:
        path = write_json([
            {
                "job_id": "job-1",
                "status": "success",
                "started_at": "2026-09-28T10:00:00+00:00",
                "finished_at": "2026-09-28T10:05:00+00:00",
                "attempt": 1,
            }
        ])

        records, errors = read_records(path)

        self.assertEqual(errors, [])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].job_id, "job-1")
        self.assertEqual(records[0].duration_seconds, 300)

    def test_skips_invalid_records(self) -> None:
        path = write_json([
            {
                "job_id": "",
                "status": "success",
                "started_at": "2026-09-28T10:00:00+00:00",
                "finished_at": "2026-09-28T10:05:00+00:00",
                "attempt": 1,
            },
            {
                "job_id": "job-1",
                "status": "success",
                "started_at": "2026-09-28T10:00:00+00:00",
                "finished_at": "2026-09-28T10:05:00+00:00",
                "attempt": 1,
            },
        ])

        records, errors = read_records(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("job_id", errors[0])

    def test_rejects_duplicate_attempts(self) -> None:
        record = {
            "job_id": "job-1",
            "status": "failed",
            "started_at": "2026-09-28T10:00:00+00:00",
            "finished_at": "2026-09-28T10:01:00+00:00",
            "attempt": 1,
        }
        path = write_json([record, record])

        records, errors = read_records(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate attempt", errors[0])

    def test_rejects_non_array_input(self) -> None:
        path = write_json({"job_id": "job-1"})

        with self.assertRaises(InputFileError):
            read_records(path)


def write_json(value: object) -> Path:
    temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    with temp:
        json.dump(value, temp)
    return Path(temp.name)


if __name__ == "__main__":
    unittest.main()
