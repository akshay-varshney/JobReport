# Design Documentation

This project is a command-line Python application that reads job execution records from a JSON file, validates the records, calculates summary metrics, and prints the result as JSON.

Each module has a single responsibility: file handling and validation, aggregation, domain models, and the command-line entry point.

## High-level block diagram

```text
+------------------+
|  JSON input file |
+--------+---------+
         |
         v
+------------------+      invalid JSON / unreadable file
|      cli.py      |------------------------------+
| parse arguments  |                              |
+--------+---------+                              v
         |                                +---------------+
         v                                | stderr error  |
+------------------+                      | exit code 2   |
|    reader.py     |                      +---------------+
| read JSON file   |
| validate records |
+--------+---------+
         |
         | valid JobRecord objects
         | plus validation warnings
         v
+------------------+      invalid records
|    summary.py    |<-----------------------------+
| group by job_id  |                              |
| calculate stats  |                              v
+--------+---------+                      +----------------+
         |                                | stderr warning |
         v                                +----------------+
+------------------+
|   Summary model  |
| convert to dict  |
+--------+---------+
         |
         v
+------------------+
|   JSON output    |
| stdout           |
+------------------+
```

## Module responsibilities

### `cli.py`

`cli.py` is the application entry point. It is responsible for:

- parsing command-line arguments;
- calling the reader;
- printing validation warnings to stderr;
- calling the summary calculator;
- printing the final summary JSON to stdout;
- returning appropriate exit codes.

It does not contain validation or aggregation logic; it only wires the other modules together.

### `reader.py`

`reader.py` is responsible for input handling and validation.

It:

- opens and parses the JSON file;
- checks that the top-level JSON value is an array;
- validates each record;
- converts valid records into `JobRecord` objects;
- collects validation errors for invalid records;
- rejects duplicate `(job_id, attempt)` pairs.

Invalid records are skipped with warnings. Invalid JSON or unreadable files are treated as file-level errors because the program cannot safely continue.

### `summary.py`

`summary.py` contains the core business logic.

It:

- groups valid records by `job_id`;
- sorts each job's attempts by attempt number;
- treats the highest attempt as the final state;
- counts successful and failed jobs;
- counts jobs that required retries;
- calculates the average duration of final successful attempts.

This module does not know anything about files, command-line arguments, or terminal output. It is unit tested directly with in-memory `JobRecord` objects.

### `models.py`

`models.py` contains dataclasses:

- `JobRecord`: validated job attempt data;
- `Summary`: calculated summary data.

Using dataclasses keeps the data structure explicit and avoids passing raw dictionaries throughout the application.

## Data flow

1. The user runs the program with a JSON file path.
2. `cli.py` parses the command-line arguments.
3. `reader.py` loads the JSON file.
4. Each raw JSON object is validated.
5. Valid records become `JobRecord` objects.
6. Invalid records are reported as warnings and skipped.
7. `summary.py` groups valid records by job ID.
8. Summary metrics are calculated.
9. `cli.py` prints the summary as JSON.

## Error handling strategy

There are two levels of errors:

| Error type | Example | Behavior |
| --- | --- | --- |
| File-level error | invalid JSON, unreadable file, top-level value is not an array | print error to stderr and exit with code `2` |
| Record-level error | missing field, invalid status, duplicate attempt, invalid timestamp | print warning to stderr and skip the record |

This approach allows the application to produce useful output when only some records are bad, while still failing clearly when the entire input file is unusable.

## Trade-offs

- **Standard library only.** No third-party dependencies to install; `dataclasses` and explicit validation cover the five input fields. A schema library (e.g. Pydantic) would be worth adding if the input format grows.
- **Whole file loaded into memory.** Suitable for the expected input size; streaming (e.g. JSON Lines) would be needed for very large files.
- **Skip bad records instead of failing.** One malformed record should not hide a useful summary; warnings on stderr keep the problem visible.
- **Output to stdout, diagnostics to stderr.** The JSON summary can be piped to other tools without being mixed with warnings.

## Testing approach

The main business logic is separated from file and terminal handling.

For example:

- `reader.py` can be tested with temporary JSON files.
- `summary.py` can be tested directly with `JobRecord` objects.
- `cli.py` is covered by end-to-end tests that check stdout, stderr, and the exit code.

## Assumptions and future improvements

Business rules (for example how retries and final status are determined) and planned improvements are documented in [README.md](README.md) so they are kept in one place.
