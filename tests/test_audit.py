from xlodit.audit import audit_workbook


def test_valid_workbook_has_no_errors(fixture_dir) -> None:
    report = audit_workbook(str(fixture_dir / "valid.xlsx"), backend="none")
    assert report.audit_completed is True
    assert report.summary["errors"] == 0


def test_formula_error_detected_with_traceback(fixture_dir) -> None:
    report = audit_workbook(
        str(fixture_dir / "formula_error_simple.xlsx"), backend="none"
    )
    assert report.summary["errors"] >= 1
    formula_issues = [i for i in report.issues if i.rule_id == "F001"]
    assert formula_issues
    assert formula_issues[0].traceback is not None


def test_numeric_text_is_warning(fixture_dir) -> None:
    report = audit_workbook(str(fixture_dir / "numeric_text.xlsx"), backend="none")
    warning_rules = {
        issue.rule_id for issue in report.issues if issue.severity == "warning"
    }
    assert "T001" in warning_rules


def test_non_xlsx_returns_incomplete_audit(tmp_path) -> None:
    path = tmp_path / "bad.txt"
    path.write_text("not a workbook", encoding="utf-8")
    report = audit_workbook(str(path), backend="none")
    assert report.audit_completed is False
    assert report.summary["errors"] == 1


def test_deterministic_ordering(fixture_dir) -> None:
    report = audit_workbook(str(fixture_dir / "mixed.xlsx"), backend="none")
    keys = [
        (
            0 if issue.severity == "error" else 1,
            issue.sheet or "",
            issue.cell or "",
            issue.rule_id,
        )
        for issue in report.issues
    ]
    assert keys == sorted(keys)
