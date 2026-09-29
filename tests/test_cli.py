from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from job_report.cli import main


class CliTests(unittest.TestCase):
    def test_prints_summary_to_stdout_and_warnings_to_stderr(self) -> None:
        records = [
            {
                "job_id": "job-1",
                "status": "success",
                "started_at": "2026-09-28T10:00:00+00:00",
                "finished_at": "2026-09-28T10:01:00+00:00",
                "attempt": 1,
            },
            {"job_id": "", "status": "success"},
        ]

        exit_code, stdout, stderr = run_cli(json.dumps(records))

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            json.loads(stdout),
            {
                "total_jobs": 1,
                "successful_jobs": 1,
                "failed_jobs": 0,
                "average_successful_duration_seconds": 60.0,
                "jobs_requiring_retries": 0,
            },
        )
        self.assertIn("warning: skipped", stderr)

    def test_invalid_json_file_returns_exit_code_2(self) -> None:
        exit_code, stdout, stderr = run_cli("{not valid json")

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("error:", stderr)


def run_cli(file_content: str) -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "jobs.json"
        path.write_text(file_content, encoding="utf-8")

        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([str(path)])

    return exit_code, stdout.getvalue(), stderr.getvalue()


if __name__ == "__main__":
    unittest.main()
