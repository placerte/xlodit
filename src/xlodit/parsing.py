from __future__ import annotations

import re
from dataclasses import dataclass

from openpyxl.utils.cell import absolute_coordinate

CELL_REF_RE = re.compile(r"\$?[A-Za-z]{1,3}\$?[0-9]{1,7}")
SHEET_AND_CELL_RE = re.compile(
    r"(?:(?:'(?P<quoted>[^']+)'|(?P<plain>[A-Za-z0-9_\-\. ]+))!)?(?P<cell>\$?[A-Za-z]{1,3}\$?[0-9]{1,7})"
)


@dataclass(frozen=True, slots=True)
class CellRef:
    sheet: str
    cell: str


def normalize_cell_ref(cell: str) -> str:
    return absolute_coordinate(cell).replace("$", "")


def parse_formula_references(formula: str, default_sheet: str) -> list[CellRef]:
    refs: list[CellRef] = []
    for match in SHEET_AND_CELL_RE.finditer(formula):
        cell_token = match.group("cell")
        if not cell_token or not CELL_REF_RE.fullmatch(cell_token):
            continue
        sheet = match.group("quoted") or match.group("plain") or default_sheet
        refs.append(CellRef(sheet=sheet, cell=normalize_cell_ref(cell_token)))
    return refs
