from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from xlodit.audit import audit_workbook


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit .xlsx workbook files")
    parser.add_argument("filepath", help="Path to workbook")
    parser.add_argument(
        "--backend", choices=["auto", "libreoffice", "none"], default="auto"
    )
    parser.add_argument("--format", choices=["terminal", "json"], default="terminal")
    parser.add_argument("--output", help="Write output to file")
    parser.add_argument("--max-traceback-depth", type=int, default=10)
    return parser


def _terminal_output(report_dict: dict) -> str:
    summary = report_dict["summary"]
    lines = [
        "xlodit audit report",
        f"ok: {report_dict['ok']}",
        f"audit_completed: {report_dict['audit_completed']}",
        f"backend: requested={report_dict['backend']['requested']} used={report_dict['backend']['used']} recalculated={report_dict['backend']['recalculated']}",
        f"summary: errors={summary['errors']} warnings={summary['warnings']} total={summary['total']}",
    ]
    for issue in report_dict["issues"]:
        loc = ""
        if issue.get("sheet") and issue.get("cell"):
            loc = f" ({issue['sheet']}!{issue['cell']})"
        lines.append(
            f"- [{issue['severity']}] {issue['rule_id']} {issue['kind']}{loc}: {issue['message']}"
        )
    return "\n".join(lines)


def _exit_code(report_dict: dict) -> int:
    if not report_dict["audit_completed"]:
        return 2
    if report_dict["summary"]["errors"] > 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    report = audit_workbook(
        args.filepath,
        backend=args.backend,
        max_traceback_depth=args.max_traceback_depth,
    )
    report_dict = report.to_dict()

    if args.format == "json":
        output_text = json.dumps(report_dict, sort_keys=True, separators=(",", ":"))
    else:
        output_text = _terminal_output(report_dict)

    if args.output:
        Path(args.output).write_text(output_text + "\n", encoding="utf-8")
    else:
        print(output_text)

    return _exit_code(report_dict)


if __name__ == "__main__":
    sys.exit(main())
