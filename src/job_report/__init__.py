"""Job execution summary package."""

from job_report.models import JobRecord, Summary
from job_report.summary import summarize

__all__ = ["JobRecord", "Summary", "summarize"]
