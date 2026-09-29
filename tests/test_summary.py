from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from job_report.models import JobRecord
from job_report.summary import summarize


class SummaryTests(unittest.TestCase):
    def test_summarizes_success_failure_and_retries(self) -> None:
        records = [
            record("job-1", "failed", 0, 60, 1),
            record("job-1", "success", 120, 300, 2),
            record("job-2", "success", 0, 60, 1),
            record("job-3", "failed", 0, 30, 1),
        ]

        summary = summarize(records)

        self.assertEqual(summary.total_jobs, 3)
        self.assertEqual(summary.successful_jobs, 2)
        self.assertEqual(summary.failed_jobs, 1)
        self.assertEqual(summary.jobs_requiring_retries, 1)
        self.assertEqual(summary.average_successful_duration_seconds, 120)

    def test_single_record_with_attempt_above_one_counts_as_retry(self) -> None:
        summary = summarize([record("job-1", "success", 0, 60, 2)])

        self.assertEqual(summary.jobs_requiring_retries, 1)

    def test_average_is_none_when_no_jobs_succeeded(self) -> None:
        summary = summarize([record("job-1", "failed", 0, 10, 1)])

        self.assertIsNone(summary.average_successful_duration_seconds)

    def test_empty_input_returns_zero_summary(self) -> None:
        summary = summarize([])

        self.assertEqual(summary.total_jobs, 0)
        self.assertEqual(summary.successful_jobs, 0)
        self.assertEqual(summary.failed_jobs, 0)
        self.assertIsNone(summary.average_successful_duration_seconds)
        self.assertEqual(summary.jobs_requiring_retries, 0)


def record(job_id: str, status: str, start_second: int, finish_second: int, attempt: int) -> JobRecord:
    base_time = datetime(2026, 9, 28, 10, 0, 0, tzinfo=timezone.utc)
    return JobRecord(
        job_id=job_id,
        status=status,
        started_at=base_time + timedelta(seconds=start_second),
        finished_at=base_time + timedelta(seconds=finish_second),
        attempt=attempt,
    )


if __name__ == "__main__":
    unittest.main()
