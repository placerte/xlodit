from __future__ import annotations

import re
from pathlib import Path

from openpyxl import Workbook

from xlodit.models import AuditIssue

NUMERIC_TEXT_RE = re.compile(r"^\d+[\.,]\d+$")
ERROR_TOKENS = {
    "#VALUE!",
    "#VALEUR!",
    "#REF!",
    "#DIV/0!",
    "#N/A",
    "#N/D",
    "#NAME?",
    "#NOM?",
    "#NUM!",
    "#NOMBRE!",
    "#NULL!",
}


def is_formula_cell(value: object) -> bool:
    return isinstance(value, str) and value.startswith("=")


def is_formula_error_token(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if value in ERROR_TOKENS:
        return True
    return value.startswith("Err:")


def formula_has_error_token(formula: str) -> bool:
    return any(token in formula for token in ERROR_TOKENS)


def rule_wb001(workbook_path: Path, message: str) -> AuditIssue:
    return AuditIssue(
        severity="error",
        kind="workbook_unreadable",
        rule_id="WB001",
        message=message,
        workbook=str(workbook_path),
    )


def structural_issues(workbook: Workbook, workbook_path: Path) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    if len(workbook.sheetnames) == 0:
        issues.append(
            AuditIssue(
                severity="error",
                kind="structural_issue",
                rule_id="S001",
                message="Workbook has no worksheets",
                workbook=str(workbook_path),
            )
        )
    return issues


def numeric_text_issues(workbook: Workbook, workbook_path: Path) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and NUMERIC_TEXT_RE.fullmatch(
                    cell.value
                ):
                    issues.append(
                        AuditIssue(
                            severity="warning",
                            kind="numeric_text",
                            rule_id="T001",
                            message="Numeric value stored as text",
                            workbook=str(workbook_path),
                            sheet=sheet.title,
                            cell=cell.coordinate,
                            value=cell.value,
                        )
                    )
    return issues
