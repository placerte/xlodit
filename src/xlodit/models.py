from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class BackendInfo:
    requested: str
    used: str
    recalculated: bool


@dataclass(slots=True)
class TracebackNode:
    sheet: str
    cell: str
    failing: bool = False
    value: Any = None
    children: list["TracebackNode"] = field(default_factory=list)


@dataclass(slots=True)
class TracebackResult:
    status: str
    cycle_detected: bool
    max_depth_reached: bool
    nodes: list[TracebackNode]
    root_candidates: list[dict[str, str]]


@dataclass(slots=True)
class AuditIssue:
    severity: str
    kind: str
    rule_id: str
    message: str
    workbook: str | None = None
    sheet: str | None = None
    cell: str | None = None
    formula: str | None = None
    value: str | int | float | None = None
    backend: str | None = None
    details: dict[str, Any] | None = None
    traceback: TracebackResult | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "severity": self.severity,
            "kind": self.kind,
            "rule_id": self.rule_id,
            "message": self.message,
        }
        optional_fields = (
            "workbook",
            "sheet",
            "cell",
            "formula",
            "value",
            "backend",
            "details",
            "traceback",
        )
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is None:
                continue
            if field_name == "traceback":
                out[field_name] = asdict(value)
            else:
                out[field_name] = value
        return out


@dataclass(slots=True)
class AuditReport:
    ok: bool
    audit_completed: bool
    backend: BackendInfo
    summary: dict[str, int]
    issues: list[AuditIssue]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "audit_completed": self.audit_completed,
            "backend": asdict(self.backend),
            "summary": self.summary,
            "issues": [issue.to_dict() for issue in self.issues],
        }
