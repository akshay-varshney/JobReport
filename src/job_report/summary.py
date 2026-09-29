from __future__ import annotations

from collections import defaultdict

from job_report.models import JobRecord, Summary


def summarize(records: list[JobRecord]) -> Summary:
    jobs: dict[str, list[JobRecord]] = defaultdict(list)
    for record in records:
        jobs[record.job_id].append(record)

    successful_durations: list[float] = []
    failed_jobs = 0
    jobs_requiring_retries = 0

    for attempts in jobs.values():
        attempts.sort(key=lambda record: record.attempt)
        final_attempt = attempts[-1]

        # attempt > 1 implies earlier attempts existed, even if they are not in the input.
        if len(attempts) > 1 or final_attempt.attempt > 1:
            jobs_requiring_retries += 1

        if final_attempt.status == "success":
            successful_durations.append(final_attempt.duration_seconds)
        else:
            failed_jobs += 1

    successful_jobs = len(successful_durations)
    average_duration = (
        sum(successful_durations) / successful_jobs
        if successful_jobs
        else None
    )

    return Summary(
        total_jobs=len(jobs),
        successful_jobs=successful_jobs,
        failed_jobs=failed_jobs,
        average_successful_duration_seconds=average_duration,
        jobs_requiring_retries=jobs_requiring_retries,
    )
