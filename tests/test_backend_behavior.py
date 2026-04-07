from xlodit.audit import audit_workbook


def test_backend_auto_fallback_to_none_when_unavailable(
    fixture_dir, monkeypatch
) -> None:
    monkeypatch.setattr("xlodit.backend.libreoffice_available", lambda: False)
    report = audit_workbook(str(fixture_dir / "valid.xlsx"), backend="auto")
    assert report.backend.requested == "auto"
    assert report.backend.used == "none"
    assert report.backend.recalculated is False


def test_backend_explicit_libreoffice_unavailable_is_failure(
    fixture_dir, monkeypatch
) -> None:
    monkeypatch.setattr("xlodit.backend.libreoffice_available", lambda: False)
    report = audit_workbook(str(fixture_dir / "valid.xlsx"), backend="libreoffice")
    assert report.audit_completed is False
    assert any(issue.rule_id == "BE001" for issue in report.issues)
