# xlodit

`xlodit` audits `.xlsx` workbooks and emits deterministic machine-readable reports.

## Scope
- Detects formula errors and formula error datatypes
- Detects numeric values stored as text (regex-based)
- Runs minimal structural checks
- Builds traceback trees for failing formula cells
- Read-only: never mutates the input workbook

## Install / Run
Use `uv`:

```bash
uv run xlodit path/to/workbook.xlsx
```

## CLI
```bash
uv run xlodit <filepath> [--backend auto|libreoffice|none] [--format terminal|json] [--output path] [--max-traceback-depth N]
```

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

## JSON Output
Primary output format is canonical JSON:

- Stable key ordering
- Deterministic issue ordering (severity, sheet, cell, rule)

You can write output to a file with `--output`.

## Example
```bash
uv run xlodit sample.xlsx --format json --output report.json
```
