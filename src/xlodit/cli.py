from __future__ import annotations

import argparse
import json
import sys
from importlib import metadata
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from xlodit.audit import audit_workbook


def _package_version() -> str:
    try:
        return metadata.version("xlodit")
    except metadata.PackageNotFoundError:
        return "0.1.0"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit .xlsx workbook files and emit a JSON report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("filepath", help="Path to workbook")
    parser.add_argument(
        "--backend",
        choices=["auto", "libreoffice", "none"],
        default="auto",
        help="Recalculation backend to use",
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format for stdout",
    )
    parser.add_argument(
        "--output",
        help=(
            "Write JSON output to file (defaults to <filepath>.xlodit.json when using terminal output)"
        ),
    )
    parser.add_argument(
        "--max-traceback-depth",
        type=int,
        default=10,
        help="Maximum depth for traceback traversal",
    )
    parser.add_argument(
        "--version", action="version", version=f"xlodit {_package_version()}"
    )
    return parser


def _render_terminal(report_dict: dict, console: Console) -> None:
    console.print(Panel("xlodit audit report", style="bold"))

    backend = report_dict["backend"]
    summary = report_dict["summary"]
    summary_table = Table(box=box.SIMPLE, show_header=False)
    summary_table.add_column("field", style="bold")
    summary_table.add_column("value")
    summary_table.add_row("ok", str(report_dict["ok"]))
    summary_table.add_row("audit_completed", str(report_dict["audit_completed"]))
    summary_table.add_row(
        "backend",
        f"requested={backend['requested']} used={backend['used']} recalculated={backend['recalculated']}",
    )
    summary_table.add_row(
        "summary",
        f"errors={summary['errors']} warnings={summary['warnings']} total={summary['total']}",
    )
    console.print(summary_table)

    issues = report_dict.get("issues", [])
    if not issues:
        console.print(Text("No issues detected.", style="green"))
        return

    table = Table(title="Issues", box=box.SIMPLE_HEAVY)
    table.add_column("Severity", style="bold")
    table.add_column("Rule")
    table.add_column("Kind")
    table.add_column("Location")
    table.add_column("Message", overflow="fold")

    for issue in issues:
        severity = issue.get("severity", "")
        severity_style = "red" if severity == "error" else "yellow"
        severity_text = Text(severity, style=severity_style)
        location = ""
        if issue.get("sheet") and issue.get("cell"):
            location = f"{issue['sheet']}!{issue['cell']}"
        table.add_row(
            severity_text,
            issue.get("rule_id", ""),
            issue.get("kind", ""),
            location,
            issue.get("message", ""),
        )

        traceback = _traceback_tree(issue)
        if traceback is not None:
            table.add_row("", "", "traceback", "", traceback)

    console.print(table)


def _node_label(node: dict) -> str:
    sheet = node.get("sheet")
    cell = node.get("cell")
    if sheet and cell:
        return f"{sheet}!{cell}"
    return cell or sheet or "<unknown>"


def _collect_traceback_paths(node: dict, require_failing: bool) -> list[list[str]]:
    if require_failing and not node.get("failing", False):
        return []
    children = node.get("children") or []
    child_paths: list[list[str]] = []
    for child in children:
        child_paths.extend(_collect_traceback_paths(child, require_failing))
    label = _node_label(node)
    if child_paths:
        return [[label, *path] for path in child_paths]
    return [[label]]


def _traceback_tree(issue: dict) -> Tree | None:
    traceback = issue.get("traceback")
    if not traceback:
        return None
    nodes = traceback.get("nodes") or []
    if not nodes:
        return None
    require_failing = "failing" in nodes[0]
    paths: list[list[str]] = []
    for node in nodes:
        paths.extend(_collect_traceback_paths(node, require_failing))
    if not paths:
        return None
    label = (
        "Traceback "
        f"(status={traceback.get('status')}, "
        f"cycle_detected={traceback.get('cycle_detected')}, "
        f"max_depth_reached={traceback.get('max_depth_reached')})"
    )
    tree = Tree(label, guide_style="dim")
    for path in paths:
        tree.add(" -> ".join(path))
    return tree


def _exit_code(report_dict: dict) -> int:
    if not report_dict["audit_completed"]:
        return 2
    if report_dict["summary"]["errors"] > 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    use_rich = args.format == "terminal" and not args.output
    console = Console() if use_rich else None

    if use_rich:
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Scanning workbook", total=None)
            report = audit_workbook(
                args.filepath,
                backend=args.backend,
                max_traceback_depth=args.max_traceback_depth,
            )
    else:
        report = audit_workbook(
            args.filepath,
            backend=args.backend,
            max_traceback_depth=args.max_traceback_depth,
        )
    report_dict = report.to_dict()

    json_text = json.dumps(report_dict, sort_keys=True, separators=(",", ":"))

    if args.format == "json":
        output_text = json_text
    else:
        _render_terminal(report_dict, console or Console())
        output_text = None

    output_path = args.output
    if output_path is None and args.format == "terminal":
        output_path = f"{args.filepath}.xlodit.json"

    if output_path is not None:
        Path(output_path).write_text(json_text + "\n", encoding="utf-8")
    if output_text is not None:
        print(output_text)

    return _exit_code(report_dict)


if __name__ == "__main__":
    sys.exit(main())
