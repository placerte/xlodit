# xlodit

`xlodit` audits `.xlsx` workbooks and emits deterministic machine-readable reports.

## Scope
- Detects formula errors and formula error datatypes
- Detects numeric values stored as text (regex-based)
- Runs minimal structural checks
- Builds traceback trees for failing formula cells
- Read-only: never mutates the input workbook

## Install / Run
From PyPI:

```bash
pip install xlodit
```

Use `uv` during development:

```bash
uv run xlodit path/to/workbook.xlsx
```

By default, `xlodit` prints a Rich terminal report and writes a JSON dump to `<filepath>.xlodit.json`.
Use `--format json` to print JSON to stdout. Terminal output uses `rich` for improved formatting.

## CLI
```bash
uv run xlodit <filepath> [--backend auto|libreoffice|none] [--format terminal|json] [--output path] [--max-traceback-depth N]
```

Use `--help` to see full option descriptions and defaults.

## Exit Codes
- `0`: audit completed and no errors
- `1`: audit completed and at least one error
- `2`: tool/runtime failure

## Limitations
- `.xlsx` only
- No `.xlsm` / `.ods`
- No macro/VBA analysis
- No formatting/chart/pivot validation
- No workbook mutation or auto-fix
- No full Excel formula engine

## License
MIT

## JSON Output
Primary output format is canonical JSON:

- Stable key ordering
- Deterministic issue ordering (severity, sheet, cell, rule)

You can write JSON output to a file with `--output`.

## Agentic Use
- Deterministic JSON ordering for reliable diffs
- Stable rule IDs and issue kinds
- Exit codes map cleanly to success, error, or runtime failure

## Example
```bash
uv run xlodit sample.xlsx --format json --output report.json
```

```bash
uv run xlodit sample.xlsx --format terminal
```

## API
Programmatic use is available via `audit_workbook`:

```python
from xlodit import audit_workbook

report = audit_workbook("/path/to/workbook.xlsx", backend="auto", max_traceback_depth=10)
report_dict = report.to_dict()
```

Key fields in the JSON report:

- `ok`: boolean success indicator
- `audit_completed`: whether the audit finished without runtime failure
- `backend`: backend details (requested, used, recalculated)
- `summary`: counts for errors, warnings, total
- `issues`: list of issues with `severity`, `kind`, `rule_id`, `message`, and location fields

For `formula_error` issues, `traceback` includes a tree of referenced cells. Each node has `sheet`, `cell`, `failing`, optional `value`, and `children` for upstream dependencies.
