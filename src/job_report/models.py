from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    status: str
    started_at: datetime
    finished_at: datetime
    attempt: int

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()


@dataclass(frozen=True)
class Summary:
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    average_successful_duration_seconds: float | None
    jobs_requiring_retries: int

    def to_dict(self) -> dict[str, int | float | None]:
        return {
            "total_jobs": self.total_jobs,
            "successful_jobs": self.successful_jobs,
            "failed_jobs": self.failed_jobs,
            "average_successful_duration_seconds": self.average_successful_duration_seconds,
            "jobs_requiring_retries": self.jobs_requiring_retries,
        }
