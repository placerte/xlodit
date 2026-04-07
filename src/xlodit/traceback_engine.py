from __future__ import annotations

from dataclasses import dataclass

from openpyxl import Workbook

from xlodit.models import TracebackNode, TracebackResult
from xlodit.parsing import CellRef, parse_formula_references
from xlodit.rules import (
    formula_has_error_token,
    is_formula_error_token,
    is_formula_cell,
)


@dataclass(slots=True)
class _TraceState:
    cycle_detected: bool = False
    max_depth_reached: bool = False
    root_candidates: list[dict[str, str]] = None

    def __post_init__(self) -> None:
        if self.root_candidates is None:
            self.root_candidates = []


def _formula_value(source_wb: Workbook, sheet: str, cell: str) -> str | None:
    if sheet not in source_wb:
        return None
    value = source_wb[sheet][cell].value
    if is_formula_cell(value):
        return value
    return None


def _display_value(values_wb: Workbook, sheet: str, cell: str) -> object:
    if sheet not in values_wb:
        return None
    return values_wb[sheet][cell].value


def _is_failing_formula(
    source_wb: Workbook, values_wb: Workbook, sheet: str, cell: str
) -> bool:
    formula = _formula_value(source_wb, sheet, cell)
    if formula is None:
        return False
    if formula_has_error_token(formula):
        return True
    if sheet in values_wb:
        cell_obj = values_wb[sheet][cell]
        value = cell_obj.value
        if is_formula_error_token(value):
            return True
        if cell_obj.data_type == "e":
            return True
    return False


def _trace_node(
    source_wb: Workbook,
    values_wb: Workbook,
    current: CellRef,
    depth: int,
    max_depth: int,
    path: set[tuple[str, str]],
    state: _TraceState,
) -> TracebackNode:
    failing = _is_failing_formula(source_wb, values_wb, current.sheet, current.cell)
    node = TracebackNode(
        sheet=current.sheet,
        cell=current.cell,
        failing=failing,
        value=_display_value(values_wb, current.sheet, current.cell),
    )
    key = (current.sheet, current.cell)
    if key in path:
        state.cycle_detected = True
        state.root_candidates.append(
            {"sheet": current.sheet, "cell": current.cell, "reason": "cycle_detected"}
        )
        return node

    formula = _formula_value(source_wb, current.sheet, current.cell)
    if formula is None:
        state.root_candidates.append(
            {"sheet": current.sheet, "cell": current.cell, "reason": "non_formula_leaf"}
        )
        return node

    if depth >= max_depth:
        state.max_depth_reached = True
        state.root_candidates.append(
            {
                "sheet": current.sheet,
                "cell": current.cell,
                "reason": "max_depth_reached",
            }
        )
        return node

    refs = parse_formula_references(formula, current.sheet)
    if not refs:
        state.root_candidates.append(
            {"sheet": current.sheet, "cell": current.cell, "reason": "no_references"}
        )
        return node

    next_path = set(path)
    next_path.add(key)
    for ref in refs:
        child = _trace_node(
            source_wb, values_wb, ref, depth + 1, max_depth, next_path, state
        )
        node.children.append(child)
        if _is_failing_formula(source_wb, values_wb, ref.sheet, ref.cell):
            state.root_candidates.append(
                {
                    "sheet": ref.sheet,
                    "cell": ref.cell,
                    "reason": "upstream_failing_formula",
                }
            )
    return node


def build_traceback(
    source_wb: Workbook,
    values_wb: Workbook,
    sheet: str,
    cell: str,
    max_depth: int,
) -> TracebackResult:
    formula = _formula_value(source_wb, sheet, cell)
    if formula is None:
        return TracebackResult(
            status="skipped",
            cycle_detected=False,
            max_depth_reached=False,
            nodes=[],
            root_candidates=[],
        )

    state = _TraceState()
    root = _trace_node(
        source_wb=source_wb,
        values_wb=values_wb,
        current=CellRef(sheet=sheet, cell=cell),
        depth=0,
        max_depth=max_depth,
        path=set(),
        state=state,
    )
    status = "complete"
    if state.cycle_detected or state.max_depth_reached:
        status = "partial"
    deduped = list(
        {
            (rc["sheet"], rc["cell"], rc["reason"]): rc for rc in state.root_candidates
        }.values()
    )
    return TracebackResult(
        status=status,
        cycle_detected=state.cycle_detected,
        max_depth_reached=state.max_depth_reached,
        nodes=[root],
        root_candidates=sorted(
            deduped, key=lambda x: (x["sheet"], x["cell"], x["reason"])
        ),
    )
